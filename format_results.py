import pandas as pd
import os
import numpy as np
import json
import glob
from datetime import datetime

def select_results_file():
    """
    Show available results files and let user select one.
    """
    # Get all results CSV files in current directory
    results_files = glob.glob("results_*.csv")
    
    if not results_files:
        raise FileNotFoundError("No results_*.csv files found in current directory")
    
    # Sort by date (assuming filename format)
    results_files.sort(reverse=True)
    
    print("\nAvailable results files:")
    for i, file in enumerate(results_files):
        # Get file creation time
        creation_time = datetime.fromtimestamp(os.path.getctime(file))
        file_size = os.path.getsize(file) / (1024 * 1024)  # Size in MB
        print(f"{i+1}. {file} (Created: {creation_time.strftime('%Y-%m-%d %H:%M:%S')}, Size: {file_size:.2f}MB)")
    
    while True:
        try:
            choice = int(input("\nSelect file number: ")) - 1
            if 0 <= choice < len(results_files):
                return results_files[choice]
            print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a number.")

def load_questions():
    """
    Load and validate questions.json
    """
    with open("questions.json", "r") as f:
        data = json.load(f)
    return data["questions"]

def create_summary_by_question(input_filename, questions_data, llm_threshold=4):
    """
    Create a summary CSV with question metadata and response statistics
    """
    print(f"Reading results file: {input_filename}")
    df = pd.read_csv(input_filename)
    
    # Convert Response and LLM_Verification_Score to numeric
    df['Response'] = pd.to_numeric(df['Response'], errors='coerce')
    df['LLM_Verification_Score'] = pd.to_numeric(df['LLM_Verification_Score'], errors='coerce')
    
    # Filter valid responses
    valid_responses = df[
        ((df['Language'] == 'English') | 
         (df['LLM_Verification_Score'] >= llm_threshold)) &
        (df['Response'].notna())
    ]
    
    # Create question lookup dict
    questions_lookup = {q['question_id']: q for q in questions_data}
    
    # Calculate statistics by question
    results = []
    for question_id, group in valid_responses.groupby('Question_ID'):
        if question_id in questions_lookup:
            q_data = questions_lookup[question_id]
            
            # Calculate statistics by language - SIMPLIFIED to just count and mean
            lang_stats_dict = {}
            for lang, lang_group in group.groupby('Language'):
                if not lang_group.empty:
                    responses = lang_group['Response'].dropna()
                    if not responses.empty:
                        lang_stats_dict[lang] = {
                            'count': int(len(responses)),
                            'mean': float(responses.mean())
                        }
            
            # Only add questions that have valid responses
            if lang_stats_dict:
                # Calculate overall statistics
                all_means = [stats['mean'] for stats in lang_stats_dict.values()]
                total_responses = sum(stats['count'] for stats in lang_stats_dict.values())
                
                results.append({
                    'question_id': question_id,
                    'title': q_data['question_title'],
                    'category': q_data['category'],
                    'scale_min': int(q_data['scale_min']),
                    'scale_max': int(q_data['scale_max']),
                    'scale_labels': q_data['scale_labels'],
                    'num_languages': len(lang_stats_dict),
                    'total_responses': total_responses,
                    'overall_mean': float(np.mean(all_means)),
                    'language_stats': lang_stats_dict,
                    'prompt_text': q_data['prompt_text']
                })
    
    # Save as JSON with timestamp
    base = os.path.splitext(input_filename)[0]
    output_filename = f"{base}_by_question.json"
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"Created summary file: {output_filename}")
    return results, output_filename

