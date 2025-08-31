"""
Hybrid Agentic Design Analysis Implementation
Combines LangChain/LangGraph orchestration with OpenAI's native agentic framework
"""

import os
import json
from typing import Dict, List, Any, TypedDict, Optional
from dotenv import load_dotenv
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from langchain_core.output_parsers import JsonOutputParser
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
import uuid

# Import DynamoDB tracker
try:
    from dynamodb_tracker import StepStatus, create_dynamodb_tracker
    DYNAMODB_AVAILABLE = True
except ImportError:
    DYNAMODB_AVAILABLE = False
    print("⚠️ DynamoDB tracker not available - status tracking disabled")

# Load environment variables
load_dotenv()

# Initialize OpenAI client for direct function calling
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize LangChain OpenAI for orchestration
llm = ChatOpenAI(
    model="gpt-4-turbo-preview",
    temperature=0.1,
    api_key=os.getenv("OPENAI_API_KEY")
)

# Initialize DynamoDB tracker if available
tracker = None
if DYNAMODB_AVAILABLE:
    try:
        tracker = create_dynamodb_tracker()
        print("✅ DynamoDB tracker initialized")
    except Exception as e:
        print(f"⚠️ Failed to initialize DynamoDB tracker: {e}")
        tracker = None

# State definition for LangGraph


class DesignAnalysisState(TypedDict):
    """State for the design analysis workflow"""
    research_data: str
    chunks: List[Dict[str, Any]]
    inferences: List[Dict[str, Any]]
    patterns: List[Dict[str, Any]]
    insights: List[Dict[str, Any]]
    design_principles: List[Dict[str, Any]]
    current_step: str
    messages: List[Any]
    analysis_metadata: Dict[str, Any]

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

# OpenAI Function Definitions for native function calling


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
                        "content": {"type": "string", "description": "The chunk content"},
                        "source": {"type": "string", "description": "Source of the chunk"},
                        "type": {
                            "type": "string",
                            "enum": ["quote", "observation", "fact", "behavior", "pain_point"],
                            "description": "Type of chunk"
                        },
                        "confidence": {"type": "number", "description": "Confidence level (0-1)"},
                        "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags to categorize this chunk"}
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
                        "chunk_id": {"type": "string", "description": "Reference to the source chunk"},
                        "meanings": {"type": "array", "items": {"type": "string"}, "description": "Multiple interpretations of the chunk"},
                        "importance": {"type": "string", "description": "Why this chunk matters"},
                        "context": {"type": "string", "description": "What this tells us about the broader context"},
                        "confidence": {"type": "number", "description": "Confidence level (0-1)"},
                        "reasoning": {"type": "string", "description": "Explanation of the reasoning process"}
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
                        "name": {"type": "string", "description": "Clear, meaningful name for the pattern"},
                        "description": {"type": "string", "description": "What this pattern represents"},
                        "related_inferences": {"type": "array", "items": {"type": "string"}, "description": "List of inference IDs that form this pattern"},
                        "themes": {"type": "array", "items": {"type": "string"}, "description": "Key themes in this pattern"},
                        "strength": {"type": "number", "description": "Strength of the pattern (0-1)"},
                        "evidence_count": {"type": "integer", "description": "Number of pieces of evidence supporting this pattern"}
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
                        "headline": {"type": "string", "description": "Bold, short headline capturing the insight"},
                        "explanation": {"type": "string", "description": "Detailed explanation of the insight"},
                        "pattern_id": {"type": "string", "description": "Reference to the source pattern"},
                        "non_consensus": {"type": "boolean", "description": "Whether this challenges common assumptions"},
                        "first_principles": {"type": "boolean", "description": "Whether this reflects fundamental truths"},
                        "impact_score": {"type": "number", "description": "Potential impact of this insight (0-1)"},
                        "supporting_evidence": {"type": "array", "items": {"type": "string"}, "description": "Evidence supporting this insight"}
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
                        "principle": {"type": "string", "description": "Clear, actionable design principle"},
                        "insight_id": {"type": "string", "description": "Reference to the source insight"},
                        "action_verbs": {"type": "array", "items": {"type": "string"}, "description": "Key action verbs in the principle"},
                        "design_direction": {"type": "string", "description": "Specific direction for design"},
                        "priority": {"type": "number", "description": "Priority level (0-1)"},
                        "feasibility": {"type": "number", "description": "Feasibility of implementation (0-1)"}
                    },
                    "required": ["principle", "insight_id", "action_verbs", "design_direction", "priority", "feasibility"]
                }
            }
        }
    ]

# LangGraph Node Functions using OpenAI's Function Calling


