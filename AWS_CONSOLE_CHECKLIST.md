# ✅ AWS Console Deployment Checklist

**Simple step-by-step checklist for AWS beginners**

## 📋 Pre-Deployment Checklist

- [ ] **AWS Account** - You have an AWS account
- [ ] **OpenAI API Key** - You have your OpenAI API key ready
- [ ] **SSH Client** - You have an SSH client (Terminal on Mac/Linux, PuTTY on Windows)
- [ ] **Git Repository** - Your code is in a Git repository (GitHub, GitLab, etc.)

## 🚀 Deployment Steps

### **Step 1: Create S3 Bucket** ⏱️ 5 minutes
- [ ] Go to AWS Console → S3
- [ ] Click "Create bucket"
- [ ] **Bucket name**: `design-analysis-yourname-2024`
- [ ] **Region**: Choose closest to you
- [ ] **Block Public Access**: Keep all enabled ✅
- [ ] Click "Create bucket"
- [ ] Go to bucket → Properties → Default encryption → Enable

### **Step 2: Create IAM Role** ⏱️ 3 minutes
- [ ] Go to AWS Console → IAM
- [ ] Click "Roles" → "Create role"
- [ ] **Trusted entity**: AWS service
- [ ] **Service**: EC2
- [ ] **Permissions**: Search for "AmazonS3FullAccess" ✅
- [ ] **Role name**: `DesignAnalysisS3Role`
- [ ] Click "Create role"

### **Step 3: Create Security Group** ⏱️ 3 minutes
- [ ] Go to AWS Console → EC2 → Security Groups
- [ ] Click "Create security group"
- [ ] **Name**: `design-analysis-sg`
- [ ] **Add rules**:
  - [ ] SSH (port 22) - Source: My IP
  - [ ] HTTP (port 80) - Source: 0.0.0.0/0
  - [ ] HTTPS (port 443) - Source: 0.0.0.0/0
- [ ] Click "Create security group"

### **Step 4: Launch EC2 Instance** ⏱️ 10 minutes
- [ ] Go to AWS Console → EC2 → Launch instances
- [ ] **AMI**: Amazon Linux 2023
- [ ] **Instance type**: t3.micro (free tier)
- [ ] **IAM instance profile**: Select `DesignAnalysisS3Role`
- [ ] **Storage**: 20 GB gp3
- [ ] **Security group**: Select `design-analysis-sg`
- [ ] **Key pair**: Create new key pair, download .pem file
- [ ] Click "Launch instances"

### **Step 5: Connect to Instance** ⏱️ 5 minutes
- [ ] Copy your instance's Public IP address
- [ ] Open Terminal/SSH client
- [ ] Connect: `ssh -i your-key.pem ec2-user@YOUR_INSTANCE_IP`
- [ ] Update system: `sudo yum update -y`

### **Step 6: Install Dependencies** ⏱️ 10 minutes
- [ ] Install Python: `sudo yum install -y python3.11 python3.11-pip python3.11-devel`
- [ ] Install tools: `sudo yum groupinstall -y "Development Tools"`
- [ ] Install nginx: `sudo yum install -y git nginx`
- [ ] Create app directory: `mkdir -p /opt/design-analysis && cd /opt/design-analysis`

### **Step 7: Deploy Application** ⏱️ 15 minutes
- [ ] Clone repository: `git clone https://github.com/yourusername/design-analysis.git .`
- [ ] Create virtual environment: `python3.11 -m venv venv`
- [ ] Activate environment: `source venv/bin/activate`
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Create .env file with your OpenAI API key and S3 bucket name

### **Step 8: Create Service** ⏱️ 5 minutes
- [ ] Create systemd service file (copy from guide)
- [ ] Enable service: `sudo systemctl enable design-analysis`
- [ ] Start service: `sudo systemctl start design-analysis`

