# -*- coding: utf-8 -*-
"""
Main application initialization.

This module initializes the Dash application, sets up configuration,
and registers all necessary callbacks and layouts.
"""

import os
import sys
from pathlib import Path
from typing import Dict

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from dash import Dash, html
import dash_bootstrap_components as dbc
from dotenv import load_dotenv

from api.callbacks import register_callbacks
from api.layout.main import create_layout
from api.state.store import init_state

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

if __name__ == '__main__':
    # Only run the app if this file is executed directly
    app = create_app()
    app.run(debug=True, port=8050)
