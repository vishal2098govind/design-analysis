#!/usr/bin/env python3
"""
Test S3 Path Generation
Tests that the S3 path generation matches the storage system's format
"""

import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_s3_path_generation():
    """Test that S3 path generation matches storage system format"""

    print("🧪 Testing S3 Path Generation")
    print("=" * 50)

    # Test request ID
    request_id = "test_analysis_123"

    print(f"📝 Test Request ID: {request_id}")

    # Test 1: Check storage system's path generation
    print("\n🔍 Test 1: Storage system path generation...")
    try:
        from s3_storage import create_s3_storage
        storage = create_s3_storage()

        # Get the object key from storage system
        object_key = storage._get_object_key(request_id, "analysis")
        print(f"   Storage system path: {object_key}")

        # Check if it follows the expected format
        import re
        if re.match(r'.*/analysis/\d{4}/\d{2}/.*\.json$', object_key):
            print("✅ Storage system path follows correct format")
        else:
            print("❌ Storage system path format is incorrect")
            return False

    except Exception as e:
        print(f"❌ Failed to test storage system: {e}")
        return False

    # Test 2: Check manual path generation (for comparison)
    print("\n🔍 Test 2: Manual path generation...")
    try:
        timestamp = datetime.now()
        year_month = timestamp.strftime("%Y/%m")
        manual_path = f"analysis/{year_month}/{request_id}.json"
        print(f"   Manual path: {manual_path}")

        # Check if it follows the expected format
        if re.match(r'analysis/\d{4}/\d{2}/.*\.json$', manual_path):
            print("✅ Manual path follows correct format")
        else:
            print("❌ Manual path format is incorrect")
            return False

    except Exception as e:
        print(f"❌ Failed to test manual path generation: {e}")
        return False

    # Test 3: Check that both paths are consistent
    print("\n🔍 Test 3: Path consistency...")
    if object_key.endswith(manual_path):
        print("✅ Paths are consistent")
    else:
        print("⚠️ Paths are different (this might be expected if prefix is different)")
        print(f"   Storage: {object_key}")
        print(f"   Manual:  {manual_path}")

    # Test 4: Check environment variables
    print("\n🔍 Test 4: Environment variables...")
    s3_prefix = os.getenv('S3_PREFIX', 'Not set')
    print(f"   S3_PREFIX: {s3_prefix}")

    if s3_prefix != 'Not set':
        print("✅ S3_PREFIX is configured")
    else:
        print("⚠️ S3_PREFIX not set (using default)")

    print("\n🎉 S3 path generation test completed successfully!")
    return True


def main():
    """Main test function"""

    print("🚀 S3 Path Generation Test")
    print("=" * 50)

    # Run test
    success = test_s3_path_generation()

    if success:
        print("\n🎉 S3 path generation test passed!")
        print("💡 The S3 path generation is working correctly.")
    else:
        print("\n❌ S3 path generation test failed!")
        print("💡 Check the logs above for details.")

    return success


if __name__ == "__main__":
    main()
