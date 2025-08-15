# Hybrid Agentic Design Analysis

An implementation of the Five Steps of Design Analysis using **LangChain/LangGraph orchestration** combined with **OpenAI's native agentic framework** and function calling.

## Overview

This project implements the design analysis methodology outlined in `Requirements.md` using a **hybrid approach** that combines:
- **LangGraph**: For workflow orchestration and state management
- **OpenAI's Function Calling**: For reliable, structured outputs
- **LangChain**: For additional utilities and integrations

## The Five Steps

### 1. **Chunk** - Break the information down
- **Node**: `chunk_research_data`
- **Function**: `create_chunk` (OpenAI native)
- **Orchestration**: LangGraph
- **Purpose**: Divides research data into small, meaningful pieces
- **Output**: Structured chunks with metadata (type, confidence, tags)

### 2. **Infer** - Ask what each chunk means
- **Node**: `infer_meanings`
- **Function**: `create_inference` (OpenAI native)
- **Orchestration**: LangGraph
- **Purpose**: Interprets chunks and extracts multiple meanings
- **Output**: Inferences with confidence scores and reasoning

### 3. **Relate** - Find patterns across meanings
- **Node**: `relate_patterns`
- **Function**: `create_pattern` (OpenAI native)
- **Orchestration**: LangGraph
- **Purpose**: Groups related inferences and identifies themes
- **Output**: Patterns with strength scores and evidence counts

### 4. **Explain** - Dig into why patterns matter
- **Node**: `explain_insights`
- **Function**: `create_insight` (OpenAI native)
- **Orchestration**: LangGraph
- **Purpose**: Generates insights that challenge assumptions
- **Output**: Bold insights with impact scores

### 5. **Activate** - Turn insights into design direction
- **Node**: `activate_design_principles`
- **Function**: `create_design_principle` (OpenAI native)
- **Orchestration**: LangGraph
- **Purpose**: Converts insights into actionable design principles
- **Output**: Design principles with priority and feasibility scores

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# Add your OpenAI API key to environment
export OPENAI_API_KEY=your_api_key_here
```

## Usage

### Direct Usage

```python
from hybrid_agentic_analysis import run_hybrid_agentic_analysis

# Your research data
research_data = """
User Interview Transcript:
- "I just want to get this done quickly. I don't need all these fancy features."
- "The interface is so cluttered, I can't find what I'm looking for."
- "I spend more time figuring out how to use the tool than actually using it."
"""

# Run the analysis
result = run_hybrid_agentic_analysis(research_data)

# Access results
print("Chunks:", len(result['chunks']))
print("Inferences:", len(result['inferences']))
print("Patterns:", len(result['patterns']))
print("Insights:", len(result['insights']))
print("Design Principles:", len(result['design_principles']))
```

### API Usage

#### Start the API Server

```bash
# Run the API server
python api.py

# Or using uvicorn directly
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

#### Using the Python Client

```python
from api_client import DesignAnalysisClient

# Initialize client
client = DesignAnalysisClient("http://localhost:8000")

# Analyze research data
result = client.analyze(
    research_data="Your research data here...",
    implementation="hybrid"  # or "openai" or "langchain"
)

print(f"Request ID: {result['request_id']}")
print(f"Execution time: {result['execution_time']:.2f} seconds")
print(f"Insights: {len(result['insights'])}")
```

#### Using HTTP Requests

```bash
# Analyze research data
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "research_data": "User Interview Transcript:\n- \"I just want to get this done quickly.\"",
    "implementation": "hybrid",
    "include_metadata": true
  }'

# Get analysis result by ID
curl "http://localhost:8000/analyze/{request_id}"

# Get available implementations
curl "http://localhost:8000/implementations"

# Get API stats
curl "http://localhost:8000/stats"
```

## Storage Options

The system supports both local file storage and AWS S3 storage for production deployments.

### Local File Storage (Default)

The API automatically saves all analysis results to local JSON files in the `analysis_results/` directory. This provides:

- **Persistence**: Results survive server restarts
- **Historical Tracking**: All analyses are stored with timestamps
- **Easy Access**: Results can be accessed via API or directly from files
- **Storage Statistics**: Track total analyses and storage usage

#### Local Storage Features

