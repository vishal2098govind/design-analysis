# 🏗️ AWS VPC Deployment Guide

**Production-Ready Deployment with VPC and Strict IAM Permissions**

This guide shows you how to deploy the Design Analysis system within a VPC with minimal, specific IAM permissions for maximum security.

## 🎯 What We'll Deploy

- **Custom VPC** - Isolated network environment
- **Public Subnet** - For your EC2 instance
- **Private Subnet** - For future database expansion
- **Internet Gateway** - Internet access for public subnet
- **Route Tables** - Network routing
- **EC2 Instance** - Your application server
- **S3 Bucket** - Data storage
- **Strict IAM Role** - Minimal required permissions
- **Security Groups** - Network security

## 📋 Prerequisites

### **What You Need:**
- ✅ AWS Account
- ✅ OpenAI API Key
- ✅ Basic understanding of AWS Console

### **Security Benefits:**
- 🔒 **Network Isolation** - Your resources are in a private network
- 🔒 **Minimal Permissions** - IAM role only has what it needs
- 🔒 **Controlled Access** - Only specific ports and sources allowed
- 🔒 **Audit Trail** - All actions are logged

## 🚀 Step-by-Step VPC Deployment

### **Step 1: Create VPC**

1. **Go to VPC Console**
   - Open AWS Console
   - Search for "VPC" and click on it

2. **Create VPC**
   - Click "Create VPC"
   - **VPC name**: `design-analysis-vpc`
   - **IPv4 CIDR**: `10.0.0.0/16`
   - **IPv6 CIDR**: No IPv6 CIDR block
   - Click "Create VPC"

3. **Note VPC ID**
   - Copy the VPC ID (e.g., `vpc-12345678`)
   - You'll need this for later steps

### **Step 2: Create Subnets**

1. **Create Public Subnet**
   - In VPC Console, click "Subnets" → "Create subnet"
   - **VPC**: Select your `design-analysis-vpc`
   - **Subnet name**: `design-analysis-public-subnet`
   - **Availability Zone**: Choose any AZ (e.g., us-east-1a)
   - **IPv4 CIDR**: `10.0.1.0/24`
   - Click "Create subnet"

2. **Create Private Subnet**
   - Click "Create subnet" again
   - **VPC**: Select your `design-analysis-vpc`
   - **Subnet name**: `design-analysis-private-subnet`
   - **Availability Zone**: Choose different AZ (e.g., us-east-1b)
   - **IPv4 CIDR**: `10.0.2.0/24`
   - Click "Create subnet"

### **Step 3: Create Internet Gateway**

1. **Create IGW**
   - In VPC Console, click "Internet gateways" → "Create internet gateway"
   - **Name**: `design-analysis-igw`
   - Click "Create internet gateway"

2. **Attach to VPC**
   - Select your IGW
   - Click "Actions" → "Attach to VPC"
   - **VPC**: Select your `design-analysis-vpc`
   - Click "Attach internet gateway"

### **Step 4: Create Route Tables**

1. **Create Public Route Table**
   - In VPC Console, click "Route tables" → "Create route table"
   - **Name**: `design-analysis-public-rt`
   - **VPC**: Select your `design-analysis-vpc`
   - Click "Create route table"

2. **Add Internet Route**
   - Select your public route table
   - Click "Routes" tab → "Edit routes"
   - Click "Add route"
   - **Destination**: `0.0.0.0/0`
   - **Target**: Internet Gateway → Select your IGW
   - Click "Save changes"

3. **Associate Public Subnet**
   - Click "Subnet associations" tab → "Edit subnet associations"
   - Check your public subnet
   - Click "Save associations"

4. **Create Private Route Table**
   - Click "Create route table"
   - **Name**: `design-analysis-private-rt`
   - **VPC**: Select your `design-analysis-vpc`
   - Click "Create route table"

5. **Associate Private Subnet**
   - Select your private route table
   - Click "Subnet associations" tab → "Edit subnet associations"
   - Check your private subnet
   - Click "Save associations"

### **Step 5: Create S3 Bucket**

1. **Go to S3 Console**
   - Search for "S3" in AWS Console
   - Click on "S3"

2. **Create Bucket**
   - Click "Create bucket"
   - **Bucket name**: `design-analysis-yourname-2024-vpc`
   - **Region**: Same as your VPC
   - **Block Public Access**: Keep all blocks enabled ✅
   - Click "Create bucket"

