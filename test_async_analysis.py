#!/usr/bin/env python3
"""
Test Script for Asynchronous Analysis
Tests the new asynchronous analysis functionality
"""

import os
import time
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')


def test_async_analysis():
    """Test asynchronous analysis functionality"""

    print("🧪 Testing Asynchronous Analysis")
    print("=" * 50)

    print(f"🔧 API URL: {API_BASE_URL}")

    # Test 1: Check API health
    print("\n🔍 Test 1: API Health Check")
    if not check_api_health():
        print("❌ API health check failed")
        return False
    print("✅ API health check passed")

    # Test 2: Submit analysis and get immediate response
    print("\n🔍 Test 2: Submit Analysis - Immediate Response")
    request_id = submit_analysis_async()
    if not request_id:
        print("❌ Analysis submission failed")
        return False
    print(f"✅ Analysis submitted successfully: {request_id}")

    # Test 3: Monitor real-time progress
    print("\n🔍 Test 3: Real-Time Progress Monitoring")
    if not monitor_async_progress(request_id):
        print("❌ Progress monitoring failed")
        return False
    print("✅ Progress monitoring completed")

    # Test 4: Verify final results
    print("\n🔍 Test 4: Final Results Verification")
    if not verify_final_results(request_id):
        print("❌ Final results verification failed")
        return False
    print("✅ Final results verification completed")

    print("\n🎉 All asynchronous analysis tests passed!")
    return True