- **Automatic Saving**: Every analysis is automatically saved to a JSON file
- **File Naming**: Files are named using the request ID (e.g., `abc123.json`)
- **Metadata**: Each file includes creation time, implementation used, and execution stats
- **Error Handling**: Failed analyses are also saved with error information
- **Cleanup**: Use the DELETE endpoint to remove unwanted analyses

#### Local Storage Location

```
analysis_results/
├── abc123-def4-5678.json    # Analysis result
├── xyz789-abc1-2345.json    # Another analysis
└── ...
```

### AWS S3 Storage (Production)

For production deployments, the system supports AWS S3 storage with automatic bucket management, encryption, and cost optimization.

#### S3 Storage Features

- **🔒 Scalability**: Handle unlimited analysis results
- **🌍 Global Access**: Access data from anywhere
- **💰 Cost-Effective**: Pay only for what you use
- **🛡️ Security**: Built-in encryption and access controls
- **📊 Analytics**: Built-in monitoring and metrics
- **🔄 Reliability**: 99.999999999% durability
- **⚡ Performance**: Fast access with CDN integration

#### S3 Configuration

Set environment variables to enable S3 storage:

```bash
# Storage configuration
export STORAGE_TYPE="s3"
export S3_BUCKET_NAME="my-design-analysis-bucket"
export S3_REGION="us-east-1"
export S3_PREFIX="design-analysis"

# AWS credentials
export AWS_ACCESS_KEY_ID="your_access_key"
export AWS_SECRET_ACCESS_KEY="your_secret_key"
```

#### S3 Folder Structure

```
design-analysis/
├── analysis/
│   ├── 2024/
│   │   ├── 01/
│   │   │   ├── abc123-def4-5678.json
│   │   │   └── xyz789-abc1-2345.json
│   │   └── 02/
│   │       └── def456-ghi7-8901.json
│   └── 2023/
│       └── 12/
│           └── old-analysis.json
└── metadata/
    └── storage-stats.json
```

#### S3 Automatic Features

- **🔒 Encryption**: AES-256 server-side encryption
- **📝 Versioning**: Data protection and recovery
- **💰 Lifecycle Policies**: Cost optimization
  - 30 days → Standard-IA
  - 90 days → Glacier
  - 365 days → Expiration
- **📁 Organized Structure**: Year/month folder organization

### Storage Statistics

The `/stats` endpoint provides storage information:

```json
{
  "total_analyses": 15,
  "implementations_used": {
    "hybrid": 10,
    "openai": 3,
    "langchain": 2
  },
  "average_execution_time": 8.5,
  "storage_stats": {
    "total_analyses": 15,
    "total_size_bytes": 2048576,
    "total_size_mb": 1.95,
    "storage_type": "local"  // or "s3"
  },
  "storage_type": "local"  // or "s3"
}
```

### Storage API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/storage/info` | Get detailed storage information |
| `GET` | `/stats` | Get storage statistics |
| `GET` | `/analyses` | List all stored analyses |

### Migration from Local to S3

To migrate existing local data to S3:

```python
from s3_storage import create_s3_storage
import json
from pathlib import Path

# Create S3 storage
s3_storage = create_s3_storage()

# Migrate local analyses
local_dir = Path("analysis_results")
for file_path in local_dir.glob("*.json"):
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    request_id = file_path.stem
    s3_storage.save_analysis(request_id, data)
    print(f"Migrated: {request_id}")
```

For detailed S3 setup instructions, see [S3_SETUP_GUIDE.md](S3_SETUP_GUIDE.md).

## API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API information |
| `GET` | `/health` | Health check |
| `POST` | `/analyze` | Analyze research data |
| `GET` | `/analyze/{request_id}` | Get analysis result from local storage |
| `GET` | `/analyses` | List all stored analyses |
| `DELETE` | `/analyze/{request_id}` | Delete analysis result from local storage |
| `POST` | `/analyze/batch` | Batch analysis (saved to local files) |
| `GET` | `/implementations` | Get available implementations |
| `GET` | `/stats` | Get API usage statistics and storage info |

### Request/Response Models

#### Analysis Request
```json
{
  "research_data": "string",
  "implementation": "hybrid|openai|langchain",
  "include_metadata": true
}
```

#### Analysis Response
```json
{
  "request_id": "uuid",
  "status": "completed",
  "implementation": "hybrid",
  "timestamp": "2024-01-01T00:00:00Z",
  "chunks": [...],
  "inferences": [...],
  "patterns": [...],
  "insights": [...],
  "design_principles": [...],
  "metadata": {...},
  "execution_time": 12.34
}
```

