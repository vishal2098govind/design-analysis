# Environment Variables Setup

## Required Environment Variables

The design analysis project requires the following environment variables to be set:

### 1. Create a `.env` file

Create a `.env` file in the root directory of the project with the following content:

```bash
# OpenAI Configuration (REQUIRED)
OPENAI_API_KEY=your_openai_api_key_here

# Model Configuration (optional - defaults provided)
OPENAI_MODEL=gpt-4-turbo-preview
TEMPERATURE=0.1

# Analysis Configuration (optional - defaults provided)
MAX_CHUNKS_PER_ANALYSIS=50
CONFIDENCE_THRESHOLD=0.7
MAX_INSIGHTS_PER_PATTERN=3

# API Configuration (optional - defaults provided)
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false
```

### 2. Get Your OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign in or create an account
3. Navigate to "API Keys" in the left sidebar
4. Click "Create new secret key"
5. Copy the generated key
6. Replace `your_openai_api_key_here` in the `.env` file with your actual API key

### 3. Environment Variables Explained

#### Required Variables:
- **`OPENAI_API_KEY`**: Your OpenAI API key (required for all AI functionality)

#### Optional Variables (with defaults):
- **`OPENAI_MODEL`**: The OpenAI model to use (default: `gpt-4-turbo-preview`)
- **`TEMPERATURE`**: Controls randomness in AI responses (default: `0.1`)
- **`MAX_CHUNKS_PER_ANALYSIS`**: Maximum chunks to process (default: `50`)
- **`CONFIDENCE_THRESHOLD`**: Minimum confidence for outputs (default: `0.7`)
- **`MAX_INSIGHTS_PER_PATTERN`**: Max insights per pattern (default: `3`)
- **`API_HOST`**: Host for the API server (default: `0.0.0.0`)
- **`API_PORT`**: Port for the API server (default: `8000`)
- **`DEBUG`**: Enable debug mode (default: `false`)

### 4. Verify Setup

After creating the `.env` file, you can test if everything is working:

```bash
# Activate virtual environment
source venv/bin/activate

# Test the output parsers
python test_output_parsers.py
```

### 5. Security Notes

- **Never commit your `.env` file to version control**
- The `.env` file is already in `.gitignore` to prevent accidental commits
- Keep your API key secure and don't share it publicly
- Consider using environment-specific API keys for development vs production

### 6. Troubleshooting

If you get errors about missing environment variables:

1. Make sure the `.env` file is in the project root directory
2. Verify the `OPENAI_API_KEY` is set correctly
3. Check that `python-dotenv` is installed (it should be in requirements.txt)
4. Ensure the virtual environment is activated
5. Try restarting your terminal/IDE after creating the `.env` file
