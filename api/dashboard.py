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
    meta_tags=[
        {"charset": "utf-8"},
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0, user-scalable=no"},
        {"name": "apple-mobile-web-app-capable", "content": "yes"},
        {"name": "mobile-web-app-capable", "content": "yes"}
    ]
)

# Add helper functions at the start, before any data loading
def format_timestamp(timestamp):
    """Convert timestamp string to friendly date format"""
    try:
        # Parse the timestamp format YYYYMMDD_HHMMSS
        date_obj = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
        # Use string formatting that works across platforms
        day = str(int(date_obj.strftime("%d")))  # Remove leading zero
        month = date_obj.strftime("%B")
        year = date_obj.strftime("%Y")
        return f"{day} {month} {year}"
    except ValueError:
        try:
            # Try just the date part if time part fails
            date_str = timestamp.split('_')[0]
            date_obj = datetime.strptime(date_str, "%Y%m%d")
            day = str(int(date_obj.strftime("%d")))  # Remove leading zero
            month = date_obj.strftime("%B")
            year = date_obj.strftime("%Y")
            return f"{day} {month} {year}"
        except ValueError:
            return timestamp

def get_language_summary(result_data):
    """Get language summary for a result set"""
    if not result_data:
        return "No languages"
    languages = set()
    for q in result_data:
        languages.update(q.get('language_stats', {}).keys())
    if len(languages) == 1:
        return next(iter(languages))
    return f"{len(languages)} languages"  # Use full word 'languages'

def format_result_option(format_type, lang_summary, timestamp):
    """Format result option label based on specified format"""
    date = format_timestamp(timestamp)
    
    if format_type == 1:
        # Option 1: Compact format - "Hebrew (6 Apr)" or "51 langs (6 Apr)"
        return f"{lang_summary} ({date})"
    elif format_type == 2:
        # Option 2: Minimal format - just show language info, date on hover
        return lang_summary
    elif format_type == 3:
        # Option 3: Date first - "6 Apr: Hebrew" or "6 Apr: 51 langs"
        return f"{date}: {lang_summary}"
    elif format_type == 4:
        # Option 4: Two lines - language on top, date below (using HTML)
        return html.Div([
            html.Div(lang_summary, style={'fontWeight': 'bold'}),
            html.Div(date, style={'fontSize': 'smaller', 'color': '#666'})
        ])
    else:
        # Default format
        return f"{lang_summary}, {date}"

# Load data once at startup
def get_available_surveys():
    """Find all available surveys"""
    surveys = {}
    survey_dir = os.path.join(os.path.dirname(__file__), "surveys")
    for survey in os.listdir(survey_dir):
        survey_path = os.path.join(survey_dir, survey)
        if os.path.isdir(survey_path):
            # Check if this is a valid survey directory (has questions.json)
            if os.path.exists(os.path.join(survey_path, "questions.json")):
                surveys[survey] = {
                    'id': survey,
                    'path': survey_path,
                    'results': get_available_results(survey_path)
                }
    return surveys

def get_available_results(survey_path):
    """Find all available result sets for a survey"""
    results = {}
    data_dir = os.path.join(survey_path, "data")
    print(f"Looking for results in: {data_dir}")  # Debug print
    if os.path.exists(data_dir):
        # Add special "combined" option first
        results["combined"] = {
            'id': 'combined',
            'path': data_dir,  # Store directory path for combined results
            'is_combined': True
        }
        
        for file in os.listdir(data_dir):
            print(f"Found file: {file}")  # Debug print
            if file.startswith("results_") and file.endswith(".json"):
                # Extract timestamp from filename
                timestamp = file[8:-5]  # Remove 'results_' and '.json'
                print(f"Adding result with timestamp: {timestamp}")  # Debug print
                results[timestamp] = {
                    'id': timestamp,
                    'path': os.path.join(data_dir, file),
                    'is_combined': False
                }
    print(f"Found results: {results}")  # Debug print
    return results

