"""
Common footer component for graph visualizations.
"""

import os
import json
from api.config.settings import SURVEY_DIR
from api.config.styles import COLORS, FONTS
from dash import html
from datetime import datetime

def get_survey_info(survey_name):
    """Get survey information from questions.json"""
    questions_file = os.path.join(SURVEY_DIR, survey_name, 'questions.json')
    if os.path.exists(questions_file):
        with open(questions_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return {
                'name': data.get('survey', {}).get('name', ''),
                'description': data.get('survey', {}).get('description', ''),
                'copyright': data.get('survey', {}).get('copyright', '')
            }
    return {}

def get_language_stats(data, selected_languages):
    """Calculate language statistics"""
    lang_stats = {}
    for lang in selected_languages:
        samples = []
        for q in data:
            stats = q.get('language_stats', {}).get(lang, {})
            if stats.get('count'):
                samples.append(stats['count'])
        if samples:
            lang_stats[lang] = {
                'avg_samples': sum(samples) / len(samples),
                'total_samples': sum(samples)
            }
    return lang_stats

def create_graph_footer(survey_name=None, model_info=None, data=None, selected_languages=None):
    """Create footer text with comprehensive information."""
    survey_info = get_survey_info(survey_name) if survey_name else {}
    
    # Model and language information
    model_text = ""
    if model_info:
        if isinstance(model_info, dict):
            model_text = f"Model: {model_info.get('name', 'Unknown')}"
        else:
            model_text = f"Model: {model_info}"
    
    # Language statistics
    lang_stats = get_language_stats(data, selected_languages) if data and selected_languages else {}
    lang_text = ""
    if lang_stats:
        avg_samples = sum(s['avg_samples'] for s in lang_stats.values()) / len(lang_stats)
        lang_text = f"{len(selected_languages)} languages selected • Avg. samples per language: {avg_samples:.1f}"
    
    # Source information
    source_text = "Questions adapted from the World Values Survey (WVS) Wave 7 (2017-2022) Master Questionnaire, published by the World Values Survey Association (www.worldvaluessurvey.org)."
    
    # Combine all information with proper wrapping
    footer_text = (
        f"{model_text} • {lang_text}" if model_text and lang_text else 
        (model_text or lang_text)
    )
    
    if source_text:
        footer_text = f"{footer_text}<br>{source_text}" if footer_text else source_text
    
    return {
        'text': footer_text,
        'x': 0.5,  # Center horizontally
        'y': -0.15,  # Position below plot area
        'xref': 'paper',
        'yref': 'paper',
        'showarrow': False,
        'font': {
            'size': FONTS['size']['small'],
            'color': COLORS['dark']
        },
        'align': 'center',
        'xanchor': 'center',
        'yanchor': 'top'
    } 