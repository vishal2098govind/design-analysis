#!/usr/bin/env python3
"""
Test script to verify local file storage functionality
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv
from api import storage, AnalysisRequest, AnalysisResponse
from hybrid_agentic_analysis import run_hybrid_agentic_analysis

# Load environment variables
load_dotenv()


def test_local_storage():
    """Test the local file storage functionality"""

    print("🧪 Testing Local File Storage...")
    print("=" * 40)

    # Test data
    sample_data = """
    User Interview Transcript:
    - "I just want to get this done quickly. I don't need all these fancy features."
    - "The interface is so cluttered, I can't find what I'm looking for."
    """

    try:
        # Test 1: Run analysis and save to file
        print("1️⃣ Running analysis and saving to file...")
        result = run_hybrid_agentic_analysis(sample_data)

        # Create a test response
        test_response = AnalysisResponse(
            request_id="test_123",
            status="completed",
            implementation="hybrid",
            timestamp="2024-01-01T12:00:00",
            chunks=result.get("chunks", []),
            inferences=result.get("inferences", []),
            patterns=result.get("patterns", []),
            insights=result.get("insights", []),
            design_principles=result.get("design_principles", []),
            metadata={"test": True},
            execution_time=1.5
        )

        # Save to file
        success = storage.save_analysis("test_123", test_response.dict())
        print(f"✅ Save result: {success}")

        # Test 2: Load from file
        print("\n2️⃣ Loading analysis from file...")
        loaded_result = storage.load_analysis("test_123")
        if loaded_result:
            print(
                f"✅ Loaded analysis with {len(loaded_result.get('chunks', []))} chunks")
            print(f"✅ Status: {loaded_result.get('status')}")
            print(f"✅ Implementation: {loaded_result.get('implementation')}")
        else:
            print("❌ Failed to load analysis")

        # Test 3: List analyses
        print("\n3️⃣ Listing all analyses...")
        analyses = storage.list_analyses()
        print(f"✅ Found {len(analyses)} analyses")
        for analysis in analyses:
            print(
                f"   - {analysis['request_id']}: {analysis['status']} ({analysis['implementation']})")

        # Test 4: Storage stats
        print("\n4️⃣ Storage statistics...")
        stats = storage.get_storage_stats()
        print(f"✅ Total analyses: {stats['total_analyses']}")
        print(f"✅ Total size: {stats['total_size_mb']} MB")
        print(f"✅ Storage path: {stats['storage_path']}")

        # Test 5: Delete analysis
        print("\n5️⃣ Deleting test analysis...")
        delete_success = storage.delete_analysis("test_123")
        print(f"✅ Delete result: {delete_success}")

        # Verify deletion
        deleted_result = storage.load_analysis("test_123")
        if deleted_result is None:
            print("✅ Analysis successfully deleted")
        else:
            print("❌ Analysis still exists after deletion")

        print("\n🎉 All local storage tests completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False


def check_storage_directory():
    """Check the storage directory structure"""
    print("\n📁 Storage Directory Structure:")
    print("=" * 40)

    storage_dir = Path("analysis_results")
    if storage_dir.exists():
        print(f"✅ Storage directory exists: {storage_dir.absolute()}")

        files = list(storage_dir.glob("*.json"))
        print(f"✅ Found {len(files)} analysis files")

        for file in files:
            size = file.stat().st_size
            print(f"   - {file.name}: {size} bytes")
    else:
        print("❌ Storage directory does not exist")


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("Please set your OpenAI API key in a .env file")
        print("Run: python setup_env.py")
    else:
        test_local_storage()
        check_storage_directory()
