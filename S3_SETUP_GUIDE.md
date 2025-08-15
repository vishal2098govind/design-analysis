# AWS S3 Storage Setup Guide

This guide shows you how to set up AWS S3 storage for the Design Analysis system in production.

## 🎯 Why Use S3 Storage?

### **Benefits:**
- **🔒 Scalability**: Handle unlimited analysis results
- **🌍 Global Access**: Access data from anywhere
- **💰 Cost-Effective**: Pay only for what you use
- **🛡️ Security**: Built-in encryption and access controls
- **📊 Analytics**: Built-in monitoring and metrics
- **🔄 Reliability**: 99.999999999% durability
- **⚡ Performance**: Fast access with CDN integration

### **Use Cases:**
- **Production Deployments**: Replace local file storage
- **Multi-Instance**: Share data across multiple API instances
- **Backup & Recovery**: Automatic data protection
- **Compliance**: Meet data retention requirements
- **Cost Optimization**: Lifecycle policies for cost management

## 🚀 Quick Setup

### 1. **Install Dependencies**
```bash
pip install boto3 botocore
```

### 2. **Configure AWS Credentials**

#### Option A: Environment Variables
```bash
export AWS_ACCESS_KEY_ID="your_access_key"
export AWS_SECRET_ACCESS_KEY="your_secret_key"
export AWS_REGION="us-east-1"
```

#### Option B: AWS CLI Configuration
```bash
aws configure
```

#### Option C: IAM Role (Recommended for Production)
- Attach IAM role to your EC2 instance or ECS task
- No credentials needed in code

### 3. **Set Environment Variables**
```bash
# Storage configuration
export STORAGE_TYPE="s3"
export S3_BUCKET_NAME="my-design-analysis-bucket"
export S3_REGION="us-east-1"
export S3_PREFIX="design-analysis"

# Optional: Custom bucket name
export S3_BUCKET_NAME="my-company-design-analysis-2024"
```

### 4. **Run the API**
```bash
python api_s3.py
```

## 🔧 Detailed Configuration

### **Environment Variables**

| Variable | Default | Description |
|----------|---------|-------------|
| `STORAGE_TYPE` | `local` | Storage type: `local` or `s3` |
| `S3_BUCKET_NAME` | Auto-generated | S3 bucket name |
| `S3_REGION` | `us-east-1` | AWS region |
| `S3_PREFIX` | `design-analysis` | Folder prefix in S3 |

### **AWS Credentials**

#### **Access Key Method** (Development)
```bash
export AWS_ACCESS_KEY_ID="AKIAIOSFODNN7EXAMPLE"
export AWS_SECRET_ACCESS_KEY="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
export AWS_REGION="us-east-1"
```

#### **IAM Role Method** (Production)
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:CreateBucket",
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket",
        "s3:PutBucketVersioning",
        "s3:PutBucketLifecycleConfiguration",
        "s3:PutBucketEncryption"
      ],
      "Resource": [
        "arn:aws:s3:::design-analysis-*",
        "arn:aws:s3:::design-analysis-*/*"
      ]
    }
  ]
}
```

## 📦 S3 Bucket Features

### **Automatic Configuration**
The system automatically configures your S3 bucket with:

- **🔒 Encryption**: AES-256 server-side encryption
- **📝 Versioning**: Data protection and recovery
- **💰 Lifecycle Policies**: Cost optimization
  - 30 days → Standard-IA
  - 90 days → Glacier
  - 365 days → Expiration
- **📁 Organized Structure**: Year/month folder organization

### **Folder Structure**
```
design-analysis/
├── analysis/
│   ├── 2024/
│   │   ├── 01/
│   │   │   ├── abc123-def4-5678.json
│   │   │   └── xyz789-abc1-2345.json
│   │   └── 02/
│   │       └── def456-ghi7-8901.json
│   └── 2023/
│       └── 12/
│           └── old-analysis.json
└── metadata/
    └── storage-stats.json
```

## 🛠️ Production Deployment

### **1. Docker Deployment**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV STORAGE_TYPE=s3
ENV S3_BUCKET_NAME=production-design-analysis
ENV S3_REGION=us-east-1

EXPOSE 8000
CMD ["python", "api_s3.py"]
```

### **2. Kubernetes Deployment**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: design-analysis-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: design-analysis-api
  template:
    metadata:
      labels:
        app: design-analysis-api
    spec:
      containers:
      - name: api
        image: design-analysis-api:latest
        env:
        - name: STORAGE_TYPE
          value: "s3"
        - name: S3_BUCKET_NAME
          value: "production-design-analysis"
        - name: S3_REGION
          value: "us-east-1"
        ports:
        - containerPort: 8000
```

### **3. AWS ECS Deployment**
```json
{
  "family": "design-analysis-api",
  "taskRoleArn": "arn:aws:iam::123456789012:role/DesignAnalysisS3Role",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "api",
      "image": "design-analysis-api:latest",
      "environment": [
        {
          "name": "STORAGE_TYPE",
          "value": "s3"
        },
        {
          "name": "S3_BUCKET_NAME",
          "value": "production-design-analysis"
        }
      ],
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ]
    }
  ]
}
```

## 🔍 Monitoring & Analytics

### **S3 Analytics**
```python
# Get storage statistics
curl http://localhost:8000/storage/info

