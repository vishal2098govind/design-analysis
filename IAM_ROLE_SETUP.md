# 🔐 IAM Role Setup Guide

**Secure AWS Access Using IAM Roles (No Access Keys Required)**

This guide shows you how to set up IAM roles for your EC2 instances to access S3 without using explicit access keys. This is the **recommended and most secure approach** for production deployments.

## 🎯 Why Use IAM Roles?

### **Security Benefits:**
- 🔒 **No Access Keys** - No credentials to manage or rotate
- 🔒 **Automatic Rotation** - AWS automatically rotates temporary credentials
- 🔒 **Principle of Least Privilege** - Only necessary permissions
- 🔒 **No Hardcoded Secrets** - No credentials in code or environment files
- 🔒 **Audit Trail** - All access is logged and traceable

### **Operational Benefits:**
- 🚀 **Simpler Deployment** - No need to manage access keys
- 🚀 **Automatic Scaling** - New instances automatically get permissions
- 🚀 **Reduced Risk** - No risk of accidentally exposing credentials
- 🚀 **Compliance** - Meets security best practices

## 🚀 Step-by-Step IAM Role Setup

### **Step 1: Create IAM Policy**

1. **Go to IAM Console**
   - Open AWS Console
   - Search for "IAM" and click on it

2. **Create Policy**
   - Click "Policies" → "Create policy"
   - Click "JSON" tab
   - Replace content with this policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "DesignAnalysisS3Access",
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
            ]
        },
        {
            "Sid": "DesignAnalysisS3BucketManagement",
            "Effect": "Allow",
            "Action": [
                "s3:CreateBucket",
                "s3:PutBucketVersioning",
                "s3:PutBucketLifecycleConfiguration",
                "s3:PutBucketEncryption",
                "s3:GetBucketVersioning",
                "s3:GetBucketLifecycleConfiguration",
                "s3:GetBucketEncryption"
            ],
            "Resource": "arn:aws:s3:::design-analysis-*"
        },
        {
            "Sid": "DesignAnalysisCloudWatchLogs",
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
                "logs:DescribeLogGroups",
                "logs:DescribeLogStreams"
            ],
            "Resource": [
                "arn:aws:logs:*:*:log-group:/aws/design-analysis/*",
                "arn:aws:logs:*:*:log-group:/aws/design-analysis/*:log-stream:*"
            ]
        }
    ]
}
```

3. **Name the Policy**
   - **Policy name**: `DesignAnalysisS3Policy`
   - **Description**: `S3 access policy for Design Analysis system`
   - Click "Create policy"

### **Step 2: Create IAM Role**

1. **Create Role**
   - In IAM Console, click "Roles" → "Create role"
   - **Trusted entity**: "AWS service"
   - **Service**: "EC2"
   - Click "Next"

2. **Attach Policy**
   - Search for "DesignAnalysisS3Policy"
   - Check the box next to it
   - Click "Next"

3. **Name the Role**
   - **Role name**: `DesignAnalysisEC2Role`
   - **Description**: `IAM role for Design Analysis EC2 instances`
   - Click "Create role"

### **Step 3: Attach Role to EC2 Instance**

#### **For New EC2 Instance:**

1. **Launch Instance**
   - Go to EC2 Console → Launch instances
   - Follow normal setup steps

2. **Configure Instance**
   - In "Configure Instance" step
   - **IAM instance profile**: Select `DesignAnalysisEC2Role`
   - Continue with launch

#### **For Existing EC2 Instance:**

1. **Modify Instance**
   - EC2 Console → Instances
   - Select your instance
   - Actions → Security → Modify IAM role

2. **Attach Role**
   - **IAM role**: Select `DesignAnalysisEC2Role`
   - Click "Update IAM role"

## 🔧 Environment Configuration

### **For IAM Role Usage:**

When using IAM roles, your `.env` file should look like this:

```bash
# OpenAI Configuration (Required)
OPENAI_API_KEY=your_openai_api_key_here

# Storage Configuration
STORAGE_TYPE=s3
S3_BUCKET_NAME=design-analysis-yourname-2024
S3_REGION=us-east-1
S3_PREFIX=design-analysis

