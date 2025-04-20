"""
Question view showing detailed analysis of a single question across languages.
"""

import plotly.graph_objects as go
from api.config.styles import COLORS, GRAPH_COLORS, FONTS, LAYOUT, GRAPH_LAYOUT
from api.components.graph_footer import create_graph_footer

def create_question_graph(data, selected_languages, selected_question, show_confidence_intervals=False, show_color_scale=False, show_numbers=False, model_info=None, survey_name=None):
    """Create a visualization for a single question showing mean responses across languages.
    
    Args:
        data: List of questions with their statistics
        selected_languages: List of languages to include in visualization
        selected_question: Question ID to visualize
        show_confidence_intervals: Whether to show ±2σ ranges (default: False)
        show_color_scale: Whether to show greyscale coloring (default: False)
        show_numbers: Whether to show number labels on bars (default: False)
        model_info: Dict containing model metadata (name, call count, etc.)
        survey_name: Name of the survey
    """
    if not data or not selected_languages or not selected_question:
        return go.Figure()

    # Find the selected question and aggregate stats across all result files
    question = None
    aggregated_stats = {lang: {'mean': None, 'std': None, 'count': 0} for lang in selected_languages}
    
    # Process each question entry (from different result files)
    for q in data:
        if q.get('question_id') == selected_question:
            question = q  # Keep the last question for metadata
            
            # Update stats for each language
            lang_stats = q.get('language_stats', {})
            for lang in selected_languages:
                if lang in lang_stats:
                    stats = lang_stats[lang]
                    current = aggregated_stats[lang]
                    
                    # If we have valid data, update the aggregated stats
                    if stats.get('mean') is not None and stats.get('count', 0) > 0:
                        if current['mean'] is None:
                            # First valid data for this language
                            current['mean'] = stats['mean']
                            current['std'] = stats.get('std', 0)
                            current['count'] = stats.get('count', 0)
                        else:
                            # Update mean and count
                            total_count = current['count'] + stats.get('count', 0)
                            if total_count > 0:
                                current['mean'] = (
                                    (current['mean'] * current['count'] + 
                                     stats['mean'] * stats.get('count', 0)) / total_count
                                )
                                # Take the larger std dev as a conservative estimate
                                current['std'] = max(current['std'] or 0, stats.get('std', 0))
                                current['count'] = total_count
    
    if not question:
        return go.Figure()

    # Get scale limits from question data
    scale_min = question.get('scale_min', 1)
    scale_max = question.get('scale_max', 10)

    # Prepare data for bar chart and sort by mean
    language_data = []
    for lang in selected_languages:
        stats = aggregated_stats[lang]
        if stats['mean'] is not None and stats['count'] > 0:
            language_data.append({
                'language': lang,
                'mean': stats['mean'],
                'std': stats['std'],
                'count': stats['count']
            })
    
    # Sort languages by mean value
    language_data.sort(key=lambda x: x['mean'])
    
    # Extract sorted data
    languages = [d['language'] for d in language_data]
    means = [d['mean'] for d in language_data]
    
    # Calculate overall mean and standard deviation for color scaling
    overall_mean = sum(means) / len(means) if means else 0
    
    # Calculate colors based on absolute distance from mean
    colors = []
    if means:
        # Find maximum absolute distance for scaling
        max_distance = max(abs(mean - overall_mean) for mean in means)
        
        for mean in means:
            # Calculate absolute distance and normalize to [0,1]
            distance = abs(mean - overall_mean)
            relative_distance = distance / max_distance if max_distance > 0 else 0
            
            if show_color_scale:
                # Greyscale mode
                grey_value = int(255 - (relative_distance * 55))  # This gives a range from 200-255
                colors.append(f'rgb({grey_value}, {grey_value}, {grey_value})')
            else:
                # Default red/white/blue mode
                if mean > overall_mean:
                    # Red scale for above mean
                    intensity = int(255 * relative_distance)
                    colors.append(f'rgb({255}, {255-intensity}, {255-intensity})')
                elif mean < overall_mean:
                    # Blue scale for below mean
                    intensity = int(255 * relative_distance)
                    colors.append(f'rgb({255-intensity}, {255-intensity}, {255})')
                else:
                    # White for mean
                    colors.append('rgb(255, 255, 255)')
    else:
        colors = [COLORS['primary']] * len(means)
    
    # Use ±2 standard deviations for error bars (95% confidence interval)
    error_plus = [2 * d['std'] if d['std'] is not None else 0 for d in language_data]
    error_minus = [2 * d['std'] if d['std'] is not None else 0 for d in language_data]
    
    hover_text = []
    for d, color in zip(language_data, colors):
        hover_text.append(
            f"Language: {d['language']}<br>"
            f"Mean: {d['mean']:.2f}<br>"
            f"Std Dev: {d['std']:.2f}<br>"
            f"±2σ Range: {d['mean']-2*d['std']:.2f} to {d['mean']+2*d['std']:.2f}<br>"
            f"Responses: {d['count']}"
        )

    # Create bar chart with consistent color scheme
    fig = go.Figure(data=go.Bar(
        x=languages,
        y=means,
        error_y=dict(
            type='data',
            symmetric=True,
            array=error_plus,
            color=GRAPH_COLORS['error_bars'],
            visible=show_confidence_intervals
        ),
        text=[f"{m:.2f}" for m in means] if show_numbers else None,
        textposition='auto',
        marker_color=colors,
        marker_line_color=COLORS['dark'],
        marker_line_width=1,
        hovertext=hover_text,
        hoverinfo='text'
    ))
    
    # Format title and subtitle with scale descriptions
    question_id = question.get('question_id', 'Unknown')
    question_title = question.get('title', 'Unknown')
    
    # Get scale labels if available
    scale_labels = question.get('scale_labels', {})
    if not isinstance(scale_labels, dict):
        scale_labels = {}
    
    # Create subtitle based on available scale labels
    subtitle = f"Scale from {scale_min} to {scale_max}"
    if 'min' in scale_labels and 'max' in scale_labels:
        subtitle += f": {scale_labels['min']} → {scale_labels['max']}"
    else:
        subtitle += ", showing mean responses across languages"
    
    graph_title = (
        f"Question {question_id}: {question_title}<br>"
        f"<span style='font-size: 14px; color: gray'>{subtitle}</span>"
    )

    # Get scale labels if available
    scale_labels = question.get('scale_labels', {})
    y_axis_title = '<b>Response Value</b>'
    y_axis_ticktext = None
    y_axis_tickvals = None
    
    # Generate tick values and labels with more intermediate points
    tick_step = 0.5  # Use 0.5-unit steps for finer scale
    tick_vals = [i/2 for i in range(int(scale_min*2), int(scale_max*2) + 1)]
    
    if scale_labels:
        if isinstance(scale_labels, dict):
            if 'min' in scale_labels and 'max' in scale_labels:
                # Show both numeric and text labels for min/max with improved formatting and word wrapping
                def wrap_text(text, width=15):
                    """Helper function to wrap text at word boundaries"""
                    words = text.split()
                    lines = []
                    current_line = []
                    current_length = 0
                    
                    for word in words:
                        if current_length + len(word) + 1 <= width:
                            current_line.append(word)
                            current_length += len(word) + 1
                        else:
                            if current_line:
                                lines.append(' '.join(current_line))
                            current_line = [word]
                            current_length = len(word)
                    
                    if current_line:
                        lines.append(' '.join(current_line))
                    return '<br>'.join(lines)

                y_axis_ticktext = [
                    f"{v:.1f}<br><span style='font-size: 11px; line-height: 1.2'>{wrap_text(scale_labels['min']) if v == scale_min else wrap_text(scale_labels['max']) if v == scale_max else ''}</span>"
                    for v in tick_vals
                ]
                y_axis_tickvals = tick_vals
            else:
                # Handle numeric scale labels with improved formatting
                label_items = sorted(
                    [(int(k), v) for k, v in scale_labels.items() if k.isdigit()],
                    key=lambda x: x[0]
                )
                if label_items:
                    y_axis_ticktext = [
                        f"{v:.1f}<br><span style='font-size: 11px'>{next((text for k, text in label_items if k == v), '')}</span>"
                        for v in tick_vals
                    ]
                    y_axis_tickvals = tick_vals
    
    # Update layout with improved formatting
    layout = GRAPH_LAYOUT.copy()
    
    # Update layout
    layout.update({
        'title': {
            'text': graph_title,
            'font': {
                'family': 'Arial, sans-serif',
                'size': 24,
                'color': COLORS['dark']
            },
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        'showlegend': False,
        'yaxis': {
            'title': {
                'text': '',  # Removed 'Response Value' label
                'font': {
                    'family': 'Arial, sans-serif',
                    'size': 16,
                    'color': COLORS['dark']
                },
                'standoff': 20
            },
            'range': [scale_min - 0.5, scale_max + 0.5],
            'tickmode': 'array',
            'ticktext': [f"{i:.0f}" for i in range(scale_min, scale_max + 1)],
            'tickvals': list(range(scale_min, scale_max + 1)),
            'tickfont': {
                'family': 'Arial, sans-serif',
                'size': 12,
                'color': COLORS['dark']
            },
            'gridcolor': COLORS['light'],
            'zeroline': False,
            'fixedrange': True,
            'showgrid': True,
            'gridwidth': 1
        },
        'xaxis': {
            'title': {
                'text': '',  # Removed 'Language' label
                'font': {
                    'family': 'Arial, sans-serif',
                    'size': 16,
                    'color': COLORS['dark']
                },
                'standoff': 15
            },
            'tickangle': 45,
            'tickfont': {
                'family': 'Arial, sans-serif',
                'size': 11,
                'color': COLORS['dark']
            },
            'tickmode': 'array',
            'ticktext': languages,
            'tickvals': list(range(len(languages))),
            'range': [-0.5, len(languages) - 0.5],
            'fixedrange': True,
            'showgrid': False,
            'ticks': 'outside',
            'ticklen': 5,
            'tickwidth': 1,
            'tickcolor': COLORS['dark']
        },
        'height': 600,  # Set explicit height to accommodate footer
        'margin': {
            't': 120,  # Top margin for title
            'b': 200,  # Much larger bottom margin for footer
            'l': 60,   # Left margin
            'r': 50,   # Right margin
            'pad': 10,
            'autoexpand': True  # Allow expansion if needed
        },
        'plot_bgcolor': 'white',
        'paper_bgcolor': 'white',
        'dragmode': False,
        'modebar': {
            'remove': [
                'zoom', 'pan', 'select', 'lasso2d', 'zoomIn', 'zoomOut', 
                'autoScale', 'resetScale', 'toggleSpikelines'
            ],
            'add': ['toImage']
        }
    })
    
    # Update bar text formatting
    fig.update_traces(
        textfont=dict(
            family='Arial, sans-serif',
            size=14,
            color='black'
        ),
        textposition='inside',
        texttemplate='%{text:.2f}' if show_numbers else ''
    )
    
    # Add footer with proper positioning below the plot
    footer = create_graph_footer(
        survey_name=survey_name,
        model_info=model_info,
        data=data,
        selected_languages=selected_languages
    )
    if footer:
        # Update footer position to be below the plot
        footer.update({
            'y': -0.4,  # Position relative to plot area
            'yshift': 0,  # Reset yshift
            'yanchor': 'top',
            'xanchor': 'center',
            'x': 0.5,
            'font': {'size': 11}
        })
        layout['annotations'] = [footer]

    fig.update_layout(layout)
    return fig 