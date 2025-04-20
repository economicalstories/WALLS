"""
Configuration settings for the survey tools
"""

# API configuration
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

# Survey settings
DEFAULT_NUM_SAMPLES = 1
VERIFICATION_THRESHOLD = 4.0  # Minimum score for non-English responses

# File paths and directories
SURVEY_NAME = "World Values Survey"  # This can be changed to any survey name
SURVEYS_DIR = f"data/{SURVEY_NAME}"
DATA_DIR = f"data/{SURVEY_NAME}"
PROCESSED_DIR = "processed"

# Response validation
MIN_RESPONSE_LENGTH = 1
MAX_RESPONSE_LENGTH = 1000

# Rate limiting
REQUESTS_PER_MINUTE = 50
MIN_DELAY_BETWEEN_REQUESTS = 1.2  # seconds 