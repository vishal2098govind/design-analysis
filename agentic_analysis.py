"""
Agentic Design Analysis Implementation
Implements the Five Steps of Design Analysis using specialized AI agents
"""

import os
import json
from typing import Dict, List, Any, TypedDict
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
import uuid

# Load environment variables
load_dotenv()

# Initialize OpenAI client
llm = ChatOpenAI(
    model="gpt-4-turbo-preview",
    temperature=0.1,
    api_key=os.getenv("OPENAI_API_KEY")
)

# State definition


class DesignAnalysisState(TypedDict):
    research_data: str
    chunks: List[Dict[str, Any]]
    inferences: List[Dict[str, Any]]
    patterns: List[Dict[str, Any]]
    insights: List[Dict[str, Any]]
    design_principles: List[Dict[str, Any]]
    current_step: str
    messages: List[Any]

# Pydantic models


class Chunk(BaseModel):
    id: str = Field(description="Unique identifier")
    content: str = Field(description="Chunk content")
    source: str = Field(description="Source of chunk")
    type: str = Field(
        description="Type: quote, observation, fact, behavior, pain_point")
    confidence: float = Field(description="Confidence level (0-1)")
    tags: List[str] = Field(description="Categorization tags")


class Inference(BaseModel):
    chunk_id: str = Field(description="Reference to chunk")
    meanings: List[str] = Field(description="Multiple interpretations")
    importance: str = Field(description="Why this matters")
    context: str = Field(description="Broader context")
    confidence: float = Field(description="Confidence level (0-1)")


class Pattern(BaseModel):
    name: str = Field(description="Pattern name")
    description: str = Field(description="What pattern represents")
    related_inferences: List[str] = Field(description="Related inference IDs")
    themes: List[str] = Field(description="Key themes")
    strength: float = Field(description="Pattern strength (0-1)")


class Insight(BaseModel):
    headline: str = Field(description="Bold headline")
    explanation: str = Field(description="Detailed explanation")
    pattern_id: str = Field(description="Source pattern")
    non_consensus: bool = Field(description="Challenges assumptions")
    first_principles: bool = Field(description="Fundamental truth")
    impact_score: float = Field(description="Potential impact (0-1)")


class DesignPrinciple(BaseModel):
    principle: str = Field(description="Actionable principle")
    insight_id: str = Field(description="Source insight")
    action_verbs: List[str] = Field(description="Key action verbs")
    design_direction: str = Field(description="Design direction")
    priority: float = Field(description="Priority level (0-1)")

# Agent Functions


def chunk_research_data(state: DesignAnalysisState) -> DesignAnalysisState:
    """Agent 1: Break research data into chunks"""

    # Create output parser for chunks
    chunk_parser = JsonOutputParser(pydantic_object=Chunk)

    system_prompt = """You are an expert at breaking down research data into meaningful chunks.
    
    Create chunks that:
    - Contain a single idea
    - Are roughly the same size
    - Are meaningful on their own
    - Are appropriately categorized
    
    {format_instructions}
    
    Return a JSON array of chunks."""

    messages = [
        SystemMessage(content=system_prompt.format(
            format_instructions=chunk_parser.get_format_instructions())),
        HumanMessage(
            content=f"Chunk this research data:\n\n{state['research_data']}")
    ]

    response = llm.invoke(messages)

    try:
        # Parse the response to get structured chunks
        parsed_chunks = chunk_parser.parse(response.content)
        chunks = parsed_chunks if isinstance(
            parsed_chunks, list) else [parsed_chunks]
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

    return {
        **state,
        "chunks": chunks,
        "current_step": "chunked",
        "messages": state["messages"] + [response]
    }


