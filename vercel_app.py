import os
import sys
import json
import traceback
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Print debug information about Python path and directory structure
print(f"Python path: {sys.path}")
print(f"Current directory: {os.getcwd()}")
print(f"Project root: {project_root}")
print(f"Directory contents: {os.listdir(project_root)}")

try:
    # Try to import the app module directly
    from api.app import create_app
    
    # Create the Dash app instance
    dash_app = create_app()
    # Expose the Flask server instance as 'app' for Vercel
    # Vercel's runtime should automatically detect and use this.
    app = dash_app.server 

except Exception as e:
    # Log startup errors
    error_traceback = traceback.format_exc()
    print(f"Startup Error: {str(e)}")
    print(f"Startup Traceback: {error_traceback}")
    # Try to list directory even on error for debugging
    try:
        dir_contents = os.listdir(os.getcwd())
    except Exception:
        dir_contents = "Error listing directory"
    print(f"Current directory contents during startup error: {dir_contents}")
    
    # If app creation fails, raise the exception to Vercel
    # This ensures the deployment fails clearly.
    raise e 