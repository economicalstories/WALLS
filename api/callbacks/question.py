# -*- coding: utf-8 -*-
"""
Question view callbacks.
Handles question selection and display updates.
"""

from typing import Dict, List, Optional, Tuple
import os
import json

from dash import Input, Output, State, Dash
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go

from .shared import load_survey_data, load_question_metadata, validate_languages
from api.views.question_view import create_question_graph
from api.config.settings import SURVEY_DIR

def register_callbacks(app: Dash) -> None:
    """Register all question view callbacks."""
    
    @app.callback(
        [
            Output('question-tab-select', 'options'),
            Output('question-tab-select', 'value')
        ],
        [
            Input('survey-select', 'value'),
            Input('model-select', 'value')
        ],
        prevent_initial_call=True
    )
    def update_question_options(survey_id: str, model_id: str) -> Tuple[List[Dict], Optional[str]]:
        """Update question options based on selected survey."""
        if not all([survey_id, model_id]):
            raise PreventUpdate
            
        try:
            # Load questions from questions.json
            questions_file = os.path.join(SURVEY_DIR, survey_id, 'questions.json')
            if not os.path.exists(questions_file):
                print(f"Questions file not found: {questions_file}")
                return [], None
                
            with open(questions_file, 'r', encoding='utf-8') as f:
                questions_data = json.load(f)
                
            # Create options from questions list
            options = []
            for q in questions_data.get('questions', []):
                q_id = q.get('question_id')
                q_title = q.get('question_title', '')
                if q_id:
                    options.append({
                        'label': f"{q_id}: {q_title}",
                        'value': q_id
                    })
            
            # Sort options by question ID
            options.sort(key=lambda x: str(x['value']))
            
            # Return options and default to first question
            if options:
                first_value = options[0]['value']
                return options, first_value
            return [], None
            
        except Exception as e:
            print(f"Error loading questions: {str(e)}")
            import traceback
            traceback.print_exc()
            return [], None

    @app.callback(
        Output('question-graph', 'figure'),
        [
            Input('survey-select', 'value'),
            Input('model-select', 'value'),
            Input('language-select', 'value'),
            Input('question-tab-select', 'value'),
            Input('show-confidence-intervals', 'value'),
            Input('show-color-scale', 'value'),
            Input('show-numbers', 'value')
        ],
        prevent_initial_call=True
    )
    def update_question_graph(
        survey_id: str,
        model_id: str,
        selected_languages: List[str],
        question_id: str,
        show_ci: List[str],
        show_color_scale: List[str],
        show_numbers: List[str]
    ) -> Dict:
        """Update question graph based on selections."""
        if not all([survey_id, model_id, selected_languages, question_id]):
            raise PreventUpdate
            
        # Load data
        data, error = load_survey_data(survey_id, model_id)
        if error:
            print(f"Error loading data: {error}")
            return {}
            
        # Convert options to booleans
        show_ci = bool(show_ci and 'show' in show_ci)
        show_cs = bool(show_color_scale and 'show' in show_color_scale)
        show_nums = bool(show_numbers and 'show' in show_numbers)
        
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
            return create_question_graph(
                data=data,
                selected_languages=selected_languages,
                selected_question=question_id,
                show_confidence_intervals=show_ci,
                show_color_scale=show_cs,
                show_numbers=show_nums,
                model_info=model_info,
                survey_name=survey_id
            )
        except Exception as e:
            print(f"Error creating question graph: {e}")
            import traceback
            traceback.print_exc()
            return {}
