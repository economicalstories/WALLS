"""
Header component for the dashboard.
Inspired by modern React design patterns while maintaining Dash compatibility.
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
from api.config.styles import COLORS, FONTS, LAYOUT, COMPONENT_STYLES

def create_header():
    """
    Create a modern header component with navigation and styling.
    Designed to be visually similar to React components while using Dash.
    """
    return html.Header(
        children=[
            # Main header container
            html.Div([
                # Logo/Title section
                html.Div([
                    html.H1(
                        ["WALLS", html.Span(" (Research Preview)", style={
                            'fontSize': f"{FONTS['size']['small']}px",
                            'fontWeight': 'normal',
                            'opacity': '0.8'
                        })],
                        style={
                            'color': COLORS['white'],
                            'fontSize': f"{FONTS['size']['header']}px",
                            'fontFamily': FONTS['family'],
                            'margin': '0',
                            'fontWeight': '700',
                            'letterSpacing': '0.5px',
                            'display': 'flex',
                            'alignItems': 'baseline',
                            'gap': '8px'
                        }
                    ),
                    html.P(
                        "Wittgenstein's Analysis of LLM Language Systems",
                        style={
                            'color': COLORS['light'],
                            'fontSize': f"{FONTS['size']['normal']}px",
                            'fontFamily': FONTS['family'],
                            'margin': '4px 0 0 0',
                            'opacity': '0.9'
                        }
                    )
                ], style={
                    'flex': '1'
                }),
                
                # Navigation links
                html.Nav([
                    html.A(
                        "About",
                        id='about-link',
                        href="#",
                        style={
                            'color': COLORS['light'],
                            'textDecoration': 'none',
                            'marginLeft': f"{LAYOUT['margins']['large']}px",
                            'fontSize': f"{FONTS['size']['normal']}px",
                            'fontFamily': FONTS['family'],
                            'opacity': '0.9',
                            'transition': 'opacity 0.2s ease',
                            'cursor': 'pointer',
                            ':hover': {'opacity': '1'}
                        }
                    ),
                    html.A(
                        "GitHub",
                        href="https://github.com/economicalstories/walls",
                        target="_blank",
                        style={
                            'color': COLORS['light'],
                            'textDecoration': 'none',
                            'marginLeft': f"{LAYOUT['margins']['large']}px",
                            'fontSize': f"{FONTS['size']['normal']}px",
                            'fontFamily': FONTS['family'],
                            'opacity': '0.9',
                            'transition': 'opacity 0.2s ease',
                            ':hover': {'opacity': '1'}
                        }
                    )
                ], style={
                    'display': 'flex',
                    'alignItems': 'center'
                })
            ], style={
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'space-between',
                'padding': f"{LAYOUT['padding']['large']}px",
                'backgroundColor': COLORS['primary'],
                'backgroundImage': f"linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%)",
                'boxShadow': '0 2px 8px rgba(0,0,0,0.15)'
            }),
            
            # About modal
            dbc.Modal(
                id='about-modal',
                children=[
                    dbc.ModalHeader(
                        dbc.ModalTitle("About WALLS")
                    ),
                    dbc.ModalBody([
                        html.P([
                            "NOTE: This is currently a research preview with limited samples per language and is not statistically robust. ",
                            "Please use at your own risk, and DO NOT use or attribute these charts without performing underlying statistical tests."
                        ], style={'marginBottom': '15px', 'fontWeight': 'bold'}),
                        html.P([
                            "A project investigating how large language models respond to standardized survey-style prompts in different languages. ",
                            "Inspired by Wittgenstein's assertion that 'the limits of my language are the limits of my world,' this project uses ",
                            "numeric outputs to compare the 'values' expressed by the LLM when prompted in various languages."
                        ])
                    ]),
                    dbc.ModalFooter(
                        dbc.Button("Close", id="close-about-modal", className="ms-auto")
                    )
                ],
                is_open=False,
                size="lg",
                centered=True
            )
        ],
        style={
            'width': '100%',
            'position': 'sticky',
            'top': '0',
            'zIndex': '1000',
            'backgroundColor': COLORS['primary']
        }
    ) 