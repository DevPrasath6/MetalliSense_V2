"""
Training Script for Anomaly Detection Agent
"""
import sys
from pathlib import Path
import pandas as pd

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from agents.anomaly_agent import AnomalyDetectionAgent
from config import DATASET_PATH, ANOMALY_MODEL_PATH, ANOMALY_CONTAMINATION


def train_anomaly_model(dataset_path: str = None, save_path: str = None):
    """
    Train and save anomaly detection model
    
    Args:
        dataset_path: Path to training dataset CSV
        save_path: Path to save trained model
    """
    if dataset_path is None:
        dataset_path = DATASET_PATH
    if save_path is None:
        save_path = ANOMALY_MODEL_PATH
    
    print("="*60)
    print("ANOMALY DETECTION AGENT TRAINING")
    print("="*60)
    
    # Load dataset
    print(f"\nLoading dataset from: {dataset_path}")
    df = pd.read_csv(dataset_path)
    print(f"Dataset shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    
    # CRITICAL FIX: Train ONLY on normal samples that are CLOSE TO SPEC
    if 'is_deviated' in df.columns:
        df_normal = df[df['is_deviated'] == False].copy()
        
        # Additional filtering: Only use samples that are within 1.5 std dev of mean
        # This creates a much tighter "normal" distribution
        filtered_samples = []
        for element in ['Fe', 'C', 'Si', 'Mn', 'P', 'S']:
            mean = df_normal[element].mean()
            std = df_normal[element].std()
            # Keep only samples within 1.5 standard deviations
            mask = (df_normal[element] >= mean - 1.5*std) & (df_normal[element] <= mean + 1.5*std)
            filtered_samples.append(mask)
        
        # Combine all masks (sample must be within 1.5 std for ALL elements)
        combined_mask = filtered_samples[0]
        for mask in filtered_samples[1:]:
            combined_mask = combined_mask & mask
        
        df_filtered = df_normal[combined_mask].copy()
        
        print(f"\n{'='*60}")
        print("⚠️  TRAINING ON TIGHTLY FILTERED NORMAL SAMPLES")
        print(f"{'='*60}")
        print(f"Original dataset: {len(df):,} samples")
        print(f"Normal samples: {len(df_normal):,} samples ({len(df_normal)/len(df)*100:.1f}%)")
        print(f"Tightly filtered (within 1.5σ): {len(df_filtered):,} samples ({len(df_filtered)/len(df_normal)*100:.1f}% of normal)")
        print(f"Deviated samples excluded: {len(df)-len(df_normal):,} samples")
        print("\nThis creates a tight definition of 'normal' for sensitive detection!")
        
        # Show what ranges we're actually using for training
        print(f"\nTraining data ranges (1.5σ filtering):")
        for element in ['Fe', 'C', 'Si', 'Mn', 'P', 'S']:
            print(f"  {element}: [{df_filtered[element].min():.2f}, {df_filtered[element].max():.2f}]")
        
        df_train = df_filtered
    else:
        print("\n⚠️  Warning: 'is_deviated' column not found, using full dataset")
        df_train = df
    
    # Initialize agent
    agent = AnomalyDetectionAgent()
    
    # Train model
    train_stats = agent.train(df_train, contamination=ANOMALY_CONTAMINATION)
    
    # Evaluate on training data
    print("\n" + "="*60)
    print("EVALUATION ON TRAINING DATA")
    print("="*60)
    agent.evaluate(df, true_label_col='is_deviated')
    
    # Save model
    print(f"\nSaving model to: {save_path}")
    agent.save(save_path)
    
    # Test prediction on sample
    print("\n" + "="*60)
    print("SAMPLE PREDICTION TEST")
    print("="*60)
    
    # Test with normal sample
    normal_sample = df[df['is_deviated'] == False].iloc[0]
    normal_comp = {col: normal_sample[col] for col in agent.elements}
    
    print("\nTest 1: Normal Sample")
    print(f"Composition: {normal_comp}")
    result = agent.predict(normal_comp)
    print(f"Result: {result}")
    
    # Test with deviated sample
    deviated_sample = df[df['is_deviated'] == True].iloc[0]
    deviated_comp = {col: deviated_sample[col] for col in agent.elements}
    
    print("\nTest 2: Deviated Sample")
    print(f"Composition: {deviated_comp}")
    result = agent.predict(deviated_comp)
    print(f"Result: {result}")
    
    print("\n" + "="*60)
    print("TRAINING COMPLETED SUCCESSFULLY")
    print("="*60)
    
    return agent, train_stats


if __name__ == "__main__":
    train_anomaly_model()
