#!/usr/bin/env python3
"""
Run Streamlit Frontend
Script to start the Streamlit frontend for the Design Analysis System
"""

import subprocess
import sys
import os
from pathlib import Path


def main():
    """Run the Streamlit frontend"""

    print("🚀 Starting Design Analysis System Frontend")
    print("=" * 50)

    # Check if streamlit is installed
    try:
        import streamlit
        print(f"✅ Streamlit {streamlit.__version__} is installed")
    except ImportError:
        print("❌ Streamlit is not installed. Installing...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "streamlit>=1.28.1"])
        print("✅ Streamlit installed successfully")

    # Check if pandas is installed
    try:
        import pandas
        print(f"✅ Pandas {pandas.__version__} is installed")
    except ImportError:
        print("❌ Pandas is not installed. Installing...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "pandas>=2.0.0"])
        print("✅ Pandas installed successfully")

    # Check if the frontend file exists
    frontend_file = Path("streamlit_frontend.py")
    if not frontend_file.exists():
        print("❌ streamlit_frontend.py not found!")
        print("Please make sure the file exists in the current directory.")
        return

    print("✅ Frontend file found")

    # Set environment variables for Streamlit
    env = os.environ.copy()

    # Streamlit-specific settings
    env["STREAMLIT_SERVER_PORT"] = "8501"
    env["STREAMLIT_SERVER_ADDRESS"] = "0.0.0.0"
    env["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"

    # Load environment variables from .env file
    from dotenv import load_dotenv
    load_dotenv()

    # Set API configuration from environment
    api_host = os.getenv('API_HOST', 'localhost')
    api_port = os.getenv('API_PORT', '8000')
    env["API_BASE_URL"] = f"http://{api_host}:{api_port}"

    # Set storage configuration
    env["STORAGE_TYPE"] = os.getenv('STORAGE_TYPE', 'local')
    env["S3_BUCKET_NAME"] = os.getenv('S3_BUCKET_NAME', '')
    env["S3_REGION"] = os.getenv('S3_REGION', 'us-east-1')
    env["S3_PREFIX"] = os.getenv('S3_PREFIX', 'design-analysis')

    # Set DynamoDB configuration
    env["DYNAMODB_TABLE_NAME"] = os.getenv(
        'DYNAMODB_TABLE_NAME', 'design-analysis-tracking')
    env["DYNAMODB_REGION"] = os.getenv(
        'DYNAMODB_REGION', os.getenv('S3_REGION', 'us-east-1'))

    # Set AWS configuration
    env["AWS_REGION"] = os.getenv(
        'AWS_REGION', os.getenv('S3_REGION', 'us-east-1'))
    env["DEBUG"] = os.getenv('DEBUG', 'false')

    print(f"🔧 API Base URL: {env['API_BASE_URL']}")
    print(f"💾 Storage Type: {env['STORAGE_TYPE']}")
    print(f"🌍 AWS Region: {env['AWS_REGION']}")
    print(f"🐛 Debug Mode: {env['DEBUG']}")

    print("\n🌐 Starting Streamlit server...")
    print("📱 Frontend will be available at: http://localhost:8501")
    print("🔧 API should be running at: http://localhost:8000")
    print("\n💡 Make sure your API is running before using the frontend!")
    print("   You can start the API with: python api_s3.py")
    print("\n" + "=" * 50)

    try:
        # Run streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_frontend.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0",
            "--browser.gatherUsageStats", "false"
        ], env=env)
    except KeyboardInterrupt:
        print("\n👋 Frontend stopped by user")
    except Exception as e:
        print(f"\n❌ Error running frontend: {e}")


if __name__ == "__main__":
    main()