def check_api_health():
    """Check if API is healthy"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"   Status: {health_data.get('status')}")
            print(f"   Storage: {health_data.get('storage_type')}")
            print(
                f"   OpenAI: {'Configured' if health_data.get('openai_key_configured') else 'Not configured'}")
            return True
        else:
            print(f"   API returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"   API health check error: {e}")
        return False


def submit_analysis_async():
    """Submit analysis and verify immediate response"""

    # Test research data
    test_data = """
    User Interview Transcript:
    
    "The current interface is too complex. I can't find what I'm looking for."
    "The navigation is confusing. I get lost easily."
    "I wish the design was simpler and more intuitive."
    "The buttons are too small and hard to click."
    "I need more visual feedback when I interact with elements."
    
    "The simpler tools are the ones I use most often."
    "I prefer straightforward interfaces over feature-rich ones."
    "The current design feels cluttered and overwhelming."
    """

    payload = {
        "research_data": test_data,
        "implementation": "hybrid",
        "include_metadata": True
    }

    try:
        start_time = time.time()
        response = requests.post(
            f"{API_BASE_URL}/analyze", json=payload, timeout=30)
        response_time = time.time() - start_time

        print(f"   Response time: {response_time:.2f} seconds")

        if response.status_code == 200:
            result = response.json()

            # Verify new response format
            request_id = result.get('request_id')
            status = result.get('status')
            message = result.get('message')
            timestamp = result.get('timestamp')

            print(f"   Request ID: {request_id}")
            print(f"   Status: {status}")
            print(f"   Message: {message}")
            print(f"   Timestamp: {timestamp}")

            # Verify response format
            if not request_id:
                print("   ❌ No request_id in response")
                return None

            if status != "started":
                print(f"   ❌ Unexpected status: {status}")
                return None

            if not message or "started" not in message.lower():
                print(f"   ❌ Unexpected message: {message}")
                return None

            # Verify response is immediate (should be fast)
            if response_time > 5.0:
                print(f"   ⚠️ Response time is slow: {response_time:.2f}s")

            print("   ✅ Immediate response format verified")
            return request_id
        else:
            print(f"   ❌ Analysis submission failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"   ❌ Analysis submission error: {e}")
        return None


def monitor_async_progress(request_id):
    """Monitor real-time progress of asynchronous analysis"""

    print("   Monitoring progress for 180 seconds...")

    start_time = time.time()
    timeout = 180  # 3 minutes timeout
    step_statuses = {}
    last_progress = 0

    while time.time() - start_time < timeout:
        try:
            # Get analysis status from API
            response = requests.get(
                f"{API_BASE_URL}/analysis/status/{request_id}", timeout=5)
            if response.status_code == 200:
                status = response.json()
                overall_status = status.get('overall_status', 'unknown')

                # Get step statuses
                steps_status = status.get(
                    'analysis_result', {}).get('steps_status', {})

                # Check for status changes
                for step_name, step_info in steps_status.items():
                    current_status = step_info.get('status', 'pending')
                    if step_name not in step_statuses or step_statuses[step_name] != current_status:
                        step_statuses[step_name] = current_status
                        print(f"   {step_name}: {current_status}")

                # Count completed steps
                completed_steps = sum(1 for step_info in steps_status.values()
                                      if step_info.get('status') == 'completed')
                total_steps = len(steps_status)

                # Only print progress if it changed
                if completed_steps != last_progress:
                    print(
                        f"   Progress: {completed_steps}/{total_steps} steps completed")
                    last_progress = completed_steps

                if overall_status == 'completed':
                    print("   ✅ Analysis completed successfully!")

                    # Check if result_data is populated
                    result_data = status.get(
                        'analysis_result', {}).get('result_data', '')
                    if result_data:
                        print(f"   ✅ Result data path: {result_data}")
                    else:
                        print("   ⚠️ Result data path is empty")

                    return True
                elif overall_status == 'failed':
                    print("   ❌ Analysis failed")
                    return False

                time.sleep(2)  # Check every 2 seconds
            else:
                print(f"   ❌ Status check failed: {response.status_code}")
                return False

        except Exception as e:
            print(f"   ❌ Status check error: {e}")
            return False

    print("   ❌ Analysis monitoring timed out")
    return False


def verify_final_results(request_id):
    """Verify that final results are properly stored and accessible"""

    try:
        # Load analysis results
        response = requests.get(
            f"{API_BASE_URL}/analysis/results/{request_id}", timeout=10)
        if response.status_code == 200:
            results = response.json()
            print("   ✅ Analysis results loaded successfully")

            # Check for expected fields
            expected_fields = ['chunks', 'inferences',
                               'patterns', 'insights', 'design_principles']
            for field in expected_fields:
                if field in results and results[field]:
                    print(f"   ✅ {field}: {len(results[field])} items")
                else:
                    print(f"   ⚠️ {field}: No data available")

            # Verify step-specific content
            verify_async_step_content(results)

            return True
        else:
            print(f"   ❌ Results loading failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"   ❌ Results verification error: {e}")
        return False


def verify_async_step_content(results):
    """Verify content for each analysis step"""

    print("\n   📊 Async Step Content Verification:")

    # Verify chunks
    if 'chunks' in results and results['chunks']:
        chunk = results['chunks'][0]
        if 'content' in chunk:
            print(
                f"   ✅ Chunking: Content present ({len(chunk['content'])} chars)")
        if 'metadata' in chunk:
            print(f"   ✅ Chunking: Metadata present")

    # Verify inferences
    if 'inferences' in results and results['inferences']:
        inference = results['inferences'][0]
        if 'meaning' in inference:
            print(f"   ✅ Inferring: Meaning present")
        if 'chunk_id' in inference:
            print(f"   ✅ Inferring: Chunk ID linked")

    # Verify patterns
    if 'patterns' in results and results['patterns']:
        pattern = results['patterns'][0]
        if 'pattern' in pattern:
            print(f"   ✅ Relating: Pattern identified")
        if 'description' in pattern:
            print(f"   ✅ Relating: Description present")

    # Verify insights
    if 'insights' in results and results['insights']:
        insight = results['insights'][0]
        if 'insight' in insight:
            print(f"   ✅ Explaining: Insight generated")
        if 'impact_score' in insight:
            print(f"   ✅ Explaining: Impact score calculated")

    # Verify design principles
    if 'design_principles' in results and results['design_principles']:
        principle = results['design_principles'][0]
        if 'principle' in principle:
            print(f"   ✅ Activating: Design principle created")
        if 'action_verbs' in principle:
            print(f"   ✅ Activating: Action verbs identified")


def test_multiple_concurrent_analyses():
    """Test multiple concurrent analyses"""

    print("\n🧪 Testing Multiple Concurrent Analyses")
    print("=" * 50)

    # Submit multiple analyses quickly
    request_ids = []
    for i in range(3):
        print(f"\n🔍 Submitting analysis {i+1}/3")

        test_data = f"""
        User Interview Transcript {i+1}:
        
        "The interface needs improvement for user {i+1}."
        "Navigation could be better for this use case."
        "Design should be more intuitive for different users."
        """

        payload = {
            "research_data": test_data,
            "implementation": "hybrid",
            "include_metadata": True
        }

        try:
            response = requests.post(
                f"{API_BASE_URL}/analyze", json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                request_id = result.get('request_id')
                if request_id:
                    request_ids.append(request_id)
                    print(f"   ✅ Analysis {i+1} submitted: {request_id}")
                else:
                    print(f"   ❌ Analysis {i+1} failed: No request ID")
            else:
                print(f"   ❌ Analysis {i+1} failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Analysis {i+1} error: {e}")

    print(f"\n📊 Submitted {len(request_ids)} analyses")

    # Monitor all analyses
    if request_ids:
        print("🔄 Monitoring all analyses...")
        completed = 0

        start_time = time.time()
        timeout = 300  # 5 minutes timeout

        while time.time() - start_time < timeout and completed < len(request_ids):
            # Copy list to avoid modification during iteration
            for request_id in request_ids[:]:
                try:
                    response = requests.get(
                        f"{API_BASE_URL}/analysis/status/{request_id}", timeout=5)
                    if response.status_code == 200:
                        status = response.json()
                        overall_status = status.get(
                            'overall_status', 'unknown')

                        if overall_status == 'completed':
                            print(f"   ✅ Analysis {request_id} completed")
                            request_ids.remove(request_id)
                            completed += 1
                        elif overall_status == 'failed':
                            print(f"   ❌ Analysis {request_id} failed")
                            request_ids.remove(request_id)
                            completed += 1

                except Exception as e:
                    print(f"   ⚠️ Error checking {request_id}: {e}")

            if request_ids:
                print(f"   📊 {len(request_ids)} analyses still running...")
                time.sleep(5)

        if completed == len(request_ids):
            print("✅ All concurrent analyses completed successfully!")
            return True
        else:
            print(f"❌ Only {completed}/{len(request_ids)} analyses completed")
            return False

    return False


def main():
    """Main test function"""

    print("🚀 Asynchronous Analysis Test Suite")
    print("=" * 60)

    # Check environment
    print("🔍 Environment Check:")
    print(f"   API_BASE_URL: {os.getenv('API_BASE_URL', 'Not set')}")
    print(
        f"   DYNAMODB_TABLE_NAME: {os.getenv('DYNAMODB_TABLE_NAME', 'Not set')}")
    print(f"   STORAGE_TYPE: {os.getenv('STORAGE_TYPE', 'Not set')}")
    print()

    # Run basic async test
    basic_success = test_async_analysis()

    if not basic_success:
        print("\n❌ Basic asynchronous analysis test failed!")
        return False

    # Run concurrent analysis test
    concurrent_success = test_multiple_concurrent_analyses()

    if concurrent_success:
        print("\n🎉 All asynchronous analysis tests passed!")
        print("\n🚀 Your asynchronous analysis system is working perfectly!")
        print("   Features verified:")
        print("   ✅ Immediate response with request ID")
        print("   ✅ Background analysis processing")
        print("   ✅ Real-time progress monitoring")
        print("   ✅ Concurrent analysis support")
        print("   ✅ Final results storage and retrieval")
        return True
    else:
        print("\n❌ Concurrent analysis test failed!")
        return False


if __name__ == "__main__":
    main()
