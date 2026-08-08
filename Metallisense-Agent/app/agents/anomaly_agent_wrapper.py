"""
AGENT 1: ANOMALY DETECTION AGENT
Production-grade wrapper for trained anomaly detection model

🎯 Purpose:
    "Is this spectrometer reading behaviorally abnormal?"

✅ Responsibilities:
    - Load trained anomaly model
    - Accept composition vector
    - Produce anomaly score, severity, and confidence
    
❌ Does NOT:
    - Decide PASS/FAIL
    - Suggest corrections
    - Override rules
    - Take autonomous actions
"""
import sys
from pathlib import Path
from typing import Dict
import numpy as np

sys.path.append(str(Path(__file__).parent.parent))

from agents.anomaly_agent import AnomalyDetectionAgent
from config import ANOMALY_MODEL_PATH


class AnomalyDetectionAgentWrapper:
    """
    Production Agent Wrapper for Anomaly Detection
    
    Design Principles:
    - Stateless: Each prediction is independent
    - Deterministic: Same input = same output
    - Explainable: Clear reasoning for decisions
    - Advisory: Never autonomous
    """
    
    AGENT_NAME = "AnomalyDetectionAgent"
    VERSION = "1.0.0"
    
    def __init__(self, model_path: str = None):
        """
        Initialize agent with trained model
        
        Args:
            model_path: Path to trained anomaly model
        """
        if model_path is None:
            model_path = ANOMALY_MODEL_PATH
        
        self.model_path = model_path
        self._ml_agent = None
        self._load_model()
    
    def _load_model(self):
        """Load trained ML model (internal operation)"""
        if not Path(self.model_path).exists():
            raise FileNotFoundError(
                f"Anomaly model not found: {self.model_path}. "
                "Train the model first using: python app/training/train_anomaly.py"
            )
        
        self._ml_agent = AnomalyDetectionAgent()
        self._ml_agent.load(self.model_path)
    
    def analyze(self, composition: Dict[str, float]) -> Dict:
        """
        Analyze composition for anomalous behavior
        
        Agent Contract:
        Input: {"Fe": 81.2, "C": 4.4, "Si": 3.1, "Mn": 0.4, "P": 0.04, "S": 0.02}
        Output: {
            "agent": "AnomalyDetectionAgent",
            "anomaly_score": 0.87,
            "severity": "HIGH",
            "confidence": 0.93,
            "explanation": "Detected deviation from historical distribution"
        }
        
        Args:
            composition: Dictionary with element percentages
            
        Returns:
            Structured agent response with anomaly analysis
        """
        if not self.is_ready():
            raise RuntimeError("Agent not ready. Model not loaded.")
        
        try:
            # Call underlying ML model
            ml_result = self._ml_agent.predict(composition)
            
            # Calculate confidence (inverse of uncertainty)
            # High anomaly scores = high confidence in anomaly
            # Low anomaly scores = high confidence in normal
            anomaly_score = ml_result["anomaly_score"]
            confidence = self._calculate_confidence(anomaly_score)
            
            # Generate explanation
            explanation = self._generate_explanation(
                severity=ml_result["severity"],
                composition=composition
            )
            
            # Return structured agent output
            return {
                "agent": self.AGENT_NAME,
                "anomaly_score": float(anomaly_score),
                "severity": ml_result["severity"],
                "confidence": float(confidence),
                "explanation": explanation
            }
        
        except Exception as e:
            # Graceful error handling
            return {
                "agent": self.AGENT_NAME,
                "anomaly_score": 0.0,
                "severity": "ERROR",
                "confidence": 0.0,
                "explanation": f"Agent error: {str(e)}"
            }
    
    def _calculate_confidence(self, anomaly_score: float) -> float:
        """
        Calculate confidence in the anomaly detection
        
        Logic:
        - Scores near 0.0 or 1.0 = high confidence
        - Scores near 0.5 = low confidence (uncertain)
        
        Args:
            anomaly_score: Normalized anomaly score (0-1)
            
        Returns:
            Confidence score (0-1)
        """
        # Distance from uncertainty (0.5)
        distance_from_uncertain = abs(anomaly_score - 0.5)
        # Map to 0-1 range
        confidence = 2 * distance_from_uncertain
        return np.clip(confidence, 0.0, 1.0)
    
    def _generate_explanation(
        self, 
        severity: str, 
        composition: Dict[str, float]
    ) -> str:
        """
        Generate human-readable explanation
        
        Args:
            anomaly_score: Anomaly score
            severity: Severity level
            composition: Input composition
            
        Returns:
            Explanation string
        """
        if severity == "LOW":
            return (
                "Detected deviation from historical composition distribution. "
                "Reading is within normal operational variance."
            )
        elif severity == "MEDIUM":
            return (
                "Moderate anomaly detected in composition pattern. "
                "Recommend verifying sensor calibration and melt stability."
            )
        elif severity == "HIGH":
            return (
                "High anomaly detected - composition significantly deviates from "
                "historical patterns. Possible sensor drift, contamination, or "
                "unstable melt chemistry. Human inspection recommended."
            )
        else:
            return "Unable to classify anomaly severity."
    
    def is_ready(self) -> bool:
        """Check if agent is ready to process requests"""
        return (
            self._ml_agent is not None and 
            self._ml_agent.is_trained
        )
    
    def get_metadata(self) -> Dict:
        """Return agent metadata"""
        return {
            "agent_name": self.AGENT_NAME,
            "version": self.VERSION,
            "model_path": self.model_path,
            "ready": self.is_ready(),
            "purpose": "Detect abnormal spectrometer behavior",
            "stateless": True,
            "deterministic": True,
            "autonomous": False
        }


# Global singleton instance
_agent_instance = None


def get_anomaly_agent() -> AnomalyDetectionAgentWrapper:
    """Get or create global anomaly agent instance"""
    global _agent_instance
    
    if _agent_instance is None:
        _agent_instance = AnomalyDetectionAgentWrapper()
    
    return _agent_instance


if __name__ == "__main__":
    # Test agent
    agent = get_anomaly_agent()
    
    print("="*60)
    print("ANOMALY DETECTION AGENT TEST")
    print("="*60)
    print(f"Metadata: {agent.get_metadata()}")
    
    # Test composition
    test_comp = {
        "Fe": 81.2,
        "C": 4.4,
        "Si": 3.1,
        "Mn": 0.4,
        "P": 0.04,
        "S": 0.02
    }
    
    print(f"\nInput: {test_comp}")
    result = agent.analyze(test_comp)
    print("\nOutput:")
    for key, value in result.items():
        print(f"  {key}: {value}")
    print("="*60)
