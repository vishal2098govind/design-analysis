# 🔍 DynamoDB Integration Guide

**Real-Time Analysis Step Tracking with DynamoDB**

This guide explains how to use DynamoDB to track the status of each analysis step in real-time, providing visibility into the progress of your design analysis requests.

## 🎯 What is DynamoDB Tracking?

### **Purpose:**
- 📊 **Real-Time Status** - Track each step of the analysis process
- 🔄 **Progress Monitoring** - See which steps are completed, processing, or failed
- 📝 **Audit Trail** - Maintain history of all analysis requests
- 🚀 **Scalability** - Handle multiple concurrent analysis requests

### **Data Structure:**
```json
{
  "request_id": "analysis_abc123",
  "research_data": "s3://bucket/research-data/interview.txt",
  "analysis_result": {
    "result_data": "s3://bucket/analysis-results/analysis_abc123.json",
    "steps_status": {
      "chunking": {
        "status": "completed",
        "message": "Successfully created 15 chunks",
        "started_at": "2024-01-15T10:30:00Z",
        "completed_at": "2024-01-15T10:30:45Z"
      },
      "inferring": {
        "status": "processing",
        "message": "Starting to infer meanings from chunks",
        "started_at": "2024-01-15T10:30:46Z",
        "completed_at": null
      },
      "relating": {
        "status": "pending",
        "message": "Waiting for inference to complete",
        "started_at": null,
        "completed_at": null
      },
      "explaining": {
        "status": "pending",
        "message": "Waiting for pattern analysis to complete",
        "started_at": null,
        "completed_at": null
      },
      "activating": {
        "status": "pending",
        "message": "Waiting for explanation to complete",
        "started_at": null,
        "completed_at": null
      }
    }
  },
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:46Z",
  "overall_status": "processing"
}
```

## 🚀 Setup Instructions

### **Step 1: Environment Configuration**

Add DynamoDB configuration to your `.env` file:

```bash
# DynamoDB Configuration
DYNAMODB_TABLE_NAME=design-analysis-tracking
DYNAMODB_REGION=us-east-1

# AWS Credentials (same as S3)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_SESSION_TOKEN=
```

### **Step 2: IAM Permissions**

Add DynamoDB permissions to your IAM role/policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "DesignAnalysisDynamoDBAccess",
            "Effect": "Allow",
            "Action": [
                "dynamodb:CreateTable",
                "dynamodb:PutItem",
                "dynamodb:GetItem",
                "dynamodb:UpdateItem",
                "dynamodb:DeleteItem",
                "dynamodb:Scan",
                "dynamodb:DescribeTable"
            ],
            "Resource": [
                "arn:aws:dynamodb:*:*:table/design-analysis-tracking",
                "arn:aws:dynamodb:*:*:table/design-analysis-tracking/*"
            ]
        }
    ]
}
```

### **Step 3: Test the Integration**

Run the DynamoDB integration test:

```bash
python test_dynamodb_integration.py
```

## 🔧 API Endpoints

### **1. Get Analysis Status**
```bash
GET /analysis/status/{request_id}
```

**Response:**
```json
{
  "request_id": "analysis_abc123",
  "status": {
    "request_id": "analysis_abc123",
    "research_data": "s3://bucket/research-data/interview.txt",
    "analysis_result": {
      "result_data": "",
      "steps_status": {
        "chunking": {
          "status": "completed",
          "message": "Successfully created 15 chunks",
          "started_at": "2024-01-15T10:30:00Z",
          "completed_at": "2024-01-15T10:30:45Z"
        }
      }
    },
    "overall_status": "processing"
  }
}
```

### **2. List Analysis Requests**
```bash
GET /analysis/requests?limit=50
```

**Response:**
```json
{
  "requests": [
    {
      "request_id": "analysis_abc123",
      "research_data": "s3://bucket/research-data/interview.txt",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:46Z",
      "overall_status": "processing"
    }
  ],
  "total": 1,
  "limit": 50
}
```

## 📊 Step Status Tracking

### **Status Values:**
- **`pending`** - Step is waiting to start
- **`processing`** - Step is currently running
- **`completed`** - Step finished successfully
- **`failed`** - Step encountered an error

### **Step Flow:**
1. **Chunking** → Break research data into chunks
2. **Inferring** → Extract meanings from chunks
3. **Relating** → Find patterns across meanings
4. **Explaining** → Generate insights from patterns
5. **Activating** → Create design principles from insights

### **Real-Time Updates:**
Each step updates its status in DynamoDB as it progresses:
- **Started** - When step begins processing
- **Completed** - When step finishes successfully
- **Failed** - If step encounters an error

## 🧪 Testing

### **1. Test DynamoDB Integration**
```bash
python test_dynamodb_integration.py
```

### **2. Test API Endpoints**
```bash
# Start the API server
python api_s3.py

