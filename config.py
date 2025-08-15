"""
Configuration settings for the Agentic Design Analysis system
"""

import os
from typing import Dict, Any


class Config:
    """Configuration class for the design analysis system"""

    # OpenAI Settings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.1"))

    # Analysis Settings
    MAX_CHUNKS_PER_ANALYSIS = int(os.getenv("MAX_CHUNKS_PER_ANALYSIS", "50"))
    CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.7"))
    MAX_INSIGHTS_PER_PATTERN = int(os.getenv("MAX_INSIGHTS_PER_PATTERN", "3"))

    # Agent Settings
    CHUNKING_CONFIDENCE_WEIGHT = 0.3
    INFERENCE_CONFIDENCE_WEIGHT = 0.25
    PATTERN_STRENGTH_WEIGHT = 0.2
    INSIGHT_IMPACT_WEIGHT = 0.15
    PRINCIPLE_PRIORITY_WEIGHT = 0.1

    # Output Settings
    INCLUDE_CONFIDENCE_SCORES = True
    INCLUDE_EVIDENCE_TRACES = True
    INCLUDE_METADATA = True

    @classmethod
    def get_agent_config(cls) -> Dict[str, Any]:
        """Get configuration for agent behavior"""
        return {
            "max_chunks": cls.MAX_CHUNKS_PER_ANALYSIS,
            "confidence_threshold": cls.CONFIDENCE_THRESHOLD,
            "max_insights": cls.MAX_INSIGHTS_PER_PATTERN,
            "include_confidence": cls.INCLUDE_CONFIDENCE_SCORES,
            "include_evidence": cls.INCLUDE_EVIDENCE_TRACES,
            "include_metadata": cls.INCLUDE_METADATA
        }

    @classmethod
    def get_llm_config(cls) -> Dict[str, Any]:
        """Get configuration for LLM settings"""
        return {
            "model": cls.OPENAI_MODEL,
            "temperature": cls.TEMPERATURE,
            "api_key": cls.OPENAI_API_KEY
        }

    @classmethod
    def validate_config(cls) -> bool:
        """Validate that all required configuration is present"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")

        if cls.TEMPERATURE < 0 or cls.TEMPERATURE > 1:
            raise ValueError("TEMPERATURE must be between 0 and 1")

        if cls.CONFIDENCE_THRESHOLD < 0 or cls.CONFIDENCE_THRESHOLD > 1:
            raise ValueError("CONFIDENCE_THRESHOLD must be between 0 and 1")

        return True
