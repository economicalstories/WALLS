"""
Survey selector component for choosing which survey to analyze.
"""

from dash import html, dcc, Output, Input
import os
import glob
import json
from datetime import datetime
from api.config.styles import COLORS, FONTS, COMPONENT_STYLES
from api.config.settings import SURVEY_DIR

def get_survey_name(survey_id):
    """Get friendly name for survey."""
    # Since we're using full names in directory structure, just return as is
    return survey_id

def get_available_surveys():
    """Get list of available surveys with proper names."""
    surveys = []
    for survey_dir in glob.glob(os.path.join(SURVEY_DIR, "*")):
        if os.path.isdir(survey_dir):
            survey_id = os.path.basename(survey_dir)
            # Only add if it has data directories
            data_dirs = [d for d in os.listdir(survey_dir) 
                        if os.path.isdir(os.path.join(survey_dir, d)) and d.startswith('data_')]
            if data_dirs:
                surveys.append({
                    'label': survey_id,  # Use the actual directory name as both label and value
                    'value': survey_id
                })
    return sorted(surveys, key=lambda x: x['label'])

def get_available_models(survey_name):
    """Get a list of available models that have data directories for a given survey.
    
    Args:
        survey_name (str): Name of the survey to get models for
        
    Returns:
        list: List of models that have results available
    """
    models = set()
    survey_dir = os.path.join(SURVEY_DIR, survey_name)
    
    if not os.path.exists(survey_dir):
        print(f"Survey directory does not exist: {survey_dir}")
        return []
    
    # Look for data directories
    for item in os.listdir(survey_dir):
        full_path = os.path.join(survey_dir, item)
        if os.path.isdir(full_path) and item.startswith('data_'):
            # Keep the full directory name as the value
            print(f"Found model directory: {item}")
            models.add(item)
    
    model_list = sorted(list(models))
    print(f"Available models for {survey_name}: {model_list}")
    return [{'label': model.replace('data_', ''), 'value': model} for model in model_list]

def create_survey_selector(app=None):
    """Create the survey selector component."""
    # Get initial surveys
    available_surveys = get_available_surveys()
    print(f"Available surveys: {available_surveys}")
    
    # Get initial value - first survey if available
    initial_survey = available_surveys[0]['value'] if available_surveys else None
    initial_models = get_available_models(initial_survey) if initial_survey else []
    initial_model = initial_models[0]['value'] if initial_models else None
    print(f"Initial survey: {initial_survey}, Initial model: {initial_model}")

    # Create the selector component
    selector = html.Div([
        html.Div([
            html.Label('Survey:', style={'font-weight': 'bold'}),
            dcc.Dropdown(
                id='survey-dropdown',
                options=available_surveys,
                value=initial_survey,
                clearable=False,
                style={'width': '100%'}
            )
        ], style={'margin-bottom': '10px'}),
        
        html.Div([
            html.Label('Model:', style={'font-weight': 'bold'}),
            dcc.Dropdown(
                id='model-dropdown',
                options=initial_models,
                value=initial_model,
                clearable=False,
                style={'width': '100%'}
            )
        ])
    ], style={'padding': '10px'})

    # Register callback if app is provided
    if app:
        @app.callback(
            [Output('model-dropdown', 'options'),
             Output('model-dropdown', 'value')],
            [Input('survey-dropdown', 'value')]
        )
        def update_model_options(selected_survey):
            """Update available models when survey is changed"""
            if not selected_survey:
                return [], None
            
            models = get_available_models(selected_survey)
            return models, models[0]['value'] if models else None

    return selector 