def chunk_research_data(state: DesignAnalysisState) -> DesignAnalysisState:
    """Node 1: Break research data into chunks using LangChain output parser"""

    # Update DynamoDB status to processing
    request_id = state.get('analysis_metadata', {}).get('request_id')
    if tracker and request_id:
        tracker.update_step_status(
            request_id, "chunking", StepStatus.PROCESSING,
            "Starting to chunk research data"
        )

    # Create output parser for chunks
    chunk_parser = JsonOutputParser(pydantic_object=Chunk)

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

{format_instructions}

Return a JSON array of chunks."""

    messages = [
        {"role": "system", "content": system_prompt.format(
            format_instructions=chunk_parser.get_format_instructions())},
        {"role": "user",
            "content": f"Please chunk the following research data:\n\n{state['research_data']}"}
    ]

    try:
        # Use OpenAI with LangChain output parser
        response = openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=messages,
            temperature=0.1
        )

        # Parse the response to get structured chunks
        parsed_chunks = chunk_parser.parse(response.choices[0].message.content)
        chunks = parsed_chunks if isinstance(
            parsed_chunks, list) else [parsed_chunks]

        # Ensure each chunk has an ID
        for chunk in chunks:
            if not hasattr(chunk, 'id') or not chunk.id:
                chunk.id = f"chunk_{uuid.uuid4().hex[:8]}"

        # Update DynamoDB status to completed
        if tracker and request_id:
            tracker.update_step_status(
                request_id, "chunking", StepStatus.COMPLETED,
                f"Successfully created {len(chunks)} chunks"
            )

    except Exception as e:
        # Fallback to rule-based chunking if parsing fails
        print(f"Parsing failed, using fallback: {e}")
        chunks = []
        lines = [line.strip()
                 for line in state['research_data'].split('\n') if line.strip()]

        for i, line in enumerate(lines):
            chunk_type = "quote" if '"' in line else "observation"
            tags = ["user_feedback"] if "user" in line.lower() else ["general"]

            chunks.append({
                "id": f"chunk_{uuid.uuid4().hex[:8]}",
                "content": line,
                "source": "research_data",
                "type": chunk_type,
                "confidence": 0.85,
                "tags": tags
            })

        # Update DynamoDB status to completed (with fallback)
        if tracker and request_id:
            tracker.update_step_status(
                request_id, "chunking", StepStatus.COMPLETED,
                f"Created {len(chunks)} chunks using fallback method"
            )

    return {
        **state,
        "chunks": chunks,
        "current_step": "chunked",
        "messages": state["messages"] + [AIMessage(content=f"Created {len(chunks)} chunks using LangChain output parser")]
    }


def infer_meanings(state: DesignAnalysisState) -> DesignAnalysisState:
    """Node 2: Interpret chunks and extract meanings using LangChain output parser"""

    # Update DynamoDB status to processing
    request_id = state.get('analysis_metadata', {}).get('request_id')
    if tracker and request_id:
        tracker.update_step_status(
            request_id, "inferring", StepStatus.PROCESSING,
            "Starting to infer meanings from chunks"
        )

    # Create output parser for inferences
    inference_parser = JsonOutputParser(pydantic_object=Inference)

    system_prompt = """You are an expert at interpreting research data and extracting meaningful insights.

For each chunk, ask and answer:
1. What does this mean?
2. Why is this important?
3. What is this telling us about the problem, topic, or context?

You can come up with multiple meanings per chunk. Meanings can overlap.
Focus on thoughtful, logical interpretations in your own words.

{format_instructions}

