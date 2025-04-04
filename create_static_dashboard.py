import json
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from format_results import (create_matrix_view, create_comparison_graph, 
                          create_z_score_summary_graph, get_filtered_languages)

def create_static_dashboard(summary_file, output_filename='index.html'):
    """
    Create a static HTML dashboard that can be hosted on GitHub Pages
    """
    print(f"\nDebug: Loading summary file: {summary_file}")
    with open(summary_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        print(f"Debug: Loaded {len(data)} questions from summary file")
    
    if not data:
        print("No valid data found to create visualization")
        return

    # Create initial figures
    matrix_fig = create_matrix_view(data)
    
    # Get comparison figures
    comparison_fig = create_comparison_graph(data, ['English'])
    summary_fig = create_z_score_summary_graph(data, get_filtered_languages(data))

    # Create the HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>WALLS: Wittgenstein's Analysis of LLM Language Systems</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .header {{
                text-align: center;
                color: #2c3e50;
                margin: 20px 0;
            }}
            .description {{
                text-align: center;
                margin: 20px auto;
                max-width: 800px;
                color: #666;
            }}
            .tab {{
                overflow: hidden;
                border: 1px solid #ccc;
                background-color: #f1f1f1;
                margin-bottom: 20px;
            }}
            .tab button {{
                background-color: inherit;
                float: left;
                border: none;
                outline: none;
                cursor: pointer;
                padding: 14px 16px;
                transition: 0.3s;
            }}
            .tab button:hover {{
                background-color: #ddd;
            }}
            .tab button.active {{
                background-color: #ccc;
            }}
            .tabcontent {{
                display: none;
                padding: 6px 12px;
                border: 1px solid #ccc;
                border-top: none;
                background-color: white;
            }}
            .footer {{
                text-align: center;
                font-size: 0.8em;
                color: #666;
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #ccc;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>WALLS: Wittgenstein's Analysis of LLM Language Systems</h1>
        </div>
        <div class="description">
            <p>A project investigating how large language models respond to standardized survey-style prompts in different languages.
            Inspired by Wittgenstein's assertion that 'the limits of my language are the limits of my world,'
            this project uses numeric outputs to compare the 'values' expressed by the LLM when prompted in various languages.</p>
        </div>
        
        <div class="tab">
            <button class="tablinks" onclick="openTab(event, 'MatrixView')" id="defaultOpen">Matrix View</button>
            <button class="tablinks" onclick="openTab(event, 'ComparisonView')">Language Comparison</button>
        </div>

        <div id="MatrixView" class="tabcontent">
            <div id="matrix"></div>
        </div>

        <div id="ComparisonView" class="tabcontent">
            <div id="comparison"></div>
            <div id="summary"></div>
        </div>

        <div class="footer">
            <p>Questions adapted from the World Values Survey (WVS) Wave 7 (2017-2022) Master Questionnaire,
            published by the World Values Survey Association (www.worldvaluessurvey.org).<br>
            Please credit: 'World Values Survey Association. (2017-2022). WVS Wave 7 Master Questionnaire.'</p>
        </div>

        <script>
            // Matrix View
            const matrixData = {matrix_fig.to_json()};
            Plotly.newPlot('matrix', matrixData.data, matrixData.layout);

            // Comparison View
            const comparisonData = {comparison_fig.to_json()};
            Plotly.newPlot('comparison', comparisonData.data, comparisonData.layout);
            
            const summaryData = {summary_fig.to_json()};
            Plotly.newPlot('summary', summaryData.data, summaryData.layout);

            function openTab(evt, tabName) {{
                var i, tabcontent, tablinks;
                tabcontent = document.getElementsByClassName("tabcontent");
                for (i = 0; i < tabcontent.length; i++) {{
                    tabcontent[i].style.display = "none";
                }}
                tablinks = document.getElementsByClassName("tablinks");
                for (i = 0; i < tablinks.length; i++) {{
                    tablinks[i].className = tablinks[i].className.replace(" active", "");
                }}
                document.getElementById(tabName).style.display = "block";
                evt.currentTarget.className += " active";
                
                // Trigger a window resize event to ensure plots render correctly
                window.dispatchEvent(new Event('resize'));
            }}

            // Get the element with id="defaultOpen" and click on it
            document.getElementById("defaultOpen").click();
        </script>
    </body>
    </html>
    """

    # Save the HTML file
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\nCreated static dashboard: {output_filename}")
    print("You can now host this file on GitHub Pages by:")
    print("1. Renaming it to 'index.html' if not already named that")
    print("2. Creating a 'gh-pages' branch in your repository")
    print("3. Pushing the HTML file to that branch")
    print("4. Enabling GitHub Pages in your repository settings")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        summary_file = sys.argv[1]
    else:
        # Use the most recent summary file in the current directory
        import glob
        import os
        summary_files = glob.glob("*_by_question.json")
        if not summary_files:
            print("No summary files found")
            sys.exit(1)
        summary_files.sort(key=os.path.getmtime, reverse=True)
        summary_file = summary_files[0]
    
    create_static_dashboard(summary_file) 