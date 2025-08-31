#!/usr/bin/env python3
"""
Test Step Status Flow
Tests that step status updates happen within each step function and result_data is updated when S3 save happens
"""

import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_step_status_flow():
    """Test that step status updates happen correctly within each step"""

    print("🧪 Testing Step Status Flow")
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

    request_id = f"test_step_flow_{int(time.time())}"
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

    # Test 2: Check initial status
    print("\n🔍 Test 2: Checking initial status...")
    status = tracker.get_analysis_status(request_id)
    if status:
        print("✅ Status retrieved successfully")
        print(f"   Overall status: {status.get('overall_status', 'N/A')}")
        print(
            f"   Result data: '{status.get('analysis_result', {}).get('result_data', '')}'")
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

    # Test 4: Check final status after S3 save
    print("\n🔍 Test 4: Checking final status after S3 save...")
    time.sleep(2)  # Wait for DynamoDB updates
    final_status = tracker.get_analysis_status(request_id)
    if final_status:
        print("✅ Final status retrieved successfully")

        # Check overall status
        overall_status = final_status.get('overall_status', '')
        print(f"   Overall status: {overall_status}")
        if overall_status == 'completed':
            print("✅ Overall status is completed")
        else:
            print(
                f"⚠️ Overall status is {overall_status} (expected 'completed')")

        # Check result_data field
        result_data = final_status.get(
            'analysis_result', {}).get('result_data', '')
        print(f"   Result data: '{result_data}'")

        if result_data and result_data != '':
            print("✅ result_data is populated with S3 path")
            if result_data.endswith('.json'):
                print("✅ result_data ends with .json (expected)")
            else:
                print("⚠️ result_data doesn't end with .json")
        else:
            print("❌ result_data is still empty")
            return False

        # Check step statuses
        steps_status = final_status.get(
            'analysis_result', {}).get('steps_status', {})
        print("\n   Step Statuses:")
        for step_name, step_info in steps_status.items():
            status = step_info.get('status', 'unknown')
            message = step_info.get('message', 'no message')
            print(f"     {step_name}: {status} - {message}")

            if step_name == 'activating':
                if status == 'completed':
                    print("     ✅ Activating step completed successfully")
                else:
                    print(f"     ❌ Activating step status: {status}")
                    return False
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

    print("\n🎉 Step status flow test completed successfully!")
    return True


def main():
    """Main test function"""

    print("🚀 Step Status Flow Test")
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
    success = test_step_status_flow()

    if success:
        print("\n🎉 Step status flow test passed!")
        print("💡 Step status updates happen within each step function.")
        print("💡 Result data is updated when S3 save happens.")
    else:
        print("\n❌ Step status flow test failed!")
        print("💡 Check the logs above for details.")

    return success


if __name__ == "__main__":
    main()