def infer_meanings(state: DesignAnalysisState) -> DesignAnalysisState:
    """Agent 2: Interpret chunks and extract meanings"""

    # Create output parser for inferences
    inference_parser = JsonOutputParser(pydantic_object=Inference)

    system_prompt = """You are an expert at interpreting research data.
    
    For each chunk, identify:
    1. What does this mean?
    2. Why is this important?
    3. What does this tell us about the context?
    
    {format_instructions}
    
    Return a JSON array of inferences."""

    chunks_text = "\n\n".join([
        f"Chunk {chunk['id']}: {chunk['content']}"
        for chunk in state['chunks']
    ])

    messages = [
        SystemMessage(content=system_prompt.format(
            format_instructions=inference_parser.get_format_instructions())),
        HumanMessage(content=f"Interpret these chunks:\n\n{chunks_text}")
    ]

    response = llm.invoke(messages)

    try:
        # Parse the response to get structured inferences
        parsed_inferences = inference_parser.parse(response.content)
        inferences = parsed_inferences if isinstance(
            parsed_inferences, list) else [parsed_inferences]
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
                "confidence": 0.88
            })

    return {
        **state,
        "inferences": inferences,
        "current_step": "inferred",
        "messages": state["messages"] + [response]
    }


def relate_patterns(state: DesignAnalysisState) -> DesignAnalysisState:
    """Agent 3: Find patterns across meanings"""

    # Create output parser for patterns
    pattern_parser = JsonOutputParser(pydantic_object=Pattern)

    system_prompt = """You are an expert at identifying patterns in research data.
    
    Look for:
    - Which meanings point in the same direction?
    - Where do you see shared themes?
    - How do pieces relate to each other?
    
    {format_instructions}
    
    Return a JSON array of patterns."""

    inferences_text = "\n\n".join([
        f"Inference {inf['chunk_id']}: {', '.join(inf['meanings'])}"
        for inf in state['inferences']
    ])

    messages = [
        SystemMessage(content=system_prompt.format(
            format_instructions=pattern_parser.get_format_instructions())),
        HumanMessage(
            content=f"Find patterns in these inferences:\n\n{inferences_text}")
    ]

    response = llm.invoke(messages)

    try:
        # Parse the response to get structured patterns
        parsed_patterns = pattern_parser.parse(response.content)
        patterns = parsed_patterns if isinstance(
            parsed_patterns, list) else [parsed_patterns]
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
                "strength": 0.89
            })

        if clarity_inferences:
            patterns.append({
                "name": "Information Clarity",
                "description": "Users struggle with unclear or complex information presentation",
                "related_inferences": clarity_inferences,
                "themes": ["clarity", "simplicity", "communication"],
                "strength": 0.87
            })

    return {
        **state,
        "patterns": patterns,
        "current_step": "patterned",
        "messages": state["messages"] + [response]
    }


def explain_insights(state: DesignAnalysisState) -> DesignAnalysisState:
    """Agent 4: Generate insights from patterns"""

    # Create output parser for insights
    insight_parser = JsonOutputParser(pydantic_object=Insight)

    system_prompt = """You are an expert at generating powerful insights from patterns.
    
    For each pattern, ask:
    - Why is this happening?
    - Why does it matter?
    - What deeper truth does this reveal?
    
    Generate insights that are:
    - Non-consensus: Challenge common assumptions
    - First-principles-based: Reflect fundamental truths
    
    {format_instructions}
    
    Return a JSON array of insights."""

    patterns_text = "\n\n".join([
        f"Pattern: {pattern['name']}\nDescription: {pattern['description']}"
        for pattern in state['patterns']
    ])

    messages = [
        SystemMessage(content=system_prompt.format(
            format_instructions=insight_parser.get_format_instructions())),
        HumanMessage(
            content=f"Generate insights from these patterns:\n\n{patterns_text}")
    ]

    response = llm.invoke(messages)

    try:
        # Parse the response to get structured insights
        parsed_insights = insight_parser.parse(response.content)
        insights = parsed_insights if isinstance(
            parsed_insights, list) else [parsed_insights]
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
                    "impact_score": 0.93
                })
            elif "clarity" in pattern['name'].lower():
                insights.append({
                    "headline": "COMPLEXITY CREATES COGNITIVE BARRIERS",
                    "explanation": "When information is presented in complex ways, users disengage rather than invest effort to understand.",
                    "pattern_id": pattern['name'],
                    "non_consensus": False,
                    "first_principles": True,
                    "impact_score": 0.91
                })

    return {
        **state,
        "insights": insights,
        "current_step": "insights_generated",
        "messages": state["messages"] + [response]
    }


