"""
OpenAI Agentic Design Analysis Implementation
Uses OpenAI's official agentic framework with function calling and structured outputs
"""

import os
import json
from typing import Dict, List, Any
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field
import uuid

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Pydantic models for structured outputs


class Chunk(BaseModel):
    id: str = Field(description="Unique identifier for the chunk")
    content: str = Field(description="The actual chunk content")
    source: str = Field(description="Where this chunk came from")
    type: str = Field(
        description="Type: quote, observation, fact, behavior, pain_point")
    confidence: float = Field(description="Confidence level (0-1)")
    tags: List[str] = Field(description="Tags to categorize this chunk")


class Inference(BaseModel):
    chunk_id: str = Field(description="Reference to the source chunk")
    meanings: List[str] = Field(
        description="Multiple interpretations of the chunk")
    importance: str = Field(description="Why this chunk matters")
    context: str = Field(
        description="What this tells us about the broader context")
    confidence: float = Field(description="Confidence level (0-1)")
    reasoning: str = Field(description="Explanation of the reasoning process")


class Pattern(BaseModel):
    name: str = Field(description="Clear, meaningful name for the pattern")
    description: str = Field(description="What this pattern represents")
    related_inferences: List[str] = Field(
        description="List of inference IDs that form this pattern")
    themes: List[str] = Field(description="Key themes in this pattern")
    strength: float = Field(description="Strength of the pattern (0-1)")
    evidence_count: int = Field(
        description="Number of pieces of evidence supporting this pattern")


class Insight(BaseModel):
    headline: str = Field(
        description="Bold, short headline capturing the insight")
    explanation: str = Field(description="Detailed explanation of the insight")
    pattern_id: str = Field(description="Reference to the source pattern")
    non_consensus: bool = Field(
        description="Whether this challenges common assumptions")
    first_principles: bool = Field(
        description="Whether this reflects fundamental truths")
    impact_score: float = Field(
        description="Potential impact of this insight (0-1)")
    supporting_evidence: List[str] = Field(
        description="Evidence supporting this insight")


class DesignPrinciple(BaseModel):
    principle: str = Field(description="Clear, actionable design principle")
    insight_id: str = Field(description="Reference to the source insight")
    action_verbs: List[str] = Field(
        description="Key action verbs in the principle")
    design_direction: str = Field(description="Specific direction for design")
    priority: float = Field(description="Priority level (0-1)")
    feasibility: float = Field(
        description="Feasibility of implementation (0-1)")

# OpenAI Function Definitions


def get_chunking_functions():
    """Define functions for the chunking agent"""
    return [
        {
            "type": "function",
            "function": {
                "name": "create_chunk",
                "description": "Create a chunk from research data",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "The chunk content"
                        },
                        "source": {
                            "type": "string",
                            "description": "Source of the chunk"
                        },
                        "type": {
                            "type": "string",
                            "enum": ["quote", "observation", "fact", "behavior", "pain_point"],
                            "description": "Type of chunk"
                        },
                        "confidence": {
                            "type": "number",
                            "description": "Confidence level (0-1)"
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Tags to categorize this chunk"
                        }
                    },
                    "required": ["content", "source", "type", "confidence", "tags"]
                }
            }
        }
    ]


def get_inference_functions():
    """Define functions for the inference agent"""
    return [
        {
            "type": "function",
            "function": {
                "name": "create_inference",
                "description": "Create an inference from a chunk",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "chunk_id": {
                            "type": "string",
                            "description": "Reference to the source chunk"
                        },
                        "meanings": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Multiple interpretations of the chunk"
                        },
                        "importance": {
                            "type": "string",
                            "description": "Why this chunk matters"
                        },
                        "context": {
                            "type": "string",
                            "description": "What this tells us about the broader context"
                        },
                        "confidence": {
                            "type": "number",
                            "description": "Confidence level (0-1)"
                        },
                        "reasoning": {
                            "type": "string",
                            "description": "Explanation of the reasoning process"
                        }
                    },
                    "required": ["chunk_id", "meanings", "importance", "context", "confidence", "reasoning"]
                }
            }
        }
    ]


