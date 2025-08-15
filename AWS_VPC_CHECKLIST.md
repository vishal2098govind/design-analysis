# ✅ AWS VPC Deployment Checklist

**Production-Ready VPC with Strict IAM Permissions**

## 📋 Pre-Deployment Checklist

- [ ] **AWS Account** - You have an AWS account
- [ ] **OpenAI API Key** - You have your OpenAI API key ready
- [ ] **SSH Client** - You have an SSH client
- [ ] **Git Repository** - Your code is in a Git repository
- [ ] **Network Planning** - You understand VPC concepts

## 🏗️ VPC Infrastructure Setup

### **Step 1: Create VPC** ⏱️ 5 minutes
- [ ] Go to VPC Console
- [ ] Click "Create VPC"
- [ ] **VPC name**: `design-analysis-vpc`
- [ ] **IPv4 CIDR**: `10.0.0.0/16`
- [ ] **IPv6**: No IPv6 CIDR block
- [ ] Click "Create VPC"
- [ ] **Note VPC ID** for later use

### **Step 2: Create Subnets** ⏱️ 5 minutes
- [ ] **Public Subnet**:
  - [ ] Name: `design-analysis-public-subnet`
  - [ ] AZ: us-east-1a (or your preferred AZ)
  - [ ] CIDR: `10.0.1.0/24`
- [ ] **Private Subnet**:
  - [ ] Name: `design-analysis-private-subnet`
  - [ ] AZ: us-east-1b (different AZ)
  - [ ] CIDR: `10.0.2.0/24`

### **Step 3: Create Internet Gateway** ⏱️ 3 minutes
- [ ] Create IGW: `design-analysis-igw`
- [ ] Attach IGW to your VPC
- [ ] Verify attachment status

### **Step 4: Create Route Tables** ⏱️ 5 minutes
- [ ] **Public Route Table**:
  - [ ] Name: `design-analysis-public-rt`
  - [ ] Add route: `0.0.0.0/0` → Internet Gateway
  - [ ] Associate with public subnet
- [ ] **Private Route Table**:
  - [ ] Name: `design-analysis-private-rt`
  - [ ] Associate with private subnet
  - [ ] No internet route (private only)

## 🔒 Security Configuration

### **Step 5: Create S3 Bucket** ⏱️ 3 minutes
- [ ] **Bucket name**: `design-analysis-yourname-2024-vpc`
- [ ] **Region**: Same as VPC
- [ ] **Block Public Access**: All enabled ✅
- [ ] **Default encryption**: Enable AES-256

### **Step 6: Create Strict IAM Policy** ⏱️ 5 minutes
- [ ] Go to IAM Console → Policies → Create policy
- [ ] Use JSON tab
- [ ] **Policy name**: `DesignAnalysisStrictPolicy`
- [ ] **Description**: `Strict permissions for Design Analysis API`
- [ ] **Permissions include**:
  - [ ] S3 access to specific bucket only
  - [ ] CloudWatch logs for specific log group
  - [ ] No admin or broad permissions

### **Step 7: Create IAM Role** ⏱️ 3 minutes
- [ ] **Role name**: `DesignAnalysisVPCRole`
- [ ] **Trusted entity**: EC2
- [ ] **Attach policy**: `DesignAnalysisStrictPolicy`
- [ ] **Description**: `Strict role for Design Analysis API in VPC`

### **Step 8: Create Security Groups** ⏱️ 5 minutes
- [ ] **Application Security Group**:
  - [ ] Name: `design-analysis-app-sg`
  - [ ] VPC: Your VPC
  - [ ] **Inbound rules**:
    - [ ] SSH (22) - Source: My IP
    - [ ] HTTP (80) - Source: 0.0.0.0/0
    - [ ] HTTPS (443) - Source: 0.0.0.0/0
- [ ] **Database Security Group** (future use):
  - [ ] Name: `design-analysis-db-sg`
  - [ ] VPC: Your VPC
  - [ ] No inbound rules (private only)

## 🚀 Instance Deployment

### **Step 9: Launch EC2 Instance** ⏱️ 10 minutes
- [ ] **AMI**: Amazon Linux 2023
- [ ] **Instance type**: t3.micro (free tier)
- [ ] **Network**: Your VPC
- [ ] **Subnet**: Public subnet
- [ ] **IAM role**: `DesignAnalysisVPCRole`
- [ ] **Security group**: `design-analysis-app-sg`
- [ ] **Storage**: 20 GB gp3
- [ ] **Key pair**: Create and download

### **Step 10: Connect and Deploy** ⏱️ 20 minutes
- [ ] **SSH Connection**:
  - [ ] Connect to instance: `ssh -i key.pem ec2-user@IP`
  - [ ] Update system: `sudo yum update -y`
- [ ] **Install Dependencies**:
  - [ ] Python 3.11 and development tools
  - [ ] Git and nginx
- [ ] **Deploy Application**:
  - [ ] Clone repository
  - [ ] Create virtual environment
  - [ ] Install Python dependencies
  - [ ] Create .env file with S3 bucket name
- [ ] **Create Service**:
  - [ ] Systemd service file
  - [ ] Enable and start service
