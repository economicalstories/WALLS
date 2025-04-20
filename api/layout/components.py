# -*- coding: utf-8 -*-
"""
Layout components for the dashboard.
"""

from dash import html, dcc
from api.config.styles import COLORS, FONTS, LAYOUT, COMPONENT_STYLES

def create_project_description():
    """Create the project description section."""
    return html.Div([
        html.H2(
            "WALLS: Wittgenstein's Analysis of LLM Language Systems (Research Preview)",
            style={
                'color': COLORS['text'],
                'fontSize': f"{FONTS['size']['title']}px",
                'fontFamily': FONTS['family'],
                'textAlign': 'center',
                'margin': f"{LAYOUT['margins']['large']}px 0"
            }
        ),
        # Project Info Box
        html.Div([
            html.P([
                "NOTE: This is currently a research preview with limited samples per language and is not statistically robust. ",
                "Please use at your own risk, and DO NOT use or attribute these charts without performing underlying statistical tests."
            ], style={
                'marginBottom': '12px',
                'fontWeight': 'bold',
                'color': COLORS['warning']
            }),
            html.P([
                "A project investigating how large language models respond to standardized survey-style prompts in different languages. ",
                "Inspired by Wittgenstein's assertion that 'the limits of my language are the limits of my world,' ",
                "this project uses numeric outputs to compare the 'values' expressed by the LLM when prompted in various languages."
            ])
        ], style={
            'backgroundColor': COLORS['light'],
            'padding': f"{LAYOUT['padding']['large']}px",
            'borderRadius': f"{LAYOUT['border_radius']}px",
            'margin': f"{LAYOUT['margins']['normal']}px 0",
            'fontSize': f"{FONTS['size']['normal']}px",
            'lineHeight': '1.5'
        })
    ], style={
        'maxWidth': '1200px',
        'margin': '0 auto',
        'padding': f"{LAYOUT['padding']['normal']}px"
    })

def create_explanation_ribbon(text: str):
    """Create an explanation ribbon with the given text."""
    return html.Div(
        text,
        style={
            'backgroundColor': COLORS['light'],
            'padding': f"{LAYOUT['padding']['normal']}px {LAYOUT['padding']['large']}px",
            'borderBottom': f"1px solid {COLORS['muted']}",
            'color': COLORS['text'],
            'fontSize': f"{FONTS['size']['normal']}px",
            'fontStyle': 'italic'
        }
    )

def create_control_container(children):
    """Create a styled container for controls."""
    return html.Div(
        children,
        style={
            'marginBottom': f"{LAYOUT['margins']['large']}px",
            'padding': f"{LAYOUT['padding']['normal']}px",
            'backgroundColor': COLORS['light'],
            'borderRadius': f"{LAYOUT['border_radius']}px",
            **COMPONENT_STYLES['container']
        }
    ) 