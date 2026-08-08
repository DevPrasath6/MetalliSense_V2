"""
Retrain Models with New Dataset Script
Use this script to retrain models with real production data instead of synthetic data
"""
import sys
from pathlib import Path
import pandas as pd
import argparse

# Add app to path
sys.path.append(str(Path(__file__).parent / "app"))

from app.config import (
    ANOMALY_MODEL_PATH,
    ALLOY_MODEL_PATH,
    ANOMALY_CONTAMINATION
)


def validate_dataset(df: pd.DataFrame) -> bool:
    """
    Validate that the dataset has required columns and format
    
    Args:
        df: Input DataFrame
        
    Returns:
        True if valid, raises ValueError if not
    """
    required_columns = ['Fe', 'C', 'Si', 'Mn', 'P', 'S', 'grade']
    
    # Check required columns
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    # Check for optional columns
    if 'is_deviated' in df.columns:
        print("✓ Found 'is_deviated' column for anomaly training")
    else:
        print("⚠ No 'is_deviated' column - will train without labels")
    
    # Check for target columns (for alloy correction)
    target_cols = [f'target_{el}' for el in ['Fe', 'C', 'Si', 'Mn', 'P', 'S']]
    has_targets = all(col in df.columns for col in target_cols)
    if has_targets:
        print("✓ Found target columns for alloy correction training")
    else:
        print("⚠ No target columns - will generate from grade specifications")
    
    # Check data types
    element_cols = ['Fe', 'C', 'Si', 'Mn', 'P', 'S']
    for col in element_cols:
        if not pd.api.types.is_numeric_dtype(df[col]):
            raise ValueError(f"Column {col} must be numeric")
          
    # Check for negative values
    for col in element_cols:
        if (df[col] < 0).any():
            raise ValueError(f"Column {col} contains negative values")
    
    # Check for missing values
    if df[element_cols].isnull().any().any():
        raise ValueError("Dataset contains missing values in element columns")
    
    print(f"✓ Dataset validation passed")
    return True


