"""
AGENT 2: ALLOY CORRECTION AGENT
Production-grade wrapper for trained alloy recommendation model

🎯 Purpose:
    "What alloy additions are required to correct the deviation?"

✅ Responsibilities:
    - Load trained alloy recommendation model
    - Accept deviated composition + target grade
    - Output alloy elements to add and required percentages
    
❌ Does NOT:
    - Validate grade compliance
    - Modify composition directly
    - Trigger actions autonomously
    - Override metallurgical rules
"""
import sys
from pathlib import Path
from typing import Dict
import numpy as np

sys.path.append(str(Path(__file__).parent.parent))

from agents.alloy_agent import AlloyCorrectionAgent
from data.grade_specs import GradeSpecificationGenerator
from config import ALLOY_MODEL_PATH, MIN_CONFIDENCE_THRESHOLD


class AlloyCorrectionAgentWrapper:
    """
    Production Agent Wrapper for Alloy Correction
    
    Design Principles:
    - Stateless: Each recommendation is independent
    - Deterministic: Same input = same output
    - Explainable: Clear reasoning for recommendations
    - Advisory: Never autonomous
    """
    
    AGENT_NAME = "AlloyCorrectionAgent"
    VERSION = "1.0.0"
    
    def __init__(self, model_path: str = None):
        """
        Initialize agent with trained model
        
        Args:
            model_path: Path to trained alloy model
        """
        if model_path is None:
            model_path = ALLOY_MODEL_PATH
        
        self.model_path = model_path
        self.grade_generator = GradeSpecificationGenerator()
        self._ml_agent = None
        self._load_model()
    
    def _load_model(self):
        """Load trained ML model (internal operation)"""
        if not Path(self.model_path).exists():
            raise FileNotFoundError(
                f"Alloy model not found: {self.model_path}. "
                "Train the model first using: python app/training/train_alloy_agent.py"
            )
        
        self._ml_agent = AlloyCorrectionAgent(self.grade_generator)
        self._ml_agent.load(self.model_path)
    
    def recommend(self, grade: str, composition: Dict[str, float]) -> Dict:
        """
        Recommend alloy additions to correct composition
        
        Agent Contract:
        Input: {
            "grade": "SG-IRON",
            "composition": {"Fe": 81.2, "C": 4.4, "Si": 3.1, "Mn": 0.4, ...}
        }
        Output: {
            "agent": "AlloyCorrectionAgent",
            "recommended_additions": {"Si": 0.22, "Mn": 0.15},
            "confidence": 0.91,
            "explanation": "Adjusting elements toward grade midpoint"
        }
        
        Args:
            grade: Target metal grade
            composition: Dictionary with element percentages
            
        Returns:
            Structured agent response with recommendations
        """
        if not self.is_ready():
            raise RuntimeError("Agent not ready. Model not loaded.")
        
        # Validate grade
        available_grades = self.grade_generator.get_available_grades()
        if grade not in available_grades:
            return {
                "agent": self.AGENT_NAME,
                "recommended_additions": {},
                "confidence": 0.0,
                "explanation": f"Unknown grade: {grade}. Available: {available_grades}"
            }
        
        try:
            # Call underlying ML model
            ml_result = self._ml_agent.predict(grade, composition)
            
            # Filter out negligible additions (< 0.01%)
            filtered_additions = {
                element: amount 
                for element, amount in ml_result["recommended_additions"].items()
                if amount >= 0.01
            }
            
            # Calculate confidence
            confidence = ml_result["confidence"]
            
            # Generate explanation
            explanation = self._generate_explanation(
                grade=grade,
                additions=filtered_additions,
                confidence=confidence
            )
            
            # Return structured agent output
            return {
                "agent": self.AGENT_NAME,
                "recommended_additions": filtered_additions,
                "confidence": float(confidence),
                "explanation": explanation
            }
        
        except Exception as e:
            # Graceful error handling
            return {
                "agent": self.AGENT_NAME,
                "recommended_additions": {},
                "confidence": 0.0,
                "explanation": f"Agent error: {str(e)}"
            }
    
    def _generate_explanation(
        self, 
        grade: str, 
        additions: Dict[str, float],
        confidence: float
    ) -> str:
        """
        Generate human-readable explanation
        
        Args:
            grade: Target grade
            additions: Recommended additions
            confidence: Confidence score
            
        Returns:
            Explanation string
        """
        if not additions:
            return f"Composition is within acceptable range for {grade}. No additions required."
        
        element_list = ", ".join([f"{el}: +{amt:.2f}%" for el, amt in additions.items()])
        
        if confidence >= 0.85:
            confidence_text = "High confidence"
        elif confidence >= 0.70:
            confidence_text = "Moderate confidence"
        else:
            confidence_text = "Low confidence"
        
        return (
            f"Adjusting elements toward {grade} grade midpoint. "
            f"Recommended: {element_list}. "
            f"{confidence_text} in recommendation based on historical correction patterns."
        )
    
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
            "available_grades": self.grade_generator.get_available_grades(),
            "purpose": "Recommend alloy additions to correct deviations",
            "stateless": True,
            "deterministic": True,
            "autonomous": False
        }
    
    def get_available_grades(self) -> list:
        """Get list of supported grades"""
        return self.grade_generator.get_available_grades()
    
    def get_grade_spec(self, grade: str) -> Dict:
        """Get specification for a grade"""
        return self.grade_generator.get_grade_spec(grade)


# Global singleton instance
_agent_instance = None


def get_alloy_agent() -> AlloyCorrectionAgentWrapper:
    """Get or create global alloy agent instance"""
    global _agent_instance
    
    if _agent_instance is None:
        _agent_instance = AlloyCorrectionAgentWrapper()
    
    return _agent_instance


if __name__ == "__main__":
    # Test agent
    agent = get_alloy_agent()
    
    print("="*60)
    print("ALLOY CORRECTION AGENT TEST")
    print("="*60)
    print(f"Metadata: {agent.get_metadata()}")
    
    # Test composition (deviated)
    test_grade = "SG-IRON"
    test_comp = {
        "Fe": 81.2,
        "C": 4.4,
        "Si": 3.1,
        "Mn": 0.4,
        "P": 0.04,
        "S": 0.02
    }
    
    print(f"\nInput Grade: {test_grade}")
    print(f"Input Composition: {test_comp}")
    result = agent.recommend(test_grade, test_comp)
    print("\nOutput:")
    for key, value in result.items():
        print(f"  {key}: {value}")
    print("="*60)
