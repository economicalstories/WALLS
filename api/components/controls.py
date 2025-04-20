"""
Controls component for the dashboard.
Includes language selection, model selection, and other UI controls.
Inspired by modern React design patterns while maintaining Dash compatibility.
"""

from dash import html, dcc
from dash.dependencies import Input, Output, State
from api.config.styles import COLORS, FONTS, LAYOUT, COMPONENT_STYLES
from .survey_selector import create_survey_selector
import os
import json
from api.utils.formatting import format_timestamp
from api.config.settings import SURVEY_DIR

def create_controls(app) -> html.Div:
    """Create the controls component."""
    print("\nCreating controls component...")
    
    controls = html.Div(
        [
            # Hidden div for initialization trigger
            html.Div(
                id='controls-trigger',
                children='init',
                style={'display': 'none'}
            ),
            
            # Survey selection
            html.Div(
                [
                    html.Label('Survey:', className='control-label'),
                    dcc.Dropdown(
                        id='survey-select',
                        options=[],
                        value=None,
                        clearable=False,
                        className='control-dropdown',
                        placeholder='Select a survey...',
                        persistence=True,
                        persistence_type='session'
                    )
                ],
                className='control-group',
                id='survey-control'
            ),
            
            # Model selection
            html.Div(
                [
                    html.Label('Model:', className='control-label'),
                    dcc.Dropdown(
                        id='model-select',
                        options=[],
                        value=None,
                        clearable=False,
                        className='control-dropdown',
                        placeholder='Select a model...',
                        persistence=True,
                        persistence_type='session'
                    )
                ],
                className='control-group',
                id='model-control'
            ),
            
            # Language selection
            html.Div(
                [
                    html.Label('Languages:', className='control-label'),
                    html.Details(
                        [
                            html.Summary('Select languages to include'),
                            html.Div([
                                html.P(
                                    "Note: Only languages with complete data are checked by default. "
                                    "Languages with missing data for any questions are unchecked.",
                                    style={'fontSize': '0.9em', 'color': '#666', 'marginBottom': '8px'}
                                ),
                                dcc.Checklist(
                                    id='language-select',
                                    options=[],
                                    value=[],
                                    className='control-checklist',
                                    style={'marginTop': '8px'},
                                    persistence=True,
                                    persistence_type='session'
                                )
                            ])
                        ],
                        className='control-details'
                    )
                ],
                className='control-group',
                id='language-control'
            )
        ],
        className='controls-container',
        id='controls-container'
    )
    
    print("Controls component created")
    return controls