def activate_design_principles(state: DesignAnalysisState) -> DesignAnalysisState:
    """Agent 5: Convert insights into design principles"""

    # Create output parser for design principles
    principle_parser = JsonOutputParser(pydantic_object=DesignPrinciple)

    system_prompt = """You are an expert at converting insights into actionable design principles.
    
    For every insight, create a design principle that:
    - Begins with "The system should..." or "The experience must..."
    - Uses action verbs: provide, match, reduce, enable, avoid, combine, simplify, clarify
    - Sparks the question "How might we do that?"
    
    {format_instructions}
    
    Return a JSON array of design principles."""

    insights_text = "\n\n".join([
        f"Insight: {insight['headline']}\nExplanation: {insight['explanation']}"
        for insight in state['insights']
    ])

    messages = [
        SystemMessage(content=system_prompt.format(
            format_instructions=principle_parser.get_format_instructions())),
        HumanMessage(
            content=f"Create design principles from these insights:\n\n{insights_text}")
    ]

    response = llm.invoke(messages)

    try:
        # Parse the response to get structured design principles
        parsed_principles = principle_parser.parse(response.content)
        design_principles = parsed_principles if isinstance(
            parsed_principles, list) else [parsed_principles]
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
                    "priority": insight['impact_score']
                })
            elif "COGNITIVE BARRIERS" in insight['headline']:
                design_principles.append({
                    "principle": "The experience must present information with maximum clarity and minimal cognitive load",
                    "insight_id": insight['headline'],
                    "action_verbs": ["clarify", "simplify", "reduce"],
                    "design_direction": "Use progressive disclosure and clear visual hierarchy",
                    "priority": insight['impact_score']
                })

    return {
        **state,
        "design_principles": design_principles,
        "current_step": "completed",
        "messages": state["messages"] + [response]
    }


def create_agentic_graph():
    """Create the agentic design analysis workflow"""

    workflow = StateGraph(DesignAnalysisState)

    # Add nodes
    workflow.add_node("chunk", chunk_research_data)
    workflow.add_node("infer", infer_meanings)
    workflow.add_node("relate", relate_patterns)
    workflow.add_node("explain", explain_insights)
    workflow.add_node("activate", activate_design_principles)

    # Define flow
    workflow.set_entry_point("chunk")
    workflow.add_edge("chunk", "infer")
    workflow.add_edge("infer", "relate")
    workflow.add_edge("relate", "explain")
    workflow.add_edge("explain", "activate")
    workflow.add_edge("activate", END)

    return workflow.compile()


def run_agentic_analysis(research_data: str) -> Dict[str, Any]:
    """Run the complete agentic design analysis"""

    graph = create_agentic_graph()

    initial_state = {
        "research_data": research_data,
        "chunks": [],
        "inferences": [],
        "patterns": [],
        "insights": [],
        "design_principles": [],
        "current_step": "initialized",
        "messages": []
    }

    result = graph.invoke(initial_state)
    return result


if __name__ == "__main__":
    # Example usage
    sample_data = """
    User Interview Transcript:
    - "I just want to get this done quickly. I don't need all these fancy features."
    - "The interface is so cluttered, I can't find what I'm looking for."
    - "I spend more time figuring out how to use the tool than actually using it."
    - "When I see too many options, I get overwhelmed and just close the app."
    - "The simpler tools are the ones I use most often."
    """

    print("Starting Agentic Design Analysis...")
    result = run_agentic_analysis(sample_data)

    print("\n=== Agentic Design Analysis Results ===\n")

    print("CHUNKS:")
    for chunk in result['chunks']:
        print(f"- [{chunk['type'].upper()}] {chunk['content']}")

    print("\nINFERENCES:")
    for inference in result['inferences']:
        print(f"- {inference['meanings'][0]}")

    print("\nPATTERNS:")
    for pattern in result['patterns']:
        print(f"- {pattern['name']}: {pattern['description']}")

    print("\nINSIGHTS:")
    for insight in result['insights']:
        print(f"- {insight['headline']}")

    print("\nDESIGN PRINCIPLES:")
    for principle in result['design_principles']:
        print(f"- {principle['principle']}")

    print(f"\nAnalysis completed successfully!")
