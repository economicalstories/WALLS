import os
import sys
import json
import traceback
from pathlib import Path
from typing import Dict

from dash import Dash, html
import dash_bootstrap_components as dbc
from dotenv import load_dotenv

# Add the project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Import local modules
from layout.main import create_layout
from state.store import init_state
from callbacks import register_callbacks

def create_app() -> Dash:
    """Create and configure the Dash application."""
    print("\n=== Starting WALLS Dashboard ===")
    
    # Load environment variables
    load_dotenv()
    
    # Initialize app with Bootstrap theme
    print("\nInitializing Dash app...")
    app = Dash(
        __name__,
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        suppress_callback_exceptions=True
    )
    
    # Initialize application state
    print("Initializing application state...")
    init_state()
    
    # Create layout first
    print("\nCreating layout...")
    app.layout = create_layout(app)
    
    # Then register callbacks
    print("\nRegistering callbacks...")
    register_callbacks(app)
    
    print("\nInitialization complete!")
    return app

# Create the app instance
app = create_app()
server = app.server

def handler(event, context):
    try:
        # Handle the request through Flask/Dash
        if event.get('httpMethod') == 'OPTIONS':
            # Handle CORS preflight request
            return {
                'statusCode': 204,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
                }
            }
        
        # Print debug information
        print(f"Received event: {json.dumps(event)}")
        
        # Handle the actual request
        response = server(event, context)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
            },
            'body': response.get('body', '')
        }
        
    except Exception as e:
        error_traceback = traceback.format_exc()
        print(f"Error in handler: {str(e)}")
        print(f"Traceback: {error_traceback}")
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e),
                'traceback': error_traceback
            })
        }

if __name__ == '__main__':
    # Only run the app if this file is executed directly
    app.run(debug=True, port=8050) 