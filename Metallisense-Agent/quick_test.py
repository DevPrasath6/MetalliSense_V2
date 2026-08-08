import sys
sys.path.append('app')

from agents.anomaly_agent import AnomalyDetectionAgent
from config import ANOMALY_MODEL_PATH

agent = AnomalyDetectionAgent()
agent.load(str(ANOMALY_MODEL_PATH))

tests = [
    ('NORM-001: Normal Grey Iron', {'Fe': 93.5, 'C': 3.2, 'Si': 2.1, 'Mn': 0.65, 'P': 0.08, 'S': 0.12}, 'NORMAL'),
    ('MED-001: Elevated carbon', {'Fe': 92.8, 'C': 3.9, 'Si': 2.2, 'Mn': 0.6, 'P': 0.09, 'S': 0.11}, 'MEDIUM'),
    ('HIGH-001: Multiple deviations', {'Fe': 89.5, 'C': 5.2, 'Si': 3.8, 'Mn': 1.2, 'P': 0.15, 'S': 0.18}, 'HIGH'),
    ('HIGH-002: Extreme carbon', {'Fe': 88.2, 'C': 6.5, 'Si': 2.8, 'Mn': 0.9, 'P': 0.12, 'S': 0.14}, 'HIGH'),
    ('HIGH-003: Critical sulfur', {'Fe': 91.3, 'C': 3.5, 'Si': 2.3, 'Mn': 0.7, 'P': 0.09, 'S': 0.35}, 'HIGH'),
]

print("Model Sensitivity Test - After Retraining on Normal Samples Only")
print("="*70)

passed = 0
failed = 0

for name, comp, expected in tests:
    result = agent.predict(comp)
    actual = result['severity']
    
    if expected == 'NORMAL':
        status = "PASS" if actual == expected else "FAIL"
    else:
        status = "PASS" if actual in ['MEDIUM', 'HIGH'] else "FAIL"
    
    if status == "PASS":
        passed += 1
        print(f"✓ {name}: {actual} (expected {expected})")
    else:
        failed += 1
        print(f"✗ {name}: {actual} (expected {expected}) - score: {result['anomaly_score']:.4f}")

print("\n" + "="*70)
print(f"Results: {passed} passed, {failed} failed out of {passed+failed} tests")
print(f"Pass rate: {passed/(passed+failed)*100:.1f}%")
