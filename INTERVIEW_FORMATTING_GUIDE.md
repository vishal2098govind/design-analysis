# Interview Transcript Formatting Guide

This guide shows you how to format interview transcripts for optimal analysis using the Five Steps Design Analysis system.

## 📋 Overview

The system can analyze any interview transcript, but proper formatting helps the AI extract better insights. The system works with:

- ✅ **Single speaker interviews**
- ✅ **Multiple speaker interviews** 
- ✅ **Structured interviews**
- ✅ **Unstructured conversations**
- ✅ **Focus groups**
- ✅ **User research sessions**

## 🎯 Best Practices

### 1. **Clear Speaker Identification**
```
✅ GOOD:
Interviewer: "What challenges do you face?"
Sarah (Product Manager): "The biggest issue is..."

❌ AVOID:
Q: "What challenges do you face?"
A: "The biggest issue is..."
```

### 2. **Include Context**
```
✅ GOOD:
User Interview - Sarah, 34, Product Manager, 8 years experience
Topic: Project Management Tools

❌ AVOID:
Interview with user about tools
```

### 3. **Preserve Natural Language**
```
✅ GOOD:
Sarah: "I just want to get this done quickly. I don't need all these fancy features."

❌ AVOID:
Sarah: "User wants quick completion without complex features."
```

### 4. **Include Pain Points and Desires**
```
✅ GOOD:
Interviewer: "What frustrates you most?"
Sarah: "The assumption that I want to spend time learning the tool. I don't."

Interviewer: "What would make your ideal tool?"
Sarah: "Something that gets out of my way..."
```

## 📝 Format Examples

### **Single Speaker Interview**

```text
User Interview - Single Speaker (Sarah, 34, Product Manager)

Interviewer: "Can you tell me about your experience with project management tools?"

Sarah: "I've been using various project management tools for about 8 years now. Honestly, most of them are way too complicated for what I actually need. I spend more time setting up the tool than actually managing my projects."

Interviewer: "What specific challenges do you face?"

Sarah: "The biggest issue is that these tools assume I have time to learn complex workflows. I just want to quickly add a task, assign it to someone, and see the status. But instead, I have to navigate through multiple screens, set up custom fields, and configure workflows that I'll never use."

Interviewer: "What would make your ideal tool?"

Sarah: "Something that gets out of my way. I want to open it and immediately see what needs to be done today. No setup, no configuration, just simple task management. The simpler the better - I'd rather have fewer features that work perfectly than hundreds of features I don't understand."
```

### **Multiple Speakers Interview**

```text
User Interview - Multiple Speakers (Design Team)

Interviewer: "Let's talk about your design workflow. How do you currently collaborate on projects?"

Alex (Senior Designer): "We use Figma for design, but the collaboration part is really fragmented. I'll create a design, share it via Slack, get feedback in comments, then have to manually update the design. It's like playing telephone - information gets lost or misinterpreted."

Maria (UX Designer): "Exactly! And the feedback loop is so slow. I'll send a design for review, wait for responses, then spend time implementing changes, only to find out the stakeholder had a completely different idea in mind. It's frustrating."

Interviewer: "What specific pain points do you experience?"

Alex: "The biggest issue is that feedback comes from everywhere - Slack, email, Figma comments, meetings. I have to constantly switch between tools to gather all the input. Sometimes I miss important feedback because it's buried in a Slack thread from last week."

Maria: "And there's no single source of truth. I might update a design based on feedback from one person, but then someone else says they never agreed to that change. It's hard to track who said what and when."
```

### **Structured Interview Format**

```text
Structured User Interview - Customer Support Team

INTERVIEWER: "Let's start with your daily workflow. Walk me through a typical day."

RESPONDENT 1 (Jenny, Support Lead): "I start by checking our support queue, which is usually overwhelming. We get about 200 tickets per day, and they're all marked as 'urgent' by customers. The first challenge is just figuring out what's actually urgent versus what customers think is urgent."

RESPONDENT 2 (Mike, Support Agent): "Yeah, and the ticket system doesn't help. Everything looks the same - red exclamation marks everywhere. I end up just working tickets in the order they came in, which probably isn't the most efficient approach."

INTERVIEWER: "What tools do you use for support?"

Jenny: "We have a help desk system, but it's not integrated with our product. So when a customer reports a bug, I have to manually check if it's a known issue, then update the ticket. It's a lot of back-and-forth."

Mike: "And the knowledge base is outdated. I'll find an article that seems relevant, but when I follow the steps, they don't match the current product. So I end up writing custom responses for every ticket instead of using templates."
```

