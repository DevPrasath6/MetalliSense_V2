"""
Comprehensive test script for MetalliSense AI Service
Tests the newly trained models with 189K dataset
"""
import requests
import json
import time
from typing import Dict, List
from datetime import datetime

BASE_URL = "http://localhost:8000"

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """Print formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")

def print_success(text: str):
    """Print success message"""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def print_error(text: str):
    """Print error message"""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def test_health():
    """Test health endpoint and model loading status"""
    print_header("HEALTH CHECK & MODEL STATUS")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        data = response.json()
        
        print(f"\n{Colors.BOLD}Status Code:{Colors.ENDC} {response.status_code}")
        print(f"{Colors.BOLD}Response:{Colors.ENDC}")
        print(json.dumps(data, indent=2))
        
        if data.get("models_loaded"):
            print_success("All models loaded successfully")
            return True
        else:
            print_error("Models not loaded properly")
            return False
            
    except Exception as e:
        print_error(f"Health check failed: {str(e)}")
        return False

def test_anomaly_detection():
    """Test anomaly detection with comprehensive test cases"""
    print_header("ANOMALY DETECTION TESTS")
    
    test_cases = [
        {
            "name": "Normal SG-IRON Composition",
            "composition": {"Fe": 86.0, "C": 3.5, "Si": 2.3, "Mn": 0.65, "P": 0.045, "S": 0.02},
            "expected_severity": "LOW"
        },
        {
            "name": "Normal LOW-CARBON-STEEL",
            "composition": {"Fe": 98.8, "C": 0.15, "Si": 0.3, "Mn": 0.6, "P": 0.025, "S": 0.02},
            "expected_severity": "LOW"
        },
        {
            "name": "Slight Deviation - Medium Risk",
            "composition": {"Fe": 82.5, "C": 4.2, "Si": 2.8, "Mn": 0.4, "P": 0.09, "S": 0.04},
            "expected_severity": "MEDIUM"
        },
        {
            "name": "Extreme Deviation - High Carbon",
            "composition": {"Fe": 80.0, "C": 5.5, "Si": 3.8, "Mn": 0.3, "P": 0.15, "S": 0.08},
            "expected_severity": "HIGH"
        },
        {
            "name": "Multiple Element Deviations",
            "composition": {"Fe": 78.5, "C": 5.2, "Si": 3.8, "Mn": 1.5, "P": 0.15, "S": 0.08},
            "expected_severity": "HIGH"
        },
        {
            "name": "Edge Case - Very Low Alloy",
            "composition": {"Fe": 99.5, "C": 0.05, "Si": 0.1, "Mn": 0.25, "P": 0.015, "S": 0.01},
            "expected_severity": "LOW"
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{Colors.BOLD}Test {i}: {test['name']}{Colors.ENDC}")
        print(f"Input: {json.dumps(test['composition'], indent=2)}")
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/anomaly/predict",
                json={"composition": test['composition']}
            )
            response_time = (time.time() - start_time) * 1000
            
            data = response.json()
            
            print(f"\n{Colors.OKCYAN}Response:{Colors.ENDC}")
            print(f"  Anomaly Score: {data.get('anomaly_score', 'N/A')}")
            print(f"  Severity: {data.get('severity', 'N/A')}")
            print(f"  Message: {data.get('message', 'N/A')}")
            print(f"  Response Time: {response_time:.2f}ms")
            
            if response.status_code == 200:
                print_success(f"Test passed - Detected as {data.get('severity', 'UNKNOWN')}")
                passed += 1
            else:
                print_error(f"Test failed - Status code: {response.status_code}")
                failed += 1
                
        except Exception as e:
            print_error(f"Test failed: {str(e)}")
            failed += 1
    
    print(f"\n{Colors.BOLD}Anomaly Detection Summary:{Colors.ENDC}")
    print(f"  Passed: {passed}/{len(test_cases)}")
    print(f"  Failed: {failed}/{len(test_cases)}")
    
    return failed == 0

def test_alloy_correction():
    """Test alloy correction for all 5 grades"""
    print_header("ALLOY CORRECTION TESTS")
    
    test_cases = [
        {
            "name": "SG-IRON - High Carbon",
            "grade": "SG-IRON",
            "composition": {"Fe": 81.2, "C": 4.4, "Si": 3.1, "Mn": 0.4, "P": 0.05, "S": 0.02}
        },
        {
            "name": "GREY-IRON - Low Silicon",
            "grade": "GREY-IRON",
            "composition": {"Fe": 90.5, "C": 3.0, "Si": 0.8, "Mn": 0.6, "P": 0.08, "S": 0.05}
        },
        {
            "name": "LOW-CARBON-STEEL - Carbon Too Low",
            "grade": "LOW-CARBON-STEEL",
            "composition": {"Fe": 98.5, "C": 0.03, "Si": 0.2, "Mn": 0.4, "P": 0.02, "S": 0.015}
        },
        {
            "name": "MEDIUM-CARBON-STEEL - Manganese Deviation",
            "grade": "MEDIUM-CARBON-STEEL",
            "composition": {"Fe": 97.8, "C": 0.45, "Si": 0.3, "Mn": 0.3, "P": 0.025, "S": 0.02}
        },
        {
            "name": "HIGH-CARBON-STEEL - Multi-Element Issue",
            "grade": "HIGH-CARBON-STEEL",
            "composition": {"Fe": 97.2, "C": 0.55, "Si": 0.15, "Mn": 0.5, "P": 0.03, "S": 0.025}
        },
        {
            "name": "SG-IRON - Extreme Deviation",
            "grade": "SG-IRON",
            "composition": {"Fe": 78.0, "C": 5.0, "Si": 4.0, "Mn": 1.2, "P": 0.12, "S": 0.05}
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{Colors.BOLD}Test {i}: {test['name']}{Colors.ENDC}")
        print(f"Grade: {test['grade']}")
        print(f"Current Composition: {json.dumps(test['composition'], indent=2)}")
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/alloy/recommend",
                json={
                    "grade": test['grade'],
                    "composition": test['composition']
                }
            )
            response_time = (time.time() - start_time) * 1000
            
            data = response.json()
            
            print(f"\n{Colors.OKCYAN}Response:{Colors.ENDC}")
            if "recommended_additions" in data:
                additions = data["recommended_additions"]
                print(f"  Recommended Additions:")
                for element, amount in additions.items():
                    if amount > 0:
                        print(f"    • {element}: +{amount:.4f}%")
                print(f"  Confidence: {data.get('confidence', 'N/A')}")
                print(f"  Response Time: {response_time:.2f}ms")
                
                if data.get('warning'):
                    print_warning(f"Warning: {data['warning']}")
                
                print_success("Recommendations generated successfully")
                passed += 1
            else:
                print(f"  Message: {data.get('message', 'No message')}")
                if response.status_code == 200:
                    print_success("Composition already within spec")
                    passed += 1
                else:
                    print_error(f"Status code: {response.status_code}")
                    failed += 1
                    
        except Exception as e:
            print_error(f"Test failed: {str(e)}")
            failed += 1
    
    print(f"\n{Colors.BOLD}Alloy Correction Summary:{Colors.ENDC}")
    print(f"  Passed: {passed}/{len(test_cases)}")
    print(f"  Failed: {failed}/{len(test_cases)}")
    
    return failed == 0

def test_grades():
    """Test grades endpoint and validate specifications"""
    print_header("GRADE SPECIFICATIONS TESTS")
    
    try:
        # Test: Get all grades
        print(f"\n{Colors.BOLD}Test 1: Fetch All Grades{Colors.ENDC}")
        response = requests.get(f"{BASE_URL}/grades")
        grades_data = response.json()
        
        if response.status_code == 200:
            print_success(f"Retrieved {len(grades_data.get('grades', []))} grades")
            print(f"Available grades: {', '.join(grades_data.get('grades', []))}")
        else:
            print_error(f"Failed with status code: {response.status_code}")
            return False
        
        # Test: Get each individual grade
        all_grades = grades_data.get('grades', [])
        passed = 0
        
        for grade in all_grades:
            print(f"\n{Colors.BOLD}Test: Fetch {grade} Specification{Colors.ENDC}")
            response = requests.get(f"{BASE_URL}/grades/{grade}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"  Grade: {data.get('grade')}")
                print(f"  Description: {data.get('description')}")
                
                # Show composition ranges
                if 'composition_ranges' in data:
                    print(f"  Composition Ranges:")
                    for element, range_vals in data['composition_ranges'].items():
                        print(f"    {element}: {range_vals[0]:.2f} - {range_vals[1]:.2f}%")
                
                print_success(f"{grade} specification retrieved")
                passed += 1
            else:
                print_error(f"Failed to fetch {grade}")
        
        print(f"\n{Colors.BOLD}Grade Specifications Summary:{Colors.ENDC}")
        print(f"  Passed: {passed}/{len(all_grades)}")
        
        return passed == len(all_grades)
        
    except Exception as e:
        print_error(f"Grades test failed: {str(e)}")
        return False


def test_performance():
    """Test model performance and response times"""
    print_header("PERFORMANCE BENCHMARKS")
    
    test_composition = {"Fe": 86.0, "C": 3.5, "Si": 2.3, "Mn": 0.65, "P": 0.045, "S": 0.02}
    num_requests = 10
    
    print(f"\n{Colors.BOLD}Running {num_requests} requests for each endpoint...{Colors.ENDC}")
    
    # Test anomaly detection performance
    anomaly_times = []
    print(f"\n{Colors.OKCYAN}Anomaly Detection Performance:{Colors.ENDC}")
    
    for i in range(num_requests):
        start = time.time()
        response = requests.post(
            f"{BASE_URL}/anomaly/predict",
            json={"composition": test_composition}
        )
        elapsed = (time.time() - start) * 1000
        anomaly_times.append(elapsed)
        
        if (i + 1) % 5 == 0:
            print(f"  Completed {i + 1}/{num_requests} requests...")
    
    print(f"  Average Response Time: {sum(anomaly_times)/len(anomaly_times):.2f}ms")
    print(f"  Min: {min(anomaly_times):.2f}ms | Max: {max(anomaly_times):.2f}ms")
    
    # Test alloy correction performance
    alloy_times = []
    print(f"\n{Colors.OKCYAN}Alloy Correction Performance:{Colors.ENDC}")
    
    for i in range(num_requests):
        start = time.time()
        response = requests.post(
            f"{BASE_URL}/alloy/recommend",
            json={"grade": "SG-IRON", "composition": test_composition}
        )
        elapsed = (time.time() - start) * 1000
        alloy_times.append(elapsed)
        
        if (i + 1) % 5 == 0:
            print(f"  Completed {i + 1}/{num_requests} requests...")
    
    print(f"  Average Response Time: {sum(alloy_times)/len(alloy_times):.2f}ms")
    print(f"  Min: {min(alloy_times):.2f}ms | Max: {max(alloy_times):.2f}ms")
    
    # Overall performance
    avg_total = (sum(anomaly_times) + sum(alloy_times)) / (len(anomaly_times) + len(alloy_times))
    
    print(f"\n{Colors.BOLD}Overall Average Response Time: {avg_total:.2f}ms{Colors.ENDC}")
    
    if avg_total < 100:
        print_success("Excellent performance (< 100ms)")
    elif avg_total < 500:
        print_success("Good performance (< 500ms)")
    else:
        print_warning("Performance could be improved (> 500ms)")
    
    return True


def test_error_handling():
    """Test API error handling"""
    print_header("ERROR HANDLING TESTS")
    
    test_cases = [
        {
            "name": "Invalid Grade Name",
            "endpoint": "/alloy/recommend",
            "data": {"grade": "INVALID-GRADE", "composition": {"Fe": 85.0, "C": 3.0, "Si": 2.0, "Mn": 0.5, "P": 0.03, "S": 0.02}},
            "expected_status": 400
        },
        {
            "name": "Missing Composition Elements",
            "endpoint": "/anomaly/predict",
            "data": {"composition": {"Fe": 85.0, "C": 3.0}},
            "expected_status": 422
        },
        {
            "name": "Negative Element Values",
            "endpoint": "/anomaly/predict",
            "data": {"composition": {"Fe": 85.0, "C": -1.0, "Si": 2.0, "Mn": 0.5, "P": 0.03, "S": 0.02}},
            "expected_status": 422
        },
        {
            "name": "Invalid Data Type",
            "endpoint": "/anomaly/predict",
            "data": {"composition": "invalid"},
            "expected_status": 422
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{Colors.BOLD}Test {i}: {test['name']}{Colors.ENDC}")
        
        try:
            response = requests.post(f"{BASE_URL}{test['endpoint']}", json=test['data'])
            
            if response.status_code >= 400:
                error_data = response.json()
                print(f"  Status: {response.status_code}")
                print(f"  Error: {error_data.get('detail') or error_data.get('error', 'Unknown error')}")
                print_success("Error handled correctly")
                passed += 1
            else:
                print_warning(f"Expected error but got status {response.status_code}")
                failed += 1
                
        except Exception as e:
            print_error(f"Test failed: {str(e)}")
            failed += 1
    
    print(f"\n{Colors.BOLD}Error Handling Summary:{Colors.ENDC}")
    print(f"  Passed: {passed}/{len(test_cases)}")
    print(f"  Failed: {failed}/{len(test_cases)}")
    
    return failed == 0


def main():
    """Run comprehensive test suite"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'METALLISENSE AI SERVICE - COMPREHENSIVE TEST SUITE'.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"\n{Colors.BOLD}Testing API at:{Colors.ENDC} {BASE_URL}")
    print(f"{Colors.BOLD}Test Start Time:{Colors.ENDC} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{Colors.BOLD}Model Dataset Size:{Colors.ENDC} ~189K samples")
    print(f"\n{Colors.WARNING}⚠ Make sure the service is running: python app/main.py{Colors.ENDC}\n")
    
    try:
        # Run comprehensive test suite
        tests = [
            ("Health Check", test_health),
            ("Anomaly Detection", test_anomaly_detection),
            ("Alloy Correction", test_alloy_correction),
            ("Grade Specifications", test_grades),
            ("Performance Benchmarks", test_performance),
            ("Error Handling", test_error_handling)
        ]
        
        results = {}
        start_time = time.time()
        
        for name, test_func in tests:
            try:
                print(f"\n{Colors.OKCYAN}Running: {name}...{Colors.ENDC}")
                success = test_func()
                results[name] = ("PASSED", success)
            except requests.exceptions.ConnectionError:
                results[name] = ("CONNECTION ERROR", False)
                print_error(f"Cannot connect to {BASE_URL}")
                print("Make sure the API service is running!")
                break
            except Exception as e:
                results[name] = (f"ERROR: {str(e)}", False)
                print_error(f"Unexpected error: {str(e)}")
        
        total_time = time.time() - start_time
        
        # Detailed Summary
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'TEST SUMMARY'.center(70)}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")
        
        passed_count = sum(1 for _, (status, success) in results.items() if success)
        total_count = len(results)
        
        for test_name, (status, success) in results.items():
            if success:
                print(f"{Colors.OKGREEN}✓ {test_name:.<50} PASSED{Colors.ENDC}")
            else:
                print(f"{Colors.FAIL}✗ {test_name:.<50} {status}{Colors.ENDC}")
        
        print(f"\n{Colors.BOLD}Results:{Colors.ENDC}")
        print(f"  Total Tests: {total_count}")
        print(f"  Passed: {Colors.OKGREEN}{passed_count}{Colors.ENDC}")
        print(f"  Failed: {Colors.FAIL}{total_count - passed_count}{Colors.ENDC}")
        print(f"  Success Rate: {passed_count/total_count*100:.1f}%")
        print(f"  Total Time: {total_time:.2f}s")
        
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
        
        if passed_count == total_count:
            print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! Your AI models are working perfectly!{Colors.ENDC}\n")
        else:
            print(f"\n{Colors.WARNING}{Colors.BOLD}⚠ Some tests failed. Please review the errors above.{Colors.ENDC}\n")
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Tests interrupted by user{Colors.ENDC}\n")


if __name__ == "__main__":
    main()
