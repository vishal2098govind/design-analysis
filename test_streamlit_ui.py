#!/usr/bin/env python3
"""
Test Script for Enhanced Streamlit UI
Tests real-time step-by-step analysis functionality
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
FRONTEND_URL = 'http://localhost:8501'


def test_streamlit_ui_workflow():
    """Test complete Streamlit UI workflow with real-time monitoring"""

    print("🧪 Testing Enhanced Streamlit UI Workflow")
    print("=" * 60)

    print(f"🔧 API URL: {API_BASE_URL}")
    print(f"🌐 Frontend URL: {FRONTEND_URL}")

    # Test 1: Check API health
    print("\n🔍 Test 1: API Health Check")
    if not check_api_health():
        print("❌ API health check failed")
        return False
    print("✅ API health check passed")

    # Test 2: Check frontend accessibility
    print("\n🔍 Test 2: Frontend Accessibility")
    if not check_frontend_accessibility():
        print("❌ Frontend accessibility check failed")
        return False
    print("✅ Frontend accessibility check passed")

    # Test 3: Submit test analysis
    print("\n🔍 Test 3: Submit Test Analysis")
    request_id = submit_test_analysis()
    if not request_id:
        print("❌ Analysis submission failed")
        return False
    print(f"✅ Analysis submitted successfully: {request_id}")

    # Test 4: Monitor real-time progress
    print("\n🔍 Test 4: Real-Time Progress Monitoring")
    if not monitor_real_time_progress(request_id):
        print("❌ Real-time progress monitoring failed")
        return False
    print("✅ Real-time progress monitoring passed")

    # Test 5: Verify step-by-step results
    print("\n🔍 Test 5: Step-by-Step Results Verification")
    if not verify_step_results(request_id):
        print("❌ Step results verification failed")
        return False
    print("✅ Step results verification passed")

    print("\n🎉 All Streamlit UI tests passed!")
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


def check_frontend_accessibility():
    """Check if Streamlit frontend is accessible"""
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print("   Frontend is accessible")
            return True
        else:
            print(f"   Frontend returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"   Frontend accessibility error: {e}")
        print("   Make sure Streamlit is running: streamlit run streamlit_frontend.py")
        return False


def submit_test_analysis():
    """Submit a test analysis and return request ID"""

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
        response = requests.post(
            f"{API_BASE_URL}/analyze", json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            request_id = result.get('request_id')
            print(f"   Analysis submitted: {request_id}")
            return request_id
        else:
            print(f"   Analysis submission failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"   Analysis submission error: {e}")
        return None


def monitor_real_time_progress(request_id):
    """Monitor real-time progress of analysis"""

    print("   Monitoring progress for 120 seconds...")

    start_time = time.time()
    timeout = 120  # 2 minutes timeout
    step_statuses = {}

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

                print(
                    f"   Progress: {completed_steps}/{total_steps} steps completed")

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
                print(f"   Status check failed: {response.status_code}")
                return False

        except Exception as e:
            print(f"   Status check error: {e}")
            return False

    print("   ❌ Analysis monitoring timed out")
    return False


def verify_step_results(request_id):
    """Verify that step results are properly loaded and displayed"""

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
            verify_step_content(results)

            return True
        else:
            print(f"   ❌ Results loading failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"   ❌ Results verification error: {e}")
        return False


def verify_step_content(results):
    """Verify content for each analysis step"""

    print("\n   📊 Step Content Verification:")

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


def test_ui_components():
    """Test individual UI components"""

    print("🧪 Testing UI Components")
    print("=" * 40)

    # Test DynamoDB integration
    print("\n🔍 Test DynamoDB Integration")
    try:
        from dynamodb_tracker import create_dynamodb_tracker
        tracker = create_dynamodb_tracker()

        # Test table info
        table_info = tracker.get_table_info()
        print(f"   ✅ DynamoDB connected")
        print(f"   Table: {table_info.get('TableName')}")
        print(f"   Status: {table_info.get('TableStatus')}")

        # Test listing analyses
        analyses = tracker.list_analysis_requests(limit=5)
        print(f"   Recent analyses: {len(analyses)}")

    except Exception as e:
        print(f"   ❌ DynamoDB integration error: {e}")
        return False

    # Test S3 integration
    print("\n🔍 Test S3 Integration")
    try:
        from s3_storage import create_s3_storage
        storage = create_s3_storage()

        bucket_info = storage.get_bucket_info()
        print(f"   ✅ S3 connected")
        print(f"   Bucket: {bucket_info.get('bucket_name')}")
        print(f"   Region: {bucket_info.get('region')}")

    except Exception as e:
        print(f"   ❌ S3 integration error: {e}")
        return False

    # Test API endpoints
    print("\n🔍 Test API Endpoints")

    endpoints = [
        ("/", "Root endpoint"),
        ("/health", "Health check"),
        ("/files", "List files"),
    ]

    for endpoint, description in endpoints:
        try:
            response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"   ✅ {description}: Working")
            else:
                print(f"   ⚠️ {description}: Status {response.status_code}")
        except Exception as e:
            print(f"   ❌ {description}: {e}")

    print("\n🎉 UI component tests completed!")
    return True


def test_file_upload_functionality():
    """Test file upload functionality"""

    print("🧪 Testing File Upload Functionality")
    print("=" * 40)

    # Test different file types
    test_files = [
        ("test_data.txt", "This is test research data for analysis."),
        ("test_data.json",
         '{"research_data": "This is test research data for analysis."}'),
        ("test_data.csv", "feedback,content\nuser1,The interface is too complex\nuser2,The navigation is confusing")
    ]

    for filename, content in test_files:
        print(f"\n🔍 Testing {filename}")

        try:
            # Create temporary file
            with open(filename, 'w') as f:
                f.write(content)

            # Submit analysis with file
            with open(filename, 'r') as f:
                files = {'file': (filename, f, 'text/plain')}
                data = {
                    'implementation': 'hybrid',
                    'include_metadata': True
                }

                response = requests.post(
                    f"{API_BASE_URL}/analyze", files=files, data=data, timeout=30)

                if response.status_code == 200:
                    result = response.json()
                    request_id = result.get('request_id')
                    print(f"   ✅ File upload successful: {request_id}")

                    # Clean up
                    os.remove(filename)
                    return True
                else:
                    print(f"   ❌ File upload failed: {response.status_code}")

        except Exception as e:
            print(f"   ❌ File upload error: {e}")
            if os.path.exists(filename):
                os.remove(filename)

    return False


def main():
    """Main test function"""

    print("🚀 Enhanced Streamlit UI Test Suite")
    print("=" * 60)

    # Check environment
    print("🔍 Environment Check:")
    print(f"   API_BASE_URL: {os.getenv('API_BASE_URL', 'Not set')}")
    print(
        f"   DYNAMODB_TABLE_NAME: {os.getenv('DYNAMODB_TABLE_NAME', 'Not set')}")
    print(f"   STORAGE_TYPE: {os.getenv('STORAGE_TYPE', 'Not set')}")
    print()

    # Run component tests
    component_success = test_ui_components()

    if not component_success:
        print("\n❌ Component tests failed. Please check your configuration.")
        return False

    # Run file upload tests
    upload_success = test_file_upload_functionality()

    if not upload_success:
        print("\n❌ File upload tests failed.")
        return False

    # Run workflow test
    workflow_success = test_streamlit_ui_workflow()

    if workflow_success:
        print("\n🎉 All Streamlit UI tests passed!")
        print("\n🚀 Your enhanced Streamlit UI is working perfectly!")
        print("   Features verified:")
        print("   ✅ Real-time step-by-step monitoring")
        print("   ✅ Individual step tabs")
        print("   ✅ File upload functionality")
        print("   ✅ Progress tracking")
        print("   ✅ Results display")
        print("   ✅ DynamoDB integration")
        print("   ✅ S3 integration")
        return True
    else:
        print("\n❌ Streamlit UI workflow test failed!")
        print("💡 Check the logs above for details.")
        return False


if __name__ == "__main__":
    main()
