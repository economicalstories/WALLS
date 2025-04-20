# -*- coding: utf-8 -*-
"""
Callback registration module.

This module imports and registers all callbacks for the dashboard application.
"""

from typing import Any
from dash import Dash

from . import (
    question,
    matrix,
    deviation,
    controls
)

def init_callbacks(app: Dash) -> None:
    """Initialize all callbacks for the dashboard application.
    
    This function ensures all callback modules are properly imported
    and their callbacks are registered with the Dash application.
    
    Args:
        app: The Dash application instance
    """
    # Register callbacks from each module
    matrix.register_callbacks(app)
    deviation.register_callbacks(app)
    question.register_callbacks(app)
    controls.register_callbacks(app)

def register_callbacks(app: Dash) -> None:
    """
    Register all callbacks with the application.
    This function is called by app.py after app initialization.
    
    Args:
        app: The Dash application instance
    """
    # Import callback modules
    from . import (
        question,
        matrix,
        deviation,
        controls,
        shared
    )
    
    # Initialize callbacks
    init_callbacks(app)
