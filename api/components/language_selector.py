# -*- coding: utf-8 -*-
"""
Language selector component for choosing which languages to analyze.
"""

from dash import html, dcc
from dash.dependencies import Input, Output, State

def create_language_selector():
    """
    Create the language selector component.
    
    Returns:
        html.Div containing the language selector
    """
    return html.Div(
        [
            html.Label('Languages:', className='control-label'),
            dcc.Checklist(
                id='language-checklist',
                options=[],  # Will be populated by callback
                value=[],  # Will be populated by callback
                className='control-checklist'
            )
        ],
        className='control-group'
    ) 