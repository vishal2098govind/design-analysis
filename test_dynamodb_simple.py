#!/usr/bin/env python3
"""
Simple DynamoDB Test
Tests basic DynamoDB functionality without the full analysis
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_dynamodb_basic():
    """Test basic DynamoDB functionality"""

    print("🧪 Testing Basic DynamoDB Functionality")
    print("=" * 50)

    # Check if DynamoDB is available
    try:
        from dynamodb_tracker import create_dynamodb_tracker
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

    # Test table info
    try:
        table_info = tracker.get_table_info()
        if table_info:
            print("✅ Table info retrieved successfully")
            print(f"   Table: {table_info.get('table_name')}")
            print(f"   Status: {table_info.get('table_status')}")
            print(f"   Items: {table_info.get('item_count')}")
            print(f"   Billing: {table_info.get('billing_mode')}")
        else:
            print("❌ Failed to get table info")
            return False
    except Exception as e:
        print(f"❌ Error getting table info: {e}")
        return False

    # Test creating a simple item
    try:
        request_id = "test_simple_123"
        research_data_path = "s3://test-bucket/test-data.txt"

        success = tracker.create_analysis_request(
            request_id, research_data_path)
        if success:
            print("✅ Test item created successfully")
        else:
            print("❌ Failed to create test item")
            return False
    except Exception as e:
        print(f"❌ Error creating test item: {e}")
        return False

    # Test retrieving the item
    try:
        status = tracker.get_analysis_status(request_id)
        if status:
            print("✅ Test item retrieved successfully")
            print(f"   Request ID: {status.get('request_id')}")
            print(f"   Overall Status: {status.get('overall_status')}")
        else:
            print("❌ Failed to retrieve test item")
            return False
    except Exception as e:
        print(f"❌ Error retrieving test item: {e}")
        return False

    # Test listing items
    try:
        requests = tracker.list_analysis_requests(10)
        print(f"✅ Listed {len(requests)} analysis requests")
    except Exception as e:
        print(f"❌ Error listing requests: {e}")
        return False

    # Clean up test item
    try:
        success = tracker.delete_analysis_request(request_id)
        if success:
            print("✅ Test item deleted successfully")
        else:
            print("⚠️ Failed to delete test item (non-critical)")
    except Exception as e:
        print(f"⚠️ Error deleting test item (non-critical): {e}")

    print("\n🎉 Basic DynamoDB test completed successfully!")
    return True


def main():
    """Main test function"""

    print("🚀 Basic DynamoDB Test")
    print("=" * 50)

    # Check environment
    print("🔍 Environment Check:")
    print(
        f"   DYNAMODB_TABLE_NAME: {os.getenv('DYNAMODB_TABLE_NAME', 'Not set')}")
    print(f"   AWS_REGION: {os.getenv('AWS_REGION', 'Not set')}")
    print(
        f"   AWS_ACCESS_KEY_ID: {'Set' if os.getenv('AWS_ACCESS_KEY_ID') else 'Not set'}")
    print(
        f"   AWS_SECRET_ACCESS_KEY: {'Set' if os.getenv('AWS_SECRET_ACCESS_KEY') else 'Not set'}")
    print()

    # Run test
    success = test_dynamodb_basic()

    if success:
        print("\n🎉 Basic DynamoDB test passed!")
        print("💡 DynamoDB integration is working correctly.")
    else:
        print("\n❌ Basic DynamoDB test failed!")
        print("💡 Check your AWS credentials and permissions.")

    return success


if __name__ == "__main__":
    main()
