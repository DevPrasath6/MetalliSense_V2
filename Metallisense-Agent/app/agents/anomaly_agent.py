"""
Agent 3: Anomaly Detection Agent
Uses Isolation Forest for unsupervised anomaly detection
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
from typing import Dict, Tuple
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from config import (
    ELEMENTS, 
    ANOMALY_CONTAMINATION, 
    RANDOM_STATE,
    ANOMALY_SEVERITY_THRESHOLDS
)


class AnomalyDetectionAgent:
    """
    Anomaly Detection Agent using Isolation Forest
    
    Purpose:
    - Detect abnormal spectrometer behavior
    - Identify sensor drift, noise, or unstable melt chemistry
    - Works independently of PASS/FAIL logic
    """
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.elements = ELEMENTS
        self.is_trained = False
        # Store score statistics for deterministic predictions
        self.score_min = None
        self.score_max = None
        
    def prepare_features(self, df: pd.DataFrame) -> np.ndarray:
        """
        Extract and prepare features for anomaly detection
        
        Args:
            df: DataFrame with composition data
            
        Returns:
            Feature array
        """
        # Extract composition features
        features = df[self.elements].values
        return features
    
    def train(self, df: pd.DataFrame, contamination: float = ANOMALY_CONTAMINATION):
        """
        Train Isolation Forest model
        
        Args:
            df: Training DataFrame
            contamination: Expected proportion of outliers
        """
        print("Training Anomaly Detection Agent...")
        print(f"Training samples: {len(df)}")
        print(f"Contamination rate: {contamination}")
        
        # Prepare features
        X = self.prepare_features(df)
        
        # Fit scaler
        X_scaled = self.scaler.fit_transform(X)
        
        # Train Isolation Forest
        self.model = IsolationForest(
            contamination=contamination,
            random_state=RANDOM_STATE,
            n_estimators=200,
            max_samples='auto',
            max_features=len(self.elements),
            bootstrap=False,
            n_jobs=-1,
            verbose=0
        )
        
        self.model.fit(X_scaled)
        self.is_trained = True
        
        # Calculate training statistics
        train_scores = self.model.score_samples(X_scaled)
        train_predictions = self.model.predict(X_scaled)
        
        # Store score statistics for deterministic predictions
        self.score_min = float(train_scores.min())
        self.score_max = float(train_scores.max())
        
        num_anomalies = np.sum(train_predictions == -1)
        anomaly_rate = num_anomalies / len(df) * 100
        
        print(f"\nTraining Results:")
        print(f"  Anomalies detected: {num_anomalies} ({anomaly_rate:.2f}%)")
        print(f"  Score range: [{train_scores.min():.4f}, {train_scores.max():.4f}]")
        print(f"  Mean score: {train_scores.mean():.4f}")
        print(f"  Std score: {train_scores.std():.4f}")
        
        return {
            "num_anomalies": int(num_anomalies),
            "anomaly_rate": float(anomaly_rate),
            "score_min": float(train_scores.min()),
            "score_max": float(train_scores.max()),
            "score_mean": float(train_scores.mean()),
            "score_std": float(train_scores.std())
        }
    
    def _normalize_score(self, raw_score: float, score_min: float, score_max: float) -> float:
        """
        Normalize anomaly score to 0-1 range
        Lower raw scores = more anomalous
        Normalized: 0 = normal, 1 = highly anomalous
        """
        # Invert and normalize
        normalized = (score_max - raw_score) / (score_max - score_min)
        return np.clip(normalized, 0, 1)
    
    def _get_severity(self, normalized_score: float) -> str:
        """
        Determine severity level based on normalized score
        
        Args:
            normalized_score: Score between 0 and 1
            
        Returns:
            Severity level: NORMAL, LOW, MEDIUM, HIGH
        """
        # Fine-tuned thresholds for better anomaly detection
        if normalized_score < 0.05:
            return "NORMAL"  # Very low anomaly score = normal reading
        elif normalized_score < 0.20:
            return "LOW"  # Minor deviation
        elif normalized_score < 0.50:
            return "MEDIUM"  # Moderate deviation
        else:
            return "HIGH"  # Severe deviation
    
    def predict(self, composition: Dict[str, float]) -> Dict:
        """
        Predict anomaly score for a single composition
        
        Args:
            composition: Dictionary with element percentages
            
        Returns:
            Dictionary with anomaly_score and severity
        """
        if not self.is_trained:
            raise ValueError("Model is not trained. Call train() first.")
        
        # Prepare single sample
        X = np.array([[composition[el] for el in self.elements]])
        X_scaled = self.scaler.transform(X)
        
        # Get anomaly score
        raw_score = self.model.score_samples(X_scaled)[0]
        
        # Use stored score statistics from training for deterministic predictions
        if self.score_min is None or self.score_max is None:
            raise ValueError("Score statistics not found. Model may need retraining.")
        
        # Normalize score
        normalized_score = self._normalize_score(raw_score, self.score_min, self.score_max)
        
        # Determine severity
        severity = self._get_severity(normalized_score)
        
        # Generate explanation
        if severity == "NORMAL":
            message = "Composition appears normal with expected characteristics."
        elif severity == "LOW":
            message = "Minor deviation detected. Reading is within acceptable variance."
        elif severity == "MEDIUM":
            message = "Moderate anomaly detected. Consider verifying sensor calibration."
        else:
            message = "High anomaly detected. Potential sensor drift or unstable melt chemistry."
        
        return {
            "anomaly_score": float(normalized_score),
            "severity": severity,
            "message": message,
            "raw_score": float(raw_score)
        }
    
    def predict_batch(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Predict anomaly scores for multiple samples
        
        Args:
            df: DataFrame with composition data
            
        Returns:
            DataFrame with added anomaly predictions
        """
        if not self.is_trained:
            raise ValueError("Model is not trained. Call train() first.")
        
        X = self.prepare_features(df)
        X_scaled = self.scaler.transform(X)
        
        # Get predictions
        raw_scores = self.model.score_samples(X_scaled)
        predictions = self.model.predict(X_scaled)
        
        # Normalize scores
        score_min = raw_scores.min()
        score_max = raw_scores.max()
        normalized_scores = np.array([
            self._normalize_score(score, score_min, score_max) 
            for score in raw_scores
        ])
        
        # Get severity levels
        severities = [self._get_severity(score) for score in normalized_scores]
        
        # Add to dataframe
        result_df = df.copy()
        result_df['anomaly_score'] = normalized_scores
        result_df['anomaly_severity'] = severities
        result_df['is_anomaly'] = predictions == -1
        
        return result_df
    
    def save(self, filepath: str):
        """Save model and scaler"""
        if not self.is_trained:
            raise ValueError("Cannot save untrained model")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'elements': self.elements,
            'is_trained': self.is_trained,
            'score_min': self.score_min,
            'score_max': self.score_max
        }
        
        joblib.dump(model_data, filepath)
        print(f"Model saved to {filepath}")
    
    def load(self, filepath: str):
        """Load model and scaler"""
        model_data = joblib.load(filepath)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.elements = model_data['elements']
        self.is_trained = model_data['is_trained']
        self.score_min = model_data.get('score_min', None)
        self.score_max = model_data.get('score_max', None)
        
        print(f"Model loaded from {filepath}")
    
    def evaluate(self, df: pd.DataFrame, true_label_col: str = 'is_deviated'):
        """
        Evaluate model performance
        
        Args:
            df: DataFrame with true labels
            true_label_col: Column name for true labels
        """
        if not self.is_trained:
            raise ValueError("Model is not trained")
        
        result_df = self.predict_batch(df)
        
        # Calculate metrics
        true_labels = df[true_label_col].values
        predicted_anomalies = result_df['is_anomaly'].values
        
        from sklearn.metrics import classification_report, confusion_matrix
        
        print("\n" + "="*60)
        print("ANOMALY DETECTION EVALUATION")
        print("="*60)
        
        print("\nClassification Report:")
        print(classification_report(true_labels, predicted_anomalies, 
                                   target_names=['Normal', 'Anomaly']))
        
        print("\nConfusion Matrix:")
        cm = confusion_matrix(true_labels, predicted_anomalies)
        print(f"                Predicted Normal  Predicted Anomaly")
        print(f"Actual Normal        {cm[0][0]:8d}         {cm[0][1]:8d}")
        print(f"Actual Anomaly       {cm[1][0]:8d}         {cm[1][1]:8d}")
        
        print("\n" + "="*60)


if __name__ == "__main__":
    # Test the agent
    print("Anomaly Detection Agent Test")
    
    # This would normally be run with actual data
    # from training script
