import pandas as pd
import os
import numpy as np
import json
import glob
from datetime import datetime
import plotly.graph_objects as go
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
from plotly.subplots import make_subplots
import textwrap
import plotly.express as px

def select_results_file():
    """
    Show available results files and let user select one.
    """
    # Get all results CSV files in current directory
    results_files = glob.glob("results_*.csv")
    
    if not results_files:
        raise FileNotFoundError("No results_*.csv files found in current directory")
    
    # Sort by date (assuming filename format)
    results_files.sort(reverse=True)
    
    print("\nAvailable results files:")
    for i, file in enumerate(results_files):
        # Get file creation time
        creation_time = datetime.fromtimestamp(os.path.getctime(file))
        file_size = os.path.getsize(file) / (1024 * 1024)  # Size in MB
        print(f"{i+1}. {file} (Created: {creation_time.strftime('%Y-%m-%d %H:%M:%S')}, Size: {file_size:.2f}MB)")
    
    while True:
        try:
            choice = int(input("\nSelect file number: ")) - 1
            if 0 <= choice < len(results_files):
                return results_files[choice]
            print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a number.")

def load_questions():
    """
    Load and validate questions.json
    """
    with open("questions.json", "r") as f:
        data = json.load(f)
    return data["questions"]

def create_summary_by_question(input_filename, questions_data, llm_threshold=4):
    """
    Create a summary CSV with question metadata and response statistics
    """
    print(f"Reading results file: {input_filename}")
    df = pd.read_csv(input_filename)
    
    # Convert Response and LLM_Verification_Score to numeric
    df['Response'] = pd.to_numeric(df['Response'], errors='coerce')
    df['LLM_Verification_Score'] = pd.to_numeric(df['LLM_Verification_Score'], errors='coerce')
    
    # Filter valid responses
    valid_responses = df[
        ((df['Language'] == 'English') | 
         (df['LLM_Verification_Score'] >= llm_threshold)) &
        (df['Response'].notna())
    ]
    
    # Create question lookup dict
    questions_lookup = {q['question_id']: q for q in questions_data}
    
    # Calculate statistics by question
    results = []
    for question_id, group in valid_responses.groupby('Question_ID'):
        if question_id in questions_lookup:
            q_data = questions_lookup[question_id]
            
            # Calculate statistics by language - SIMPLIFIED to just count and mean
            lang_stats_dict = {}
            for lang, lang_group in group.groupby('Language'):
                if not lang_group.empty:
                    responses = lang_group['Response'].dropna()
                    if not responses.empty:
                        lang_stats_dict[lang] = {
                            'count': int(len(responses)),
                            'mean': float(responses.mean())
                        }
            
            # Only add questions that have valid responses
            if lang_stats_dict:
                # Calculate overall statistics
                all_means = [stats['mean'] for stats in lang_stats_dict.values()]
                total_responses = sum(stats['count'] for stats in lang_stats_dict.values())
                
                results.append({
                    'question_id': question_id,
                    'title': q_data['question_title'],
                    'category': q_data['category'],
                    'scale_min': int(q_data['scale_min']),
                    'scale_max': int(q_data['scale_max']),
                    'scale_labels': q_data['scale_labels'],
                    'num_languages': len(lang_stats_dict),
                    'total_responses': total_responses,
                    'overall_mean': float(np.mean(all_means)),
                    'language_stats': lang_stats_dict,
                    'prompt_text': q_data['prompt_text']
                })
    
    # Save as JSON with timestamp
    base = os.path.splitext(input_filename)[0]
    output_filename = f"{base}_by_question.json"
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"Created summary file: {output_filename}")
    return results, output_filename

