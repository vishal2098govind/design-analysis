#!/usr/bin/env python3
"""
DynamoDB Tracker for Design Analysis Steps
Tracks the status of each analysis step in real-time
"""

import os
import json
import logging
from datetime import timezone
import boto3
from datetime import datetime
from typing import Dict, Optional, Any
from enum import Enum
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dynamodb_tracker.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class StepStatus(Enum):
    """Enum for step status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DynamoDBTracker:
    """DynamoDB tracker for analysis step status"""

    def __init__(self, table_name: Optional[str] = None):
        """Initialize DynamoDB tracker"""
        self.table_name = table_name or os.getenv(
            "DYNAMODB_TABLE_NAME", "design-analysis-tracking")
        self.region = os.getenv("AWS_REGION", "us-east-1")

        # Initialize DynamoDB client
        self._init_dynamodb_client()

        # Ensure table exists
        self._ensure_table_exists()

        logger.info(
            f"🔍 DynamoDB Tracker initialized for table: {self.table_name}")

    def _init_dynamodb_client(self):
        """Initialize DynamoDB client with proper configuration"""
        try:
            # Check if explicit credentials are provided
            aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
            aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
            aws_session_token = os.getenv("AWS_SESSION_TOKEN")

            # Build client configuration
            client_kwargs = {
                'region_name': self.region
            }

            # Only add explicit credentials if they are provided
            if aws_access_key_id and aws_secret_access_key:
                logger.info("Using explicit AWS credentials for DynamoDB")
                client_kwargs.update({
                    'aws_access_key_id': aws_access_key_id,
                    'aws_secret_access_key': aws_secret_access_key
                })
                if aws_session_token:
                    client_kwargs['aws_session_token'] = aws_session_token
            else:
                logger.info(
                    "No explicit credentials provided - using IAM role for DynamoDB")

            # Initialize DynamoDB client
            self.dynamodb = boto3.client('dynamodb', **client_kwargs)

            # Test connection
            self.dynamodb.list_tables()
            logger.info(
                f"DynamoDB client initialized successfully for region: {self.region}")

        except NoCredentialsError:
            raise Exception(
                "AWS credentials not found for DynamoDB. Please either:\n"
                "1. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables, or\n"
                "2. Configure AWS CLI with 'aws configure', or\n"
                "3. Attach an IAM role to your EC2 instance with DynamoDB permissions"
            )
        except Exception as e:
            raise Exception(f"Failed to initialize DynamoDB client: {e}")

    def _ensure_table_exists(self):
        """Create DynamoDB table if it doesn't exist"""
        try:
            # Check if table exists
            self.dynamodb.describe_table(TableName=self.table_name)
            logger.info(f"Using existing DynamoDB table: {self.table_name}")

        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                # Table doesn't exist, create it
                self._create_table()
            else:
                raise Exception(f"Error checking DynamoDB table: {e}")

    def _create_table(self):
        """Create DynamoDB table with proper configuration"""
        try:
            logger.info(f"Creating DynamoDB table: {self.table_name}")

            table_params = {
                'TableName': self.table_name,
                'KeySchema': [
                    {
                        'AttributeName': 'request_id',
                        'KeyType': 'HASH'  # Partition key
                    }
                ],
                'AttributeDefinitions': [
                    {
                        'AttributeName': 'request_id',
                        'AttributeType': 'S'
                    }
                ],
                'BillingMode': 'PAY_PER_REQUEST'  # On-demand billing
            }

            # Add encryption if supported (DynamoDB uses default encryption by default)
            # Only add explicit encryption if needed for compliance
            # table_params['SSESpecification'] = {
            #     'Enabled': True,
            #     'SSEType': 'AES256'  # or 'KMS' for customer-managed keys
            # }

            # Add tags for better organization
            table_params['Tags'] = [
                {
                    'Key': 'Project',
                    'Value': 'DesignAnalysis'
                },
                {
                    'Key': 'Environment',
                    'Value': os.getenv('ENVIRONMENT', 'development')
                },
                {
                    'Key': 'CreatedBy',
                    'Value': 'DesignAnalysisSystem'
                }
            ]

            self.dynamodb.create_table(**table_params)

            # Wait for table to be active
            logger.info("Waiting for table to become active...")
            waiter = self.dynamodb.get_waiter('table_exists')
            waiter.wait(TableName=self.table_name)

            logger.info(
                f"✅ DynamoDB table '{self.table_name}' created successfully")

        except Exception as e:
            raise Exception(f"Failed to create DynamoDB table: {e}")

    def create_analysis_request(self, request_id: str, research_data_s3_path: str) -> bool:
        """Create a new analysis request tracking entry"""
        try:
            logger.info(f"📝 Creating analysis request tracking: {request_id}")

            # Initialize step status with proper DynamoDB format
            steps_status = {
                "chunking": {
                    "M": {
                        "status": {"S": StepStatus.PENDING.value},
                        "message": {"S": "Waiting to start chunking"},
                        "started_at": {"NULL": True},
                        "completed_at": {"NULL": True}
                    }
                },
                "inferring": {
                    "M": {
                        "status": {"S": StepStatus.PENDING.value},
                        "message": {"S": "Waiting for chunking to complete"},
                        "started_at": {"NULL": True},
                        "completed_at": {"NULL": True}
                    }
                },
                "relating": {
                    "M": {
                        "status": {"S": StepStatus.PENDING.value},
                        "message": {"S": "Waiting for inference to complete"},
                        "started_at": {"NULL": True},
                        "completed_at": {"NULL": True}
                    }
                },
                "explaining": {
                    "M": {
                        "status": {"S": StepStatus.PENDING.value},
                        "message": {"S": "Waiting for pattern analysis to complete"},
                        "started_at": {"NULL": True},
                        "completed_at": {"NULL": True}
                    }
                },
                "activating": {
                    "M": {
                        "status": {"S": StepStatus.PENDING.value},
                        "message": {"S": "Waiting for explanation to complete"},
                        "started_at": {"NULL": True},
                        "completed_at": {"NULL": True}
                    }
                }
            }

            item = {
                'request_id': {'S': request_id},
                'research_data': {'S': research_data_s3_path},
                'analysis_result': {
                    'M': {
                        # Will be updated when analysis completes
                        'result_data': {'S': ''},
                        'steps_status': {'M': steps_status}
                    }
                },
                'created_at': {'S': datetime.utcnow().isoformat()},
                'updated_at': {'S': datetime.utcnow().isoformat()},
                'overall_status': {'S': StepStatus.PENDING.value}
            }

            self.dynamodb.put_item(TableName=self.table_name, Item=item)

            logger.info(f"✅ Analysis request tracking created: {request_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to create analysis request tracking: {e}")
            return False

    def update_step_status(self, request_id: str, step_name: str, status: StepStatus,
                           message: str, result_s3_path: Optional[str] = None) -> bool:
        """Update the status of a specific step"""
        try:
            logger.info(
                f"🔄 Updating step status: {request_id} - {step_name} - {status.value}")

            # Get current timestamp
            timestamp = datetime.utcnow().isoformat()

            # Prepare update expression
            update_expression = "SET "
            expression_attribute_values = {}
            expression_attribute_names = {}

            # Update step status - use proper nested path
            step_path = f"#analysis_result.#steps_status.#{step_name}.#status"
            message_path = f"#analysis_result.#steps_status.#{step_name}.#message"

            update_expression += f"{step_path} = :status, "
            update_expression += f"{message_path} = :message, "

            expression_attribute_names.update({
                '#analysis_result': 'analysis_result',
                '#steps_status': 'steps_status',
                f'#{step_name}': step_name,
                '#status': 'status',
                '#message': 'message'
            })

            expression_attribute_values.update({
                ':status': {'S': status.value},
                ':message': {'S': message}
            })

            # Update started_at if processing
            if status == StepStatus.PROCESSING:
                started_path = f"#analysis_result.#steps_status.#{step_name}.#started_at"
                update_expression += f"{started_path} = :timestamp, "
                expression_attribute_names['#started_at'] = 'started_at'
                expression_attribute_values[':timestamp'] = {'S': timestamp}

            # Update completed_at if completed or failed
            if status in [StepStatus.COMPLETED, StepStatus.FAILED]:
                completed_path = f"#analysis_result.#steps_status.#{step_name}.#completed_at"
                update_expression += f"{completed_path} = :timestamp, "
                expression_attribute_names['#completed_at'] = 'completed_at'
                expression_attribute_values[':timestamp'] = {'S': timestamp}

            # Update overall status and result data if analysis is complete
            if step_name == "activating" and status == StepStatus.COMPLETED:
                update_expression += "#overall_status = :overall_status, "
                update_expression += "#analysis_result.#result_data = :result_data, "
                update_expression += "#updated_at = :timestamp"

                expression_attribute_names.update({
                    '#overall_status': 'overall_status',
                    '#result_data': 'result_data',
                    '#updated_at': 'updated_at'
                })

                expression_attribute_values.update({
                    ':overall_status': {'S': StepStatus.COMPLETED.value},
                    ':result_data': {'S': result_s3_path or ''},
                    ':timestamp': {'S': timestamp}
                })
            else:
                update_expression += "#updated_at = :timestamp"
                expression_attribute_names['#updated_at'] = 'updated_at'
                expression_attribute_values[':timestamp'] = {'S': timestamp}

            # Remove trailing comma and space
            update_expression = update_expression.rstrip(', ')

            # Update item
            self.dynamodb.update_item(
                TableName=self.table_name,
                Key={'request_id': {'S': request_id}},
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values
            )

            logger.info(
                f"✅ Step status updated: {request_id} - {step_name} - {status.value}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to update step status: {e}")
            return False

    def update_result_data(self, request_id: str, result_s3_path: str) -> bool:
        """Update only the result_data field with S3 path"""
        try:
            logger.info(
                f"📝 Updating result data: {request_id} - {result_s3_path}")

            timestamp = datetime.now(timezone.utc).isoformat()

            # Update only the result_data field
            update_expression = "SET #analysis_result.#result_data = :result_data, #updated_at = :timestamp"

            expression_attribute_names = {
                '#analysis_result': 'analysis_result',
                '#result_data': 'result_data',
                '#updated_at': 'updated_at'
            }

            expression_attribute_values = {
                ':result_data': {'S': result_s3_path},
                ':timestamp': {'S': timestamp}
            }

            # Update item
            self.dynamodb.update_item(
                TableName=self.table_name,
                Key={'request_id': {'S': request_id}},
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values
            )

            logger.info(
                f"✅ Result data updated: {request_id} - {result_s3_path}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to update result data: {e}")
            return False

    def get_analysis_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of an analysis request"""
        try:
            logger.info(f"📊 Getting analysis status: {request_id}")

            response = self.dynamodb.get_item(
                TableName=self.table_name,
                Key={'request_id': {'S': request_id}}
            )

            if 'Item' not in response:
                logger.warning(f"⚠️ Analysis request not found: {request_id}")
                return None

            # Convert DynamoDB item to Python dict
            item = self._dynamodb_to_dict(response['Item'])

            logger.info(f"✅ Analysis status retrieved: {request_id}")
            return item

        except Exception as e:
            logger.error(f"❌ Failed to get analysis status: {e}")
            return None

    def list_analysis_requests(self, limit: int = 50) -> list:
        """List recent analysis requests"""
        try:
            logger.info(f"📋 Listing analysis requests (limit: {limit})")

            response = self.dynamodb.scan(
                TableName=self.table_name,
                Limit=limit,
                ProjectionExpression="request_id, research_data, created_at, updated_at, overall_status"
            )

            items = []
            for item in response.get('Items', []):
                items.append(self._dynamodb_to_dict(item))

            # Sort by created_at (newest first)
            items.sort(key=lambda x: x.get('created_at', ''), reverse=True)

            logger.info(f"✅ Listed {len(items)} analysis requests")
            return items

        except Exception as e:
            logger.error(f"❌ Failed to list analysis requests: {e}")
            return []

    def delete_analysis_request(self, request_id: str) -> bool:
        """Delete an analysis request tracking entry"""
        try:
            logger.info(f"🗑️ Deleting analysis request: {request_id}")

            self.dynamodb.delete_item(
                TableName=self.table_name,
                Key={'request_id': {'S': request_id}}
            )

            logger.info(f"✅ Analysis request deleted: {request_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to delete analysis request: {e}")
            return False

    def _dynamodb_to_dict(self, item: Dict) -> Dict[str, Any]:
        """Convert DynamoDB item to Python dictionary"""
        def convert_value(value):
            if 'S' in value:
                return value['S']
            elif 'N' in value:
                return float(value['N']) if '.' in value['N'] else int(value['N'])
            elif 'BOOL' in value:
                return value['BOOL']
            elif 'NULL' in value:
                return None
            elif 'L' in value:
                return [convert_value(v) for v in value['L']]
            elif 'M' in value:
                return {k: convert_value(v) for k, v in value['M'].items()}
            elif 'SS' in value:
                return set(value['SS'])
            elif 'NS' in value:
                return set([float(n) if '.' in n else int(n) for n in value['NS']])
            else:
                return value

        return {k: convert_value(v) for k, v in item.items()}

    def get_table_info(self) -> Dict[str, Any]:
        """Get information about the DynamoDB table"""
        try:
            response = self.dynamodb.describe_table(TableName=self.table_name)
            table_info = response['Table']

            return {
                'table_name': table_info['TableName'],
                'table_status': table_info['TableStatus'],
                'item_count': table_info.get('ItemCount', 0),
                'table_size_bytes': table_info.get('TableSizeBytes', 0),
                'billing_mode': table_info.get('BillingModeSummary', {}).get('BillingMode', 'UNKNOWN'),
                'creation_date': table_info.get('CreationDateTime', '').isoformat() if table_info.get('CreationDateTime') else None
            }

        except Exception as e:
            logger.error(f"❌ Failed to get table info: {e}")
            return {}


def create_dynamodb_tracker(table_name: Optional[str] = None) -> DynamoDBTracker:
    """Factory function to create DynamoDB tracker"""
    return DynamoDBTracker(table_name)


# Example usage
if __name__ == "__main__":
    # Test the DynamoDB tracker
    tracker = create_dynamodb_tracker()

    # Test creating an analysis request
    request_id = "test-request-123"
    research_data_path = "s3://my-bucket/research-data/interview-transcript.txt"

    print("🧪 Testing DynamoDB Tracker")
    print("=" * 50)

    # Create request
    success = tracker.create_analysis_request(request_id, research_data_path)
    print(f"Create request: {'✅' if success else '❌'}")

    # Update step status
    success = tracker.update_step_status(
        request_id, "chunking", StepStatus.PROCESSING, "Starting to chunk research data"
    )
    print(f"Update chunking to processing: {'✅' if success else '❌'}")

    # Update step status to completed
    success = tracker.update_step_status(
        request_id, "chunking", StepStatus.COMPLETED, "Chunking completed successfully"
    )
    print(f"Update chunking to completed: {'✅' if success else '❌'}")

    # Get status
    status = tracker.get_analysis_status(request_id)
    print(f"Get status: {'✅' if status else '❌'}")
    if status:
        print(f"Overall status: {status.get('overall_status')}")
        print(
            f"Steps: {list(status.get('analysis_result', {}).get('steps_status', {}).keys())}")

    # List requests
    requests = tracker.list_analysis_requests(10)
    print(f"List requests: ✅ Found {len(requests)} requests")

    # Get table info
    table_info = tracker.get_table_info()
    print(f"Table info: {'✅' if table_info else '❌'}")
    if table_info:
        print(f"Table: {table_info.get('table_name')}")
        print(f"Status: {table_info.get('table_status')}")
        print(f"Items: {table_info.get('item_count')}")

    print("🎉 DynamoDB Tracker test completed!")
