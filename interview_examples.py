#!/usr/bin/env python3
"""
Interview Transcript Examples for Design Analysis
Shows how to format interview data for the Five Steps analysis system
"""

from api_client import DesignAnalysisClient
import json


def analyze_interview_transcript(transcript: str, implementation: str = "hybrid"):
    """Analyze an interview transcript using the design analysis system"""

    client = DesignAnalysisClient("http://localhost:8000")

    print(
        f"🔍 Analyzing interview transcript using {implementation} implementation...")
    print("=" * 60)

    try:
        result = client.analyze(
            research_data=transcript,
            implementation=implementation
        )

        print(f"✅ Analysis completed!")
        print(f"📋 Request ID: {result['request_id']}")
        print(f"⏱️  Execution time: {result['execution_time']:.2f} seconds")
        print(f"📊 Results:")
        print(f"   - Chunks: {len(result['chunks'])}")
        print(f"   - Inferences: {len(result['inferences'])}")
        print(f"   - Patterns: {len(result['patterns'])}")
        print(f"   - Insights: {len(result['insights'])}")
        print(f"   - Design Principles: {len(result['design_principles'])}")

        return result

    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return None


# Example 1: Single Speaker Interview
SINGLE_SPEAKER_TRANSCRIPT = """
User Interview - Single Speaker (Sarah, 34, Product Manager)

Interviewer: "Can you tell me about your experience with project management tools?"

Sarah: "I've been using various project management tools for about 8 years now. Honestly, most of them are way too complicated for what I actually need. I spend more time setting up the tool than actually managing my projects."

Interviewer: "What specific challenges do you face?"

Sarah: "The biggest issue is that these tools assume I have time to learn complex workflows. I just want to quickly add a task, assign it to someone, and see the status. But instead, I have to navigate through multiple screens, set up custom fields, and configure workflows that I'll never use."

Interviewer: "What would make your ideal tool?"

Sarah: "Something that gets out of my way. I want to open it and immediately see what needs to be done today. No setup, no configuration, just simple task management. The simpler the better - I'd rather have fewer features that work perfectly than hundreds of features I don't understand."

Interviewer: "How do you currently track progress?"

Sarah: "I end up using a combination of sticky notes, email, and sometimes just my memory. It's not ideal, but it's faster than fighting with the project management software. I know I'm missing things, but at least I'm not spending hours just trying to update a task status."

Interviewer: "What frustrates you most about current tools?"

Sarah: "The assumption that I want to spend time learning the tool. I don't. I want to spend time doing my actual work. Every time I try a new tool, I have to watch tutorials, read documentation, and figure out their specific way of doing things. It's exhausting."
"""

# Example 2: Multiple Speakers Interview
MULTIPLE_SPEAKERS_TRANSCRIPT = """
User Interview - Multiple Speakers (Design Team)

Interviewer: "Let's talk about your design workflow. How do you currently collaborate on projects?"

Alex (Senior Designer): "We use Figma for design, but the collaboration part is really fragmented. I'll create a design, share it via Slack, get feedback in comments, then have to manually update the design. It's like playing telephone - information gets lost or misinterpreted."

Maria (UX Designer): "Exactly! And the feedback loop is so slow. I'll send a design for review, wait for responses, then spend time implementing changes, only to find out the stakeholder had a completely different idea in mind. It's frustrating."

Interviewer: "What specific pain points do you experience?"

Alex: "The biggest issue is that feedback comes from everywhere - Slack, email, Figma comments, meetings. I have to constantly switch between tools to gather all the input. Sometimes I miss important feedback because it's buried in a Slack thread from last week."

Maria: "And there's no single source of truth. I might update a design based on feedback from one person, but then someone else says they never agreed to that change. It's hard to track who said what and when."

Interviewer: "How do you handle design reviews?"

Alex: "We try to have structured review sessions, but they often turn into free-for-alls. Everyone has an opinion, and they're not always aligned. I end up making changes to please everyone, which usually results in a design that pleases no one."

Maria: "The review process is too subjective. There's no clear criteria for what makes a good design, so feedback is all over the place. One person wants it more minimal, another wants more features, and I'm stuck in the middle trying to make everyone happy."

Interviewer: "What would improve your workflow?"

Alex: "I need a way to consolidate all feedback in one place, with clear ownership and decision-making. Right now, it feels like I'm herding cats - everyone has input, but no one wants to make the final decision."

Maria: "And I need better tools for tracking design decisions. Why did we choose this approach? What alternatives did we consider? Right now, that information gets lost, so we end up revisiting the same discussions over and over."

Interviewer: "How do you handle design handoffs to developers?"

Alex: "That's another pain point. I create detailed specs, but developers often have questions that I can't answer because I don't have the technical context. The handoff process is like throwing designs over a wall and hoping they land correctly."

Maria: "And there's no good way to track what's been implemented versus what's still in design. I'll see something in production that doesn't match my design, but I don't know if it's because the developer misunderstood or if requirements changed."
"""

