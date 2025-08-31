#!/usr/bin/env python3
"""
Design Analysis API with S3 Storage Support
FastAPI application with configurable storage (local or S3) and DynamoDB tracking
"""

from dynamodb_tracker import StepStatus
from s3_storage import create_s3_storage, S3Storage
from agentic_analysis import run_agentic_analysis
from hybrid_agentic_analysis import run_hybrid_agentic_analysis
from openai_agentic_analysis import run_openai_agentic_analysis

# Import DynamoDB tracker
try:
    from dynamodb_tracker import create_dynamodb_tracker
    DYNAMODB_AVAILABLE = True
except ImportError:
    DYNAMODB_AVAILABLE = False
    print("⚠️ DynamoDB tracker not available - status tracking disabled")

import os
import json
import argparse
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator, model_validator
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_s3.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import the analysis implementations

# Import storage implementations

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

# DynamoDB configuration
DYNAMODB_TABLE_NAME = os.getenv(
    "DYNAMODB_TABLE_NAME", "design-analysis-tracking")

# Server configuration
DEFAULT_PORT = int(os.getenv("API_PORT", "8000"))
DEFAULT_HOST = os.getenv("API_HOST", "0.0.0.0")

# Local file storage configuration
RESULTS_DIR = Path("analysis_results")
RESULTS_DIR.mkdir(exist_ok=True)

# Initialize DynamoDB tracker if available
tracker = None
if DYNAMODB_AVAILABLE:
    try:
        tracker = create_dynamodb_tracker(DYNAMODB_TABLE_NAME)
        logger.info("✅ DynamoDB tracker initialized")
    except Exception as e:
        logger.warning(f"⚠️ Failed to initialize DynamoDB tracker: {e}")
        tracker = None


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

    def save_research_file(self, s3_path: str, content: bytes, metadata: dict) -> bool:
        """Save a research file to local storage"""
        try:
            # Extract file ID and extension from s3_path
            file_id = s3_path.split("/")[-1].split(".")[0]
            file_extension = Path(s3_path).suffix
            local_path = self.storage_dir / \
                "research_data" / f"{file_id}{file_extension}"
            local_path.parent.mkdir(exist_ok=True)

            with open(local_path, "wb") as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error saving research file {s3_path}: {e}")
            return False

    def load_research_file(self, s3_path: str) -> Optional[str]:
        """Load a research file from local storage"""
        logger.info(f"📂 Local: Starting to load research file: {s3_path}")
        try:
            # Extract file ID and extension from s3_path
            file_id = s3_path.split("/")[-1].split(".")[0]
            file_extension = Path(s3_path).suffix
            local_path = self.storage_dir / \
                "research_data" / f"{file_id}{file_extension}"

            logger.info(f"📁 Local: Resolved local path: {local_path}")

            if local_path.exists():
                logger.info(f"✅ Local: File exists, reading content...")
                file_size = local_path.stat().st_size
                logger.info(f"📏 Local: File size: {file_size} bytes")

                with open(local_path, "r", encoding="utf-8") as f:
                    content = f.read()

                logger.info(
                    f"✅ Local: Successfully read file. Content length: {len(content)} characters")
                logger.info(
                    f"📄 Local: Content preview (first 200 chars): {content[:200]}...")
                return content
            else:
                logger.warning(
                    f"⚠️ Local: File not found at path: {local_path}")
                return None
        except UnicodeDecodeError as e:
            logger.error(
                f"❌ Local: Unicode decode error loading file {s3_path}: {e}")
            return None
        except Exception as e:
            logger.error(
                f"❌ Local: Error loading research file {s3_path}: {e}")
            return None

    def list_research_files(self) -> List[Dict[str, Any]]:
        """List all uploaded research files"""
        files = []
        try:
            research_dir = self.storage_dir / "research_data"
            if research_dir.exists():
                for file_path in research_dir.glob("*"):
                    if file_path.is_file():
                        files.append({
                            "file_id": file_path.stem,
                            "original_filename": file_path.name,
                            "s3_path": str(file_path),
                            "file_size": file_path.stat().st_size,
                            "upload_time": datetime.fromtimestamp(file_path.stat().st_ctime).isoformat(),
                            "file_extension": file_path.suffix,
                            "created": datetime.fromtimestamp(file_path.stat().st_ctime).isoformat(),
                            "storage_type": "local"
                        })
            return files
        except Exception as e:
            print(f"Error listing research files: {e}")
            return []

    def delete_research_file(self, s3_path: str) -> bool:
        """Delete a research file from local storage"""
        try:
            # Extract file ID and extension from s3_path
            file_id = s3_path.split("/")[-1].split(".")[0]
            file_extension = Path(s3_path).suffix
            local_path = self.storage_dir / \
                "research_data" / f"{file_id}{file_extension}"
            if local_path.exists():
                local_path.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting research file {s3_path}: {e}")
            return False


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
    research_data: Optional[str] = Field(
        None, description="Research data to analyze (for small data)")
    s3_file_path: Optional[str] = Field(
        None, description="S3 path to research data file (for large data)")
    implementation: str = Field(
        default="hybrid", description="Analysis implementation to use")
    include_metadata: bool = Field(
        default=True, description="Include analysis metadata in response")

    @field_validator('research_data', 's3_file_path')
    @classmethod
    def validate_input(cls, v, info):
        """Ensure either research_data or s3_file_path is provided, but not both"""
        if info.field_name == 's3_file_path' and v and info.data.get('research_data'):
            raise ValueError(
                "Provide either research_data or s3_file_path, not both")
        return v

    @model_validator(mode='after')
    def validate_required_fields(self):
        """Ensure at least one input method is provided"""
        if not self.research_data and not self.s3_file_path:
            raise ValueError(
                "Either research_data or s3_file_path must be provided")
        return self