# Response:
{
  "storage_type": "s3",
  "configuration": {
    "s3_bucket_name": "design-analysis-abc123",
    "s3_region": "us-east-1",
    "s3_prefix": "design-analysis"
  },
  "storage_info": {
    "bucket_name": "design-analysis-abc123",
    "region": "us-east-1",
    "versioning_status": "Enabled",
    "encryption_enabled": true
  },
  "stats": {
    "total_analyses": 150,
    "total_size_mb": 45.2,
    "implementations_used": {
      "hybrid": 100,
      "openai": 30,
      "langchain": 20
    }
  }
}
```

### **AWS CloudWatch Metrics**
- **Storage Usage**: Monitor bucket size and object count
- **Request Metrics**: Track API calls and errors
- **Cost Monitoring**: Monitor S3 costs and usage patterns

## 💰 Cost Optimization

### **Lifecycle Policies**
The system automatically configures cost optimization:

```json
{
  "Rules": [
    {
      "ID": "CostOptimization",
      "Status": "Enabled",
      "Filter": {"Prefix": "design-analysis/"},
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "STANDARD_IA"
        },
        {
          "Days": 90,
          "StorageClass": "GLACIER"
        }
      ],
      "Expiration": {
        "Days": 365
      }
    }
  ]
}
```

### **Cost Estimates** (Monthly)
- **1,000 analyses** (~50MB): ~$0.50
- **10,000 analyses** (~500MB): ~$2.50
- **100,000 analyses** (~5GB): ~$15.00

## 🔒 Security Best Practices

### **1. IAM Policies**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::design-analysis-*",
        "arn:aws:s3:::design-analysis-*/*"
      ],
      "Condition": {
        "StringEquals": {
          "aws:RequestTag/Environment": "production"
        }
      }
    }
  ]
}
```

### **2. Bucket Policies**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyUnencryptedObjectUploads",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::design-analysis-*/*",
      "Condition": {
        "StringNotEquals": {
          "s3:x-amz-server-side-encryption": "AES256"
        }
      }
    }
  ]
}
```

### **3. VPC Endpoints** (Private Access)
```bash
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-12345678 \
  --service-name com.amazonaws.us-east-1.s3 \
  --region us-east-1
```

## 🔄 Migration from Local Storage

### **1. Backup Local Data**
```python
from s3_storage import create_s3_storage

# Create S3 storage
s3_storage = create_s3_storage()

# Backup local data to S3
s3_storage.backup_to_local("local_backup")
```

### **2. Migrate Existing Data**
```python
import json
from pathlib import Path
from s3_storage import create_s3_storage

# Load local analyses
local_dir = Path("analysis_results")
s3_storage = create_s3_storage()

for file_path in local_dir.glob("*.json"):
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    request_id = file_path.stem
    s3_storage.save_analysis(request_id, data)
    print(f"Migrated: {request_id}")
```

### **3. Verify Migration**
```bash
# Check local count
ls analysis_results/*.json | wc -l

# Check S3 count
curl http://localhost:8000/stats | jq '.total_analyses'
```

## 🧪 Testing S3 Storage

### **1. Test Script**
```python
#!/usr/bin/env python3
"""Test S3 storage functionality"""

from s3_storage import create_s3_storage
from hybrid_agentic_analysis import run_hybrid_agentic_analysis

def test_s3_storage():
    # Initialize S3 storage
    storage = create_s3_storage()
    
    # Test data
    test_data = "User interview: I want a simple interface."
    
    # Run analysis
    result = run_hybrid_agentic_analysis(test_data)
    
    # Save to S3
    request_id = "test_s3_001"
    success = storage.save_analysis(request_id, result)
    print(f"Save success: {success}")
    
    # Load from S3
    loaded = storage.load_analysis(request_id)
    print(f"Load success: {loaded is not None}")
    
    # List analyses
    analyses = storage.list_analyses()
    print(f"Total analyses: {len(analyses)}")
    
    # Get stats
    stats = storage.get_storage_stats()
    print(f"Storage stats: {stats}")

if __name__ == "__main__":
    test_s3_storage()
```

### **2. Run Test**
```bash
python test_s3_storage.py
```

## 🚨 Troubleshooting

### **Common Issues**

#### **1. Credentials Error**
```
❌ Failed to initialize S3 client: NoCredentialsError
```
**Solution**: Configure AWS credentials
```bash
aws configure
# or
export AWS_ACCESS_KEY_ID="your_key"
export AWS_SECRET_ACCESS_KEY="your_secret"
```

#### **2. Bucket Already Exists**
```
❌ BucketAlreadyExists: The requested bucket name is not available
```
**Solution**: Use a unique bucket name
```bash
export S3_BUCKET_NAME="my-design-analysis-$(date +%s)"
```

#### **3. Permission Denied**
```
❌ AccessDenied: Access Denied
```
**Solution**: Check IAM permissions
```bash
aws s3 ls s3://your-bucket-name
```

#### **4. Region Mismatch**
```
❌ BucketAlreadyExists: The requested bucket name is not available in the selected region
```
**Solution**: Use correct region
```bash
export S3_REGION="us-west-2"  # or your preferred region
```

### **Debug Mode**
```bash
# Enable debug logging
export AWS_LOG_LEVEL=DEBUG
python api_s3.py
```

## 📚 Additional Resources

- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [S3 Cost Optimization](https://aws.amazon.com/s3/cost-optimization/)

## 🎯 Next Steps

1. **Set up AWS credentials**
2. **Configure environment variables**
3. **Test with small dataset**
4. **Monitor costs and performance**
5. **Set up monitoring and alerts**
6. **Implement backup strategies**

Your design analysis system is now ready for production with scalable, secure, and cost-effective S3 storage! 🚀