3. **Configure Bucket**
   - Click on your bucket
   - Go to "Properties" tab
   - Scroll to "Default encryption"
   - Click "Edit" → "Enable" → "Save changes"

### **Step 6: Create Strict IAM Policy**

1. **Go to IAM Console**
   - Search for "IAM" in AWS Console
   - Click on "IAM"

2. **Create Policy**
   - Click "Policies" → "Create policy"
   - Click "JSON" tab
   - Replace content with this strict policy:

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
                "arn:aws:s3:::design-analysis-yourname-2024-vpc",
                "arn:aws:s3:::design-analysis-yourname-2024-vpc/*"
            ]
        },
        {
            "Sid": "DesignAnalysisS3BucketManagement",
            "Effect": "Allow",
            "Action": [
                "s3:PutBucketVersioning",
                "s3:PutBucketLifecycleConfiguration",
                "s3:PutBucketEncryption"
            ],
            "Resource": "arn:aws:s3:::design-analysis-yourname-2024-vpc"
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

3. **Name Policy**
   - **Policy name**: `DesignAnalysisStrictPolicy`
   - **Description**: `Strict permissions for Design Analysis API`
   - Click "Create policy"

### **Step 7: Create IAM Role**

1. **Create Role**
   - In IAM Console, click "Roles" → "Create role"
   - **Trusted entity**: "AWS service"
   - **Service**: "EC2"
   - Click "Next"

2. **Attach Policy**
   - Search for "DesignAnalysisStrictPolicy"
   - Check the box next to it
   - Click "Next"

3. **Name Role**
   - **Role name**: `DesignAnalysisVPCRole`
   - **Description**: `Strict role for Design Analysis API in VPC`
   - Click "Create role"

### **Step 8: Create Security Groups**

1. **Create Application Security Group**
   - Go to EC2 Console → Security Groups
   - Click "Create security group"
   - **Name**: `design-analysis-app-sg`
   - **Description**: `Security group for Design Analysis API`
   - **VPC**: Select your `design-analysis-vpc`

2. **Add Inbound Rules**
   - Click "Add rule"
   - **Type**: SSH
   - **Source**: My IP (or specific IP range)
   - Click "Add rule"
   - **Type**: HTTP
   - **Source**: 0.0.0.0/0
   - Click "Add rule"
   - **Type**: HTTPS
   - **Source**: 0.0.0.0/0
   - Click "Create security group"

3. **Create Database Security Group** (for future use)
   - Click "Create security group"
   - **Name**: `design-analysis-db-sg`
   - **Description**: `Security group for future database`
   - **VPC**: Select your `design-analysis-vpc`
   - **No inbound rules** (private access only)
   - Click "Create security group"

### **Step 9: Launch EC2 Instance in VPC**

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
   - **Network**: Select your `design-analysis-vpc`
   - **Subnet**: Select your public subnet
   - **IAM instance profile**: Select `DesignAnalysisVPCRole`
   - Click "Next: Add Storage"

5. **Add Storage**
   - **Size**: 20 GB
   - **Volume type**: gp3
   - Click "Next: Add Tags"

6. **Add Tags**
   - Click "Add tag"
   - **Key**: Name
   - **Value**: Design Analysis API VPC
   - Click "Next: Configure Security Group"

7. **Configure Security Group**
   - **Select existing security group**
   - Choose `design-analysis-app-sg`
   - Click "Review and Launch"

8. **Review and Launch**
   - Review settings
   - Click "Launch"

9. **Create Key Pair**
   - **Key pair name**: `design-analysis-vpc-key`
   - Click "Download Key Pair"
   - Click "Launch instances"

### **Step 10: Connect and Deploy**

1. **Get Instance IP**
   - In EC2 Console, find your instance
   - Copy the "Public IPv4 address"

2. **Connect via SSH**
   ```bash
   ssh -i design-analysis-vpc-key.pem ec2-user@YOUR_INSTANCE_IP
   ```

3. **Update System**
   ```bash
   sudo yum update -y
   ```

4. **Install Dependencies**
   ```bash
   sudo yum install -y python3.11 python3.11-pip python3.11-devel
   sudo yum groupinstall -y "Development Tools"
   sudo yum install -y git nginx
   ```

5. **Deploy Application**
   ```bash
   mkdir -p /opt/design-analysis
   cd /opt/design-analysis
   git clone https://github.com/yourusername/design-analysis.git .
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

6. **Create Environment File**
   ```bash
   cat > .env << EOF
   OPENAI_API_KEY=your_openai_api_key_here
   STORAGE_TYPE=s3
   S3_BUCKET_NAME=design-analysis-yourname-2024-vpc
   S3_REGION=us-east-1
   S3_PREFIX=design-analysis
   EOF
   ```

7. **Create Service**
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

   sudo systemctl enable design-analysis
   sudo systemctl start design-analysis
   ```

8. **Configure Nginx**
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

   sudo systemctl enable nginx
   sudo systemctl start nginx
   ```

9. **Configure Firewall**
   ```bash
   sudo firewall-cmd --permanent --add-service=http
   sudo firewall-cmd --permanent --add-service=https
   sudo firewall-cmd --reload
   ```

## 🔒 Security Features

### **Network Security:**
- ✅ **VPC Isolation** - Your resources are in a private network
- ✅ **Public/Private Subnets** - Separate network tiers
- ✅ **Controlled Internet Access** - Only public subnet has internet access
- ✅ **Security Groups** - Specific port and source restrictions

### **IAM Security:**
- ✅ **Principle of Least Privilege** - Only necessary permissions
- ✅ **Resource-Specific Access** - Only your specific S3 bucket
- ✅ **No Admin Access** - No broad permissions
- ✅ **Audit Trail** - All actions logged

### **Data Security:**
- ✅ **Encrypted Storage** - S3 bucket encryption enabled
- ✅ **Private Bucket** - No public access
- ✅ **Versioning Ready** - Can enable for data protection

## 🎉 Test Your VPC Deployment

### **1. Health Check**
```
http://YOUR_INSTANCE_IP/health
```

### **2. API Documentation**
```
http://YOUR_INSTANCE_IP/docs
```

### **3. Test Analysis**
```bash
curl -X POST "http://YOUR_INSTANCE_IP/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "research_data": "User interview: I want a simple interface.",
    "implementation": "hybrid"
  }'
