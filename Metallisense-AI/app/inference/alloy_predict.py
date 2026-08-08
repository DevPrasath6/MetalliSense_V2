"""
Inference module for Alloy Correction
"""
import sys
from pathlib import Path
from typing import Dict

sys.path.append(str(Path(__file__).parent.parent))

from agents.alloy_agent import AlloyCorrectionAgent
from data.grade_specs import GradeSpecificationGenerator
from config import ALLOY_MODEL_PATH


class AlloyPredictor:
    """Wrapper for alloy correction inference"""
    
    def __init__(self, model_path: str = None):
        """
        Initialize predictor with trained model
        
        Args:
            model_path: Path to trained model file
        """
        if model_path is None:
            model_path = ALLOY_MODEL_PATH
        
        self.grade_generator = GradeSpecificationGenerator()
        self.agent = AlloyCorrectionAgent(self.grade_generator)
        
        # Load trained model
        if Path(model_path).exists():
            self.agent.load(model_path)
            print(f"Alloy correction model loaded from: {model_path}")
        else:
            raise FileNotFoundError(
                f"Model file not found: {model_path}. "
                "Please train the model first using training/train_alloy_agent.py"
            )
    
    def predict(self, grade: str, composition: Dict[str, float]) -> Dict:
        """
        Predict alloy additions for composition
        
        Args:
            grade: Target metal grade
            composition: Dictionary with element percentages
            
        Returns:
            Dictionary with recommended_additions, confidence, message, and warning
        """
        try:
            result = self.agent.predict(grade, composition)
            return result
        except Exception as e:
            return {
                "recommended_additions": {},
                "confidence": 0.0,
                "message": f"Prediction failed: {str(e)}",
                "warning": "ERROR",
                "error": str(e)
            }
    
    def get_available_grades(self) -> list:
        """Get list of supported grades"""
        return self.grade_generator.get_available_grades()
    
    def get_grade_spec(self, grade: str) -> Dict:
        """Get specification for a grade"""
        return self.grade_generator.get_grade_spec(grade)
    
    def is_healthy(self) -> bool:
        """Check if model is loaded and ready"""
        return self.agent.is_trained


# Global predictor instance (lazy loading)
_alloy_predictor = None


def get_alloy_predictor() -> AlloyPredictor:
    """Get or create global alloy predictor instance"""
    global _alloy_predictor
    
    if _alloy_predictor is None:
        _alloy_predictor = AlloyPredictor()
    
    return _alloy_predictor


if __name__ == "__main__":
    # Test inference
    predictor = get_alloy_predictor()
    
    # Test composition
    test_grade = "SG-IRON"
    test_comp = {
        "Fe": 81.2,
        "C": 4.4,
        "Si": 3.1,
        "Mn": 0.4,
        "P": 0.05,
        "S": 0.02
    }
    
    print("Testing Alloy Predictor")
    print(f"Grade: {test_grade}")
    print(f"Input: {test_comp}")
    result = predictor.predict(test_grade, test_comp)
    print(f"Result: {result}")