def create_controls_old(app):
    """
    Create a modern controls panel component.
    Includes dropdowns, checklists, and other interactive elements.
    """
    
    # Register the collapse callback
    @app.callback(
        [
            Output('dataset-content', 'style'),
            Output('dataset-collapse-button', 'children'),
            Output('language-checklist-container', 'style')
        ],
        [Input('dataset-collapse-button', 'n_clicks')]
    )
    def toggle_dataset_collapse(n_clicks):
        if n_clicks is None or n_clicks % 2 == 0:
            return {'display': 'none'}, "Details of languages included in this dataset ▼", {'display': 'none'}
        return {'display': 'block'}, "Details of languages included in this dataset ▲", {'display': 'block'}
    
    # Register the language selection callback
    @app.callback(
        [
            Output('language-checklist', 'options'),
            Output('language-checklist', 'value'),
            Output('dataset-info', 'children'),
            Output('languages-heading', 'children')
        ],
        [
            Input('survey-dropdown', 'value'),
            Input('model-dropdown', 'value')
        ]
    )
    def update_language_selection(selected_survey, selected_model):
        """Update language selection based on survey and model."""
        if not selected_survey or not selected_model:
            return [], [], "Please select a survey and model to view available languages.", "Languages"
        
        # Find all results files in the data directory
        data_dir = os.path.join(SURVEY_DIR, selected_survey, f"data_{selected_model}")
        if not os.path.exists(data_dir):
            return [], [], f"Data directory not found: {data_dir}", "Languages"
            
        result_files = [f for f in os.listdir(data_dir) 
                       if f.startswith('results_') and f.endswith('.json')]
        if not result_files:
            return [], [], "No results found for the selected survey and model.", "Languages"
        
        # Process all result files and consolidate languages
        languages = {}
        total_questions = 0
        latest_timestamp = None
        
        for result_file in result_files:
            try:
                with open(os.path.join(data_dir, result_file), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Handle both old and new format
                questions = data['results'] if isinstance(data, dict) else data
                quality_metrics = data.get('quality_metrics', {}) if isinstance(data, dict) else {}
                
                if not isinstance(questions, list):
                    continue
                
                # Update total questions if this file has more
                total_questions = max(total_questions, len(questions))
                
                # Update latest timestamp
                timestamp = result_file.split('results_')[-1].split('.')[0]
                if not latest_timestamp or timestamp > latest_timestamp:
                    latest_timestamp = timestamp
                
                # Process languages from this file
                for question in questions:
                    for lang, stats in question.get('language_stats', {}).items():
                        if lang not in languages:
                            languages[lang] = {
                                'questions_present': 0,
                                'total_questions': total_questions,
                                'total_responses': 0,
                                'quality_metrics': quality_metrics.get('language_quality', {}).get(lang, {})
                            }
                        
                        if stats.get('count', 0) > 0:
                            languages[lang]['questions_present'] += 1
                            languages[lang]['total_responses'] += stats['count']
                            
                        # Update quality metrics if better or not set
                        file_metrics = quality_metrics.get('language_quality', {}).get(lang, {})
                        if file_metrics:
                            current_metrics = languages[lang]['quality_metrics']
                            if not current_metrics or file_metrics.get('avg_verification_score', 0) > current_metrics.get('avg_verification_score', 0):
                                languages[lang]['quality_metrics'] = file_metrics
                
            except Exception as e:
                print(f"Error processing file {result_file}: {str(e)}")
                continue
        
        if not languages:
            return [], [], "No language data found in results", "Languages"
        
        # Create options with indicators for missing data
        options = []
        complete_languages = []
        partial_languages = []
        
        for lang, stats in languages.items():
            missing_ratio = 1 - (stats['questions_present'] / stats['total_questions'])
            avg_responses = stats['total_responses'] / stats['questions_present'] if stats['questions_present'] > 0 else 0
            quality = stats.get('quality_metrics', {})
            verification_score = quality.get('avg_verification_score', 0)
            
            # Format label with clear statistics
            label = lang
            if missing_ratio > 0:
                label += f" ({int((1-missing_ratio) * 100)}% coverage)"
            if verification_score > 0:
                label += f" [quality: {verification_score:.1f}]"
            
            disabled = missing_ratio > 0.8 or quality.get('passes_threshold') is False
            
            option = {
                'label': label,
                'value': lang,
                'disabled': disabled,
                'title': (
                    f"Responses: {stats['total_responses']} across {stats['questions_present']} questions\n"
                    f"Coverage: {(1-missing_ratio)*100:.1f}%\n"
                    f"Quality Score: {verification_score:.1f}"
                )
            }
            options.append(option)
            
            if not disabled and missing_ratio < 0.05:
                complete_languages.append(lang)
            elif not disabled and missing_ratio < 0.2:
                partial_languages.append(lang)
        
        # Sort options alphabetically
        options.sort(key=lambda x: x['value'])
        
        # Create info text
        info_text = [
            html.Div([
                html.P([
                    html.Strong("Dataset Summary"),
                    html.Br(),
                    f"Last updated: {format_timestamp(latest_timestamp)}",
                    html.Br(),
                    f"Questions: {total_questions}",
                    html.Br(),
                    f"Languages: {len(languages)} total",
                    html.Br(),
                    f"Complete coverage (>95%): {len(complete_languages)}",
                    html.Br(),
                    f"Partial coverage (80-95%): {len(partial_languages)}"
                ], style={
                    'marginBottom': '8px',
                    'lineHeight': '1.6'
                })
            ], style={
                'backgroundColor': f"{COLORS['background']}40",
                'padding': f"{LAYOUT['padding']['normal']}px",
                'borderRadius': f"{LAYOUT['border_radius']}px",
                'marginBottom': '16px'
            })
        ]
        
        # Update the heading with language count
        heading = f"{len(languages)} Languages"
        
        return options, complete_languages, html.Div(info_text), heading
    
    return html.Div([
        # Main Controls Section
        html.Div([
            # Language Selection
            html.Div([
                html.Label(
                    "Languages",
                    id='languages-heading',
                    style={
                        'color': COLORS['text'],
                        'fontSize': f"{FONTS['size']['normal']}px",
                        'fontFamily': FONTS['family'],
                        'fontWeight': '500',
                        'marginBottom': '8px',
                        'display': 'block'
                    }
                ),
                html.Button(
                    "Details of languages included in this dataset ▼",
                    id='dataset-collapse-button',
                    style={
                        'backgroundColor': 'transparent',
                        'border': 'none',
                        'color': COLORS['primary'],
                        'cursor': 'pointer',
                        'padding': '0',
                        'marginBottom': '8px',
                        'fontFamily': FONTS['family'],
                        'fontSize': f"{FONTS['size']['small']}px",
                        'textAlign': 'left',
                        'width': '100%'
                    }
                ),
                html.Div(
                    id='dataset-content',
                    style={'display': 'none'},
                    children=[
                        html.Div(
                            id='dataset-info',
                            style={
                                'marginBottom': '16px',
                                'fontSize': f"{FONTS['size']['small']}px"
                            }
                        )
                    ]
                ),
                html.Div(
                    id='language-checklist-container',
                    style={'display': 'none'},
                    children=[
                        dcc.Checklist(
                            id='language-checklist',
                            options=[],
                            value=[],
                            style={
                                'maxHeight': '300px',
                                'overflowY': 'auto',
                                'marginBottom': '16px'
                            },
                            className='language-checklist'
                        )
                    ]
                )
            ])
        ], style=COMPONENT_STYLES['container'])
    ]) 