```

## 🔧 VPC-Specific Troubleshooting

### **Network Issues:**
```bash
# Check if instance can reach internet
ping google.com

# Check route table
route -n

# Check security group rules
aws ec2 describe-security-groups --group-names design-analysis-app-sg
```

### **S3 Access Issues:**
```bash
# Test S3 access from instance
aws s3 ls s3://design-analysis-yourname-2024-vpc

# Check IAM role
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/
```

## 🗑️ Cleanup VPC Resources

### **To Avoid Charges:**
1. **Terminate EC2 Instance**
2. **Delete S3 Bucket**
3. **Delete IAM Role and Policy**
4. **Delete Security Groups**
5. **Delete Route Tables**
6. **Detach and Delete Internet Gateway**
7. **Delete Subnets**
8. **Delete VPC**

## 🎯 Benefits of VPC Deployment

### **Security:**
- 🔒 **Network Isolation** - Your resources are isolated
- 🔒 **Controlled Access** - Only specific traffic allowed
- 🔒 **Audit Trail** - All network activity logged

### **Scalability:**
- 📈 **Easy Expansion** - Add databases, load balancers
- 📈 **Multi-Tier Architecture** - Public/private subnets
- 📈 **Future-Proof** - Ready for production scaling

### **Compliance:**
- ✅ **Enterprise Ready** - Meets security standards
- ✅ **Audit Friendly** - Clear network boundaries
- ✅ **Best Practices** - Follows AWS recommendations

## 🚀 Next Steps

### **Immediate:**
1. ✅ **Test your VPC deployment**
2. ✅ **Verify security groups**
3. ✅ **Check IAM permissions**

### **Future Enhancements:**
1. **Add Database** - Deploy RDS in private subnet
2. **Load Balancer** - Add ALB for high availability
3. **Auto Scaling** - Scale based on demand
4. **VPN Access** - Secure remote access
5. **Monitoring** - CloudWatch integration

---

## 🎉 Congratulations!

You've successfully deployed your Design Analysis system in a **secure VPC environment** with **strict IAM permissions**!

**Your API is now live at:**
```
http://YOUR_INSTANCE_IP
```

**Security Features:**
- ✅ **VPC Network Isolation**
- ✅ **Strict IAM Permissions**
- ✅ **Encrypted Storage**
- ✅ **Controlled Access**

**Production-Ready Features:**
- ✅ **Multi-Tier Architecture**
- ✅ **Scalable Design**
- ✅ **Security Best Practices**
- ✅ **Audit Compliance**

Your system is now enterprise-ready with maximum security! 🚀
