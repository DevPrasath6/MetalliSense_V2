"""
Complete Setup and Training Script for MetalliSense AI Service
Run this script to generate data, train models, and verify the system
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
    """Run complete setup process"""
    
    print("\n" + "="*70)
    print(" METALLISENSE AI SERVICE - COMPLETE SETUP")
    print("="*70)
    
    # Step 1: Generate Grade Specifications
    print("\n[STEP 1] Generating Grade Specifications...")
    print("-"*70)
    
    grade_gen = GradeSpecificationGenerator()
    print(f"✓ Generated {len(grade_gen.get_available_grades())} grades:")
    for grade in grade_gen.get_available_grades():
        spec = grade_gen.get_grade_spec(grade)
        print(f"  - {grade}: {spec['description']}")
    
    # Step 2: Generate Synthetic Dataset
    print("\n[STEP 2] Generating Synthetic Dataset...")
    print("-"*70)
    
    data_gen = SyntheticDataGenerator(grade_gen)
    df = data_gen.generate_dataset(
        num_samples=SYNTHETIC_DATASET_SIZE,
        normal_ratio=NORMAL_RATIO,
        add_noise=True
    )
    
    # Save dataset
    DATASET_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(DATASET_PATH, index=False)
    print(f"\n✓ Dataset saved to: {DATASET_PATH}")
    
    # Analyze dataset
    data_gen.analyze_dataset(df)
    
    # Step 3: Train Anomaly Detection Agent
    print("\n[STEP 3] Training Anomaly Detection Agent (Agent 3)...")
    print("-"*70)
    
    from app.training.train_anomaly import train_anomaly_model
    anomaly_agent, anomaly_stats = train_anomaly_model(
        dataset_path=str(DATASET_PATH),
        save_path=str(ANOMALY_MODEL_PATH)
    )
    
    # Step 4: Train Alloy Correction Agent
    print("\n[STEP 4] Training Alloy Correction Agent (Agent 4)...")
    print("-"*70)
    
    from app.training.train_alloy_agent import train_alloy_model
    alloy_agent, alloy_stats = train_alloy_model(
        dataset_path=str(DATASET_PATH),
        save_path=str(ALLOY_MODEL_PATH)
    )
    
    # Step 5: Verification
    print("\n[STEP 5] System Verification...")
    print("-"*70)
    
    # Verify models exist
    models_exist = {
        "Anomaly Model": ANOMALY_MODEL_PATH.exists(),
        "Alloy Model": ALLOY_MODEL_PATH.exists(),
        "Dataset": DATASET_PATH.exists()
    }
    
    print("\nFile Verification:")
    for name, exists in models_exist.items():
        status = "✓" if exists else "✗"
        print(f"  {status} {name}")
    
    # Test inference
    print("\nTesting Inference Modules:")
    
    try:
        from app.inference.anomaly_predict import get_anomaly_predictor
        from app.inference.alloy_predict import get_alloy_predictor
        
        anomaly_pred = get_anomaly_predictor()
        alloy_pred = get_alloy_predictor()
        
        print("  ✓ Anomaly predictor loaded")
        print("  ✓ Alloy predictor loaded")
        
        # Quick test
        test_comp = {
            "Fe": 85.0,
            "C": 3.5,
            "Si": 2.2,
            "Mn": 0.7,
            "P": 0.04,
            "S": 0.02
        }
        
        anomaly_result = anomaly_pred.predict(test_comp)
        alloy_result = alloy_pred.predict("SG-IRON", test_comp)
        
        print("\n  Quick Inference Test:")
        print(f"    Anomaly Score: {anomaly_result['anomaly_score']:.4f} ({anomaly_result['severity']})")
        print(f"    Alloy Confidence: {alloy_result['confidence']:.4f}")
        print("  ✓ Inference working correctly")
        
    except Exception as e:
        print(f"  ✗ Inference test failed: {e}")
    
    # Final Summary
    print("\n" + "="*70)
    print(" SETUP COMPLETED SUCCESSFULLY!")
    print("="*70)
    
    print("\nNext Steps:")
    print("  1. Start the API service:")
    print("     python app/main.py")
    print("")
    print("  2. Access API documentation:")
    print("     http://localhost:8000/docs")
    print("")
    print("  3. Test endpoints:")
    print("     curl http://localhost:8000/health")
    print("")
    print("  4. Integrate with Node.js backend")
    print("")
    
    print("="*70)
    print("\n")


if __name__ == "__main__":
    main()
