#!/usr/bin/env python3
"""
Test IAM Role Functionality
Verifies that the system can access S3 using IAM roles without access keys
"""

import os
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_iam_role_access():
    """Test S3 access using IAM role"""

    print("🔐 Testing IAM Role Access to S3")
    print("=" * 50)

    # Check if explicit credentials are provided
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")

    if aws_access_key_id and aws_secret_access_key:
        print("⚠️  Explicit AWS credentials found in environment")
        print("   This test is designed for IAM role usage")
        print("   Consider removing AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
        print()

    try:
        # Try to create S3 client without explicit credentials
        print("🔗 Initializing S3 client...")
        s3_client = boto3.client('s3')

        # Test basic S3 access
        print("📋 Testing S3 access...")
        response = s3_client.list_buckets()

        print("✅ S3 access successful!")
        print(f"📊 Found {len(response['Buckets'])} buckets:")

        for bucket in response['Buckets'][:5]:  # Show first 5 buckets
            print(f"   • {bucket['Name']}")

        if len(response['Buckets']) > 5:
            print(f"   ... and {len(response['Buckets']) - 5} more")

        return True

    except NoCredentialsError:
        print("❌ No AWS credentials found")
        print("💡 This could mean:")
        print("   1. No IAM role attached to EC2 instance")
        print("   2. IAM role doesn't have S3 permissions")
        print("   3. Not running on EC2 instance")
        print("   4. AWS CLI not configured")
        return False

    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'AccessDenied':
            print("❌ Access denied to S3")
            print("💡 This could mean:")
            print("   1. IAM role doesn't have sufficient S3 permissions")
            print("   2. Bucket doesn't exist")
            print("   3. Region mismatch")
        else:
            print(f"❌ S3 error: {error_code}")
        return False

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_specific_bucket_access():
    """Test access to a specific S3 bucket"""

    bucket_name = os.getenv("S3_BUCKET_NAME")
    if not bucket_name:
        print("\n📦 No S3_BUCKET_NAME specified - skipping bucket test")
        return True

    print(f"\n📦 Testing access to specific bucket: {bucket_name}")
    print("-" * 50)

    try:
        s3_client = boto3.client('s3')

        # Test bucket access
        print("🔍 Testing bucket access...")
        s3_client.head_bucket(Bucket=bucket_name)
        print("✅ Bucket access successful!")

        # Test listing objects
        print("📋 Testing object listing...")
        response = s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=5)

        if 'Contents' in response:
            print(f"✅ Found {len(response['Contents'])} objects in bucket")
            for obj in response['Contents'][:3]:
                print(f"   • {obj['Key']} ({obj['Size']} bytes)")
        else:
            print("✅ Bucket is empty (no objects found)")

        return True

    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NoSuchBucket':
            print(f"❌ Bucket '{bucket_name}' does not exist")
            print("💡 The bucket will be created automatically when needed")
        elif error_code == 'AccessDenied':
            print(f"❌ Access denied to bucket '{bucket_name}'")
            print("💡 Check IAM role permissions")
        else:
            print(f"❌ Bucket error: {error_code}")
        return False

    except Exception as e:
        print(f"❌ Unexpected bucket error: {e}")
        return False


def test_ec2_metadata():
    """Test if running on EC2 and can access instance metadata"""

    print("\n🖥️  Testing EC2 Instance Metadata")
    print("-" * 50)

    try:
        import requests

        # Test instance metadata service
        print("🔍 Checking EC2 instance metadata...")
        response = requests.get(
            'http://169.254.169.254/latest/meta-data/instance-id', timeout=2)

        if response.status_code == 200:
            instance_id = response.text
            print(f"✅ Running on EC2 instance: {instance_id}")

            # Check IAM role
            try:
                iam_response = requests.get(
                    'http://169.254.169.254/latest/meta-data/iam/security-credentials/', timeout=2)
                if iam_response.status_code == 200:
                    role_name = iam_response.text.strip()
                    print(f"✅ IAM role attached: {role_name}")
                    return True
                else:
                    print("❌ No IAM role attached to instance")
                    return False
            except:
                print("❌ Could not check IAM role")
                return False
        else:
            print("❌ Not running on EC2 instance")
            return False

    except requests.exceptions.RequestException:
        print("❌ Could not access EC2 metadata service")
        print("💡 This is normal if not running on EC2")
        return False
    except Exception as e:
        print(f"❌ Metadata error: {e}")
        return False


def test_storage_initialization():
    """Test the S3Storage class initialization"""

    print("\n🏗️  Testing S3Storage Class Initialization")
    print("-" * 50)

    try:
        from s3_storage import create_s3_storage

        print("🔗 Creating S3Storage instance...")
        storage = create_s3_storage()

        print("✅ S3Storage initialized successfully!")
        print(f"📦 Bucket: {storage.bucket_name}")
        print(f"🌍 Region: {storage.region}")
        print(f"📁 Prefix: {storage.prefix}")

        # Test bucket info
        print("📊 Getting bucket info...")
        bucket_info = storage.get_bucket_info()
        print(
            f"✅ Bucket info retrieved: {bucket_info.get('bucket_name', 'N/A')}")

        return True

    except Exception as e:
        print(f"❌ S3Storage initialization failed: {e}")
        return False


def main():
    """Main test function"""

    print("🚀 IAM Role and S3 Access Test Suite")
    print("=" * 60)

    # Check environment
    print("🔍 Environment Check:")
    print(f"   STORAGE_TYPE: {os.getenv('STORAGE_TYPE', 'local')}")
    print(f"   S3_BUCKET_NAME: {os.getenv('S3_BUCKET_NAME', 'Not set')}")
    print(f"   S3_REGION: {os.getenv('S3_REGION', 'us-east-1')}")
    print(
        f"   AWS_ACCESS_KEY_ID: {'Set' if os.getenv('AWS_ACCESS_KEY_ID') else 'Not set'}")
    print(
        f"   AWS_SECRET_ACCESS_KEY: {'Set' if os.getenv('AWS_SECRET_ACCESS_KEY') else 'Not set'}")
    print()

    # Run tests
    tests = [
        ("IAM Role Access", test_iam_role_access),
        ("Specific Bucket Access", test_specific_bucket_access),
        ("EC2 Metadata", test_ec2_metadata),
        ("S3Storage Class", test_storage_initialization)
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))

    # Summary
    print(f"\n{'='*60}")
    print("📊 Test Results Summary")
    print("=" * 60)

    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1

    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")

    if passed == len(results):
        print("🎉 All tests passed! IAM role access is working correctly.")
        print("💡 Your system is ready for secure S3 access without access keys!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        print("💡 Make sure your EC2 instance has the correct IAM role attached.")

    # Recommendations
    print(f"\n💡 Recommendations:")
    if os.getenv('AWS_ACCESS_KEY_ID'):
        print("   • Consider removing AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
        print("   • Use IAM roles for better security")
    else:
        print("   • Great! No explicit credentials found")
        print("   • System is using IAM role for secure access")

    return passed == len(results)


if __name__ == "__main__":
    main()
