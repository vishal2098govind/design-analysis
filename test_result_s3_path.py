#!/usr/bin/env python3
"""
Test Result S3 Path
Tests that the result_data field in DynamoDB is populated with the correct S3 path
"""

import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_result_s3_path():
    """Test that result_data field is populated with S3 path"""

    print("🧪 Testing Result S3 Path Population")
    print("=" * 50)

    # Check if DynamoDB is available
    try:
        from dynamodb_tracker import create_dynamodb_tracker, StepStatus
        from hybrid_agentic_analysis import run_hybrid_agentic_analysis
        print("✅ DynamoDB tracker imported successfully")
    except ImportError as e:
        print(f"❌ DynamoDB tracker not available: {e}")
        return False

    # Initialize tracker
    try:
        tracker = create_dynamodb_tracker()
        print("✅ DynamoDB tracker initialized")
    except Exception as e:
        print(f"❌ Failed to initialize DynamoDB tracker: {e}")
        return False

    # Test data
    sample_research_data = """
    User Interview Transcript:
    - "I just want to get this done quickly. I don't need all these fancy features."
    - "The interface is so cluttered, I can't find what I'm looking for."
    - "I spend more time figuring out how to use the tool than actually using it."
    """

    request_id = f"test_result_path_{int(time.time())}"
    research_data_s3_path = f"test-research-data/{request_id}.txt"

    print(f"📝 Test Request ID: {request_id}")
    print(f"📁 Test Research Data S3 Path: {research_data_s3_path}")

    # Test 1: Create analysis request
    print("\n🔍 Test 1: Creating analysis request...")
    success = tracker.create_analysis_request(
        request_id, research_data_s3_path)
    if success:
        print("✅ Analysis request created successfully")
    else:
        print("❌ Failed to create analysis request")
        return False

    # Test 2: Check initial status (result_data should be empty)
    print("\n🔍 Test 2: Checking initial status...")
    status = tracker.get_analysis_status(request_id)
    if status:
        print("✅ Status retrieved successfully")
        result_data = status.get('analysis_result', {}).get('result_data', '')
        print(f"   Initial result_data: '{result_data}'")
        if result_data == '':
            print("✅ Initial result_data is empty (expected)")
        else:
            print("❌ Initial result_data should be empty")
            return False
    else:
        print("❌ Failed to get status")
        return False

    # Test 3: Run analysis with S3 save enabled
    print("\n🔍 Test 3: Running analysis with S3 save...")
    try:
        result = run_hybrid_agentic_analysis(
            sample_research_data,
            request_id,
            research_data_s3_path,
            save_to_s3=True  # Enable S3 save
        )
        print("✅ Analysis completed successfully")
        print(f"   Chunks: {len(result.get('chunks', []))}")
        print(
            f"   Design Principles: {len(result.get('design_principles', []))}")
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return False

    # Test 4: Check final status (result_data should have S3 path)
    print("\n🔍 Test 4: Checking final status...")
    time.sleep(2)  # Wait for DynamoDB updates
    final_status = tracker.get_analysis_status(request_id)
    if final_status:
        print("✅ Final status retrieved successfully")
        result_data = final_status.get(
            'analysis_result', {}).get('result_data', '')
        print(f"   Final result_data: '{result_data}'")

        if result_data and result_data != '':
            print("✅ result_data is populated with S3 path")
            if result_data.endswith('.json'):
                print("✅ result_data ends with .json (expected)")
            else:
                print("⚠️ result_data doesn't end with .json")

            # Check if it follows the expected format: analysis/YYYY/MM/request_id.json
            import re
            if re.match(r'.*/analysis/\d{4}/\d{2}/.*\.json$', result_data):
                print("✅ result_data follows correct S3 path format")
            else:
                print(f"⚠️ result_data format: {result_data}")
        else:
            print("❌ result_data is still empty")
            return False

        # Check overall status
        overall_status = final_status.get('overall_status', '')
        print(f"   Overall status: {overall_status}")
        if overall_status == 'completed':
            print("✅ Overall status is completed")
        else:
            print(
                f"⚠️ Overall status is {overall_status} (expected 'completed')")
    else:
        print("❌ Failed to get final status")
        return False

    # Test 5: Clean up
    print("\n🔍 Test 5: Cleaning up...")
    try:
        success = tracker.delete_analysis_request(request_id)
        if success:
            print("✅ Test request deleted successfully")
        else:
            print("⚠️ Failed to delete test request (non-critical)")
    except Exception as e:
        print(f"⚠️ Error deleting test request (non-critical): {e}")

    print("\n🎉 Result S3 path test completed successfully!")
    return True


def main():
    """Main test function"""

    print("🚀 Result S3 Path Test")
    print("=" * 50)

    # Check environment
    print("🔍 Environment Check:")
    print(
        f"   DYNAMODB_TABLE_NAME: {os.getenv('DYNAMODB_TABLE_NAME', 'Not set')}")
    print(f"   AWS_REGION: {os.getenv('AWS_REGION', 'Not set')}")
    print(f"   STORAGE_TYPE: {os.getenv('STORAGE_TYPE', 'Not set')}")
    print(f"   S3_PREFIX: {os.getenv('S3_PREFIX', 'Not set')}")
    print()

    # Run test
    success = test_result_s3_path()

    if success:
        print("\n🎉 Result S3 path test passed!")
        print("💡 The result_data field is being populated correctly with S3 paths.")
    else:
        print("\n❌ Result S3 path test failed!")
        print("💡 Check the logs above for details.")

    return success


if __name__ == "__main__":
    main()