def prepare_dataset_for_training(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare dataset for training by adding necessary columns if missing
    
    Args:
        df: Input DataFrame
        
    Returns:
        Prepared DataFrame
    """
    from app.data.grade_specs import GradeSpecificationGenerator
    
    df_prepared = df.copy()
    
    # Generate target columns if missing
    target_cols = [f'target_{el}' for el in ['Fe', 'C', 'Si', 'Mn', 'P', 'S']]
    if not all(col in df_prepared.columns for col in target_cols):
        print("\nGenerating target values from grade specifications...")
        
        grade_gen = GradeSpecificationGenerator()
        
        for idx, row in df_prepared.iterrows():
            grade = row['grade']
            spec = grade_gen.get_grade_spec(grade)
            
            if spec:
                comp_ranges = spec['composition_ranges']
                for element in ['Fe', 'C', 'Si', 'Mn', 'P', 'S']:
                    target_col = f'target_{element}'
                    if target_col not in df_prepared.columns:
                        # Use midpoint of range as target
                        min_val, max_val = comp_ranges[element]
                        df_prepared.at[idx, target_col] = (min_val + max_val) / 2
        
        print("✓ Generated target values from grade specifications")
    
    # Generate is_deviated column if missing
    if 'is_deviated' not in df_prepared.columns:
        print("\nGenerating deviation labels...")
        
        grade_gen = GradeSpecificationGenerator()
        deviation_threshold = 0.15  # 15% deviation from spec
        
        deviations = []
        for idx, row in df_prepared.iterrows():
            grade = row['grade']
            spec = grade_gen.get_grade_spec(grade)
            
            is_deviated = False
            if spec:
                comp_ranges = spec['composition_ranges']
                for element in ['Fe', 'C', 'Si', 'Mn', 'P', 'S']:
                    min_val, max_val = comp_ranges[element]
                    actual_val = row[element]
                    
                    # Check if outside spec range
                    if actual_val < min_val or actual_val > max_val:
                        is_deviated = True
                        break
            
            deviations.append(1 if is_deviated else 0)
        
        df_prepared['is_deviated'] = deviations
        print(f"✓ Generated deviation labels: {sum(deviations)} anomalies / {len(deviations)} total")
    
    return df_prepared


def train_anomaly_model(dataset_path: str, contamination: float = None):
    """
    Train anomaly detection model on new dataset
    
    Args:
        dataset_path: Path to new dataset CSV
        contamination: Expected proportion of anomalies (0-0.5)
    """
    from app.agents.anomaly_agent import AnomalyDetectionAgent
    
    print("\n" + "="*70)
    print(" TRAINING ANOMALY DETECTION MODEL")
    print("="*70)
    
    # Load dataset
    print(f"\nLoading dataset from: {dataset_path}")
    df = pd.read_csv(dataset_path)
    print(f"Dataset shape: {df.shape}")
    print(f"Samples: {len(df)}")
    
    # Validate
    validate_dataset(df)
    
    # Prepare dataset
    df = prepare_dataset_for_training(df)
    
    # Initialize agent
    agent = AnomalyDetectionAgent()
    
    # Use provided contamination or calculate from data
    if contamination is None:
        if 'is_deviated' in df.columns:
            contamination = df['is_deviated'].mean()
            print(f"\nCalculated contamination from data: {contamination:.3f}")
        else:
            contamination = ANOMALY_CONTAMINATION
            print(f"\nUsing default contamination: {contamination}")
    
    # Train model
    print(f"\nTraining with contamination={contamination:.3f}...")
    train_stats = agent.train(df, contamination=contamination)
    
    # Evaluate if labels available
    if 'is_deviated' in df.columns:
        print("\n" + "="*70)
        print(" EVALUATION ON TRAINING DATA")
        print("="*70)
        agent.evaluate(df, true_label_col='is_deviated')
    
    # Save model
    print(f"\nSaving model to: {ANOMALY_MODEL_PATH}")
    ANOMALY_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    agent.save(str(ANOMALY_MODEL_PATH))
    print("✓ Anomaly model saved successfully")
    
    return agent, train_stats


def train_alloy_model(dataset_path: str, test_size: float = 0.2):
    """
    Train alloy correction model on new dataset
    
    Args:
        dataset_path: Path to new dataset CSV
        test_size: Proportion of data to use for testing (0-1)
    """
    from app.agents.alloy_agent import AlloyCorrectionAgent
    from app.data.grade_specs import GradeSpecificationGenerator
    
    print("\n" + "="*70)
    print(" TRAINING ALLOY CORRECTION MODEL")
    print("="*70)
    
    # Load dataset
    print(f"\nLoading dataset from: {dataset_path}")
    df = pd.read_csv(dataset_path)
    print(f"Dataset shape: {df.shape}")
    print(f"Samples: {len(df)}")
    
    # Validate
    validate_dataset(df)
    
    # Prepare dataset
    df = prepare_dataset_for_training(df)
    
    # Initialize grade generator and agent
    grade_generator = GradeSpecificationGenerator()
    agent = AlloyCorrectionAgent(grade_generator)
    
    # Train model
    print(f"\nTraining with test_size={test_size}...")
    train_stats = agent.train(df, test_size=test_size)
    
    # Save model
    print(f"\nSaving model to: {ALLOY_MODEL_PATH}")
    ALLOY_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    agent.save(str(ALLOY_MODEL_PATH))
    print("✓ Alloy correction model saved successfully")
    
    return agent, train_stats


def test_models():
    """Quick test of trained models"""
    print("\n" + "="*70)
    print(" TESTING TRAINED MODELS")
    print("="*70)
    
    try:
        from app.inference.anomaly_predict import get_anomaly_predictor
        from app.inference.alloy_predict import get_alloy_predictor
        
        anomaly_pred = get_anomaly_predictor()
        alloy_pred = get_alloy_predictor()
        
        print("✓ Models loaded successfully")
        
        # Test composition
        test_comp = {
            "Fe": 85.0,
            "C": 3.5,
            "Si": 2.2,
            "Mn": 0.7,
            "P": 0.04,
            "S": 0.02
        }
        
        print("\nTest Composition:", test_comp)
        
        # Test anomaly detection
        anomaly_result = anomaly_pred.predict(test_comp)
        print(f"\nAnomaly Detection:")
        print(f"  Score: {anomaly_result['anomaly_score']:.4f}")
        print(f"  Severity: {anomaly_result['severity']}")
        print(f"  Message: {anomaly_result['message']}")
        
        # Test alloy correction
        alloy_result = alloy_pred.predict("SG-IRON", test_comp)
        print(f"\nAlloy Correction (SG-IRON):")
        print(f"  Confidence: {alloy_result['confidence']:.4f}")
        if alloy_result['recommended_additions']:
            print("  Recommended Additions:")
            for element, amount in alloy_result['recommended_additions'].items():
                if amount > 0:
                    print(f"    {element}: +{amount:.4f}%")
        
        print("\n✓ Model inference working correctly")
        return True
        
    except Exception as e:
        print(f"\n✗ Model test failed: {e}")
        return False


def main():
    """Main retraining workflow"""
    parser = argparse.ArgumentParser(
        description="Retrain MetalliSense AI models with new dataset"
    )
    parser.add_argument(
        'dataset',
        type=str,
        help='Path to new dataset CSV file'
    )
    parser.add_argument(
        '--anomaly-only',
        action='store_true',
        help='Only retrain anomaly detection model'
    )
    parser.add_argument(
        '--alloy-only',
        action='store_true',
        help='Only retrain alloy correction model'
    )
    parser.add_argument(
        '--contamination',
        type=float,
        default=None,
        help='Expected proportion of anomalies (default: auto-detect or 0.35)'
    )
    parser.add_argument(
        '--test-size',
        type=float,
        default=0.2,
        help='Proportion of data for testing (default: 0.2)'
    )
    parser.add_argument(
        '--skip-validation',
        action='store_true',
        help='Skip final model testing'
    )
    
    args = parser.parse_args()
    
    # Verify dataset exists
    dataset_path = Path(args.dataset)
    if not dataset_path.exists():
        print(f"❌ Error: Dataset file not found: {dataset_path}")
        sys.exit(1)
    
    print("\n" + "="*70)
    print(" METALLISENSE AI - MODEL RETRAINING")
    print("="*70)
    print(f"\nDataset: {dataset_path}")
    print(f"File size: {dataset_path.stat().st_size / 1024 / 1024:.2f} MB")
    
    try:
        # Train models based on flags
        if not args.alloy_only:
            train_anomaly_model(str(dataset_path), args.contamination)
        
        if not args.anomaly_only:
            train_alloy_model(str(dataset_path), args.test_size)
        
        # Test models
        if not args.skip_validation:
            test_models()
        
        # Success summary
        print("\n" + "="*70)
        print(" RETRAINING COMPLETED SUCCESSFULLY!")
        print("="*70)
        
        print("\nModels Updated:")
        if not args.alloy_only:
            print(f"  ✓ Anomaly Detection: {ANOMALY_MODEL_PATH}")
        if not args.anomaly_only:
            print(f"  ✓ Alloy Correction: {ALLOY_MODEL_PATH}")
        
        print("\nNext Steps:")
        print("  1. Restart the API service to load new models:")
        print("     python app/main.py")
        print("")
        print("  2. Test with new predictions:")
        print("     python test_api.py")
        print("")
        print("  3. Monitor model performance in production")
        print("")
        
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Retraining failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    # If no arguments, show help
    if len(sys.argv) == 1:
        print("\n" + "="*70)
        print(" METALLISENSE AI - MODEL RETRAINING SCRIPT")
        print("="*70)
        print("\nUsage Examples:")
        print("\n  Basic retraining with new dataset:")
        print("    python retrain.py data/production_data.csv")
        print("\n  Retrain only anomaly detection:")
        print("    python retrain.py data/production_data.csv --anomaly-only")
        print("\n  Retrain only alloy correction:")
        print("    python retrain.py data/production_data.csv --alloy-only")
        print("\n  Custom contamination rate:")
        print("    python retrain.py data/production_data.csv --contamination 0.25")
        print("\n  Custom test split:")
        print("    python retrain.py data/production_data.csv --test-size 0.3")
        print("\nDataset Requirements:")
        print("  Required columns: Fe, C, Si, Mn, P, S, grade")
        print("  Optional columns: is_deviated, target_Fe, target_C, target_Si, target_Mn, target_P, target_S")
        print("  Format: CSV file with header row")
        print("\n" + "="*70 + "\n")
        sys.exit(0)
    
    main()
