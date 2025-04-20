"""
Footer component for the dashboard.
Includes attribution, links, and copyright information.
Inspired by modern React design patterns while maintaining Dash compatibility.
"""

from dash import html
from api.config.styles import COLORS, FONTS, LAYOUT, COMPONENT_STYLES

def create_footer():
    """
    Create a modern footer component.
    Includes attribution to World Values Survey and other relevant links.
    """
    return html.Footer(
        children=[
            html.Div([
                # Left section with copyright and attribution
                html.Div([
                    html.P([
                        "Data source: ",
                        html.A(
                            "World Values Survey",
                            href="https://www.worldvaluessurvey.org/",
                            target="_blank",
                            style={
                                'color': COLORS['primary'],
                                'textDecoration': 'none'
                            }
                        ),
                        " Wave 7 (2017-2022)"
                    ], style={
                        'margin': '0',
                        'color': COLORS['text'],
                        'fontSize': f"{FONTS['size']['small']}px",
                        'fontFamily': FONTS['family']
                    }),
                    html.P(
                        "© 2024 World Values Survey Analysis. All rights reserved.",
                        style={
                            'margin': '4px 0 0 0',
                            'color': COLORS['muted'],
                            'fontSize': f"{FONTS['size']['small']}px",
                            'fontFamily': FONTS['family']
                        }
                    )
                ], style={'flex': '1'}),
                
                # Right section with links
                html.Div([
                    html.A(
                        "Documentation",
                        href="#",
                        style={
                            'color': COLORS['primary'],
                            'textDecoration': 'none',
                            'fontSize': f"{FONTS['size']['small']}px",
                            'fontFamily': FONTS['family'],
                            'marginRight': f"{LAYOUT['margins']['large']}px"
                        }
                    ),
                    html.A(
                        "GitHub",
                        href="https://github.com/yourusername/wvs-analysis",
                        target="_blank",
                        style={
                            'color': COLORS['primary'],
                            'textDecoration': 'none',
                            'fontSize': f"{FONTS['size']['small']}px",
                            'fontFamily': FONTS['family'],
                            'marginRight': f"{LAYOUT['margins']['large']}px"
                        }
                    ),
                    html.A(
                        "Privacy Policy",
                        href="#",
                        style={
                            'color': COLORS['primary'],
                            'textDecoration': 'none',
                            'fontSize': f"{FONTS['size']['small']}px",
                            'fontFamily': FONTS['family']
                        }
                    )
                ])
            ], style={
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'space-between',
                'maxWidth': '1200px',
                'margin': '0 auto',
                'padding': f"{LAYOUT['padding']['normal']}px {LAYOUT['padding']['large']}px"
            })
        ],
        style={
            'width': '100%',
            'backgroundColor': COLORS['white'],
            'borderTop': f"1px solid {COLORS['light']}",
            'marginTop': 'auto'  # Push to bottom of page
        }
    ) 