def get_pattern_functions():
    """Define functions for the pattern agent"""
    return [
        {
            "type": "function",
            "function": {
                "name": "create_pattern",
                "description": "Create a pattern from related inferences",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Clear, meaningful name for the pattern"
                        },
                        "description": {
                            "type": "string",
                            "description": "What this pattern represents"
                        },
                        "related_inferences": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of inference IDs that form this pattern"
                        },
                        "themes": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Key themes in this pattern"
                        },
                        "strength": {
                            "type": "number",
                            "description": "Strength of the pattern (0-1)"
                        },
                        "evidence_count": {
                            "type": "integer",
                            "description": "Number of pieces of evidence supporting this pattern"
                        }
                    },
                    "required": ["name", "description", "related_inferences", "themes", "strength", "evidence_count"]
                }
            }
        }
    ]


def get_insight_functions():
    """Define functions for the insight agent"""
    return [
        {
            "type": "function",
            "function": {
                "name": "create_insight",
                "description": "Create an insight from a pattern",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "headline": {
                            "type": "string",
                            "description": "Bold, short headline capturing the insight"
                        },
                        "explanation": {
                            "type": "string",
                            "description": "Detailed explanation of the insight"
                        },
                        "pattern_id": {
                            "type": "string",
                            "description": "Reference to the source pattern"
                        },
                        "non_consensus": {
                            "type": "boolean",
                            "description": "Whether this challenges common assumptions"
                        },
                        "first_principles": {
                            "type": "boolean",
                            "description": "Whether this reflects fundamental truths"
                        },
                        "impact_score": {
                            "type": "number",
                            "description": "Potential impact of this insight (0-1)"
                        },
                        "supporting_evidence": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Evidence supporting this insight"
                        }
                    },
                    "required": ["headline", "explanation", "pattern_id", "non_consensus", "first_principles", "impact_score", "supporting_evidence"]
                }
            }
        }
    ]


def get_design_principle_functions():
    """Define functions for the design principle agent"""
    return [
        {
            "type": "function",
            "function": {
                "name": "create_design_principle",
                "description": "Create a design principle from an insight",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "principle": {
                            "type": "string",
                            "description": "Clear, actionable design principle"
                        },
                        "insight_id": {
                            "type": "string",
                            "description": "Reference to the source insight"
                        },
                        "action_verbs": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Key action verbs in the principle"
                        },
                        "design_direction": {
                            "type": "string",
                            "description": "Specific direction for design"
                        },
                        "priority": {
                            "type": "number",
                            "description": "Priority level (0-1)"
                        },
                        "feasibility": {
                            "type": "number",
                            "description": "Feasibility of implementation (0-1)"
                        }
                    },
                    "required": ["principle", "insight_id", "action_verbs", "design_direction", "priority", "feasibility"]
                }
            }
        }
    ]

# Agent Functions using OpenAI's Function Calling