## Architecture

### Hybrid Framework

This implementation combines the best of both worlds:

1. **LangGraph Orchestration**: Manages workflow state and flow
2. **OpenAI Function Calling**: Ensures reliable, structured outputs
3. **LangChain Integration**: Provides additional utilities and message handling

### LangGraph Workflow

```python
def create_hybrid_agentic_graph():
    workflow = StateGraph(DesignAnalysisState)
    
    # Add nodes (each using OpenAI function calling internally)
    workflow.add_node("chunk", chunk_research_data)
    workflow.add_node("infer", infer_meanings)
    workflow.add_node("relate", relate_patterns)
    workflow.add_node("explain", explain_insights)
    workflow.add_node("activate", activate_design_principles)
    
    # Define the flow
    workflow.set_entry_point("chunk")
    workflow.add_edge("chunk", "infer")
    workflow.add_edge("infer", "relate")
    workflow.add_edge("relate", "explain")
    workflow.add_edge("explain", "activate")
    workflow.add_edge("activate", END)
    
    return workflow.compile()
```

### OpenAI Function Calling

Each node uses OpenAI's native function calling:

```python
def chunk_research_data(state: DesignAnalysisState) -> DesignAnalysisState:
    # Use OpenAI's native function calling
    response = openai_client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=messages,
        tools=get_chunking_functions(),
        tool_choice={"type": "function", "function": {"name": "create_chunk"}},
        temperature=0.1
    )
    
    # Process structured output
    chunks = []
    for choice in response.choices:
        if choice.message.tool_calls:
            for tool_call in choice.message.tool_calls:
                if tool_call.function.name == "create_chunk":
                    chunk_data = json.loads(tool_call.function.arguments)
                    chunks.append(chunk_data)
    
    return {**state, "chunks": chunks}
```

### State Management

LangGraph manages the state throughout the workflow:

```python
class DesignAnalysisState(TypedDict):
    research_data: str
    chunks: List[Dict[str, Any]]
    inferences: List[Dict[str, Any]]
    patterns: List[Dict[str, Any]]
    insights: List[Dict[str, Any]]
    design_principles: List[Dict[str, Any]]
    current_step: str
    messages: List[Any]
    analysis_metadata: Dict[str, Any]
```

## Data Models

### Chunk
```python
{
    "id": "unique_identifier",
    "content": "chunk content",
    "source": "research_data",
    "type": "quote|observation|fact|behavior|pain_point",
    "confidence": 0.85,
    "tags": ["user_feedback", "efficiency"]
}
```

### Inference
```python
{
    "chunk_id": "reference_to_chunk",
    "meanings": ["meaning1", "meaning2"],
    "importance": "why this matters",
    "context": "broader context",
    "confidence": 0.88,
    "reasoning": "explanation of reasoning"
}
```

### Pattern
```python
{
    "name": "User Efficiency Needs",
    "description": "Users consistently seek efficiency",
    "related_inferences": ["chunk_id1", "chunk_id2"],
    "themes": ["efficiency", "speed"],
    "strength": 0.89,
    "evidence_count": 3
}
```

### Insight
```python
{
    "headline": "USERS PRIORITIZE SPEED OVER FEATURES",
    "explanation": "Detailed explanation",
    "pattern_id": "User Efficiency Needs",
    "non_consensus": True,
    "first_principles": True,
    "impact_score": 0.93,
    "supporting_evidence": ["evidence1", "evidence2"]
}
```

### Design Principle
```python
{
    "principle": "The system should prioritize speed and efficiency",
    "insight_id": "USERS PRIORITIZE SPEED OVER FEATURES",
    "action_verbs": ["prioritize", "simplify"],
    "design_direction": "Focus on reducing steps",
    "priority": 0.93,
    "feasibility": 0.85
}
```

## Features

### Hybrid Capabilities

- **LangGraph Orchestration**: Sophisticated workflow management
- **OpenAI Function Calling**: Reliable, structured outputs
- **State Persistence**: Full audit trail and state management
- **Message Handling**: LangChain message types for consistency

### Analysis Quality

