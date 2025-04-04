from dash import Dash, html, dcc
from dash.dependencies import Input, Output, State
from format_results import (create_matrix_view, create_comparison_graph, 
                          create_z_score_summary_graph, get_filtered_languages,
                          create_question_view)
import json
import os
import glob

# Initialize the Dash app
app = Dash(__name__)

# Get the most recent summary file
def get_latest_summary_file():
    summary_files = glob.glob("*_by_question.json")
    if not summary_files:
        raise FileNotFoundError("No summary files found")
    summary_files.sort(key=os.path.getmtime, reverse=True)
    return summary_files[0]

# Load the data
try:
    summary_file = get_latest_summary_file()
    with open(summary_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
except Exception as e:
    print(f"Error loading data: {e}")
    data = None

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
        value=[],
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

# Add callbacks
@app.callback(
    Output('matrix-graph', 'figure'),
    [Input('matrix-controls', 'value'),
     Input('global-controls', 'value')]
)
def update_matrix(matrix_controls, global_controls):
    fig = create_matrix_view(data)
    show_numbers = 'show_numbers' in matrix_controls
    fig.update_traces(texttemplate='%{text}' if show_numbers else '', selector=dict(type='heatmap'))
    if 'show_nan' not in global_controls:
        filtered_languages = get_filtered_languages(data)
        update_figure_with_filtered_languages(fig, filtered_languages)
    return fig

# Add other callbacks as needed...

# For Vercel deployment
server = app.server

if __name__ == '__main__':
    app.run_server(debug=True) 