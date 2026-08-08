import requests
import json

# Test cases with expected anomalies
tests = [
    {
        'name': 'Normal composition',
        'data': {
            'composition': {'Fe': 93.5, 'C': 3.2, 'Si': 2.1, 'Mn': 0.65, 'P': 0.08, 'S': 0.12},
            'grade': 'GREY-IRON'
        }
    },
    {
        'name': 'Slightly elevated carbon',
        'data': {
            'composition': {'Fe': 92.8, 'C': 3.9, 'Si': 2.2, 'Mn': 0.6, 'P': 0.09, 'S': 0.11},
            'grade': 'GREY-IRON'
        }
    },
    {
        'name': 'Multiple deviations',
        'data': {
            'composition': {'Fe': 89.5, 'C': 5.2, 'Si': 3.8, 'Mn': 1.2, 'P': 0.15, 'S': 0.18},
            'grade': 'GREY-IRON'
        }
    },
    {
        'name': 'Extreme carbon content',
        'data': {
            'composition': {'Fe': 88.2, 'C': 6.5, 'Si': 2.8, 'Mn': 0.9, 'P': 0.12, 'S': 0.14},
            'grade': 'SG-IRON'
        }
    },
]

print("="*70)
print("ANOMALY DETECTION ANALYSIS - Checking Model Sensitivity")
print("="*70)

for test in tests:
    comp = test['data']['composition']
    print(f"\n{test['name']}:")
    print(f"  Composition: C={comp['C']}%, Si={comp['Si']}%, Mn={comp['Mn']}%, P={comp['P']}%, S={comp['S']}%")
    
    response = requests.post('http://localhost:8001/agents/analyze', json=test['data'])
    result = response.json()
    anomaly = result['anomaly_agent']
    
    print(f"  Anomaly Score: {anomaly['anomaly_score']:.4f}")
    print(f"  Severity: {anomaly['severity']}")
    print(f"  Confidence: {anomaly['confidence']:.2%}")
    
    if anomaly['severity'] in ['MEDIUM', 'HIGH']:
        print(f"  ✓ Detected as anomaly")
    else:
        print(f"  ✗ NOT detected as anomaly (treated as {anomaly['severity']})")

print("\n" + "="*70)
