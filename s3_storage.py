#!/usr/bin/env python3
"""
AWS S3 Storage Implementation for Design Analysis System
Replaces local file storage with S3 for production scalability
"""

import os
import json
import boto3
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timezone
from pathlib import Path
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class S3Storage:
    """
    AWS S3 Storage implementation for design analysis results

    Features:
    - Automatic bucket creation and management
    - Structured folder organization
    - Metadata tracking
    - Error handling and retries
    - Cost optimization
    - Security best practices
    """

    def __init__(
        self,
        bucket_name: Optional[str] = None,
        region: Optional[str] = None,
        prefix: str = "design-analysis",
        enable_versioning: bool = True,
        enable_lifecycle: bool = True
    ):
        """
        Initialize S3 storage

        Args:
            bucket_name: S3 bucket name (auto-generated if not provided)
            region: AWS region (defaults to environment or us-east-1)
            prefix: Folder prefix for organizing data
            enable_versioning: Enable S3 versioning for data protection
            enable_lifecycle: Enable lifecycle policies for cost optimization
        """
        self.region = region or os.getenv("AWS_REGION", "us-east-1")
        self.prefix = prefix.rstrip("/")
        self.enable_versioning = enable_versioning
        self.enable_lifecycle = enable_lifecycle

        # Auto-generate bucket name if not provided
        if bucket_name:
            self.bucket_name = bucket_name
        else:
            import uuid
            self.bucket_name = f"design-analysis-{uuid.uuid4().hex[:8]}"

        # Initialize S3 client
        self._init_s3_client()

        # Ensure bucket exists
        self._ensure_bucket_exists()

    def _init_s3_client(self):
        """Initialize S3 client with proper configuration"""
        try:
            # Try to get credentials from environment or IAM role
            self.s3_client = boto3.client(
                's3',
                region_name=self.region,
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                aws_session_token=os.getenv("AWS_SESSION_TOKEN")
            )

            # Test connection
            self.s3_client.list_buckets()
            logger.info(
                f"S3 client initialized successfully for region: {self.region}")

        except NoCredentialsError:
            raise Exception(
                "AWS credentials not found. Please set AWS_ACCESS_KEY_ID and "
                "AWS_SECRET_ACCESS_KEY environment variables, or configure AWS CLI."
            )
        except Exception as e:
            raise Exception(f"Failed to initialize S3 client: {e}")

    def _ensure_bucket_exists(self):
        """Create bucket if it doesn't exist and configure it"""
        try:
            # Check if bucket exists
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"Using existing bucket: {self.bucket_name}")

        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                # Bucket doesn't exist, create it
                self._create_bucket()
            else:
                raise Exception(f"Error checking bucket: {e}")

    def _create_bucket(self):
        """Create S3 bucket with proper configuration"""
        try:
            # Create bucket
            if self.region == 'us-east-1':
                self.s3_client.create_bucket(Bucket=self.bucket_name)
            else:
                self.s3_client.create_bucket(
                    Bucket=self.bucket_name,
                    CreateBucketConfiguration={
                        'LocationConstraint': self.region}
                )

            logger.info(f"Created bucket: {self.bucket_name}")

            # Configure bucket settings
            self._configure_bucket()

        except Exception as e:
            raise Exception(f"Failed to create bucket: {e}")

    def _configure_bucket(self):
        """Configure bucket with versioning, lifecycle, and security"""
        try:
            # Enable versioning
            if self.enable_versioning:
                self.s3_client.put_bucket_versioning(
                    Bucket=self.bucket_name,
                    VersioningConfiguration={'Status': 'Enabled'}
                )
                logger.info("Enabled S3 versioning")

            # Configure lifecycle policy for cost optimization
            if self.enable_lifecycle:
                lifecycle_config = {
                    'Rules': [
                        {
                            'ID': 'CostOptimization',
                            'Status': 'Enabled',
                            'Filter': {'Prefix': f'{self.prefix}/'},
                            'Transitions': [
                                {
                                    'Days': 30,
                                    'StorageClass': 'STANDARD_IA'
                                },
                                {
                                    'Days': 90,
                                    'StorageClass': 'GLACIER'
                                }
                            ],
                            'Expiration': {
                                'Days': 365  # Keep for 1 year
                            }
                        }
                    ]
                }

                self.s3_client.put_bucket_lifecycle_configuration(
                    Bucket=self.bucket_name,
                    LifecycleConfiguration=lifecycle_config
                )
                logger.info("Configured lifecycle policy")

            # Set bucket encryption
            self.s3_client.put_bucket_encryption(
                Bucket=self.bucket_name,
                ServerSideEncryptionConfiguration={
                    'Rules': [
                        {
                            'ApplyServerSideEncryptionByDefault': {
                                'SSEAlgorithm': 'AES256'
                            }
                        }
                    ]
                }
            )
            logger.info("Enabled bucket encryption")

        except Exception as e:
            logger.warning(f"Failed to configure bucket settings: {e}")

    def _get_object_key(self, request_id: str, file_type: str = "analysis") -> str:
        """Generate S3 object key with organized folder structure"""
        timestamp = datetime.now()
        year_month = timestamp.strftime("%Y/%m")

        return f"{self.prefix}/{file_type}/{year_month}/{request_id}.json"

    def save_analysis(self, request_id: str, result: dict) -> bool:
        """
        Save analysis result to S3

        Args:
            request_id: Unique identifier for the analysis
            result: Analysis result dictionary

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Add metadata to result
            result['s3_metadata'] = {
                'bucket': self.bucket_name,
                'region': self.region,
                'stored_at': datetime.now(timezone.utc).isoformat(),
                'storage_type': 's3'
            }

            # Convert to JSON
            json_data = json.dumps(
                result, indent=2, ensure_ascii=False, default=str)

            # Generate S3 key
            object_key = self._get_object_key(request_id, "analysis")

            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=object_key,
                Body=json_data,
                ContentType='application/json',
                Metadata={
                    'request_id': request_id,
                    'implementation': result.get('implementation', 'unknown'),
                    'status': result.get('status', 'unknown'),
                    'timestamp': result.get('timestamp', ''),
                    'file_type': 'analysis'
                }
            )

            logger.info(f"Saved analysis {request_id} to S3: {object_key}")
            return True

        except Exception as e:
            logger.error(f"Failed to save analysis {request_id}: {e}")
            return False

    def load_analysis(self, request_id: str) -> Optional[dict]:
        """
        Load analysis result from S3

        Args:
            request_id: Unique identifier for the analysis

        Returns:
            dict: Analysis result or None if not found
        """
        try:
            # Try to find the object by searching common paths
            possible_keys = [
                self._get_object_key(request_id, "analysis"),
                f"{self.prefix}/analysis/{request_id}.json",
                f"{self.prefix}/{request_id}.json"
            ]

            for object_key in possible_keys:
                try:
                    response = self.s3_client.get_object(
                        Bucket=self.bucket_name,
                        Key=object_key
                    )

                    # Parse JSON
                    result = json.loads(
                        response['Body'].read().decode('utf-8'))
                    logger.info(
                        f"Loaded analysis {request_id} from S3: {object_key}")
                    return result

                except ClientError as e:
                    if e.response['Error']['Code'] == 'NoSuchKey':
                        continue
                    else:
                        raise e

            logger.warning(f"Analysis {request_id} not found in S3")
            return None

        except Exception as e:
            logger.error(f"Failed to load analysis {request_id}: {e}")
            return None

    def delete_analysis(self, request_id: str) -> bool:
        """
        Delete analysis result from S3

        Args:
            request_id: Unique identifier for the analysis

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Try to find and delete the object
            possible_keys = [
                self._get_object_key(request_id, "analysis"),
                f"{self.prefix}/analysis/{request_id}.json",
                f"{self.prefix}/{request_id}.json"
            ]

            for object_key in possible_keys:
                try:
                    self.s3_client.delete_object(
                        Bucket=self.bucket_name,
                        Key=object_key
                    )
                    logger.info(
                        f"Deleted analysis {request_id} from S3: {object_key}")
                    return True

                except ClientError as e:
                    if e.response['Error']['Code'] == 'NoSuchKey':
                        continue
                    else:
                        raise e

            logger.warning(f"Analysis {request_id} not found for deletion")
            return False

        except Exception as e:
            logger.error(f"Failed to delete analysis {request_id}: {e}")
            return False

    def list_analyses(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        List all stored analyses with metadata

        Args:
            limit: Maximum number of analyses to return

        Returns:
            List of analysis metadata dictionaries
        """
        try:
            analyses = []

            # List objects in the analysis folder
            paginator = self.s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(
                Bucket=self.bucket_name,
                Prefix=f"{self.prefix}/analysis/",
                MaxItems=limit
            )

            for page in pages:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        try:
                            # Get object metadata
                            response = self.s3_client.head_object(
                                Bucket=self.bucket_name,
                                Key=obj['Key']
                            )

                            metadata = response.get('Metadata', {})

                            analyses.append({
                                "request_id": metadata.get('request_id', obj['Key'].split('/')[-1].replace('.json', '')),
                                "timestamp": metadata.get('timestamp', ''),
                                "implementation": metadata.get('implementation', 'unknown'),
                                "status": metadata.get('status', 'unknown'),
                                "file_size": obj['Size'],
                                "created": obj['LastModified'].isoformat(),
                                "s3_key": obj['Key'],
                                "storage_type": "s3"
                            })

                        except Exception as e:
                            logger.warning(
                                f"Failed to get metadata for {obj['Key']}: {e}")
                            continue

            # Sort by creation time (newest first)
            analyses.sort(key=lambda x: x['created'], reverse=True)

            logger.info(f"Listed {len(analyses)} analyses from S3")
            return analyses

        except Exception as e:
            logger.error(f"Failed to list analyses: {e}")
            return []

    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics

        Returns:
            Dictionary with storage statistics
        """
        try:
            total_size = 0
            total_analyses = 0
            implementations = {}

            # Get storage statistics
            paginator = self.s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(
                Bucket=self.bucket_name,
                Prefix=f"{self.prefix}/analysis/"
            )

            for page in pages:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        total_size += obj['Size']
                        total_analyses += 1

                        # Get implementation info
                        try:
                            response = self.s3_client.head_object(
                                Bucket=self.bucket_name,
                                Key=obj['Key']
                            )
                            implementation = response.get('Metadata', {}).get(
                                'implementation', 'unknown')
                            implementations[implementation] = implementations.get(
                                implementation, 0) + 1
                        except:
                            implementations['unknown'] = implementations.get(
                                'unknown', 0) + 1

            # Get bucket info
            bucket_info = self.s3_client.get_bucket_location(
                Bucket=self.bucket_name)

            stats = {
                "total_analyses": total_analyses,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "total_size_gb": round(total_size / (1024 * 1024 * 1024), 2),
                "implementations_used": implementations,
                "storage_type": "s3",
                "bucket_name": self.bucket_name,
                "bucket_region": bucket_info.get('LocationConstraint', 'us-east-1'),
                "prefix": self.prefix,
                "versioning_enabled": self.enable_versioning,
                "lifecycle_enabled": self.enable_lifecycle
            }

            logger.info(
                f"Storage stats: {total_analyses} analyses, {stats['total_size_mb']} MB")
            return stats

        except Exception as e:
            logger.error(f"Failed to get storage stats: {e}")
            return {"error": str(e)}

    def search_analyses(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Search analyses by content (basic text search)

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of matching analyses
        """
        try:
            results = []
            query_lower = query.lower()

            # Get all analyses
            analyses = self.list_analyses(limit=1000)  # Get more for searching

            for analysis in analyses:
                # Load the full analysis for content search
                full_analysis = self.load_analysis(analysis['request_id'])
                if full_analysis:
                    # Search in various fields
                    searchable_text = json.dumps(
                        full_analysis, default=str).lower()

                    if query_lower in searchable_text:
                        results.append({
                            **analysis,
                            'match_score': searchable_text.count(query_lower)
                        })

            # Sort by match score and limit results
            results.sort(key=lambda x: x.get('match_score', 0), reverse=True)
            return results[:limit]

        except Exception as e:
            logger.error(f"Failed to search analyses: {e}")
            return []

    def backup_to_local(self, output_dir: str = "s3_backup") -> bool:
        """
        Backup all S3 data to local filesystem

        Args:
            output_dir: Local directory to save backup

        Returns:
            bool: True if successful
        """
        try:
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)

            analyses = self.list_analyses(limit=10000)

            for analysis in analyses:
                full_analysis = self.load_analysis(analysis['request_id'])
                if full_analysis:
                    file_path = output_path / f"{analysis['request_id']}.json"
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(full_analysis, f, indent=2,
                                  ensure_ascii=False)

            logger.info(f"Backed up {len(analyses)} analyses to {output_dir}")
            return True

        except Exception as e:
            logger.error(f"Failed to backup to local: {e}")
            return False

    def get_bucket_info(self) -> Dict[str, Any]:
        """Get detailed bucket information"""
        try:
            # Get bucket location
            location = self.s3_client.get_bucket_location(
                Bucket=self.bucket_name)

            # Get bucket versioning
            versioning = self.s3_client.get_bucket_versioning(
                Bucket=self.bucket_name)

            # Get bucket encryption
            try:
                encryption = self.s3_client.get_bucket_encryption(
                    Bucket=self.bucket_name)
            except ClientError:
                encryption = {
                    "ServerSideEncryptionConfiguration": {"Rules": []}}

            return {
                "bucket_name": self.bucket_name,
                "region": location.get('LocationConstraint', 'us-east-1'),
                "versioning_status": versioning.get('Status', 'NotEnabled'),
                "encryption_enabled": len(encryption.get('ServerSideEncryptionConfiguration', {}).get('Rules', [])) > 0,
                "prefix": self.prefix,
                "created_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to get bucket info: {e}")
            return {"error": str(e)}


# Factory function for easy initialization
def create_s3_storage(
    bucket_name: Optional[str] = None,
    region: Optional[str] = None,
    prefix: str = "design-analysis"
) -> S3Storage:
    """
    Factory function to create S3 storage instance

    Args:
        bucket_name: S3 bucket name (auto-generated if not provided)
        region: AWS region
        prefix: Folder prefix for organizing data

    Returns:
        S3Storage instance
    """
    return S3Storage(
        bucket_name=bucket_name,
        region=region,
        prefix=prefix
    )


# Example usage
if __name__ == "__main__":
    # Test S3 storage
    try:
        storage = create_s3_storage()
        print(f"✅ S3 Storage initialized successfully!")
        print(f"📦 Bucket: {storage.bucket_name}")
        print(f"🌍 Region: {storage.region}")
        print(f"📁 Prefix: {storage.prefix}")

        # Get bucket info
        info = storage.get_bucket_info()
        print(f"📊 Bucket Info: {info}")

    except Exception as e:
        print(f"❌ Failed to initialize S3 storage: {e}")
        print("💡 Make sure AWS credentials are configured properly")