class FileUploadResponse(BaseModel):
    file_id: str
    s3_path: str
    file_size: int
    upload_time: str
    message: str


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
        "description": "API for the Five Steps of Design Analysis using agentic AI with configurable storage",
        "storage_type": STORAGE_TYPE,
        "features": [
            "Direct text analysis",
            "File upload and S3 path analysis",
            "Multiple analysis implementations",
            "Configurable storage (local/S3)"
        ],
        "endpoints": {
            "upload": "/upload - Upload research files",
            "analyze": "/analyze - Analyze research data",
            "files": "/files - List uploaded files",
            "docs": "/docs - API documentation"
        },
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


@app.post("/upload", response_model=FileUploadResponse)
async def upload_research_file(file: UploadFile = File(...)):
    """Upload research data file to S3"""

    # Validate file type
    allowed_extensions = ['.txt', '.json', '.md', '.csv']
    file_extension = Path(file.filename).suffix.lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {allowed_extensions}"
        )

    # Check file size (max 50MB)
    max_size = 50 * 1024 * 1024  # 50MB
    if file.size and file.size > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: 50MB"
        )

    try:
        # Generate file ID
        file_id = str(uuid.uuid4())

        # Read file content
        content = await file.read()

        # Create file metadata
        file_metadata = {
            "file_id": file_id,
            "original_filename": file.filename,
            "file_size": len(content),
            "content_type": file.content_type,
            "upload_time": datetime.now().isoformat(),
            "file_extension": file_extension
        }

        # Save file to storage
        if STORAGE_TYPE == "s3":
            # Save to S3
            s3_path = f"{S3_PREFIX}/research-data/{file_id}{file_extension}"
            success = storage.save_research_file(
                s3_path, content, file_metadata)
            if not success:
                raise HTTPException(
                    status_code=500, detail="Failed to upload file to S3")
        else:
            # Save to local storage
            local_path = RESULTS_DIR / "research_data" / \
                f"{file_id}{file_extension}"
            local_path.parent.mkdir(exist_ok=True)
            with open(local_path, "wb") as f:
                f.write(content)
            s3_path = str(local_path)  # Use local path for consistency

        return FileUploadResponse(
            file_id=file_id,
            s3_path=s3_path,
            file_size=len(content),
            upload_time=file_metadata["upload_time"],
            message=f"File uploaded successfully. Use s3_file_path: '{s3_path}' in analysis request"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_research_data(request: AnalysisRequest):
    """Analyze research data using the specified implementation"""

    # Generate request ID
    request_id = str(uuid.uuid4())
    logger.info(f"🚀 New analysis request received: {request_id}")
    logger.info(
        f"📋 Request details - Implementation: {request.implementation}, Include metadata: {request.include_metadata}")

    if request.s3_file_path:
        logger.info(f"📁 S3 file path provided: {request.s3_file_path}")
    elif request.research_data:
        logger.info(
            f"📝 Direct research data provided (length: {len(request.research_data)} chars)")

    # Validate OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        logger.error(
            f"❌ OpenAI API key not configured for request {request_id}")
        raise HTTPException(
            status_code=500,
            detail="OpenAI API key not configured"
        )

    # Validate implementation choice
    valid_implementations = ["openai", "hybrid", "langchain"]
    if request.implementation not in valid_implementations:
        logger.error(
            f"❌ Invalid implementation '{request.implementation}' for request {request_id}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid implementation. Must be one of: {valid_implementations}"
        )

    try:
        # Get research data from appropriate source
        research_data = None
        if request.research_data:
            logger.info(
                f"📝 Using direct research data for request {request_id}")
            research_data = request.research_data
            logger.info(
                f"📊 Research data length: {len(research_data)} characters")
        elif request.s3_file_path:
            logger.info(
                f"📁 Loading file from path: {request.s3_file_path} for request {request_id}")

            # Load data from S3 or local file
            if STORAGE_TYPE == "s3":
                logger.info(
                    f"☁️ Loading from S3 storage: {request.s3_file_path}")
                try:
                    research_data = storage.load_research_file(
                        request.s3_file_path)
                    if research_data:
                        logger.info(
                            f"✅ Successfully loaded S3 file. Content length: {len(research_data)} characters")
                        logger.info(
                            f"📄 File content preview (first 200 chars): {research_data[:200]}...")
                    else:
                        logger.warning(
                            f"⚠️ S3 file load returned None for path: {request.s3_file_path}")
                except Exception as e:
                    logger.error(
                        f"❌ Failed to load S3 file {request.s3_file_path}: {str(e)}")
                    raise HTTPException(
                        status_code=500, detail=f"Failed to load S3 file: {str(e)}")
            else:
                # Load from local file
                logger.info(
                    f"📂 Loading from local file: {request.s3_file_path}")
                file_path = Path(request.s3_file_path)
                if file_path.exists():
                    try:
                        logger.info(f"📖 Reading local file: {file_path}")
                        file_size = file_path.stat().st_size
                        logger.info(f"📏 File size: {file_size} bytes")

                        with open(file_path, "r", encoding="utf-8") as f:
                            research_data = f.read()

                        logger.info(
                            f"✅ Successfully read local file. Content length: {len(research_data)} characters")
                        logger.info(
                            f"📄 File content preview (first 200 chars): {research_data[:200]}...")

                    except UnicodeDecodeError as e:
                        logger.error(
                            f"❌ Unicode decode error reading file {file_path}: {str(e)}")
                        raise HTTPException(
                            status_code=500, detail=f"File encoding error: {str(e)}")
                    except Exception as e:
                        logger.error(
                            f"❌ Error reading local file {file_path}: {str(e)}")
                        raise HTTPException(
                            status_code=500, detail=f"File read error: {str(e)}")
                else:
                    logger.error(f"❌ Local file not found: {file_path}")
                    raise HTTPException(
                        status_code=404, detail=f"File not found: {request.s3_file_path}")

        if not research_data:
            logger.error(
                f"❌ No research data available for request {request_id}")
            raise HTTPException(
                status_code=400, detail="No research data available")

        logger.info(
            f"📊 Final research data length for analysis: {len(research_data)} characters")

        # Prepare S3 path for DynamoDB tracking
        research_data_s3_path = None
        if request.s3_file_path:
            research_data_s3_path = request.s3_file_path
        elif STORAGE_TYPE == "s3":
            # If using S3 storage but no S3 path provided, create one
            research_data_s3_path = f"{S3_PREFIX}/research-data/{request_id}.txt"

        # Create initial DynamoDB entry for tracking
        if tracker:
            try:
                tracker.create_analysis_request(
                    request_id, research_data_s3_path, request.implementation)
                logger.info(
                    f"✅ Created DynamoDB tracking entry for request {request_id}")
            except Exception as e:
                logger.error(
                    f"❌ Failed to create DynamoDB tracking entry: {e}")

        # Start analysis asynchronously
        logger.info(
            f"🚀 Starting asynchronous analysis for request {request_id}")

        # Use asyncio.create_task to run analysis in background
        import asyncio
        asyncio.create_task(
            run_analysis_async(
                request_id,
                research_data,
                request.implementation,
                research_data_s3_path,
                request.include_metadata
            )
        )

        # Return immediately with request ID
        logger.info(
            f"✅ Analysis triggered successfully for request {request_id}")
        return {
            "request_id": request_id,
            "status": "started",
            "message": "Analysis has been started. Use the request_id to monitor progress.",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(
            f"❌ Failed to start analysis for request {request_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start analysis: {str(e)}"
        )


async def run_analysis_async(request_id: str, research_data: str, implementation: str, research_data_s3_path: str, include_metadata: bool):
    """Run analysis asynchronously in the background"""

    logger.info(f"🔄 Starting background analysis for request {request_id}")

    try:
        import time
        start_time = time.time()

        # Run analysis based on implementation choice
        logger.info(
            f"🔍 Running analysis with implementation: {implementation}")

        if implementation == "openai":
            logger.info(
                f"🤖 Running OpenAI agentic analysis for request {request_id}")
            result = run_openai_agentic_analysis(research_data)
        elif implementation == "hybrid":
            logger.info(
                f"🔄 Running hybrid agentic analysis for request {request_id}")
            result = run_hybrid_agentic_analysis(
                research_data, request_id, research_data_s3_path, save_to_s3=True)
        else:  # langchain
            logger.info(
                f"🔗 Running LangChain agentic analysis for request {request_id}")
            result = run_agentic_analysis(research_data)

        execution_time = time.time() - start_time
        logger.info(
            f"⏱️ Analysis completed in {execution_time:.2f} seconds for request {request_id}")

        # Prepare response
        logger.info(f"📋 Preparing response for request {request_id}")
        response = AnalysisResponse(
            request_id=request_id,
            status="completed",
            implementation=implementation,
            timestamp=datetime.now().isoformat(),
            chunks=result.get("chunks", []),
            inferences=result.get("inferences", []),
            patterns=result.get("patterns", []),
            insights=result.get("insights", []),
            design_principles=result.get("design_principles", []),
            metadata=result.get(
                "analysis_metadata") if include_metadata else None,
            execution_time=execution_time
        )

        # Store result
        logger.info(f"💾 Storing analysis result for request {request_id}")
        storage_success = storage.save_analysis(request_id, response.dict())
        if storage_success:
            logger.info(
                f"✅ Analysis result stored successfully for request {request_id}")

            # Update DynamoDB with the result S3 path if using hybrid implementation
            if implementation == "hybrid" and tracker and request_id:
                try:
                    # Get the actual S3 path where the result was stored using storage system
                    result_s3_path = storage._get_object_key(
                        request_id, "analysis")

                    # Update DynamoDB with the result S3 path (only the result_data field)
                    tracker.update_result_data(request_id, result_s3_path)
                    logger.info(
                        f"✅ DynamoDB updated with result S3 path: {result_s3_path}")
                except Exception as e:
                    logger.error(
                        f"❌ Failed to update DynamoDB with result S3 path: {e}")
        else:
            logger.warning(
                f"⚠️ Failed to store analysis result for request {request_id}")

        logger.info(f"🎉 Analysis request {request_id} completed successfully")

    except Exception as e:
        logger.error(f"❌ Analysis failed for request {request_id}: {str(e)}")

        # Update DynamoDB status to failed
        if tracker:
            try:
                tracker.update_overall_status(request_id, "failed")
                logger.info(
                    f"✅ Updated DynamoDB status to failed for request {request_id}")
            except Exception as db_error:
                logger.error(f"❌ Failed to update DynamoDB status: {db_error}")

        # Store error result
        error_response = AnalysisResponse(
            request_id=request_id,
            status="error",
            implementation=implementation,
            timestamp=datetime.now().isoformat(),
            chunks=[],
            inferences=[],
            patterns=[],
            insights=[],
            design_principles=[],
            metadata={"error": str(e)},
            execution_time=0.0
        )

        logger.info(f"💾 Storing error result for request {request_id}")
        storage.save_analysis(request_id, error_response.dict())


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


@app.get("/files")
async def list_research_files():
    """List all uploaded research files"""
    try:
        if STORAGE_TYPE == "s3":
            files = storage.list_research_files()
        else:
            # For local storage, list files in research_data directory
            research_dir = RESULTS_DIR / "research_data"
            files = []
            if research_dir.exists():
                for file_path in research_dir.glob("*"):
                    if file_path.is_file():
                        files.append({
                            "file_id": file_path.stem,
                            "original_filename": file_path.name,
                            "s3_path": str(file_path),
                            "file_size": file_path.stat().st_size,
                            "upload_time": datetime.fromtimestamp(file_path.stat().st_ctime).isoformat(),
                            "file_extension": file_path.suffix,
                            "created": datetime.fromtimestamp(file_path.stat().st_ctime).isoformat(),
                            "storage_type": "local"
                        })

        return {
            "files": files,
            "total_count": len(files),
            "storage_type": STORAGE_TYPE
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to list files: {str(e)}")


@app.delete("/files/{file_id}")
async def delete_research_file(file_id: str):
    """Delete a research file"""
    try:
        if STORAGE_TYPE == "s3":
            # Find the file by ID and delete it
            files = storage.list_research_files()
            file_to_delete = None
            for file in files:
                if file["file_id"] == file_id:
                    file_to_delete = file
                    break

            if not file_to_delete:
                raise HTTPException(
                    status_code=404, detail=f"File with ID {file_id} not found")

            success = storage.delete_research_file(file_to_delete["s3_path"])
        else:
            # For local storage, find and delete the file
            research_dir = RESULTS_DIR / "research_data"
            file_found = False
            for file_path in research_dir.glob("*"):
                if file_path.stem == file_id:
                    file_path.unlink()
                    file_found = True
                    break

            if not file_found:
                raise HTTPException(
                    status_code=404, detail=f"File with ID {file_id} not found")
            success = True

        if success:
            return {"message": f"File {file_id} deleted successfully"}
        else:
            raise HTTPException(
                status_code=500, detail="Failed to delete file")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete file: {str(e)}")


@app.get("/analysis/status/{request_id}")
async def get_analysis_status(request_id: str):
    """Get the current status of an analysis request from DynamoDB"""
    if not tracker:
        raise HTTPException(
            status_code=503,
            detail="DynamoDB tracking not available"
        )

    try:
        status = tracker.get_analysis_status(request_id)
        if not status:
            raise HTTPException(
                status_code=404,
                detail=f"Analysis request {request_id} not found"
            )

        return {
            "request_id": request_id,
            "status": status
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get analysis status for {request_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get analysis status: {str(e)}"
        )


@app.get("/analysis/requests")
async def list_analysis_requests(limit: int = 50):
    """List recent analysis requests from DynamoDB"""
    if not tracker:
        raise HTTPException(
            status_code=503,
            detail="DynamoDB tracking not available"
        )

    try:
        requests = tracker.list_analysis_requests(limit)
        return {
            "requests": requests,
            "total": len(requests),
            "limit": limit
        }
    except Exception as e:
        logger.error(f"❌ Failed to list analysis requests: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list analysis requests: {str(e)}"
        )


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


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Design Analysis API with S3 Storage Support")
    parser.add_argument("--port", "-p", type=int, default=DEFAULT_PORT,
                        help=f"Port to run the server on (default: {DEFAULT_PORT})")
    parser.add_argument("--host", type=str, default=DEFAULT_HOST,
                        help=f"Host to bind the server to (default: {DEFAULT_HOST})")
    parser.add_argument("--reload", "-r", action="store_true", default=True,
                        help="Enable auto-reload on code changes (default: True)")
    parser.add_argument("--no-reload", action="store_true",
                        help="Disable auto-reload on code changes")
    return parser.parse_args()


if __name__ == "__main__":
    import uvicorn

    # Parse command line arguments
    args = parse_arguments()

    # Determine reload setting
    reload_enabled = args.reload and not args.no_reload

    print("🚀 Starting Design Analysis API with S3 Storage Support...")
    print(f"📦 Storage Type: {STORAGE_TYPE}")
    print(f"🌐 Server: {args.host}:{args.port}")
    print(f"🔄 Auto-reload: {'Enabled' if reload_enabled else 'Disabled'}")

    if STORAGE_TYPE == "s3":
        print(f"🌍 S3 Region: {S3_REGION}")
        print(f"📁 S3 Prefix: {S3_PREFIX}")
    else:
        print(f"📁 Local Path: {RESULTS_DIR}")

    uvicorn.run(
        "api_s3:app",
        host=args.host,
        port=args.port,
        reload=reload_enabled
    )
