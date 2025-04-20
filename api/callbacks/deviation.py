# -*- coding: utf-8 -*-
"""
Deviation analysis callbacks module.

Handles:
- Deviation analysis updates
- Deviation-specific controls
"""
from typing import Dict, List, Optional, Tuple

from dash import Input, Output, Dash
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go

from .shared import load_survey_data
from api.views.deviation_view import create_deviation_graph

def register_callbacks(app: Dash) -> None:
    """Register all callbacks related to deviation analysis."""
    
    @app.callback(
        Output('deviation-graph', 'figure'),
        [
            Input('survey-select', 'value'),
            Input('model-select', 'value'),
            Input('language-select', 'value'),
            Input('deviation-show-numbers', 'value')
        ],
        prevent_initial_call=True
    )
    def update_deviation_graph(
        survey_id: str,
        model_id: str,
        selected_languages: List[str],
        show_numbers: List[str]
    ) -> Dict:
        """Update deviation analysis graph based on selected survey, model, and languages.
        
        Args:
            survey_id: Selected survey ID
            model_id: Selected model ID
            selected_languages: List of selected language codes
            show_numbers: List containing 'show' if numbers should be displayed
            
        Returns:
            Updated figure dictionary for the deviation graph
        """
        if not all([survey_id, model_id]) or not selected_languages:
            raise PreventUpdate
            
        # Load survey data
        data, error = load_survey_data(survey_id, model_id)
        if error:
            print(f"Error loading survey data: {error}")
            return {}
            
        # No need to filter data - the view will handle language filtering
        
        # Create model info
        total_responses = sum(q.get('total_responses', 0) for q in data)
        model_info = {
            'name': model_id,
            'call_count': sum(q.get('model_stats', {}).get('total_calls', 0) for q in data),
            'avg_tokens': (
                sum(q.get('model_stats', {}).get('total_tokens', 0) for q in data) / total_responses
                if total_responses > 0 else 0
            )
        }
        
        try:
            return create_deviation_graph(
                data=data,
                selected_languages=selected_languages,
                show_numbers=bool(show_numbers and 'show' in show_numbers),
                model_info=model_info,
                survey_name=survey_id
            )
        except Exception as e:
            print(f"Error creating deviation graph: {e}")
            import traceback
            traceback.print_exc()
            return {}
