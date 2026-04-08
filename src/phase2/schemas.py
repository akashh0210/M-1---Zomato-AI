from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field, field_validator


class RecommendationRequest(BaseModel):
    location: str = Field(..., min_length=1)
    budget: float = Field(..., description="Maximum budget for two people", ge=0.0)
    cuisine: str | List[str]
    min_rating: float = Field(..., ge=0.0, le=5.0)
    additional_preferences: str | List[str] | None = None

    @field_validator("location")
    @classmethod
    def normalize_location(cls, value: str) -> str:
        return value.strip().lower()



    @field_validator("cuisine")
    @classmethod
    def normalize_cuisine(cls, value: str | List[str]) -> str | List[str]:
        if isinstance(value, str):
            text = value.strip().lower()
            if not text:
                raise ValueError("cuisine cannot be empty")
            return text
        cleaned = [item.strip().lower() for item in value if item and item.strip()]
        if not cleaned:
            raise ValueError("cuisine list cannot be empty")
        return cleaned

    @field_validator("additional_preferences")
    @classmethod
    def normalize_preferences(cls, value: str | List[str] | None) -> str | List[str] | None:
        if value is None:
            return None
        if isinstance(value, str):
            return value.strip().lower()
        return [item.strip().lower() for item in value if item and item.strip()]


class RecommendationItem(BaseModel):
    rank: int
    restaurant_name: str
    location_city: str
    cuisines: List[str]
    rating: float
    estimated_cost_for_two: float
    explanation: str
    confidence: float = Field(..., ge=0.0, le=1.0)


class RecommendationResponse(BaseModel):
    query: RecommendationRequest
    suggestions: List[str] = []
    recommendations: List[RecommendationItem]
    message: str | None = None

