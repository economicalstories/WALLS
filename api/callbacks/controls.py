# -*- coding: utf-8 -*-
"""
Core control callbacks for the dashboard.
Handles survey, model, and language selection.
"""

import os
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dash import Input, Output, State, html
from dash.exceptions import PreventUpdate
import json

from .shared import load_survey_data
from ..state.store import get_state
from api.config.settings import SURVEY_DIR

def get_available_surveys() -> List[str]:
    """Get list of available surveys."""
    print("\n=== Looking for Available Surveys ===")
    
    # Use the project root directory and look for 'data' subdirectory
    project_root = Path(__file__).parent.parent.parent
    data_dir = project_root / 'data'
    print(f"Project root path: {project_root}")
    print(f"Data directory path: {data_dir}")
    print(f"Data directory exists: {data_dir.exists()}")
    
    if not data_dir.exists():
        print("WARNING: Data directory not found!")
        return []
        
    # List all directories in the data directory
    print("\nContents of data directory:")
    try:
        for item in data_dir.iterdir():
            print(f"- {item.name} ({'directory' if item.is_dir() else 'file'})")
        
        # Find survey directories (any directory in the data folder)
        surveys = [d.name for d in data_dir.iterdir() 
                  if d.is_dir()]
        
        print(f"\nFound surveys: {surveys}")
        return surveys
    except Exception as e:
        print(f"Error reading data directory: {e}")
        import traceback
        print(traceback.format_exc())
        return []

def get_available_models(survey_id: str) -> List[Dict[str, str]]:
    """Get list of available models for a given survey."""
    print(f"\n=== Looking for Models in Survey: {survey_id} ===")
    if not survey_id:
        print("No survey_id provided")
        return []
        
    project_root = Path(__file__).parent.parent.parent
    survey_dir = project_root / 'data' / survey_id
    print(f"Survey directory path: {survey_dir}")
    print(f"Directory exists: {survey_dir.exists()}")
    
    if not survey_dir.exists():
        print(f"WARNING: Survey directory not found: {survey_dir}")
        return []
        
    try:
        # List all directories in the survey directory
        print("\nContents of survey directory:")
        for item in survey_dir.iterdir():
            print(f"- {item.name} ({'directory' if item.is_dir() else 'file'})")
        
        # Get directories that match the expected model directory names
        models = [d.name for d in survey_dir.iterdir() 
                 if d.is_dir() 
                 and (d.name == 'data_gpt-3.5-turbo' or d.name == 'data_gpt-4o-2024-08-06')]
        
        print(f"Found model directories: {models}")
        
        # Create options with proper display names
        options = [
            {
                'label': model_dir.replace('data_gpt-', 'GPT-'),
                'value': model_dir
            }
            for model_dir in sorted(models)
        ]
        
        print(f"Processed model options: {options}")
        return options
    except Exception as e:
        print(f"Error reading survey directory: {e}")
        import traceback
        print(traceback.format_exc())
        return []