- **Confidence Scoring**: Each output includes confidence levels
- **Evidence Tracking**: Patterns and insights link back to source data
- **Impact Assessment**: Insights and principles are scored for impact
- **Feasibility Evaluation**: Design principles include feasibility scores

### Framework Benefits

- **Best of Both Worlds**: LangGraph orchestration + OpenAI reliability
- **Structured Workflows**: Clear state management and flow control
- **Reliable Outputs**: Function calling ensures structured responses
- **Extensible**: Easy to add new nodes or modify existing ones

### API Features

- **RESTful API**: Full REST API with FastAPI
- **Interactive Documentation**: Auto-generated Swagger docs at `/docs`
- **Multiple Implementations**: Choose between OpenAI, Hybrid, or LangChain
- **Batch Processing**: Analyze multiple datasets at once
- **Result Storage**: Store and retrieve analysis results
- **Health Monitoring**: API health checks and statistics

## Example Output

```
=== Hybrid Agentic Design Analysis Results ===

CHUNKS:
- [QUOTE] "I just want to get this done quickly. I don't need all these fancy features."
  Tags: user_feedback, efficiency | Confidence: 0.85
- [OBSERVATION] The interface is so cluttered, I can't find what I'm looking for.
  Tags: user_feedback, interface | Confidence: 0.88

INFERENCES:
- Chunk chunk_abc123: Users prioritize speed and efficiency
  Importance: Reveals user behavior patterns and needs
  Confidence: 0.92
- Chunk chunk_def456: Users struggle with complexity
  Importance: Indicates need for simplicity in design
  Confidence: 0.89

PATTERNS:
- User Efficiency Needs
  Description: Users consistently seek ways to complete tasks more efficiently
  Strength: 0.89 | Evidence: 3 pieces

INSIGHTS:
- USERS PRIORITIZE SPEED OVER FEATURES
  Explanation: Despite having access to advanced features, users consistently choose the fastest path
  Impact Score: 0.93
  Non-consensus: True | First-principles: True

DESIGN PRINCIPLES:
- The system should prioritize speed and efficiency over feature complexity
  Direction: Focus on reducing steps and eliminating unnecessary complexity
  Priority: 0.93 | Feasibility: 0.85
  Action Verbs: prioritize, simplify, streamline

Analysis completed using Hybrid Agentic Framework!
Framework: Hybrid (LangGraph + OpenAI Agentic)
Orchestration: LangGraph
Function Calling: OpenAI Native
```

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `OPENAI_MODEL`: Model to use (default: gpt-4-turbo-preview)
- `TEMPERATURE`: LLM temperature (default: 0.1)

### Model Settings

The implementation uses:
- **Model**: `gpt-4-turbo-preview`
- **Temperature**: `0.1` (for consistent outputs)
- **Tool Choice**: Forced function execution
- **Orchestration**: LangGraph state management

### API Configuration

- **Host**: `0.0.0.0` (all interfaces)
- **Port**: `8000`
- **CORS**: Enabled for all origins
- **Documentation**: Available at `/docs` and `/redoc`

## Framework Comparison

| Feature | Hybrid (LangGraph + OpenAI) | Pure OpenAI | Pure LangChain |
|---------|------------------------------|-------------|----------------|
| **Orchestration** | LangGraph (Advanced) | Manual | LangGraph |
| **Function Calling** | OpenAI Native | OpenAI Native | LangChain wrappers |
| **State Management** | LangGraph State | Manual | LangGraph State |
| **Reliability** | High | High | Variable |
| **Complexity** | Medium | Low | High |
| **Flexibility** | High | Medium | High |

## Implementation Options

This repository provides three different implementations:

1. **`openai_agentic_analysis.py`** - Pure OpenAI implementation
2. **`hybrid_agentic_analysis.py`** - Hybrid (LangGraph + OpenAI) implementation
3. **`agentic_analysis.py`** - Pure LangChain/LangGraph implementation

Choose based on your needs:
- **Pure OpenAI**: Simple, minimal dependencies
- **Hybrid**: Best of both worlds (recommended)
- **Pure LangChain**: Maximum flexibility and features

## Deployment

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY=your_api_key_here

# Run the API
python api.py
```

### Production Deployment

```bash
# Using Docker (create Dockerfile)
docker build -t design-analysis-api .
docker run -p 8000:8000 -e OPENAI_API_KEY=your_key design-analysis-api

# Using uvicorn directly
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
