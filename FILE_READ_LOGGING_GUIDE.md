# File Read Logging Guide

This guide documents the comprehensive logging functionality that has been added to track file read operations when using S3 file paths in the analyze API.

## Overview

The Design Analysis API now includes detailed logging for all file read operations, providing visibility into:
- File upload processes
- S3 and local file loading operations
- Content decoding attempts
- File size and content validation
- Analysis execution flow
- Error handling and troubleshooting

## Logging Configuration

### Log File Location
- **Primary log file**: `api_s3.log` (in the project root)
- **Console output**: Logs are also displayed in the console
- **Log format**: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

### Log Levels
- **INFO**: Normal operations and successful file reads
- **WARNING**: Non-critical issues (e.g., encoding fallbacks)
- **ERROR**: Critical errors and failures

## Logging Features

### 1. Request Tracking
Each analysis request is assigned a unique ID and tracked throughout the entire process:

```
🚀 New analysis request received: 12345678-1234-1234-1234-123456789abc
📋 Request details - Implementation: hybrid, Include metadata: True
📁 S3 file path provided: design-analysis/research-data/abc123.txt
```

### 2. File Read Operations

#### S3 File Loading
When loading files from S3, the logs show:

```
☁️ S3: Starting to load research file: design-analysis/research-data/abc123.txt
📦 S3: Target bucket: my-design-analysis-bucket
🔍 S3: Attempting to get object from S3...
✅ S3: Successfully retrieved object from S3
📖 S3: Reading object content...
📊 S3: Raw content size: 2048 bytes
🔤 S3: Attempting UTF-8 decoding...
✅ S3: Successfully decoded with UTF-8. Content length: 2048 characters
📄 S3: Content preview (first 200 chars): Design Analysis Test Document...
```

#### Local File Loading
When loading files from local storage:

```
📂 Local: Starting to load research file: /path/to/file.txt
📁 Local: Resolved local path: /app/analysis_results/research_data/abc123.txt
✅ Local: File exists, reading content...
📏 Local: File size: 2048 bytes
✅ Local: Successfully read file. Content length: 2048 characters
📄 Local: Content preview (first 200 chars): Design Analysis Test Document...
```

### 3. Content Decoding
The system attempts multiple encoding strategies and logs each attempt:

```
🔤 S3: Attempting UTF-8 decoding...
⚠️ S3: UTF-8 decode failed: 'utf-8' codec can't decode byte 0xff. Trying alternative encodings...
🔤 S3: Trying latin-1 encoding...
✅ S3: Successfully decoded with latin-1. Content length: 2048 characters
```

### 4. Analysis Execution
The analysis process is tracked with timing information:

```
🔍 Starting analysis with implementation: hybrid
🔄 Running hybrid agentic analysis for request 12345678-1234-1234-1234-123456789abc
⏱️ Analysis completed in 15.23 seconds for request 12345678-1234-1234-1234-123456789abc
📋 Preparing response for request 12345678-1234-1234-1234-123456789abc
💾 Storing analysis result for request 12345678-1234-1234-1234-123456789abc
✅ Analysis result stored successfully for request 12345678-1234-1234-1234-123456789abc
🎉 Analysis request 12345678-1234-1234-1234-123456789abc completed successfully
```

### 5. Error Handling
Comprehensive error logging for troubleshooting:

```
❌ S3: File not found in S3: design-analysis/research-data/nonexistent.txt
❌ Local: File not found at path: /app/analysis_results/research_data/nonexistent.txt
❌ S3: Unicode decode error loading file: design-analysis/research-data/corrupted.txt
❌ Analysis failed for request 12345678-1234-1234-1234-123456789abc: File not found
```

## Usage Examples

### 1. Upload and Analyze File
```bash
# Upload a file
curl -X POST "http://localhost:8000/upload" \
  -F "file=@design_document.txt"

# Analyze using S3 file path
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "s3_file_path": "design-analysis/research-data/abc123.txt",
    "implementation": "hybrid",
    "include_metadata": true
  }'
```

### 2. Test Script
Run the provided test script to see logging in action:

```bash
python test_file_read_logging.py
```

This script will:
- Upload a test file
- Analyze it using S3 file path
- Perform a direct analysis for comparison
- Show the complete logging flow

## Log Analysis

### Key Log Entries to Monitor

1. **File Upload Success**:
   ```
   ✅ File uploaded successfully!
   📁 File ID: abc123-def456
   📂 S3 Path: design-analysis/research-data/abc123-def456.txt
   ```

2. **File Read Success**:
   ```
   ✅ S3: Successfully loaded S3 file. Content length: 2048 characters
   ✅ Local: Successfully read file. Content length: 2048 characters
   ```

3. **Analysis Completion**:
   ```
   🎉 Analysis request 12345678-1234-1234-1234-123456789abc completed successfully
   ```

4. **Performance Metrics**:
   ```
   ⏱️ Analysis completed in 15.23 seconds for request 12345678-1234-1234-1234-123456789abc
   ```

### Troubleshooting Common Issues

1. **File Not Found**:
   ```
   ❌ S3: File not found in S3: design-analysis/research-data/nonexistent.txt
   ```
   - Check if the file was uploaded successfully
   - Verify the S3 path is correct
   - Ensure the file exists in the specified bucket

2. **Encoding Issues**:
   ```
   ⚠️ S3: UTF-8 decode failed. Trying alternative encodings...
   ```
   - The system automatically tries multiple encodings
   - Check the original file encoding
   - Consider converting files to UTF-8 before upload

3. **S3 Access Issues**:
   ```
   ❌ S3: AWS ClientError loading file: Access Denied
   ```
   - Verify AWS credentials are configured correctly
   - Check S3 bucket permissions
   - Ensure the IAM role has read access to the bucket

## Configuration

### Environment Variables
The logging behavior can be controlled through environment variables:

```bash
# Log level (default: INFO)
export LOG_LEVEL=DEBUG

# Log file path (default: api_s3.log)
export LOG_FILE=my_app.log

# Enable/disable console logging (default: true)
export CONSOLE_LOGGING=true
```

### Customizing Log Format
To modify the log format, edit the logging configuration in `api_s3.py`:

```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_s3.log'),
        logging.StreamHandler()
    ]
)
```

## Best Practices

1. **Monitor Log Files**: Regularly check `api_s3.log` for errors and performance issues
2. **Set Up Log Rotation**: Configure log rotation to prevent log files from growing too large
3. **Use Request IDs**: Use the unique request IDs in logs to trace specific requests
4. **Monitor Performance**: Track execution times to identify slow operations
5. **Error Alerting**: Set up alerts for critical errors in production environments

## Integration with Monitoring Tools

The structured logging format makes it easy to integrate with monitoring tools:

- **ELK Stack**: Parse logs with Logstash
- **Splunk**: Use the structured format for analysis
- **CloudWatch**: Send logs to AWS CloudWatch for monitoring
- **Prometheus**: Extract metrics from log entries

## Conclusion

The comprehensive logging system provides complete visibility into file read operations, making it easier to:
- Debug issues with file uploads and analysis
- Monitor system performance
- Track user requests and usage patterns
- Ensure data integrity and proper error handling

For questions or issues with the logging system, refer to the log files or contact the development team.
