# -*- coding: utf-8 -*-
"""
Tab layout components for the dashboard.
"""

from dash import html, dcc
from api.config.styles import LAYOUT, COMPONENT_STYLES
from .components import create_explanation_ribbon, create_control_container

def create_question_tab():
    """Create the Question View tab."""
    return dcc.Tab(
        label='Question View',
        children=[
            create_explanation_ribbon(
                "Examine how different languages respond to a single question. "
                "This view helps you understand specific value differences across languages."
            ),
            html.Div([
                create_control_container([
                    html.Label('Select Question:', style={'marginBottom': f"{LAYOUT['margins']['small']}px"}),
                    dcc.Dropdown(
                        id='question-tab-select',
                        placeholder='Select a question to analyze...',
                        style={
                            **COMPONENT_STYLES['dropdown'], 
                            'marginBottom': f"{LAYOUT['margins']['normal']}px",
                            'width': '100%'
                        }
                    ),
                    dcc.Checklist(
                        id='show-confidence-intervals',
                        options=[{'label': 'Show Confidence Intervals', 'value': 'show'}],
                        value=[],
                        style={'marginBottom': f"{LAYOUT['margins']['small']}px"}
                    ),
                    dcc.Checklist(
                        id='show-color-scale',
                        options=[{'label': 'Show Color Scale', 'value': 'show'}],
                        value=[],
                        style={'marginBottom': f"{LAYOUT['margins']['small']}px"}
                    ),
                    dcc.Checklist(
                        id='show-numbers',
                        options=[{'label': 'Show Numbers', 'value': 'show'}],
                        value=[],
                        style={'marginBottom': f"{LAYOUT['margins']['small']}px"}
                    ),
                ]),
                dcc.Graph(
                    id='question-graph',
                    style={'height': 'calc(100vh - 300px)'}
                )
            ])
        ]
    )

def create_matrix_tab():
    """Create the Matrix View tab."""
    return dcc.Tab(
        label='Matrix View',
        children=[
            create_explanation_ribbon(
                "Get a comprehensive overview of all responses across questions and languages. "
                "The matrix reveals patterns and clusters in how different languages respond."
            ),
            html.Div([
                create_control_container([
                    dcc.Checklist(
                        id='matrix-hide-colors',
                        options=[{'label': 'Hide Colors', 'value': 'hide'}],
                        value=[],
                        style={'marginBottom': f"{LAYOUT['margins']['small']}px"}
                    ),
                    dcc.Checklist(
                        id='matrix-hide-numbers',
                        options=[{'label': 'Hide Numbers', 'value': 'hide'}],
                        value=[],
                        style={'marginBottom': f"{LAYOUT['margins']['small']}px"}
                    ),
                ]),
                dcc.Graph(
                    id='matrix-graph',
                    style={'height': 'calc(100vh - 300px)'}
                )
            ])
        ]
    )

def create_deviation_tab():
    """Create the Deviation Analysis tab."""
    return dcc.Tab(
        label='Deviation Analysis',
        children=[
            create_explanation_ribbon(
                "Analyze how much each language's responses deviate from others. "
                "This view helps identify which languages show unique response patterns."
            ),
            html.Div([
                create_control_container([
                    dcc.Checklist(
                        id='deviation-show-numbers',
                        options=[{'label': 'Show Numbers', 'value': 'show'}],
                        value=[],
                        style={'marginBottom': f"{LAYOUT['margins']['small']}px"}
                    ),
                ]),
                dcc.Graph(
                    id='deviation-graph',
                    style={'height': 'calc(100vh - 300px)'}
                )
            ])
        ]
    )

def create_tabs():
    """
    Create the main tab navigation.
    
    Returns:
        dcc.Tabs containing all view tabs
    """
    return dcc.Tabs(
        [
            create_question_tab(),
            create_matrix_tab(),
            create_deviation_tab()
        ],
        className='custom-tabs',
        id='tabs'
    ) 