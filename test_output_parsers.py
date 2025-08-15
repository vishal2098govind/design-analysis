#!/usr/bin/env python3
"""
Test script to verify output parsers are working correctly
"""

import os
from dotenv import load_dotenv
from agentic_analysis import run_agentic_analysis

# Load environment variables
load_dotenv()

def test_output_parsers():
    """Test the output parsers with sample data"""
    
    sample_data = """
    User Interview Transcript:
    - "I just want to get this done quickly. I don't need all these fancy features."
    - "The interface is so cluttered, I can't find what I'm looking for."
    - "I spend more time figuring out how to use the tool than actually using it."
    - "When I see too many options, I get overwhelmed and just close the app."
    - "The simpler tools are the ones I use most often."
    """
    
    print("Testing Output Parsers in Agentic Analysis...")
    print("=" * 50)
    
    try:
        result = run_agentic_analysis(sample_data)
        
        print("✅ Analysis completed successfully!")
        print(f"✅ Generated {len(result['chunks'])} chunks")
        print(f"✅ Generated {len(result['inferences'])} inferences")
        print(f"✅ Generated {len(result['patterns'])} patterns")
        print(f"✅ Generated {len(result['insights'])} insights")
        print(f"✅ Generated {len(result['design_principles'])} design principles")
        
        print("\n📋 Sample Output Structure:")
        print(f"Chunks: {type(result['chunks'])} - {len(result['chunks'])} items")
        if result['chunks']:
            print(f"  First chunk keys: {list(result['chunks'][0].keys())}")
        
        print(f"Inferences: {type(result['inferences'])} - {len(result['inferences'])} items")
        if result['inferences']:
            print(f"  First inference keys: {list(result['inferences'][0].keys())}")
        
        print(f"Patterns: {type(result['patterns'])} - {len(result['patterns'])} items")
        if result['patterns']:
            print(f"  First pattern keys: {list(result['patterns'][0].keys())}")
        
        print(f"Insights: {type(result['insights'])} - {len(result['insights'])} items")
        if result['insights']:
            print(f"  First insight keys: {list(result['insights'][0].keys())}")
        
        print(f"Design Principles: {type(result['design_principles'])} - {len(result['design_principles'])} items")
        if result['design_principles']:
            print(f"  First principle keys: {list(result['design_principles'][0].keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return False

if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("Please set your OpenAI API key in a .env file")
    else:
        test_output_parsers()
