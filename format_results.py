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
    Create a summary JSON with question metadata and response statistics
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
    
    # Save timestamped version in root directory
    base = os.path.splitext(input_filename)[0]
    output_filename = f"{base}_by_question.json"
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nCreated summary file: {output_filename}")
    
    # Save a copy in api/data with a fixed name
    api_data_dir = "api/data"
    os.makedirs(api_data_dir, exist_ok=True)
    latest_filename = os.path.join(api_data_dir, "latest_results.json")
    with open(latest_filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Created fixed location copy: {latest_filename}")
    
    return results, output_filename

def save_results(results, input_filename):
    """Save results to a fixed location in the repo"""
    output_filename = "api/data/latest_results.json"
    os.makedirs("api/data", exist_ok=True)
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

def main():
    try:
        # Select results file
        input_file = select_results_file()
        
        # Load questions data
        questions_data = load_questions()
        
        # Create summary
        results, summary_file = create_summary_by_question(input_file, questions_data)
        
        # Save results
        save_results(results, input_file)
        
        print("\nData processing complete!")
        print("\nTo visualize the results:")
        print("1. The processed data has been saved to:", summary_file)
        print("2. To view the interactive dashboard:")
        print("   a. Run the dashboard locally:")
        print("      python api/dashboard.py")
        print("      Then open http://localhost:8080/dashboard/ in your browser")
        print("   b. Or deploy to Vercel for online access")
        print("\nThe dashboard provides three views:")
        print("- Matrix View: Overview of all questions and languages")
        print("- Question View: Detailed analysis of individual questions")
        print("- Language Comparison: Compare responses across languages")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()