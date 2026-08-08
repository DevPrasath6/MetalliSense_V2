"""
Test Script for Explainable AI Copilot
Tests explanation generation, chat, and voice services
"""
import requests
import json
from pathlib import Path

# API Configuration
API_BASE = "http://localhost:8001"

# Test composition
TEST_COMPOSITION = {
    "Fe": 94.5,
    "C": 3.2,
    "Si": 2.0,
    "Mn": 0.4,
    "P": 0.05,
    "S": 0.10
}
TEST_GRADE = "GREY-IRON"


def print_header(title):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def print_result(title, data):
    """Print formatted result"""
    print(f"\n{title}:")
    print("-" * 50)
    print(json.dumps(data, indent=2))
    print("-" * 50)


def test_health_check():
    """Test health endpoint"""
    print_header("Test 1: Health Check")
    
    response = requests.get(f"{API_BASE}/health")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print_result("Health Status", data)
        
        # Check if copilot is loaded
        if data.get("models_loaded", {}).get("copilot"):
            print("✓ Copilot is initialized")
            return True
        else:
            print("✗ Copilot not initialized")
            return False
    else:
        print("✗ Health check failed")
        return False


def test_explain_analysis():
    """Test explanation endpoint"""
    print_header("Test 2: Explain Analysis")
    
    payload = {
        "composition": TEST_COMPOSITION,
        "grade": TEST_GRADE
    }
    
    print("Request:")
    print(json.dumps(payload, indent=2))
    
    response = requests.post(
        f"{API_BASE}/copilot/explain",
        json=payload
    )
    
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        print("\n" + "="*70)
        print("EXPLANATION:")
        print("="*70)
        print(data.get("explanation", ""))
        
        print("\n" + "="*70)
        print("SUMMARY:")
        print("="*70)
        print(data.get("summary", ""))
        
        print("\n" + "="*70)
        print("ACTION ITEMS:")
        print("="*70)
        for i, action in enumerate(data.get("action_items", []), 1):
            print(f"{i}. {action}")
        
        print("\n" + "="*70)
        print(f"Risk Level: {data.get('risk_level')}")
        print(f"Confidence: {data.get('confidence'):.2%}")
        print(f"Timestamp: {data.get('timestamp')}")
        print("="*70)
        
        return True
    else:
        print(f"✗ Explanation failed: {response.text}")
        return False


def test_chat():
    """Test chat endpoint"""
    print_header("Test 3: Interactive Chat")
    
    questions = [
        "Why do we need to add Manganese?",
        "What happens if we don't correct this deviation?",
        "Explain the risk level",
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\nQuestion {i}: {question}")
        print("-" * 50)
        
        payload = {
            "message": question,
            "include_context": True
        }
        
        response = requests.post(
            f"{API_BASE}/copilot/chat",
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response:\n{data.get('response', '')}")
            print(f"\nConversation ID: {data.get('conversation_id', 'N/A')}")
        else:
            print(f"✗ Chat failed: {response.text}")
            return False
    
    return True


def test_clear_history():
    """Test clear history endpoint"""
    print_header("Test 4: Clear Chat History")
    
    response = requests.delete(f"{API_BASE}/copilot/chat/history")
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print_result("Clear History Result", data)
        return True
    else:
        print(f"✗ Clear history failed: {response.text}")
        return False


def test_get_languages():
    """Test get languages endpoint"""
    print_header("Test 5: Get Supported Languages")
    
    response = requests.get(f"{API_BASE}/copilot/voice/languages")
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        languages = data.get("languages", {})
        
        print("\nSupported Languages:")
        print("-" * 50)
        for code, name in languages.items():
            print(f"  {code}: {name}")
        print("-" * 50)
        print(f"Total: {len(languages)} languages")
        
        return True
    else:
        print(f"✗ Get languages failed: {response.text}")
        return False


def test_text_to_speech():
    """Test text-to-speech endpoint"""
    print_header("Test 6: Text-to-Speech")
    
    payload = {
        "text": "Silicon addition of 0.22% is recommended to reach the target range for GREY-IRON.",
        "language": "en",
        "slow": False
    }
    
    print("Request:")
    print(json.dumps(payload, indent=2))
    
    response = requests.post(
        f"{API_BASE}/copilot/voice/synthesize",
        json=payload
    )
    
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        # Save audio file
        output_file = Path(__file__).parent / "test_output.mp3"
        with open(output_file, "wb") as f:
            f.write(response.content)
        
        print(f"✓ Audio saved to: {output_file}")
        print(f"  Size: {len(response.content)} bytes")
        print(f"  Content-Type: {response.headers.get('Content-Type')}")
        
        return True
    else:
        print(f"✗ Text-to-speech failed: {response.text}")
        return False


def test_transcribe_audio():
    """Test speech-to-text endpoint (if audio file exists)"""
    print_header("Test 7: Speech-to-Text")
    
    # Check if test audio file exists
    test_audio = Path(__file__).parent / "test_output.mp3"
    
    if not test_audio.exists():
        print("⚠ Skipping: No test audio file available")
        print("  (Run test_text_to_speech first to generate test_output.mp3)")
        return True
    
    print(f"Using audio file: {test_audio}")
    
    with open(test_audio, "rb") as f:
        files = {"audio": ("test.mp3", f, "audio/mpeg")}
        
        response = requests.post(
            f"{API_BASE}/copilot/voice/transcribe",
            files=files
        )
    
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print_result("Transcription Result", data)
        
        if data.get("success"):
            print(f"\n✓ Transcribed Text: {data.get('text')}")
            print(f"  Language: {data.get('language')}")
        else:
            print(f"✗ Transcription failed: {data.get('error')}")
        
        return True
    else:
        print(f"✗ Speech-to-text failed: {response.text}")
        return False


def run_all_tests():
    """Run all copilot tests"""
    print("\n" + "="*70)
    print("  EXPLAINABLE AI COPILOT - TEST SUITE")
    print("="*70)
    print(f"\nAPI Base URL: {API_BASE}")
    print("\nStarting tests...\n")
    
    tests = [
        ("Health Check", test_health_check),
        ("Explain Analysis", test_explain_analysis),
        ("Interactive Chat", test_chat),
        ("Clear Chat History", test_clear_history),
        ("Get Languages", test_get_languages),
        ("Text-to-Speech", test_text_to_speech),
        ("Speech-to-Text", test_transcribe_audio),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n✗ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "="*70)
    print("  TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status:8} - {test_name}")
    
    print("="*70)
    print(f"Results: {passed}/{total} tests passed")
    print("="*70)
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    import sys
    
    try:
        exit_code = run_all_tests()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        sys.exit(1)