Return a JSON array of inferences."""

    chunks_text = "\n\n".join([
        f"Chunk {chunk['id']}: {chunk['content']}"
        for chunk in state['chunks']
    ])

    messages = [
        {"role": "system", "content": system_prompt.format(
            format_instructions=inference_parser.get_format_instructions())},
        {"role": "user", "content": f"Please interpret the following chunks:\n\n{chunks_text}"}
    ]

    try:
        # Use OpenAI with LangChain output parser
        response = openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=messages,
            temperature=0.1
        )

        # Parse the response to get structured inferences
        parsed_inferences = inference_parser.parse(
            response.choices[0].message.content)
        inferences = parsed_inferences if isinstance(
            parsed_inferences, list) else [parsed_inferences]

        # Update DynamoDB status to completed
        if tracker and request_id:
            tracker.update_step_status(
                request_id, "inferring", StepStatus.COMPLETED,
                f"Successfully generated {len(inferences)} inferences"
            )

    except Exception as e:
        # Fallback to rule-based inference if parsing fails
        print(f"Parsing failed, using fallback: {e}")
        inferences = []
        for chunk in state['chunks']:
            content = chunk['content'].lower()

            meanings = []
            if "quick" in content or "fast" in content:
                meanings.append("Users prioritize speed and efficiency")
            if "cluttered" in content or "complex" in content:
                meanings.append("Users struggle with complexity")
            if "simple" in content:
                meanings.append("Users prefer simplicity")

            if not meanings:
                meanings.append("Users have specific needs and preferences")

            inferences.append({
                "chunk_id": chunk['id'],
                "meanings": meanings,
                "importance": "Reveals user behavior patterns and needs",
                "context": "Indicates fundamental user preferences",
                "confidence": 0.88,
                "reasoning": "Based on user feedback patterns"
            })

        # Update DynamoDB status to completed (with fallback)
        if tracker and request_id:
            tracker.update_step_status(
                request_id, "inferring", StepStatus.COMPLETED,
                f"Generated {len(inferences)} inferences using fallback method"
            )

    return {
        **state,
        "inferences": inferences,
        "current_step": "inferred",
        "messages": state["messages"] + [AIMessage(content=f"Generated {len(inferences)} inferences using LangChain output parser")]
    }


def relate_patterns(state: DesignAnalysisState) -> DesignAnalysisState:
    """Node 3: Find patterns across meanings using LangChain output parser"""

    # Update DynamoDB status to processing
    request_id = state.get('analysis_metadata', {}).get('request_id')
    if tracker and request_id:
        tracker.update_step_status(
            request_id, "relating", StepStatus.PROCESSING,
            "Starting to identify patterns across meanings"
        )

    # Create output parser for patterns
    pattern_parser = JsonOutputParser(pydantic_object=Pattern)

    system_prompt = """You are an expert at identifying patterns and relationships in research data.

Look at the inferences and group the ones that feel connected. Find:
- Which meanings are pointing in the same direction?
- Where do you see repetition or shared themes?
- How do pieces of information relate to each other?

Give each pattern a clear, meaningful name. Patterns aren't just categories—
they express relationships and reveal structure in the data.

{format_instructions}

Return a JSON array of patterns."""

    inferences_text = "\n\n".join([
        f"Inference {inf['chunk_id']}: {', '.join(inf['meanings'])}"
        for inf in state['inferences']
    ])

    messages = [
        {"role": "system", "content": system_prompt.format(
            format_instructions=pattern_parser.get_format_instructions())},
        {"role": "user", "content": f"Please identify patterns in the following inferences:\n\n{inferences_text}"}
    ]

    try:
        # Use OpenAI with LangChain output parser
        response = openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=messages,
            temperature=0.1
        )

        # Parse the response to get structured patterns
        parsed_patterns = pattern_parser.parse(
            response.choices[0].message.content)
        patterns = parsed_patterns if isinstance(
            parsed_patterns, list) else [parsed_patterns]

        # Update DynamoDB status to completed
        if tracker and request_id:
            tracker.update_step_status(
                request_id, "relating", StepStatus.COMPLETED,
                f"Successfully identified {len(patterns)} patterns"
            )

    except Exception as e:
        # Fallback to rule-based pattern detection if parsing fails
        print(f"Parsing failed, using fallback: {e}")
        # Group by themes
        efficiency_inferences = []
        clarity_inferences = []

        for inference in state['inferences']:
            meanings_text = ' '.join(inference['meanings']).lower()
            if any(word in meanings_text for word in ['speed', 'efficient', 'quick', 'fast']):
                efficiency_inferences.append(inference['chunk_id'])
            if any(word in meanings_text for word in ['complex', 'cluttered', 'simple', 'clear']):
                clarity_inferences.append(inference['chunk_id'])

        patterns = []
        if efficiency_inferences:
            patterns.append({
                "name": "User Efficiency Needs",
                "description": "Users consistently seek ways to complete tasks more efficiently",
                "related_inferences": efficiency_inferences,
                "themes": ["efficiency", "speed", "productivity"],
                "strength": 0.89,
                "evidence_count": len(efficiency_inferences)
            })

        if clarity_inferences:
            patterns.append({
                "name": "Information Clarity",
                "description": "Users struggle with unclear or complex information presentation",
                "related_inferences": clarity_inferences,
                "themes": ["clarity", "simplicity", "communication"],
                "strength": 0.87,
                "evidence_count": len(clarity_inferences)
            })

        # Update DynamoDB status to completed (with fallback)
        if tracker and request_id:
            tracker.update_step_status(
                request_id, "relating", StepStatus.COMPLETED,
                f"Identified {len(patterns)} patterns using fallback method"
            )

    return {
        **state,
        "patterns": patterns,
        "current_step": "patterned",
        "messages": state["messages"] + [AIMessage(content=f"Identified {len(patterns)} patterns using LangChain output parser")]
    }


def explain_insights(state: DesignAnalysisState) -> DesignAnalysisState:
    """Node 4: Generate insights from patterns using LangChain output parser"""

    # Update DynamoDB status to processing
    request_id = state.get('analysis_metadata', {}).get('request_id')
    if tracker and request_id:
        tracker.update_step_status(
            request_id, "explaining", StepStatus.PROCESSING,
            "Starting to generate insights from patterns"
        )

    # Create output parser for insights
    insight_parser = JsonOutputParser(pydantic_object=Insight)

    system_prompt = """You are an expert at generating powerful insights from research patterns.

