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


# ============================================================================
# AGENT-BASED SCHEMAS (Production Agent Architecture)
# ============================================================================

class AgentComposition(BaseModel):
    """Simplified composition for agent inputs"""
    Fe: float = Field(..., ge=0, le=100)
    C: float = Field(..., ge=0, le=100)
    Si: float = Field(..., ge=0, le=100)
    Mn: float = Field(..., ge=0, le=100)
    P: Optional[float] = Field(0.0, ge=0, le=100)
    S: Optional[float] = Field(0.0, ge=0, le=100)


class AnomalyAgentInput(BaseModel):
    """Input schema for Anomaly Detection Agent"""
    composition: AgentComposition


class AnomalyAgentOutput(BaseModel):
    """Output schema for Anomaly Detection Agent"""
    agent: str = Field(default="AnomalyDetectionAgent", description="Agent name")
    anomaly_score: float = Field(..., ge=0, le=1, description="Anomaly score (0-1)")
    severity: str = Field(..., description="Severity: LOW, MEDIUM, HIGH")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")
    explanation: str = Field(..., description="Human-readable explanation")


class AlloyAgentInput(BaseModel):
    """Input schema for Alloy Correction Agent"""
    grade: str = Field(..., description="Target metal grade")
    composition: AgentComposition


class AlloyAgentOutput(BaseModel):
    """Output schema for Alloy Correction Agent"""
    agent: str = Field(default="AlloyCorrectionAgent", description="Agent name")
    recommended_additions: Dict[str, float] = Field(..., description="Element additions (percentage)")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")
    explanation: str = Field(..., description="Human-readable explanation")


class AgentAnalysisRequest(BaseModel):
    """Request for full agent analysis"""
    composition: AgentComposition
    grade: str = Field(..., description="Target metal grade")


class AgentAnalysisResponse(BaseModel):
    """Response from agent manager with aggregated analysis"""
    anomaly_agent: Optional[AnomalyAgentOutput] = Field(None, description="Anomaly detection results")
    alloy_agent: Optional[AlloyAgentOutput] = Field(None, description="Alloy correction results")
    final_note: str = Field(default="Human approval required before action", description="Safety note")
    timestamp: Optional[str] = Field(None, description="Analysis timestamp")
