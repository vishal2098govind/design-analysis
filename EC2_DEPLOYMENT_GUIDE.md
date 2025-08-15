# AWS EC2 Deployment Guide

This guide shows you how to deploy the Design Analysis system on AWS EC2 with S3 storage for production use.

## 🎯 Deployment Overview

### **Architecture:**
```
Internet → Load Balancer → EC2 Instance → Design Analysis API → S3 Storage
```

### **Components:**
- **EC2 Instance**: Runs the FastAPI application
- **S3 Bucket**: Stores analysis results
- **IAM Role**: Provides secure access to S3
- **Security Groups**: Controls network access
- **Load Balancer** (Optional): For high availability

## 🚀 Quick Deployment

### **1. Launch EC2 Instance**

#### **Using AWS Console:**

1. **Go to EC2 Dashboard** → **Launch Instance**
2. **Choose AMI**: `Amazon Linux 2023` (recommended)
3. **Instance Type**: `t3.medium` (2 vCPU, 4 GB RAM)
4. **Key Pair**: Create or select existing key pair
5. **Network Settings**: 
   - VPC: Default VPC
   - Security Group: Create new (see below)
6. **Storage**: 20 GB gp3 (default)
7. **Advanced Details**: Add IAM role (see below)

#### **Using AWS CLI:**

```bash
# Create security group
aws ec2 create-security-group \
  --group-name design-analysis-sg \
  --description "Security group for Design Analysis API"

# Add rules
aws ec2 authorize-security-group-ingress \
  --group-name design-analysis-sg \
  --protocol tcp \
  --port 22 \
  --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-name design-analysis-sg \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-name design-analysis-sg \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-name design-analysis-sg \
  --protocol tcp \
  --port 8000 \
  --cidr 0.0.0.0/0

# Launch instance
aws ec2 run-instances \
  --image-id ami-0c02fb55956c7d316 \
  --count 1 \
  --instance-type t3.medium \
  --key-name your-key-pair \
  --security-group-ids sg-xxxxxxxxx \
  --iam-instance-profile Name=DesignAnalysisS3Role \
  --user-data file://user-data.sh
```

### **2. Create IAM Role**

#### **IAM Policy for S3 Access:**

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
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
```

#### **Create Role:**

```bash
# Create policy
aws iam create-policy \
  --policy-name DesignAnalysisS3Policy \
  --policy-document file://s3-policy.json

# Create role
aws iam create-role \
  --role-name DesignAnalysisS3Role \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Principal": {
          "Service": "ec2.amazonaws.com"
        },
        "Action": "sts:AssumeRole"
      }
    ]
  }'

# Attach policy to role
aws iam attach-role-policy \
  --role-name DesignAnalysisS3Role \
  --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/DesignAnalysisS3Policy

# Create instance profile
aws iam create-instance-profile \
  --instance-profile-name DesignAnalysisS3Role

# Add role to instance profile
aws iam add-role-to-instance-profile \
  --instance-profile-name DesignAnalysisS3Role \
  --role-name DesignAnalysisS3Role
```

### **3. User Data Script**

Create `user-data.sh` for automatic setup:

```bash
#!/bin/bash
# User data script for EC2 instance setup

# Update system
yum update -y

# Install Python 3.11 and pip
yum install -y python3.11 python3.11-pip python3.11-devel

# Install development tools
yum groupinstall -y "Development Tools"
yum install -y git

# Create application directory
mkdir -p /opt/design-analysis
cd /opt/design-analysis

# Clone your repository (replace with your repo URL)
git clone https://github.com/yourusername/design-analysis.git .

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create environment file
cat > .env << EOF
OPENAI_API_KEY=your_openai_api_key_here
STORAGE_TYPE=s3
S3_BUCKET_NAME=design-analysis-production
S3_REGION=us-east-1
S3_PREFIX=design-analysis
EOF

# Create systemd service
cat > /etc/systemd/system/design-analysis.service << EOF
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

# Enable and start service
systemctl enable design-analysis
systemctl start design-analysis

# Install and configure nginx
yum install -y nginx

# Configure nginx
cat > /etc/nginx/conf.d/design-analysis.conf << EOF
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

# Start nginx
systemctl enable nginx
systemctl start nginx

# Configure firewall
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --reload
```

## 🔧 Manual Deployment

### **1. Connect to EC2 Instance**

```bash
# SSH to your instance
ssh -i your-key.pair ec2-user@your-instance-public-ip
```

### **2. Install Dependencies**

```bash
# Update system
sudo yum update -y

