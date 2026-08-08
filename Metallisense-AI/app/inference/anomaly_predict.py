"""
Inference module for Anomaly Detection
"""
import sys
from pathlib import Path
from typing import Dict

sys.path.append(str(Path(__file__).parent.parent))

from agents.anomaly_agent import AnomalyDetectionAgent
from config import ANOMALY_MODEL_PATH


class AnomalyPredictor:
    """Wrapper for anomaly detection inference"""
    
    def __init__(self, model_path: str = None):
        """
        Initialize predictor with trained model
        
        Args:
            model_path: Path to trained model file
        """
        if model_path is None:
            model_path = ANOMALY_MODEL_PATH
        
        self.agent = AnomalyDetectionAgent()
        
        # Load trained model
        if Path(model_path).exists():
            self.agent.load(model_path)
            print(f"Anomaly model loaded from: {model_path}")
        else:
            raise FileNotFoundError(
                f"Model file not found: {model_path}. "
                "Please train the model first using training/train_anomaly.py"
            )
    
    def predict(self, composition: Dict[str, float], grade: str = None) -> Dict:
        """
        Predict anomaly score for composition
        
        Args:
            composition: Dictionary with element percentages
            grade: Optional grade for grade-aware detection
            
        Returns:
            Dictionary with anomaly_score, severity, and message
        """
        try:
            result = self.agent.predict(composition, grade=grade)
            return result
        except Exception as e:
            return {
                "anomaly_score": 0.0,
                "severity": "ERROR",
                "message": f"Prediction failed: {str(e)}",
                "error": str(e)
            }
    
    def is_healthy(self) -> bool:
        """Check if model is loaded and ready"""
        return self.agent.is_trained


# Global predictor instance (lazy loading)
_anomaly_predictor = None


def get_anomaly_predictor() -> AnomalyPredictor:
    """Get or create global anomaly predictor instance"""
    global _anomaly_predictor
    
    if _anomaly_predictor is None:
        _anomaly_predictor = AnomalyPredictor()
    
    return _anomaly_predictor


if __name__ == "__main__":
    # Test inference
    predictor = get_anomaly_predictor()
    
    # Test composition
    test_comp = {
        "Fe": 85.5,
        "C": 3.2,
        "Si": 2.1,
        "Mn": 0.6,
        "P": 0.04,
        "S": 0.02
    }
    
    print("Testing Anomaly Predictor")
    print(f"Input: {test_comp}")
    result = predictor.predict(test_comp)
    print(f"Result: {result}")