def create_matrix_view(data):
    """
    Create a matrix view showing all questions vs languages with summary stats
    """
    # Extract unique questions and languages
    questions = [q['question_id'] for q in data]
    
    # Get all languages or filtered languages based on show_nan state
    languages = set()
    for q in data:
        languages.update(q['language_stats'].keys())
    languages = sorted(list(languages), reverse=True)  # Reverse for alphabetical top to bottom
    
    # Create matrix data and store scale info
    matrix_data = []
    scale_info = []  # Store scale info for each question
    for q in questions:
        q_data = next((item for item in data if item['question_id'] == q), None)
        if q_data:
            scale_info.append((1, q_data['scale_max']))  # Always use 1 as min
    
    # Create matrix data
    for lang in languages:
        row = []
        for q_idx, q in enumerate(questions):
            q_data = next((item for item in data if item['question_id'] == q), None)
            if q_data and lang in q_data['language_stats']:
                row.append(q_data['language_stats'][lang]['mean'])
            else:
                row.append(None)
        matrix_data.append(row)
    
    # Convert to numpy array for proper handling of None values
    matrix_data = np.array(matrix_data, dtype=float)
    
    # Calculate summary statistics separately
    summary_stats = calculate_summary_stats(matrix_data)
    
    # Create normalized data using [1-max] -> [0-1] scaling for heatmap only
    normalized_data = np.zeros_like(matrix_data)
    for col in range(matrix_data.shape[1]):
        col_data = matrix_data[:, col]
        scale_min, scale_max = scale_info[col]
        # Normalize from [1-max] to [0-1]
        normalized_data[:, col] = (col_data - scale_min) / (scale_max - scale_min)
    
    # Create the heatmap with separate color arrays for data and stats
    z_colors = np.vstack([normalized_data, np.full((3, normalized_data.shape[1]), None)])  # None for white background
    z_values = np.vstack([matrix_data, summary_stats])
    combined_y = languages + ['Mean', 'Std Dev', 'Mode']
    
    # Create the combined heatmap
    fig = go.Figure(data=go.Heatmap(
        z=z_colors,  # Use separate array for colors
        x=questions,
        y=combined_y,
        colorscale='RdYlBu',
        text=np.round(z_values, 2),  # Use actual values for text
        texttemplate='%{text}',
        textfont={"size": 11},
        hoverongaps=False,
        hovertemplate=(
            "<b>%{y}</b><br>" +
            "<b>Question:</b> %{x}<br>" +
            "<b>Value:</b> %{text:.2f}<br>" +
            "<b>Details:</b> %{customdata}<br>" +
            "<extra></extra>"
        ),
        customdata=[[f"{next((q['title'] for q in data if q['question_id'] == qid), '')}" 
                    for qid in questions] for _ in range(len(combined_y))],
        colorbar=dict(
            title=dict(
                text="Scale",
                side="right"
            ),
            tickmode="array",
            ticktext=["Min (1)", "Mid", "Max"],
            tickvals=[0, 0.5, 1],
            ticks="outside",
            len=0.9,
            thickness=20
        ),
        showscale=True
    ))
    
    # Update layout
    fig.update_layout(
        height=max(800, len(combined_y) * 25 + 100),  # Adjust height for combined view
        margin=dict(t=80, l=120, r=50, b=50),
        xaxis=dict(
            tickangle=45,
            side='top',
            ticktext=questions,
            tickvals=questions,
            tickfont=dict(size=11)
        ),
        yaxis=dict(
            tickfont=dict(size=11),
            tickmode='array',
            ticktext=combined_y,
            tickvals=list(range(len(combined_y))),
            automargin=True
        ),
        hoverlabel=dict(
            bgcolor="white",
            font=dict(size=11, family="Arial")
        )
    )
    
    # Add a shape to separate the summary stats
    fig.add_shape(
        type="line",
        x0=-0.5,
        y0=len(languages) - 0.5,
        x1=len(questions) - 0.5,
        y1=len(languages) - 0.5,
        line=dict(color="black", width=2)
    )
    
    return fig

def calculate_summary_stats(matrix_data):
    """Calculate summary statistics for each column, handling NaN values."""
    summary_stats = []
    
    # Calculate mean for each column
    means = np.nanmean(matrix_data, axis=0)
    summary_stats.append(means)
    
    # Calculate standard deviation for each column
    stds = np.nanstd(matrix_data, axis=0)
    summary_stats.append(stds)
    
    # Calculate mode for each column
    modes = []
    for col in range(matrix_data.shape[1]):
        col_data = matrix_data[:, col]
        valid_data = col_data[~np.isnan(col_data)]
        if len(valid_data) > 0:
            # Round to 1 decimal place for mode calculation
            rounded_data = np.round(valid_data, 1)
            mode_result = float(pd.Series(rounded_data).mode().iloc[0])
            modes.append(mode_result)
        else:
            modes.append(np.nan)
    summary_stats.append(modes)
    
    return np.array(summary_stats)

