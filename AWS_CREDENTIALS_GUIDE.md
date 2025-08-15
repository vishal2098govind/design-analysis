# AWS Credentials Configuration Guide

This guide explains how the Design Analysis System handles AWS credentials and how to configure them properly.

## Overview

The system supports multiple ways to provide AWS credentials:

1. **IAM Role** (Recommended for production)
2. **Explicit Access Keys** (For development/local use)
3. **AWS CLI Configuration** (Fallback option)

## Credential Priority Order

The system checks for credentials in this order:

1. **Explicit Environment Variables** (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
2. **IAM Role** (if running on EC2)
3. **AWS CLI Configuration** (`~/.aws/credentials`)
4. **AWS SDK Default Provider Chain**

## Configuration Options

### Option 1: IAM Role (Recommended for Production)

If you're running on an EC2 instance with an attached IAM role, simply leave the credential environment variables empty or unset:

```bash
# In your .env file
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_SESSION_TOKEN=
```

**Benefits:**
- More secure (no hardcoded credentials)
- Automatic credential rotation
- No need to manage access keys

### Option 2: Explicit Access Keys (Development/Local)

For local development or when not using IAM roles, you can set explicit credentials:

```bash
# In your .env file
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_SESSION_TOKEN=  # Optional, for temporary credentials
```

**Important:** Make sure the values are not empty strings. Empty strings (`""`) are treated as "not set" and will cause the system to fall back to IAM roles or AWS CLI configuration.

### Option 3: AWS CLI Configuration

You can configure credentials using the AWS CLI:

```bash
aws configure
```

This will create `~/.aws/credentials` and `~/.aws/config` files.

## Troubleshooting

### Empty String Issue

If you have empty strings in your `.env` file like this:

```bash
AWS_ACCESS_KEY_ID=""
AWS_SECRET_ACCESS_KEY=""
```

The system will treat these as "not set" and use IAM roles or AWS CLI configuration instead. This is the correct behavior.

### Testing Your Configuration

Use the provided test script to verify your credential configuration:

```bash
python test_aws_credentials.py
```

This script will:
- Check your environment variables
- Detect empty strings
- Test S3 access
- Provide specific guidance for any issues

### Common Issues

#### "No AWS credentials found"

**Solutions:**
1. Set `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in your `.env` file
2. Configure AWS CLI: `aws configure`
3. Attach an IAM role to your EC2 instance

#### "Access denied to S3"

**Solutions:**
1. Ensure your credentials have S3 permissions
2. Check that the bucket exists and is in the correct region
3. Verify your IAM role has the necessary S3 policies

#### "Partial credentials detected"

**Cause:** You have only one of `AWS_ACCESS_KEY_ID` or `AWS_SECRET_ACCESS_KEY` set.

**Solution:** Either set both credentials or remove both to use IAM roles.

## Security Best Practices

1. **Use IAM Roles** for production deployments
2. **Never commit credentials** to version control
3. **Rotate access keys** regularly
4. **Use least privilege** - only grant necessary S3 permissions
5. **Consider using temporary credentials** for enhanced security

## Environment Variable Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `AWS_ACCESS_KEY_ID` | No | AWS access key ID |
| `AWS_SECRET_ACCESS_KEY` | No | AWS secret access key |
| `AWS_SESSION_TOKEN` | No | AWS session token (for temporary credentials) |
| `AWS_REGION` | No | AWS region (defaults to us-east-1) |
| `S3_BUCKET_NAME` | No | S3 bucket name (auto-generated if not provided) |
| `S3_REGION` | No | S3 bucket region (defaults to us-east-1) |
| `S3_PREFIX` | No | S3 folder prefix (defaults to design-analysis) |

## Example Configurations

### Local Development
```bash
STORAGE_TYPE=s3
AWS_ACCESS_KEY_ID=your_dev_key
AWS_SECRET_ACCESS_KEY=your_dev_secret
AWS_REGION=us-east-1
```

### Production (EC2 with IAM Role)
```bash
STORAGE_TYPE=s3
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1
```

### Using AWS CLI
```bash
STORAGE_TYPE=s3
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1
# Then run: aws configure
```

## Getting Help

If you're still having issues:

1. Run `python test_aws_credentials.py` for detailed diagnostics
2. Check the AWS documentation for credential configuration
3. Verify your IAM permissions and policies
4. Ensure your AWS region settings are correct