def create_enhanced_dashboard(summary_file, output_filename='survey_dashboard.html'):
    """
    Create an enhanced dashboard using question metadata
    """
    import plotly.graph_objects as go
    
    print(f"\nDebug: Loading summary file: {summary_file}")
    # Load summary data
    with open(summary_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        print(f"Debug: Loaded {len(data)} questions from summary file")
    
    if not data:
        print("No valid data found to create visualization")
        return
    
    fig = go.Figure()
    
    # Create traces for each question
    for q_idx, question in enumerate(data):
        print(f"\nDebug: Processing question {q_idx + 1}: {question.get('question_id', 'unknown')}")
        
        # Debug print the question structure
        print(f"Debug: Question keys: {list(question.keys())}")
        
        # Skip questions with no language stats
        if not question.get('language_stats'):
            print(f"Debug: Skipping question - no language stats")
            continue
            
        # Sort languages by mean response
        languages = []
        values = []
        try:
            for lang, stats in question['language_stats'].items():
                print(f"Debug: Processing language {lang}, stats: {stats}")
                if stats.get('mean') is not None:
                    languages.append(lang)
                    values.append(stats['mean'])
        except Exception as e:
            print(f"Debug: Error processing language stats: {e}")
            continue
        
        # Only create trace if we have data
        if languages and values:
            try:
                fig.add_trace(
                    go.Bar(
                        x=languages,
                        y=values,
                        name=question['question_id'],
                        visible=False,
                        hovertemplate=(
                            "Language: %{x}<br>" +
                            "Mean Response: %{y:.2f}<br>" +
                            "<extra></extra>"
                        )
                    )
                )
                print(f"Debug: Added trace with {len(languages)} languages")
            except Exception as e:
                print(f"Debug: Error adding trace: {e}")
                continue
    
    # Check if we created any traces
    if not fig.data:
        print("No valid traces created. Check if there's enough data for visualization.")
        return
    
    print("\nDebug: Created traces successfully, making first trace visible")
    fig.data[0].visible = True
    
    # Create dropdown buttons
    dropdown_buttons = []
    for idx, question in enumerate(data):
        try:
            if not question.get('language_stats'):
                continue
                
            visible_array = [i == idx for i in range(len(fig.data))]
            
            # Format question title and metadata
            title_text = (
                f"<b>{question['question_id']}: {question['title']}</b><br>" +
                f"Category: {question['category']}<br>" +
                f"Scale: {question['scale_min']} ({question['scale_labels'].get('min', '')}) to " +
                f"{question['scale_max']} ({question['scale_labels'].get('max', '')})<br><br>" +
                f"{question['prompt_text']}"
            )
            
            dropdown_buttons.append(dict(
                label=f"{question['question_id']}: {question['title'][:50]}...",
                method="update",
                args=[
                    {"visible": visible_array},
                    {
                        "title": {"text": title_text},
                        "yaxis": {
                            "range": [
                                question['scale_min'] - 0.5,
                                question['scale_max'] + 0.5
                            ],
                            "title": f"Response (Scale: {question['scale_min']}-{question['scale_max']})"
                        }
                    }
                ]
            ))
            print(f"Debug: Added dropdown button for question {question['question_id']}")
        except Exception as e:
            print(f"Debug: Error creating dropdown button for question {idx}: {e}")
            continue
    
    if not dropdown_buttons:
        print("No valid questions to display")
        return
    
    print("\nDebug: Creating layout")
    # Update layout
    try:
        first_question = data[0]
        fig.update_layout(
            title={
                "text": (
                    f"<b>{first_question['question_id']}: {first_question['title']}</b><br>" +
                    f"Category: {first_question['category']}<br>" +
                    f"Scale: {first_question['scale_min']} to {first_question['scale_max']}<br><br>" +
                    f"{first_question['prompt_text']}"
                ),
                "x": 0.5,
                "xanchor": "center",
                "y": 0.95,
                "yanchor": "top"
            },
            updatemenus=[{
                "buttons": dropdown_buttons,
                "direction": "down",
                "showactive": True,
                "x": 0.1,
                "xanchor": "left",
                "y": 1.2,
                "yanchor": "top"
            }],
            margin=dict(t=200, l=50, r=50, b=100),
            height=800,
            xaxis_title="Language",
            yaxis_title=f"Response (Scale: {first_question['scale_min']}-{first_question['scale_max']})",
            xaxis=dict(tickangle=45),
            showlegend=False
        )
        print("Debug: Layout created successfully")
    except Exception as e:
        print(f"Debug: Error creating layout: {e}")
        return
    
    # Save the figure
    try:
        fig.write_html(output_filename)
        print(f"Dashboard saved as {output_filename}")
    except Exception as e:
        print(f"Error saving dashboard: {e}")

def main():
    try:
        # Select results file
        input_file = select_results_file()
        
        # Load questions data
        questions_data = load_questions()
        
        # Create summary
        results, summary_file = create_summary_by_question(input_file, questions_data)
        
        # Create enhanced dashboard
        create_enhanced_dashboard(summary_file)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()