# Example 3: Structured Interview Format
STRUCTURED_INTERVIEW = """
Structured User Interview - Customer Support Team

INTERVIEWER: "Let's start with your daily workflow. Walk me through a typical day."

RESPONDENT 1 (Jenny, Support Lead): "I start by checking our support queue, which is usually overwhelming. We get about 200 tickets per day, and they're all marked as 'urgent' by customers. The first challenge is just figuring out what's actually urgent versus what customers think is urgent."

RESPONDENT 2 (Mike, Support Agent): "Yeah, and the ticket system doesn't help. Everything looks the same - red exclamation marks everywhere. I end up just working tickets in the order they came in, which probably isn't the most efficient approach."

INTERVIEWER: "What tools do you use for support?"

Jenny: "We have a help desk system, but it's not integrated with our product. So when a customer reports a bug, I have to manually check if it's a known issue, then update the ticket. It's a lot of back-and-forth."

Mike: "And the knowledge base is outdated. I'll find an article that seems relevant, but when I follow the steps, they don't match the current product. So I end up writing custom responses for every ticket instead of using templates."

INTERVIEWER: "What frustrates you most about your current process?"

Jenny: "The lack of context. Customers often don't provide enough information, so I have to ask follow-up questions. But by the time they respond, I've moved on to other tickets and lost the context. It's inefficient for everyone."

Mike: "And there's no way to see if similar issues have been reported before. I might spend 30 minutes solving a problem that someone else already solved last week. If we had better search or tagging, I could find those solutions quickly."

INTERVIEWER: "How do you measure success in your role?"

Jenny: "We're measured on response time and resolution time, but those metrics don't capture quality. I can close a ticket quickly by giving a generic response, but that doesn't solve the customer's problem. The real success is when a customer doesn't need to contact us again for the same issue."

Mike: "And there's no feedback loop. I don't know if my solutions actually helped the customer or if they just gave up and found another way. Without that feedback, I can't improve my responses."

INTERVIEWER: "What would make your job easier?"

Jenny: "Better integration between our tools. If the help desk could automatically check if an issue is known, or if the knowledge base could suggest relevant articles based on the ticket content, that would save a lot of time."

Mike: "And I need better search capabilities. Right now, I have to guess what keywords to use to find relevant information. If the system could understand the intent behind a ticket and suggest solutions, that would be amazing."
"""


def main():
    """Run examples of interview transcript analysis"""

    print("🎤 Interview Transcript Analysis Examples")
    print("=" * 60)

    # Example 1: Single Speaker
    print("\n📝 Example 1: Single Speaker Interview")
    print("-" * 40)
    result1 = analyze_interview_transcript(SINGLE_SPEAKER_TRANSCRIPT, "hybrid")

    if result1:
        print("\n🔍 Key Insights from Single Speaker:")
        for insight in result1['insights'][:3]:  # Show first 3 insights
            print(f"   • {insight['headline']}")

    # Example 2: Multiple Speakers
    print("\n\n📝 Example 2: Multiple Speakers Interview")
    print("-" * 40)
    result2 = analyze_interview_transcript(
        MULTIPLE_SPEAKERS_TRANSCRIPT, "hybrid")

    if result2:
        print("\n🔍 Key Insights from Multiple Speakers:")
        for insight in result2['insights'][:3]:  # Show first 3 insights
            print(f"   • {insight['headline']}")

    # Example 3: Structured Interview
    print("\n\n📝 Example 3: Structured Interview")
    print("-" * 40)
    result3 = analyze_interview_transcript(STRUCTURED_INTERVIEW, "hybrid")

    if result3:
        print("\n🔍 Key Insights from Structured Interview:")
        for insight in result3['insights'][:3]:  # Show first 3 insights
            print(f"   • {insight['headline']}")


if __name__ == "__main__":
    main()
