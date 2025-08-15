# 📁 File Upload and S3 Path Analysis

**Handle Large Research Data with File Uploads**

This guide shows you how to use the enhanced API that supports both direct text input and file uploads for large research data like interview transcripts.

## 🎯 Why File Uploads?

### **Benefits for Large Data:**
- 📏 **No Size Limits** - Handle large interview transcripts
- 🚀 **Better Performance** - Avoid HTTP request size limits
- 💾 **Persistent Storage** - Files stored in S3/local storage
- 🔄 **Reusable Data** - Analyze the same file multiple times
- 📊 **File Management** - List, delete, and manage uploaded files

### **Use Cases:**
- **Interview Transcripts** - Large text files with multiple interviews
- **Research Documents** - PDFs converted to text
- **Survey Responses** - CSV files with qualitative data
- **Focus Group Notes** - Markdown files with detailed notes

## 🚀 How It Works

### **Two Input Methods:**

#### **1. Direct Text Input** (Small Data)
```json
{
  "research_data": "User interview: I want a simple interface...",
  "implementation": "hybrid"
}
```

#### **2. S3 File Path** (Large Data)
```json
{
  "s3_file_path": "design-analysis/research-data/abc123-def4-5678.txt",
  "implementation": "hybrid"
}
```

## 📋 Step-by-Step Usage

### **Step 1: Upload Your File**

#### **Using cURL:**
```bash
curl -X POST "http://localhost:8000/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@interview_transcript.txt"
```

#### **Using Python:**
```python
import requests

# Upload file
with open('interview_transcript.txt', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8000/upload', files=files)

upload_result = response.json()
print(f"File uploaded: {upload_result['s3_path']}")
```

#### **Response:**
```json
{
  "file_id": "abc123-def4-5678-9012",
  "s3_path": "design-analysis/research-data/abc123-def4-5678-9012.txt",
  "file_size": 45678,
  "upload_time": "2024-01-15T14:30:25.123Z",
  "message": "File uploaded successfully. Use s3_file_path: 'design-analysis/research-data/abc123-def4-5678-9012.txt' in analysis request"
}
```

### **Step 2: Analyze Using S3 Path**

#### **Using cURL:**
```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "s3_file_path": "design-analysis/research-data/abc123-def4-5678-9012.txt",
    "implementation": "hybrid"
  }'
```

#### **Using Python:**
```python
import requests

# Analyze using S3 path
analysis_request = {
    "s3_file_path": "design-analysis/research-data/abc123-def4-5678-9012.txt",
    "implementation": "hybrid"
}

response = requests.post('http://localhost:8000/analyze', json=analysis_request)
result = response.json()
print(f"Analysis completed: {result['request_id']}")
```

## 📁 File Management

### **List Uploaded Files**

#### **Get All Files:**
```bash
curl "http://localhost:8000/files"
```

#### **Response:**
```json
{
  "files": [
    {
      "file_id": "abc123-def4-5678-9012",
      "original_filename": "interview_transcript.txt",
      "s3_path": "design-analysis/research-data/abc123-def4-5678-9012.txt",
      "file_size": 45678,
      "upload_time": "2024-01-15T14:30:25.123Z",
      "file_extension": ".txt",
      "created": "2024-01-15T14:30:25.123Z",
      "storage_type": "s3"
    }
  ],
  "total_count": 1,
  "storage_type": "s3"
}
```

### **Delete a File**

#### **Delete by File ID:**
```bash
curl -X DELETE "http://localhost:8000/files/abc123-def4-5678-9012"
```

## 🔧 API Endpoints

### **File Upload Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/upload` | POST | Upload research file |
| `/files` | GET | List uploaded files |
| `/files/{file_id}` | DELETE | Delete a file |

### **Analysis Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/analyze` | POST | Analyze research data (text or S3 path) |
| `/analyze/{request_id}` | GET | Get analysis result |
| `/analyses` | GET | List all analyses |

## 📝 File Format Support

### **Supported File Types:**
- ✅ **`.txt`** - Plain text files
- ✅ **`.json`** - JSON files
- ✅ **`.md`** - Markdown files
- ✅ **`.csv`** - CSV files

### **File Size Limits:**
- **Maximum Size**: 50MB per file
- **Recommended**: Under 10MB for best performance

## 🎯 Complete Example

### **1. Upload Interview Transcript**
```python
import requests

# Upload the file
with open('user_interviews.txt', 'rb') as f:
    files = {'file': f}
    upload_response = requests.post('http://localhost:8000/upload', files=files)

if upload_response.status_code == 200:
    upload_data = upload_response.json()
    s3_path = upload_data['s3_path']
    print(f"✅ File uploaded: {s3_path}")
else:
    print(f"❌ Upload failed: {upload_response.text}")
```

