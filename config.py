# config.py

import os
from dotenv import load_dotenv

# Load environment variables (primarily for API Key)
load_dotenv()

# Get the API key from environment variables
API_KEY = os.getenv("OPENAI_API_KEY")
if API_KEY is None:
    raise ValueError("OpenAI API key not found. Make sure it's set in the .env file or as an environment variable named OPENAI_API_KEY.")

# --- Direct Configuration Settings ---
# Edit these values directly to control the script's behavior for your run.

# Model to use for API calls (e.g., "gpt-4", "gpt-3.5-turbo")
MODEL_NAME = "gpt-4o"

# Number of times to run each question
NUM_TRIALS = 1 # Set to 1 or 2 for quick tests, higher (e.g., 10, 50, 100) for full runs

# Delay between API calls in seconds (to avoid rate limits)
API_DELAY = 0

# Whether to translate prompts (True/False)
USE_TRANSLATION = True

# List of languages to run the survey in.
# This list is derived from the WVS-7 (2017-2022) dataset PDF.
LANGUAGES = [
    "English",
    "Catalan",
    "Spanish",
    "French"
    # "Armenian",
    # "Bengali",
    # "Portuguese",
    # "Mandarin Chinese",
    # "Greek",
    # "Turkish",
    # "Czech",
    # "Arabic",
    # "Amharic",
    # "Oromo",
    # "Tigris",
    # "German",
    # "Cantonese",
    # "Hindu",
    # "Indonesian",
    # "Persian",
    # "Japanese",
    # "Kazakh",
    # "Russian",
    # "Swahili",
    # "Kirghiz",
    # "Malay",
    # "Dhivehi",
    # "Mongolian",
    # "Burmese",
    # "Dutch",
    # "Hausa",
    # "Igbo",
    # "Yoruba",
    # "Urdu",
    # "Bikol",
    # "Cebuano",
    # "Filipino",
    # "Ikolo",
    # "Tausug",
    # "Waray",
    # "Hiligaynon",
    # "Romanian",
    # "Serbian",
    # "Slovak",
    # "Korean",
    # "Tajik",
    # "Thai",
    # "Ukrainian",
    # "Uzbek",
    # "Vietnamese",
    # "Shona",
    # "Ndebele"
]

# --- End of Direct Configuration Settings ---

# Note: The IS_PRODUCTION flag and separate _TEST/_PROD variables have been removed.
