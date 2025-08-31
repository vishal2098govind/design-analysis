#!/usr/bin/env python3
"""
Test Result Data Update
Tests that the update_result_data method correctly updates only the result_data field
"""

import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_result_data_update():
    """Test that update_result_data method works correctly"""

    print("🧪 Testing Result Data Update")
    print("=" * 50)

    # Check if DynamoDB is available
    try:
        from dynamodb_tracker import create_dynamodb_tracker, StepStatus
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
    request_id = f"test_result_data_{int(time.time())}"
    research_data_s3_path = f"test-research-data/{request_id}.txt"
    test_result_s3_path = f"test-analysis-results/{request_id}.json"

    print(f"📝 Test Request ID: {request_id}")
    print(f"📁 Test Research Data S3 Path: {research_data_s3_path}")
    print(f"📄 Test Result S3 Path: {test_result_s3_path}")

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

    # Test 3: Update step status to completed
    print("\n🔍 Test 3: Updating step status to completed...")
    success = tracker.update_step_status(
        request_id, "activating", StepStatus.COMPLETED,
        "Test step completed successfully"
    )
    if success:
        print("✅ Step status updated successfully")
    else:
        print("❌ Failed to update step status")
        return False

    # Test 4: Update result_data field
    print("\n🔍 Test 4: Updating result_data field...")
    success = tracker.update_result_data(request_id, test_result_s3_path)
    if success:
        print("✅ Result data updated successfully")
    else:
        print("❌ Failed to update result data")
        return False

    # Test 5: Check final status
    print("\n🔍 Test 5: Checking final status...")
    time.sleep(1)  # Wait for DynamoDB updates
    final_status = tracker.get_analysis_status(request_id)
    if final_status:
        print("✅ Final status retrieved successfully")

        # Check result_data field
        result_data = final_status.get(
            'analysis_result', {}).get('result_data', '')
        print(f"   Final result_data: '{result_data}'")

        if result_data == test_result_s3_path:
            print("✅ result_data is correctly updated")
        else:
            print(
                f"❌ result_data is incorrect: expected '{test_result_s3_path}', got '{result_data}'")
            return False

        # Check that step status is still completed
        steps_status = final_status.get(
            'analysis_result', {}).get('steps_status', {})
        activating_status = steps_status.get(
            'activating', {}).get('status', 'unknown')
        print(f"   Activating step status: {activating_status}")

        if activating_status == 'completed':
            print("✅ Activating step status is still completed")
        else:
            print(
                f"❌ Activating step status is {activating_status} (expected 'completed')")
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

    # Test 6: Clean up
    print("\n🔍 Test 6: Cleaning up...")
    try:
        success = tracker.delete_analysis_request(request_id)
        if success:
            print("✅ Test request deleted successfully")
        else:
            print("⚠️ Failed to delete test request (non-critical)")
    except Exception as e:
        print(f"⚠️ Error deleting test request (non-critical): {e}")

    print("\n🎉 Result data update test completed successfully!")
    return True


def main():
    """Main test function"""

    print("🚀 Result Data Update Test")
    print("=" * 50)

    # Check environment
    print("🔍 Environment Check:")
    print(
        f"   DYNAMODB_TABLE_NAME: {os.getenv('DYNAMODB_TABLE_NAME', 'Not set')}")
    print(f"   AWS_REGION: {os.getenv('AWS_REGION', 'Not set')}")
    print()

    # Run test
    success = test_result_data_update()

    if success:
        print("\n🎉 Result data update test passed!")
        print("💡 The update_result_data method works correctly.")
        print("💡 Step status remains unchanged when updating result_data.")
    else:
        print("\n❌ Result data update test failed!")
        print("💡 Check the logs above for details.")

    return success


if __name__ == "__main__":
    main()
