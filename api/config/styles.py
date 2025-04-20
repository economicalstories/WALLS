"""
Styling configuration for the dashboard application.
Contains color schemes, fonts, margins, and other visual styling constants.
"""

# Color schemes
COLORS = {
    'background': '#ffffff',
    'text': '#1a1a1a',
    'primary': '#1e3a8a',  # Deep blue
    'secondary': '#3b82f6',  # Bright blue
    'success': '#059669',  # Green
    'danger': '#dc2626',  # Red
    'warning': '#d97706',  # Amber
    'info': '#0891b2',  # Cyan
    'light': '#f3f4f6',  # Light gray
    'dark': '#111827',  # Dark gray
    'muted': '#6b7280',  # Medium gray
    'white': '#ffffff',
    'transparent': 'rgba(0,0,0,0)',
    'accent': '#8b5cf6'  # Purple accent
}

# Graph colors
GRAPH_COLORS = {
    'heatmap': 'RdYlBu',  # Colorscale for heatmaps
    'error_bars': '#6b7280',  # Color for error bars
    'mean_line': '#6b7280',  # Color for mean lines
    'grid': '#e5e7eb',  # Color for grid lines
    'sequence': [  # Color sequence for multiple traces
        '#1e3a8a',  # Primary blue
        '#3b82f6',  # Secondary blue
        '#8b5cf6',  # Purple
        '#059669',  # Green
        '#d97706',  # Amber
        '#dc2626',  # Red
        '#0891b2',  # Cyan
        '#6b7280',  # Gray
        '#4f46e5',  # Indigo
        '#0d9488'   # Teal
    ]
}

# Font styles
FONTS = {
    'family': 'Inter, system-ui, -apple-system, sans-serif',
    'size': {
        'small': 12,
        'normal': 14,
        'large': 16,
        'title': 20,
        'header': 24
    }
}

# Layout styles
LAYOUT = {
    'margins': {
        'small': 8,
        'normal': 16,
        'large': 24
    },
    'padding': {
        'small': 8,
        'normal': 16,
        'large': 24
    },
    'border_radius': 6
}

# Component-specific styles
COMPONENT_STYLES = {
    'header': {
        'backgroundColor': COLORS['primary'],
        'color': COLORS['white'],
        'padding': f"{LAYOUT['padding']['large']}px",
        'marginBottom': f"{LAYOUT['margins']['large']}px",
        'textAlign': 'center',
        'fontSize': f"{FONTS['size']['header']}px",
        'fontFamily': FONTS['family']
    },
    'container': {
        'backgroundColor': COLORS['light'],
        'padding': f"{LAYOUT['padding']['normal']}px",
        'borderRadius': f"{LAYOUT['border_radius']}px",
        'marginBottom': f"{LAYOUT['margins']['normal']}px",
        'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'
    },
    'button': {
        'primary': {
            'backgroundColor': COLORS['primary'],
            'color': COLORS['white'],
            'border': 'none',
            'padding': f"{LAYOUT['padding']['normal']}px",
            'borderRadius': f"{LAYOUT['border_radius']}px",
            'cursor': 'pointer',
            'transition': 'background-color 0.2s ease'
        },
        'secondary': {
            'backgroundColor': COLORS['secondary'],
            'color': COLORS['white'],
            'border': 'none',
            'padding': f"{LAYOUT['padding']['normal']}px",
            'borderRadius': f"{LAYOUT['border_radius']}px",
            'cursor': 'pointer',
            'transition': 'background-color 0.2s ease'
        }
    },
    'dropdown': {
        'backgroundColor': COLORS['white'],
        'color': COLORS['text'],
        'border': f"1px solid {COLORS['muted']}",
        'padding': f"{LAYOUT['padding']['normal']}px",
        'borderRadius': f"{LAYOUT['border_radius']}px",
        'fontSize': f"{FONTS['size']['normal']}px",
        'fontFamily': FONTS['family'],
        'width': '100%',
        'maxWidth': '300px'
    }
}

# Graph layout styles
GRAPH_LAYOUT = {
    'margin': {
        'l': 60,
        'r': 40,
        't': 40,
        'b': 40
    },
    'plot_bgcolor': COLORS['background'],
    'paper_bgcolor': COLORS['background'],
    'font': {
        'family': FONTS['family'],
        'size': FONTS['size']['normal'],
        'color': COLORS['text']
    },
    'showlegend': True,
    'legend': {
        'orientation': 'h',
        'yanchor': 'bottom',
        'y': 1.02,
        'xanchor': 'right',
        'x': 1
    }
}

# Mobile-specific styles
MOBILE_STYLES = {
    'container': {
        'padding': f"{LAYOUT['padding']['small']}px",
        'margin': f"{LAYOUT['margins']['small']}px"
    },
    'font': {
        'size': {
            'small': 10,
            'normal': 12,
            'large': 14,
            'title': 16,
            'header': 20
        }
    },
    'graph_layout': {
        'margin': {
            't': 30,
            'r': 20,
            'b': 30,
            'l': 40
        }
    }
} 