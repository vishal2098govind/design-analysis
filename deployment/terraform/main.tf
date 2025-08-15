# Terraform configuration for Design Analysis API on EC2
# This creates a complete infrastructure including EC2, IAM, and security groups

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Data sources
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# IAM Role for EC2 instance
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

  tags = {
    Name = "Design Analysis S3 Role"
  }
}

# IAM Policy for S3 access
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
          "s3:ListBucket",
          "s3:PutBucketVersioning",
          "s3:PutBucketLifecycleConfiguration",
          "s3:PutBucketEncryption",
          "s3:GetBucketLocation",
          "s3:GetBucketVersioning",
          "s3:GetBucketEncryption"
        ]
        Resource = [
          "arn:aws:s3:::design-analysis-*",
          "arn:aws:s3:::design-analysis-*/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "ec2:DescribeInstances",
          "ec2:DescribeTags"
        ]
        Resource = "*"
      }
    ]
  })
}

# IAM Instance Profile
resource "aws_iam_instance_profile" "design_analysis" {
  name = "DesignAnalysisS3Role"
  role = aws_iam_role.design_analysis.name
}

# Security Group
resource "aws_security_group" "design_analysis" {
  name        = "design-analysis-sg"
  description = "Security group for Design Analysis API"
  vpc_id      = data.aws_vpc.default.id

  # SSH access
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.allowed_ssh_cidr
    description = "SSH access"
  }

  # HTTP access
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP access"
  }

  # HTTPS access
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS access"
  }

  # API direct access (optional)
  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = var.allowed_api_cidr
    description = "API direct access"
  }

  # All outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = {
    Name = "Design Analysis Security Group"
  }
}

# EC2 Instance
resource "aws_instance" "design_analysis" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = var.instance_type
  key_name               = var.key_pair_name
  vpc_security_group_ids = [aws_security_group.design_analysis.id]
  iam_instance_profile   = aws_iam_instance_profile.design_analysis.name
  subnet_id              = data.aws_subnets.default.ids[0]

  root_block_device {
    volume_type = "gp3"
    volume_size = var.root_volume_size
    encrypted   = true
  }

  user_data = templatefile("${path.module}/../user-data.sh", {
    openai_api_key = var.openai_api_key
    s3_bucket_name = var.s3_bucket_name
    s3_region      = var.aws_region
    s3_prefix      = var.s3_prefix
    repo_url       = var.repo_url
  })

  metadata_options {
    http_tokens = "required"
    http_endpoint = "enabled"
  }

  tags = {
    Name        = "Design Analysis API"
    Environment = var.environment
    Project     = "Design Analysis"
  }
}

# Elastic IP (optional)
resource "aws_eip" "design_analysis" {
  count    = var.create_eip ? 1 : 0
  instance = aws_instance.design_analysis.id
  domain   = "vpc"

  tags = {
    Name = "Design Analysis EIP"
  }
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "design_analysis" {
  name              = "/aws/ec2/design-analysis"
  retention_in_days = 14

  tags = {
    Name = "Design Analysis Logs"
  }
}

# Outputs
output "instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.design_analysis.id
}

output "public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_instance.design_analysis.public_ip
}

output "elastic_ip" {
  description = "Elastic IP address (if created)"
  value       = var.create_eip ? aws_eip.design_analysis[0].public_ip : null
}

output "api_url" {
  description = "URL of the Design Analysis API"
  value       = "http://${aws_instance.design_analysis.public_ip}"
}

output "health_check_url" {
  description = "Health check URL"
  value       = "http://${aws_instance.design_analysis.public_ip}/health"
}

output "security_group_id" {
  description = "ID of the security group"
  value       = aws_security_group.design_analysis.id
}

output "iam_role_arn" {
  description = "ARN of the IAM role"
  value       = aws_iam_role.design_analysis.arn
}
