"""
Utility functions for formatting dates, text, and display labels.
"""

from datetime import datetime
import textwrap
from dash import html

def format_timestamp(timestamp):
    """Convert timestamp string to friendly date format"""
    try:
        # Parse the timestamp format YYYYMMDD_HHMMSS
        date_obj = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
        # Use string formatting that works across platforms
        day = str(int(date_obj.strftime("%d")))  # Remove leading zero
        month = date_obj.strftime("%B")
        year = date_obj.strftime("%Y")
        return f"{day} {month} {year}"
    except ValueError:
        try:
            # Try just the date part if time part fails
            date_str = timestamp.split('_')[0]
            date_obj = datetime.strptime(date_str, "%Y%m%d")
            day = str(int(date_obj.strftime("%d")))  # Remove leading zero
            month = date_obj.strftime("%B")
            year = date_obj.strftime("%Y")
            return f"{day} {month} {year}"
        except ValueError:
            return timestamp

def get_friendly_model_name(model_name):
    """Convert model name to friendly display name"""
    # Extract date if present
    if '-' in model_name:
        base_name, version = model_name.rsplit('-', 1)
        try:
            # Try to parse date from version (YYMM format)
            date = datetime.strptime(version, "%y%m")
            return f"{base_name.upper()} ({date.strftime('%b %Y')})"
        except ValueError:
            return model_name.upper()
    return model_name.upper()

def format_result_option(format_type, lang_summary, timestamp):
    """Format result option label based on specified format"""
    date = format_timestamp(timestamp)
    
    if format_type == 1:
        # Option 1: Compact format - "Hebrew (6 Apr)" or "51 langs (6 Apr)"
        return f"{lang_summary} ({date})"
    elif format_type == 2:
        # Option 2: Minimal format - just show language info, date on hover
        return lang_summary
    elif format_type == 3:
        # Option 3: Date first - "6 Apr: Hebrew" or "6 Apr: 51 langs"
        return f"{date}: {lang_summary}"
    elif format_type == 4:
        # Option 4: Two lines - language on top, date below (using HTML)
        return html.Div([
            html.Div(lang_summary, style={'fontWeight': 'bold'}),
            html.Div(date, style={'fontSize': 'smaller', 'color': '#666'})
        ])
    else:
        # Default format
        return f"{lang_summary}, {date}"

def wrap_text(text, width=30):
    """Wrap text to specified width"""
    return textwrap.shorten(text, width=width, placeholder="...")

def get_scale_labels(question):
    """Convert scale labels from any format to a list of labels."""
    scale_labels = question['scale_labels']
    if isinstance(scale_labels, dict):
        # If it's a min/max format
        if 'min' in scale_labels and 'max' in scale_labels:
            num_points = question['scale_max'] - question['scale_min'] + 1
            if num_points == 2:
                return [scale_labels['min'], scale_labels['max']]
            # For scales > 2 points, create intermediate labels
            labels = [scale_labels['min']]
            for i in range(num_points - 2):
                labels.append(f"Level {i + 2}")
            labels.append(scale_labels['max'])
            return labels
        # If it's a numbered format (e.g., "1": "Very good", "4": "Very bad")
        else:
            labels = [""] * (question['scale_max'] - question['scale_min'] + 1)
            for i in range(question['scale_min'], question['scale_max'] + 1):
                if str(i) in scale_labels:
                    labels[i - question['scale_min']] = scale_labels[str(i)]
                else:
                    labels[i - question['scale_min']] = f"Level {i}"
            return labels
    return [str(i) for i in range(question['scale_min'], question['scale_max'] + 1)] 