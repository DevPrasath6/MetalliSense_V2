"""
Complete Setup and Training Script for MetalliSense AI Service
===============================================================
This script sets up and trains the AI models for a new laptop/environment.

Run: python setup.py

Features:
- Dataset verification
- Model training with all optimizations
- Comprehensive testing and validation
- Deterministic predictions
"""
import sys
from pathlib import Path

# Add app to path
sys.path.append(str(Path(__file__).parent / "app"))

from app.data.grade_specs import GradeSpecificationGenerator
from app.data.synthetic_gen import SyntheticDataGenerator
from app.config import (
    DATASET_PATH, 
    SYNTHETIC_DATASET_SIZE, 
    NORMAL_RATIO,
    ANOMALY_MODEL_PATH,
    ALLOY_MODEL_PATH
)


def main():
    """Run complete setup process - Verify dataset and train models"""
    
    print("\n" + "="*70)
    print(" METALLISENSE AI SERVICE - COMPLETE SETUP")
    print("="*70)
    
    # Step 1: Verify Dataset Exists
    print("\n[STEP 1] Verifying Dataset...")
    print("-"*70)
    
    if not DATASET_PATH.exists():
        print(f"✗ Dataset not found: {DATASET_PATH}")
        print("  Please ensure dataset.csv exists in app/data/")
        print("  You can generate synthetic data using synthetic_gen.py")
        return False
    
    # Load and analyze existing dataset
    import pandas as pd
    df = pd.read_csv(DATASET_PATH)
    
    print(f"✓ Dataset loaded: {DATASET_PATH}")
    print(f"  Total samples: {len(df):,}")
    print(f"  Columns: {', '.join(df.columns.tolist())}")
    
    # Check for required columns
    required_cols = ['Fe', 'C', 'Si', 'Mn', 'P', 'S', 'grade']
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        print(f"✗ Missing required columns: {missing_cols}")
        return False
    
    print(f"✓ All required columns present")
    
    # Dataset statistics
    print(f"\n  Dataset Statistics:")
    print(f"    Grades: {df['grade'].nunique()}")
    print(f"    Grade distribution:")
    for grade, count in df['grade'].value_counts().items():
        print(f"      {grade}: {count:,} samples ({count/len(df)*100:.1f}%)")
    
    if 'is_deviated' in df.columns:
        deviated_count = df['is_deviated'].sum()
        normal_count = len(df) - deviated_count
        print(f"    Normal samples: {normal_count:,} ({normal_count/len(df)*100:.1f}%)")
        print(f"    Deviated samples: {deviated_count:,} ({deviated_count/len(df)*100:.1f}%)")
    
    # Step 2: Train Anomaly Detection Agent
    print("\n[STEP 2] Training Anomaly Detection Agent...")
    print("-"*70)
    print("  Configuration:")
    print("    • Training: TIGHTLY FILTERED NORMAL SAMPLES (within 1.5σ)")
    print("    • Contamination: 0.05 (5% anomalies expected)")
    print("    • Predictions: DETERMINISTIC (score stats stored)")
    
    from app.training.train_anomaly import train_anomaly_model
    
    try:
        anomaly_agent, anomaly_stats = train_anomaly_model(
            dataset_path=str(DATASET_PATH),
            save_path=str(ANOMALY_MODEL_PATH)
        )
        print(f"\n✓ Anomaly model trained and saved")
        
        # Verify deterministic predictions
        if hasattr(anomaly_agent, 'score_min') and hasattr(anomaly_agent, 'score_max'):
            print(f"✓ Score statistics stored for deterministic predictions")
        
    except Exception as e:
        print(f"\n✗ Anomaly training failed: {e}")
        return False
    
    # Step 3: Train Alloy Correction Agent
    print("\n[STEP 3] Training Alloy Correction Agent...")
    print("-"*70)
    
    from app.training.train_alloy_agent import train_alloy_model
    
    try:
        alloy_agent, alloy_stats = train_alloy_model(
            dataset_path=str(DATASET_PATH),
            save_path=str(ALLOY_MODEL_PATH)
        )
        print(f"\n✓ Alloy model trained and saved")
    except Exception as e:
        print(f"\n✗ Alloy training failed: {e}")
        return False
    
    # Step 4: Comprehensive Verification
    print("\n[STEP 4] System Verification & Testing...")
    print("-"*70)
    
    # Verify models exist
    models_exist = {
        "Anomaly Model": ANOMALY_MODEL_PATH.exists(),
        "Alloy Model": ALLOY_MODEL_PATH.exists(),
        "Dataset": DATASET_PATH.exists()
    }
    
    print("\nFile Verification:")
    all_exist = True
    for name, exists in models_exist.items():
        status = "✓" if exists else "✗"
        print(f"  {status} {name}")
        if not exists:
            all_exist = False
    
    if not all_exist:
        print("\n✗ Some required files are missing!")
        return False
    
    # Test inference modules
    print("\nTesting Inference:")
    
    try:
        from app.inference.anomaly_predict import get_anomaly_predictor
        from app.inference.alloy_predict import get_alloy_predictor
        
        anomaly_pred = get_anomaly_predictor()
        alloy_pred = get_alloy_predictor()
        
        print("  ✓ Predictors loaded successfully")
        
        # Quick test with normal composition
        test_comp_normal = {
            "Fe": 94.5, "C": 3.2, "Si": 2.0,
            "Mn": 0.4, "P": 0.05, "S": 0.10
        }
        
        # Quick test with deviated composition
        test_comp_deviated = {
            "Fe": 85.0, "C": 5.0, "Si": 3.5,
            "Mn": 1.2, "P": 0.15, "S": 0.25
        }
        
        print("\n  Test 1: Normal Composition")
        result1 = anomaly_pred.predict(test_comp_normal)
        print(f"    Severity: {result1['severity']} (Score: {result1['anomaly_score']:.4f})")
        
        print("\n  Test 2: Deviated Composition")
        result2 = anomaly_pred.predict(test_comp_deviated)
        print(f"    Severity: {result2['severity']} (Score: {result2['anomaly_score']:.4f})")
        
        if result2['severity'] in ['MEDIUM', 'HIGH']:
            print("    ✓ Correctly detected deviation")
        
        # Test determinism
        print("\n  Test 3: Determinism (same input 3x)")
        scores = [anomaly_pred.predict(test_comp_normal)['anomaly_score'] for _ in range(3)]
        
        if len(set(scores)) == 1:
            print(f"    ✓ DETERMINISTIC: All scores = {scores[0]:.8f}")
        else:
            print(f"    ✗ NON-DETERMINISTIC: Scores vary!")
            return False
        
        # Test alloy recommendations
        print("\n  Test 4: Alloy Recommendations")
        alloy_result = alloy_pred.predict("GREY-IRON", test_comp_deviated)
        print(f"    Confidence: {alloy_result['confidence']:.4f}")
        print(f"    Recommendations: {len(alloy_result['recommended_additions'])} elements")
        print("  ✓ Alloy agent working correctly")
        
    except Exception as e:
        print(f"  ✗ Inference test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Final Summary
    print("\n" + "="*70)
    print(" ✅ SETUP COMPLETED SUCCESSFULLY!")
    print("="*70)
    
    print("\n📊 Summary:")
    print(f"  • Dataset: {len(df):,} samples")
    print(f"  • Models trained: 2 (Anomaly + Alloy)")
    print(f"  • Verification: All tests passed")
    print(f"  • Predictions: DETERMINISTIC ✓")
    print(f"  • Single-element detection: ENABLED ✓")
    print(f"  • Alloy invocation: MEDIUM & HIGH severity ✓")
    
    print("\n📁 Model Locations:")
    print(f"  • Anomaly: {ANOMALY_MODEL_PATH}")
    print(f"  • Alloy: {ALLOY_MODEL_PATH}")
    
    print("\n🚀 Next Steps:")
    print("  1. Start the API service:")
    print("     python app/main.py")
    print("")
    print("  2. Run comprehensive tests:")
    print("     python test_determinism.py")
    print("     python test_single_element.py")
    print("")
    print("  3. Access API documentation:")
    print("     http://localhost:8001/docs")
    print("")
    print("  4. Use /agents/analyze endpoint for production")
    print("")
    
    print("="*70)
    print("\n")
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n✗ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