### **Step 9: Configure Nginx** ⏱️ 5 minutes
- [ ] Create nginx config file (copy from guide)
- [ ] Enable nginx: `sudo systemctl enable nginx`
- [ ] Start nginx: `sudo systemctl start nginx`
- [ ] Configure firewall: `sudo firewall-cmd --permanent --add-service=http --add-service=https && sudo firewall-cmd --reload`

## 🎉 Testing Checklist

### **Test Your Deployment**
- [ ] **Health Check**: Visit `http://YOUR_INSTANCE_IP/health`
- [ ] **API Docs**: Visit `http://YOUR_INSTANCE_IP/docs`
- [ ] **Test Analysis**: Send a test request to your API
- [ ] **Check Logs**: `sudo journalctl -u design-analysis -f`

### **Expected Results**
- [ ] Health check returns: `{"status": "healthy", "storage_type": "s3"}`
- [ ] API documentation loads properly
- [ ] Analysis request returns results
- [ ] No errors in logs

## 🔧 Troubleshooting Checklist

### **If You Can't Connect via SSH**
- [ ] Check security group allows SSH (port 22)
- [ ] Verify you're using the correct key file
- [ ] Make sure instance is running
- [ ] Check your IP address hasn't changed

### **If Application Not Responding**
- [ ] Check service status: `sudo systemctl status design-analysis`
- [ ] Check nginx status: `sudo systemctl status nginx`
- [ ] Check logs: `sudo journalctl -u design-analysis -f`
- [ ] Verify firewall allows HTTP traffic

### **If S3 Access Issues**
- [ ] Check IAM role is attached to instance
- [ ] Test S3 access: `aws s3 ls s3://your-bucket-name`
- [ ] Verify bucket name in .env file
- [ ] Check IAM role permissions

## 💰 Cost Management Checklist

### **Free Tier (First 12 Months)**
- [ ] Using t3.micro instance (free tier eligible)
- [ ] S3 usage under 5 GB
- [ ] Data transfer under 15 GB/month

### **Cost Monitoring**
- [ ] Set up billing alerts in AWS Console
- [ ] Monitor costs in AWS Billing Dashboard
- [ ] Check EC2 usage in CloudWatch

## 🔒 Security Checklist

### **What's Already Secure**
- [ ] ✅ S3 bucket is private (no public access)
- [ ] ✅ IAM role used (no hardcoded credentials)
- [ ] ✅ Security group restricts access
- [ ] ✅ Storage is encrypted

### **Additional Security (Optional)**
- [ ] Restrict SSH access to your IP only
- [ ] Add SSL certificate for HTTPS
- [ ] Set up CloudWatch monitoring
- [ ] Configure backup strategy

## 🗑️ Cleanup Checklist (When Done)

### **To Avoid Charges**
- [ ] Terminate EC2 instance
- [ ] Delete S3 bucket
- [ ] Delete IAM role
- [ ] Delete security group
- [ ] Delete key pair

## 📞 Getting Help

### **If You Get Stuck**
- [ ] Check AWS Console error messages
- [ ] Review the detailed guide: `AWS_CONSOLE_DEPLOYMENT.md`
- [ ] Check AWS documentation: https://docs.aws.amazon.com/
- [ ] Use AWS Support (if you have support plan)

## 🎯 Success Criteria

### **You're Done When:**
- [ ] ✅ You can access `http://YOUR_INSTANCE_IP/health`
- [ ] ✅ Health check returns healthy status
- [ ] ✅ You can view API documentation
- [ ] ✅ You can run an analysis successfully
- [ ] ✅ Results are stored in S3

### **Your API is Live At:**
```
http://YOUR_INSTANCE_IP
```

### **API Documentation:**
```
http://YOUR_INSTANCE_IP/docs
```

---

## 🎉 Congratulations!

If you've completed all the checkboxes above, you've successfully deployed your Design Analysis system on AWS using only the web console!

**Total Time**: ~1 hour
**Cost**: Free tier eligible (first 12 months)
**Difficulty**: Beginner-friendly

Happy analyzing! 🚀
