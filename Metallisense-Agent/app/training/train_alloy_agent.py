"""
Training Script for Alloy Correction Agent
"""
import sys
from pathlib import Path
import pandas as pd

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from agents.alloy_agent import AlloyCorrectionAgent
from data.grade_specs import GradeSpecificationGenerator
from config import DATASET_PATH, ALLOY_MODEL_PATH


def train_alloy_model(dataset_path: str = None, save_path: str = None):
    """
    Train and save alloy correction model
    
    Args:
        dataset_path: Path to training dataset CSV
        save_path: Path to save trained model
    """
    if dataset_path is None:
        dataset_path = DATASET_PATH
    if save_path is None:
        save_path = ALLOY_MODEL_PATH
    
    print("="*60)
    print("ALLOY CORRECTION AGENT TRAINING")
    print("="*60)
    
    # Load dataset
    print(f"\nLoading dataset from: {dataset_path}")
    df = pd.read_csv(dataset_path)
    print(f"Dataset shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    
    # Initialize grade generator
    grade_generator = GradeSpecificationGenerator()
    
    # Initialize agent
    agent = AlloyCorrectionAgent(grade_generator)
    
    # Train model
    train_stats = agent.train(df, test_size=0.2)
    
    # Save model
    print(f"\nSaving model to: {save_path}")
    agent.save(save_path)
    
    # Test predictions on samples
    print("\n" + "="*60)
    print("SAMPLE PREDICTION TESTS")
    print("="*60)
    
    # Test with normal sample (should need minimal corrections)
    normal_sample = df[df['is_deviated'] == False].iloc[0]
    grade = normal_sample['grade']
    normal_comp = {col: normal_sample[col] for col in agent.elements}
    
    print(f"\nTest 1: Normal Sample ({grade})")
    print(f"Composition: {normal_comp}")
    result = agent.predict(grade, normal_comp)
    print(f"Recommended Additions: {result['recommended_additions']}")
    print(f"Confidence: {result['confidence']:.4f}")
    print(f"Message: {result['message']}")
    if result['warning']:
        print(f"Warning: {result['warning']}")
    
    # Test with deviated sample (should recommend corrections)
    deviated_sample = df[df['is_deviated'] == True].iloc[0]
    grade = deviated_sample['grade']
    deviated_comp = {col: deviated_sample[col] for col in agent.elements}
    
    print(f"\nTest 2: Deviated Sample ({grade})")
    print(f"Composition: {deviated_comp}")
    result = agent.predict(grade, deviated_comp)
    print(f"Recommended Additions: {result['recommended_additions']}")
    print(f"Confidence: {result['confidence']:.4f}")
    print(f"Message: {result['message']}")
    if result['warning']:
        print(f"Warning: {result['warning']}")
    
    # Test with another grade
    if len(df['grade'].unique()) > 1:
        other_grade = df['grade'].unique()[1]
        other_sample = df[df['grade'] == other_grade].iloc[0]
        other_comp = {col: other_sample[col] for col in agent.elements}
        
        print(f"\nTest 3: Different Grade ({other_grade})")
        print(f"Composition: {other_comp}")
        result = agent.predict(other_grade, other_comp)
        print(f"Recommended Additions: {result['recommended_additions']}")
        print(f"Confidence: {result['confidence']:.4f}")
        print(f"Message: {result['message']}")
        if result['warning']:
            print(f"Warning: {result['warning']}")
    
    print("\n" + "="*60)
    print("TRAINING COMPLETED SUCCESSFULLY")
    print("="*60)
    
    return agent, train_stats


if __name__ == "__main__":
    train_alloy_model()
