from pydantic import BaseModel, Field
from typing import List

class CapabilityDimension(BaseModel):
    dimension_name: str
    assessment: str = Field(..., description="Objective assessment based purely on evidence")
    evidence_citation: str = Field(..., description="File name and/or timestamp backing this assessment")
    confidence: str = Field(..., description="Must be one of: High, Medium, Low, Unknown")

class ArtistIntelligence(BaseModel):
    artist_id: str
    category: str = Field(..., description="Must be one of: photographer, musician, video_editor")
    profile_claims: List[str] = Field(..., description="Claims extracted directly from the profile text")
    demonstrated_evidence: List[str] = Field(..., description="Skills actually demonstrated in the media")
    evidence_gaps: List[str] = Field(..., description="Claims that lack supporting media evidence")
    category_specific_dimensions: List[CapabilityDimension]
    unknowns: List[str] = Field(..., description="What cannot be determined from the provided media")
    overall_confidence_rationale: str

class RefinementQuestion(BaseModel):
    question: str
    expected_impact: str = Field(..., description="How the answer would materially change the ranking")

class RankedArtist(BaseModel):
    artist_id: str
    rank: int
    match_reasoning: str = Field(..., description="Why this artist matches the intent based on evidence")
    trade_offs: str = Field(..., description="What the hirer sacrifices by choosing this artist")
    assumptions_made: str
    uncertainty: str

class RecommendationResult(BaseModel):
    brief_id: str
    interpreted_intent: str = Field(..., description="Summary of what the hirer is actually looking for")
    explicit_constraints: List[str]
    important_unknowns: List[str]
    initial_top_two: List[RankedArtist]
    refinement_questions: List[RefinementQuestion] = Field(..., description="Max 2 questions")

class UpdatedRecommendationResult(BaseModel):
    brief_id: str
    new_information: str = Field(..., description="Summary of the update")
    what_changed_and_why: str = Field(..., description="Explanation of how the ranking shifted")
    updated_top_two: List[RankedArtist]
