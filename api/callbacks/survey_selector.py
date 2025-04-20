# -*- coding: utf-8 -*-
"""
Callbacks for survey selector component.
"""

import os
import json
from typing import List, Dict, Optional
from dash import Input, Output, State

from api.config.settings import SURVEY_DIR

def register_callbacks(app):
    """Register all callbacks for survey selector."""
    
    @app.callback(
        [Output('model-dropdown', 'options'),
         Output('model-dropdown', 'value')],
        [Input('survey-dropdown', 'value')],
        prevent_initial_call=True
    )
    def update_model_options(survey_id: str) -> tuple[List[Dict], Optional[str]]:
        """
        Update model dropdown options when survey is selected.
        
        Args:
            survey_id: Selected survey ID
            
        Returns:
            Tuple of (model_options, selected_model)
            - model_options: List of dictionaries with label and value for each model
            - selected_model: First model ID or None if no models available
        """
        if not survey_id:
            return [], None
            
        survey_path = os.path.join(SURVEY_DIR, survey_id)
        if not os.path.exists(survey_path):
            return [], None
            
        # Find all data directories (data_*)
        model_dirs = [d for d in os.listdir(survey_path) 
                     if os.path.isdir(os.path.join(survey_path, d)) 
                     and d.startswith('data_')]
                     
        # Extract model IDs and create options
        model_ids = [d.replace('data_', '') for d in model_dirs]
        options = [{'label': model_id, 'value': model_id} for model_id in model_ids]
        
        # Return options and first model as default
        return options, model_ids[0] if model_ids else None 