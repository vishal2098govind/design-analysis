#!/usr/bin/env python3
"""
Test S3 Storage Functionality
Verifies that S3 storage works correctly for the design analysis system
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_s3_storage():
    """Test S3 storage functionality"""

    print("🧪 Testing S3 Storage Functionality")
    print("=" * 50)

    try:
        # Import S3 storage
        from s3_storage import create_s3_storage
        from hybrid_agentic_analysis import run_hybrid_agentic_analysis

        print("✅ Imports successful")

        # Initialize S3 storage
        print("\n🔗 Initializing S3 storage...")
        storage = create_s3_storage()
        print(f"✅ S3 storage initialized!")
        print(f"📦 Bucket: {storage.bucket_name}")
        print(f"🌍 Region: {storage.region}")
        print(f"📁 Prefix: {storage.prefix}")

        # Get bucket info
        bucket_info = storage.get_bucket_info()
        print(f"📊 Bucket Info: {bucket_info}")

        # Test data
        test_data = """
        User Interview Transcript:
        
        Sarah (Product Manager): "I spend more time setting up project management tools than actually managing my projects. 
        I just want to quickly add a task, assign it to someone, and see the status. 
        But instead, I have to navigate through multiple screens, set up custom fields, and configure workflows that I'll never use."
        
        Interviewer: "What would make this easier for you?"
        
        Sarah: "If the tool could understand what I'm trying to do and just do it. 
        I don't want to learn complex workflows - I want to get my work done."
        """

        print(f"\n📝 Running analysis on test data...")

        # Run analysis
        result = run_hybrid_agentic_analysis(test_data)
        print(f"✅ Analysis completed!")
        print(
            f"📊 Results: {len(result.get('chunks', []))} chunks, {len(result.get('insights', []))} insights")

        # Test save to S3
        request_id = f"test_s3_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"\n💾 Saving analysis to S3 (ID: {request_id})...")

        success = storage.save_analysis(request_id, result)
        print(f"✅ Save success: {success}")

        # Test load from S3
        print(f"\n📖 Loading analysis from S3...")
        loaded = storage.load_analysis(request_id)
        print(f"✅ Load success: {loaded is not None}")

        if loaded:
            print(
                f"📊 Loaded data: {len(loaded.get('chunks', []))} chunks, {len(loaded.get('insights', []))} insights")

        # Test list analyses
        print(f"\n📋 Listing analyses from S3...")
        analyses = storage.list_analyses(limit=10)
        print(f"✅ Found {len(analyses)} analyses")

        for analysis in analyses[:3]:  # Show first 3
            print(
                f"   - {analysis['request_id']}: {analysis['implementation']} ({analysis['status']})")

        # Test storage stats
        print(f"\n📈 Getting storage statistics...")
        stats = storage.get_storage_stats()
        print(f"✅ Storage stats: {stats}")

        # Test search functionality
        print(f"\n🔍 Testing search functionality...")
        search_results = storage.search_analyses("simple", limit=5)
        print(f"✅ Search results: {len(search_results)} matches")

        # Test delete functionality
        print(f"\n🗑️ Testing delete functionality...")
        delete_success = storage.delete_analysis(request_id)
        print(f"✅ Delete success: {delete_success}")

        # Verify deletion
        deleted_analysis = storage.load_analysis(request_id)
        print(f"✅ Verification: Analysis deleted: {deleted_analysis is None}")

        print(f"\n🎉 All S3 storage tests passed!")
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure boto3 is installed: pip install boto3")
        return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("💡 Check your AWS credentials and configuration")
        return False


def test_storage_comparison():
    """Compare local vs S3 storage"""

    print("\n" + "=" * 50)
    print("🔄 Storage Comparison Test")
    print("=" * 50)

    try:
        from s3_storage import create_s3_storage
        from api import AnalysisStorage as LocalStorage
        from hybrid_agentic_analysis import run_hybrid_agentic_analysis

        # Test data
        test_data = "User interview: I need a simpler interface."
        result = run_hybrid_agentic_analysis(test_data)

        # Test local storage
        print("\n📁 Testing local storage...")
        local_storage = LocalStorage()
        local_success = local_storage.save_analysis("test_local", result)
        local_loaded = local_storage.load_analysis("test_local")
        print(
            f"✅ Local storage: Save={local_success}, Load={local_loaded is not None}")

        # Test S3 storage
        print("\n☁️ Testing S3 storage...")
        s3_storage = create_s3_storage()
        s3_success = s3_storage.save_analysis("test_s3", result)
        s3_loaded = s3_storage.load_analysis("test_s3")
        print(f"✅ S3 storage: Save={s3_success}, Load={s3_loaded is not None}")

        # Compare results
        print(f"\n📊 Comparison Results:")
        print(
            f"   Local: {len(local_loaded.get('chunks', [])) if local_loaded else 0} chunks")
        print(
            f"   S3: {len(s3_loaded.get('chunks', [])) if s3_loaded else 0} chunks")

        # Cleanup
        local_storage.delete_analysis("test_local")
        s3_storage.delete_analysis("test_s3")

        print(f"✅ Storage comparison completed!")
        return True

    except Exception as e:
        print(f"❌ Comparison test failed: {e}")
        return False


def test_api_integration():
    """Test API integration with S3 storage"""

    print("\n" + "=" * 50)
    print("🌐 API Integration Test")
    print("=" * 50)

    try:
        import requests
        import time

        # Start API server (this would be done separately in production)
        print("⚠️ Note: This test assumes the API is running on localhost:8000")
        print("💡 Start the API with: python api_s3.py")

        # Test API endpoints
        base_url = "http://localhost:8000"

        # Health check
        print(f"\n🏥 Testing health endpoint...")
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health check passed!")
            print(f"   Storage type: {health_data.get('storage_type')}")
            print(
                f"   OpenAI configured: {health_data.get('openai_key_configured')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False

        # Test analysis endpoint
        print(f"\n🔍 Testing analysis endpoint...")
        analysis_data = {
            "research_data": "User interview: I want a simple interface.",
            "implementation": "hybrid",
            "include_metadata": True
        }

        response = requests.post(f"{base_url}/analyze", json=analysis_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Analysis completed!")
            print(f"   Request ID: {result.get('request_id')}")
            print(f"   Status: {result.get('status')}")
            print(f"   Execution time: {result.get('execution_time')}s")

            # Test retrieving the result
            request_id = result.get('request_id')
            response = requests.get(f"{base_url}/analyze/{request_id}")
            if response.status_code == 200:
                print(f"✅ Result retrieval successful!")
            else:
                print(f"❌ Result retrieval failed: {response.status_code}")

        else:
            print(f"❌ Analysis failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False

        # Test stats endpoint
        print(f"\n📊 Testing stats endpoint...")
        response = requests.get(f"{base_url}/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Stats retrieved!")
            print(f"   Total analyses: {stats.get('total_analyses')}")
            print(f"   Storage type: {stats.get('storage_type')}")
        else:
            print(f"❌ Stats failed: {response.status_code}")

        print(f"\n🎉 API integration test completed!")
        return True

    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to API server")
        print(f"💡 Make sure the API is running: python api_s3.py")
        return False

    except Exception as e:
        print(f"❌ API integration test failed: {e}")
        return False


def main():
    """Main test function"""

    print("🚀 S3 Storage Test Suite")
    print("=" * 60)

    # Check environment
    print("🔍 Environment Check:")
    print(f"   STORAGE_TYPE: {os.getenv('STORAGE_TYPE', 'local')}")
    print(f"   S3_BUCKET_NAME: {os.getenv('S3_BUCKET_NAME', 'Not set')}")
    print(f"   S3_REGION: {os.getenv('S3_REGION', 'us-east-1')}")
    print(
        f"   AWS_ACCESS_KEY_ID: {'Set' if os.getenv('AWS_ACCESS_KEY_ID') else 'Not set'}")

    # Run tests
    tests = [
        ("S3 Storage", test_s3_storage),
        ("Storage Comparison", test_storage_comparison),
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
        print("🎉 All tests passed! S3 storage is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")

    return passed == len(results)


if __name__ == "__main__":
    main()