### **2. Analyze the File**
```python
# Analyze using the S3 path
analysis_request = {
    "s3_file_path": s3_path,
    "implementation": "hybrid",
    "include_metadata": True
}

analysis_response = requests.post('http://localhost:8000/analyze', json=analysis_request)

if analysis_response.status_code == 200:
    result = analysis_response.json()
    print(f"✅ Analysis completed!")
    print(f"📊 Insights found: {len(result['insights'])}")
    print(f"🎯 Design principles: {len(result['design_principles'])}")
else:
    print(f"❌ Analysis failed: {analysis_response.text}")
```

### **3. Check Results**
```python
# Get the analysis result
request_id = result['request_id']
result_response = requests.get(f'http://localhost:8000/analyze/{request_id}')

if result_response.status_code == 200:
    final_result = result_response.json()
    print("📋 Analysis Results:")
    for insight in final_result['insights']:
        print(f"  • {insight['headline']}")
```

## 🔍 File Content Examples

### **Interview Transcript Format:**
```txt
User Interview Transcript - Product Feedback Session

Interviewer: Sarah Johnson
Participant: Alex Chen
Date: January 15, 2024

Interviewer: "Can you tell me about your experience with our project management tool?"

Alex: "I spend more time setting up the tool than actually managing my projects. 
I just want to quickly add a task, assign it to someone, and see the status. 
But instead, I have to navigate through multiple screens, set up custom fields, 
and configure workflows that I'll never use."

Interviewer: "What would make this easier for you?"

Alex: "If the tool could understand what I'm trying to do and just do it. 
I don't want to learn complex workflows - I want to get my work done."

[Continue with more interview content...]
```

### **Survey Response Format:**
```json
{
  "survey_id": "UX-2024-001",
  "responses": [
    {
      "question": "What frustrates you most about our interface?",
      "answer": "The complexity of the setup process. I just want to start working immediately.",
      "user_id": "user_123",
      "timestamp": "2024-01-15T10:30:00Z"
    },
    {
      "question": "What would make your workflow more efficient?",
      "answer": "A simpler way to create and assign tasks without all the configuration steps.",
      "user_id": "user_456",
      "timestamp": "2024-01-15T11:15:00Z"
    }
  ]
}
```

## 🚨 Error Handling

### **Common Upload Errors:**

#### **File Too Large:**
```json
{
  "detail": "File too large. Maximum size: 50MB"
}
```

#### **Invalid File Type:**
```json
{
  "detail": "File type not allowed. Allowed types: ['.txt', '.json', '.md', '.csv']"
}
```

#### **File Not Found (Analysis):**
```json
{
  "detail": "File not found: design-analysis/research-data/invalid-path.txt"
}
```

## 💡 Best Practices

### **File Preparation:**
1. **Clean Text** - Remove formatting artifacts
2. **Consistent Format** - Use consistent structure
3. **UTF-8 Encoding** - Ensure proper character encoding
4. **Reasonable Size** - Keep files under 10MB for best performance

### **Analysis Workflow:**
1. **Upload First** - Upload file before analysis
2. **Save S3 Path** - Store the returned S3 path
3. **Reuse Files** - Use the same file for multiple analyses
4. **Clean Up** - Delete files when no longer needed

### **Storage Management:**
1. **Monitor Usage** - Check file storage regularly
2. **Archive Old Files** - Move old files to cheaper storage
3. **Set Lifecycle Policies** - Automate file cleanup
4. **Backup Important Files** - Keep copies of critical data

## 🔧 Troubleshooting

### **Upload Issues:**
- **File Size**: Check if file is under 50MB
- **File Type**: Ensure file extension is supported
- **Network**: Check internet connection for large files
- **Permissions**: Verify API has write access to storage

### **Analysis Issues:**
- **File Path**: Verify S3 path is correct
- **File Content**: Check if file contains readable text
- **Encoding**: Ensure file uses UTF-8 encoding
- **Storage**: Verify file exists in storage

---

## 🎉 Benefits Summary

### **For Large Data:**
- ✅ **No Size Limits** - Handle massive interview transcripts
- ✅ **Better Performance** - Avoid HTTP request timeouts
- ✅ **Persistent Storage** - Files stored securely
- ✅ **Reusable** - Analyze same file multiple times

### **For Workflow:**
- ✅ **File Management** - Upload, list, delete files
- ✅ **Flexible Input** - Text or file path
- ✅ **Error Handling** - Clear error messages
- ✅ **Monitoring** - Track file usage and storage

Your API now supports both small text inputs and large file uploads for comprehensive research analysis! 🚀
