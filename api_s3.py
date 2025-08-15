#!/usr/bin/env python3
"""
Design Analysis API with S3 Storage Support
FastAPI application with configurable storage (local or S3)
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

# Import storage implementations
from s3_storage import create_s3_storage, S3Storage

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Design Analysis API with S3 Storage",
    description="API for the Five Steps of Design Analysis using agentic AI with configurable storage",
    version="2.0.0",
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

# Storage configuration
STORAGE_TYPE = os.getenv("STORAGE_TYPE", "local").lower()  # "local" or "s3"
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_REGION = os.getenv("S3_REGION", "us-east-1")
S3_PREFIX = os.getenv("S3_PREFIX", "design-analysis")

# Local file storage configuration
RESULTS_DIR = Path("analysis_results")
RESULTS_DIR.mkdir(exist_ok=True)


class LocalAnalysisStorage:
    """Local file storage implementation"""

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
                            "created": datetime.fromtimestamp(file_path.stat().st_ctime).isoformat(),
                            "storage_type": "local"
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
                "storage_path": str(self.storage_dir.absolute()),
                "storage_type": "local"
            }
        except Exception as e:
            print(f"Error getting storage stats: {e}")
            return {"error": str(e)}


# Initialize storage based on configuration
def initialize_storage():
    """Initialize storage based on environment configuration"""
    if STORAGE_TYPE == "s3":
        try:
            print(f"🔗 Initializing S3 storage...")
            storage = create_s3_storage(
                bucket_name=S3_BUCKET_NAME,
                region=S3_REGION,
                prefix=S3_PREFIX
            )
            print(f"✅ S3 storage initialized successfully!")
            print(f"📦 Bucket: {storage.bucket_name}")
            print(f"🌍 Region: {storage.region}")
            return storage
        except Exception as e:
            print(f"❌ Failed to initialize S3 storage: {e}")
            print("🔄 Falling back to local storage...")
            return LocalAnalysisStorage()
    else:
        print(f"📁 Using local storage: {RESULTS_DIR}")
        return LocalAnalysisStorage()


# Initialize storage
storage = initialize_storage()


# Pydantic models
class AnalysisRequest(BaseModel):
    research_data: str = Field(..., description="Research data to analyze")
    implementation: str = Field(
        default="hybrid", description="Analysis implementation to use")
    include_metadata: bool = Field(
        default=True, description="Include analysis metadata in response")


class AnalysisResponse(BaseModel):
    request_id: str
    status: str
    implementation: str
    timestamp: str
    chunks: List[Dict[str, Any]]
    inferences: List[Dict[str, Any]]
    patterns: List[Dict[str, Any]]
    insights: List[Dict[str, Any]]
    design_principles: List[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]] = None
    execution_time: float


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    storage_type: str
    storage_info: Dict[str, Any]
    openai_key_configured: bool


class StatsResponse(BaseModel):
    total_analyses: int
    implementations_used: Dict[str, int]
    average_execution_time: float
    storage_stats: Dict[str, Any]
    storage_type: str


# API endpoints
@app.get("/")
async def root():
    """API information"""
    return {
        "name": "Design Analysis API with S3 Storage",
        "version": "2.0.0",
        "description": "API for the Five Steps of Design Analysis using agentic AI",
        "storage_type": STORAGE_TYPE,
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    storage_info = storage.get_bucket_info() if STORAGE_TYPE == "s3" else {
        "storage_path": str(RESULTS_DIR)}

    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        storage_type=STORAGE_TYPE,
        storage_info=storage_info,
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

        # Store result
        storage.save_analysis(request_id, response.dict())

        return response

    except Exception as e:
        # Store error result
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
            execution_time=0.0
        )
        storage.save_analysis(request_id, error_response.dict())

        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@app.get("/analyze/{request_id}", response_model=AnalysisResponse)
async def get_analysis_result(request_id: str):
    """Get analysis result by request ID"""
    result = storage.load_analysis(request_id)

    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Analysis with ID {request_id} not found"
        )

    return AnalysisResponse(**result)


@app.delete("/analyze/{request_id}")
async def delete_analysis(request_id: str):
    """Delete analysis result by request ID"""
    success = storage.delete_analysis(request_id)

    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Analysis with ID {request_id} not found"
        )

    return {"message": f"Analysis {request_id} deleted successfully"}


@app.get("/implementations")
async def get_implementations():
    """Get available analysis implementations"""
    return {
        "implementations": [
            {
                "name": "openai",
                "description": "Pure OpenAI implementation using native function calling",
                "features": ["Fast", "Simple", "Direct OpenAI integration"]
            },
            {
                "name": "hybrid",
                "description": "Hybrid implementation combining LangGraph orchestration with OpenAI function calling",
                "features": ["Best of both worlds", "Structured workflow", "Flexible"]
            },
            {
                "name": "langchain",
                "description": "Full LangChain/LangGraph implementation",
                "features": ["Complete LangChain ecosystem", "Advanced features", "Extensible"]
            }
        ]
    }


@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get API statistics"""
    analyses = storage.list_analyses()

    # Calculate statistics
    implementations_used = {}
    total_execution_time = 0
    completed_analyses = 0

    for analysis in analyses:
        impl = analysis.get("implementation", "unknown")
        implementations_used[impl] = implementations_used.get(impl, 0) + 1

        # Try to get execution time from full analysis
        if analysis.get("status") == "completed":
            full_analysis = storage.load_analysis(analysis["request_id"])
            if full_analysis and "execution_time" in full_analysis:
                total_execution_time += full_analysis["execution_time"]
                completed_analyses += 1

    avg_execution_time = total_execution_time / \
        completed_analyses if completed_analyses > 0 else 0

    return StatsResponse(
        total_analyses=len(analyses),
        implementations_used=implementations_used,
        average_execution_time=round(avg_execution_time, 2),
        storage_stats=storage.get_storage_stats(),
        storage_type=STORAGE_TYPE
    )


@app.get("/analyses")
async def list_analyses():
    """List all stored analyses"""
    analyses = storage.list_analyses()

    return {
        "analyses": analyses,
        "total_count": len(analyses),
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

            # Store result
            storage.save_analysis(request_id, response.dict())
            results.append(response)

        except Exception as e:
            # Store error result
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
                execution_time=0.0
            )
            storage.save_analysis(request_id, error_response.dict())
            results.append(error_response)

    return {
        "batch_results": results,
        "total_processed": len(requests),
        "successful": len([r for r in results if r.status == "completed"]),
        "failed": len([r for r in results if r.status == "error"])
    }


@app.get("/storage/info")
async def get_storage_info():
    """Get detailed storage information"""
    if STORAGE_TYPE == "s3":
        storage_info = storage.get_bucket_info()
    else:
        storage_info = {
            "storage_type": "local",
            "storage_path": str(RESULTS_DIR),
            "total_files": len(list(RESULTS_DIR.glob("*.json")))
        }

    return {
        "storage_type": STORAGE_TYPE,
        "configuration": {
            "s3_bucket_name": S3_BUCKET_NAME,
            "s3_region": S3_REGION,
            "s3_prefix": S3_PREFIX
        },
        "storage_info": storage_info,
        "stats": storage.get_storage_stats()
    }


if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting Design Analysis API with S3 Storage Support...")
    print(f"📦 Storage Type: {STORAGE_TYPE}")
    if STORAGE_TYPE == "s3":
        print(f"🌍 S3 Region: {S3_REGION}")
        print(f"📁 S3 Prefix: {S3_PREFIX}")
    else:
        print(f"📁 Local Path: {RESULTS_DIR}")

    uvicorn.run(
        "api_s3:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