def load_survey_questions(survey_id):
    """Load questions for a specific survey"""
    questions_path = os.path.join(os.path.dirname(__file__), "surveys", survey_id, "questions.json")
    if os.path.exists(questions_path):
        with open(questions_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def load_survey_results(survey_id, result_id):
    """Load specific result set for a survey"""
    if result_id == "combined":
        # Load and combine all results
        combined_data = []
        data_dir = os.path.join(os.path.dirname(__file__), "surveys", survey_id, "data")
        
        if os.path.exists(data_dir):
            all_results = {}
            
            # First, collect all results
            for file in os.listdir(data_dir):
                if file.startswith("results_") and file.endswith(".json"):
                    with open(os.path.join(data_dir, file), 'r', encoding='utf-8') as f:
                        result_data = json.load(f)
                        for question in result_data:
                            qid = question['question_id']
                            if qid not in all_results:
                                all_results[qid] = {
                                    'question': question,
                                    'language_stats': {}
                                }
                            # Merge language stats
                            for lang, stats in question['language_stats'].items():
                                if lang not in all_results[qid]['language_stats']:
                                    all_results[qid]['language_stats'][lang] = stats
            
            # Convert back to list format
            for qid in all_results:
                question_data = all_results[qid]['question'].copy()
                question_data['language_stats'] = all_results[qid]['language_stats']
                combined_data.append(question_data)
            
            return combined_data
    else:
        # Load single result file as before
        result_path = os.path.join(os.path.dirname(__file__), "surveys", survey_id, "data", f"results_{result_id}.json")
        if os.path.exists(result_path):
            with open(result_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    return None

def load_survey_metadata(survey_id):
    """Load metadata for a specific survey"""
    questions_path = os.path.join(os.path.dirname(__file__), "surveys", survey_id, "questions.json")
    if os.path.exists(questions_path):
        with open(questions_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('survey', {}).get('copyright', ''), data.get('survey', {}).get('source', '')
    return '', ''

# Load available surveys at startup
print("Loading available surveys...")  # Debug print
available_surveys = get_available_surveys()
print(f"Found surveys: {available_surveys}")  # Debug print

# Get initial values for dropdowns
initial_survey = next(iter(available_surveys.keys())) if available_surveys else None
initial_results = []
initial_result = None
if initial_survey:
    results = available_surveys[initial_survey]['results']
    initial_results = [{'label': f"Results from {result_id}", 'value': result_id} 
                      for result_id in results.keys()]
    initial_result = next(iter(results.keys())) if results else None

# Load initial data
data = load_survey_results(initial_survey, initial_result) if initial_survey and initial_result else []

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

def create_question_view(data, default_view=None, initial_figure=None):
    """Create a question-by-language view with toggleable graph type"""
    if not data:
        return None

    # Create dropdown options with wrapped text
    dropdown_options = []
    for question in data:
        if question.get('language_stats'):
            wrapped_title = textwrap.fill(question['title'], width=50 if default_view == 'bar' else 80)
            dropdown_options.append({
                'label': f"{question['question_id']}: {wrapped_title}",
                'value': question['question_id']
            })

    # Set default controls based on device type
    default_controls = ['bar', 'colors'] if default_view == 'bar' else ['colors']

    return html.Div([
        html.H3("Individual Question Analysis", 
                style=dict(heading_style, **{'fontSize': '20px' if default_view == 'bar' else '24px'})),
        html.P("Analyze how different languages respond to individual questions.",
               style=dict(subtitle_style, **{'fontSize': '12px' if default_view == 'bar' else '14px'})),
        html.Div([
            html.Div("Select Question:", 
                     style={'marginBottom': '5px', 'fontWeight': 'bold', 'fontSize': '14px' if default_view == 'bar' else '16px'}),
            dcc.Dropdown(
                id='question-dropdown',
                options=dropdown_options,
                value=data[0]['question_id'],
                clearable=False,
                optionHeight=60,
                style={'width': '100%'}
            ),
            html.Div([
                html.Div(id='question-details', style={
                    'margin': '20px 0',
                    'padding': '15px',
                    'backgroundColor': '#f8f9fa',
                    'border': '1px solid #dee2e6',
                    'borderRadius': '5px',
                    'maxWidth': '800px',
                    'margin': '20px auto',
                    'wordWrap': 'break-word'
                })
            ])
        ], style={'width': '95%' if default_view == 'bar' else '80%', 'margin': '20px auto'}),
        html.Div([
            dcc.Graph(
                id='question-heatmap',
                figure=initial_figure if initial_figure is not None else {},
                style={'height': '600px' if default_view == 'bar' else '800px'},
                config={
                    'displayModeBar': True,
                    'displaylogo': False,
                    'modeBarButtonsToRemove': [
                        'zoom', 'pan', 'select', 'lasso2d', 'zoomIn', 'zoomOut', 
                        'autoScale', 'resetScale', 'hoverClosestCartesian',
                        'hoverCompareCartesian', 'toggleSpikelines'
                    ],
                    'toImageButtonOptions': {
                        'format': 'png',
                        'filename': 'question_analysis',
                        'height': 800,
                        'width': 1200,
                        'scale': 2
                    },
                    'scrollZoom': False,
                    'doubleClick': False
                }
            )
        ], style={'width': '100%', 'minHeight': '600px' if default_view == 'bar' else '800px'}),
        html.Div([
            dcc.Checklist(
                id='graph-controls',
                options=[
                    {'label': ' Show as Bar Graph', 'value': 'bar'},
                    {'label': ' Show Mean Line', 'value': 'mean'},
                    {'label': ' Show Mode Line', 'value': 'mode'},
                    {'label': ' Show Colors', 'value': 'colors'}
                ],
                value=default_controls,
                style={'margin': '10px', 'fontSize': '12px' if default_view == 'bar' else '14px'}
            )
        ], style={
            'width': '100%',
            'display': 'flex',
            'justifyContent': 'center',
            'marginTop': '10px'
        })
    ])

# Add callback for question details
@app.callback(
    Output('question-details', 'children'),
    [Input('question-dropdown', 'value')]
)
def update_question_details(selected_question_id):
    """Update the question details when a new question is selected"""
    if not selected_question_id:
        return ""
    
    question = next((q for q in data if q['question_id'] == selected_question_id), None)
    if not question:
        return ""
    
    return [
        html.H4(question['question_id'], style={
            'fontSize': '16px',
            'fontWeight': 'bold',
            'marginBottom': '10px'
        }),
        html.P(question['title'], style={
            'fontSize': '14px',
            'marginBottom': '10px'
        }),
        html.P(question.get('prompt_text', ''), style={
            'fontSize': '12px',
            'color': '#666',
            'marginBottom': '10px'
        }),
        html.P(f"Scale: {question['scale_min']} to {question['scale_max']}", style={
            'fontSize': '12px',
            'color': '#666'
        })
    ]

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
    
    # Define common graph configuration
    graph_config = {
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToRemove': [
            'zoom', 'pan', 'select', 'lasso2d', 'zoomIn', 'zoomOut', 
            'autoScale', 'resetScale', 'hoverClosestCartesian',
            'hoverCompareCartesian', 'toggleSpikelines'
        ],
        'toImageButtonOptions': {
            'format': 'png',
            'filename': 'language_comparison',
            'height': 800,
            'width': 1200,
            'scale': 2
        }
    }
    
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
        dcc.Graph(
            id='comparison-graph',
            style={'height': '600px'},
            config=graph_config
        ),
        html.Hr(style={'margin': '40px 0'}),
        html.Div([
            html.H4("Language Deviation Summary", style=heading_style),
            html.P("Shows how much each language tends to differ from the average response pattern (lower score = more similar to average, higher score = more different).",
                   style=subtitle_style)
        ]),
        dcc.Graph(
            id='z-score-summary-graph',
            style={'height': '500px'},
            config=dict(
                graph_config,
                toImageButtonOptions={'filename': 'language_deviation'}
            )
        )
    ])

