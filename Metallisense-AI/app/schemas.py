"""
Pydantic schemas for request/response validation
"""
from typing import Dict, Optional
from pydantic import BaseModel, Field, validator


class Composition(BaseModel):
    """Chemical composition model"""
    Fe: float = Field(..., ge=0, le=100, description="Iron percentage")
    C: float = Field(..., ge=0, le=100, description="Carbon percentage")
    Si: float = Field(..., ge=0, le=100, description="Silicon percentage")
    Mn: float = Field(..., ge=0, le=100, description="Manganese percentage")
    P: float = Field(..., ge=0, le=100, description="Phosphorus percentage")
    S: float = Field(..., ge=0, le=100, description="Sulfur percentage")

    @validator('*')
    def check_percentage(cls, v):
        if not 0 <= v <= 100:
            raise ValueError('Percentage must be between 0 and 100')
        return v


class AnomalyRequest(BaseModel):
    """Request model for anomaly detection"""
    composition: Composition
    grade: Optional[str] = Field(None, description="Optional grade for grade-aware detection")


class AnomalyResponse(BaseModel):
    """Response model for anomaly detection"""
    anomaly_score: float = Field(..., ge=0, le=1, description="Anomaly score (0-1)")
    severity: str = Field(..., description="Severity level: LOW, MEDIUM, HIGH")
    message: str = Field(..., description="Human-readable explanation")


class AlloyRecommendationRequest(BaseModel):
    """Request model for alloy correction recommendations"""
    grade: str = Field(..., description="Target metal grade")
    composition: Composition


class AlloyRecommendationResponse(BaseModel):
    """Response model for alloy correction recommendations"""
    recommended_additions: Dict[str, float] = Field(
        ..., 
        description="Recommended additions for each element (percentage)"
    )
    confidence: float = Field(
        ..., 
        ge=0, 
        le=1, 
        description="Confidence score (0-1)"
    )
    message: str = Field(..., description="Human-readable explanation")
    warning: Optional[str] = Field(None, description="Safety warnings if any")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    message: str
    models_loaded: Dict[str, bool]


class GradeSpecification(BaseModel):
    """Grade specification model"""
    grade: str
    composition_ranges: Dict[str, list]
    description: Optional[str] = None
