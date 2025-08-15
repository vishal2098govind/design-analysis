# 🚀 Simple AWS Console Deployment Guide

**No Terraform, No Command Line - Just AWS Console!**

This guide shows you how to deploy the Design Analysis system using only the AWS web interface. Perfect for AWS beginners!

## 🎯 What We'll Deploy

- **EC2 Instance** - Runs your application
- **S3 Bucket** - Stores analysis results
- **IAM Role** - Gives EC2 access to S3
- **Security Group** - Controls network access

## 📋 Prerequisites

### **What You Need:**
- ✅ AWS Account
- ✅ OpenAI API Key
- ✅ Basic understanding of AWS Console

### **What You DON'T Need:**
- ❌ Terraform
- ❌ Command line tools
- ❌ AWS CLI
- ❌ Programming knowledge

## 🚀 Step-by-Step Deployment

### **Step 1: Create S3 Bucket**

1. **Go to S3 Console**
   - Open AWS Console
   - Search for "S3" and click on it

2. **Create Bucket**
   - Click "Create bucket"
   - **Bucket name**: `design-analysis-yourname-2024` (replace with your name)
   - **Region**: Choose closest to you (e.g., US East 1)
   - **Block Public Access**: Keep all blocks enabled ✅
   - Click "Create bucket"

3. **Configure Bucket**
   - Click on your new bucket
   - Go to "Properties" tab
   - Scroll down to "Default encryption"
   - Click "Edit" → "Enable" → "Save changes"

### **Step 2: Create IAM Role**

1. **Go to IAM Console**
   - Search for "IAM" in AWS Console
   - Click on "IAM"

2. **Create Role**
   - Click "Roles" → "Create role"
   - **Trusted entity**: "AWS service"
   - **Service**: "EC2"
   - Click "Next"

3. **Add Permissions**
   - Search for "AmazonS3FullAccess"
   - Check the box next to it
   - Click "Next"

4. **Name the Role**
   - **Role name**: `DesignAnalysisS3Role`
   - **Description**: `Role for Design Analysis API to access S3`
   - Click "Create role"

### **Step 3: Create Security Group**

1. **Go to EC2 Console**
   - Search for "EC2" in AWS Console
   - Click on "EC2"

2. **Create Security Group**
   - Click "Security Groups" → "Create security group"
   - **Name**: `design-analysis-sg`
   - **Description**: `Security group for Design Analysis API`

3. **Add Inbound Rules**
   - Click "Add rule"
   - **Type**: SSH
   - **Source**: My IP (or 0.0.0.0/0 for anywhere)
   - Click "Add rule" again
   - **Type**: HTTP
   - **Source**: 0.0.0.0/0
   - Click "Add rule" again
   - **Type**: HTTPS
   - **Source**: 0.0.0.0/0
   - Click "Create security group"

### **Step 4: Launch EC2 Instance**

1. **Launch Instance**
   - In EC2 Console, click "Launch instances"

2. **Choose AMI**
   - **Name**: `Amazon Linux 2023`
   - **Architecture**: x86
   - Click "Select"

3. **Choose Instance Type**
   - **Instance type**: `t3.micro` (free tier) or `t3.small`
   - Click "Next: Configure Instance Details"

4. **Configure Instance**
   - **Number of instances**: 1
   - **IAM instance profile**: Select `DesignAnalysisS3Role`
   - Click "Next: Add Storage"

5. **Add Storage**
   - **Size**: 20 GB
   - **Volume type**: gp3
   - Click "Next: Add Tags"

6. **Add Tags**
   - Click "Add tag"
   - **Key**: Name
   - **Value**: Design Analysis API
   - Click "Next: Configure Security Group"

7. **Configure Security Group**
   - **Select existing security group**
   - Choose `design-analysis-sg`
   - Click "Review and Launch"

8. **Review and Launch**
   - Review settings
   - Click "Launch"

9. **Create Key Pair**
   - **Key pair name**: `design-analysis-key`
   - Click "Download Key Pair" (save the .pem file)
   - Click "Launch instances"

### **Step 5: Connect to Your Instance**

1. **Get Instance IP**
   - In EC2 Console, click "Instances"
   - Find your instance and copy the "Public IPv4 address"

2. **Connect via SSH**
   - **Windows**: Use PuTTY or Windows Terminal
   - **Mac/Linux**: Use Terminal

   ```bash
   # Mac/Linux Terminal
   ssh -i design-analysis-key.pem ec2-user@YOUR_INSTANCE_IP
   ```

3. **Update System**
   ```bash
   sudo yum update -y
   ```

### **Step 6: Install Dependencies**

1. **Install Python and Tools**
   ```bash
   sudo yum install -y python3.11 python3.11-pip python3.11-devel
   sudo yum groupinstall -y "Development Tools"
   sudo yum install -y git nginx
   ```

2. **Create Application Directory**
   ```bash
   mkdir -p /opt/design-analysis
   cd /opt/design-analysis
   ```

### **Step 7: Deploy Your Application**

1. **Clone Your Repository**
   ```bash
   # Replace with your actual repository URL
   git clone https://github.com/yourusername/design-analysis.git .
   ```

2. **Create Virtual Environment**
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Create Environment File**
   ```bash
   
   cat > .env << EOF
   OPENAI_API_KEY=your_openai_api_key_here
   STORAGE_TYPE=s3
   S3_BUCKET_NAME=design-analysis-yourname-2024
   S3_REGION=us-east-1
   S3_PREFIX=design-analysis
   EOF
   ```

### **Step 8: Create System Service**

