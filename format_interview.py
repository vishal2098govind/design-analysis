#!/usr/bin/env python3
"""
Interview Transcript Formatter
Helps you format interview transcripts for optimal analysis
"""

import os
from pathlib import Path


def format_interview_transcript():
    """Interactive interview transcript formatter"""

    print("🎤 Interview Transcript Formatter")
    print("=" * 40)
    print("This tool helps you format interview transcripts for the design analysis system.")
    print()

    # Get interview metadata
    print("📋 Interview Information:")
    interview_title = input(
        "Interview title (e.g., 'User Interview - Project Management Tools'): ").strip()
    interview_type = input(
        "Type (single speaker/multiple speakers/focus group): ").strip().lower()

    # Get speaker information
    speakers = []
    if interview_type in ["multiple speakers", "focus group"]:
        print("\n👥 Speaker Information:")
        while True:
            name = input("Speaker name (or 'done' to finish): ").strip()
            if name.lower() == 'done':
                break
            role = input(f"Role for {name}: ").strip()
            speakers.append(f"{name} ({role})")
    else:
        name = input("Speaker name: ").strip()
        role = input("Speaker role: ").strip()
        speakers.append(f"{name} ({role})")

    # Get interview content
    print("\n📝 Interview Content:")
    print("Enter the interview transcript. Use 'Interviewer:' and speaker names to identify who's talking.")
    print("Type 'END' on a new line when finished.")
    print()

    lines = []
    while True:
        line = input()
        if line.strip().upper() == 'END':
            break
        lines.append(line)

    # Format the transcript
    formatted_transcript = format_transcript_content(
        interview_title,
        interview_type,
        speakers,
        lines
    )

    # Show the formatted result
    print("\n" + "="*50)
    print("✅ FORMATTED TRANSCRIPT")
    print("="*50)
    print(formatted_transcript)
    print("="*50)

    # Save option
    save = input("\n💾 Save to file? (y/N): ").strip().lower()
    if save == 'y':
        filename = input("Filename (without extension): ").strip()
        if not filename:
            filename = "interview_transcript"

        filepath = Path(f"{filename}.txt")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(formatted_transcript)

        print(f"✅ Saved to: {filepath.absolute()}")

    return formatted_transcript


def format_transcript_content(title, interview_type, speakers, lines):
    """Format the transcript content with proper structure"""

    # Create header
    header = f"{title}\n\n"

    # Add speaker context if multiple speakers
    if len(speakers) > 1:
        header += f"Participants: {', '.join(speakers)}\n\n"
    else:
        header += f"Participant: {speakers[0]}\n\n"

    # Process the content
    formatted_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check if line starts with a speaker identifier
        if any(line.startswith(speaker.split(' (')[0] + ':') for speaker in speakers):
            # Already formatted
            formatted_lines.append(line)
        elif line.startswith('Interviewer:'):
            # Already formatted
            formatted_lines.append(line)
        elif line.startswith('Q:') or line.startswith('Question:'):
            # Convert to Interviewer format
            formatted_lines.append(line.replace(
                'Q:', 'Interviewer:').replace('Question:', 'Interviewer:'))
        elif line.startswith('A:') or line.startswith('Answer:'):
            # Convert to speaker format
            if speakers:
                speaker_name = speakers[0].split(' (')[0]
                formatted_lines.append(line.replace(
                    'A:', f"{speaker_name}:").replace('Answer:', f"{speaker_name}:"))
        else:
            # Assume it's a continuation or needs speaker identification
            if speakers and not any(line.startswith(s) for s in ['Interviewer:', 'Q:', 'A:', 'Question:', 'Answer:']):
                # Add speaker name if it's a response
                speaker_name = speakers[0].split(' (')[0]
                formatted_lines.append(f"{speaker_name}: \"{line}\"")
            else:
                formatted_lines.append(line)

    return header + '\n'.join(formatted_lines)


def quick_format_example():
    """Show a quick formatting example"""

    print("📖 Quick Formatting Example:")
    print("=" * 40)

    example = """
User Interview - Single Speaker (Sarah, 34, Product Manager)

Interviewer: "Can you tell me about your experience with project management tools?"

Sarah: "I've been using various project management tools for about 8 years now. Honestly, most of them are way too complicated for what I actually need. I spend more time setting up the tool than actually managing my projects."

Interviewer: "What specific challenges do you face?"

Sarah: "The biggest issue is that these tools assume I have time to learn complex workflows. I just want to quickly add a task, assign it to someone, and see the status. But instead, I have to navigate through multiple screens, set up custom fields, and configure workflows that I'll never use."
"""

    print(example)
    print("\nKey formatting rules:")
    print("✅ Use 'Interviewer:' for questions")
    print("✅ Use 'Speaker Name:' for responses")
    print("✅ Include context in the title")
    print("✅ Preserve natural language")
    print("✅ Include pain points and desires")


def main():
    """Main function"""

    print("🎤 Interview Transcript Formatter")
    print("=" * 40)
    print("1. Format a new interview transcript")
    print("2. See formatting example")
    print("3. Exit")

    choice = input("\nChoose an option (1-3): ").strip()

    if choice == '1':
        format_interview_transcript()
    elif choice == '2':
        quick_format_example()
    elif choice == '3':
        print("Goodbye!")
    else:
        print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
