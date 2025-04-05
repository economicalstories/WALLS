from flask import Flask
from dash import Dash

# Initialize Flask
server = Flask(__name__)

# Initialize Dash
app = Dash(
    __name__,
    server=server,
    url_base_pathname='/',
    serve_locally=True,
    compress=False
)

# Configure response headers
@server.after_request
def add_header(response):
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

# This is what Vercel will use
application = server 