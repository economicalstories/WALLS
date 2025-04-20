# -*- coding: utf-8 -*-
"""
Callbacks for the matrix view.
"""

from dash import Input, Output, State, html
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go
from typing import Dict, List, Optional, Tuple
import os

from .shared import load_survey_data, load_question_metadata, validate_languages
from api.views.matrix_view import create_matrix_graph
from api.data_processing.matrix_processor import merge_result_files
from api.state import store

def register_callbacks(app):
    """Register all callbacks related to the matrix view."""
    
    @app.callback(
        Output('matrix-graph', 'figure'),
        [
            Input('survey-select', 'value'),
            Input('model-select', 'value'),
            Input('language-select', 'value'),
            Input('matrix-hide-numbers', 'value'),
            Input('matrix-hide-colors', 'value')
        ],
        prevent_initial_call=True
    )
    def update_matrix_graph(
        survey_id: str,
        model_id: str,
        selected_languages: List[str],
        hide_numbers: bool,
        hide_colors: bool
    ) -> Dict:
        """Update matrix view graph based on selected survey, model, and languages.
        
        Args:
            survey_id: Selected survey ID
            model_id: Selected model ID
            selected_languages: List of selected language codes
            hide_numbers: Whether to hide numbers on the matrix
            hide_colors: Whether to hide colors on the matrix
            
        Returns:
            Updated figure dictionary for the matrix graph
        """
        print("\n=== Matrix View Update ===")
        print(f"Survey ID: {survey_id}")
        print(f"Model ID: {model_id}")
        print(f"Selected Languages: {selected_languages}")
        print(f"Hide Numbers: {hide_numbers}")
        print(f"Hide Colors: {hide_colors}")
        
        if not all([survey_id, model_id]) or not selected_languages:
            print("Missing required selections")
            raise PreventUpdate
            
        # Get paths to all relevant result files
        result_files = []
        base_path = os.path.join("data", survey_id, model_id)
        
        # Add primary result file
        primary_file = os.path.join(base_path, f"results_{model_id}.json")
        if os.path.exists(primary_file):
            result_files.append(primary_file)
            
        # Check for additional result files
        for file in os.listdir(base_path):
            if file.startswith("results_") and file.endswith(".json") and file != f"results_{model_id}.json":
                result_files.append(os.path.join(base_path, file))
                
        print(f"\nFound result files: {result_files}")
        
        # Load and merge data from all result files
        matrix_data, error = merge_result_files(result_files)
        if error:
            print(f"Error loading data: {error}")
            return go.Figure()
            
        if not matrix_data:
            print("No data available")
            return go.Figure()
            
        # Create matrix figure
        try:
            matrix_fig = create_matrix_graph(
                matrix_data=matrix_data,
                selected_languages=selected_languages,
                hide_color_scale=hide_colors,
                show_numbers=not hide_numbers,
                model_info={'name': model_id},
                survey_name=survey_id
            )
            print("Matrix figure created successfully")
            return matrix_fig
            
        except Exception as e:
            print(f"Error creating matrix figure: {str(e)}")
            import traceback
            traceback.print_exc()
            return go.Figure()