def chunk_research_data(research_data: str) -> List[Dict[str, Any]]:
    """Agent 1: Break research data into chunks using OpenAI function calling"""

    system_prompt = """You are an expert at breaking down research data into meaningful chunks.

Your task is to divide the research data into small, individual pieces of information called chunks.
Each chunk should:
- Contain a single idea
- Be roughly the same size as others
- Be meaningful on its own
- Not be too granular (if it can't be broken down further without losing meaning, it's at the right level)

Types of chunks can include:
- Quotes from interviews
- Observations from user research
- Facts from secondary sources
- Behavioral patterns
- Pain points or needs

Use the create_chunk function for each meaningful piece of information you identify."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Please chunk the following research data:\n\n{research_data}"}
    ]

    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=messages,
        tools=get_chunking_functions(),
        tool_choice={"type": "function", "function": {"name": "create_chunk"}},
        temperature=0.1
    )

    chunks = []
    for choice in response.choices:
        if choice.message.tool_calls:
            for tool_call in choice.message.tool_calls:
                if tool_call.function.name == "create_chunk":
                    chunk_data = json.loads(tool_call.function.arguments)
                    chunk_data["id"] = f"chunk_{uuid.uuid4().hex[:8]}"
                    chunks.append(chunk_data)

    return chunks


def infer_meanings(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Agent 2: Interpret chunks and extract meanings using OpenAI function calling"""

    system_prompt = """You are an expert at interpreting research data and extracting meaningful insights.

For each chunk, ask and answer:
1. What does this mean?
2. Why is this important?
3. What is this telling us about the problem, topic, or context?

You can come up with multiple meanings per chunk. Meanings can overlap.
Focus on thoughtful, logical interpretations in your own words.

Use the create_inference function for each chunk you interpret."""

    chunks_text = "\n\n".join([
        f"Chunk {chunk['id']}: {chunk['content']}"
        for chunk in chunks
    ])

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Please interpret the following chunks:\n\n{chunks_text}"}
    ]

    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=messages,
        tools=get_inference_functions(),
        tool_choice={"type": "function", "function": {
            "name": "create_inference"}},
        temperature=0.1
    )

    inferences = []
    for choice in response.choices:
        if choice.message.tool_calls:
            for tool_call in choice.message.tool_calls:
                if tool_call.function.name == "create_inference":
                    inference_data = json.loads(tool_call.function.arguments)
                    inferences.append(inference_data)

    return inferences


def relate_patterns(inferences: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Agent 3: Find patterns across meanings using OpenAI function calling"""

    system_prompt = """You are an expert at identifying patterns and relationships in research data.

Look at the inferences and group the ones that feel connected. Find:
- Which meanings are pointing in the same direction?
- Where do you see repetition or shared themes?
- How do pieces of information relate to each other?

Give each pattern a clear, meaningful name. Patterns aren't just categories—
they express relationships and reveal structure in the data.

Use the create_pattern function for each pattern you identify."""

    inferences_text = "\n\n".join([
        f"Inference {inf['chunk_id']}: {', '.join(inf['meanings'])}"
        for inf in inferences
    ])

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Please identify patterns in the following inferences:\n\n{inferences_text}"}
    ]

    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=messages,
        tools=get_pattern_functions(),
        tool_choice={"type": "function",
                     "function": {"name": "create_pattern"}},
        temperature=0.1
    )

    patterns = []
    for choice in response.choices:
        if choice.message.tool_calls:
            for tool_call in choice.message.tool_calls:
                if tool_call.function.name == "create_pattern":
                    pattern_data = json.loads(tool_call.function.arguments)
                    patterns.append(pattern_data)

    return patterns


def explain_insights(patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Agent 4: Generate insights from patterns using OpenAI function calling"""

    system_prompt = """You are an expert at generating powerful insights from research patterns.

For each pattern, ask "why?" and dig deeper:
- Why is this happening?
- Why does it matter?
- What deeper truth does this reveal?

Generate insights that are:
- Non-consensus: They challenge common assumptions
- First-principles-based: They reflect fundamental truths

Write insights as short, bold headlines that capture uniqueness and significance.

Use the create_insight function for each insight you generate."""

    patterns_text = "\n\n".join([
        f"Pattern: {pattern['name']}\nDescription: {pattern['description']}\nThemes: {', '.join(pattern['themes'])}"
        for pattern in patterns
    ])

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Please generate insights from the following patterns:\n\n{patterns_text}"}
    ]

    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=messages,
        tools=get_insight_functions(),
        tool_choice={"type": "function",
                     "function": {"name": "create_insight"}},
        temperature=0.1
    )

    insights = []
    for choice in response.choices:
        if choice.message.tool_calls:
            for tool_call in choice.message.tool_calls:
                if tool_call.function.name == "create_insight":
                    insight_data = json.loads(tool_call.function.arguments)
                    insights.append(insight_data)

    return insights