# Install Python 3.11
sudo yum install -y python3.11 python3.11-pip python3.11-devel

# Install development tools
sudo yum groupinstall -y "Development Tools"
sudo yum install -y git nginx
```

### **3. Deploy Application**

```bash
# Create application directory
mkdir -p /opt/design-analysis
cd /opt/design-analysis

# Clone your repository
git clone https://github.com/yourusername/design-analysis.git .

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### **4. Configure Environment**

```bash
# Create environment file
cat > .env << EOF
OPENAI_API_KEY=your_openai_api_key_here
STORAGE_TYPE=s3
S3_BUCKET_NAME=design-analysis-production
S3_REGION=us-east-1
S3_PREFIX=design-analysis
EOF
```

### **5. Create Systemd Service**

```bash
# Create service file
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

# Enable and start service
sudo systemctl enable design-analysis
sudo systemctl start design-analysis

# Check status
sudo systemctl status design-analysis
```

### **6. Configure Nginx**

```bash
# Create nginx configuration
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

# Start nginx
sudo systemctl enable nginx
sudo systemctl start nginx
```

### **7. Configure Firewall**

```bash
# Configure firewall
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

## 🔒 Security Configuration

### **1. Security Groups**

Create security group with these rules:

| Type | Protocol | Port | Source | Description |
|------|----------|------|--------|-------------|
| SSH | TCP | 22 | Your IP | SSH access |
| HTTP | TCP | 80 | 0.0.0.0/0 | HTTP access |
| HTTPS | TCP | 443 | 0.0.0.0/0 | HTTPS access |
| Custom | TCP | 8000 | 0.0.0.0/0 | API direct access |

### **2. IAM Best Practices**

- **Use IAM roles** instead of access keys
- **Principle of least privilege** for S3 access
- **Enable CloudTrail** for audit logging
- **Use VPC endpoints** for private S3 access

### **3. SSL/TLS Configuration**

```bash
# Install certbot
sudo yum install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 Monitoring & Logging

### **1. CloudWatch Logs**

```bash
# Install CloudWatch agent
sudo yum install -y amazon-cloudwatch-agent

# Configure CloudWatch
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-config-wizard

# Start CloudWatch agent
sudo systemctl enable amazon-cloudwatch-agent
sudo systemctl start amazon-cloudwatch-agent
```

### **2. Application Logging**

Update the service file to include logging:

```ini
[Service]
Type=simple
User=ec2-user
WorkingDirectory=/opt/design-analysis
Environment=PATH=/opt/design-analysis/venv/bin
ExecStart=/opt/design-analysis/venv/bin/python api_s3.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
```

### **3. Health Checks**

```bash
# Create health check script
cat > /opt/design-analysis/health-check.sh << 'EOF'
#!/bin/bash
curl -f http://localhost:8000/health || exit 1
EOF

chmod +x /opt/design-analysis/health-check.sh

# Add to crontab
echo "*/5 * * * * /opt/design-analysis/health-check.sh" | crontab -
```

## 🔄 Deployment Automation

### **1. Using AWS Systems Manager**

```bash
# Create deployment document
aws ssm create-document \
  --name "DesignAnalysisDeployment" \
  --content file://deployment-document.json \
  --document-type "Command"
```

### **2. Using AWS CodeDeploy**

Create `appspec.yml`:

```yaml
version: 0.0
os: linux
files:
  - source: /
    destination: /opt/design-analysis/
hooks:
  BeforeInstall:
    - location: scripts/before_install.sh
      timeout: 300
      runas: root
  AfterInstall:
    - location: scripts/after_install.sh
      timeout: 300
      runas: root
  ApplicationStart:
    - location: scripts/start_application.sh
      timeout: 300
      runas: root
```

### **3. Using Terraform**

```hcl
# main.tf
provider "aws" {
  region = "us-east-1"
}

resource "aws_instance" "design_analysis" {
  ami           = "ami-0c02fb55956c7d316"
  instance_type = "t3.medium"
  
  iam_instance_profile = aws_iam_instance_profile.design_analysis.name
  
  vpc_security_group_ids = [aws_security_group.design_analysis.id]
  
  user_data = file("user-data.sh")
  
  tags = {
    Name = "Design Analysis API"
  }
}

resource "aws_security_group" "design_analysis" {
  name        = "design-analysis-sg"
  description = "Security group for Design Analysis API"
  
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_iam_role" "design_analysis" {
  name = "DesignAnalysisS3Role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_instance_profile" "design_analysis" {
  name = "DesignAnalysisS3Role"
  role = aws_iam_role.design_analysis.name
}

resource "aws_iam_role_policy" "design_analysis_s3" {
  name = "DesignAnalysisS3Policy"
  role = aws_iam_role.design_analysis.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:CreateBucket",
          "s3:PutObject",
          "s3:GetObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::design-analysis-*",
          "arn:aws:s3:::design-analysis-*/*"
        ]
      }
    ]
  })
}
```

