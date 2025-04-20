"""
Matrix visualization view using Plotly.
"""

import numpy as np
import plotly.graph_objs as go
from typing import Dict, List, Any, Optional

from api.data_structures.matrix_data import MatrixData
from api.data_processing.matrix_processor import debug_matrix_data
from api.components.graph_footer import create_graph_footer

def create_matrix_graph(
    matrix_data: MatrixData,
    selected_languages: List[str],
    hide_color_scale: bool = False,
    show_numbers: bool = True,
    model_info: Optional[Dict[str, Any]] = None,
    survey_name: Optional[str] = None
) -> go.Figure:
    """Create a matrix visualization showing correlations between questions.
    
    Args:
        matrix_data: Processed matrix data
        selected_languages: List of languages to include in visualization
        hide_color_scale: Whether to hide colors (use greyscale)
        show_numbers: Whether to show number labels
        model_info: Dict containing model metadata
        survey_name: Name of the survey
    """
    # Filter for selected languages
    filtered_matrix = MatrixData()
    for q in matrix_data.questions:
        filtered_matrix.add_question(q['id'], q['title'], matrix_data.metadata.get(q['id']))
    
    for lang in selected_languages:
        if lang in matrix_data.languages:
            filtered_matrix.add_language(lang)
            for q in matrix_data.questions:
                q_id = q['id']
                if q_id in matrix_data.values[lang]:
                    filtered_matrix.set_value(
                        lang, 
                        q_id, 
                        matrix_data.values[lang][q_id],
                        matrix_data.sources[lang][q_id]
                    )
    
    # Get matrix representation
    question_ids, languages, z_array = filtered_matrix.get_matrix()
    
    # Calculate question means for relative coloring
    question_means = np.nanmean(z_array, axis=0)
    # Create relative coloring matrix (deviation from mean)
    relative_z = np.zeros_like(z_array)
    for i in range(z_array.shape[1]):  # For each question
        mean = question_means[i]
        if not np.isnan(mean):
            relative_z[:, i] = z_array[:, i] - mean
    
    # Create x-axis labels with question IDs and titles
    x_data = [f"{q_id}: {matrix_data.questions[i]['title'][:30]}..." 
              for i, q_id in enumerate(question_ids)]
    
    # Create hover text
    hover_text = []
    for lang_idx, lang in enumerate(languages):
        row_hover = []
        for q_idx, q_id in enumerate(question_ids):
            value = z_array[lang_idx, q_idx]
            relative_value = relative_z[lang_idx, q_idx]
            source = filtered_matrix.sources[lang].get(q_id, "unknown")
            hover_str = (
                f"<b>Question {q_id}</b><br>"
                f"{filtered_matrix.questions[q_idx]['title']}<br><br>"
                f"<b>{lang}</b><br>"
                f"Mean: {value:.1f}<br>"
                f"Deviation from Q-mean: {relative_value:+.1f}<br>"
                f"Source: {source}"
            )
            row_hover.append(hover_str)
        hover_text.append(row_hover)
    
    # Create figure with subplots
    try:
        fig = go.Figure()
        
        # Add relative value heatmap (for coloring)
        fig.add_trace(go.Heatmap(
            z=relative_z,
            x=x_data,
            y=languages,
            text=None,  # No text for this trace
            hoverinfo='skip',  # Skip hover for this trace
            showscale=True,
            colorscale=[
                [0.0, 'rgb(49,54,149)'],      # Blue for below mean
                [0.45, 'rgb(158,202,225)'],    # Light blue
                [0.5, 'rgb(255,255,255)'],     # White for mean
                [0.55, 'rgb(252,146,114)'],    # Light red
                [1.0, 'rgb(180,4,38)']         # Red for above mean
            ] if not hide_color_scale else 'Greys',
            zmid=0.0,  # Center at 0 (mean)
            zmin=-5.0,  # Allow for deviations up to 5 points below mean
            zmax=5.0,   # Allow for deviations up to 5 points above mean
            colorbar=dict(
                title='Deviation from<br>Question Mean',
                thickness=15,
                len=0.85,
                y=0.5,
                yanchor='middle',
                tickformat='+.1f'
            ),
            hoverongaps=False,
            name='Relative Values'
        ))
        
        # Add text layer on top
        fig.add_trace(go.Heatmap(
            z=z_array,
            x=x_data,
            y=languages,
            text=[[f"{val:.1f}" if val > 0 else "" for val in row] for row in z_array],
            texttemplate="%{text}" if show_numbers else "",
            textfont={'size': 11, 'color': 'black', 'family': 'Arial'},
            hoverinfo='text',
            hovertext=hover_text,
            showscale=False,  # Hide scale for this trace
            colorscale=[[0, 'rgba(0,0,0,0)'], [1, 'rgba(0,0,0,0)']],  # Transparent background
            hoverongaps=False,
            name='Values'
        ))
        
        # Calculate height based on number of languages with a minimum
        min_height = 800  # Minimum height in pixels
        height_per_language = 45  # Increased from 35 to 45 pixels per language
        margin_height = 250  # Total margin height (top + bottom)
        calculated_height = max(min_height, margin_height + height_per_language * len(languages))
        
        # Calculate width based on number of questions and font size
        # Assuming each character is ~8px wide at font-size 10px
        # For a number with 1 decimal place (e.g. "4.2"), we need ~24px (3 chars)
        char_width = 8  # pixels per character at font-size 10px
        number_width = char_width * 3  # width for a number with 1 decimal place
        width_per_question = number_width + 10  # Add some padding
        margin_width = 250  # Total margin width (left + right)
        calculated_width = max(1000, margin_width + width_per_question * len(question_ids))
        
        # Update layout
        fig.update_layout(
            title=dict(
                text=f"Question Response Matrix<br><sup>Survey: {survey_name or 'Unknown'}</sup>",
                x=0.5,
                xanchor='center',
                y=0.98,
                yanchor='top'
            ),
            margin=dict(
                t=220,  # Increased from 180 to 220 for more title spacing
                r=20,
                b=100,
                l=200
            ),
            xaxis=dict(
                tickangle=45,
                tickfont=dict(size=10),
                showgrid=False,
                side='top',
                tickson='boundaries',
                constrain='domain',
                automargin=True,
                fixedrange=True
            ),
            yaxis=dict(
                tickfont=dict(size=12),
                showgrid=False,
                constrain='domain',
                automargin=True,
                fixedrange=True
            ),
            width=calculated_width,
            height=calculated_height,
            plot_bgcolor='white',
            autosize=False,
            uirevision=True,
            dragmode=False
        )
        
        # Add footer if model info provided
        if model_info:
            footer = create_graph_footer(
                survey_name=survey_name,
                model_info=model_info,
                data=None,  # No data needed for matrix view
                selected_languages=selected_languages
            )
            if footer:
                fig.add_annotation(footer)
            
        return fig
        
    except Exception as e:
        print(f"Error creating visualization: {str(e)}")
        import traceback
        traceback.print_exc()
        return go.Figure() 