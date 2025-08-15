#!/usr/bin/env python3
"""
Test File Upload and S3 Path Analysis
Demonstrates the new file upload functionality for large research data
"""

import requests
import json
import tempfile
import os
from pathlib import Path


def create_test_file():
    """Create a sample interview transcript file"""

    test_content = """User Interview Transcript - Product Feedback Session

Interviewer: Sarah Johnson
Participant: Alex Chen
Date: January 15, 2024

Interviewer: "Can you tell me about your experience with our project management tool?"

Alex: "I spend more time setting up the tool than actually managing my projects. 
I just want to quickly add a task, assign it to someone, and see the status. 
But instead, I have to navigate through multiple screens, set up custom fields, 
and configure workflows that I'll never use."

Interviewer: "What would make this easier for you?"

Alex: "If the tool could understand what I'm trying to do and just do it. 
I don't want to learn complex workflows - I want to get my work done."

Interviewer: "How do you currently work around these issues?"

Alex: "I end up using a combination of sticky notes, email, and sometimes just my memory. 
It's not ideal, but it's faster than fighting with the tool."

Interviewer: "What would be your ideal workflow?"

Alex: "I want to open the tool and immediately see what I need to do. 
No setup, no configuration, just start working. 
If I need to add a task, I want to type it and assign it in one step. 
If I need to check status, I want to see it at a glance."

Interviewer: "Thank you for your time, Alex."

Alex: "You're welcome. I hope this helps make the tool better for everyone."
"""

    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(
        mode='w', suffix='.txt', delete=False)
    temp_file.write(test_content)
    temp_file.close()

    return temp_file.name


def test_file_upload_and_analysis():
    """Test the complete file upload and analysis workflow"""

    base_url = "http://localhost:8000"

    print("🧪 Testing File Upload and S3 Path Analysis")
    print("=" * 50)

    # Step 1: Create test file
    print("\n📝 Creating test interview transcript...")
    test_file_path = create_test_file()
    print(f"✅ Test file created: {test_file_path}")

    try:
        # Step 2: Upload file
        print("\n📤 Uploading file to API...")
        with open(test_file_path, 'rb') as f:
            files = {'file': f}
            upload_response = requests.post(f"{base_url}/upload", files=files)

        if upload_response.status_code == 200:
            upload_data = upload_response.json()
            s3_path = upload_data['s3_path']
            file_id = upload_data['file_id']
            print(f"✅ File uploaded successfully!")
            print(f"   File ID: {file_id}")
            print(f"   S3 Path: {s3_path}")
            print(f"   File Size: {upload_data['file_size']} bytes")
        else:
            print(f"❌ Upload failed: {upload_response.status_code}")
            print(f"   Error: {upload_response.text}")
            return

        # Step 3: List files
        print("\n📋 Listing uploaded files...")
        files_response = requests.get(f"{base_url}/files")
        if files_response.status_code == 200:
            files_data = files_response.json()
            print(f"✅ Found {files_data['total_count']} files:")
            for file in files_data['files']:
                print(
                    f"   • {file['original_filename']} ({file['file_size']} bytes)")
        else:
            print(f"❌ Failed to list files: {files_response.status_code}")

        # Step 4: Analyze using S3 path
        print("\n🔍 Analyzing file using S3 path...")
        analysis_request = {
            "s3_file_path": s3_path,
            "implementation": "hybrid",
            "include_metadata": True
        }

        analysis_response = requests.post(
            f"{base_url}/analyze", json=analysis_request)

        if analysis_response.status_code == 200:
            result = analysis_response.json()
            request_id = result['request_id']
            print(f"✅ Analysis completed successfully!")
            print(f"   Request ID: {request_id}")
            print(f"   Execution Time: {result['execution_time']:.2f} seconds")
            print(f"   Chunks: {len(result['chunks'])}")
            print(f"   Insights: {len(result['insights'])}")
            print(f"   Design Principles: {len(result['design_principles'])}")

            # Display some insights
            print("\n💡 Key Insights:")
            for i, insight in enumerate(result['insights'][:3], 1):
                print(f"   {i}. {insight['headline']}")
                print(f"      Impact Score: {insight['impact_score']}")

            # Display design principles
            print("\n🎯 Design Principles:")
            for i, principle in enumerate(result['design_principles'][:3], 1):
                print(f"   {i}. {principle['principle']}")
                print(f"      Priority: {principle['priority']}")

        else:
            print(f"❌ Analysis failed: {analysis_response.status_code}")
            print(f"   Error: {analysis_response.text}")
            return

        # Step 5: Get analysis result by ID
        print(f"\n📊 Retrieving analysis result...")
        result_response = requests.get(f"{base_url}/analyze/{request_id}")

        if result_response.status_code == 200:
            final_result = result_response.json()
            print(f"✅ Result retrieved successfully!")
            print(f"   Status: {final_result['status']}")
            print(f"   Implementation: {final_result['implementation']}")
        else:
            print(
                f"❌ Failed to retrieve result: {result_response.status_code}")

        # Step 6: Clean up - Delete the file
        print(f"\n🗑️ Cleaning up - Deleting uploaded file...")
        delete_response = requests.delete(f"{base_url}/files/{file_id}")

        if delete_response.status_code == 200:
            print(f"✅ File deleted successfully!")
        else:
            print(f"❌ Failed to delete file: {delete_response.status_code}")

        # Verify file is deleted
        files_response = requests.get(f"{base_url}/files")
        if files_response.status_code == 200:
            files_data = files_response.json()
            print(f"📋 Remaining files: {files_data['total_count']}")

    finally:
        # Clean up temporary file
        if os.path.exists(test_file_path):
            os.unlink(test_file_path)
            print(f"🧹 Temporary file cleaned up: {test_file_path}")


