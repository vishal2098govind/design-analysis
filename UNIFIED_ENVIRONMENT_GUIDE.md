# 🌍 Unified Environment Configuration

**Single Environment Setup for API and Streamlit Frontend**

Both the FastAPI backend and Streamlit frontend now use the same environment configuration from the `.env` file.

## 🎯 Overview

- **Single `.env` file** for both services
- **Consistent configuration** across API and frontend
- **Easy deployment** with unified settings
- **Debug mode** for development

## 📁 Setup

### **1. Copy Environment File**
```bash
cp env.example .env
```

### **2. Configure Your Settings**
```bash
# Edit with your actual values
nano .env
```

### **3. Key Variables for Both Services**
```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false

# Storage Configuration
STORAGE_TYPE=s3
S3_BUCKET_NAME=your-bucket-name
S3_REGION=us-east-1
S3_PREFIX=design-analysis

# DynamoDB Configuration
DYNAMODB_TABLE_NAME=design-analysis-tracking
DYNAMODB_REGION=us-east-1

# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4-turbo-preview
TEMPERATURE=0.1
```

## 🔧 How It Works

### **API Environment Loading**
```python
# api_s3.py
from dotenv import load_dotenv
load_dotenv()

API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', '8000'))
STORAGE_TYPE = os.getenv('STORAGE_TYPE', 'local')
```

### **Streamlit Environment Loading**
```python
# streamlit_frontend.py
from dotenv import load_dotenv
load_dotenv()

API_BASE_URL = os.getenv('API_BASE_URL', f"http://{os.getenv('API_HOST', 'localhost')}:{os.getenv('API_PORT', '8000')}")
STORAGE_TYPE = os.getenv('STORAGE_TYPE', 'local')
AWS_REGION = os.getenv('AWS_REGION', os.getenv('S3_REGION', 'us-east-1'))
```

### **Run Script Configuration**
```python
# run_streamlit.py
load_dotenv()

# Set API configuration from environment
api_host = os.getenv('API_HOST', 'localhost')
api_port = os.getenv('API_PORT', '8000')
env["API_BASE_URL"] = f"http://{api_host}:{api_port}"

# Set storage configuration
env["STORAGE_TYPE"] = os.getenv('STORAGE_TYPE', 'local')
env["S3_BUCKET_NAME"] = os.getenv('S3_BUCKET_NAME', '')
```

## 📊 Streamlit Settings Page

The Streamlit frontend now includes a comprehensive settings page showing:

- **🌍 Environment Configuration** - Storage type, AWS region, debug mode
- **🔌 API Configuration** - API URL, connection tests
- **💾 Storage Configuration** - S3/local storage details
- **💻 System Information** - Versions and environment info
- **🔍 Debug Information** - All environment variables (when DEBUG=true)

## 🚀 Deployment

### **Systemd Service**
```ini
[Service]
Environment=PATH=/home/ubuntu/design_analysis/venv/bin
Environment=PYTHONPATH=/home/ubuntu/design_analysis
Environment=STREAMLIT_SERVER_PORT=8501
Environment=STREAMLIT_SERVER_ADDRESS=0.0.0.0
# Environment variables loaded from .env file
```

### **Local Development**
```bash
# Start API
python api_s3.py

# Start Streamlit
python run_streamlit.py
```

## 🎯 Benefits

1. **Consistency** - Both services use same configuration
2. **Simplicity** - Single `.env` file to manage
3. **Flexibility** - Easy environment switching
4. **Security** - Centralized credential management

## 🛠️ Troubleshooting

### **Environment Not Loading**
```bash
# Check .env file exists
ls -la .env

# Install python-dotenv
pip install python-dotenv

# Test environment loading
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('STORAGE_TYPE'))"
```

### **Configuration Issues**
```bash
# Check API health
curl http://localhost:8000/health

# Check Streamlit settings page
# Navigate to Settings tab in Streamlit UI
```

The unified environment configuration makes your Design Analysis system easier to manage and deploy! 🎉