def create_question_view(data):
    """
    Create a question-by-language view with toggleable graph type
    """
    if not data:
        return None

    # Create dropdown options with wrapped text
    dropdown_options = []
    for question in data:
        if question.get('language_stats'):
            # Wrap the title to ~80 characters per line
            wrapped_title = textwrap.fill(question['title'], width=80)
            dropdown_options.append({
                'label': f"{question['question_id']}: {wrapped_title}",
                'value': question['question_id']
            })

    # Create the layout with a scrollable dropdown, graph, and view toggles
    layout = html.Div([
        html.Div([
            html.Div("Select Question:", style={'marginBottom': '5px', 'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='question-dropdown',
                options=dropdown_options,
                value=data[0]['question_id'],
                clearable=False,
                optionHeight=60,  # Increase height to accommodate wrapped text
                style={
                    'width': '100%',
                }
            )
        ], style={'width': '80%', 'margin': '20px auto'}),
        html.Div([
            dcc.Graph(
                id='question-heatmap',
                style={'height': '800px'},  # Set a fixed initial height
                config={'responsive': True}
            )
        ], style={'width': '100%', 'minHeight': '800px'}),  # Ensure container maintains minimum height
        html.Div([
            dcc.Checklist(
                id='graph-controls',
                options=[
                    {'label': ' Show as Bar Graph', 'value': 'bar'},
                    {'label': ' Show Mean Line', 'value': 'mean'},
                    {'label': ' Show Mode Line', 'value': 'mode'},
                    {'label': ' Show Colors', 'value': 'colors'}
                ],
                value=['colors', 'mean', 'mode'],
                style={'margin': '10px'}
            )
        ], style={
            'width': '100%',
            'display': 'flex',
            'justifyContent': 'center',
            'marginTop': '10px'
        })
    ], style={'width': '100%', 'height': '100%'})

    return layout

def get_scale_labels(question):
    """Convert scale labels from any format to a list of labels."""
    scale_labels = question['scale_labels']
    if isinstance(scale_labels, dict):
        # If it's a min/max format
        if 'min' in scale_labels and 'max' in scale_labels:
            num_points = question['scale_max'] - question['scale_min'] + 1
            if num_points == 2:
                return [scale_labels['min'], scale_labels['max']]
            # For scales > 2 points, create intermediate labels
            labels = [scale_labels['min']]
            for i in range(num_points - 2):
                labels.append(f"Level {i + 2}")
            labels.append(scale_labels['max'])
            return labels
        # If it's a numbered format (e.g., "1": "Very good", "4": "Very bad")
        else:
            labels = [""] * (question['scale_max'] - question['scale_min'] + 1)
            for i in range(question['scale_min'], question['scale_max'] + 1):
                if str(i) in scale_labels:
                    labels[i - question['scale_min']] = scale_labels[str(i)]
                else:
                    labels[i - question['scale_min']] = f"Level {i}"
            return labels
    return [str(i) for i in range(question['scale_min'], question['scale_max'] + 1)]

def create_single_question_heatmap(question, all_languages, graph_controls):
    """
    Create a graph for a single question, with configurable display options
    """
    if not question.get('language_stats'):
        return go.Figure()

    # Parse controls
    is_bar_graph = 'bar' in graph_controls
    show_mean = 'mean' in graph_controls
    show_mode = 'mode' in graph_controls
    show_colors = 'colors' in graph_controls

    # Get scale labels as a list
    scale_labels = get_scale_labels(question)

    # Collect and sort data
    language_data = []
    for lang in all_languages:
        if lang in question['language_stats']:
            language_data.append((lang, question['language_stats'][lang]['mean']))
    
    # Sort by mean value
    language_data.sort(key=lambda x: x[1])
    
    languages = [item[0] for item in language_data]
    values = [item[1] for item in language_data]

    # Calculate statistics
    mean_value = np.mean(values)
    mode_value = float(pd.Series(np.round(values, 1)).mode().iloc[0])

    # Calculate dynamic height based on number of languages and orientation
    row_height = 30 if is_bar_graph else 15  # Adjust height based on orientation
    margin_top = 250  # Space for title and header
    margin_bottom = 80  # Space for bottom axis and labels
    total_height = margin_top + (len(languages) * row_height) + margin_bottom

    # Create the graph
    fig = go.Figure()
    
    # Add bars/columns with appropriate color scheme
    if show_colors:
        marker_config = dict(
            color=values,
            colorscale='RdYlBu',
            showscale=False
        )
    else:
        marker_config = dict(
            color='black',
            line=dict(color='black', width=1)
        )

    # Create hover template based on orientation
    if not is_bar_graph:
        hover_template = (
            "<b>%{x}</b><br>" +
            "<b>Response:</b> %{y:.2f}<br>" +
            "<b>Scale Label:</b> %{customdata}<br>" +
            "<extra></extra>"
        )
        customdata = [scale_labels[int(val) - 1] if 0 < int(val) <= len(scale_labels) else "Unknown" for val in values]
    else:
        hover_template = (
            "<b>%{y}</b><br>" +
            "<b>Response:</b> %{x:.2f}<br>" +
            "<b>Scale Label:</b> %{customdata}<br>" +
            "<extra></extra>"
        )
        customdata = [scale_labels[int(val) - 1] if 0 < int(val) <= len(scale_labels) else "Unknown" for val in values]

    fig.add_trace(go.Bar(
        x=languages if not is_bar_graph else values,
        y=values if not is_bar_graph else languages,
        orientation='v' if not is_bar_graph else 'h',
        marker=marker_config,
        text=values,
        texttemplate='%{text:.2f}',
        textposition='auto',
        hovertemplate=hover_template,
        customdata=customdata
    ))

    # Add mean and mode lines if enabled
    if not is_bar_graph:
        if show_mean:
            fig.add_hline(
                y=mean_value,
                line_dash="solid",
                line_color="black",
                annotation_text=f"Mean: {mean_value:.2f}",
                annotation_position="right",
                annotation_font=dict(size=12)
            )
        if show_mode:
            fig.add_hline(
                y=mode_value,
                line_dash="dash",
                line_color="black",
                annotation_text=f"Mode: {mode_value:.1f}",
                annotation_position="left",
                annotation_font=dict(size=12)
            )
    else:
        if show_mean:
            fig.add_vline(
                x=mean_value,
                line_dash="solid",
                line_color="black",
                annotation_text=f"Mean: {mean_value:.2f}",
                annotation_position="top",
                annotation_font=dict(size=12)
            )
        if show_mode:
            fig.add_vline(
                x=mode_value,
                line_dash="dash",
                line_color="black",
                annotation_text=f"Mode: {mode_value:.1f}",
                annotation_position="bottom",
                annotation_font=dict(size=12)
            )

    # Word wrap the title and prompt text
    wrapped_title = '<br>'.join(textwrap.wrap(question['title'], width=80))
    wrapped_prompt = '<br>'.join(textwrap.wrap(question['prompt_text'], width=80))
    
    # Update layout
    title_text = (
        f"<b>{question['question_id']}: {wrapped_title}</b><br>" +
        f"Category: {question['category']}<br>" +
        f"Scale: {question['scale_min']} to {question['scale_max']}<br><br>" +
        f"{wrapped_prompt}"
    )

    # Set axis configurations based on orientation
    if not is_bar_graph:  # Column graph
        xaxis_config = dict(
            title="",
            tickfont=dict(size=12),
            tickangle=45,
            automargin=True
        )
        yaxis_config = dict(
            title="Response Value",
            title_font=dict(size=12),
            range=[0, question['scale_max'] + 0.5],
            gridcolor='lightgrey',
            showgrid=True,
            tickfont=dict(size=11),
            # Add scale labels to y-axis
            tickmode='array',
            ticktext=scale_labels,
            tickvals=list(range(1, len(scale_labels) + 1))
        )
    else:  # Bar graph
        xaxis_config = dict(
            title="Response Value",
            title_font=dict(size=12),
            range=[0, question['scale_max'] + 0.5],
            gridcolor='lightgrey',
            showgrid=True,
            tickfont=dict(size=11),
            # Add scale labels to x-axis
            tickmode='array',
            ticktext=scale_labels,
            tickvals=list(range(1, len(scale_labels) + 1))
        )
        yaxis_config = dict(
            title="",
            tickfont=dict(size=12),
            automargin=True,
            tickmode='array',
            ticktext=languages,
            tickvals=list(range(len(languages)))
        )

    fig.update_layout(
        title={
            "text": title_text,
            "x": 0.5,
            "xanchor": "center",
            "y": 0.98,
            "yanchor": "top",
            "font": dict(size=14)
        },
        height=total_height,
        margin=dict(
            t=margin_top,
            l=150,
            r=100,
            b=margin_bottom if not is_bar_graph else 80
        ),
        xaxis=xaxis_config,
        yaxis=yaxis_config,
        plot_bgcolor='white',
        bargap=0.2,
        showlegend=False
    )

    return fig

def create_comparison_view(data):
    """
    Create a view comparing selected languages against the overall mean using markers and error bars,
    and showing a summary of average Z-score deviation.
    """
    # Get all languages - but don't filter yet, as that will be handled by the callback
    all_langs = get_all_languages(data)
    comparison_languages = sorted(all_langs)
    
    # Default selection (English only)
    default_selection = ['English'] if 'English' in comparison_languages else []
    if not default_selection and comparison_languages:
        default_selection = [comparison_languages[0]]

    language_checklist = dcc.Checklist(
        id='language-checklist',
        options=[{'label': lang, 'value': lang} for lang in comparison_languages],
        value=default_selection,
        labelStyle={'display': 'inline-block', 'marginRight': '15px'}
    )
    
    comparison_graph = dcc.Graph(id='comparison-graph', style={'height': '600px'}, config={'responsive': True})
    summary_graph = dcc.Graph(id='z-score-summary-graph', style={'height': '500px'}, config={'responsive': True})
    
    # Define styles once to avoid repetition and improve readability
    heading_style = {
        'textAlign': 'center',
        'marginBottom': '5px'
    }
    
    subtitle_style = {
        'textAlign': 'center',
        'fontSize': '0.9em',
        'color': '#666',
        'marginTop': '0px',
        'marginBottom': '20px'
    }
    
    return html.Div([
        html.Div([html.Label("Select languages to compare against the overall mean:"), language_checklist],
                 style={'width': '80%', 'margin': '20px auto', 'textAlign': 'center'}),
        html.Div([
            html.H4("Language Scores vs Overall Mean", style=heading_style),
            html.P("Shows how each selected language's responses compare to the average response (±2 standard deviations) across all languages for each question.",
                  style=subtitle_style)
        ]),
        comparison_graph,
        html.Hr(),
        html.Div([
            html.H4("Language Deviation Summary", style=heading_style),
            html.P("Shows how much each language tends to differ from the average response pattern (lower score = more similar to average, higher score = more different).",
                  style=subtitle_style)
        ]),
        summary_graph
    ])

def create_comparison_graph(data, selected_languages):
    """
    Create a plot comparing selected language scores against the overall mean +/- 2SD using error bars.
    Always shows the overall mean and error bars.
    """
    # No early exit if selected_languages is empty
    # if not selected_languages: 
    #     return go.Figure(layout=dict(title="Please select at least one language to compare."))

    questions_data = [q for q in data if q.get('language_stats')]
    questions_data.sort(key=lambda x: x['question_id'])
    question_ids = [q['question_id'] for q in questions_data]
    question_titles = [q['title'] for q in questions_data]
    
    overall_means = []
    overall_sds = []
    language_scores = {lang: [] for lang in selected_languages}

    # Calculate overall stats and gather language scores
    for q in questions_data:
        lang_stats = q['language_stats']
        valid_means = [stats['mean'] for stats in lang_stats.values() if pd.notna(stats['mean'])]
        
        if len(valid_means) >= 2:
            q_mean = np.mean(valid_means)
            q_std = np.std(valid_means)
        elif len(valid_means) == 1:
            q_mean = valid_means[0]
            q_std = 0
        else:
            q_mean = np.nan
            q_std = np.nan

        overall_means.append(q_mean)
        overall_sds.append(q_std)

        # Only gather scores if languages are selected
        if selected_languages:
            for lang in selected_languages:
                score = lang_stats.get(lang, {}).get('mean', np.nan)
                language_scores[lang].append(score)
            
    overall_means = np.array(overall_means)
    overall_sds = np.array(overall_sds)
    error_values = 2 * overall_sds 

    fig = go.Figure()

    # Add Overall Mean with Error Bars (always plotted)
    fig.add_trace(go.Scatter(
        x=question_ids,
        y=overall_means,
        mode='markers', 
        name='Overall Mean',
        marker=dict(color='black', size=8, symbol='diamond'),
        error_y=dict(
            type='data', 
            array=error_values,
            visible=True,
            thickness=1.5,
            width=5, 
            color='grey'
        ),
        customdata=question_titles,
        hovertemplate='<b>Question:</b> %{x} (%{customdata})<br><b>Overall Mean:</b> %{y:.2f}<br><b>+/- 2SD:</b> %{error_y.array:.2f}<extra></extra>',
        showlegend=True
    ))

    # Add language markers only if languages are selected
    if selected_languages:
        colors = px.colors.qualitative.Plotly
        for i, lang in enumerate(selected_languages):
            lang_scores_np = np.array(language_scores[lang])
            customdata_list = [[om, osd, qt] for om, osd, qt in zip(overall_means, overall_sds, question_titles)]
            
            fig.add_trace(go.Scatter(
                x=question_ids,
                y=lang_scores_np,
                mode='markers',
                name=lang,
                marker=dict(color=colors[i % len(colors)], size=8),
                customdata=customdata_list, 
                hovertemplate=(
                    f'<b>Language:</b> {lang}<br>'
                    f'<b>Question:</b> %{{x}} (%{{customdata[2]}})<br>'
                    f'<b>Score:</b> %{{y:.2f}}<br>'
                    f'<b>Overall Mean:</b> %{{customdata[0]:.2f}}<br>'
                    f'<b>Overall SD:</b> %{{customdata[1]:.2f}}<extra></extra>'
                )
            ))

    # Update layout
    max_scale_list = [q['scale_max'] for q in questions_data if pd.notna(q.get('scale_max'))]
    min_scale_list = [q['scale_min'] for q in questions_data if pd.notna(q.get('scale_min'))]
    max_scale = max(max_scale_list) if max_scale_list else 10
    min_scale = min(min_scale_list) if min_scale_list else 1
    
    fig.update_layout(
        xaxis_title="Question ID",
        yaxis_title="Response Score",
        yaxis_range=[min_scale - 1, max_scale + 1],
        hovermode='closest',
        legend_title_text='Legend',
        xaxis=dict(tickangle=45),
        margin=dict(l=60, r=30, t=30, b=100)  # Reduced top margin since title is removed
    )

    return fig

def create_z_score_summary_graph(data, available_languages=None):
    """
    Create a bar chart showing the average absolute Z-score for each language,
    ordered from lowest to highest deviation.
    """
    # Use provided language list or get all languages
    all_languages = available_languages if available_languages is not None else get_all_languages(data)
    questions_data = [q for q in data if q.get('language_stats')]
    
    language_z_scores = {lang: [] for lang in all_languages}

    # Calculate Z-scores for available languages across all questions
    for q in questions_data:
        lang_stats = q['language_stats']
        valid_means = [stats['mean'] for lang, stats in lang_stats.items() 
                      if lang in all_languages and pd.notna(stats['mean'])]
        
        if len(valid_means) < 2:
            continue  # Need at least 2 points for mean/sd
        
        q_mean = np.mean(valid_means)
        q_std = np.std(valid_means)

        if q_std == 0:
            q_std = 1  # Avoid division by zero

        for lang in all_languages:
            if lang in lang_stats:
                score = lang_stats[lang].get('mean', np.nan)
                if pd.notna(score):
                    z_score = (score - q_mean) / q_std
                    language_z_scores[lang].append(z_score)

    # Calculate average absolute Z-score for each language
    avg_abs_z_scores = {}
    for lang, z_scores in language_z_scores.items():
        if z_scores:  # Only include languages with at least one valid Z-score
            avg_abs_z_scores[lang] = np.mean(np.abs(z_scores))
        else:
            avg_abs_z_scores[lang] = np.nan

    # Sort languages by average absolute Z-score (lowest to highest)
    sorted_langs = sorted(avg_abs_z_scores.keys(), 
                         key=lambda l: avg_abs_z_scores[l] if pd.notna(avg_abs_z_scores[l]) else float('inf'))
    sorted_scores = [avg_abs_z_scores[lang] for lang in sorted_langs]
    
    # Remove languages with NaN scores from plot data
    plot_langs = [l for l, s in zip(sorted_langs, sorted_scores) if pd.notna(s)]
    plot_scores = [s for s in sorted_scores if pd.notna(s)]

    # Create the bar chart
    fig = go.Figure(data=[go.Bar(
        x=plot_langs,
        y=plot_scores,
        marker_color=px.colors.qualitative.Plotly[0],
        hovertemplate='<b>Language:</b> %{x}<br><b>Avg. Abs. Z-Score:</b> %{y:.3f}<extra></extra>'
    )])

    fig.update_layout(
        xaxis_title="Language",
        yaxis_title="Average Absolute Z-Score",
        xaxis=dict(tickangle=45),
        margin=dict(l=60, r=30, t=30, b=100)  # Reduced top margin since title is removed
    )

    return fig

def create_enhanced_dashboard(summary_file, output_filename='survey_dashboard.html'):
    """
    Create an enhanced dashboard with multiple views
    """
    print(f"\nDebug: Loading summary file: {summary_file}")
    with open(summary_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        print(f"Debug: Loaded {len(data)} questions from summary file")
    
    if not data:
        print("No valid data found to create visualization")
        return
    
    # Create the Dash app
    app = dash.Dash(__name__)
    
    # Create the header
    header = html.Div([
        html.H1("WALLS: Wittgenstein's Analysis of LLM Language Systems", 
                style={'textAlign': 'center', 'color': '#2c3e50', 'margin': '20px'}),
        html.P([
            "A project investigating how large language models respond to standardized survey-style prompts in different languages. ",
            "Inspired by Wittgenstein's assertion that 'the limits of my language are the limits of my world,' ",
            "this project uses numeric outputs to compare the 'values' expressed by the LLM when prompted in various languages."
        ], style={'textAlign': 'center', 'margin': '20px', 'maxWidth': '800px', 'margin': '0 auto'})
    ])

    # Create global controls
    global_controls = html.Div([
        dcc.Checklist(
            id='global-controls',
            options=[
                {'label': ' Show Languages with Missing Data', 'value': 'show_nan'}
            ],
            value=[],  # Empty by default - languages with missing data will be hidden
            style={'margin': '10px'}
        )
    ], style={
        'width': '100%',
        'display': 'flex',
        'justifyContent': 'center',
        'marginBottom': '20px'
    })
    
    # Create matrix view with controls
    matrix_view = html.Div([
        dcc.Graph(id='matrix-graph', figure=create_matrix_view(data)),
        html.Div([
            dcc.Checklist(
                id='matrix-controls',
                options=[
                    {'label': ' Show Numbers', 'value': 'show_numbers'}
                ],
                value=['show_numbers'],
                style={'margin': '10px'}
            )
        ], style={
            'width': '100%',
            'display': 'flex',
            'justifyContent': 'center',
            'marginTop': '10px'
        })
    ])
    
    # Create the tabs
    tabs = dcc.Tabs([
        dcc.Tab(label='Matrix View', children=[matrix_view]),
        dcc.Tab(label='Question View', children=[
            create_question_view(data)
        ]),
        dcc.Tab(label='Language Comparison', children=[
            create_comparison_view(data)
        ])
    ], id='tabs')
    
    # Create the footer
    footer = html.Div([
        html.Hr(),
        html.P([
            "Questions adapted from the World Values Survey (WVS) Wave 7 (2017-2022) Master Questionnaire, ",
            "published by the World Values Survey Association (www.worldvaluessurvey.org). ",
            "Please credit: 'World Values Survey Association. (2017-2022). WVS Wave 7 Master Questionnaire.'"
        ], style={'textAlign': 'center', 'fontSize': '0.8em', 'color': '#666', 'margin': '20px'})
    ])
    
    # Create the main layout
    app.layout = html.Div([
        header,
        global_controls,
        tabs,
        footer
    ])

    # Add callback for matrix controls
    @app.callback(
        Output('matrix-graph', 'figure'),
        [Input('matrix-controls', 'value'),
         Input('global-controls', 'value')]
    )
    def update_matrix(matrix_controls, global_controls):
        # Create base figure
        fig = create_matrix_view(data)
        
        # Handle show/hide numbers
        show_numbers = 'show_numbers' in matrix_controls
        fig.update_traces(texttemplate='%{text}' if show_numbers else '', selector=dict(type='heatmap'))
        
        # Always filter unless explicitly showing all languages
        if 'show_nan' not in global_controls:
            filtered_languages = get_filtered_languages(data)
            update_figure_with_filtered_languages(fig, filtered_languages)
        
        return fig

    # Update callback for question view
    @app.callback(
        Output('question-heatmap', 'figure'),
        [Input('question-dropdown', 'value'),
         Input('graph-controls', 'value'),
         Input('global-controls', 'value'),
         Input('tabs', 'value')]  # Add tabs as an input
    )
    def update_question_heatmap(selected_question_id, graph_controls, global_controls, active_tab):
        if not selected_question_id:
            selected_question_id = data[0]['question_id']
        
        question = next((q for q in data if q['question_id'] == selected_question_id), None)
        if not question:
            return {}
        
        # Get languages (filtered by default)
        languages = get_all_languages(data) if 'show_nan' in global_controls else get_filtered_languages(data)
        
        fig = create_single_question_heatmap(question, languages, graph_controls)
        
        # Ensure the figure maintains its dimensions
        fig.update_layout(
            autosize=True,
            height=800,  # Set a fixed height
            transition_duration=500  # Smooth transition when switching
        )
        
        return fig

    # Add callback to update language checklist options based on global controls
    @app.callback(
        [Output('language-checklist', 'options'),
         Output('language-checklist', 'value')],
        [Input('global-controls', 'value'),
         State('language-checklist', 'value')]
    )
    def update_language_checklist(global_controls, current_selection):
        # Get appropriate language list based on global controls
        if 'show_nan' in (global_controls or []):
            available_languages = get_all_languages(data)
        else:
            available_languages = get_filtered_languages(data)
        
        # Create new options
        new_options = [{'label': lang, 'value': lang} for lang in sorted(available_languages)]
        
        # Update selection to only include available languages
        new_selection = [lang for lang in (current_selection or []) if lang in available_languages]
        
        # Ensure English is selected if available
        if 'English' in available_languages and not new_selection:
            new_selection = ['English']
        
        return new_options, new_selection

    # Update comparison callback to use filtered languages
    @app.callback(
        [Output('comparison-graph', 'figure'),
         Output('z-score-summary-graph', 'figure')],
        [Input('language-checklist', 'value'),
         Input('global-controls', 'value')]
    )
    def update_comparison(selected_languages, global_controls):
        # Get appropriate language list based on global controls
        available_languages = (get_all_languages(data) if 'show_nan' in (global_controls or [])
                             else get_filtered_languages(data))
        
        # Filter selected languages to only those available
        valid_selected = [lang for lang in (selected_languages or []) if lang in available_languages]
        
        # Create figures using filtered data
        comparison_fig = create_comparison_graph(data, valid_selected)
        summary_fig = create_z_score_summary_graph(data, available_languages)  # Pass available languages
        return comparison_fig, summary_fig

    # Run the dashboard
    print(f"Dashboard running on http://localhost:8050")
    app.run(debug=False, port=8050)

def get_filtered_languages(data):
    """Get list of languages after filtering out those with NaN values"""
    valid_languages = {'English'}  # Always include English
    for lang in get_all_languages(data):
        if lang == 'English':
            continue
        # Check if language has any NaN values across all questions
        has_missing_data = False
        for q in data:
            if lang not in q['language_stats'] or pd.isna(q['language_stats'][lang]['mean']):
                has_missing_data = True
                break
        if not has_missing_data:
            valid_languages.add(lang)
    return sorted(list(valid_languages), reverse=True)

def get_all_languages(data):
    """Get list of all languages"""
    languages = set()
    for q in data:
        languages.update(q['language_stats'].keys())
    return sorted(list(languages), reverse=True)

def update_figure_with_filtered_languages(fig, filtered_languages):
    """Update a figure to show only filtered languages"""
    heatmap_data = next(trace for trace in fig.data if trace.type == 'heatmap')
    
    # Get current data
    y_data = np.array(heatmap_data.y)
    z_data = np.array(heatmap_data.z)
    text_data = np.array(heatmap_data.text)
    customdata = np.array(heatmap_data.customdata)
    
    # Find indices of languages to keep (excluding summary stats rows)
    valid_indices = [i for i, lang in enumerate(y_data[:-3]) if lang in filtered_languages]
    
    # Filter data
    filtered_y = np.concatenate([y_data[valid_indices], y_data[-3:]])
    filtered_z = np.vstack([z_data[valid_indices], z_data[-3:]])
    filtered_text = np.vstack([text_data[valid_indices], text_data[-3:]])
    filtered_customdata = np.vstack([customdata[valid_indices], customdata[-3:]])
    
    # Update the heatmap
    fig.update_traces(
        z=filtered_z,
        y=filtered_y,
        text=filtered_text,
        customdata=filtered_customdata,
        selector=dict(type='heatmap')
    )
    
    # Update layout
    fig.update_layout(
        height=max(800, len(filtered_y) * 25 + 100),
        yaxis=dict(
            tickfont=dict(size=11),
            tickmode='array',
            ticktext=filtered_y,
            tickvals=list(range(len(filtered_y))),
            automargin=True
        )
    )
    
    # Update the separator line position
    fig.update_shapes(dict(
        y0=len(filtered_y) - 3.5,
        y1=len(filtered_y) - 3.5
    ))

def main():
    try:
        # Select results file
        input_file = select_results_file()
        
        # Load questions data
        questions_data = load_questions()
        
        # Create summary
        results, summary_file = create_summary_by_question(input_file, questions_data)
        
        # Create enhanced dashboard
        create_enhanced_dashboard(summary_file)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()