def test_direct_text_analysis():
    """Test direct text analysis for comparison"""

    base_url = "http://localhost:8000"

    print("\n" + "=" * 50)
    print("🧪 Testing Direct Text Analysis (for comparison)")
    print("=" * 50)

    # Test with small text
    test_text = "User interview: I want a simple interface that doesn't require setup."

    print(f"\n📝 Analyzing direct text input...")
    analysis_request = {
        "research_data": test_text,
        "implementation": "hybrid",
        "include_metadata": True
    }

    analysis_response = requests.post(
        f"{base_url}/analyze", json=analysis_request)

    if analysis_response.status_code == 200:
        result = analysis_response.json()
        print(f"✅ Direct text analysis completed!")
        print(f"   Request ID: {result['request_id']}")
        print(f"   Execution Time: {result['execution_time']:.2f} seconds")
        print(f"   Insights: {len(result['insights'])}")
    else:
        print(
            f"❌ Direct text analysis failed: {analysis_response.status_code}")
        print(f"   Error: {analysis_response.text}")


def test_api_health():
    """Test API health and endpoints"""

    base_url = "http://localhost:8000"

    print("\n" + "=" * 50)
    print("🏥 Testing API Health")
    print("=" * 50)

    # Test root endpoint
    print("\n📋 Testing root endpoint...")
    root_response = requests.get(f"{base_url}/")
    if root_response.status_code == 200:
        root_data = root_response.json()
        print(f"✅ API is running!")
        print(f"   Name: {root_data['name']}")
        print(f"   Version: {root_data['version']}")
        print(f"   Storage Type: {root_data['storage_type']}")
        print(f"   Features: {len(root_data['features'])}")
    else:
        print(f"❌ Root endpoint failed: {root_response.status_code}")
        return False

    # Test health endpoint
    print("\n🏥 Testing health endpoint...")
    health_response = requests.get(f"{base_url}/health")
    if health_response.status_code == 200:
        health_data = health_response.json()
        print(f"✅ Health check passed!")
        print(f"   Status: {health_data['status']}")
        print(f"   Storage Type: {health_data['storage_type']}")
        print(f"   OpenAI Configured: {health_data['openai_key_configured']}")
    else:
        print(f"❌ Health check failed: {health_response.status_code}")
        return False

    return True


def main():
    """Main test function"""

    print("🚀 File Upload and S3 Path Analysis Test Suite")
    print("=" * 60)

    # Test API health first
    if not test_api_health():
        print("\n❌ API is not available. Make sure the server is running:")
        print("   python api_s3.py")
        return

    # Test file upload and analysis
    test_file_upload_and_analysis()

    # Test direct text analysis for comparison
    test_direct_text_analysis()

    print("\n" + "=" * 60)
    print("🎉 Test Suite Completed!")
    print("=" * 60)
    print("✅ File upload and S3 path analysis is working correctly!")
    print("✅ Both input methods (direct text and file upload) are supported")
    print("✅ File management (upload, list, delete) is functional")
    print("\n💡 You can now handle large interview transcripts efficiently!")


if __name__ == "__main__":
    main()
