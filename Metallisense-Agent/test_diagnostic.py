"""
Diagnostic Test Script for MetalliSense AI Agent System
Identifies model errors and analyzes failure patterns
"""

import requests
import json
from typing import Dict, Any, List
from collections import defaultdict
import sys

# API Configuration
BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}

# Test Results Storage
test_results = []
failure_patterns = defaultdict(list)
error_categories = {
    "severity_mismatch": [],
    "confidence_issues": [],
    "false_positives": [],
    "false_negatives": [],
    "alloy_invocation_errors": [],
    "boundary_errors": [],
    "grade_specific_errors": []
}


class DiagnosticTest:
    def __init__(self, test_id: str, category: str, description: str, 
                 input_data: Dict, expected_behavior: Dict):
        self.test_id = test_id
        self.category = category
        self.description = description
        self.input_data = input_data
        self.expected_behavior = expected_behavior
        self.actual_result = None
        self.passed = None
        self.errors = []


def check_api_health() -> bool:
    """Check if API is running"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def run_test(test: DiagnosticTest) -> bool:
    """Execute a single test and analyze results"""
    try:
        response = requests.post(
            f"{BASE_URL}/agents/analyze",
            json=test.input_data,
            headers=HEADERS,
            timeout=10
        )
        test.actual_result = response.json()
        
        # Analyze the results
        test.passed = analyze_result(test)
        return test.passed
        
    except Exception as e:
        test.actual_result = {"error": str(e)}
        test.errors.append(f"Request failed: {e}")
        test.passed = False
        return False


def analyze_result(test: DiagnosticTest) -> bool:
    """Analyze test result and categorize errors"""
    actual = test.actual_result
    expected = test.expected_behavior
    passed = True
    
    if actual.get("status") == "error":
        test.errors.append(f"API Error: {actual.get('message')}")
        return False
    
    # Extract actual values - API uses "anomaly_agent" not "anomaly_detection"
    anomaly_data = actual.get("anomaly_agent", {})
    actual_severity = anomaly_data.get("severity")
    actual_confidence = anomaly_data.get("confidence", 0)
    actual_anomaly_score = anomaly_data.get("anomaly_score", 0)
    
    # Derive is_anomaly from severity (NORMAL/LOW = False, MEDIUM/HIGH = True)
    actual_is_anomaly = actual_severity in ["MEDIUM", "HIGH"]
    
    # Extract alloy data - API uses "alloy_agent" not "alloy_recommendations"
    alloy_data = actual.get("alloy_agent", {})
    alloy_invoked = alloy_data is not None and len(alloy_data.get("recommended_additions", {})) > 0
    
    # Check anomaly detection
    if "is_anomaly" in expected:
        if actual_is_anomaly != expected["is_anomaly"]:
            passed = False
            error_type = "false_positive" if actual_is_anomaly else "false_negative"
            test.errors.append(f"Anomaly detection: expected {expected['is_anomaly']}, got {actual_is_anomaly}")
            error_categories[f"{error_type}s"].append({
                "test_id": test.test_id,
                "composition": test.input_data["composition"],
                "grade": test.input_data["grade"],
                "expected": expected["is_anomaly"],
                "actual": actual_is_anomaly,
                "confidence": actual_confidence
            })
    
    # Check severity level
    if "severity" in expected:
        if actual_severity != expected["severity"]:
            passed = False
            test.errors.append(f"Severity: expected {expected['severity']}, got {actual_severity}")
            error_categories["severity_mismatch"].append({
                "test_id": test.test_id,
                "composition": test.input_data["composition"],
                "grade": test.input_data["grade"],
                "expected_severity": expected["severity"],
                "actual_severity": actual_severity,
                "confidence": actual_confidence
            })
    
    # Check confidence levels
    if "min_confidence" in expected:
        if actual_confidence < expected["min_confidence"]:
            passed = False
            test.errors.append(f"Confidence too low: expected >={expected['min_confidence']:.2f}, got {actual_confidence:.2f}")
            error_categories["confidence_issues"].append({
                "test_id": test.test_id,
                "expected_min": expected["min_confidence"],
                "actual": actual_confidence,
                "severity": actual_severity
            })
    
    # Check alloy invocation
    if "alloy_should_invoke" in expected:
        if alloy_invoked != expected["alloy_should_invoke"]:
            passed = False
            test.errors.append(f"Alloy invocation: expected {expected['alloy_should_invoke']}, got {alloy_invoked}")
            error_categories["alloy_invocation_errors"].append({
                "test_id": test.test_id,
                "severity": actual_severity,
                "expected_invoke": expected["alloy_should_invoke"],
                "actual_invoke": alloy_invoked
            })
    
    # Check boundary conditions
    if test.category == "boundary":
        if not passed:
            error_categories["boundary_errors"].append({
                "test_id": test.test_id,
                "description": test.description,
                "composition": test.input_data["composition"],
                "errors": test.errors
            })
    
    # Track grade-specific errors
    if not passed:
        error_categories["grade_specific_errors"].append({
            "test_id": test.test_id,
            "grade": test.input_data["grade"],
            "category": test.category,
            "errors": test.errors
        })
    
    return passed


def create_diagnostic_tests() -> List[DiagnosticTest]:
    """Create comprehensive diagnostic test cases"""
    tests = []
    
    # ========================================================================
    # CATEGORY 1: NORMAL COMPOSITIONS (Should NOT be anomalies)
    # ========================================================================
    
    tests.append(DiagnosticTest(
        test_id="NORM-001",
        category="normal",
        description="Perfect Grey Iron composition",
        input_data={
            "composition": {"Fe": 93.5, "C": 3.2, "Si": 2.1, "Mn": 0.65, "P": 0.08, "S": 0.12},
            "grade": "GREY-IRON"
        },
        expected_behavior={
            "is_anomaly": False,
            "severity": "NORMAL",
            "min_confidence": 0.6,
            "alloy_should_invoke": False
        }
    ))
    
    tests.append(DiagnosticTest(
        test_id="NORM-002",
        category="normal",
        description="Normal SG Iron",
        input_data={
            "composition": {"Fe": 94.2, "C": 3.6, "Si": 2.5, "Mn": 0.35, "P": 0.03, "S": 0.015},
            "grade": "SG-IRON"
        },
        expected_behavior={
            "is_anomaly": False,
            "severity": "NORMAL",
            "min_confidence": 0.6,
            "alloy_should_invoke": False
        }
    ))
    
    tests.append(DiagnosticTest(
        test_id="NORM-003",
        category="normal",
        description="Normal Steel composition",
        input_data={
            "composition": {"Fe": 98.5, "C": 0.4, "Si": 0.3, "Mn": 0.6, "P": 0.02, "S": 0.015},
            "grade": "STEEL"
        },
        expected_behavior={
            "is_anomaly": False,
            "severity": "NORMAL",
            "min_confidence": 0.6,
            "alloy_should_invoke": False
        }
    ))
    
    # ========================================================================
    # CATEGORY 2: MINOR DEVIATIONS (Should be MEDIUM severity)
    # ========================================================================
    
    tests.append(DiagnosticTest(
        test_id="MED-001",
        category="medium_deviation",
        description="Slightly elevated carbon",
        input_data={
            "composition": {"Fe": 92.8, "C": 3.9, "Si": 2.2, "Mn": 0.6, "P": 0.09, "S": 0.11},
            "grade": "GREY-IRON"
        },
        expected_behavior={
            "is_anomaly": True,
            "severity": "MEDIUM",
            "min_confidence": 0.4,
            "alloy_should_invoke": False
        }
    ))
    
    tests.append(DiagnosticTest(
        test_id="MED-002",
        category="medium_deviation",
        description="Low silicon content",
        input_data={
            "composition": {"Fe": 94.5, "C": 3.4, "Si": 1.3, "Mn": 0.55, "P": 0.07, "S": 0.10},
            "grade": "GREY-IRON"
        },
        expected_behavior={
            "is_anomaly": True,
            "severity": "MEDIUM",
            "alloy_should_invoke": False
        }
    ))
    
    tests.append(DiagnosticTest(
        test_id="MED-003",
        category="medium_deviation",
        description="Elevated manganese",
        input_data={
            "composition": {"Fe": 93.0, "C": 3.3, "Si": 2.0, "Mn": 1.1, "P": 0.08, "S": 0.11},
            "grade": "GREY-IRON"
        },
        expected_behavior={
            "is_anomaly": True,
            "severity": "MEDIUM",
            "alloy_should_invoke": False
        }
    ))
    
    # ========================================================================
    # CATEGORY 3: HIGH SEVERITY (Should trigger alloy recommendations)
    # ========================================================================
    
    tests.append(DiagnosticTest(
        test_id="HIGH-001",
        category="high_severity",
        description="Very high carbon - multiple deviations",
        input_data={
            "composition": {"Fe": 89.5, "C": 5.2, "Si": 3.8, "Mn": 1.2, "P": 0.15, "S": 0.18},
            "grade": "GREY-IRON"
        },
        expected_behavior={
            "is_anomaly": True,
            "severity": "HIGH",
            "min_confidence": 0.6,
            "alloy_should_invoke": True
        }
    ))
    
    tests.append(DiagnosticTest(
        test_id="HIGH-002",
        category="high_severity",
        description="Extreme carbon content",
        input_data={
            "composition": {"Fe": 88.2, "C": 6.5, "Si": 2.8, "Mn": 0.9, "P": 0.12, "S": 0.14},
            "grade": "SG-IRON"
        },
        expected_behavior={
            "is_anomaly": True,
            "severity": "HIGH",
            "min_confidence": 0.7,
            "alloy_should_invoke": True
        }
    ))
    
    tests.append(DiagnosticTest(
        test_id="HIGH-003",
        category="high_severity",
        description="Critical sulfur contamination",
        input_data={
            "composition": {"Fe": 91.3, "C": 3.5, "Si": 2.3, "Mn": 0.7, "P": 0.09, "S": 0.35},
            "grade": "SG-IRON"
        },
        expected_behavior={
            "is_anomaly": True,
            "severity": "HIGH",
            "min_confidence": 0.6,
            "alloy_should_invoke": True
        }
    ))
    
    # ========================================================================
    # CATEGORY 4: BOUNDARY CONDITIONS
    # ========================================================================
    
    tests.append(DiagnosticTest(
        test_id="BOUND-001",
        category="boundary",
        description="Minimum carbon boundary",
        input_data={
            "composition": {"Fe": 95.2, "C": 2.5, "Si": 2.0, "Mn": 0.5, "P": 0.05, "S": 0.08},
            "grade": "GREY-IRON"
        },
        expected_behavior={
            "is_anomaly": False,
            "severity": "NORMAL",
            "min_confidence": 0.5
        }
    ))
    
    tests.append(DiagnosticTest(
        test_id="BOUND-002",
        category="boundary",
        description="Maximum carbon boundary",
        input_data={
            "composition": {"Fe": 90.5, "C": 4.5, "Si": 2.2, "Mn": 0.7, "P": 0.10, "S": 0.12},
            "grade": "GREY-IRON"
        },
        expected_behavior={
            "is_anomaly": True,
            "severity": "MEDIUM",
            "min_confidence": 0.4
        }
    ))
    
    tests.append(DiagnosticTest(
        test_id="BOUND-003",
        category="boundary",
        description="Zero phosphorus edge case",
        input_data={
            "composition": {"Fe": 94.0, "C": 3.3, "Si": 2.1, "Mn": 0.6, "P": 0.0, "S": 0.10},
            "grade": "SG-IRON"
        },
        expected_behavior={
            "is_anomaly": True,
            "min_confidence": 0.3
        }
    ))
    
    # ========================================================================
    # CATEGORY 5: EXTREME CASES (Stress testing)
    # ========================================================================
    
    tests.append(DiagnosticTest(
        test_id="EXT-001",
        category="extreme",
        description="All elements at minimum",
        input_data={
            "composition": {"Fe": 99.0, "C": 0.1, "Si": 0.1, "Mn": 0.1, "P": 0.01, "S": 0.01},
            "grade": "STEEL"
        },
        expected_behavior={
            "is_anomaly": True,
            "severity": "HIGH",
            "alloy_should_invoke": True
        }
    ))
    
    tests.append(DiagnosticTest(
        test_id="EXT-002",
        category="extreme",
        description="Highly imbalanced composition",
        input_data={
            "composition": {"Fe": 85.0, "C": 7.5, "Si": 4.2, "Mn": 1.8, "P": 0.20, "S": 0.25},
            "grade": "GREY-IRON"
        },
        expected_behavior={
            "is_anomaly": True,
            "severity": "HIGH",
            "min_confidence": 0.75,
            "alloy_should_invoke": True
        }
    ))
    
    # ========================================================================
    # CATEGORY 6: DIFFERENT GRADES
    # ========================================================================
    
    tests.append(DiagnosticTest(
        test_id="GRADE-001",
        category="grade_specific",
        description="Ductile Iron normal",
        input_data={
            "composition": {"Fe": 93.5, "C": 3.8, "Si": 2.6, "Mn": 0.4, "P": 0.03, "S": 0.015},
            "grade": "DUCTILE-IRON"
        },
        expected_behavior={
            "is_anomaly": False,
            "severity": "NORMAL"
        }
    ))
    
    tests.append(DiagnosticTest(
        test_id="GRADE-002",
        category="grade_specific",
        description="Stainless Steel normal",
        input_data={
            "composition": {"Fe": 68.0, "C": 0.08, "Si": 0.5, "Mn": 1.2, "P": 0.03, "S": 0.02},
            "grade": "STAINLESS-STEEL"
        },
        expected_behavior={
            "is_anomaly": False,
            "severity": "NORMAL"
        }
    ))
    
    tests.append(DiagnosticTest(
        test_id="GRADE-003",
        category="grade_specific",
        description="Ductile Iron with deviation",
        input_data={
            "composition": {"Fe": 92.0, "C": 4.2, "Si": 3.5, "Mn": 0.4, "P": 0.04, "S": 0.02},
            "grade": "DUCTILE-IRON"
        },
        expected_behavior={
            "is_anomaly": True,
            "severity": "MEDIUM"
        }
    ))
    
    # ========================================================================
    # CATEGORY 7: FALSE POSITIVE TRAPS
    # ========================================================================
    
    tests.append(DiagnosticTest(
        test_id="FP-001",
        category="false_positive_trap",
        description="Slightly off but acceptable",
        input_data={
            "composition": {"Fe": 93.2, "C": 3.35, "Si": 2.15, "Mn": 0.68, "P": 0.075, "S": 0.105},
            "grade": "GREY-IRON"
        },
        expected_behavior={
            "is_anomaly": False,
            "severity": "NORMAL"
        }
    ))
    
    tests.append(DiagnosticTest(
        test_id="FP-002",
        category="false_positive_trap",
        description="Natural variation within spec",
        input_data={
            "composition": {"Fe": 93.7, "C": 3.25, "Si": 2.05, "Mn": 0.62, "P": 0.085, "S": 0.115},
            "grade": "GREY-IRON"
        },
        expected_behavior={
            "is_anomaly": False,
            "severity": "NORMAL"
        }
    ))
    
    return tests


def analyze_failure_patterns():
    """Analyze all failures and identify patterns"""
    print("\n" + "="*80)
    print("FAILURE PATTERN ANALYSIS")
    print("="*80)
    
    total_tests = len(test_results)
    failed_tests = [t for t in test_results if not t.passed]
    passed_tests = [t for t in test_results if t.passed]
    
    print(f"\n📊 Overall Statistics:")
    print(f"   Total Tests: {total_tests}")
    print(f"   Passed: {len(passed_tests)} ({len(passed_tests)/total_tests*100:.1f}%)")
    print(f"   Failed: {len(failed_tests)} ({len(failed_tests)/total_tests*100:.1f}%)")
    
    # Analyze by category
    print(f"\n📂 Failures by Category:")
    category_failures = defaultdict(int)
    for test in failed_tests:
        category_failures[test.category] += 1
    
    for category, count in sorted(category_failures.items(), key=lambda x: x[1], reverse=True):
        total_in_category = len([t for t in test_results if t.category == category])
        print(f"   {category}: {count}/{total_in_category} failed ({count/total_in_category*100:.0f}%)")
    
    # Specific error analysis
    print(f"\n🔍 Error Type Analysis:")
    
    if error_categories["false_positives"]:
        print(f"\n   ❌ False Positives: {len(error_categories['false_positives'])}")
        print(f"      (Model detected anomaly when composition was normal)")
        for fp in error_categories["false_positives"][:3]:
            print(f"      - Test: {fp['test_id']} | Grade: {fp['grade']} | Confidence: {fp['confidence']:.2%}")
    
    if error_categories["false_negatives"]:
        print(f"\n   ❌ False Negatives: {len(error_categories['false_negatives'])}")
        print(f"      (Model missed anomaly that should be detected)")
        for fn in error_categories["false_negatives"][:3]:
            print(f"      - Test: {fn['test_id']} | Grade: {fn['grade']} | Confidence: {fn['confidence']:.2%}")
    
    if error_categories["severity_mismatch"]:
        print(f"\n   ⚠️  Severity Mismatches: {len(error_categories['severity_mismatch'])}")
        print(f"      (Detected anomaly but wrong severity level)")
        severity_patterns = defaultdict(int)
        for sm in error_categories["severity_mismatch"]:
            pattern = f"{sm['expected_severity']} → {sm['actual_severity']}"
            severity_patterns[pattern] += 1
        for pattern, count in severity_patterns.items():
            print(f"      - {pattern}: {count} cases")
    
    if error_categories["confidence_issues"]:
        print(f"\n   📉 Confidence Issues: {len(error_categories['confidence_issues'])}")
        print(f"      (Correct detection but low confidence)")
        avg_confidence = sum(c["actual"] for c in error_categories["confidence_issues"]) / len(error_categories["confidence_issues"])
        print(f"      - Average confidence: {avg_confidence:.2%}")
    
    if error_categories["alloy_invocation_errors"]:
        print(f"\n   🔧 Alloy Invocation Errors: {len(error_categories['alloy_invocation_errors'])}")
        print(f"      (Incorrect alloy agent invocation)")
        for aie in error_categories["alloy_invocation_errors"][:3]:
            print(f"      - Test: {aie['test_id']} | Severity: {aie['severity']} | Expected: {aie['expected_invoke']}, Got: {aie['actual_invoke']}")
    
    if error_categories["boundary_errors"]:
        print(f"\n   🎯 Boundary Errors: {len(error_categories['boundary_errors'])}")
        print(f"      (Issues at specification boundaries)")
        for be in error_categories["boundary_errors"]:
            print(f"      - {be['test_id']}: {be['description']}")
    
    # Grade-specific analysis
    print(f"\n🏷️  Grade-Specific Error Patterns:")
    grade_errors = defaultdict(list)
    for ge in error_categories["grade_specific_errors"]:
        grade_errors[ge["grade"]].append(ge)
    
    for grade, errors in sorted(grade_errors.items()):
        print(f"   {grade}: {len(errors)} errors")
        categories = defaultdict(int)
        for e in errors:
            categories[e["category"]] += 1
        for cat, count in categories.items():
            print(f"      - {cat}: {count}")
    
    # Identify common patterns
    print(f"\n🔬 Common Failure Patterns Identified:")
    patterns_found = []
    
    # Pattern 1: High carbon always causes issues
    high_carbon_tests = [t for t in failed_tests if t.input_data["composition"]["C"] > 5.0]
    if high_carbon_tests:
        patterns_found.append(f"High carbon (>5.0%) failures: {len(high_carbon_tests)} cases")
    
    # Pattern 2: Low confidence in medium severity
    low_conf_medium = [e for e in error_categories["confidence_issues"] if e["severity"] == "MEDIUM"]
    if low_conf_medium:
        patterns_found.append(f"Low confidence in MEDIUM severity: {len(low_conf_medium)} cases")
    
    # Pattern 3: Boundary value problems
    if error_categories["boundary_errors"]:
        patterns_found.append(f"Boundary condition issues: {len(error_categories['boundary_errors'])} cases")
    
    if patterns_found:
        for i, pattern in enumerate(patterns_found, 1):
            print(f"   {i}. {pattern}")
    else:
        print(f"   ✓ No significant patterns found - errors appear random")
    
    # Recommendations
    print(f"\n💡 Recommendations for Model Improvement:")
    recommendations = []
    
    if error_categories["false_positives"]:
        recommendations.append("Consider adjusting anomaly threshold to reduce false positives")
    
    if error_categories["false_negatives"]:
        recommendations.append("Retrain with more extreme deviation examples to catch missed anomalies")
    
    if error_categories["severity_mismatch"]:
        recommendations.append("Review severity threshold values - may need recalibration")
    
    if error_categories["confidence_issues"]:
        recommendations.append("Model confidence is low - consider ensemble methods or more training data")
    
    if error_categories["boundary_errors"]:
        recommendations.append("Add more training samples at specification boundaries")
    
    if len(grade_errors) > 0:
        worst_grade = max(grade_errors.items(), key=lambda x: len(x[1]))
        recommendations.append(f"Focus on {worst_grade[0]} grade - highest error rate")
    
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
    else:
        print(f"   ✓ Model performance is good - no major improvements needed")


def main():
    """Main diagnostic execution"""
    print("="*80)
    print(" METALLISENSE AI - DIAGNOSTIC TEST & ERROR PATTERN ANALYSIS")
    print("="*80)
    
    # Check API
    print(f"\n🔍 Checking API health...")
    if not check_api_health():
        print(f"❌ ERROR: API is not running!")
        print(f"   Start the API: python app/main.py")
        sys.exit(1)
    print(f"✓ API is healthy")
    
    # Create tests
    print(f"\n📋 Loading diagnostic tests...")
    tests = create_diagnostic_tests()
    print(f"✓ Loaded {len(tests)} diagnostic tests")
    
    # Run all tests
    print(f"\n🚀 Running diagnostic tests...\n")
    for i, test in enumerate(tests, 1):
        print(f"[{i}/{len(tests)}] Running {test.test_id}: {test.description}...", end=" ")
        result = run_test(test)
        test_results.append(test)
        
        if result:
            print("✓ PASS")
        else:
            print("✗ FAIL")
            for error in test.errors:
                print(f"         └─ {error}")
    
    # Analyze patterns
    analyze_failure_patterns()
    
    # Final summary
    print(f"\n" + "="*80)
    print(" DIAGNOSTIC TEST COMPLETE")
    print("="*80)
    
    failed_count = len([t for t in test_results if not t.passed])
    if failed_count == 0:
        print(f"\n🎉 All tests passed! Model is performing excellently.")
    else:
        print(f"\n⚠️  {failed_count} test(s) failed. Review the pattern analysis above.")
        print(f"   Use findings to improve model training and configuration.")
    
    print("")


if __name__ == "__main__":
    main()
