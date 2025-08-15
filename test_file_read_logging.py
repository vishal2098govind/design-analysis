#!/usr/bin/env python3
"""
Test script to demonstrate file read logging functionality
when using S3 file paths in the analyze API
"""

import requests
import json
import time
from pathlib import Path

# API configuration
API_BASE_URL = "http://localhost:8000"


def test_file_upload_and_analysis():
    """Test uploading a file and then analyzing it using S3 file path"""

    print("🚀 Testing file upload and analysis with logging...")

    # Step 1: Upload a test file
    print("\n📤 Step 1: Uploading test file...")

    # Create a test file
    test_content = """
    Design Analysis Test Document
    
    This is a test document for demonstrating the file read logging functionality
    in the Design Analysis API. The document contains various design principles
    and patterns that can be analyzed by the AI system.
    
    Key Design Principles:
    1. User-Centered Design
    2. Accessibility
    3. Responsive Design
    4. Performance Optimization
    5. Security Best Practices
    
    This document will be uploaded to the API and then analyzed using the S3 file path
    to demonstrate the comprehensive logging that has been implemented.
    """

    # Create test file
    test_file_path = Path("test_design_document.txt")
    with open(test_file_path, "w", encoding="utf-8") as f:
        f.write(test_content)

    # Upload file
    with open(test_file_path, "rb") as f:
        files = {"file": ("test_design_document.txt", f, "text/plain")}
        response = requests.post(f"{API_BASE_URL}/upload", files=files)

    if response.status_code == 200:
        upload_result = response.json()
        print(f"✅ File uploaded successfully!")
        print(f"📁 File ID: {upload_result['file_id']}")
        print(f"📂 S3 Path: {upload_result['s3_path']}")
        print(f"📏 File Size: {upload_result['file_size']} bytes")

        # Step 2: Analyze using S3 file path
        print("\n🔍 Step 2: Analyzing file using S3 file path...")

        analysis_request = {
            "s3_file_path": upload_result['s3_path'],
            "implementation": "hybrid",
            "include_metadata": True
        }

        print(f"📋 Analysis request: {json.dumps(analysis_request, indent=2)}")

        # Send analysis request
        analysis_response = requests.post(
            f"{API_BASE_URL}/analyze",
            json=analysis_request,
            headers={"Content-Type": "application/json"}
        )

        if analysis_response.status_code == 200:
            analysis_result = analysis_response.json()
            print(f"✅ Analysis completed successfully!")
            print(f"🆔 Request ID: {analysis_result['request_id']}")
            print(
                f"⏱️ Execution Time: {analysis_result['execution_time']:.2f} seconds")
            print(f"📊 Results Summary:")
            print(f"   - Chunks: {len(analysis_result['chunks'])}")
            print(f"   - Inferences: {len(analysis_result['inferences'])}")
            print(f"   - Patterns: {len(analysis_result['patterns'])}")
            print(f"   - Insights: {len(analysis_result['insights'])}")
            print(
                f"   - Design Principles: {len(analysis_result['design_principles'])}")

            # Show some sample results
            if analysis_result['insights']:
                print(f"\n💡 Sample Insight:")
                print(
                    f"   {analysis_result['insights'][0]['content'][:200]}...")

            if analysis_result['design_principles']:
                print(f"\n🎯 Sample Design Principle:")
                print(
                    f"   {analysis_result['design_principles'][0]['content'][:200]}...")

        else:
            print(
                f"❌ Analysis failed with status {analysis_response.status_code}")
            print(f"Error: {analysis_response.text}")

    else:
        print(f"❌ File upload failed with status {response.status_code}")
        print(f"Error: {response.text}")

    # Clean up test file
    if test_file_path.exists():
        test_file_path.unlink()
        print(f"\n🧹 Cleaned up test file: {test_file_path}")


def test_direct_analysis():
    """Test direct analysis with research data (for comparison)"""

    print("\n" + "="*60)
    print("🔍 Testing direct analysis (for comparison)...")

    research_data = """
    Direct Analysis Test
    
    This is a direct analysis test that bypasses file upload.
    It demonstrates the logging differences between direct data
    and S3 file path analysis.
    
    Design Patterns:
    - Observer Pattern
    - Factory Pattern
    - Singleton Pattern
    - Strategy Pattern
    """

    analysis_request = {
        "research_data": research_data,
        "implementation": "openai",
        "include_metadata": True
    }

    print(
        f"📋 Direct analysis request (data length: {len(research_data)} chars)")

    analysis_response = requests.post(
        f"{API_BASE_URL}/analyze",
        json=analysis_request,
        headers={"Content-Type": "application/json"}
    )

    if analysis_response.status_code == 200:
        analysis_result = analysis_response.json()
        print(f"✅ Direct analysis completed successfully!")
        print(f"🆔 Request ID: {analysis_result['request_id']}")
        print(
            f"⏱️ Execution Time: {analysis_result['execution_time']:.2f} seconds")
    else:
        print(
            f"❌ Direct analysis failed with status {analysis_response.status_code}")
        print(f"Error: {analysis_response.text}")


def check_api_health():
    """Check if the API is running and healthy"""

    print("🏥 Checking API health...")

    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"✅ API is healthy!")
            print(f"📦 Storage Type: {health['storage_type']}")
            print(
                f"🔑 OpenAI Key Configured: {health['openai_key_configured']}")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to API: {e}")
        print(f"💡 Make sure the API is running on {API_BASE_URL}")
        return False


if __name__ == "__main__":
    print("🧪 Design Analysis API - File Read Logging Test")
    print("=" * 60)

    # Check API health first
    if not check_api_health():
        print("\n❌ API is not available. Please start the API server first.")
        print("💡 Run: python api_s3.py")
        exit(1)

    # Run tests
    test_file_upload_and_analysis()
    test_direct_analysis()

    print("\n" + "="*60)
    print("🎉 Test completed!")
    print("📝 Check the logs in 'api_s3.log' to see the detailed file read logging.")
    print("💡 The logs will show:")
    print("   - File upload process")
    print("   - S3/local file loading with detailed steps")
    print("   - Content decoding attempts")
    print("   - File size and content preview")
    print("   - Analysis execution flow")
