"""
Design Analysis API
FastAPI application exposing the design analysis functionality
"""

import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uuid

# Import the analysis implementations
from openai_agentic_analysis import run_openai_agentic_analysis
from hybrid_agentic_analysis import run_hybrid_agentic_analysis
from agentic_analysis import run_agentic_analysis

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Design Analysis API",
    description="API for the Five Steps of Design Analysis using agentic AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Local file storage configuration
RESULTS_DIR = Path("analysis_results")
RESULTS_DIR.mkdir(exist_ok=True)


class AnalysisStorage:
    """Local file-based storage for analysis results"""

    def __init__(self, storage_dir: Path = RESULTS_DIR):
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(exist_ok=True)

    def save_analysis(self, request_id: str, result: dict) -> bool:
        """Save analysis result to local file"""
        try:
            file_path = self.storage_dir / f"{request_id}.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False, default=str)
            return True
        except Exception as e:
            print(f"Error saving analysis {request_id}: {e}")
            return False

    def load_analysis(self, request_id: str) -> Optional[dict]:
        """Load analysis result from local file"""
        try:
            file_path = self.storage_dir / f"{request_id}.json"
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            return None
        except Exception as e:
            print(f"Error loading analysis {request_id}: {e}")
            return None

    def delete_analysis(self, request_id: str) -> bool:
        """Delete analysis result from local file"""
        try:
            file_path = self.storage_dir / f"{request_id}.json"
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting analysis {request_id}: {e}")
            return False

    def list_analyses(self) -> List[Dict[str, Any]]:
        """List all stored analyses with metadata"""
        analyses = []
        try:
            for file_path in self.storage_dir.glob("*.json"):
                request_id = file_path.stem
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        analyses.append({
                            "request_id": request_id,
                            "timestamp": data.get("timestamp", "Unknown"),
                            "implementation": data.get("implementation", "Unknown"),
                            "status": data.get("status", "Unknown"),
                            "file_size": file_path.stat().st_size,
                            "created": datetime.fromtimestamp(file_path.stat().st_ctime).isoformat()
                        })
                except Exception as e:
                    print(f"Error reading analysis file {file_path}: {e}")
        except Exception as e:
            print(f"Error listing analyses: {e}")

        return sorted(analyses, key=lambda x: x["timestamp"], reverse=True)

    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        try:
            files = list(self.storage_dir.glob("*.json"))
            total_size = sum(f.stat().st_size for f in files)
            return {
                "total_analyses": len(files),
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "storage_path": str(self.storage_dir.absolute())
            }
        except Exception as e:
            print(f"Error getting storage stats: {e}")
            return {"error": str(e)}


# Initialize storage
storage = AnalysisStorage()

# Pydantic models for API requests and responses


class AnalysisRequest(BaseModel):
    research_data: str = Field(..., description="The research data to analyze")
    implementation: str = Field(
        default="hybrid",
        description="Implementation to use: 'openai', 'hybrid', or 'langchain'"
    )
    include_metadata: bool = Field(
        default=True,
        description="Whether to include analysis metadata"
    )


class AnalysisResponse(BaseModel):
    request_id: str = Field(..., description="Unique request identifier")
    status: str = Field(..., description="Analysis status")
    implementation: str = Field(..., description="Implementation used")
    timestamp: str = Field(..., description="Analysis timestamp")
    chunks: List[Dict[str, Any]] = Field(..., description="Generated chunks")
    inferences: List[Dict[str, Any]
                     ] = Field(..., description="Generated inferences")
    patterns: List[Dict[str, Any]
                   ] = Field(..., description="Generated patterns")
    insights: List[Dict[str, Any]
                   ] = Field(..., description="Generated insights")
    design_principles: List[Dict[str, Any]
                            ] = Field(..., description="Generated design principles")
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Analysis metadata")
    execution_time: Optional[float] = Field(
        None, description="Execution time in seconds")


class HealthResponse(BaseModel):
    status: str = Field(..., description="API health status")
    timestamp: str = Field(..., description="Current timestamp")
    openai_key_configured: bool = Field(...,
                                        description="Whether OpenAI API key is configured")


# Local file storage for analysis results
# analysis_results = {}  # Replaced with file-based storage


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Design Analysis API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        openai_key_configured=bool(os.getenv("OPENAI_API_KEY"))
    )


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_research_data(request: AnalysisRequest):
    """Analyze research data using the specified implementation"""

    # Validate OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(
            status_code=500,
            detail="OpenAI API key not configured"
        )

    # Validate implementation choice
    valid_implementations = ["openai", "hybrid", "langchain"]
    if request.implementation not in valid_implementations:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid implementation. Must be one of: {valid_implementations}"
        )

    # Generate request ID
    request_id = str(uuid.uuid4())

    try:
        import time
        start_time = time.time()

        # Run analysis based on implementation choice
        if request.implementation == "openai":
            result = run_openai_agentic_analysis(request.research_data)
        elif request.implementation == "hybrid":
            result = run_hybrid_agentic_analysis(request.research_data)
        else:  # langchain
            result = run_agentic_analysis(request.research_data)

        execution_time = time.time() - start_time

        # Prepare response
        response = AnalysisResponse(
            request_id=request_id,
            status="completed",
            implementation=request.implementation,
            timestamp=datetime.now().isoformat(),
            chunks=result.get("chunks", []),
            inferences=result.get("inferences", []),
            patterns=result.get("patterns", []),
            insights=result.get("insights", []),
            design_principles=result.get("design_principles", []),
            metadata=result.get(
                "analysis_metadata") if request.include_metadata else None,
            execution_time=execution_time
        )

        # Store result to local file
        storage.save_analysis(request_id, response.dict())

        return response

    except Exception as e:
        # Store error result to local file
        error_response = AnalysisResponse(
            request_id=request_id,
            status="error",
            implementation=request.implementation,
            timestamp=datetime.now().isoformat(),
            chunks=[],
            inferences=[],
            patterns=[],
            insights=[],
            design_principles=[],
            metadata={"error": str(e)},
            execution_time=time.time() - start_time if 'start_time' in locals() else None
        )
        storage.save_analysis(request_id, error_response.dict())
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analyze/{request_id}", response_model=AnalysisResponse)
async def get_analysis_result(request_id: str):
    """Get analysis result by request ID"""

    result = storage.load_analysis(request_id)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Analysis result not found"
        )

    return result


