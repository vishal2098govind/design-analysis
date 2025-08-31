#!/usr/bin/env python3
"""
Test Frontend Functionality
Tests the Streamlit frontend integration with the Design Analysis system
"""

import requests
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_frontend_workflow():
    """Test complete frontend workflow"""

    print("🧪 Testing Frontend Workflow")
    print("=" * 50)

    api_url = os.getenv('API_BASE_URL', 'http://localhost:8000')
    frontend_url = 'http://localhost:8501'

    print(f"🔧 API URL: {api_url}")
    print(f"🌐 Frontend URL: {frontend_url}")

    # Test 1: Check API health
    print("\n🔍 Test 1: API Health Check")
    try:
        response = requests.get(f"{api_url}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ API is healthy")
            print(f"   Status: {health_data.get('status')}")
            print(f"   Storage: {health_data.get('storage_type')}")
            print(
                f"   OpenAI: {'Configured' if health_data.get('openai_key_configured') else 'Not configured'}")
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API health check error: {e}")
        return False

    # Test 2: Check frontend accessibility
    print("\n🔍 Test 2: Frontend Accessibility")
    try:
        response = requests.get(frontend_url, timeout=10)
        if response.status_code == 200:
            print("✅ Frontend is accessible")
        else:
            print(f"❌ Frontend accessibility failed: {response.status_code}")
            print("   Make sure Streamlit is running on port 8501")
            return False
    except Exception as e:
        print(f"❌ Frontend accessibility error: {e}")
        print("   Make sure Streamlit is running: python run_streamlit.py")
        return False

    # Test 3: Submit test analysis
    print("\n🔍 Test 3: Submit Test Analysis")
    test_data = """
    User Interview Transcript:
    - "I just want to get this done quickly. I don't need all these fancy features."
    - "The interface is so cluttered, I can't find what I'm looking for."
    - "I spend more time figuring out how to use the tool than actually using it."
    - "When I see too many options, I get overwhelmed and just close the app."
    - "The simpler tools are the ones I use most often."
    """

    payload = {
        "research_data": test_data,
        "implementation": "hybrid",
        "include_metadata": True
    }

    try:
        response = requests.post(
            f"{api_url}/analyze", json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            request_id = result.get('request_id')
            print(f"✅ Analysis submitted successfully")
            print(f"   Request ID: {request_id}")
            print(f"   Status: {result.get('status')}")
        else:
            print(f"❌ Analysis submission failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Analysis submission error: {e}")
        return False

    # Test 4: Monitor analysis progress
    print("\n🔍 Test 4: Monitor Analysis Progress")
    print("   Monitoring progress for 60 seconds...")

    start_time = time.time()
    timeout = 60  # 60 seconds timeout

    while time.time() - start_time < timeout:
        try:
            response = requests.get(
                f"{api_url}/analysis/status/{request_id}", timeout=5)
            if response.status_code == 200:
                status = response.json()
                overall_status = status.get('overall_status', 'unknown')

                # Count completed steps
                steps_status = status.get(
                    'analysis_result', {}).get('steps_status', {})
                completed_steps = sum(1 for step in steps_status.values()
                                      if step.get('status') == 'completed')
                total_steps = len(steps_status)

                print(
                    f"   Status: {overall_status} ({completed_steps}/{total_steps} steps completed)")

                if overall_status == 'completed':
                    print("✅ Analysis completed successfully!")

                    # Check if result_data is populated
                    result_data = status.get(
                        'analysis_result', {}).get('result_data', '')
                    if result_data:
                        print(f"✅ Result data path: {result_data}")
                    else:
                        print("⚠️ Result data path is empty")

                    break
                elif overall_status == 'failed':
                    print("❌ Analysis failed")
                    return False

                time.sleep(2)  # Check every 2 seconds
            else:
                print(f"❌ Status check failed: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Status check error: {e}")
            return False

    else:
        print("❌ Analysis monitoring timed out")
        return False

    # Test 5: Load analysis results
    print("\n🔍 Test 5: Load Analysis Results")
    try:
        response = requests.get(f"{api_url}/analyze/{request_id}", timeout=10)
        if response.status_code == 200:
            results = response.json()
            print("✅ Analysis results loaded successfully")

            # Check for expected fields
            expected_fields = ['chunks', 'inferences',
                               'patterns', 'insights', 'design_principles']
            for field in expected_fields:
                if field in results and results[field]:
                    print(f"   {field}: {len(results[field])} items")
                else:
                    print(f"   {field}: No data")
        else:
            print(f"❌ Failed to load results: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Results loading error: {e}")
        return False

    print("\n🎉 Frontend workflow test completed successfully!")
    return True


def test_frontend_components():
    """Test individual frontend components"""

    print("🧪 Testing Frontend Components")
    print("=" * 50)

    api_url = os.getenv('API_BASE_URL', 'http://localhost:8000')

    # Test DynamoDB integration
    print("\n🔍 Test DynamoDB Integration")
    try:
        from dynamodb_tracker import create_dynamodb_tracker
        tracker = create_dynamodb_tracker()

        # Test table info
        table_info = tracker.get_table_info()
        print(f"✅ DynamoDB connected")
        print(f"   Table: {table_info.get('TableName')}")
        print(f"   Status: {table_info.get('TableStatus')}")

        # Test listing analyses
        analyses = tracker.list_analysis_requests(limit=5)
        print(f"   Recent analyses: {len(analyses)}")

    except Exception as e:
        print(f"❌ DynamoDB integration error: {e}")
        return False

    # Test S3 integration
    print("\n🔍 Test S3 Integration")
    try:
        from s3_storage import create_s3_storage
        storage = create_s3_storage()

        bucket_info = storage.get_bucket_info()
        print(f"✅ S3 connected")
        print(f"   Bucket: {bucket_info.get('bucket_name')}")
        print(f"   Region: {bucket_info.get('region')}")

    except Exception as e:
        print(f"❌ S3 integration error: {e}")
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
            response = requests.get(f"{api_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {description}: OK")
            else:
                print(f"⚠️ {description}: {response.status_code}")
        except Exception as e:
            print(f"❌ {description}: {e}")

    print("\n🎉 Frontend components test completed!")
    return True


def main():
    """Main test function"""

    print("🚀 Frontend Integration Test")
    print("=" * 50)

    # Check environment
    print("🔍 Environment Check:")
    print(f"   API_BASE_URL: {os.getenv('API_BASE_URL', 'Not set')}")
    print(
        f"   DYNAMODB_TABLE_NAME: {os.getenv('DYNAMODB_TABLE_NAME', 'Not set')}")
    print(f"   STORAGE_TYPE: {os.getenv('STORAGE_TYPE', 'Not set')}")
    print()

    # Run component tests
    component_success = test_frontend_components()

    if not component_success:
        print("\n❌ Component tests failed. Please check your configuration.")
        return False

    # Run workflow test
    workflow_success = test_frontend_workflow()

    if workflow_success:
        print("\n🎉 All frontend tests passed!")
        print("💡 Your frontend is ready to use!")
        print("🌐 Access it at: http://localhost:8501")
    else:
        print("\n❌ Frontend workflow test failed!")
        print("💡 Check the logs above for details.")

    return workflow_success


if __name__ == "__main__":
    main()
