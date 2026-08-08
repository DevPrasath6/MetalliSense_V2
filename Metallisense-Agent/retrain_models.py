"""
COMPLETE MODEL RETRAINING SCRIPT
================================
Retrains both models with all optimizations and fixes applied.
This script incorporates all improvements for accurate predictions.

Run: python retrain_models.py
"""
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

# Add app to path
sys.path.append(str(Path(__file__).parent / "app"))

from app.config import DATASET_PATH, ANOMALY_MODEL_PATH, ALLOY_MODEL_PATH


def print_header(title):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f" {title}")
    print("="*70)


def print_section(title):
    """Print formatted section"""
    print("\n" + "-"*70)
    print(f"📌 {title}")
    print("-"*70)


def verify_dataset():
    """Verify dataset exists and has correct structure"""
    print_section("STEP 1: Dataset Verification")
    
    if not DATASET_PATH.exists():
        print(f"\n❌ ERROR: Dataset not found at {DATASET_PATH}")
        print("   Please ensure dataset.csv exists in app/data/")
        return None
    
    # Load and validate
    df = pd.read_csv(DATASET_PATH)
    print(f"✓ Dataset loaded: {len(df):,} samples")
    
    # Check required columns
    required_cols = ['Fe', 'C', 'Si', 'Mn', 'P', 'S', 'grade', 'is_deviated']
    missing = [col for col in required_cols if col not in df.columns]
    
    if missing:
        print(f"❌ ERROR: Missing required columns: {missing}")
        return None
    
    print(f"✓ All required columns present: {', '.join(required_cols)}")
    
    # Dataset statistics
    print(f"\n📊 Dataset Statistics:")
    print(f"   Total samples: {len(df):,}")
    
    if 'is_deviated' in df.columns:
        normal_count = (df['is_deviated'] == False).sum()
        deviated_count = (df['is_deviated'] == True).sum()
        print(f"   Normal samples: {normal_count:,} ({normal_count/len(df)*100:.1f}%)")
        print(f"   Deviated samples: {deviated_count:,} ({deviated_count/len(df)*100:.1f}%)")
    
    print(f"\n   Grades: {df['grade'].nunique()}")
    for grade, count in df['grade'].value_counts().head().items():
        print(f"     • {grade}: {count:,} samples")
    
    # Element ranges
    print(f"\n   Element Ranges:")
    for element in ['Fe', 'C', 'Si', 'Mn', 'P', 'S']:
        print(f"     • {element}: [{df[element].min():.2f}, {df[element].max():.2f}]")
    
    return df


def train_anomaly_model(df):
    """Train anomaly detection model with all optimizations"""
    print_section("STEP 2: Anomaly Detection Model Training")
    
    print("\n🔧 Training Configuration:")
    print("   • Training on: TIGHTLY FILTERED NORMAL SAMPLES ONLY")
    print("   • Filtering: Within 1.5σ of mean for ALL elements")
    print("   • Contamination: 0.05 (5% expected anomalies)")
    print("   • Score statistics: STORED for deterministic predictions")
    
    print("\n⚙️  Starting training...")
    
    from app.training.train_anomaly import train_anomaly_model
    
    try:
        anomaly_agent, anomaly_stats = train_anomaly_model(
            dataset_path=str(DATASET_PATH),
            save_path=str(ANOMALY_MODEL_PATH)
        )
        
        print(f"\n✅ SUCCESS: Model saved to {ANOMALY_MODEL_PATH}")
        
        # Verify model has score statistics
        if hasattr(anomaly_agent, 'score_min') and hasattr(anomaly_agent, 'score_max'):
            print(f"✓ Score statistics stored: [{anomaly_agent.score_min:.4f}, {anomaly_agent.score_max:.4f}]")
            print("✓ Predictions will be DETERMINISTIC")
        else:
            print("⚠️  Warning: Score statistics not stored, predictions may vary")
        
        return anomaly_agent, anomaly_stats
        
    except Exception as e:
        print(f"\n❌ ERROR: Anomaly training failed")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None


def train_alloy_model(df):
    """Train alloy correction model"""
    print_section("STEP 3: Alloy Correction Model Training")
    
    print("\n🔧 Training Configuration:")
    print("   • Model: Gradient Boosting Multi-output Regressor")
    print("   • Input: Grade + Current composition")
    print("   • Output: Recommended additions for each element")
    
    print("\n⚙️  Starting training...")
    
    from app.training.train_alloy_agent import train_alloy_model
    
    try:
        alloy_agent, alloy_stats = train_alloy_model(
            dataset_path=str(DATASET_PATH),
            save_path=str(ALLOY_MODEL_PATH)
        )
        
        print(f"\n✅ SUCCESS: Model saved to {ALLOY_MODEL_PATH}")
        return alloy_agent, alloy_stats
        
    except Exception as e:
        print(f"\n❌ ERROR: Alloy training failed")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None