## 🚀 High Availability Setup

### **1. Load Balancer Configuration**

```bash
# Create Application Load Balancer
aws elbv2 create-load-balancer \
  --name design-analysis-alb \
  --subnets subnet-xxxxxxxxx subnet-yyyyyyyyy \
  --security-groups sg-xxxxxxxxx

# Create target group
aws elbv2 create-target-group \
  --name design-analysis-tg \
  --protocol HTTP \
  --port 80 \
  --vpc-id vpc-xxxxxxxxx \
  --health-check-path /health \
  --health-check-interval-seconds 30

# Register targets
aws elbv2 register-targets \
  --target-group-arn arn:aws:elasticloadbalancing:region:account:targetgroup/design-analysis-tg/xxxxxxxxx \
  --targets Id=i-xxxxxxxxx
```

### **2. Auto Scaling Group**

```bash
# Create launch template
aws ec2 create-launch-template \
  --launch-template-name design-analysis-lt \
  --version-description v1 \
  --launch-template-data file://launch-template-data.json

# Create auto scaling group
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name design-analysis-asg \
  --launch-template LaunchTemplateName=design-analysis-lt,Version=\$Latest \
  --min-size 2 \
  --max-size 10 \
  --desired-capacity 2 \
  --vpc-zone-identifier subnet-xxxxxxxxx,subnet-yyyyyyyyy \
  --target-group-arns arn:aws:elasticloadbalancing:region:account:targetgroup/design-analysis-tg/xxxxxxxxx
```

## 🔍 Troubleshooting

### **1. Common Issues**

#### **Service Not Starting**
```bash
# Check service status
sudo systemctl status design-analysis

# Check logs
sudo journalctl -u design-analysis -f

# Check environment
cd /opt/design-analysis
source venv/bin/activate
python api_s3.py
```

#### **S3 Access Issues**
```bash
# Test S3 access
aws s3 ls s3://your-bucket-name

# Check IAM role
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/

# Test with boto3
python3 -c "
import boto3
s3 = boto3.client('s3')
print(s3.list_buckets())
"
```

#### **Port Issues**
```bash
# Check if port is listening
sudo netstat -tlnp | grep 8000

# Check firewall
sudo firewall-cmd --list-all

# Check nginx
sudo nginx -t
sudo systemctl status nginx
```

### **2. Performance Optimization**

```bash
# Increase file descriptors
echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf

# Optimize nginx
sudo tee /etc/nginx/conf.d/design-analysis.conf > /dev/null << EOF
upstream design_analysis {
    server 127.0.0.1:8000;
    keepalive 32;
}

server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://design_analysis;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
    }
}
EOF
```

## 📈 Cost Optimization

### **1. Instance Types**

| Use Case | Instance Type | vCPU | RAM | Cost/Hour |
|----------|---------------|------|-----|-----------|
| Development | t3.micro | 2 | 1 GB | ~$0.01 |
| Small Production | t3.small | 2 | 2 GB | ~$0.02 |
| Medium Production | t3.medium | 2 | 4 GB | ~$0.04 |
| Large Production | t3.large | 2 | 8 GB | ~$0.08 |

### **2. Reserved Instances**

```bash
# Purchase reserved instance
aws ec2 describe-reserved-instances-offerings \
  --instance-type t3.medium \
  --offering-type All Upfront \
  --product-description "Linux/UNIX"
```

### **3. Spot Instances** (for non-critical workloads)

```bash
# Request spot instance
aws ec2 request-spot-instances \
  --spot-price "0.02" \
  --instance-count 1 \
  --type "one-time" \
  --launch-specification file://spot-specification.json
```

## 🎯 Next Steps

1. **Set up monitoring** with CloudWatch
2. **Configure backups** for S3 data
3. **Set up CI/CD** pipeline
4. **Implement auto-scaling** based on load
5. **Add SSL certificate** for HTTPS
6. **Set up domain name** and DNS
7. **Configure alerts** for system health

Your Design Analysis system is now deployed on AWS EC2 with production-ready S3 storage! 🚀
