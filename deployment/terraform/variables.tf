# Terraform variables for Design Analysis EC2 deployment

variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.medium"
  
  validation {
    condition     = contains(["t3.micro", "t3.small", "t3.medium", "t3.large", "t3.xlarge"], var.instance_type)
    error_message = "Instance type must be a valid t3 instance type."
  }
}

variable "key_pair_name" {
  description = "Name of the EC2 key pair for SSH access"
  type        = string
}

variable "root_volume_size" {
  description = "Size of the root volume in GB"
  type        = number
  default     = 20
  
  validation {
    condition     = var.root_volume_size >= 8 && var.root_volume_size <= 100
    error_message = "Root volume size must be between 8 and 100 GB."
  }
}

variable "allowed_ssh_cidr" {
  description = "CIDR blocks allowed for SSH access"
  type        = list(string)
  default     = ["0.0.0.0/0"]
  
  validation {
    condition = alltrue([
      for cidr in var.allowed_ssh_cidr : can(cidrhost(cidr, 0))
    ])
    error_message = "All SSH CIDR blocks must be valid CIDR notation."
  }
}

variable "allowed_api_cidr" {
  description = "CIDR blocks allowed for direct API access (port 8000)"
  type        = list(string)
  default     = ["0.0.0.0/0"]
  
  validation {
    condition = alltrue([
      for cidr in var.allowed_api_cidr : can(cidrhost(cidr, 0))
    ])
    error_message = "All API CIDR blocks must be valid CIDR notation."
  }
}

variable "environment" {
  description = "Environment name (e.g., dev, staging, prod)"
  type        = string
  default     = "prod"
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "openai_api_key" {
  description = "OpenAI API key for the application"
  type        = string
  sensitive   = true
}

variable "s3_bucket_name" {
  description = "Name of the S3 bucket for storing analysis results"
  type        = string
  default     = "design-analysis-production"
  
  validation {
    condition     = length(var.s3_bucket_name) >= 3 && length(var.s3_bucket_name) <= 63
    error_message = "S3 bucket name must be between 3 and 63 characters."
  }
}

variable "s3_prefix" {
  description = "Prefix for organizing data in S3"
  type        = string
  default     = "design-analysis"
}

variable "repo_url" {
  description = "Git repository URL for the application code"
  type        = string
  default     = "https://github.com/yourusername/design-analysis.git"
}

variable "create_eip" {
  description = "Whether to create an Elastic IP for the instance"
  type        = bool
  default     = false
}

# Optional variables for advanced configuration
variable "enable_cloudwatch_agent" {
  description = "Whether to install and configure CloudWatch agent"
  type        = bool
  default     = true
}

variable "enable_ssl" {
  description = "Whether to configure SSL/TLS with Let's Encrypt"
  type        = bool
  default     = false
}

variable "domain_name" {
  description = "Domain name for SSL certificate (required if enable_ssl is true)"
  type        = string
  default     = ""
  
  validation {
    condition     = var.enable_ssl ? var.domain_name != "" : true
    error_message = "Domain name is required when SSL is enabled."
  }
}

variable "backup_enabled" {
  description = "Whether to enable automated backups"
  type        = bool
  default     = true
}

variable "backup_retention_days" {
  description = "Number of days to retain backups"
  type        = number
  default     = 30
  
  validation {
    condition     = var.backup_retention_days >= 1 && var.backup_retention_days <= 365
    error_message = "Backup retention must be between 1 and 365 days."
  }
}

# Tags
variable "tags" {
  description = "Additional tags for resources"
  type        = map(string)
  default = {
    Project     = "Design Analysis"
    ManagedBy   = "Terraform"
    Environment = "production"
  }
}
