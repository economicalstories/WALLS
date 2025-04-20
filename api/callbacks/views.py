# -*- coding: utf-8 -*-
"""
Callbacks for handling view updates and interactions.
"""

from dash import Input, Output, State, html, dcc
from dash.exceptions import PreventUpdate

from .shared import load_survey_data, load_question_metadata, validate_languages
from api.views.matrix_view import create_matrix_graph
from api.views.deviation_view import create_deviation_graph
from api.views.question_view import create_question_graph

def register_callbacks(app):
    """Register all callbacks related to view updates."""
    
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
        ]
    )
    def update_question_view(survey_id, model_id, languages, question_id, show_ci, show_cs, show_num):
        """Update the question view when inputs change."""
        if not all([survey_id, model_id, languages, question_id]):
            raise PreventUpdate
            
        # Load and process data
        data, error = load_survey_data(survey_id, model_id)
        if error or not data:
            return {}
            
        # Create question view graph
        fig = create_question_graph(
            data=data,
            selected_languages=languages,
            selected_question=question_id,
            show_confidence_intervals=bool(show_ci and 'show' in show_ci),
            show_color_scale=bool(show_cs and 'show' in show_cs),
            show_numbers=bool(show_num and 'show' in show_num),
            model_info={'name': model_id},
            survey_name=survey_id
        )
        
        return fig
        
    @app.callback(
        Output('matrix-graph', 'figure'),
        [
            Input('survey-select', 'value'),
            Input('model-select', 'value'),
            Input('language-select', 'value'),
            Input('matrix-hide-colors', 'value'),
            Input('matrix-hide-numbers', 'value')
        ]
    )
    def update_matrix_view(survey_id, model_id, languages, hide_colors, hide_numbers):
        """Update the matrix view when inputs change."""
        if not all([survey_id, model_id, languages]):
            raise PreventUpdate
            
        # Load and process data
        data, error = load_survey_data(survey_id, model_id)
        if error or not data:
            return {}
            
        # Create matrix view graph
        fig = create_matrix_graph(
            data=data,
            selected_languages=languages,
            show_color_scale=not bool(hide_colors and 'hide' in hide_colors),
            show_numbers=not bool(hide_numbers and 'hide' in hide_numbers),
            model_info={'name': model_id},
            survey_name=survey_id
        )
        
        return fig
        
    @app.callback(
        Output('deviation-graph', 'figure'),
        [
            Input('survey-select', 'value'),
            Input('model-select', 'value'),
            Input('language-select', 'value'),
            Input('deviation-show-numbers', 'value')
        ]
    )
    def update_deviation_view(survey_id, model_id, languages, show_numbers):
        """Update the deviation view when inputs change."""
        if not all([survey_id, model_id, languages]):
            raise PreventUpdate
            
        # Load and process data
        data, error = load_survey_data(survey_id, model_id)
        if error or not data:
            return {}
            
        # Create deviation view graph
        fig = create_deviation_graph(
            data=data,
            selected_languages=languages,
            model_info={'name': model_id},
            survey_name=survey_id,
            show_numbers=bool(show_numbers and 'show' in show_numbers)
        )
        
        return fig 