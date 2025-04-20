"""
Deviation analysis showing how each language's responses differ from the mean.
"""

import plotly.graph_objects as go
import numpy as np
from api.config.styles import COLORS, GRAPH_COLORS, FONTS, LAYOUT, GRAPH_LAYOUT
from api.components.graph_footer import create_graph_footer
from api.views.shared import consolidate_question_data
from api.data_structures.matrix_data import MatrixData

def normalize_language_code(lang: str) -> str:
    """Normalize language codes to handle variations like 'he' and 'heb'."""
    if lang in ['he', 'heb']:
        return 'he'  # Standardize Hebrew codes
    return lang

def create_deviation_graph(data, selected_languages, model_info=None, survey_name=None, show_numbers=False):
    """Create a visualization showing how each language's responses differ from the mean."""
    if not data or not selected_languages:
        return go.Figure()
    
    # Create matrix data structure
    matrix_data = MatrixData()
    
    # Add questions and their metadata
    for item in data:
        q_id = item.get('question_id')
        if q_id:
            matrix_data.add_question(q_id, item.get('title'), {
                'category': item.get('category'),
                'scale_min': item.get('scale_min'),
                'scale_max': item.get('scale_max'),
                'scale_labels': item.get('scale_labels')
            })
    
    # Add languages and their values
    for lang in selected_languages:
        matrix_data.add_language(lang)
        for item in data:
            q_id = item.get('question_id')
            if q_id and lang in item.get('language_stats', {}):
                stats = item['language_stats'][lang]
                if stats.get('mean') is not None:
                    matrix_data.set_value(lang, q_id, stats['mean'], 'survey')
    
    # Get matrix representation
    question_ids, languages, z_array = matrix_data.get_matrix()
    
    # Calculate average deviation for each language
    deviations = {}
    for lang_idx, lang in enumerate(languages):
        # Get all values for this language
        lang_values = z_array[lang_idx]
        # Calculate mean and std of this language's values
        lang_mean = np.nanmean(lang_values)
        lang_std = np.nanstd(lang_values)
        
        # Calculate how much this language's mean differs from the overall mean
        overall_mean = np.nanmean(z_array)
        overall_std = np.nanstd(z_array)
        
        if overall_std > 0:  # Avoid division by zero
            z_score = abs(lang_mean - overall_mean) / overall_std
            deviations[lang] = z_score
    
    # Sort languages by deviation (ascending)
    sorted_langs = sorted(deviations.items(), key=lambda x: x[1])
    languages = [x[0] for x in sorted_langs]
    deviation_values = [x[1] for x in sorted_langs]

    # Create the bar chart
    fig = go.Figure(
        data=[
            go.Bar(
                x=languages,
                y=deviation_values,
                text=[f"{val:.2f}" for val in deviation_values] if show_numbers else None,
                textposition='outside',
                marker_color='rgb(49,54,149)',  # Use consistent blue color
                hovertemplate='%{x}<br>Z-score deviation: %{y:.2f}<extra></extra>'
            )
        ]
    )

    # Add footer
    footer = create_graph_footer(
        survey_name=survey_name,
        model_info=model_info,
        data=data,  # Pass original data for footer
        selected_languages=selected_languages
    )

    # Update layout with footer annotation only
    annotations = []
    if footer:
        annotations.append(footer)

    # Update layout
    fig.update_layout(
        title={
            'text': '<b>Language Response Pattern Deviation Analysis</b><br><br><span style="font-size: 14px; color: gray">For each language, shows the average number of standard deviations its responses differ from the mean of all languages.<br>For example, a value of 1.0 means that language\'s responses typically differ by one standard deviation from the mean of all languages in the sample.</span>',
            'x': 0.5,
            'y': 0.95,  # Moved down slightly
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 24}
        },
        showlegend=False,
        xaxis={
            'title': None,
            'tickangle': 45,
            'showgrid': False
        },
        yaxis={
            'title': 'Average Z-Score Deviation',
            'showgrid': True,
            'gridcolor': 'rgba(0,0,0,0.1)',
            'gridwidth': 1,
            'zeroline': True,
            'zerolinecolor': 'rgba(0,0,0,0.2)',
            'zerolinewidth': 1
        },
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin={'t': 180, 'b': 100, 'l': 60, 'r': 40},  # Increased top margin
        height=600,
        annotations=annotations,
        # Add modebar configuration directly in the layout
        modebar={
            'remove': [
                'zoom', 'pan', 'select', 'lasso2d', 'zoomIn', 'zoomOut',
                'autoScale', 'resetScale', 'hoverClosestCartesian',
                'hoverCompareCartesian', 'toggleSpikelines'
            ],
            'add': ['toImage']
        }
    )

    return fig

def create_deviation_view(data, selected_languages, model_info=None, survey_name=None):
    """Create a deviation view showing how responses deviate from the mean."""
    if not data or not selected_languages:
        return go.Figure()

    # Create the deviation graph
    fig = create_deviation_graph(data, selected_languages, model_info, survey_name)
    return fig 