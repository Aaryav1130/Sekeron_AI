import os
from google import genai
from google.genai import types
import json
from pathlib import Path
from typing import Literal

from src.schemas import ArtistIntelligence, CapabilityDimension
from src.media_extractor import MediaSelector

class AIEngine:
    def __init__(self, api_key: str):
        # Using the new official google.genai SDK
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-3.6-flash"
        
    def _read_profile_text(self, folder_path: Path) -> str:
        """Finds and reads the profile text file."""
        for ext in ["*.txt", "*.md"]:
            for file_path in folder_path.glob(ext):
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    return f.read()
        return "No profile text found. Incomplete data."

    def process_artist(self, artist_folder: str, category: str) -> ArtistIntelligence:
        folder = Path(artist_folder)
        artist_id = folder.name
        
        profile_text = self._read_profile_text(folder)
        
        selector = MediaSelector(artist_folder)
        media_files = []
        
        # Select media based on category
        if category == "photographer":
            media_files = selector.select_images()
        elif category == "video_editor":
            media_files = selector.extract_video_keyframes()
        elif category == "musician":
            media_files = selector.select_audio()
            
        uploaded_files = []
        for mf in media_files:
            try:
                uploaded = self.client.files.upload(file=str(mf))
                uploaded_files.append(uploaded)
            except Exception as e:
                print(f"\nWarning: Could not upload {mf} - {e}")

        prompt = f"""
        You are an expert talent evaluator for a creative marketplace.
        Analyze the provided artist profile text and the accompanying media.
        
        Artist Category: {category}
        Profile Text:
        {profile_text}
        
        Your task is to build an evidence-backed capability record.
        1. Extract what the profile CLAIMS the artist can do.
        2. Evaluate the media to see what is ACTUALLY DEMONSTRATED.
        3. Identify any claims that lack supporting media evidence.
        4. Assess the artist on 4 category-specific dimensions (e.g., Lighting/Composition for photographers, Pacing/Color for video editors, Genre/Production for musicians).
        5. Provide a confidence level for each dimension and an overall rationale.
        6. Explicitly state what CANNOT be determined from this incomplete data.
        
        If the media is damaged or missing, note that in your evidence gaps and set confidence to Unknown.
        Return the result strictly conforming to the JSON schema requested.
        """
        
        contents = [prompt] + uploaded_files
        
        # Enforce strict JSON output using Pydantic schema with smart retry for rate limits
        import time
        for attempt in range(4):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=ArtistIntelligence
                    )
                )
                result = ArtistIntelligence.model_validate_json(response.text)
                result.artist_id = artist_id  # Ensure ID is accurate
                
                # Clean up uploaded files from Google servers
                for uf in uploaded_files:
                    try:
                        self.client.files.delete(name=uf.name)
                    except:
                        pass
                        
                return result
                
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "Quota exceeded" in error_msg:
                    print(f"\n[Rate Limit Hit] Waiting 60 seconds before retrying {artist_id}...")
                    time.sleep(60)
                    continue
                else:
                    print(f"\n[Error processing {artist_id}]: {e}")
                    break
        
        # Fallback for damaged/unparsable cases if all retries fail
        for uf in uploaded_files:
            try:
                self.client.files.delete(name=uf.name)
            except:
                pass
                
        return ArtistIntelligence(
            artist_id=artist_id,
            category=category,
            profile_claims=["Failed to parse"],
            demonstrated_evidence=[],
            evidence_gaps=["Pipeline error or corrupt media"],
            category_specific_dimensions=[],
            unknowns=["Everything due to processing failure"],
            overall_confidence_rationale="Error occurred during API generation."
        )
