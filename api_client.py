"""
Design Analysis API Client
Python client for interacting with the Design Analysis API
"""

import requests
import json
from typing import Dict, List, Any


class DesignAnalysisClient:
    """Client for the Design Analysis API"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()

    def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    def analyze(
        self,
        research_data: str,
        implementation: str = "hybrid",
        include_metadata: bool = True
    ) -> Dict[str, Any]:
        """Analyze research data"""

        payload = {
            "research_data": research_data,
            "implementation": implementation,
            "include_metadata": include_metadata
        }

        response = self.session.post(
            f"{self.base_url}/analyze",
            json=payload
        )
        response.raise_for_status()
        return response.json()

    def get_result(self, request_id: str) -> Dict[str, Any]:
        """Get analysis result by request ID"""
        response = self.session.get(f"{self.base_url}/analyze/{request_id}")
        response.raise_for_status()
        return response.json()

    def get_implementations(self) -> Dict[str, Any]:
        """Get available implementation options"""
        response = self.session.get(f"{self.base_url}/implementations")
        response.raise_for_status()
        return response.json()

    def get_stats(self) -> Dict[str, Any]:
        """Get API usage statistics"""
        response = self.session.get(f"{self.base_url}/stats")
        response.raise_for_status()
        return response.json()

    def delete_result(self, request_id: str) -> Dict[str, Any]:
        """Delete analysis result by request ID"""
        response = self.session.delete(f"{self.base_url}/analyze/{request_id}")
        response.raise_for_status()
        return response.json()

    def analyze_batch(
        self,
        requests: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze multiple research data sets in batch"""

        response = self.session.post(
            f"{self.base_url}/analyze/batch",
            json=requests
        )
        response.raise_for_status()
        return response.json()

# Convenience functions


def analyze_research_data(
    research_data: str,
    implementation: str = "hybrid",
    base_url: str = "http://localhost:8000"
) -> Dict[str, Any]:
    """Quick function to analyze research data"""
    client = DesignAnalysisClient(base_url)
    return client.analyze(research_data, implementation)


def analyze_batch_data(
    research_data_list: List[str],
    implementation: str = "hybrid",
    base_url: str = "http://localhost:8000"
) -> Dict[str, Any]:
    """Quick function to analyze multiple research data sets"""
    client = DesignAnalysisClient(base_url)

    requests = [
        {
            "research_data": data,
            "implementation": implementation,
            "include_metadata": True
        }
        for data in research_data_list
    ]

    return client.analyze_batch(requests)


if __name__ == "__main__":
    # Example usage
    client = DesignAnalysisClient()

    # Check health
    print("Health check:")
    health = client.health_check()
    print(json.dumps(health, indent=2))

    # Get implementations
    print("\nAvailable implementations:")
    implementations = client.get_implementations()
    print(json.dumps(implementations, indent=2))

    # Analyze sample data
    sample_data = """
    User Interview Transcript:
    - "I just want to get this done quickly. I don't need all these fancy features."
    - "The interface is so cluttered, I can't find what I'm looking for."
    - "I spend more time figuring out how to use the tool than actually using it."
    """

    print("\nAnalyzing sample data...")
    result = client.analyze(sample_data, implementation="hybrid")

    print(f"Request ID: {result['request_id']}")
    print(f"Implementation: {result['implementation']}")
    print(f"Execution time: {result['execution_time']:.2f} seconds")
    print(f"Chunks generated: {len(result['chunks'])}")
    print(f"Insights generated: {len(result['insights'])}")
    print(f"Design principles generated: {len(result['design_principles'])}")

    # Get stats
    print("\nAPI Stats:")
    stats = client.get_stats()
    print(json.dumps(stats, indent=2))
