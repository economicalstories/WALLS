from dash import Dash, html, dcc
import plotly.express as px

# Create a simple Dash app
app = Dash(__name__)

# For Vercel
server = app.server

# Create a simple layout
app.layout = html.Div([
    html.H1("WALLS: Wittgenstein's Analysis of LLM Language Systems", 
            style={'textAlign': 'center', 'margin': '20px'}),
    html.P("Dashboard is loading... Please wait a moment.", 
           style={'textAlign': 'center'}),
    html.P("If this message persists, there might be an issue with the data loading.",
           style={'textAlign': 'center', 'color': 'gray'}),
    dcc.Graph(
        figure=px.bar(
            x=["Test", "Data"], 
            y=[1, 2],
            title="Test Chart"
        )
    )
])

if __name__ == '__main__':
    app.run_server(debug=True) 