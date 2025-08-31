# 🌐 Streamlit Frontend Guide

**Web Interface for Design Analysis System**

This guide explains how to set up and use the Streamlit frontend for your Design Analysis system.

## 🎯 What is the Streamlit Frontend?

### **Purpose:**
- 🌐 **Web Interface** - User-friendly web application for interacting with the Design Analysis system
- 📊 **Real-Time Monitoring** - Live progress tracking of analysis steps
- 📝 **Easy Data Input** - Multiple ways to input research data (text, file upload, S3 path)
- 📋 **Analysis Management** - View history, filter results, and manage analyses
- ⚙️ **System Configuration** - Configure API endpoints and check system status

### **Features:**
- **Dashboard** - System status and recent analyses overview
- **New Analysis** - Submit new analysis requests with various input methods
- **Analysis History** - View and filter past analyses
- **Settings** - Configure API endpoints and check system health

## 🚀 Setup Instructions

### **Step 1: Install Dependencies**

Add Streamlit and pandas to your requirements:

```bash
pip install streamlit>=1.28.1 pandas>=2.0.0
```

Or update your `requirements.txt`:

```txt
streamlit>=1.28.1
pandas>=2.0.0
```

### **Step 2: Environment Configuration**

Add frontend-specific environment variables to your `.env` file:

```bash
# Frontend Configuration
API_BASE_URL=http://localhost:8000
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Existing variables (should already be set)
DYNAMODB_TABLE_NAME=design-analysis-tracking
AWS_REGION=us-east-1
STORAGE_TYPE=s3
S3_PREFIX=design-analysis
```

### **Step 3: Start the Frontend**

#### **Option A: Using the Run Script**
```bash
python run_streamlit.py
```

#### **Option B: Direct Streamlit Command**
```bash
streamlit run streamlit_frontend.py --server.port 8501 --server.address 0.0.0.0
```

#### **Option C: Development Mode**
```bash
streamlit run streamlit_frontend.py --server.port 8501 --server.address 0.0.0.0 --server.runOnSave true
```

### **Step 4: Access the Frontend**

Open your browser and navigate to:
```
http://localhost:8501
```

## 📱 Using the Frontend

### **Dashboard Page**

The dashboard provides an overview of your system:

- **System Status** - API and DynamoDB connection status
- **Recent Analyses** - Count of recent and completed analyses
- **Analysis Table** - Recent analyses with status indicators
- **Quick Actions** - View details of selected analyses

### **New Analysis Page**

Submit new analysis requests:

#### **Configuration:**
- **Implementation** - Choose between `hybrid`, `openai`, or `langchain`
- **Include Metadata** - Toggle detailed metadata in responses

#### **Research Data Input:**
1. **Direct Text Input** - Paste research data directly
2. **File Upload** - Upload text files (.txt, .md, .json, .csv)
3. **S3 Path** - Use existing S3 file paths

#### **Progress Monitoring:**
- Real-time progress bar showing step completion
- Live status updates from DynamoDB
- Automatic completion detection

### **Analysis History Page**

View and manage past analyses:

#### **Filtering Options:**
- **Status Filter** - Filter by completion status
- **Date Filter** - Filter by creation date
- **Search** - Search by request ID

#### **Analysis Details:**
- **Basic Info** - Status, creation time, update time
- **Research Data** - S3 path to input data
- **Step Status** - Detailed status of each analysis step
- **Results** - S3 path to analysis results
- **Load Results** - View formatted analysis results

### **Settings Page**

Configure and monitor system:

#### **API Configuration:**
- **API Base URL** - Configure API endpoint
- **Connection Test** - Test API connectivity

#### **DynamoDB Configuration:**
- **Table Name** - DynamoDB table configuration
- **Connection Test** - Test DynamoDB connectivity

#### **System Information:**
- Python and Streamlit versions
- Current configuration values

## 🔧 Configuration Options

### **Environment Variables**

| Variable | Default | Description |
|----------|---------|-------------|
| `API_BASE_URL` | `http://localhost:8000` | Base URL for the Design Analysis API |
| `DYNAMODB_TABLE_NAME` | `design-analysis-tracking` | DynamoDB table for tracking |
| `STREAMLIT_SERVER_PORT` | `8501` | Port for Streamlit server |
| `STREAMLIT_SERVER_ADDRESS` | `0.0.0.0` | Address for Streamlit server |

### **Streamlit Configuration**

Create a `.streamlit/config.toml` file for custom configuration:

```toml
[server]
port = 8501
address = "0.0.0.0"
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
```

## 🚀 Deployment Options

### **Local Development**
```bash
# Terminal 1: Start API
python api_s3.py

# Terminal 2: Start Frontend
python run_streamlit.py
```

