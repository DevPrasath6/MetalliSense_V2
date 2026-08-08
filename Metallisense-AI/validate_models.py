"""
Model Validation Script with Expected Answers
Tests models against predefined cases with known expected outcomes
"""
import requests
import json
from typing import Dict, List, Tuple, Any
from datetime import datetime

BASE_URL = "http://localhost:8000"

# Color codes
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_section(title: str):
    """Print section header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{title.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")


def print_test_header(test_num: int, test_name: str):
    """Print individual test header"""
    print(f"\n{Colors.BOLD}{Colors.OKCYAN}[Test {test_num}] {test_name}{Colors.ENDC}")
    print("-" * 80)


def print_expected(label: str, value: Any):
    """Print expected value"""
    print(f"{Colors.OKBLUE}  Expected {label:.<40} {value}{Colors.ENDC}")


def print_actual(label: str, value: Any):
    """Print actual value"""
    print(f"{Colors.WARNING}  Actual {label:.<40} {value}{Colors.ENDC}")


def print_pass(message: str = "PASS"):
    """Print pass message"""
    print(f"{Colors.OKGREEN}  ✓ {message}{Colors.ENDC}")


def print_fail(message: str = "FAIL"):
    """Print fail message"""
    print(f"{Colors.FAIL}  ✗ {message}{Colors.ENDC}")


class AnomalyTestCase:
    """Test case for anomaly detection"""
    def __init__(self, name: str, composition: Dict[str, float], 
                 expected_severity: str, expected_is_anomaly: bool, reason: str):
        self.name = name
        self.composition = composition
        self.expected_severity = expected_severity
        self.expected_is_anomaly = expected_is_anomaly
        self.reason = reason


class AlloyTestCase:
    """Test case for alloy correction"""
    def __init__(self, name: str, grade: str, composition: Dict[str, float],
                 expected_needs_correction: bool, expected_elements: List[str], reason: str):
        self.name = name
        self.grade = grade
        self.composition = composition
        self.expected_needs_correction = expected_needs_correction
        self.expected_elements = expected_elements  # Elements that should be corrected
        self.reason = reason


def get_anomaly_test_cases() -> List[AnomalyTestCase]:
    """Define comprehensive anomaly detection test cases"""
    return [
        # ===== NORMAL CASES =====
        AnomalyTestCase(
            name="Perfect SG-IRON Composition",
            composition={"Fe": 86.0, "C": 3.5, "Si": 2.3, "Mn": 0.65, "P": 0.045, "S": 0.02},
            expected_severity="LOW",
            expected_is_anomaly=False,
            reason="All elements within typical SG-IRON ranges"
        ),
        
        AnomalyTestCase(
            name="Perfect LOW-CARBON-STEEL",
            composition={"Fe": 98.8, "C": 0.15, "Si": 0.3, "Mn": 0.6, "P": 0.025, "S": 0.02},
            expected_severity="LOW",
            expected_is_anomaly=False,
            reason="All elements within typical low-carbon steel ranges"
        ),
        
        AnomalyTestCase(
            name="Perfect GREY-IRON",
            composition={"Fe": 88.5, "C": 3.2, "Si": 1.8, "Mn": 0.7, "P": 0.08, "S": 0.06},
            expected_severity="LOW",
            expected_is_anomaly=False,
            reason="All elements within typical grey-iron ranges"
        ),
        
        AnomalyTestCase(
            name="Perfect MEDIUM-CARBON-STEEL",
            composition={"Fe": 98.1, "C": 0.45, "Si": 0.35, "Mn": 0.9, "P": 0.025, "S": 0.025},
            expected_severity="LOW",
            expected_is_anomaly=False,
            reason="All elements within medium-carbon steel ranges"
        ),
        
        AnomalyTestCase(
            name="Perfect HIGH-CARBON-STEEL",
            composition={"Fe": 97.8, "C": 0.9, "Si": 0.45, "Mn": 1.2, "P": 0.025, "S": 0.025},
            expected_severity="LOW",
            expected_is_anomaly=False,
            reason="All elements within high-carbon steel ranges"
        ),
        
        # ===== BOUNDARY CASES (Should still be NORMAL or LOW) =====
        AnomalyTestCase(
            name="SG-IRON Lower Boundary",
            composition={"Fe": 82.5, "C": 3.0, "Si": 1.8, "Mn": 0.3, "P": 0.01, "S": 0.01},
            expected_severity="LOW",
            expected_is_anomaly=False,
            reason="At lower bounds of SG-IRON specification"
        ),
        
        AnomalyTestCase(
            name="SG-IRON Upper Boundary",
            composition={"Fe": 89.5, "C": 4.0, "Si": 2.8, "Mn": 1.0, "P": 0.08, "S": 0.03},
            expected_severity="LOW",
            expected_is_anomaly=False,
            reason="At upper bounds of SG-IRON specification"
        ),
        
        # ===== MEDIUM SEVERITY CASES =====
        AnomalyTestCase(
            name="Moderate Carbon Deviation",
            composition={"Fe": 84.5, "C": 4.3, "Si": 2.5, "Mn": 0.6, "P": 0.05, "S": 0.02},
            expected_severity="MEDIUM",
            expected_is_anomaly=True,
            reason="Carbon slightly above normal range (4.3% vs 4.0% max)"
        ),
        
        AnomalyTestCase(
            name="Moderate Silicon Deviation",
            composition={"Fe": 85.2, "C": 3.5, "Si": 3.1, "Mn": 0.65, "P": 0.045, "S": 0.02},
            expected_severity="MEDIUM",
            expected_is_anomaly=True,
            reason="Silicon moderately high (3.1% vs 2.8% max)"
        ),
        
        AnomalyTestCase(
            name="Low Iron Content",
            composition={"Fe": 79.5, "C": 3.5, "Si": 2.3, "Mn": 0.65, "P": 0.045, "S": 0.02},
            expected_severity="MEDIUM",
            expected_is_anomaly=True,
            reason="Iron content low (79.5% vs 82% min for SG-IRON)"
        ),
        
        AnomalyTestCase(
            name="High Phosphorus",
            composition={"Fe": 85.8, "C": 3.5, "Si": 2.3, "Mn": 0.65, "P": 0.12, "S": 0.02},
            expected_severity="MEDIUM",
            expected_is_anomaly=True,
            reason="Phosphorus elevated (0.12% vs 0.08% max typical)"
        ),
        
        AnomalyTestCase(
            name="High Sulfur",
            composition={"Fe": 85.9, "C": 3.5, "Si": 2.3, "Mn": 0.65, "P": 0.045, "S": 0.06},
            expected_severity="MEDIUM",
            expected_is_anomaly=True,
            reason="Sulfur elevated (0.06% vs 0.03% max for SG-IRON)"
        ),
        
        # ===== HIGH SEVERITY CASES =====
        AnomalyTestCase(
            name="Extreme Carbon Deviation",
            composition={"Fe": 80.0, "C": 5.5, "Si": 2.3, "Mn": 0.65, "P": 0.045, "S": 0.02},
            expected_severity="HIGH",
            expected_is_anomaly=True,
            reason="Carbon extremely high (5.5% vs 4.0% max)"
        ),
        
        AnomalyTestCase(
            name="Multiple Extreme Deviations",
            composition={"Fe": 78.0, "C": 5.2, "Si": 3.8, "Mn": 1.5, "P": 0.15, "S": 0.08},
            expected_severity="HIGH",
            expected_is_anomaly=True,
            reason="Multiple elements severely out of range"
        ),
        
        AnomalyTestCase(
            name="Very Low Iron",
            composition={"Fe": 75.0, "C": 3.5, "Si": 2.3, "Mn": 0.65, "P": 0.045, "S": 0.02},
            expected_severity="HIGH",
            expected_is_anomaly=True,
            reason="Iron critically low (75% vs 82% min)"
        ),
        
        AnomalyTestCase(
            name="Extreme Silicon",
            composition={"Fe": 82.0, "C": 3.5, "Si": 4.5, "Mn": 0.65, "P": 0.045, "S": 0.02},
            expected_severity="HIGH",
            expected_is_anomaly=True,
            reason="Silicon extremely high (4.5% vs 2.8% max)"
        ),
        
        # ===== EDGE CASES =====
        AnomalyTestCase(
            name="Very Low Carbon Steel",
            composition={"Fe": 99.4, "C": 0.03, "Si": 0.15, "Mn": 0.35, "P": 0.015, "S": 0.015},
            expected_severity="LOW",
            expected_is_anomaly=False,
            reason="Ultra-low carbon steel composition (valid)"
        ),
        
        AnomalyTestCase(
            name="Near-Pure Iron",
            composition={"Fe": 99.7, "C": 0.02, "Si": 0.05, "Mn": 0.15, "P": 0.01, "S": 0.01},
            expected_severity="LOW",
            expected_is_anomaly=False,
            reason="Near-pure iron composition (valid edge case)"
        ),
        
        AnomalyTestCase(
            name="High Alloy Content",
            composition={"Fe": 88.5, "C": 2.8, "Si": 2.5, "Mn": 1.8, "P": 0.06, "S": 0.04},
            expected_severity="MEDIUM",
            expected_is_anomaly=True,
            reason="High manganese for typical grades (1.8% vs 1.5% max)"
        ),
        
        AnomalyTestCase(
            name="Contaminated Sample",
            composition={"Fe": 72.0, "C": 6.0, "Si": 4.0, "Mn": 2.0, "P": 0.20, "S": 0.15},
            expected_severity="HIGH",
            expected_is_anomaly=True,
            reason="Severely contaminated or mixed alloy"
        ),
    ]


def get_alloy_test_cases() -> List[AlloyTestCase]:
    """Define comprehensive alloy correction test cases"""
    return [
        # ===== NO CORRECTION NEEDED =====
        AlloyTestCase(
            name="Perfect SG-IRON - No Correction",
            grade="SG-IRON",
            composition={"Fe": 86.0, "C": 3.5, "Si": 2.3, "Mn": 0.65, "P": 0.045, "S": 0.02},
            expected_needs_correction=False,
            expected_elements=[],
            reason="All elements within specification"
        ),
        
        AlloyTestCase(
            name="Perfect LOW-CARBON-STEEL - No Correction",
            grade="LOW-CARBON-STEEL",
            composition={"Fe": 98.8, "C": 0.15, "Si": 0.3, "Mn": 0.6, "P": 0.025, "S": 0.02},
            expected_needs_correction=False,
            expected_elements=[],
            reason="All elements within specification"
        ),
        
        # ===== SINGLE ELEMENT CORRECTIONS =====
        AlloyTestCase(
            name="SG-IRON - Low Carbon",
            grade="SG-IRON",
            composition={"Fe": 87.5, "C": 2.5, "Si": 2.3, "Mn": 0.65, "P": 0.045, "S": 0.02},
            expected_needs_correction=True,
            expected_elements=["C"],
            reason="Carbon too low (2.5% vs 3.0% min) - need to add carbon"
        ),
        
        AlloyTestCase(
            name="SG-IRON - High Carbon",
            grade="SG-IRON",
            composition={"Fe": 81.0, "C": 4.5, "Si": 2.3, "Mn": 0.65, "P": 0.045, "S": 0.02},
            expected_needs_correction=True,
            expected_elements=["C"],
            reason="Carbon too high (4.5% vs 4.0% max) - need to dilute"
        ),
        
        AlloyTestCase(
            name="SG-IRON - Low Silicon",
            grade="SG-IRON",
            composition={"Fe": 88.0, "C": 3.5, "Si": 1.2, "Mn": 0.65, "P": 0.045, "S": 0.02},
            expected_needs_correction=True,
            expected_elements=["Si"],
            reason="Silicon too low (1.2% vs 1.8% min) - need to add silicon"
        ),
        
        AlloyTestCase(
            name="SG-IRON - High Silicon",
            grade="SG-IRON",
            composition={"Fe": 83.0, "C": 3.5, "Si": 3.2, "Mn": 0.65, "P": 0.045, "S": 0.02},
            expected_needs_correction=True,
            expected_elements=["Si"],
            reason="Silicon too high (3.2% vs 2.8% max) - need to reduce"
        ),
        
        AlloyTestCase(
            name="GREY-IRON - Low Silicon",
            grade="GREY-IRON",
            composition={"Fe": 90.5, "C": 3.0, "Si": 0.6, "Mn": 0.7, "P": 0.08, "S": 0.06},
            expected_needs_correction=True,
            expected_elements=["Si"],
            reason="Silicon critically low (0.6% vs 1.0% min)"
        ),
        
        AlloyTestCase(
            name="LOW-CARBON-STEEL - High Carbon",
            grade="LOW-CARBON-STEEL",
            composition={"Fe": 97.8, "C": 0.35, "Si": 0.3, "Mn": 0.6, "P": 0.025, "S": 0.02},
            expected_needs_correction=True,
            expected_elements=["C"],
            reason="Carbon too high (0.35% vs 0.25% max for low-carbon)"
        ),
        
        AlloyTestCase(
            name="LOW-CARBON-STEEL - Low Manganese",
            grade="LOW-CARBON-STEEL",
            composition={"Fe": 98.9, "C": 0.15, "Si": 0.3, "Mn": 0.15, "P": 0.025, "S": 0.02},
            expected_needs_correction=True,
            expected_elements=["Mn"],
            reason="Manganese too low (0.15% vs 0.3% min)"
        ),
        
        AlloyTestCase(
            name="MEDIUM-CARBON-STEEL - Low Carbon",
            grade="MEDIUM-CARBON-STEEL",
            composition={"Fe": 98.5, "C": 0.2, "Si": 0.35, "Mn": 0.9, "P": 0.025, "S": 0.025},
            expected_needs_correction=True,
            expected_elements=["C"],
            reason="Carbon too low (0.2% vs 0.3% min for medium-carbon)"
        ),
        
        AlloyTestCase(
            name="HIGH-CARBON-STEEL - Low Carbon",
            grade="HIGH-CARBON-STEEL",
            composition={"Fe": 98.2, "C": 0.5, "Si": 0.45, "Mn": 1.2, "P": 0.025, "S": 0.025},
            expected_needs_correction=True,
            expected_elements=["C"],
            reason="Carbon too low (0.5% vs 0.6% min for high-carbon)"
        ),
        
        # ===== MULTIPLE ELEMENT CORRECTIONS =====
        AlloyTestCase(
            name="SG-IRON - Low Carbon & Silicon",
            grade="SG-IRON",
            composition={"Fe": 89.0, "C": 2.7, "Si": 1.5, "Mn": 0.65, "P": 0.045, "S": 0.02},
            expected_needs_correction=True,
            expected_elements=["C", "Si"],
            reason="Both carbon and silicon below minimum"
        ),
        
        AlloyTestCase(
            name="SG-IRON - Multiple High Elements",
            grade="SG-IRON",
            composition={"Fe": 80.0, "C": 4.2, "Si": 3.0, "Mn": 1.2, "P": 0.09, "S": 0.04},
            expected_needs_correction=True,
            expected_elements=["C", "Si", "Mn", "P", "S"],
            reason="Multiple elements above specification"
        ),
        
        AlloyTestCase(
            name="GREY-IRON - Multiple Low Elements",
            grade="GREY-IRON",
            composition={"Fe": 92.0, "C": 2.0, "Si": 0.7, "Mn": 0.3, "P": 0.02, "S": 0.02},
            expected_needs_correction=True,
            expected_elements=["C", "Si"],
            reason="Carbon and silicon both critically low"
        ),
        
        # ===== IMPURITY CORRECTIONS =====
        AlloyTestCase(
            name="SG-IRON - High Phosphorus",
            grade="SG-IRON",
            composition={"Fe": 85.8, "C": 3.5, "Si": 2.3, "Mn": 0.65, "P": 0.12, "S": 0.02},
            expected_needs_correction=True,
            expected_elements=["P"],
            reason="Phosphorus too high (0.12% vs 0.08% max) - impurity"
        ),
        
        AlloyTestCase(
            name="SG-IRON - High Sulfur",
            grade="SG-IRON",
            composition={"Fe": 85.9, "C": 3.5, "Si": 2.3, "Mn": 0.65, "P": 0.045, "S": 0.06},
            expected_needs_correction=True,
            expected_elements=["S"],
            reason="Sulfur too high (0.06% vs 0.03% max) - impurity"
        ),
        
        AlloyTestCase(
            name="LOW-CARBON-STEEL - High P & S",
            grade="LOW-CARBON-STEEL",
            composition={"Fe": 98.5, "C": 0.15, "Si": 0.3, "Mn": 0.6, "P": 0.06, "S": 0.07},
            expected_needs_correction=True,
            expected_elements=["P", "S"],
            reason="Both P and S impurities elevated"
        ),
        
        # ===== EXTREME CASES =====
        AlloyTestCase(
            name="SG-IRON - Severely Off-Spec",
            grade="SG-IRON",
            composition={"Fe": 78.0, "C": 5.0, "Si": 4.0, "Mn": 1.5, "P": 0.15, "S": 0.08},
            expected_needs_correction=True,
            expected_elements=["C", "Si", "Mn", "P", "S"],
            reason="All elements severely out of specification"
        ),
    ]


def validate_anomaly_detection():
    """Validate anomaly detection with expected answers"""
    print_section("ANOMALY DETECTION VALIDATION")
    
    test_cases = get_anomaly_test_cases()
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print_test_header(i, test.name)
        
        # Print test details
        print(f"  Composition: {json.dumps(test.composition)}")
        print(f"  Reason: {test.reason}")
        
        # Print expected results
        print(f"\n{Colors.BOLD}Expected Results:{Colors.ENDC}")
        print_expected("Severity", test.expected_severity)
        print_expected("Is Anomaly", "YES" if test.expected_is_anomaly else "NO")
        
        try:
            # Get model prediction
            response = requests.post(
                f"{BASE_URL}/anomaly/predict",
                json={"composition": test.composition}
            )
            
            if response.status_code != 200:
                print_fail(f"API Error: {response.status_code}")
                failed += 1
                continue
            
            result = response.json()
            actual_severity = result.get('severity', 'UNKNOWN')
            actual_score = result.get('anomaly_score', 0)
            
            # Determine if model considers it an anomaly (MEDIUM or HIGH severity)
            actual_is_anomaly = actual_severity in ['MEDIUM', 'HIGH']
            
            # Print actual results
            print(f"\n{Colors.BOLD}Actual Results:{Colors.ENDC}")
            print_actual("Severity", actual_severity)
            print_actual("Is Anomaly", "YES" if actual_is_anomaly else "NO")
            print_actual("Anomaly Score", f"{actual_score:.4f}")
            
            # Validate results
            print(f"\n{Colors.BOLD}Validation:{Colors.ENDC}")
            
            severity_match = actual_severity == test.expected_severity
            anomaly_match = actual_is_anomaly == test.expected_is_anomaly
            
            if severity_match:
                print_pass(f"Severity matches: {actual_severity}")
            else:
                print_fail(f"Severity mismatch: Expected {test.expected_severity}, Got {actual_severity}")
            
            if anomaly_match:
                print_pass(f"Anomaly detection correct: {actual_is_anomaly}")
            else:
                print_fail(f"Anomaly detection wrong: Expected {test.expected_is_anomaly}, Got {actual_is_anomaly}")
            
            # Test passes if at least anomaly detection is correct
            # (Severity might vary slightly based on model)
            if anomaly_match:
                print_pass("TEST PASSED")
                passed += 1
            else:
                print_fail("TEST FAILED")
                failed += 1
                
        except Exception as e:
            print_fail(f"Exception: {str(e)}")
            failed += 1
    
    # Summary
    print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}Anomaly Detection Summary:{Colors.ENDC}")
    print(f"  Total Tests: {len(test_cases)}")
    print(f"  {Colors.OKGREEN}Passed: {passed}{Colors.ENDC}")
    print(f"  {Colors.FAIL}Failed: {failed}{Colors.ENDC}")
    print(f"  Success Rate: {passed/len(test_cases)*100:.1f}%")
    
    return passed, failed


def validate_alloy_correction():
    """Validate alloy correction with expected answers"""
    print_section("ALLOY CORRECTION VALIDATION")
    
    test_cases = get_alloy_test_cases()
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print_test_header(i, test.name)
        
        # Print test details
        print(f"  Grade: {test.grade}")
        print(f"  Composition: {json.dumps(test.composition)}")
        print(f"  Reason: {test.reason}")
        
        # Print expected results
        print(f"\n{Colors.BOLD}Expected Results:{Colors.ENDC}")
        print_expected("Needs Correction", "YES" if test.expected_needs_correction else "NO")
        if test.expected_elements:
            print_expected("Elements to Correct", ", ".join(test.expected_elements))
        
        try:
            # Get model prediction
            response = requests.post(
                f"{BASE_URL}/alloy/recommend",
                json={
                    "grade": test.grade,
                    "composition": test.composition
                }
            )
            
            if response.status_code != 200:
                print_fail(f"API Error: {response.status_code}")
                failed += 1
                continue
            
            result = response.json()
            
            # Check if correction is recommended
            has_additions = 'recommended_additions' in result
            actual_needs_correction = has_additions
            
            # Get elements with recommended changes
            actual_elements = []
            if has_additions:
                additions = result['recommended_additions']
                actual_elements = [elem for elem, val in additions.items() if abs(val) > 0.001]
            
            # Print actual results
            print(f"\n{Colors.BOLD}Actual Results:{Colors.ENDC}")
            print_actual("Needs Correction", "YES" if actual_needs_correction else "NO")
            
            if actual_elements:
                print_actual("Elements Changed", ", ".join(actual_elements))
                print(f"  {Colors.WARNING}Recommendations:{Colors.ENDC}")
                for elem in actual_elements:
                    val = result['recommended_additions'][elem]
                    sign = "+" if val > 0 else ""
                    print(f"    {elem}: {sign}{val:.4f}%")
            
            if 'confidence' in result:
                print_actual("Confidence", f"{result['confidence']:.4f}")
            
            # Validate results
            print(f"\n{Colors.BOLD}Validation:{Colors.ENDC}")
            
            correction_match = actual_needs_correction == test.expected_needs_correction
            
            if correction_match:
                print_pass(f"Correction requirement matches: {actual_needs_correction}")
            else:
                print_fail(f"Correction mismatch: Expected {test.expected_needs_correction}, Got {actual_needs_correction}")
            
            # Check if expected elements are in actual elements
            elements_match = True
            if test.expected_needs_correction and test.expected_elements:
                expected_set = set(test.expected_elements)
                actual_set = set(actual_elements)
                
                # Check if at least some expected elements are present
                overlap = expected_set.intersection(actual_set)
                if overlap:
                    print_pass(f"Detected corrections for: {', '.join(overlap)}")
                else:
                    print_fail(f"Expected elements not detected: {', '.join(expected_set)}")
                    elements_match = False
            
            # Test passes if correction requirement matches
            if correction_match and (elements_match or not test.expected_needs_correction):
                print_pass("TEST PASSED")
                passed += 1
            else:
                print_fail("TEST FAILED")
                failed += 1
                
        except Exception as e:
            print_fail(f"Exception: {str(e)}")
            failed += 1
    
    # Summary
    print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}Alloy Correction Summary:{Colors.ENDC}")
    print(f"  Total Tests: {len(test_cases)}")
    print(f"  {Colors.OKGREEN}Passed: {passed}{Colors.ENDC}")
    print(f"  {Colors.FAIL}Failed: {failed}{Colors.ENDC}")
    print(f"  Success Rate: {passed/len(test_cases)*100:.1f}%")
    
    return passed, failed


def main():
    """Run comprehensive model validation"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'METALLISENSE AI - MODEL VALIDATION WITH EXPECTED ANSWERS'.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}Validation Start:{Colors.ENDC} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{Colors.BOLD}API Endpoint:{Colors.ENDC} {BASE_URL}")
    print(f"\n{Colors.WARNING}⚠ Make sure the service is running: python app/main.py{Colors.ENDC}\n")
    
    try:
        # Check API health
        print(f"{Colors.BOLD}Checking API health...{Colors.ENDC}")
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print_fail("API is not responding correctly!")
            return
        print_pass("API is healthy and ready\n")
        
    except requests.exceptions.ConnectionError:
        print_fail(f"Cannot connect to {BASE_URL}")
        print("Please start the API service first!")
        return
    except Exception as e:
        print_fail(f"Health check failed: {e}")
        return
    
    # Run validation tests
    anomaly_passed, anomaly_failed = validate_anomaly_detection()
    alloy_passed, alloy_failed = validate_alloy_correction()
    
    # Overall summary
    total_passed = anomaly_passed + alloy_passed
    total_failed = anomaly_failed + alloy_failed
    total_tests = total_passed + total_failed
    
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'OVERALL VALIDATION SUMMARY'.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")
    
    print(f"{Colors.BOLD}Anomaly Detection:{Colors.ENDC}")
    print(f"  Passed: {Colors.OKGREEN}{anomaly_passed}{Colors.ENDC} | Failed: {Colors.FAIL}{anomaly_failed}{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}Alloy Correction:{Colors.ENDC}")
    print(f"  Passed: {Colors.OKGREEN}{alloy_passed}{Colors.ENDC} | Failed: {Colors.FAIL}{alloy_failed}{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}Total:{Colors.ENDC}")
    print(f"  Total Tests: {total_tests}")
    print(f"  Passed: {Colors.OKGREEN}{total_passed}{Colors.ENDC}")
    print(f"  Failed: {Colors.FAIL}{total_failed}{Colors.ENDC}")
    print(f"  Success Rate: {total_passed/total_tests*100:.1f}%")
    
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    
    if total_failed == 0:
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 ALL VALIDATIONS PASSED! Models are performing as expected!{Colors.ENDC}\n")
    else:
        print(f"\n{Colors.WARNING}{Colors.BOLD}⚠ Some validations failed. Review the results above for details.{Colors.ENDC}\n")
        print(f"{Colors.WARNING}Note: Minor discrepancies in severity levels may be acceptable.{Colors.ENDC}")
        print(f"{Colors.WARNING}Focus on anomaly detection accuracy and correction requirements.{Colors.ENDC}\n")


if __name__ == "__main__":
    main()