# In another terminal, test the endpoints
curl http://localhost:8000/analysis/status/your-request-id
curl http://localhost:8000/analysis/requests?limit=10
```

### **3. Monitor Real-Time Progress**
```bash
# Watch status updates in real-time
watch -n 2 'curl -s http://localhost:8000/analysis/status/your-request-id | jq'
```

## 🔍 Monitoring and Debugging

### **DynamoDB Console:**
1. Go to AWS DynamoDB Console
2. Select your table (`design-analysis-tracking`)
3. Click "Explore table data"
4. View real-time updates

### **CloudWatch Logs:**
Monitor application logs for DynamoDB operations:
```bash
tail -f dynamodb_tracker.log
```

### **Common Issues:**

#### **1. "DynamoDB tracking not available"**
**Cause:** DynamoDB tracker failed to initialize
**Solution:** Check AWS credentials and IAM permissions

#### **2. "Table not found"**
**Cause:** DynamoDB table doesn't exist
**Solution:** The system will create the table automatically on first use

#### **3. "Access denied"**
**Cause:** Insufficient IAM permissions
**Solution:** Add DynamoDB permissions to your IAM role

#### **4. "SSEType AES256 is not supported"**
**Cause:** AES256 encryption not supported in your region/account
**Solution:** The system now uses default DynamoDB encryption (no explicit configuration needed)

## 🎯 Use Cases

### **1. Real-Time Progress Monitoring**
```python
import requests
import time

def monitor_analysis_progress(request_id):
    while True:
        response = requests.get(f"http://localhost:8000/analysis/status/{request_id}")
        status = response.json()
        
        print(f"Overall Status: {status['status']['overall_status']}")
        for step, info in status['status']['analysis_result']['steps_status'].items():
            print(f"  {step}: {info['status']} - {info['message']}")
        
        if status['status']['overall_status'] in ['completed', 'failed']:
            break
            
        time.sleep(5)
```

### **2. Batch Analysis Tracking**
```python
def track_multiple_analyses(request_ids):
    for request_id in request_ids:
        status = requests.get(f"http://localhost:8000/analysis/status/{request_id}").json()
        print(f"{request_id}: {status['status']['overall_status']}")
```

### **3. Error Monitoring**
```python
def monitor_failed_analyses():
    requests = requests.get("http://localhost:8000/analysis/requests").json()
    failed = [req for req in requests['requests'] if req['overall_status'] == 'failed']
    
    for req in failed:
        print(f"Failed analysis: {req['request_id']}")
        # Send alert or retry
```

## 🚀 Production Deployment

### **1. DynamoDB Table Configuration**
- **Billing Mode:** On-demand (pay per request)
- **Encryption:** AES256 (enabled by default)
- **Backup:** Point-in-time recovery (optional)
- **Tags:** Project, Environment, CreatedBy

### **2. Monitoring Setup**
- **CloudWatch Alarms:** Monitor table metrics
- **CloudTrail:** Audit DynamoDB API calls
- **X-Ray:** Trace DynamoDB operations

### **3. Cost Optimization**
- **On-demand billing:** Good for variable workloads
- **Provisioned capacity:** For predictable workloads
- **TTL:** Auto-delete old records (optional)

## 📈 Benefits

### **Operational:**
- 🔍 **Real-Time Visibility** - See exactly what's happening
- 🚨 **Error Detection** - Identify failed steps quickly
- 📊 **Performance Monitoring** - Track step execution times
- 🔄 **Progress Tracking** - Monitor long-running analyses

### **Development:**
- 🐛 **Debugging** - Easier to identify issues
- 📝 **Audit Trail** - Complete history of all requests
- 🔧 **Troubleshooting** - Step-by-step status information
- 📈 **Analytics** - Track usage patterns and performance

### **User Experience:**
- ⏱️ **Progress Updates** - Users can see real-time progress
- 🎯 **Status Clarity** - Clear indication of what's happening
- 🔄 **Retry Logic** - Identify and retry failed steps
- 📊 **Completion Tracking** - Know when analysis is done

## 🎉 Summary

DynamoDB integration provides:
- ✅ **Real-time step tracking**
- ✅ **Progress monitoring**
- ✅ **Error detection**
- ✅ **Audit trail**
- ✅ **Scalable architecture**

Your system now has complete visibility into the analysis process! 🚀
