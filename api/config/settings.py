"""
Application settings and configuration constants.
Contains Flask and Dash settings, file paths, and other application-wide constants.
"""

import os

# Flask settings
FLASK_CONFIG = {
    'SEND_FILE_MAX_AGE_DEFAULT': 0,
    'JSON_AS_ASCII': False,
    'JSONIFY_MIMETYPE': 'application/json;charset=utf-8'
}

# Dash settings
DASH_CONFIG = {
    'url_base_pathname': '/',  # Keep at root
    'serve_locally': True,
    'compress': False,
    'update_title': None,
    'suppress_callback_exceptions': True,
    'assets_folder': 'assets',  # Local folder name
    'assets_url_path': '/',  # Set URL path to root
    'include_assets_files': True,
    'assets_ignore': '^(?!.*\.(js|css|png|jpg|jpeg|gif|ico)$).*$'
}

# Meta tags for responsive design
META_TAGS = [
    {"charset": "utf-8"},
    {
        "name": "viewport",
        "content": "width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0, user-scalable=no"
    },
    {"name": "apple-mobile-web-app-capable", "content": "yes"},
    {"name": "mobile-web-app-capable", "content": "yes"}
]

# File paths and directories
SURVEY_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")

# Data file patterns
DATA_FILE_PATTERNS = {
    'results': "results_*.json",
    'data': "data_*.csv",
    'questions': "questions.json"
}

# Graph settings
GRAPH_SETTINGS = {
    'comparison': {
        'height': 800,
        'width': '100%',
        'template': 'plotly_white',
        'show_legend': True,
        'legend_position': 'bottom'
    },
    'matrix': {
        'height': 800,
        'width': '100%',
        'template': 'plotly_white',
        'show_legend': True,
        'legend_position': 'right'
    },
    'deviation': {
        'height': 800,
        'width': '100%',
        'template': 'plotly_white',
        'show_legend': True,
        'legend_position': 'bottom'
    }
}

# Mobile breakpoints
MOBILE_BREAKPOINTS = {
    'max_width': 768,  # Maximum width for mobile view
    'min_width': 769   # Minimum width for desktop view
}

# Default values
DEFAULTS = {
    'language': 'English',
    'view_type': 'matrix',
    'result_format': 1,  # Default result format option
    'graph_controls': ['show_grid', 'show_error_bars']
}

# Cache settings
CACHE_CONFIG = {
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache',
    'CACHE_DEFAULT_TIMEOUT': 300
}

# Debug settings
DEBUG = False  # Set to False in production

# Application Settings
APP_SETTINGS = {
    'title': 'World Values Survey Analysis',
    'description': 'Interactive visualization of World Values Survey data',
    'debug': True,
    'host': '0.0.0.0',
    'port': 8080
}

# Data Settings
DATA_SETTINGS = {
    'default_language': 'English',
    'default_question': 'Q1',
    'scale_min': 1,
    'scale_max': 5,
    'missing_value': -1
}

# Cache Settings
CACHE_SETTINGS = {
    'timeout': 300,  # 5 minutes
    'directory': '.cache'
}

# External Links
EXTERNAL_LINKS = {
    'wvs': 'https://www.worldvaluessurvey.org/',
    'github': 'https://github.com/yourusername/wvs-analysis'
} 