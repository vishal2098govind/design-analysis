# Terraform Deployment for Design Analysis API

This directory contains Terraform configuration to deploy the Design Analysis API on AWS EC2 with S3 storage.

## 🚀 Quick Start

### Prerequisites

1. **Terraform** (version >= 1.0)
2. **AWS CLI** configured with appropriate credentials
3. **EC2 Key Pair** created in AWS
4. **OpenAI API Key** for the application

### Deployment Steps

1. **Clone and navigate to the deployment directory:**
   ```bash
   cd deployment/terraform
   ```

2. **Copy and configure variables:**
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your values
   ```

3. **Initialize Terraform:**
   ```bash
   terraform init
   ```

4. **Plan the deployment:**
   ```bash
   terraform plan
   ```

5. **Apply the configuration:**
   ```bash
   terraform apply
   ```

6. **Verify deployment:**
   ```bash
   # Get the API URL
   terraform output api_url
   
   # Test health check
   curl $(terraform output -raw health_check_url)
   ```

## 📋 Configuration

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `key_pair_name` | EC2 key pair name | `my-key-pair` |
| `openai_api_key` | OpenAI API key | `sk-...` |
| `allowed_ssh_cidr` | SSH access CIDR | `["192.168.1.0/24"]` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `instance_type` | EC2 instance type | `t3.medium` |
| `aws_region` | AWS region | `us-east-1` |
| `environment` | Environment name | `prod` |
| `create_eip` | Create Elastic IP | `false` |

## 🏗️ Infrastructure Components

### Created Resources

- **EC2 Instance**: Runs the Design Analysis API
- **IAM Role**: Provides S3 access permissions
- **Security Group**: Controls network access
- **CloudWatch Log Group**: Application logging
- **Elastic IP** (optional): Static IP address

### Security Features

- **Encrypted EBS volumes**
- **IMDSv2** (Instance Metadata Service v2)
- **Restricted SSH access**
- **IAM roles** instead of access keys
- **Security group** with minimal required ports

## 🔧 Customization

### Instance Types

Choose the appropriate instance type based on your needs:

| Use Case | Instance Type | vCPU | RAM | Cost/Hour |
|----------|---------------|------|-----|-----------|
| Development | `t3.micro` | 2 | 1 GB | ~$0.01 |
| Small Production | `t3.small` | 2 | 2 GB | ~$0.02 |
| Medium Production | `t3.medium` | 2 | 4 GB | ~$0.04 |
| Large Production | `t3.large` | 2 | 8 GB | ~$0.08 |

### Security Configuration

Update security settings in `terraform.tfvars`:

```hcl
# Restrict SSH access to your IP
allowed_ssh_cidr = ["YOUR_IP_ADDRESS/32"]

# Restrict API access if needed
allowed_api_cidr = ["10.0.0.0/8"]
```

## 📊 Monitoring

### CloudWatch Integration

The deployment includes CloudWatch logging:

```bash
# View application logs
aws logs tail /aws/ec2/design-analysis --follow

# Create CloudWatch dashboard
aws cloudwatch put-dashboard \
  --dashboard-name "DesignAnalysis" \
  --dashboard-body file://dashboard.json
```

### Health Checks

The application includes built-in health checks:

```bash
# Check application health
curl http://YOUR_INSTANCE_IP/health

# Check storage status
curl http://YOUR_INSTANCE_IP/storage/info
```

## 🔄 Updates and Maintenance

### Updating the Application

1. **Update the repository URL** in `terraform.tfvars`
2. **Apply changes:**
   ```bash
   terraform plan
   terraform apply
   ```

### Scaling

To scale the deployment:

1. **Increase instance size:**
   ```hcl
   instance_type = "t3.large"
   ```

2. **Add more instances** (requires load balancer setup)

### Backup and Recovery

The S3 storage provides automatic backup capabilities:

```bash
# Backup S3 data
aws s3 sync s3://your-bucket-name ./backup/

# Restore from backup
aws s3 sync ./backup/ s3://your-bucket-name/
```

## 🗑️ Cleanup

To destroy the infrastructure:

```bash
# Destroy all resources
terraform destroy

# Confirm destruction
terraform destroy -auto-approve
```

**⚠️ Warning**: This will delete all data in the S3 bucket!

## 🔍 Troubleshooting

### Common Issues

#### **Terraform Plan Fails**
```bash
# Check AWS credentials
aws sts get-caller-identity

# Validate configuration
terraform validate
```

#### **Instance Fails to Start**
```bash
# Check instance logs
aws ec2 get-console-output --instance-id i-xxxxxxxxx

# SSH to instance
ssh -i your-key.pem ec2-user@YOUR_INSTANCE_IP
```

#### **Application Not Responding**
```bash
# Check service status
sudo systemctl status design-analysis

# Check nginx status
sudo systemctl status nginx

# Check logs
sudo journalctl -u design-analysis -f
```

### Debug Commands

```bash
# Get instance details
terraform output

# Check security group
aws ec2 describe-security-groups --group-ids $(terraform output -raw security_group_id)

# Test S3 access
aws s3 ls s3://$(terraform output -raw s3_bucket_name)
```

## 📈 Cost Optimization

### Reserved Instances

Purchase reserved instances for cost savings:

```bash
# Check reserved instance offerings
aws ec2 describe-reserved-instances-offerings \
  --instance-type t3.medium \
  --offering-type All Upfront
```

### Spot Instances

For non-critical workloads, consider spot instances:

```hcl
# Add to main.tf
resource "aws_spot_instance_request" "design_analysis" {
  spot_price = "0.02"
  # ... other configuration
}
```

## 🎯 Next Steps

1. **Set up monitoring** with CloudWatch dashboards
2. **Configure alerts** for system health
3. **Set up CI/CD** pipeline for automated deployments
4. **Add SSL certificate** for HTTPS
5. **Configure domain name** and DNS
6. **Set up backup** and disaster recovery

## 📚 Additional Resources

- [Terraform AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS EC2 User Guide](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/)
- [AWS S3 User Guide](https://docs.aws.amazon.com/s3/)
- [CloudWatch Documentation](https://docs.aws.amazon.com/cloudwatch/)

Your Design Analysis API is now deployed with infrastructure as code! 🚀