def register_callbacks(app):
    """Register core control callbacks."""
    print("\n=== Registering Control Callbacks ===")
    
    @app.callback(
        [Output('survey-select', 'options'),
         Output('survey-select', 'value')],
        [Input('controls-trigger', 'children')],
        prevent_initial_call=False
    )
    def update_survey_options(trigger_value):
        """Update survey dropdown options."""
        print("\n=== Updating Survey Options ===")
        print(f"Trigger value: {trigger_value}")
        
        # Force a survey update
        print("Forcing survey update...")
        surveys = get_available_surveys()
        print(f"Available surveys: {surveys}")
        
        if not surveys:
            print("No surveys found - returning empty options")
            return [], None
            
        options = [{'label': survey, 'value': survey} for survey in sorted(surveys)]
        print(f"Created survey options: {options}")
        print(f"Default survey: {surveys[0]}")
        return options, surveys[0]
    
    print("Survey callback registered")
    
    @app.callback(
        [Output('model-select', 'options'),
         Output('model-select', 'value')],
        [Input('survey-select', 'value')],
        prevent_initial_call=True
    )
    def update_model_options(survey_id):
        """Update model dropdown options."""
        print(f"\n=== Updating Model Options for Survey: {survey_id} ===")
        
        if not survey_id:
            print("No survey selected - returning empty options")
            return [], None
            
        options = get_available_models(survey_id)
        print(f"Found model options: {options}")
        
        if not options:
            print("No models found - returning empty options")
            return [], None
            
        print(f"Default model: {options[0]['value']}")
        return options, options[0]['value']
    
    @app.callback(
        Output('language-select', 'options'),
        Output('language-select', 'value'),
        Input('survey-select', 'value'),
        Input('model-select', 'value'),
        prevent_initial_call=True
    )
    def update_language_options(
        survey_id: Optional[str],
        model_id: Optional[str]
    ) -> Tuple[List[Dict], List[str]]:
        """Update language checklist options based on selected survey and model."""
        print("\n=== Updating Language Options ===")
        print(f"Selected survey: {survey_id}")
        print(f"Selected model: {model_id}")
        
        if not all([survey_id, model_id]):
            print("Missing survey_id or model_id")
            raise PreventUpdate
            
        try:
            # Load survey data
            data, error = load_survey_data(survey_id, model_id)
            if error:
                print(f"Error loading survey data: {error}")
                return [], []
                
            if not data:
                print("No data loaded")
                return [], []
                
            print(f"Loaded {len(data)} questions")
            
            try:
                # Get valid languages from the root quality_metrics in results
                if isinstance(data, list) and len(data) > 0:
                    # First try to get from first question's quality_metrics
                    quality_metrics = data[0].get('quality_metrics', {})
                    valid_languages = quality_metrics.get('valid_languages', [])
                    
                    # If not found, try to get from the results data structure
                    if not valid_languages and hasattr(data, 'quality_metrics'):
                        valid_languages = data.quality_metrics.get('valid_languages', [])
                
                # If still not found, try loading the results file directly
                if not valid_languages:
                    print("Trying to load results files directly...")
                    project_root = Path(__file__).parent.parent.parent
                    results_dir = project_root / 'data' / survey_id / model_id
                    if results_dir.exists():
                        result_files = [f for f in results_dir.iterdir() 
                                      if f.name.startswith('results_') and f.name.endswith('.json')]
                        
                        # Consolidate valid languages from all results files
                        all_valid_languages = set()
                        for result_file in result_files:
                            print(f"Loading results from: {result_file}")
                            try:
                                with open(result_file, 'r', encoding='utf-8') as f:
                                    results_data = json.load(f)
                                    file_valid_languages = results_data.get('quality_metrics', {}).get('valid_languages', [])
                                    if file_valid_languages:
                                        all_valid_languages.update(file_valid_languages)
                                        print(f"Added {len(file_valid_languages)} languages from {result_file}")
                            except Exception as e:
                                print(f"Error reading {result_file}: {e}")
                                continue
                        
                        valid_languages = sorted(list(all_valid_languages))
                        print(f"Consolidated {len(valid_languages)} unique languages from all results files")
                
                if not valid_languages:
                    print("No valid languages found in any results files")
                    return [], []
                
                print(f"\nFound {len(valid_languages)} valid languages: {sorted(valid_languages)}")
                
                # Create options for valid languages
                options = [
                    {'label': lang, 'value': lang}
                    for lang in sorted(valid_languages)
                ]
                
                # All valid languages are selected by default
                default_languages = valid_languages
                
                print(f"\nAll language options: {options}")
                print(f"Default selected languages: {default_languages}")
                
                return options, default_languages
                
            except Exception as e:
                print(f"Error processing valid languages: {str(e)}")
                import traceback
                traceback.print_exc()
                return [], []
            
        except Exception as e:
            print(f"Error updating language options: {str(e)}")
            import traceback
            traceback.print_exc()
            return [], []
    
    @app.callback(
        Output('about-modal', 'is_open'),
        [Input('about-link', 'n_clicks'), Input('close-about-modal', 'n_clicks')],
        [State('about-modal', 'is_open')],
        prevent_initial_call=True
    )
    def toggle_about_modal(about_clicks, close_clicks, is_open):
        """Toggle the about modal visibility."""
        if about_clicks or close_clicks:
            return not is_open
        return is_open 