## 🔧 Using the System

### **Via API**

```python
from api_client import DesignAnalysisClient

client = DesignAnalysisClient("http://localhost:8000")

# Analyze interview transcript
result = client.analyze(
    research_data=your_interview_transcript,
    implementation="hybrid"  # or "openai" or "langchain"
)

print(f"Insights: {len(result['insights'])}")
for insight in result['insights']:
    print(f"• {insight['headline']}")
```

### **Via HTTP**

```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "research_data": "Your interview transcript here...",
    "implementation": "hybrid",
    "include_metadata": true
  }'
```

### **Via Direct Function Call**

```python
from hybrid_agentic_analysis import run_hybrid_agentic_analysis

result = run_hybrid_agentic_analysis(your_interview_transcript)
```

## 📊 Expected Output

The system will analyze your interview and provide:

1. **Chunks** - Individual pieces of information from the interview
2. **Inferences** - What each piece means and why it matters
3. **Patterns** - Connections and themes across the interview
4. **Insights** - Deep understanding of user needs and pain points
5. **Design Principles** - Actionable guidance for design decisions

### **Example Output Structure**

```json
{
  "request_id": "abc123-def4-5678",
  "status": "completed",
  "implementation": "hybrid",
  "timestamp": "2024-01-01T12:00:00Z",
  "chunks": [
    {
      "id": "chunk_1",
      "content": "I spend more time setting up the tool than actually managing my projects",
      "type": "pain_point",
      "confidence": 0.95
    }
  ],
  "inferences": [
    {
      "chunk_id": "chunk_1",
      "meanings": ["Users prioritize actual work over tool setup"],
      "importance": "Reveals fundamental user preference for simplicity"
    }
  ],
  "patterns": [
    {
      "name": "Simplicity Preference",
      "description": "Users consistently prefer simple, immediate solutions over complex setup",
      "strength": 0.89
    }
  ],
  "insights": [
    {
      "headline": "USERS PRIORITIZE WORK OVER TOOL SETUP",
      "explanation": "Users want to start working immediately, not spend time configuring tools",
      "impact_score": 0.93
    }
  ],
  "design_principles": [
    {
      "principle": "The system should require minimal setup and configuration",
      "action_verbs": ["minimize", "simplify", "streamline"],
      "priority": 0.93
    }
  ]
}
```

## 🎯 Tips for Better Analysis

### **1. Include Diverse Perspectives**
- Interview multiple users with different roles
- Include both power users and casual users
- Capture different use cases and scenarios

### **2. Ask Open-Ended Questions**
```
✅ GOOD: "What frustrates you most about this process?"
❌ AVOID: "Do you like this feature? (Yes/No)"
```

### **3. Capture Emotional Responses**
```
✅ GOOD: "It's exhausting trying to figure out how to use this tool"
❌ AVOID: "The tool is difficult to use"
```

### **4. Include Context and Scenarios**
```
✅ GOOD: "When I'm in a hurry and need to quickly update a task..."
❌ AVOID: "The tool should be faster"
```

### **5. Ask About Workarounds**
```
✅ GOOD: "What do you do when the tool doesn't work as expected?"
❌ AVOID: "What problems do you have with the tool?"
```

## 🚀 Running Examples

To see these formats in action, run:

```bash
python interview_examples.py
```

This will analyze three different interview formats and show you the insights generated from each.

## 📈 Analysis Quality

The quality of your analysis depends on:

1. **Interview Quality** - Well-conducted interviews with open-ended questions
2. **Transcript Clarity** - Clear speaker identification and natural language
3. **Diverse Input** - Multiple perspectives and use cases
4. **Rich Context** - Background information and scenarios

The system is designed to work with any interview format, but following these guidelines will help you get the most valuable insights for your design decisions.