# AWS Configuration (IAM Role - No Access Keys Needed)
# Leave these empty - the system will use the IAM role automatically
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_SESSION_TOKEN=

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false
```

### **Key Points:**
- ✅ **No Access Keys** - Leave AWS credential fields empty
- ✅ **Automatic Detection** - System detects IAM role automatically
- ✅ **Secure** - No credentials to manage or expose

## 🧪 Testing IAM Role Access

### **Test from EC2 Instance:**

1. **Connect to your EC2 instance**
   ```bash
   ssh -i your-key.pem ec2-user@your-instance-ip
   ```

2. **Test S3 access**
   ```bash
   # Test if you can list S3 buckets
   aws s3 ls
   
   # Test if you can access your bucket
   aws s3 ls s3://design-analysis-yourname-2024
   ```

3. **Test with Python**
   ```python
   import boto3
   
   # This should work without any credentials
   s3 = boto3.client('s3')
   response = s3.list_buckets()
   print("Buckets:", [bucket['Name'] for bucket in response['Buckets']])
   ```

### **Test Your Application:**

1. **Start the API**
   ```bash
   python api_s3.py
   ```

2. **Check logs**
   - Look for: "No explicit credentials provided - using IAM role"
   - Look for: "S3 client initialized successfully"

3. **Test file upload**
   ```bash
   curl -X POST "http://localhost:8000/upload" \
     -F "file=@test.txt"
   ```

## 🔍 Troubleshooting

### **Common Issues:**

#### **1. "NoCredentialsError"**
```
AWS credentials not found. Please either:
1. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables, or
2. Configure AWS CLI with 'aws configure', or
3. Attach an IAM role to your EC2 instance with S3 permissions
```

**Solution:**
- Verify IAM role is attached to EC2 instance
- Check IAM role has correct permissions
- Ensure EC2 instance is in the correct region

#### **2. "AccessDenied"**
```
An error occurred (AccessDenied) when calling the ListBuckets operation
```

**Solution:**
- Check IAM policy permissions
- Verify bucket name matches policy resource pattern
- Ensure role is properly attached

#### **3. "NoSuchBucket"**
```
An error occurred (NoSuchBucket) when calling the HeadBucket operation
```

**Solution:**
- Check S3_BUCKET_NAME in environment
- Verify bucket exists in the specified region
- Ensure bucket name is correct

### **Debug Steps:**

1. **Check IAM Role Attachment**
   ```bash
   # Get instance metadata
   curl http://169.254.169.254/latest/meta-data/iam/security-credentials/
   ```

2. **Check IAM Role Permissions**
   ```bash
   # Test specific S3 operations
   aws s3 ls s3://your-bucket-name
   aws s3 cp test.txt s3://your-bucket-name/
   ```

3. **Check Application Logs**
   ```bash
   # Look for credential-related messages
   tail -f /var/log/your-app.log
   ```

## 🎯 Best Practices

### **Security:**
- ✅ **Use IAM Roles** - Always prefer IAM roles over access keys
- ✅ **Principle of Least Privilege** - Only grant necessary permissions
- ✅ **Regular Audits** - Review IAM policies regularly
- ✅ **Monitor Access** - Use CloudTrail to monitor S3 access

### **Deployment:**
- ✅ **Automate Role Creation** - Use CloudFormation or Terraform
- ✅ **Environment-Specific Roles** - Different roles for dev/staging/prod
- ✅ **Tag Resources** - Tag EC2 instances and IAM roles
- ✅ **Document Permissions** - Document what each role does

### **Monitoring:**
- ✅ **CloudWatch Logs** - Monitor application logs
- ✅ **CloudTrail** - Monitor API calls
- ✅ **S3 Access Logs** - Monitor S3 access patterns
- ✅ **IAM Access Analyzer** - Find unused permissions

## 🚀 Production Deployment

### **Recommended Setup:**

```bash
# Production .env file
OPENAI_API_KEY=your_production_openai_key
STORAGE_TYPE=s3
S3_BUCKET_NAME=design-analysis-production
S3_REGION=us-east-1
S3_PREFIX=design-analysis
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false

# No AWS credentials needed - uses IAM role
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_SESSION_TOKEN=
```

### **IAM Role for Production:**

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "DesignAnalysisS3Access",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::design-analysis-production",
                "arn:aws:s3:::design-analysis-production/*"
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

## 🎉 Benefits Summary

### **Security:**
- 🔒 **No Credential Management** - AWS handles credential rotation
- 🔒 **No Secret Exposure** - No access keys in code or config files
- 🔒 **Audit Trail** - All access is logged and traceable
- 🔒 **Compliance** - Meets security best practices

### **Operations:**
- 🚀 **Simpler Deployment** - No credential setup required
- 🚀 **Automatic Scaling** - New instances get permissions automatically
- 🚀 **Reduced Risk** - No risk of credential exposure
- 🚀 **Easier Management** - Centralized permission management

Your system now supports secure IAM role-based access to S3 without requiring any access keys! 🚀
