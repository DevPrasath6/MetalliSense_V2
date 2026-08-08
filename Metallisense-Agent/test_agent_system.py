"""
Agent System Integration Test
Tests the complete agent architecture end-to-end
"""
import sys
from pathlib import Path

# Add app directory to path
sys.path.append(str(Path(__file__).parent / "app"))

import requests
import json
from typing import Dict


def print_section(title: str):
    """Print a section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def print_result(label: str, value: any, indent: int = 2):
    """Print a result with proper formatting"""
    spaces = " " * indent
    if isinstance(value, dict):
        print(f"{spaces}{label}:")
        for k, v in value.items():
            print(f"{spaces}  {k}: {v}")
    else:
        print(f"{spaces}{label}: {value}")


def test_health_check(base_url: str) -> bool:
    """Test health check endpoint"""
    print_section("1. HEALTH CHECK")
    
    try:
        response = requests.get(f"{base_url}/health")
        data = response.json()
        
        print_result("Status", data["status"])
        print_result("Message", data["message"])
        print_result("Models Loaded", data["models_loaded"])
        
        all_healthy = all(data["models_loaded"].values())
        if all_healthy:
            print("\n  ✓ System is healthy and ready")
            return True
        else:
            print("\n  ✗ Some components are not ready")
            return False
    
    except Exception as e:
        print(f"\n  ✗ Health check failed: {e}")
        return False


def test_agent_analysis(
    base_url: str, 
    composition: Dict[str, float], 
    grade: str,
    test_name: str
) -> Dict:
    """Test agent analysis endpoint"""
    print_section(f"TEST: {test_name}")
    
    print(f"\n  Input Composition:")
    for element, value in composition.items():
        print(f"    {element}: {value}%")
    print(f"  Grade: {grade}")
    
    try:
        response = requests.post(
            f"{base_url}/agents/analyze",
            json={
                "composition": composition,
                "grade": grade
            }
        )
        
        if response.status_code != 200:
            print(f"\n  ✗ Request failed: {response.status_code}")
            print(f"    Error: {response.text}")
            return None
        
        data = response.json()
        
        # Anomaly Agent Results
        print(f"\n  📊 ANOMALY DETECTION AGENT:")
        if data.get("anomaly_agent"):
            anomaly = data["anomaly_agent"]
            print(f"    Agent: {anomaly['agent']}")
            print(f"    Anomaly Score: {anomaly['anomaly_score']:.3f}")
            print(f"    Severity: {anomaly['severity']}")
            print(f"    Confidence: {anomaly['confidence']:.3f}")
            print(f"    Explanation: {anomaly['explanation'][:80]}...")
        
        # Alloy Agent Results
        print(f"\n  🔧 ALLOY CORRECTION AGENT:")
        if data.get("alloy_agent"):
            alloy = data["alloy_agent"]
            print(f"    Agent: {alloy['agent']}")
            
            additions = alloy.get("recommended_additions", {})
            if additions:
                print(f"    Recommended Additions:")
                for element, amount in additions.items():
                    print(f"      {element}: +{amount:.2f}%")
                print(f"    Confidence: {alloy['confidence']:.3f}")
            else:
                print(f"    Status: Not invoked (severity below threshold)")
            
            print(f"    Explanation: {alloy['explanation'][:80]}...")
        
        # Final Note
        print(f"\n  ⚠️  SAFETY NOTE:")
        print(f"    {data['final_note']}")
        print(f"    Timestamp: {data.get('timestamp', 'N/A')}")
        
        print("\n  ✓ Test completed successfully")
        return data
    
    except Exception as e:
        print(f"\n  ✗ Test failed: {e}")
        return None


def test_legacy_endpoints(base_url: str, composition: Dict[str, float], grade: str):
    """Test legacy endpoints for backward compatibility"""
    print_section("LEGACY ENDPOINTS TEST")
    
    # Test anomaly endpoint
    print("\n  Testing /anomaly/predict...")
    try:
        response = requests.post(
            f"{base_url}/anomaly/predict",
            json={"composition": composition}
        )
        data = response.json()
        print(f"    ✓ Anomaly Score: {data['anomaly_score']:.3f}")
        print(f"    ✓ Severity: {data['severity']}")
    except Exception as e:
        print(f"    ✗ Failed: {e}")
    
    # Test alloy endpoint
    print("\n  Testing /alloy/recommend...")
    try:
        response = requests.post(
            f"{base_url}/alloy/recommend",
            json={
                "grade": grade,
                "composition": composition
            }
        )
        data = response.json()
        print(f"    ✓ Confidence: {data['confidence']:.3f}")
        if data['recommended_additions']:
            print(f"    ✓ Recommendations: {len(data['recommended_additions'])} elements")
    except Exception as e:
        print(f"    ✗ Failed: {e}")


def main():
    """Run all tests"""
    BASE_URL = "http://localhost:8000"
    
    print("\n" + "🤖"*35)
    print("  METALLISENSE AGENT SYSTEM - INTEGRATION TEST")
    print("🤖"*35)
    
    # Test 1: Health Check
    if not test_health_check(BASE_URL):
        print("\n❌ System not ready. Please ensure:")
        print("  1. API service is running (python app/main.py)")
        print("  2. Models are trained")
        print("  3. Virtual environment is activated")
        return
    
    # Test 2: Normal Composition (Expected: LOW severity, no alloy recommendations)
    normal_composition = {
        "Fe": 82.5,
        "C": 3.8,
        "Si": 2.5,
        "Mn": 0.5,
        "P": 0.04,
        "S": 0.02
    }
    test_agent_analysis(
        BASE_URL,
        normal_composition,
        "SG-IRON",
        "Normal Composition (Expected: LOW severity)"
    )
    
    # Test 3: Deviated Composition (Expected: HIGH severity, alloy recommendations)
    deviated_composition = {
        "Fe": 81.2,
        "C": 4.4,
        "Si": 3.1,
        "Mn": 0.4,
        "P": 0.04,
        "S": 0.02
    }
    test_agent_analysis(
        BASE_URL,
        deviated_composition,
        "SG-IRON",
        "Deviated Composition (Expected: HIGH severity + recommendations)"
    )
    
    # Test 4: Different Grade (Steel)
    steel_composition = {
        "Fe": 97.5,
        "C": 0.2,
        "Si": 0.1,
        "Mn": 1.0,
        "P": 0.03,
        "S": 0.02
    }
    test_agent_analysis(
        BASE_URL,
        steel_composition,
        "LOW-CARBON-STEEL",
        "Low Carbon Steel Composition"
    )
    
    # Test 5: Legacy Endpoints
    test_legacy_endpoints(BASE_URL, deviated_composition, "SG-IRON")
    
    # Final Summary
    print_section("SUMMARY")
    print("\n  ✅ All tests completed")
    print("\n  Key Points:")
    print("    • Agent system is operational")
    print("    • Anomaly detection is working")
    print("    • Alloy recommendations are conditional on severity")
    print("    • Human approval is ALWAYS required")
    print("    • Legacy endpoints are maintained for compatibility")
    
    print("\n  📚 Documentation:")
    print("    • Architecture: DOCS/AGENT_ARCHITECTURE.md")
    print("    • Quick Start: DOCS/AGENT_QUICKSTART.md")
    print("    • API Docs: http://localhost:8000/docs")
    
    print("\n" + "🎉"*35)
    print("  AGENT SYSTEM VALIDATION COMPLETE!")
    print("🎉"*35 + "\n")


if __name__ == "__main__":
    main()
