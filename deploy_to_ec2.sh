#!/bin/bash
# Quick EC2 Deployment Script for Design Analysis API
# This script automates the deployment process

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS credentials not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    # Check Terraform
    if ! command -v terraform &> /dev/null; then
        print_error "Terraform is not installed. Please install it first."
        exit 1
    fi
    
    print_success "All prerequisites are met!"
}

# Function to get user input
get_user_input() {
    print_status "Please provide the following information:"
    
    # Get OpenAI API key
    read -p "OpenAI API Key: " openai_api_key
    if [ -z "$openai_api_key" ]; then
        print_error "OpenAI API key is required!"
        exit 1
    fi
    
    # Get EC2 key pair name
    read -p "EC2 Key Pair Name: " key_pair_name
    if [ -z "$key_pair_name" ]; then
        print_error "EC2 key pair name is required!"
        exit 1
    fi
    
    # Get user's IP address for SSH access
    read -p "Your IP Address (for SSH access, or press Enter for 0.0.0.0/0): " user_ip
    if [ -z "$user_ip" ]; then
        allowed_ssh_cidr="0.0.0.0/0"
    else
        allowed_ssh_cidr="${user_ip}/32"
    fi
    
    # Get instance type
    read -p "Instance Type (t3.micro/t3.small/t3.medium/t3.large) [t3.medium]: " instance_type
    instance_type=${instance_type:-t3.medium}
    
    # Get region
    read -p "AWS Region [us-east-1]: " aws_region
    aws_region=${aws_region:-us-east-1}
    
    # Get S3 bucket name
    read -p "S3 Bucket Name [design-analysis-production]: " s3_bucket_name
    s3_bucket_name=${s3_bucket_name:-design-analysis-production}
    
    # Get repository URL
    read -p "Git Repository URL [https://github.com/yourusername/design-analysis.git]: " repo_url
    repo_url=${repo_url:-https://github.com/yourusername/design-analysis.git}
    
    # Ask for Elastic IP
    read -p "Create Elastic IP? (y/N): " create_eip
    create_eip=${create_eip:-n}
    
    print_success "Configuration collected!"
}

# Function to create Terraform configuration
create_terraform_config() {
    print_status "Creating Terraform configuration..."
    
    # Create deployment directory
    mkdir -p deployment/terraform
    
    # Copy Terraform files
    cp deployment/terraform/main.tf deployment/terraform/
    cp deployment/terraform/variables.tf deployment/terraform/
    
    # Create terraform.tfvars
    cat > deployment/terraform/terraform.tfvars << EOF
# AWS Configuration
aws_region = "${aws_region}"

# EC2 Configuration
instance_type     = "${instance_type}"
key_pair_name     = "${key_pair_name}"
root_volume_size  = 20

# Security Configuration
allowed_ssh_cidr = ["${allowed_ssh_cidr}"]
allowed_api_cidr = ["0.0.0.0/0"]

# Environment
environment = "prod"

# Application Configuration
openai_api_key = "${openai_api_key}"
s3_bucket_name = "${s3_bucket_name}"
s3_prefix      = "design-analysis"
repo_url       = "${repo_url}"

# Network Configuration
create_eip = ${create_eip}

# Optional Features
enable_cloudwatch_agent = true
enable_ssl             = false
domain_name            = ""
backup_enabled         = true
backup_retention_days  = 30

# Tags
tags = {
  Project     = "Design Analysis"
  ManagedBy   = "Terraform"
  Environment = "production"
  Owner       = "deployment-script"
  CostCenter  = "engineering"
}
EOF
    
    print_success "Terraform configuration created!"
}

# Function to deploy with Terraform
deploy_with_terraform() {
    print_status "Deploying with Terraform..."
    
    cd deployment/terraform
    
    # Initialize Terraform
    print_status "Initializing Terraform..."
    terraform init
    
    # Plan deployment
    print_status "Planning deployment..."
    terraform plan
    
    # Ask for confirmation
    read -p "Do you want to proceed with the deployment? (y/N): " confirm
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        print_warning "Deployment cancelled by user."
        exit 0
    fi
    
    # Apply configuration
    print_status "Applying Terraform configuration..."
    terraform apply -auto-approve
    
    # Get outputs
    print_status "Getting deployment outputs..."
    instance_ip=$(terraform output -raw public_ip)
    api_url=$(terraform output -raw api_url)
    health_url=$(terraform output -raw health_check_url)
    
    print_success "Deployment completed successfully!"
    echo ""
    echo "🌐 API URL: ${api_url}"
    echo "🏥 Health Check: ${health_url}"
    echo "🖥️  Instance IP: ${instance_ip}"
    echo ""
    
    cd ../..
}

# Function to test deployment
test_deployment() {
    print_status "Testing deployment..."
    
    cd deployment/terraform
    
    # Get the health check URL
    health_url=$(terraform output -raw health_check_url)
    
    # Wait for the application to start
    print_status "Waiting for application to start (this may take a few minutes)..."
    
    for i in {1..30}; do
        if curl -f -s "${health_url}" > /dev/null 2>&1; then
            print_success "Application is responding!"
            break
        fi
        
        if [ $i -eq 30 ]; then
            print_warning "Application is not responding after 5 minutes."
            print_warning "You may need to check the instance manually."
            break
        fi
        
        echo -n "."
        sleep 10
    done
    
    # Test the API
    print_status "Testing API endpoints..."
    
    # Health check
    if curl -f -s "${health_url}" > /dev/null; then
        print_success "Health check passed!"
    else
        print_warning "Health check failed!"
    fi
    
    # Storage info
    storage_url="${health_url%/health}/storage/info"
    if curl -f -s "${storage_url}" > /dev/null; then
        print_success "Storage info endpoint working!"
    else
        print_warning "Storage info endpoint failed!"
    fi
    
    cd ../..
}

# Function to show next steps
show_next_steps() {
    print_status "Next steps:"
    echo ""
    echo "1. 🌐 Access your API at: $(cd deployment/terraform && terraform output -raw api_url)"
    echo "2. 📊 Monitor logs: aws logs tail /aws/ec2/design-analysis --follow"
    echo "3. 🔧 SSH to instance: ssh -i your-key.pem ec2-user@$(cd deployment/terraform && terraform output -raw public_ip)"
    echo "4. 📝 View deployment logs: ssh -i your-key.pem ec2-user@$(cd deployment/terraform && terraform output -raw public_ip) 'cat /opt/design-analysis/deployment.log'"
    echo "5. 🗑️  To destroy: cd deployment/terraform && terraform destroy"
    echo ""
    echo "📚 Documentation:"
    echo "   - EC2 Deployment Guide: EC2_DEPLOYMENT_GUIDE.md"
    echo "   - S3 Setup Guide: S3_SETUP_GUIDE.md"
    echo "   - API Documentation: http://$(cd deployment/terraform && terraform output -raw api_url)/docs"
    echo ""
}

# Main deployment function
main() {
    echo "🚀 Design Analysis API - EC2 Deployment Script"
    echo "=============================================="
    echo ""
    
    # Check prerequisites
    check_prerequisites
    
    # Get user input
    get_user_input
    
    # Create Terraform configuration
    create_terraform_config
    
    # Deploy with Terraform
    deploy_with_terraform
    
    # Test deployment
    test_deployment
    
    # Show next steps
    show_next_steps
    
    print_success "Deployment script completed!"
}

# Check if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
