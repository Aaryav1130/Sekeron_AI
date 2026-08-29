import json
from google import genai
from google.genai import types
from typing import List

from src.schemas import RecommendationResult, UpdatedRecommendationResult, ArtistIntelligence

class Recommender:
    def __init__(self, api_key: str):
        # Using the new official google.genai SDK
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-3.6-flash"
        
    def generate_recommendation(
        self, brief_id: str, brief_text: str, artist_records: List[ArtistIntelligence]
    ) -> RecommendationResult:
        
        # Serialize the artist intelligence for context
        artists_json = [json.loads(a.model_dump_json()) for a in artist_records]
        
        prompt = f"""
        You are a recommendation engine for a creative marketplace.
        
        Hirer Brief:
        {brief_text}
        
        Available Artists Intelligence (Evidence-Backed):
        {json.dumps(artists_json, indent=2)}
        
        Task:
        1. Interpret the hirer's intent from the incomplete brief.
        2. Identify explicit constraints and important unknowns.
        3. Recommend the TOP 2 artists from the provided list based ONLY on their demonstrated evidence (not just claims).
        4. Explain the match reasoning, trade-offs, and assumptions made.
        5. Formulate up to 2 high-impact refinement questions for the hirer that would materially change this ranking.
        
        Return the result strictly conforming to the requested JSON schema. Provide ALL required fields.
        """
        
        # Adding a retry loop because LLMs occasionally miss nested fields in strict JSON schema
        import time
        for attempt in range(5):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=RecommendationResult,
                        temperature=0.1  # Low temp for deterministic JSON
                    )
                )
                
                result = RecommendationResult.model_validate_json(response.text)
                result.brief_id = brief_id
                return result
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "Quota exceeded" in error_msg:
                    print(f"\n[Rate Limit Hit] Waiting 60s before retrying {brief_id}...")
                    time.sleep(60)
                    continue
                elif attempt >= 4:
                    print(f"\n[Warning] Recommendation for {brief_id} failed: {e}")
                    break
                    
        # Return safe fallback object if all attempts exhaust (e.g. constant 429s)
        return RecommendationResult(
            brief_id=brief_id,
            interpreted_intent="Error: Could not generate structured recommendation due to strict quota limits.",
            explicit_constraints=[],
            important_unknowns=[],
            initial_top_two=[],
            refinement_questions=[]
        )

    def rerank_recommendation(
        self, brief_id: str, original_recommendation: RecommendationResult, 
        update_text: str, artist_records: List[ArtistIntelligence]
    ) -> UpdatedRecommendationResult:
        
        artists_json = [json.loads(a.model_dump_json()) for a in artist_records]
        
        prompt = f"""
        You are a recommendation engine for a creative marketplace.
        
        Original Recommendation Context:
        {original_recommendation.model_dump_json(indent=2)}
        
        New Hirer Update:
        {update_text}
        
        Available Artists Intelligence:
        {json.dumps(artists_json, indent=2)}
        
        Task:
        Re-rank the candidates based on the new information. 
        Select the updated top 2 artists.
        Explain exactly what changed in your ranking logic and why this new evidence shifted the result.
        
        Return the result strictly conforming to the requested JSON schema. Provide ALL required fields.
        """
        
        import time
        for attempt in range(5):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=UpdatedRecommendationResult,
                        temperature=0.1
                    )
                )
                
                result = UpdatedRecommendationResult.model_validate_json(response.text)
                result.brief_id = brief_id
                return result
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "Quota exceeded" in error_msg:
                    print(f"\n[Rate Limit Hit] Waiting 60s before retrying re-rank for {brief_id}...")
                    time.sleep(60)
                    continue
                elif attempt >= 4:
                    print(f"\n[Warning] Re-ranking for {brief_id} failed: {e}")
                    break
                    
        return UpdatedRecommendationResult(
            brief_id=brief_id,
            new_information="Error parsing update",
            what_changed_and_why="Pipeline encountered an API error or hit persistent quota limits.",
            updated_top_two=[]
        )
