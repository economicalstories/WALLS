# -*- coding: utf-8 -*-
"""
Model selector component for choosing which model to analyze.
"""

from dash import html, dcc
from dash.dependencies import Input, Output, State

def create_model_selector():
    """
    Create the model selector component.
    
    Returns:
        html.Div containing the model selector
    """
    return html.Div(
        [
            html.Label('Model:', className='control-label'),
            dcc.Dropdown(
                id='model-dropdown',
                options=[],  # Will be populated by callback
                value=None,
                clearable=False,
                className='control-dropdown'
            )
        ],
        className='control-group'
    ) 