# Update header with consistent styling and load button
header = html.Div([
    html.H1("WALLS: Wittgenstein's Analysis of LLM Language Systems", 
            style=dict(heading_style, **{
                'fontSize': '32px',  # Increased from 28px
                'margin': '30px 10px 20px',  # Adjusted margins
                'wordWrap': 'break-word',
                'lineHeight': '1.3',  # Slightly increased
                'color': '#1a2a3a',  # Darker, richer color
                'fontWeight': '600'  # Slightly bolder
            })),
    html.P([
        "A project investigating how large language models respond to standardized survey-style prompts in different languages. ",
        "Inspired by Wittgenstein's assertion that 'the limits of my language are the limits of my world,' ",
        "this project uses numeric outputs to compare the 'values' expressed by the LLM when prompted in various languages."
    ], style=dict(subtitle_style, **{
        'fontSize': '15px',  # Increased from 14px
        'padding': '0 20px',  # Increased padding
        'lineHeight': '1.5',  # Increased line height
        'color': '#4a5568',  # Warmer gray color
        'maxWidth': '800px',  # Control line length
        'margin': '0 auto 30px'  # Added bottom margin
    }))
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
    dcc.Graph(
        id='matrix-graph',
        config={
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': [
                'zoom', 'pan', 'select', 'lasso2d', 'zoomIn', 'zoomOut', 
                'autoScale', 'resetScale', 'hoverClosestCartesian',
                'hoverCompareCartesian', 'toggleSpikelines'
            ],
            'toImageButtonOptions': {
                'format': 'png',
                'filename': 'response_matrix',
                'height': 800,
                'width': 1200,
                'scale': 2
            },
            'scrollZoom': False,
            'doubleClick': False
        }
    ),
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

footer = html.Div(id='footer')

# Add helper function for device detection
def is_mobile():
    """Helper function to check if the viewport is mobile-sized"""
    return html.Div([
        html.Div(id='viewport-container', 
                 n_clicks=0,
                 style={
                     'width': '100vw',  # Use viewport width
                     'height': '100vh',  # Use viewport height
                     'position': 'fixed',
                     'top': '0',
                     'left': '0',
                     'overflow': 'hidden',
                     'visibility': 'hidden',
                     'pointer-events': 'none',
                     'z-index': '-1'
                 })
    ])

# Add client-side callback for device detection
app.clientside_callback(
    """
    function(n_clicks) {
        function checkMobile() {
            // Check if the device is actually mobile using user agent
            const isMobileDevice = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
            
            // Check viewport width
            const isNarrowViewport = window.innerWidth < 768;
            
            // Consider it mobile view only if BOTH conditions are true:
            // 1. Either it's a mobile device OR the viewport is narrow
            // 2. The viewport width is less than 768px
            return (isMobileDevice || isNarrowViewport) && window.innerWidth < 768 ? 'mobile' : 'desktop';
        }
        
        // Initial check
        let currentType = checkMobile();
        
        // Add resize listener if not already added
        if (!window.mobileViewListener) {
            window.mobileViewListener = true;
            window.addEventListener('resize', function() {
                let newType = checkMobile();
                if (newType !== currentType) {
                    currentType = newType;
                    // Force callback by updating click count
                    document.getElementById('viewport-container').click();
                }
            });
        }
        
        return currentType;
    }
    """,
    Output('device-type', 'data'),
    Input('viewport-container', 'n_clicks'),
    prevent_initial_call=False
)

# Add mobile info message style
mobile_info_style = {
    'textAlign': 'center',
    'padding': '10px',
    'margin': '10px',
    'backgroundColor': '#f8f9fa',
    'border': '1px solid #dee2e6',
    'borderRadius': '5px',
    'fontSize': '12px',
    'color': '#666',
    'display': 'none'  # Hidden by default
}

# Create mobile info message
mobile_info = html.Div([
    html.P([
        "You are currently in mobile view. ",
        "For additional features including the Matrix View and Language Comparison, ",
        "please visit on a desktop device."
    ])
], id='mobile-info', style=mobile_info_style)

# Add callback to control mobile info visibility
@app.callback(
    Output('mobile-info', 'style'),
    [Input('device-type', 'data')]
)
def update_mobile_info_visibility(device_type):
    """Update mobile info message visibility based on device type"""
    style = dict(mobile_info_style)
    style['display'] = 'block' if device_type == 'mobile' else 'none'
    return style

def create_app_layout():
    """Create the main app layout"""
    return html.Div([
        is_mobile(),
        header,
        mobile_info,
        # Survey Selection Interface
        html.Div([
            # Survey Selection
            html.Div([
                html.Label("Select Survey:", 
                          style={
                              'display': 'block',
                              'marginBottom': '10px',
                              'fontWeight': '600',
                              'color': '#1a2a3a',
                              'fontSize': '15px'
                          }),
                dcc.Dropdown(
                    id='survey-dropdown',
                    options=[{'label': survey_id.upper(), 'value': survey_id} 
                            for survey_id in available_surveys.keys()],
                    value=initial_survey,
                    clearable=False,
                    style={
                        'width': '100%',
                        'marginBottom': '25px',
                        'backgroundColor': 'white',
                        'fontSize': '14px'
                    }
                ),
            ], style={'width': '100%'}),
            
            # Result Set Selection
            html.Div([
                html.Label("Select Result Set:", 
                          style={
                              'display': 'block',
                              'marginBottom': '10px',
                              'fontWeight': '600',
                              'color': '#1a2a3a',
                              'fontSize': '15px'
                          }),
                dcc.Dropdown(
                    id='result-dropdown',
                    options=initial_results,
                    value=initial_result,
                    clearable=False,
                    style={
                        'width': '100%',
                        'marginBottom': '25px',
                        'backgroundColor': 'white',
                        'fontSize': '14px'
                    }
                ),
            ], style={'width': '100%'}),
            
            # Load Button
            html.Div([
                html.Button(
                    'Load Survey', 
                    id='load-survey-button',
                    n_clicks=0,
                    style={
                        'width': '100%',
                        'padding': '12px 20px',
                        'backgroundColor': '#4CAF50',
                        'color': 'white',
                        'border': 'none',
                        'borderRadius': '6px',
                        'cursor': 'pointer',
                        'fontSize': '16px',
                        'fontWeight': '600',
                        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                        'transition': 'all 0.3s ease',
                        'opacity': '0.6',  # Initially dimmed
                        'letterSpacing': '0.5px'
                    }
                )
            ], style={'width': '100%', 'marginBottom': '25px'})
        ], style={
            'width': '100%',
            'maxWidth': '800px',
            'margin': '0 auto',
            'marginTop': '25px',
            'marginBottom': '35px'
        }),
        global_controls,
        dcc.Store(id='device-type', data='desktop'),
        dcc.Store(id='data-loaded', data=False),
        dcc.Store(id='initial-load', data=True),
        dcc.Store(id='current-survey', data=initial_survey),
        dcc.Store(id='current-result', data=initial_result),
        html.Div(id='content-container'),
        footer
    ])

app.layout = create_app_layout()

# Update the load_survey_data callback to update current selections
@app.callback(
    [Output('content-container', 'children'),
     Output('data-loaded', 'data'),
     Output('initial-load', 'data'),
     Output('footer', 'children'),
     Output('current-survey', 'data'),
     Output('current-result', 'data')],
    [Input('load-survey-button', 'n_clicks'),
     Input('initial-load', 'data'),
     Input('device-type', 'data')],
    [State('survey-dropdown', 'value'),
     State('result-dropdown', 'value')]
)
def load_survey_data(n_clicks, is_initial, device_type, selected_survey, selected_result):
    """Load survey data when button is clicked or on initial load"""
    if not is_initial and n_clicks == 0:
        return None, False, False, None, None, None
        
    if not selected_survey or not selected_result:
        return (
            html.Div("Please select both a survey and result set.", 
                    style={'textAlign': 'center', 'margin': '20px'}),
            False, False, None, None, None
        )
    
    # Load the data
    global data
    data = load_survey_results(selected_survey, selected_result)
    
    if not data:
        return (
            html.Div("Error loading survey data.", 
                    style={'textAlign': 'center', 'margin': '20px'}),
            False, False, None, None, None
        )
    
    # Load survey metadata for footer
    copyright_text, source_text = load_survey_metadata(selected_survey)
    footer_content = html.P([
        f"{copyright_text}",
        html.Br(),
        "Method and source code for WALLS: Wittgenstein's Analysis of LLM Language Systems available at ",
        html.A("GitHub", href="https://github.com/economicalstories/WALLS", target="_blank")
    ], style={'textAlign': 'center', 'fontSize': '0.8em', 'color': '#666', 'margin': '20px'})
    
    # Create initial figure for question view
    if data and len(data) > 0:
        initial_question = data[0]
        languages = get_filtered_languages(data)
        initial_figure = create_single_question_heatmap(
            initial_question,
            languages,
            ['bar', 'colors'] if device_type == 'mobile' else ['colors']
        )
    else:
        initial_figure = go.Figure()

    # Create appropriate content based on device type
    if device_type == 'mobile':
        content = html.Div([
            html.Div([
                html.H3("Individual Question Analysis", style=heading_style),
                html.P("Analyze how different languages respond to individual questions.",
                       style=subtitle_style),
                html.Div([
                    html.Label("Select Question:", 
                             style={'marginBottom': '5px', 'fontWeight': 'bold', 'fontSize': '14px'}),
                    dcc.Dropdown(
                        id='question-dropdown',
                        options=[{
                            'label': f"{q['question_id']}: {textwrap.fill(q['title'], width=50)}",
                            'value': q['question_id']
                        } for q in data if q.get('language_stats')],
                        value=data[0]['question_id'] if data else None,
                        clearable=False,
                        optionHeight=60,
                        style={'width': '100%'}
                    ),
                    html.Div(id='question-details', style={
                        'margin': '20px 0',
                        'padding': '15px',
                        'backgroundColor': '#f8f9fa',
                        'border': '1px solid #dee2e6',
                        'borderRadius': '5px'
                    })
                ], style={'width': '95%', 'margin': '20px auto'}),
                dcc.Graph(
                    id='question-heatmap',
                    figure=initial_figure,
                    style={'height': '600px'},
                    config={
                        'displayModeBar': True,
                        'displaylogo': False,
                        'modeBarButtonsToRemove': [
                            'zoom', 'pan', 'select', 'lasso2d', 'zoomIn', 'zoomOut', 
                            'autoScale', 'resetScale', 'hoverClosestCartesian',
                            'hoverCompareCartesian', 'toggleSpikelines'
                        ],
                        'toImageButtonOptions': {
                            'format': 'png',
                            'filename': 'question_analysis',
                            'height': 800,
                            'width': 1200,
                            'scale': 2
                        },
                        'scrollZoom': False,
                        'doubleClick': False
                    }
                ),
                html.Div([
                    dcc.Checklist(
                        id='graph-controls',
                        options=[
                            {'label': ' Show as Bar Graph', 'value': 'bar'},
                            {'label': ' Show Mean Line', 'value': 'mean'},
                            {'label': ' Show Mode Line', 'value': 'mode'},
                            {'label': ' Show Colors', 'value': 'colors'}
                        ],
                        value=['bar', 'colors'],
                        style={'margin': '10px', 'fontSize': '12px'}
                    )
                ], style={
                    'width': '100%',
                    'display': 'flex',
                    'justifyContent': 'center',
                    'marginTop': '10px'
                })
            ])
        ])
    else:
        content = dcc.Tabs([
            dcc.Tab(label='Matrix View', children=[matrix_view]),
            dcc.Tab(label='Question View', children=[
                create_question_view(data, initial_figure=initial_figure)
            ]),
            dcc.Tab(label='Language Comparison', children=[
                create_comparison_view(data)
            ])
        ])
    
    return content, True, False, footer_content, selected_survey, selected_result

# Add callback to update result options with formatted descriptions
@app.callback(
    [Output('result-dropdown', 'options'),
     Output('result-dropdown', 'value')],
    [Input('survey-dropdown', 'value'),
     Input('current-survey', 'data'),
     Input('current-result', 'data')]
)
def update_result_options(selected_survey, current_survey, current_result):
    """Update available result sets when survey is changed"""
    if not selected_survey or selected_survey not in available_surveys:
        return [], None
        
    results = available_surveys[selected_survey]['results']
    # Sort timestamps but put "combined" first
    sorted_timestamps = ["combined"] + sorted([k for k in results.keys() if k != "combined"], reverse=True)
    
    # Create formatted options
    options = []
    for timestamp in sorted_timestamps:
        result_data = load_survey_results(selected_survey, timestamp)
        lang_summary = get_language_summary(result_data)
        
        if timestamp == "combined":
            label = f"All Results Combined ({lang_summary})"
        else:
            friendly_date = format_timestamp(timestamp)
            label = f"{lang_summary}, {friendly_date}"
            
        options.append({'label': label, 'value': timestamp})
    
    if selected_survey == current_survey:
        selected_result = current_result
    else:
        selected_result = sorted_timestamps[0] if sorted_timestamps else None
    
    return options, selected_result

# Add callback to enable/disable Load Survey button
@app.callback(
    [Output('load-survey-button', 'disabled'),
     Output('load-survey-button', 'style')],
    [Input('survey-dropdown', 'value'),
     Input('result-dropdown', 'value'),
     Input('current-survey', 'data'),
     Input('current-result', 'data')]
)
def update_load_button_state(selected_survey, selected_result, current_survey, current_result):
    """Enable/disable Load Survey button based on selection changes"""
    base_style = {
        'width': '100%',
        'padding': '12px 20px',
        'backgroundColor': '#4CAF50',
        'color': 'white',
        'border': 'none',
        'borderRadius': '6px',
        'cursor': 'pointer',
        'fontSize': '16px',
        'fontWeight': '600',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
        'transition': 'all 0.3s ease',
        'opacity': '0.6',  # Initially dimmed
        'letterSpacing': '0.5px',
        'hover': {
            'backgroundColor': '#45a049'
        }
    }
    
    # Check if selection has changed
    selection_changed = (
        selected_survey != current_survey or 
        selected_result != current_result
    )
    
    if selection_changed:
        # Enable button
        base_style['opacity'] = '1'
        base_style['cursor'] = 'pointer'
        return False, base_style
    else:
        # Disable button
        base_style['opacity'] = '0.6'
        base_style['cursor'] = 'not-allowed'
        return True, base_style

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
     Input('device-type', 'data')]
)
def update_question_heatmap(selected_question, graph_controls, device_type):
    """Update the question heatmap based on selected question and graph controls"""
    if not selected_question or not data:
        return go.Figure()
    
    # Find the selected question data
    question = next((q for q in data if q['question_id'] == selected_question), None)
    if not question:
        return go.Figure()
    
    # Get available languages
    languages = get_filtered_languages(data)
    
    # Ensure graph_controls is a list
    graph_controls = graph_controls or []
    
    # For mobile view, ensure we have proper defaults
    if device_type == 'mobile':
        # If no controls are selected, default to bar and colors
        if not graph_controls:
            graph_controls = ['bar', 'colors']
        # If colors is not selected, add it
        if 'colors' not in graph_controls:
            graph_controls.append('colors')
    
    # Create updated figure with current controls
    fig = create_single_question_heatmap(question, languages, graph_controls)
    
    # For mobile view, adjust the layout
    if device_type == 'mobile':
        fig.update_layout(
            height=500,  # Reduced height for mobile
            margin=dict(
                t=80,  # Reduced top margin
                l=120 if 'bar' in graph_controls else 50,  # Adjust left margin based on graph type
                r=20,
                b=50,
                pad=2
            ),
            title={
                'font': {'size': 14}  # Smaller title font
            }
        )
        # Adjust font sizes for mobile
        fig.update_xaxes(tickfont=dict(size=9))
        fig.update_yaxes(tickfont=dict(size=9))
    
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
    
    # Create the comparison graph
    comparison_fig = create_comparison_graph(data, valid_selected)
    
    # Create and configure the z-score summary graph
    summary_fig = create_z_score_summary_graph(data, available_languages)
    
    # Add config for both graphs to enable PNG downloads
    for fig in [comparison_fig, summary_fig]:
        fig.update_layout(
            dragmode=False,
            modebar=dict(
                remove=['zoom', 'pan', 'select', 'lasso2d', 'zoomIn', 'zoomOut', 
                       'autoScale', 'resetScale', 'hoverClosestCartesian',
                       'hoverCompareCartesian', 'toggleSpikelines']
            )
        )
    
    return comparison_fig, summary_fig