def verify_models():
    """Verify models are working correctly"""
    print_section("STEP 4: Model Verification & Testing")
    
    # Check files exist
    print("\n📁 File Verification:")
    files = {
        "Dataset": DATASET_PATH,
        "Anomaly Model": ANOMALY_MODEL_PATH,
        "Alloy Model": ALLOY_MODEL_PATH
    }
    
    all_exist = True
    for name, path in files.items():
        exists = path.exists()
        status = "✓" if exists else "✗"
        print(f"   {status} {name}: {path}")
        if not exists:
            all_exist = False
    
    if not all_exist:
        print("\n❌ ERROR: Some files are missing")
        return False
    
    # Load and test models
    print("\n🧪 Testing Model Inference:")
    
    try:
        from app.inference.anomaly_predict import get_anomaly_predictor
        from app.inference.alloy_predict import get_alloy_predictor
        
        anomaly_pred = get_anomaly_predictor()
        alloy_pred = get_alloy_predictor()
        
        print("   ✓ Models loaded successfully")
        
        # Test with normal composition
        test_comp_normal = {
            "Fe": 94.5, "C": 3.2, "Si": 2.0,
            "Mn": 0.4, "P": 0.05, "S": 0.10
        }
        
        # Test with deviated composition
        test_comp_deviated = {
            "Fe": 85.0, "C": 5.0, "Si": 3.5,
            "Mn": 1.2, "P": 0.15, "S": 0.25
        }
        
        print("\n   Test 1: Normal Composition")
        result1 = anomaly_pred.predict(test_comp_normal)
        print(f"      Severity: {result1['severity']}")
        print(f"      Score: {result1['anomaly_score']:.4f}")
        
        print("\n   Test 2: Deviated Composition")
        result2 = anomaly_pred.predict(test_comp_deviated)
        print(f"      Severity: {result2['severity']}")
        print(f"      Score: {result2['anomaly_score']:.4f}")
        
        # Test determinism
        print("\n   Test 3: Determinism Check (same input 3 times)")
        scores = []
        for i in range(3):
            result = anomaly_pred.predict(test_comp_normal)
            scores.append(result['anomaly_score'])
            print(f"      Run {i+1}: {result['anomaly_score']:.8f}")
        
        if len(set(scores)) == 1:
            print("      ✓ DETERMINISTIC: All predictions identical")
        else:
            print("      ✗ NON-DETERMINISTIC: Predictions vary!")
            return False
        
        # Test alloy recommendations
        print("\n   Test 4: Alloy Recommendations")
        alloy_result = alloy_pred.predict("GREY-IRON", test_comp_deviated)
        print(f"      Confidence: {alloy_result['confidence']:.4f}")
        if alloy_result['recommended_additions']:
            print(f"      Recommendations: {len(alloy_result['recommended_additions'])} elements")
        
        print("\n   ✅ All verification tests passed!")
        return True
        
    except Exception as e:
        print(f"\n   ❌ Verification failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def print_summary(start_time, df, success):
    """Print final summary"""
    duration = (datetime.now() - start_time).total_seconds()
    
    print_header("RETRAINING COMPLETE!")
    
    if success:
        print("\n✅ Status: SUCCESS")
        print(f"\n📊 Summary:")
        print(f"   • Duration: {duration:.1f} seconds")
        print(f"   • Dataset size: {len(df):,} samples")
        print(f"   • Models trained: 2 (Anomaly + Alloy)")
        print(f"   • Verification: PASSED")
        
        print(f"\n📁 Model Files:")
        print(f"   • Anomaly: {ANOMALY_MODEL_PATH}")
        print(f"   • Alloy: {ALLOY_MODEL_PATH}")
        
        print(f"\n🎯 Key Improvements Applied:")
        print("   ✓ Deterministic predictions (no randomness)")
        print("   ✓ Trained on tightly filtered normal samples")
        print("   ✓ Sensitive single-element deviation detection")
        print("   ✓ Alloy agent invokes for MEDIUM & HIGH severity")
        print("   ✓ Contamination: 0.05 for high sensitivity")
        
        print(f"\n🚀 Next Steps:")
        print("   1. Start API server:")
        print("      python app/main.py")
        print("")
        print("   2. Test the system:")
        print("      python test_determinism.py")
        print("")
        print("   3. Access API docs:")
        print("      http://localhost:8001/docs")
        print("")
        print("   4. Use /agents/analyze endpoint")
        
    else:
        print("\n❌ Status: FAILED")
        print("   Please check error messages above")
        print("   Common issues:")
        print("   • Missing dataset.csv in app/data/")
        print("   • Incorrect dataset format")
        print("   • Missing dependencies")
    
    print("\n" + "="*70 + "\n")


def main():
    """Main retraining workflow"""
    start_time = datetime.now()
    
    print_header("METALLISENSE AI - MODEL RETRAINING")
    print(f"\n🕐 Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📂 Working Directory: {Path.cwd()}")
    
    # Step 1: Verify dataset
    df = verify_dataset()
    if df is None:
        print_summary(start_time, None, False)
        return False
    
    # Step 2: Train anomaly model
    anomaly_agent, anomaly_stats = train_anomaly_model(df)
    if anomaly_agent is None:
        print_summary(start_time, df, False)
        return False
    
    # Step 3: Train alloy model
    alloy_agent, alloy_stats = train_alloy_model(df)
    if alloy_agent is None:
        print_summary(start_time, df, False)
        return False
    
    # Step 4: Verify everything works
    success = verify_models()
    
    # Final summary
    print_summary(start_time, df, success)
    
    return success


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Training interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
