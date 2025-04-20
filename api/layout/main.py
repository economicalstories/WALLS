# -*- coding: utf-8 -*-
"""
Main layout for the dashboard.
"""

from dash import html, dcc
from dash.dependencies import Input, Output, State
from dash import Dash

from .tabs import create_tabs
from ..components.controls import create_controls
from ..components.header import create_header


def create_layout(app: Dash) -> html.Div:
    """Create the main layout for the dashboard.
    
    Args:
        app: The Dash application instance
        
    Returns:
        html.Div containing the complete dashboard layout
    """
    return html.Div(
        [
            # Hidden div for callbacks
            html.Div(id='_', style={'display': 'none'}),
            
            # Header
            create_header(),
            
            # Controls
            create_controls(app),
            
            # Tabs
            create_tabs()
        ],
        className='dashboard-container'
    )
