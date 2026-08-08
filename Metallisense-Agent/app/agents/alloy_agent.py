"""
Agent 4: Alloy Correction Agent
Multi-output regression model for recommending alloy additions
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
from typing import Dict, List, Tuple
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from config import ELEMENTS, RANDOM_STATE, MAX_ADDITION_PERCENTAGE, MIN_CONFIDENCE_THRESHOLD
from data.grade_specs import GradeSpecificationGenerator


class AlloyCorrectionAgent:
    """
    Alloy Correction Agent using Multi-Output Regression
    
    Purpose:
    - Given deviated composition, recommend alloy additions
    - Bring composition back into grade specification
    - Does NOT decide if metal is good/bad
    - Only answers: "What alloy additions will correct the deviation?"
    """
    
    def __init__(self, grade_generator: GradeSpecificationGenerator):
        self.model = None
        self.scaler_X = StandardScaler()
        self.scaler_y = StandardScaler()
        self.grade_generator = grade_generator
        self.elements = ELEMENTS
        self.is_trained = False
        self.grade_encodings = {}
        
    def _encode_grade(self, grade: str) -> int:
        """Encode grade as integer"""
        if grade not in self.grade_encodings:
            self.grade_encodings[grade] = len(self.grade_encodings)
        return self.grade_encodings[grade]
    
    def _prepare_training_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare training data with correction deltas
        
        Strategy:
        1. For each sample, calculate deviation from grade midpoint
        2. Compute required additions to reach midpoint
        3. Train model to predict these additions
        
        Args:
            df: DataFrame with composition and grade information
            
        Returns:
            X (features), y (target additions)
        """
        X_list = []
        y_list = []
        
        for idx, row in df.iterrows():
            grade = row['grade']
            
            # Current composition
            current_comp = {el: row[el] for el in self.elements}
            
            # Target composition (grade midpoint)
            target_comp = self.grade_generator.get_composition_midpoint(grade)
            
            # Calculate required additions (delta to reach target)
            additions = {}
            for element in self.elements:
                delta = target_comp[element] - current_comp[element]
                # Only positive additions (we can only add, not remove)
                # For elements above target, set addition to 0
                additions[element] = max(0.0, delta)
            
            # Create feature vector: [encoded_grade, current_composition]
            grade_encoded = self._encode_grade(grade)
            features = [grade_encoded] + [current_comp[el] for el in self.elements]
            
            # Target vector: additions for each element
            targets = [additions[el] for el in self.elements]
            
            X_list.append(features)
            y_list.append(targets)
        
        return np.array(X_list), np.array(y_list)
    
    def train(self, df: pd.DataFrame, test_size: float = 0.2):
        """
        Train alloy correction model
        
        Args:
            df: Training DataFrame with composition and grade
            test_size: Proportion of data for testing
        """
        print("Training Alloy Correction Agent...")
        print(f"Training samples: {len(df)}")
        
        # Prepare training data
        X, y = self._prepare_training_data(df)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=RANDOM_STATE
        )
        
        print(f"Train samples: {len(X_train)}")
        print(f"Test samples: {len(X_test)}")
        
        # Scale features
        X_train_scaled = self.scaler_X.fit_transform(X_train)
        X_test_scaled = self.scaler_X.transform(X_test)
        
        # Scale targets
        y_train_scaled = self.scaler_y.fit_transform(y_train)
        
        # Train multi-output gradient boosting regressor
        base_estimator = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=RANDOM_STATE,
            verbose=0
        )
        
        self.model = MultiOutputRegressor(base_estimator, n_jobs=-1)
        
        print("\nTraining model...")
        self.model.fit(X_train_scaled, y_train_scaled)
        self.is_trained = True
        
        # Evaluate on test set
        y_pred_scaled = self.model.predict(X_test_scaled)
        y_pred = self.scaler_y.inverse_transform(y_pred_scaled)
        
        # Calculate metrics
        from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
        
        mse = mean_squared_error(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        print(f"\nTraining Results:")
        print(f"  MSE: {mse:.6f}")
        print(f"  MAE: {mae:.6f}")
        print(f"  R² Score: {r2:.4f}")
        
        # Per-element performance
        print(f"\nPer-Element MAE:")
        for i, element in enumerate(self.elements):
            element_mae = mean_absolute_error(y_test[:, i], y_pred[:, i])
            print(f"  {element}: {element_mae:.6f}")
        
        return {
            "mse": float(mse),
            "mae": float(mae),
            "r2_score": float(r2),
            "test_samples": len(X_test)
        }
    
    def _calculate_confidence(self, additions: Dict[str, float], 
                             current_comp: Dict[str, float],
                             grade: str) -> float:
        """
        Calculate confidence score for recommendations
        
        Based on:
        - Magnitude of additions required
        - Whether additions are within safe limits
        - How far current composition is from target
        """
        spec = self.grade_generator.get_grade_spec(grade)
        target_comp = self.grade_generator.get_composition_midpoint(grade)
        
        # Factor 1: Total addition magnitude (lower is better)
        total_addition = sum(additions.values())
        addition_factor = 1.0 - min(total_addition / 5.0, 1.0)  # Penalize large additions
        
        # Factor 2: Number of elements needing correction
        num_corrections = sum(1 for v in additions.values() if v > 0.01)
        correction_factor = 1.0 - (num_corrections / len(self.elements))
        
        # Factor 3: Distance from target
        total_deviation = sum(abs(current_comp[el] - target_comp[el]) 
                             for el in self.elements)
        deviation_factor = 1.0 - min(total_deviation / 10.0, 1.0)
        
        # Weighted average
        confidence = (0.4 * addition_factor + 
                     0.3 * correction_factor + 
                     0.3 * deviation_factor)
        
        return np.clip(confidence, 0, 1)
    
    def predict(self, grade: str, composition: Dict[str, float]) -> Dict:
        """
        Predict alloy additions for a given composition
        
        Args:
            grade: Target metal grade
            composition: Current composition
            
        Returns:
            Dictionary with recommended additions and confidence
        """
        if not self.is_trained:
            raise ValueError("Model is not trained. Call train() first.")
        
        if grade not in self.grade_encodings:
            return {
                "recommended_additions": {},
                "confidence": 0.0,
                "message": f"Unknown grade: {grade}",
                "warning": f"Grade not in training data: {grade}"
            }
        
        # Prepare features
        grade_encoded = self._encode_grade(grade)
        features = np.array([[grade_encoded] + [composition[el] for el in self.elements]])
        
        # Scale and predict
        features_scaled = self.scaler_X.transform(features)
        prediction_scaled = self.model.predict(features_scaled)
        prediction = self.scaler_y.inverse_transform(prediction_scaled)[0]
        
        # Convert to dictionary and apply safety constraints
        additions = {}
        for i, element in enumerate(self.elements):
            value = max(0.0, prediction[i])  # No negative additions
            
            # Apply maximum addition limit
            if value > MAX_ADDITION_PERCENTAGE:
                value = MAX_ADDITION_PERCENTAGE
                
            # Only include significant additions (> 0.01%)
            if value > 0.01:
                additions[element] = round(value, 4)
        
        # Calculate confidence
        confidence = self._calculate_confidence(additions, composition, grade)
        
        # Generate message
        if not additions:
            message = "Composition is close to target. No significant additions needed."
        elif confidence >= 0.8:
            message = "High confidence recommendation. Additions should bring composition into spec."
        elif confidence >= 0.6:
            message = "Moderate confidence. Consider verifying with metallurgical expert."
        else:
            message = "Low confidence. Large corrections needed. Manual review recommended."
        
        # Generate warnings
        warning = None
        if sum(additions.values()) > 3.0:
            warning = "Large total addition required (>3%). Consider re-melting or blending."
        elif confidence < MIN_CONFIDENCE_THRESHOLD:
            warning = f"Confidence below threshold ({MIN_CONFIDENCE_THRESHOLD}). Use with caution."
        
        return {
            "recommended_additions": additions,
            "confidence": float(confidence),
            "message": message,
            "warning": warning
        }
    
    def predict_batch(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Predict additions for multiple samples
        
        Args:
            df: DataFrame with grade and composition columns
            
        Returns:
            DataFrame with added prediction columns
        """
        if not self.is_trained:
            raise ValueError("Model is not trained")
        
        results = []
        for idx, row in df.iterrows():
            grade = row['grade']
            composition = {el: row[el] for el in self.elements}
            
            prediction = self.predict(grade, composition)
            results.append(prediction)
        
        result_df = df.copy()
        result_df['recommended_additions'] = [r['recommended_additions'] for r in results]
        result_df['correction_confidence'] = [r['confidence'] for r in results]
        
        return result_df
    
    def save(self, filepath: str):
        """Save model and scalers"""
        if not self.is_trained:
            raise ValueError("Cannot save untrained model")
        
        model_data = {
            'model': self.model,
            'scaler_X': self.scaler_X,
            'scaler_y': self.scaler_y,
            'grade_encodings': self.grade_encodings,
            'elements': self.elements,
            'is_trained': self.is_trained
        }
        
        joblib.dump(model_data, filepath)
        print(f"Model saved to {filepath}")
    
    def load(self, filepath: str):
        """Load model and scalers"""
        model_data = joblib.load(filepath)
        
        self.model = model_data['model']
        self.scaler_X = model_data['scaler_X']
        self.scaler_y = model_data['scaler_y']
        self.grade_encodings = model_data['grade_encodings']
        self.elements = model_data['elements']
        self.is_trained = model_data['is_trained']
        
        print(f"Model loaded from {filepath}")


if __name__ == "__main__":
    # Test the agent
    print("Alloy Correction Agent Test")