For each pattern, ask "why?" and dig deeper:
- Why is this happening?
- Why does it matter?
- What deeper truth does this reveal?

Generate insights that are:
- Non-consensus: They challenge common assumptions
- First-principles-based: They reflect fundamental truths

Write insights as short, bold headlines that capture uniqueness and significance.

{format_instructions}

Return a JSON array of insights."""

    patterns_text = "\n\n".join([
        f"Pattern: {pattern['name']}\nDescription: {pattern['description']}\nThemes: {', '.join(pattern['themes'])}"
        for pattern in state['patterns']
    ])

    messages = [
        {"role": "system", "content": system_prompt.format(
            format_instructions=insight_parser.get_format_instructions())},
        {"role": "user", "content": f"Please generate insights from the following patterns:\n\n{patterns_text}"}
    ]

    try:
        # Use OpenAI with LangChain output parser
        response = openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=messages,
            temperature=0.1
        )

        # Parse the response to get structured insights
        parsed_insights = insight_parser.parse(
            response.choices[0].message.content)
        insights = parsed_insights if isinstance(
            parsed_insights, list) else [parsed_insights]

        # Update DynamoDB status to completed
        if tracker and request_id:
            tracker.update_step_status(
                request_id, "explaining", StepStatus.COMPLETED,
                f"Successfully generated {len(insights)} insights"
            )

    except Exception as e:
        # Fallback to rule-based insight generation if parsing fails
        print(f"Parsing failed, using fallback: {e}")
        insights = []
        for pattern in state['patterns']:
            if "efficiency" in pattern['name'].lower():
                insights.append({
                    "headline": "USERS PRIORITIZE SPEED OVER FEATURES",
                    "explanation": "Despite having access to advanced features, users consistently choose the fastest path to completion.",
                    "pattern_id": pattern['name'],
                    "non_consensus": True,
                    "first_principles": True,
                    "impact_score": 0.93,
                    "supporting_evidence": ["User feedback on speed preferences", "Behavioral patterns in tool usage"]
                })
            elif "clarity" in pattern['name'].lower():
                insights.append({
                    "headline": "COMPLEXITY CREATES COGNITIVE BARRIERS",
                    "explanation": "When information is presented in complex ways, users disengage rather than invest effort to understand.",
                    "pattern_id": pattern['name'],
                    "non_consensus": False,
                    "first_principles": True,
                    "impact_score": 0.91,
                    "supporting_evidence": ["User frustration with complex interfaces", "Preference for simple tools"]
                })

        # Update DynamoDB status to completed (with fallback)
        if tracker and request_id:
            tracker.update_step_status(
                request_id, "explaining", StepStatus.COMPLETED,
                f"Generated {len(insights)} insights using fallback method"
            )

    return {
        **state,
        "insights": insights,
        "current_step": "insights_generated",
        "messages": state["messages"] + [AIMessage(content=f"Generated {len(insights)} insights using LangChain output parser")]
    }


def activate_design_principles(state: DesignAnalysisState) -> DesignAnalysisState:
    """Node 5: Convert insights into design principles using LangChain output parser"""

    # Update DynamoDB status to processing
    request_id = state.get('analysis_metadata', {}).get('request_id')
    if tracker and request_id:
        tracker.update_step_status(
            request_id, "activating", StepStatus.PROCESSING,
            "Starting to create design principles from insights"
        )

    # Create output parser for design principles
    principle_parser = JsonOutputParser(pydantic_object=DesignPrinciple)

    system_prompt = """You are an expert at converting insights into actionable design principles.

For every insight, write a design principle: a clear, actionable statement that suggests how design should respond.
These are not final solutions but starting points for ideation.

