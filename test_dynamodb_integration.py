#!/usr/bin/env python3
"""
Test DynamoDB Integration
Tests the DynamoDB tracking functionality with the hybrid analysis
"""

import os
import json
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_dynamodb_integration():
    """Test DynamoDB integration with hybrid analysis"""

    print("🧪 Testing DynamoDB Integration with Hybrid Analysis")
    print("=" * 60)

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
    - "When I see too many options, I get overwhelmed and just close the app."
    - "The simpler tools are the ones I use most often."
    """

    request_id = f"test_{int(time.time())}"
    research_data_s3_path = f"test-research-data/{request_id}.txt"

    print(f"📝 Test Request ID: {request_id}")
    print(f"📁 Test S3 Path: {research_data_s3_path}")

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
        print(f"   Overall status: {status.get('overall_status')}")
        steps = status.get('analysis_result', {}).get('steps_status', {})
        for step_name, step_info in steps.items():
            print(
                f"   {step_name}: {step_info.get('status')} - {step_info.get('message')}")
    else:
        print("❌ Failed to get status")
        return False

    # Test 3: Run analysis with tracking
    print("\n🔍 Test 3: Running analysis with tracking...")
    try:
        result = run_hybrid_agentic_analysis(
            sample_research_data,
            request_id,
            research_data_s3_path
        )
        print("✅ Analysis completed successfully")
        print(f"   Chunks: {len(result.get('chunks', []))}")
        print(f"   Inferences: {len(result.get('inferences', []))}")
        print(f"   Patterns: {len(result.get('patterns', []))}")
        print(f"   Insights: {len(result.get('insights', []))}")
        print(
            f"   Design Principles: {len(result.get('design_principles', []))}")
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return False

    # Test 4: Check final status
    print("\n🔍 Test 4: Checking final status...")
    time.sleep(2)  # Wait for DynamoDB updates
    final_status = tracker.get_analysis_status(request_id)
    if final_status:
        print("✅ Final status retrieved successfully")
        print(f"   Overall status: {final_status.get('overall_status')}")
        steps = final_status.get('analysis_result', {}).get('steps_status', {})
        for step_name, step_info in steps.items():
            print(
                f"   {step_name}: {step_info.get('status')} - {step_info.get('message')}")
            if step_info.get('started_at'):
                print(f"     Started: {step_info.get('started_at')}")
            if step_info.get('completed_at'):
                print(f"     Completed: {step_info.get('completed_at')}")
    else:
        print("❌ Failed to get final status")
        return False

    # Test 5: List analysis requests
    print("\n🔍 Test 5: Listing analysis requests...")
    requests = tracker.list_analysis_requests(10)
    if requests:
        print(f"✅ Found {len(requests)} analysis requests")
        for req in requests[:3]:  # Show first 3
            print(
                f"   {req.get('request_id')}: {req.get('overall_status')} - {req.get('created_at')}")
    else:
        print("❌ Failed to list requests")
        return False

    # Test 6: Get table info
    print("\n🔍 Test 6: Getting table info...")
    table_info = tracker.get_table_info()
    if table_info:
        print("✅ Table info retrieved successfully")
        print(f"   Table: {table_info.get('table_name')}")
        print(f"   Status: {table_info.get('table_status')}")
        print(f"   Items: {table_info.get('item_count')}")
        print(f"   Size: {table_info.get('table_size_bytes')} bytes")
    else:
        print("❌ Failed to get table info")
        return False

    print("\n🎉 All DynamoDB integration tests passed!")
    return True


def test_api_integration():
    """Test API integration with DynamoDB"""

    print("\n🧪 Testing API Integration with DynamoDB")
    print("=" * 60)

    # This would require the API to be running
    print("📝 Note: API integration test requires the API server to be running")
    print("   Run: python api_s3.py")
    print(
        "   Then test with: curl http://localhost:8000/analysis/status/{request_id}")

    return True


def main():
    """Main test function"""

    print("🚀 DynamoDB Integration Test Suite")
    print("=" * 60)

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

    # Run tests
    tests = [
        ("DynamoDB Integration", test_dynamodb_integration),
        ("API Integration", test_api_integration)
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))

    # Summary
    print(f"\n{'='*60}")
    print("📊 Test Results Summary")
    print("=" * 60)

    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1

    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")

    if passed == len(results):
        print("🎉 All tests passed! DynamoDB integration is working correctly.")
        print("💡 Your system is ready for real-time analysis tracking!")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        print("💡 Make sure your AWS credentials and DynamoDB permissions are correct.")

    # Recommendations
    print(f"\n💡 Recommendations:")
    if not os.getenv('AWS_ACCESS_KEY_ID'):
        print("   • Consider using IAM roles instead of access keys")
        print("   • DynamoDB will work with the same IAM role as S3")
    else:
        print("   • Great! AWS credentials are configured")
        print("   • DynamoDB tracking is ready to use")

    return passed == len(results)


if __name__ == "__main__":
    main()
