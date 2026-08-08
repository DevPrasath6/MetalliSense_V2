"""
Quick retraining script to apply model fixes
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "app"))

from app.config import DATASET_PATH, ANOMALY_MODEL_PATH, ALLOY_MODEL_PATH
from app.data.grade_specs import GradeSpecificationGenerator
from app.agents.anomaly_agent import AnomalyDetectionAgent
from app.agents.alloy_agent import AlloyCorrectionAgent
import pandas as pd

print("="*70)
print(" QUICK RETRAIN - APPLYING MODEL FIXES")
print("="*70)

# Load existing dataset
print(f"\n[1] Loading dataset from: {DATASET_PATH}")
df = pd.read_csv(DATASET_PATH)
print(f"Dataset shape: {df.shape}")
print(f"Samples: {len(df)}")

# Initialize grade generator
print("\n[2] Initializing grade generator...")
grade_gen = GradeSpecificationGenerator()
print(f"Loaded {len(grade_gen.get_available_grades())} grades")

# Retrain Anomaly Detection with grade-aware features
print("\n[3] Retraining Anomaly Detection Agent...")
print("-"*70)
anomaly_agent = AnomalyDetectionAgent(grade_generator=grade_gen)
anomaly_stats = anomaly_agent.train(df, contamination=0.35)

# Save anomaly model
print(f"\nSaving model to: {ANOMALY_MODEL_PATH}")
ANOMALY_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
anomaly_agent.save(str(ANOMALY_MODEL_PATH))
print("✓ Anomaly model saved")

# Retrain Alloy Correction
print("\n[4] Retraining Alloy Correction Agent...")
print("-"*70)
alloy_agent = AlloyCorrectionAgent(grade_gen)
alloy_stats = alloy_agent.train(df, test_size=0.2)

# Save alloy model
print(f"\nSaving model to: {ALLOY_MODEL_PATH}")
ALLOY_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
alloy_agent.save(str(ALLOY_MODEL_PATH))
print("✓ Alloy correction model saved")

# Summary
print("\n" + "="*70)
print(" RETRAINING COMPLETE")
print("="*70)

print("\nChanges Applied:")
print("  ✓ Anomaly Detection: Added grade-aware deviation features")
print("  ✓ Alloy Correction: Added spec-check to avoid unnecessary corrections")

print("\nNext Steps:")
print("  1. Restart the API: python app/main.py")
print("  2. Run validation: python validate_models.py")

print("\n" + "="*70 + "\n")
