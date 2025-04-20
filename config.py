"""
Global configuration settings for WALLS.
Survey-specific settings should be placed in api/surveys/<survey_id>/config.json
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI API Configuration
API_KEY = os.getenv('OPENAI_API_KEY')
MODEL_NAME = os.getenv('OPENAI_MODEL', 'gpt-4o')  # Default to GPT-4 if not specified
#gpt-4-turbo
#gpt-4
#gpt-3.5-turbo


API_DELAY = float(os.getenv('API_DELAY', '0'))  # Delay between API calls in seconds

# Default settings (can be overridden in survey config)
DEFAULT_LANGUAGES = ['English']  # Default to English only
DEFAULT_NUM_TRIALS = 1  # Default to single trial
USE_TRANSLATION = True  # Whether to use translation for non-English languages

# Get the API key from environment variables
if API_KEY is None:
    raise ValueError("OpenAI API key not found. Make sure it's set in the .env file or as an environment variable named OPENAI_API_KEY.")

# --- Direct Configuration Settings ---
# Edit these values directly to control the script's behavior for your run.

# Number of times to run each question
NUM_TRIALS = DEFAULT_NUM_TRIALS

# Whether to translate prompts (True/False)
USE_TRANSLATION = USE_TRANSLATION

# List of languages to run the survey in.
# This list is derived from the WVS-7 (2017-2022) dataset PDF.
LANGUAGES = DEFAULT_LANGUAGES

# --- End of Direct Configuration Settings ---

# Note: The IS_PRODUCTION flag and separate _TEST/_PROD variables have been removed.
