from .dashboard import application

# This is what Vercel will look for
app = application

# Make sure all routes are registered
from . import dashboard  # This will register all the Dash routes 