@app.get("/implementations")
async def get_implementations():
    """Get available implementation options"""
    return {
        "implementations": [
            {
                "id": "openai",
                "name": "OpenAI Agentic",
                "description": "Pure OpenAI implementation with native function calling",
                "features": ["Minimal dependencies", "Native function calling", "High reliability"]
            },
            {
                "id": "hybrid",
                "name": "Hybrid (LangGraph + OpenAI)",
                "description": "Combines LangGraph orchestration with OpenAI function calling",
                "features": ["LangGraph orchestration", "OpenAI function calling", "State management"]
            },
            {
                "id": "langchain",
                "name": "LangChain/LangGraph",
                "description": "Pure LangChain/LangGraph implementation",
                "features": ["Maximum flexibility", "Advanced features", "Complex workflows"]
            }
        ]
    }


@app.get("/stats")
async def get_stats():
    """Get API usage statistics"""
    analyses = storage.list_analyses()

    implementations_used = {"openai": 0, "hybrid": 0, "langchain": 0}
    total_execution_time = 0
    completed_analyses = 0

    for analysis in analyses:
        impl = analysis.get("implementation", "unknown")
        if impl in implementations_used:
            implementations_used[impl] += 1

        # Load full analysis for execution time
        full_analysis = storage.load_analysis(analysis["request_id"])
        if full_analysis and full_analysis.get("status") == "completed":
            execution_time = full_analysis.get("execution_time", 0)
            if execution_time:
                total_execution_time += execution_time
                completed_analyses += 1

    return {
        "total_analyses": len(analyses),
        "implementations_used": implementations_used,
        "average_execution_time": total_execution_time / completed_analyses if completed_analyses > 0 else 0,
        "storage_stats": storage.get_storage_stats()
    }


@app.delete("/analyze/{request_id}")
async def delete_analysis_result(request_id: str):
    """Delete analysis result by request ID"""

    if not storage.delete_analysis(request_id):
        raise HTTPException(
            status_code=404,
            detail="Analysis result not found"
        )

    return {"message": "Analysis result deleted successfully"}


@app.get("/analyses")
async def list_analyses():
    """List all stored analyses"""
    return {
        "analyses": storage.list_analyses(),
        "storage_stats": storage.get_storage_stats()
    }


@app.post("/analyze/batch")
async def analyze_batch(requests: List[AnalysisRequest]):
    """Analyze multiple research data sets in batch"""

    results = []
    for request in requests:
        try:
            # Generate request ID
            request_id = str(uuid.uuid4())

            import time
            start_time = time.time()

            # Run analysis
            if request.implementation == "openai":
                result = run_openai_agentic_analysis(request.research_data)
            elif request.implementation == "hybrid":
                result = run_hybrid_agentic_analysis(request.research_data)
            else:
                result = run_agentic_analysis(request.research_data)

            execution_time = time.time() - start_time

            # Prepare response
            response = AnalysisResponse(
                request_id=request_id,
                status="completed",
                implementation=request.implementation,
                timestamp=datetime.now().isoformat(),
                chunks=result.get("chunks", []),
                inferences=result.get("inferences", []),
                patterns=result.get("patterns", []),
                insights=result.get("insights", []),
                design_principles=result.get("design_principles", []),
                metadata=result.get(
                    "analysis_metadata") if request.include_metadata else None,
                execution_time=execution_time
            )

            # Store result to local file
            storage.save_analysis(request_id, response.dict())
            results.append(response)

        except Exception as e:
            # Store error result to local file
            error_request_id = str(uuid.uuid4())
            error_response = {
                "request_id": error_request_id,
                "status": "failed",
                "error": str(e),
                "implementation": request.implementation,
                "timestamp": datetime.now().isoformat()
            }
            storage.save_analysis(error_request_id, error_response)
            results.append(error_response)

    return {"results": results}

# Error handlers


@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Resource not found", "detail": str(exc)}


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"error": "Internal server error", "detail": str(exc)}

if __name__ == "__main__":
    import uvicorn

    # Check if OpenAI API key is configured
    if not os.getenv("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY not found in environment variables")
        print("Please set your OpenAI API key before running the API")

    # Run the API server
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
