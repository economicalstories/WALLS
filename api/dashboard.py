from flask import Flask
import json
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import textwrap
import os
import glob
from datetime import datetime
import math

# Initialize Flask with minimal settings
server = Flask(__name__)
server.config.update({
    'SEND_FILE_MAX_AGE_DEFAULT': 0,
    'JSON_AS_ASCII': False,
    'JSONIFY_MIMETYPE': 'application/json;charset=utf-8'
})

# Initialize Dash with minimal settings
app = dash.Dash(
    __name__,
    server=server,
    url_base_pathname='/',
    serve_locally=True,
    compress=False,
    update_title=None,
    meta_tags=[{"charset": "utf-8"}]
)

# Load data once at startup
def load_data():
    """Find and load the most recent results file"""
    fixed_location = os.path.join(os.path.dirname(__file__), "data", "latest_results.json")
    if os.path.exists(fixed_location):
        try:
            print(f"Loading from fixed location: {fixed_location}")
            with open(fixed_location, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Failed to load from fixed location: {str(e)}")
            raise

    raise FileNotFoundError("Could not find latest_results.json in the expected location")

# Load data
try:
    data = load_data()
except Exception as e:
    print(f"Error loading data: {str(e)}")
    data = []  # Provide empty default to prevent complete failure

# Enable efficient loading of assets
app.scripts.config.serve_locally = True
app.css.config.serve_locally = True

# Add helper functions before the layout code
def get_all_languages(data):
    """Get list of all languages"""
    languages = set()
    for q in data:
        languages.update(q['language_stats'].keys())
    return sorted(list(languages), reverse=True)

def get_filtered_languages(data):
    """Get list of languages after filtering out those with NaN values"""
    valid_languages = {'English'}  # Always include English
    all_languages = get_all_languages(data)
    for lang in all_languages:
        if lang == 'English':
            continue
        # Check if language has any NaN values across all questions
        has_missing_data = False
        for q in data:
            if lang not in q['language_stats'] or q['language_stats'][lang]['mean'] is None:
                has_missing_data = True
                break
        if not has_missing_data:
            valid_languages.add(lang)
    return sorted(list(valid_languages))

def update_figure_with_filtered_languages(fig, filtered_languages):
    """Update a figure to show only filtered languages"""
    if not fig.data:
        return fig
        
    heatmap_data = fig.data[0]
    if not heatmap_data:
        return fig
    
    # Get current data
    y_data = heatmap_data.y
    z_data = heatmap_data.z
    text_data = heatmap_data.text
    
    # Find indices of languages to keep
    valid_indices = [i for i, lang in enumerate(y_data) if lang in filtered_languages]
    
    # Filter data
    filtered_y = [y_data[i] for i in valid_indices]
    filtered_z = [z_data[i] for i in valid_indices]
    filtered_text = [text_data[i] for i in valid_indices]
    
    # Update the heatmap
    fig.update_traces(
        z=filtered_z,
        y=filtered_y,
        text=filtered_text,
        selector=dict(type='heatmap')
    )
    
    # Update layout
    fig.update_layout(
        height=max(800, len(filtered_y) * 25 + 100),
        yaxis=dict(
            tickfont=dict(size=10),
            automargin=True
        )
    )
    
    return fig

def create_matrix_view(data):
    """Create a matrix view of questions vs languages"""
    # First collect all questions and their metadata
    questions = []
    question_titles = []
    question_scale_labels = []
    
    for q in data:
        short_title = textwrap.shorten(q['title'], width=30, placeholder="...")
        questions.append(f"{q['question_id']}: {short_title}")
        question_titles.append(q['title'])
        
        scale_labels = q['scale_labels']
        if isinstance(scale_labels, dict):
            if 'min' in scale_labels and 'max' in scale_labels:
                question_scale_labels.append((scale_labels['min'], scale_labels['max']))
            else:
                min_label = scale_labels.get(str(q['scale_min']), str(q['scale_min']))
                max_label = scale_labels.get(str(q['scale_max']), str(q['scale_max']))
                question_scale_labels.append((min_label, max_label))
        else:
            question_scale_labels.append((str(q['scale_min']), str(q['scale_max'])))

    # Get all languages and sort them
    languages = sorted(list(set(
        lang for q in data 
        for lang in q['language_stats'].keys()
        if any(stat['mean'] is not None for stat in [q['language_stats'][lang]])
    )))

    # Create matrix data for languages
    matrix_data = []
    text_data = []
    customdata = []

    # Create language rows
    for lang in languages:
        value_row = []
        text_row = []
        customdata_row = []
        
        for q in data:
            stats = q['language_stats'].get(lang, {'mean': None})
            val = stats['mean']
            
            value_row.append(val)
            text_row.append(f"{val:.2f}" if val is not None else "N/A")
            customdata_row.append([
                q['title'],
                q['scale_min'],
                q['scale_max'],
                question_scale_labels[questions.index(f"{q['question_id']}: {textwrap.shorten(q['title'], width=30, placeholder='...')}")][0],
                question_scale_labels[questions.index(f"{q['question_id']}: {textwrap.shorten(q['title'], width=30, placeholder='...')}")][1]
            ])
        
        matrix_data.append(value_row)
        text_data.append(text_row)
        customdata.append(customdata_row)

    # Create the main heatmap figure
    fig = go.Figure()

    # Add language data heatmap
    fig.add_trace(go.Heatmap(
        z=matrix_data,
        x=questions,
        y=languages,
        colorscale='RdBu',
        showscale=True,
        text=text_data,
        texttemplate="%{text}",
        textfont={"size": 10},
        hoverongaps=False,
        customdata=customdata,
        hovertemplate=(
            "<b>Language:</b> %{y}<br>" +
            "<b>Question:</b> %{customdata[0]}<br>" +
            "<b>Value:</b> %{text}<br>" +
            "<b>Scale:</b> %{customdata[3]} (%{customdata[1]}) to %{customdata[4]} (%{customdata[2]})<extra></extra>"
        )
    ))

    # Update matrix layout
    fig.update_layout(
        xaxis_title='',
        yaxis_title='',
        xaxis=dict(
            tickangle=45,
            tickfont=dict(size=10),
            side='top',
            automargin=True
        ),
        yaxis=dict(
            tickfont=dict(size=10),
            automargin=True
        ),
        height=max(800, len(languages) * 25 + 200),
        margin=dict(t=150, l=150, r=50, b=50),
        autosize=True
    )

    return fig

def calculate_summary_stats(matrix_data):
    """Calculate summary statistics for each column"""
    summary_stats = []
    
    # Calculate mean for each column
    means = []
    for col in zip(*matrix_data):
        valid_values = [x for x in col if x is not None]
        mean = sum(valid_values) / len(valid_values) if valid_values else None
        means.append(mean)
    summary_stats.append(means)
    
    # Calculate standard deviation for each column
    stds = []
    for col in zip(*matrix_data):
        valid_values = [x for x in col if x is not None]
        if valid_values:
            mean = sum(valid_values) / len(valid_values)
            variance = sum((x - mean) ** 2 for x in valid_values) / len(valid_values)
            std = math.sqrt(variance)
            stds.append(std)
        else:
            stds.append(None)
    summary_stats.append(stds)
    
    # Calculate mode for each column
    modes = []
    for col in zip(*matrix_data):
        valid_values = [x for x in col if x is not None]
        if valid_values:
            # Count occurrences of each value
            value_counts = {}
            for value in valid_values:
                value_counts[value] = value_counts.get(value, 0) + 1
            # Find the most common value
            mode = max(value_counts.items(), key=lambda x: x[1])[0]
            modes.append(mode)
        else:
            modes.append(None)
    summary_stats.append(modes)
    
    return summary_stats

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

# Define consistent styles for headings and subtitles
heading_style = {
    'textAlign': 'center',
    'color': '#2c3e50',
    'marginBottom': '5px',
    'fontSize': '24px',
    'fontWeight': 'bold',
    'paddingTop': '20px'
}

subtitle_style = {
    'textAlign': 'center',
    'fontSize': '14px',
    'color': '#666',
    'marginTop': '5px',
    'marginBottom': '20px',
    'maxWidth': '800px',
    'margin': '0 auto',
    'paddingBottom': '20px'
}

def create_question_view(data):
    """Create a question-by-language view with toggleable graph type"""
    if not data:
        return None

    # Create dropdown options with wrapped text
    dropdown_options = []
    for question in data:
        if question.get('language_stats'):
            wrapped_title = textwrap.fill(question['title'], width=80)
            dropdown_options.append({
                'label': f"{question['question_id']}: {wrapped_title}",
                'value': question['question_id']
            })

    return html.Div([
        html.H3("Individual Question Analysis", style=heading_style),
        html.P("Analyze how different languages respond to individual questions, with options to view as bars or columns and show statistical markers.",
               style=subtitle_style),
        html.Div([
            html.Div("Select Question:", style={'marginBottom': '5px', 'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='question-dropdown',
                options=dropdown_options,
                value=data[0]['question_id'],
                clearable=False,
                optionHeight=60,
                style={'width': '100%'}
            )
        ], style={'width': '80%', 'margin': '20px auto'}),
        html.Div([
            dcc.Graph(
                id='question-heatmap',
                style={'height': '800px'},
                config={'responsive': True}
            )
        ], style={'width': '100%', 'minHeight': '800px'}),
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
    ])

def create_comparison_view(data):
    """Create a view comparing selected languages against the overall mean"""
    all_langs = get_all_languages(data)
    comparison_languages = sorted(all_langs)
    
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
    
    return html.Div([
        html.H3("Language Comparison Analysis", style=heading_style),
        html.P("Compare how different languages respond across all questions, highlighting variations from the overall patterns.",
               style=subtitle_style),
        html.Div([
            html.Label("Select languages to compare against the overall mean:"),
            language_checklist
        ], style={'width': '80%', 'margin': '20px auto', 'textAlign': 'center'}),
        html.Div([
            html.H4("Language Scores vs Overall Mean", style=heading_style),
            html.P("Shows how each selected language's responses compare to the average response (±2 standard deviations) across all languages for each question.",
                   style=subtitle_style)
        ]),
        comparison_graph,
        html.Hr(style={'margin': '40px 0'}),
        html.Div([
            html.H4("Language Deviation Summary", style=heading_style),
            html.P("Shows how much each language tends to differ from the average response pattern (lower score = more similar to average, higher score = more different).",
                   style=subtitle_style)
        ]),
        summary_graph
    ])

# Update header with consistent styling
header = html.Div([
    html.H1("WALLS: Wittgenstein's Analysis of LLM Language Systems", 
            style=dict(heading_style, **{'fontSize': '32px', 'margin': '20px'})),
    html.P([
        "A project investigating how large language models respond to standardized survey-style prompts in different languages. ",
        "Inspired by Wittgenstein's assertion that 'the limits of my language are the limits of my world,' ",
        "this project uses numeric outputs to compare the 'values' expressed by the LLM when prompted in various languages."
    ], style=subtitle_style)
])

global_controls = html.Div([
    dcc.Checklist(
        id='global-controls',
        options=[
            {'label': ' Show Languages with Missing Data', 'value': 'show_nan'}
        ],
        value=[],
        style={'margin': '10px'}
    )
], style={
    'width': '100%',
    'display': 'flex',
    'justifyContent': 'center',
    'marginBottom': '20px'
})

# Update matrix view with consistent styling and minimal text
matrix_view = html.Div([
    html.H3("Response Matrix by Language", style=heading_style),
    html.P("Darker colors indicate stronger agreement or disagreement.",
           style=subtitle_style),
    dcc.Graph(id='matrix-graph'),
    html.Div([
        dcc.Checklist(
            id='matrix-controls',
            options=[
                {'label': ' Show Numbers', 'value': 'show_numbers'},
                {'label': ' Show Colors', 'value': 'show_colors'}
            ],
            value=['show_numbers', 'show_colors'],
            style={'margin': '10px'}
        )
    ], style={
        'width': '100%',
        'display': 'flex',
        'justifyContent': 'center',
        'marginTop': '10px'
    })
])

tabs = dcc.Tabs([
    dcc.Tab(label='Matrix View', children=[matrix_view]),
    dcc.Tab(label='Question View', children=[
        create_question_view(data)
    ]),
    dcc.Tab(label='Language Comparison', children=[
        create_comparison_view(data)
    ])
], id='tabs')

footer = html.Div([
    html.Hr(),
    html.P([
        "Questions adapted from the World Values Survey (WVS) Wave 7 (2017-2022) Master Questionnaire, ",
        "published by the World Values Survey Association (www.worldvaluessurvey.org). ",
        "Please credit: 'World Values Survey Association. (2017-2022). WVS Wave 7 Master Questionnaire.'"
    ], style={'textAlign': 'center', 'fontSize': '0.8em', 'color': '#666', 'margin': '20px'})
])

app.layout = html.Div([
    header,
    global_controls,
    tabs,
    footer
])

@app.callback(
    Output('matrix-graph', 'figure'),
    [Input('matrix-controls', 'value'),
     Input('global-controls', 'value')]
)
def update_matrix(matrix_controls, global_controls):
    """Update matrix based on controls"""
    # Handle None values for controls
    matrix_controls = matrix_controls if matrix_controls is not None else []
    global_controls = global_controls if global_controls is not None else []
    
    # Create base figure
    fig = create_matrix_view(data)
    
    # Get display settings
    show_numbers = 'show_numbers' in matrix_controls
    show_colors = 'show_colors' in matrix_controls
    
    # Update main heatmap (languages)
    fig.update_traces(
        texttemplate='%{text}' if show_numbers else '',
        textfont={"size": 10 if show_numbers else 1},
        colorscale='RdBu' if show_colors else [[0, 'lightgrey'], [1, 'lightgrey']]
    )
    
    # Filter languages if needed
    if 'show_nan' not in global_controls:
        languages = get_filtered_languages(data)
        
        # Get current data
        heatmap_data = fig.data[0]
        mask = [y in languages for y in heatmap_data.y]
        
        # Apply filter
        fig.update_traces(
            z=[z for i, z in enumerate(heatmap_data.z) if mask[i]],
            y=[y for i, y in enumerate(heatmap_data.y) if mask[i]],
            text=[t for i, t in enumerate(heatmap_data.text) if mask[i]],
            customdata=[c for i, c in enumerate(heatmap_data.customdata) if mask[i]]
        )
    
    # Update matrix height based on visible rows
    visible_rows = len(fig.data[0].y)
    fig.update_layout(
        height=max(800, visible_rows * 25 + 200)
    )
    
    return fig

@app.callback(
    Output('question-heatmap', 'figure'),
    [Input('question-dropdown', 'value'),
     Input('graph-controls', 'value'),
     Input('global-controls', 'value'),
     Input('tabs', 'value')]
)
def update_question_heatmap(selected_question_id, graph_controls, global_controls, active_tab):
    if not selected_question_id:
        selected_question_id = data[0]['question_id']
    
    question = next((q for q in data if q['question_id'] == selected_question_id), None)
    if not question:
        return {}
    
    languages = get_all_languages(data) if 'show_nan' in global_controls else get_filtered_languages(data)
    fig = create_single_question_heatmap(question, languages, graph_controls)
    
    fig.update_layout(
        autosize=True,
        height=800,
        transition_duration=500
    )
    
    return fig

@app.callback(
    [Output('language-checklist', 'options'),
     Output('language-checklist', 'value')],
    [Input('global-controls', 'value'),
     State('language-checklist', 'value')]
)
def update_language_checklist(global_controls, current_selection):
    if 'show_nan' in (global_controls or []):
        available_languages = get_all_languages(data)
    else:
        available_languages = get_filtered_languages(data)
    
    new_options = [{'label': lang, 'value': lang} for lang in sorted(available_languages)]
    new_selection = [lang for lang in (current_selection or []) if lang in available_languages]
    
    if 'English' in available_languages and not new_selection:
        new_selection = ['English']
    
    return new_options, new_selection

@app.callback(
    [Output('comparison-graph', 'figure'),
     Output('z-score-summary-graph', 'figure')],
    [Input('language-checklist', 'value'),
     Input('global-controls', 'value')]
)
def update_comparison(selected_languages, global_controls):
    available_languages = (get_all_languages(data) if 'show_nan' in (global_controls or [])
                         else get_filtered_languages(data))
    
    valid_selected = [lang for lang in (selected_languages or []) if lang in available_languages]
    
    comparison_fig = create_comparison_graph(data, valid_selected)
    summary_fig = create_z_score_summary_graph(data, available_languages)
    return comparison_fig, summary_fig

# Add these functions before the callbacks
def create_single_question_heatmap(question, all_languages, graph_controls):
    """Create a graph for a single question, with configurable display options"""
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
    mean_value = sum(values) / len(values) if values else None
    mode_value = values[0] if values else None

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

def create_comparison_graph(data, selected_languages):
    """Create a comparison graph showing actual values with mean and error bars"""
    if not selected_languages:
        return go.Figure()

    # Define a fixed color sequence
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
              '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

    # First, collect all questions and their data
    questions_data = []
    question_labels = []
    
    for q in data:
        # Create short question label
        short_title = textwrap.shorten(q['title'], width=30, placeholder="...")
        question_label = f"{q['question_id']}: {short_title}"
        
        # Calculate statistics for this question
        valid_stats = {lang: stats['mean'] for lang, stats in q['language_stats'].items() 
                      if stats['mean'] is not None}
        
        if valid_stats:
            values = list(valid_stats.values())
            overall_mean = sum(values) / len(values)
            overall_std = math.sqrt(sum((x - overall_mean) ** 2 for x in values) / len(values))
            
            questions_data.append({
                'question_id': q['question_id'],
                'label': question_label,
                'title': q['title'],
                'stats': valid_stats,
                'mean': overall_mean,
                'std': overall_std,
                'scale_min': q['scale_min'],
                'scale_max': q['scale_max']
            })
            question_labels.append(question_label)

    # Create traces for selected languages
    traces = []
    
    # First add mean and error bars for each question
    x_positions = list(range(len(questions_data)))
    means = [q['mean'] for q in questions_data]
    errors = [q['std'] * 2 for q in questions_data]  # 2 standard deviations
    
    # Add error bars
    traces.append(go.Scatter(
        x=x_positions,
        y=means,
        mode='markers',
        name='Mean',
        marker=dict(
            color='gray',
            size=8,
            symbol='diamond'
        ),
        error_y=dict(
            type='data',
            array=errors,
            visible=True,
            color='gray',
            thickness=1,
            width=5
        ),
        hovertemplate=(
            "<b>Question:</b> %{text}<br>" +
            "<b>Mean:</b> %{y:.2f}<br>" +
            "<b>±2 SD:</b> %{error_y.array:.2f}" +
            "<extra></extra>"
        ),
        text=[q['title'] for q in questions_data]
    ))

    # Then add points for each language
    for i, lang in enumerate(selected_languages):
        x_values = []
        y_values = []
        hover_texts = []
        
        for j, q in enumerate(questions_data):
            if lang in q['stats']:
                x_values.append(j)  # Use numeric position for x
                y_values.append(q['stats'][lang])
                
                hover_text = f"Question: {q['title']}<br>"
                hover_text += f"Language: {lang}<br>"
                hover_text += f"Value: {q['stats'][lang]:.2f}<br>"
                hover_text += f"Mean: {q['mean']:.2f}<br>"
                hover_text += f"±2 SD: {q['std']*2:.2f}"
                hover_texts.append(hover_text)

        if y_values:  # Only add trace if we have data
            traces.append(go.Scatter(
                x=x_values,
                y=y_values,
                mode='markers',
                name=lang,
                marker=dict(
                    color=colors[i % len(colors)],
                    size=10,
                    symbol='circle'
                ),
                hovertext=hover_texts,
                hoverinfo='text'
            ))

    # Create the figure
    fig = go.Figure(data=traces)
    
    # Get overall min and max scale values
    min_scale = min(q['scale_min'] for q in questions_data)
    max_scale = max(q['scale_max'] for q in questions_data)
    
    # Update layout
    fig.update_layout(
        title={
            'text': 'Language Response Values with Mean ±2SD',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24}
        },
        xaxis_title="Questions",
        yaxis_title="Response Value",
        hovermode='closest',
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        margin=dict(t=100, b=150),  # Increase bottom margin for labels
        xaxis=dict(
            tickmode='array',
            ticktext=question_labels,
            tickvals=x_positions,
            tickangle=45,
            tickfont=dict(size=10)
        ),
        yaxis=dict(
            range=[min_scale - 0.5, max_scale + 0.5],  # Add some padding
            gridcolor='lightgray',
            gridwidth=1
        )
    )
    
    return fig

def create_z_score_summary_graph(data, available_languages=None):
    """Create a bar chart showing the average absolute Z-score for each language"""
    # Use provided language list or get all languages
    all_languages = available_languages if available_languages is not None else get_all_languages(data)
    questions_data = [q for q in data if q.get('language_stats')]
    
    language_z_scores = {lang: [] for lang in all_languages}

    # Calculate Z-scores for available languages across all questions
    for q in questions_data:
        lang_stats = q['language_stats']
        # Get valid means for languages that have data
        valid_means = []
        for lang in all_languages:
            if lang in lang_stats and lang_stats[lang].get('mean') is not None:
                valid_means.append(lang_stats[lang]['mean'])
        
        if len(valid_means) < 2:
            continue  # Need at least 2 points for mean/sd
        
        q_mean = sum(valid_means) / len(valid_means)
        q_std = math.sqrt(sum((x - q_mean) ** 2 for x in valid_means) / len(valid_means))

        if q_std == 0:
            continue  # Skip questions with no variation

        for lang in all_languages:
            if lang in lang_stats:
                score = lang_stats[lang].get('mean')
                if score is not None:
                    z_score = (score - q_mean) / q_std
                    language_z_scores[lang].append(z_score)

    # Calculate average absolute Z-score for each language
    avg_abs_z_scores = {}
    for lang, z_scores in language_z_scores.items():
        if z_scores:  # Only include languages with at least one valid Z-score
            avg_abs_z_scores[lang] = sum(abs(z) for z in z_scores) / len(z_scores)

    # Sort languages by average absolute Z-score (lowest to highest)
    sorted_items = sorted(
        [(lang, score) for lang, score in avg_abs_z_scores.items() if score is not None],
        key=lambda x: x[1]
    )
    
    if not sorted_items:
        # Return empty figure if no valid data
        fig = go.Figure()
        fig.update_layout(
            xaxis_title="Language",
            yaxis_title="Average Absolute Z-Score",
            xaxis=dict(tickangle=45),
            margin=dict(l=60, r=30, t=30, b=100)
        )
        return fig
        
    sorted_langs, sorted_scores = zip(*sorted_items)

    # Create the bar chart
    fig = go.Figure(data=[go.Bar(
        x=list(sorted_langs),
        y=list(sorted_scores),
        marker_color='#1f77b4',  # Standard blue color
        hovertemplate='<b>Language:</b> %{x}<br><b>Avg. Abs. Z-Score:</b> %{y:.3f}<extra></extra>'
    )])

    fig.update_layout(
        xaxis_title="Language",
        yaxis_title="Average Absolute Z-Score",
        xaxis=dict(tickangle=45),
        margin=dict(l=60, r=30, t=30, b=100)
    )

    return fig

# This is what Vercel will use
application = app.server

if __name__ == '__main__':
    application.run(debug=True, host='0.0.0.0', port=8050) 