def activate_design_principles(insights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Agent 5: Convert insights into design principles using OpenAI function calling"""

    system_prompt = """You are an expert at converting insights into actionable design principles.

For every insight, write a design principle: a clear, actionable statement that suggests how design should respond.
These are not final solutions but starting points for ideation.

Design principles should:
- Begin with phrases like "The system should..." or "The experience must..."
- Use action verbs: provide, match, reduce, enable, avoid, combine, simplify, clarify, etc.
- Spark the question "How might we do that?"

Use the create_design_principle function for each design principle you create."""

    insights_text = "\n\n".join([
        f"Insight: {insight['headline']}\nExplanation: {insight['explanation']}"
        for insight in insights
    ])

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Please create design principles from the following insights:\n\n{insights_text}"}
    ]

    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=messages,
        tools=get_design_principle_functions(),
        tool_choice={"type": "function", "function": {
            "name": "create_design_principle"}},
        temperature=0.1
    )

    design_principles = []
    for choice in response.choices:
        if choice.message.tool_calls:
            for tool_call in choice.message.tool_calls:
                if tool_call.function.name == "create_design_principle":
                    principle_data = json.loads(tool_call.function.arguments)
                    design_principles.append(principle_data)

    return design_principles


def run_openai_agentic_analysis(research_data: str) -> Dict[str, Any]:
    """Run the complete OpenAI agentic design analysis workflow"""

    print("Step 1: Chunking research data...")
    chunks = chunk_research_data(research_data)

    print("Step 2: Inferring meanings...")
    inferences = infer_meanings(chunks)

    print("Step 3: Relating patterns...")
    patterns = relate_patterns(inferences)

    print("Step 4: Explaining insights...")
    insights = explain_insights(patterns)

    print("Step 5: Activating design principles...")
    design_principles = activate_design_principles(insights)

    return {
        "chunks": chunks,
        "inferences": inferences,
        "patterns": patterns,
        "insights": insights,
        "design_principles": design_principles,
        "analysis_metadata": {
            "framework": "OpenAI Agentic",
            "model": "gpt-4-turbo-preview",
            "steps_completed": 5
        }
    }


if __name__ == "__main__":
    # Example usage
    sample_research_data = """
    User Interview Transcript:
    - "I just want to get this done quickly. I don't need all these fancy features."
    - "The interface is so cluttered, I can't find what I'm looking for."
    - "I spend more time figuring out how to use the tool than actually using it."
    - "When I see too many options, I get overwhelmed and just close the app."
    - "The simpler tools are the ones I use most often."
    - "I wish there was a way to just get to what I need without all the extra steps."
    - "The help documentation is too complex - I just want simple instructions."
    """

    print("Starting OpenAI Agentic Design Analysis...")
    result = run_openai_agentic_analysis(sample_research_data)

    print("\n=== OpenAI Agentic Design Analysis Results ===\n")

    print("CHUNKS:")
    for chunk in result['chunks']:
        print(f"- [{chunk['type'].upper()}] {chunk['content']}")
        print(
            f"  Tags: {', '.join(chunk['tags'])} | Confidence: {chunk['confidence']:.2f}")

    print("\nINFERENCES:")
    for inference in result['inferences']:
        print(f"- Chunk {inference['chunk_id']}: {inference['meanings'][0]}")
        print(f"  Importance: {inference['importance']}")
        print(f"  Confidence: {inference['confidence']:.2f}")

    print("\nPATTERNS:")
    for pattern in result['patterns']:
        print(f"- {pattern['name']}")
        print(f"  Description: {pattern['description']}")
        print(
            f"  Strength: {pattern['strength']:.2f} | Evidence: {pattern['evidence_count']} pieces")

    print("\nINSIGHTS:")
    for insight in result['insights']:
        print(f"- {insight['headline']}")
        print(f"  Explanation: {insight['explanation']}")
        print(f"  Impact Score: {insight['impact_score']:.2f}")
        print(
            f"  Non-consensus: {insight['non_consensus']} | First-principles: {insight['first_principles']}")

    print("\nDESIGN PRINCIPLES:")
    for principle in result['design_principles']:
        print(f"- {principle['principle']}")
        print(f"  Direction: {principle['design_direction']}")
        print(
            f"  Priority: {principle['priority']:.2f} | Feasibility: {principle['feasibility']:.2f}")
        print(f"  Action Verbs: {', '.join(principle['action_verbs'])}")

    print(f"\nAnalysis completed using OpenAI's agentic framework!")