1. **Create Service File**
   ```bash
   sudo tee /etc/systemd/system/design-analysis.service > /dev/null << EOF
   [Unit]
   Description=Design Analysis API
   After=network.target

   [Service]
   Type=simple
   User=ec2-user
   WorkingDirectory=/opt/design-analysis
   Environment=PATH=/opt/design-analysis/venv/bin
   ExecStart=/opt/design-analysis/venv/bin/python api_s3.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   EOF
   ```

2. **Start Service**
   ```bash
   sudo systemctl enable design-analysis
   sudo systemctl start design-analysis
   ```

### **Step 9: Configure Nginx**

1. **Create Nginx Config**
   ```bash
   sudo tee /etc/nginx/conf.d/design-analysis.conf > /dev/null << EOF
   server {
       listen 80;
       server_name _;

       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host \$host;
           proxy_set_header X-Real-IP \$remote_addr;
           proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto \$scheme;
       }
   }
   EOF
   ```

2. **Start Nginx**
   ```bash
   sudo systemctl enable nginx
   sudo systemctl start nginx
   ```

### **Step 10: Configure Firewall**

```bash
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

## 🎉 Test Your Deployment

### **1. Health Check**
Open your browser and go to:
```
http://YOUR_INSTANCE_IP/health
```

You should see:
```json
{
  "status": "healthy",
  "storage_type": "s3",
  "openai_key_configured": true
}
```

### **2. API Documentation**
Visit:
```
http://YOUR_INSTANCE_IP/docs
```

### **3. Test Analysis**
Use the API to analyze some data:
```bash
curl -X POST "http://YOUR_INSTANCE_IP/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "research_data": "User interview: I want a simple interface.",
    "implementation": "hybrid"
  }'
```

## 🔧 Troubleshooting

### **Common Issues:**

#### **1. Can't Connect via SSH**
- Check security group allows SSH (port 22)
- Make sure you're using the correct key file
- Verify the instance is running

#### **2. Application Not Responding**
```bash
# Check service status
sudo systemctl status design-analysis

# Check logs
sudo journalctl -u design-analysis -f

# Check nginx
sudo systemctl status nginx
```

#### **3. S3 Access Issues**
```bash
# Test S3 access
aws s3 ls s3://your-bucket-name

# Check IAM role
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/
```

## 💰 Cost Management

### **Free Tier (First 12 Months):**
- **EC2**: 750 hours/month of t3.micro
- **S3**: 5 GB storage
- **Data Transfer**: 15 GB/month

### **After Free Tier:**
- **t3.micro**: ~$7.30/month
- **S3**: ~$0.50/month for 1,000 analyses
- **Total**: ~$8-10/month

## 🔒 Security Best Practices

### **What We've Done:**
- ✅ **Private S3 bucket** - No public access
- ✅ **IAM role** - No hardcoded credentials
- ✅ **Security group** - Only necessary ports open
- ✅ **Encrypted storage** - Data encrypted at rest

### **Additional Security:**
1. **Restrict SSH access** to your IP only
2. **Use HTTPS** (add SSL certificate)
3. **Regular updates** - Keep system updated
4. **Monitor costs** - Set up billing alerts

## 📊 Monitoring

### **Check Your Application:**
- **Health**: `http://YOUR_INSTANCE_IP/health`
- **Stats**: `http://YOUR_INSTANCE_IP/stats`
- **Storage**: `http://YOUR_INSTANCE_IP/storage/info`

### **AWS Console Monitoring:**
- **EC2 Console** → Your instance → "Monitoring" tab
- **CloudWatch** → Logs (if configured)
- **S3 Console** → Your bucket → "Metrics" tab

## 🗑️ Cleanup (When Done)

### **To Avoid Charges:**
1. **Terminate EC2 Instance**
   - EC2 Console → Instances → Select instance → "Instance state" → "Terminate instance"

2. **Delete S3 Bucket**
   - S3 Console → Your bucket → "Delete bucket"

3. **Delete IAM Role**
   - IAM Console → Roles → Select role → "Delete role"

4. **Delete Security Group**
   - EC2 Console → Security Groups → Select group → "Delete security group"

## 🎯 Next Steps

### **Immediate:**
1. ✅ **Test your API** with sample data
2. ✅ **Bookmark your API URL**
3. ✅ **Set up billing alerts**

### **Future Enhancements:**
1. **Add domain name** and SSL certificate
2. **Set up monitoring** with CloudWatch
3. **Configure backups** for S3 data
4. **Add authentication** to your API

## 🆘 Getting Help

### **AWS Support:**
- **AWS Documentation**: https://docs.aws.amazon.com/
- **AWS Support Center**: https://console.aws.amazon.com/support/
- **AWS Forums**: https://forums.aws.amazon.com/

### **Your Application:**
- **API Documentation**: `http://YOUR_INSTANCE_IP/docs`
- **Health Check**: `http://YOUR_INSTANCE_IP/health`
- **Logs**: `sudo journalctl -u design-analysis -f`

---

## 🎉 Congratulations!

You've successfully deployed your Design Analysis system on AWS using only the web console! 

**Your API is now live at:**
```
http://YOUR_INSTANCE_IP
```

**API Documentation:**
```
http://YOUR_INSTANCE_IP/docs
```

**Health Check:**
```
http://YOUR_INSTANCE_IP/health
```

You now have a production-ready system with:
- ✅ **Scalable S3 storage**
- ✅ **Secure EC2 deployment**
- ✅ **Professional monitoring**
- ✅ **Cost-effective infrastructure**

Happy analyzing! 🚀