- [ ] **Configure Nginx**:
  - [ ] Nginx configuration
  - [ ] Enable and start nginx
  - [ ] Configure firewall

## 🎉 Testing Checklist

### **Network Connectivity**
- [ ] **Internet Access**: Instance can reach internet
- [ ] **SSH Access**: Can connect via SSH
- [ ] **HTTP Access**: Can access web interface

### **Application Testing**
- [ ] **Health Check**: `http://YOUR_IP/health`
- [ ] **API Documentation**: `http://YOUR_IP/docs`
- [ ] **Test Analysis**: Send test request
- [ ] **S3 Integration**: Verify data storage

### **Security Verification**
- [ ] **IAM Permissions**: Only necessary access
- [ ] **Network Isolation**: VPC boundaries respected
- [ ] **Encryption**: S3 bucket encrypted
- [ ] **Access Control**: Security groups working

## 🔧 VPC-Specific Troubleshooting

### **Network Issues**
- [ ] **Route Table**: Verify internet route exists
- [ ] **Security Groups**: Check inbound rules
- [ ] **Internet Gateway**: Verify attachment
- [ ] **Subnet Association**: Correct route table

### **IAM Issues**
- [ ] **Role Attachment**: Verify role is attached to instance
- [ ] **Policy Permissions**: Check specific bucket access
- [ ] **CloudWatch Logs**: Verify log group permissions
- [ ] **No Broad Access**: Confirm no admin permissions

### **S3 Access Issues**
- [ ] **Bucket Name**: Correct in .env file
- [ ] **Region**: Same as VPC
- [ ] **Permissions**: Test from instance
- [ ] **Encryption**: Verify encryption enabled

## 🔒 Security Verification

### **Network Security**
- [ ] ✅ **VPC Isolation**: Resources in private network
- [ ] ✅ **Public/Private Subnets**: Proper network tiers
- [ ] ✅ **Controlled Internet Access**: Only public subnet
- [ ] ✅ **Security Groups**: Specific port restrictions

### **IAM Security**
- [ ] ✅ **Principle of Least Privilege**: Minimal permissions
- [ ] ✅ **Resource-Specific Access**: Only your S3 bucket
- [ ] ✅ **No Admin Access**: No broad permissions
- [ ] ✅ **Audit Trail**: All actions logged

### **Data Security**
- [ ] ✅ **Encrypted Storage**: S3 bucket encryption
- [ ] ✅ **Private Bucket**: No public access
- [ ] ✅ **Versioning Ready**: Can enable for protection
- [ ] ✅ **Access Logging**: S3 access logs enabled

## 💰 Cost Management

### **VPC Costs**
- [ ] **VPC**: Free (no additional charges)
- [ ] **Internet Gateway**: Free (no additional charges)
- [ ] **Route Tables**: Free (no additional charges)
- [ ] **Security Groups**: Free (no additional charges)

### **Resource Costs**
- [ ] **EC2**: t3.micro (free tier eligible)
- [ ] **S3**: Pay per use (~$0.50/month for 1,000 analyses)
- [ ] **Data Transfer**: Free tier 15 GB/month

## 🗑️ Cleanup Checklist

### **To Avoid Charges**
- [ ] **Terminate EC2 Instance**
- [ ] **Delete S3 Bucket**
- [ ] **Delete IAM Role and Policy**
- [ ] **Delete Security Groups**
- [ ] **Delete Route Tables**
- [ ] **Detach and Delete Internet Gateway**
- [ ] **Delete Subnets**
- [ ] **Delete VPC**

## 🎯 Success Criteria

### **You're Done When:**
- [ ] ✅ VPC infrastructure is created and configured
- [ ] ✅ EC2 instance is running in VPC
- [ ] ✅ IAM role has strict, minimal permissions
- [ ] ✅ S3 bucket is encrypted and private
- [ ] ✅ Application is accessible via HTTP
- [ ] ✅ Health check returns healthy status
- [ ] ✅ Analysis requests work and store in S3

### **Your VPC Architecture:**
```
Internet → Internet Gateway → Public Subnet → EC2 Instance
                                    ↓
                              Private Subnet (future DB)
```

### **Your API is Live At:**
```
http://YOUR_INSTANCE_IP
```

### **Security Features:**
- ✅ **Network Isolation**: VPC environment
- ✅ **Strict IAM**: Minimal required permissions
- ✅ **Encrypted Storage**: S3 encryption
- ✅ **Controlled Access**: Security groups

---

## 🎉 Congratulations!

You've successfully deployed your Design Analysis system in a **secure VPC environment** with **strict IAM permissions**!

**Production-Ready Features:**
- ✅ **Enterprise Security**: VPC isolation and strict IAM
- ✅ **Scalable Architecture**: Multi-tier network design
- ✅ **Compliance Ready**: Audit-friendly configuration
- ✅ **Future-Proof**: Ready for database and load balancer

**Total Time**: ~1.5 hours
**Cost**: Free tier eligible (first 12 months)
**Security Level**: Enterprise-grade

Your system is now production-ready with maximum security! 🚀