### **Docker Deployment**
```dockerfile
# Dockerfile for frontend
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "streamlit_frontend.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### **Cloud Deployment**

#### **Heroku:**
```bash
# Create Procfile
echo "web: streamlit run streamlit_frontend.py --server.port=\$PORT --server.address=0.0.0.0" > Procfile

# Deploy
heroku create your-app-name
git push heroku main
```

#### **AWS EC2:**
```bash
# Install dependencies
pip install streamlit pandas

# Run with systemd service
sudo systemctl start streamlit-frontend
```

## 🧪 Testing the Frontend

### **Manual Testing**

1. **Start both services:**
   ```bash
   # Terminal 1
   python api_s3.py
   
   # Terminal 2
   python run_streamlit.py
   ```

2. **Test each page:**
   - Dashboard - Check system status
   - New Analysis - Submit test analysis
   - Analysis History - View results
   - Settings - Test connections

### **Automated Testing**

Create test scripts for frontend functionality:

```python
# test_frontend.py
import requests
import time

def test_frontend_workflow():
    """Test complete frontend workflow"""
    
    # Test API health
    response = requests.get("http://localhost:8000/health")
    assert response.status_code == 200
    
    # Test frontend accessibility
    response = requests.get("http://localhost:8501")
    assert response.status_code == 200
    
    # Test analysis submission
    payload = {
        "research_data": "Test research data for frontend testing",
        "implementation": "hybrid",
        "include_metadata": True
    }
    
    response = requests.post("http://localhost:8000/analyze", json=payload)
    assert response.status_code == 200
    
    result = response.json()
    request_id = result.get('request_id')
    
    # Monitor progress
    for _ in range(30):  # Wait up to 60 seconds
        time.sleep(2)
        # Check status via API
        response = requests.get(f"http://localhost:8000/analysis/status/{request_id}")
        if response.status_code == 200:
            status = response.json()
            if status.get('overall_status') == 'completed':
                print("✅ Frontend workflow test passed!")
                return True
    
    print("❌ Frontend workflow test failed!")
    return False
```

## 🔍 Troubleshooting

### **Common Issues**

#### **Frontend won't start:**
```bash
# Check if port is in use
lsof -i :8501

# Kill existing process
kill -9 <PID>

# Start with different port
streamlit run streamlit_frontend.py --server.port 8502
```

#### **API connection failed:**
```bash
# Check API status
curl http://localhost:8000/health

# Check environment variables
echo $API_BASE_URL

# Test API directly
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"research_data": "test", "implementation": "hybrid"}'
```

#### **DynamoDB connection failed:**
```bash
# Check AWS credentials
aws sts get-caller-identity

# Test DynamoDB access
python -c "from dynamodb_tracker import create_dynamodb_tracker; tracker = create_dynamodb_tracker(); print(tracker.get_table_info())"
```

### **Logs and Debugging**

#### **Streamlit Logs:**
```bash
# Enable debug logging
streamlit run streamlit_frontend.py --logger.level debug

# Check logs in browser
# Go to http://localhost:8501 and check browser console
```

#### **API Logs:**
```bash
# Run API with debug logging
python api_s3.py --log-level debug
```

## 🎨 Customization

### **Styling**

Modify the CSS in `streamlit_frontend.py`:

```python
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    font-weight: bold;
    color: #1f77b4;  # Change primary color
    text-align: center;
    margin-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)
```

### **Adding New Pages**

Add new pages to the navigation:

```python
# In main() function
page = st.sidebar.selectbox(
    "Choose a page:",
    ["📊 Dashboard", "📝 New Analysis", "📋 Analysis History", "⚙️ Settings", "🆕 New Page"]
)

# Add new page handler
elif page == "🆕 New Page":
    show_new_page()

def show_new_page():
    """Show new page content"""
    st.markdown('<h2 class="sub-header">🆕 New Page</h2>', unsafe_allow_html=True)
    # Add your page content here
```

## 📚 Best Practices

### **Performance**
- Use caching for expensive operations
- Implement pagination for large datasets
- Optimize database queries

### **User Experience**
- Provide clear error messages
- Add loading indicators
- Implement responsive design

### **Security**
- Validate all user inputs
- Implement proper authentication
- Use HTTPS in production

### **Monitoring**
- Add health checks
- Monitor API response times
- Track user interactions

## 🚀 Next Steps

1. **Deploy to Production** - Set up production environment
2. **Add Authentication** - Implement user authentication
3. **Enhanced Analytics** - Add usage analytics and reporting
4. **Mobile Optimization** - Optimize for mobile devices
5. **API Documentation** - Add interactive API docs to frontend

The Streamlit frontend provides a powerful, user-friendly interface for your Design Analysis system! 🎉