# Add these functions before the callbacks
def create_single_question_heatmap(question, all_languages, graph_controls):
    """Create a graph for a single question, with configurable display options"""
    if not question.get('language_stats'):
        return go.Figure()

    # Parse controls with default values
    graph_controls = graph_controls or []
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

    # Calculate dynamic height based on number of languages
    num_languages = len(languages)
    min_height = 400  # Minimum height
    height_per_language = 25  # Reduced space per language
    margin_top = 100  # Space for title and controls
    margin_bottom = 40  # Bottom margin
    total_height = max(min_height, margin_top + (num_languages * height_per_language) + margin_bottom)

    # Create the graph
    fig = go.Figure()
    
    # Add bars/columns with appropriate color scheme
    if show_colors:
        marker_config = dict(
            color=values,
            colorscale='RdYlBu_r' if show_colors else None,
            showscale=False,
            line=dict(width=1, color='rgba(0,0,0,0.3)'),
            opacity=0.85
        )
    else:
        marker_config = dict(
            color='black',
            line=dict(color='black', width=1)
        )

    # Create hover template
    hover_template = (
        "<b>%{customdata[1]}</b><br>" +
        "<b>Response:</b> %{customdata[0]:.2f}<br>" +
        "<b>Scale Label:</b> %{customdata[2]}<br>" +
        "<extra></extra>"
    )

    # Prepare customdata
    customdata = [[val, lang, scale_labels[int(val) - 1] if 0 < int(val) <= len(scale_labels) else "Unknown"] 
                 for val, lang in zip(values, languages)]

    # Add the main trace
    if is_bar_graph:
        fig.add_trace(go.Bar(
            x=values,
            y=languages,
            orientation='h',
            marker=marker_config,
            text=values,
            texttemplate='%{text:.1f}',
            textposition='auto',
            hovertemplate=hover_template,
            customdata=customdata,
            width=0.8
        ))
    else:
        fig.add_trace(go.Bar(
            x=languages,
            y=values,
            orientation='v',
            marker=marker_config,
            text=values,
            texttemplate='%{text:.1f}',
            textposition='auto',
            hovertemplate=hover_template,
            customdata=customdata,
            width=0.8
        ))

    # Add mean and mode lines if enabled
    if show_mean or show_mode:
        annotation_font = dict(size=10, color='rgba(0,0,0,0.7)')
        line_config = dict(width=1.5)
        
        if is_bar_graph:
            if show_mean and mean_value is not None:
                fig.add_vline(
                    x=mean_value, 
                    line=dict(dash="solid", color="rgba(0,0,0,0.7)", **line_config),
                    annotation_text=f"Mean: {mean_value:.1f}",
                    annotation_position="top", 
                    annotation_font=annotation_font
                )
            if show_mode and mode_value is not None:
                fig.add_vline(
                    x=mode_value, 
                    line=dict(dash="dash", color="rgba(0,0,0,0.5)", **line_config),
                    annotation_text=f"Mode: {mode_value:.1f}",
                    annotation_position="bottom", 
                    annotation_font=annotation_font
                )
        else:
            if show_mean and mean_value is not None:
                fig.add_hline(
                    y=mean_value, 
                    line=dict(dash="solid", color="rgba(0,0,0,0.7)", **line_config),
                    annotation_text=f"Mean: {mean_value:.1f}",
                    annotation_position="right", 
                    annotation_font=annotation_font
                )
            if show_mode and mode_value is not None:
                fig.add_hline(
                    y=mode_value, 
                    line=dict(dash="dash", color="rgba(0,0,0,0.5)", **line_config),
                    annotation_text=f"Mode: {mode_value:.1f}",
                    annotation_position="left", 
                    annotation_font=annotation_font
                )

    # Set axis configurations
    if is_bar_graph:
        xaxis_config = dict(
            title="",
            range=[0, question['scale_max'] + 0.5],
            gridcolor='lightgrey',
            showgrid=True,
            tickfont=dict(size=10),
            tickmode='array',
            ticktext=scale_labels,
            tickvals=list(range(1, len(scale_labels) + 1)),
            side='top'
        )
        yaxis_config = dict(
            title="",
            tickfont=dict(size=11),
            automargin=True,
            tickmode='array',
            ticktext=languages,
            tickvals=list(range(len(languages))),
            side='left'
        )
    else:
        xaxis_config = dict(
            title="",
            tickfont=dict(size=10),
            tickangle=45,
            automargin=True,
            tickmode='array',
            ticktext=languages,
            tickvals=list(range(len(languages)))
        )
        yaxis_config = dict(
            title="",
            range=[0, question['scale_max'] + 0.5],
            gridcolor='lightgrey',
            showgrid=True,
            tickfont=dict(size=10),
            tickmode='array',
            ticktext=scale_labels,
            tickvals=list(range(1, len(scale_labels) + 1))
        )

    # Update layout
    fig.update_layout(
        title={
            'text': f"{question['question_id']}: {question['title']}",
            'x': 0.5,
            'xanchor': 'center',
            'y': 0.98,
            'yanchor': 'top',
            'font': {'size': 16}
        },
        height=total_height,
        margin=dict(
            t=margin_top,
            l=150 if is_bar_graph else 50,
            r=20,
            b=margin_bottom if not is_bar_graph else 50,
            pad=2
        ),
        xaxis=xaxis_config,
        yaxis=yaxis_config,
        plot_bgcolor='rgba(245,245,245,0.95)',
        paper_bgcolor='white',
        bargap=0.15,
        showlegend=False,
        uniformtext=dict(mode='hide', minsize=8),
        dragmode=False,
        autosize=True
    )

    # Update axes grids
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')

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

    # Create the figure with restricted interactions
    fig = go.Figure(data=traces)
    
    # Get overall min and max scale values
    min_scale = min(q['scale_min'] for q in questions_data)
    max_scale = max(q['scale_max'] for q in questions_data)
    
    # Update layout with interaction restrictions
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
        margin=dict(t=100, b=150),
        xaxis=dict(
            tickmode='array',
            ticktext=question_labels,
            tickvals=x_positions,
            tickangle=45,
            tickfont=dict(size=10),
            fixedrange=True
        ),
        yaxis=dict(
            range=[0, max_scale + 0.5],  # Changed to start from 0
            gridcolor='lightgray',
            gridwidth=1,
            fixedrange=True
        ),
        dragmode=False,
        paper_bgcolor='white'
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
        marker_color='#1f77b4',
        hovertemplate='<b>Language:</b> %{x}<br><b>Avg. Abs. Z-Score:</b> %{y:.3f}<extra></extra>'
    )])

    # Update layout with interaction restrictions
    fig.update_layout(
        xaxis_title="Language",
        yaxis_title="Average Absolute Z-Score",
        xaxis=dict(
            tickangle=45,
            fixedrange=True
        ),
        yaxis=dict(
            fixedrange=True
        ),
        margin=dict(l=60, r=30, t=30, b=100),
        dragmode=False,
        paper_bgcolor='white'
    )

    return fig

# This is what Vercel will use
application = app.server

if __name__ == '__main__':
    application.run(debug=True, host='0.0.0.0', port=8080) 