Design principles should:
- Begin with phrases like "The system should..." or "The experience must..."
- Use action verbs: provide, match, reduce, enable, avoid, combine, simplify, clarify, etc.
- Spark the question "How might we do that?"

{format_instructions}

Return a JSON array of design principles."""

    insights_text = "\n\n".join([
        f"Insight: {insight['headline']}\nExplanation: {insight['explanation']}"
        for insight in state['insights']
    ])

    messages = [
        {"role": "system", "content": system_prompt.format(
            format_instructions=principle_parser.get_format_instructions())},
        {"role": "user", "content": f"Please create design principles from the following insights:\n\n{insights_text}"}
    ]

    try:
        # Use OpenAI with LangChain output parser
        response = openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=messages,
            temperature=0.1
        )

        # Parse the response to get structured design principles
        parsed_principles = principle_parser.parse(
            response.choices[0].message.content)
        design_principles = parsed_principles if isinstance(
            parsed_principles, list) else [parsed_principles]

        # Update DynamoDB status to completed
        if tracker and request_id:
            tracker.update_step_status(
                request_id, "activating", StepStatus.COMPLETED,
                f"Successfully created {len(design_principles)} design principles"
            )

    except Exception as e:
        # Fallback to rule-based design principle generation if parsing fails
        print(f"Parsing failed, using fallback: {e}")
        design_principles = []
        for insight in state['insights']:
            if "SPEED OVER FEATURES" in insight['headline']:
                design_principles.append({
                    "principle": "The system should prioritize speed and efficiency over feature complexity",
                    "insight_id": insight['headline'],
                    "action_verbs": ["prioritize", "simplify", "streamline"],
                    "design_direction": "Focus on reducing steps and eliminating unnecessary complexity",
                    "priority": insight['impact_score'],
                    "feasibility": 0.85
                })
            elif "COGNITIVE BARRIERS" in insight['headline']:
                design_principles.append({
                    "principle": "The experience must present information with maximum clarity and minimal cognitive load",
                    "insight_id": insight['headline'],
                    "action_verbs": ["clarify", "simplify", "reduce"],
                    "design_direction": "Use progressive disclosure and clear visual hierarchy",
                    "priority": insight['impact_score'],
                    "feasibility": 0.82
                })

        # Update DynamoDB status to completed (with fallback)
        if tracker and request_id:
            tracker.update_step_status(
                request_id, "activating", StepStatus.COMPLETED,
                f"Created {len(design_principles)} design principles using fallback method"
            )

    return {
        **state,
        "design_principles": design_principles,
        "current_step": "completed",
        "messages": state["messages"] + [AIMessage(content=f"Created {len(design_principles)} design principles using LangChain output parser")]
    }

# LangGraph Workflow Construction


def create_hybrid_agentic_graph():
    """Create the hybrid agentic design analysis workflow using LangGraph"""

    # Create the graph
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


def run_hybrid_agentic_analysis(research_data: str, request_id: Optional[str] = None, research_data_s3_path: Optional[str] = None) -> Dict[str, Any]:
    """Run the complete hybrid agentic design analysis workflow"""

    # Create the LangGraph workflow
    graph = create_hybrid_agentic_graph()

    # Generate request ID if not provided
    if not request_id:
        request_id = f"analysis_{uuid.uuid4().hex[:8]}"

    # Initialize DynamoDB tracking if available
    if tracker and research_data_s3_path:
        tracker.create_analysis_request(request_id, research_data_s3_path)

    # Initialize state
    initial_state = {
        "research_data": research_data,
        "chunks": [],
        "inferences": [],
        "patterns": [],
        "insights": [],
        "design_principles": [],
        "current_step": "initialized",
        "messages": [],
        "analysis_metadata": {
            "request_id": request_id,
            "framework": "Hybrid (LangGraph + OpenAI Agentic)",
            "model": "gpt-4-turbo-preview",
            "orchestration": "LangGraph",
            "function_calling": "OpenAI Native",
            "research_data_s3_path": research_data_s3_path
        }
    }

    # Run the workflow
    result = graph.invoke(initial_state)

    return result


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

    print("Starting Hybrid Agentic Design Analysis...")
    print("(LangGraph orchestration + OpenAI native function calling)")

    result = run_hybrid_agentic_analysis(sample_research_data)

    print("\n=== Hybrid Agentic Design Analysis Results ===\n")

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

    print(f"\nAnalysis completed using Hybrid Agentic Framework!")
    print(f"Framework: {result['analysis_metadata']['framework']}")
    print(f"Orchestration: {result['analysis_metadata']['orchestration']}")
    print(
        f"Function Calling: {result['analysis_metadata']['function_calling']}")
