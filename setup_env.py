#!/usr/bin/env python3
"""
Environment Setup Script
Helps you set up the required environment variables for the design analysis project
"""

import os
import getpass
from pathlib import Path


def setup_environment():
    """Interactive setup for environment variables"""

    print("🔧 Design Analysis Environment Setup")
    print("=" * 40)

    # Check if .env file already exists
    env_file = Path(".env")
    if env_file.exists():
        print("⚠️  .env file already exists!")
        overwrite = input(
            "Do you want to overwrite it? (y/N): ").lower().strip()
        if overwrite != 'y':
            print("Setup cancelled.")
            return

    # Get OpenAI API Key
    print("\n🔑 OpenAI API Key Setup")
    print("You need an OpenAI API key to use this project.")
    print("Get one from: https://platform.openai.com/api-keys")

    api_key = getpass.getpass(
        "Enter your OpenAI API key (input will be hidden): ").strip()

    if not api_key:
        print("❌ API key is required!")
        return

    # Optional configurations
    print("\n⚙️  Optional Configuration")
    print("Press Enter to use defaults, or enter custom values:")

    model = input(
        f"OpenAI Model (default: gpt-4-turbo-preview): ").strip() or "gpt-4-turbo-preview"
    temperature = input(f"Temperature (default: 0.1): ").strip() or "0.1"
    max_chunks = input(
        f"Max chunks per analysis (default: 50): ").strip() or "50"
    confidence = input(
        f"Confidence threshold (default: 0.7): ").strip() or "0.7"
    max_insights = input(
        f"Max insights per pattern (default: 3): ").strip() or "3"
    api_host = input(f"API Host (default: 0.0.0.0): ").strip() or "0.0.0.0"
    api_port = input(f"API Port (default: 8000): ").strip() or "8000"
    debug = input(f"Debug mode (default: false): ").strip().lower() or "false"

    # Create .env content
    env_content = f"""# OpenAI Configuration (REQUIRED)
OPENAI_API_KEY={api_key}

# Model Configuration (optional - defaults provided)
OPENAI_MODEL={model}
TEMPERATURE={temperature}

# Analysis Configuration (optional - defaults provided)
MAX_CHUNKS_PER_ANALYSIS={max_chunks}
CONFIDENCE_THRESHOLD={confidence}
MAX_INSIGHTS_PER_PATTERN={max_insights}

# API Configuration (optional - defaults provided)
API_HOST={api_host}
API_PORT={api_port}
DEBUG={debug}
"""

    # Write .env file
    try:
        with open(".env", "w") as f:
            f.write(env_content)
        print("\n✅ .env file created successfully!")

        # Test the setup
        print("\n🧪 Testing environment setup...")
        os.environ["OPENAI_API_KEY"] = api_key

        # Try to import and test
        try:
            from dotenv import load_dotenv
            load_dotenv()

            if os.getenv("OPENAI_API_KEY"):
                print("✅ Environment variables loaded successfully!")
                print("✅ You can now run the design analysis tools!")
            else:
                print("❌ Environment variables not loaded properly")

        except ImportError:
            print("⚠️  python-dotenv not found. Make sure to install requirements:")
            print("   pip install -r requirements.txt")

    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return

    print("\n📋 Next Steps:")
    print("1. Activate your virtual environment: source venv/bin/activate")
    print("2. Test the setup: python test_output_parsers.py")
    print("3. Run the API: python api.py")
    print("4. Or use the analysis directly: python agentic_analysis.py")


if __name__ == "__main__":
    setup_environment()
