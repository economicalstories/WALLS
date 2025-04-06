import pandas as pd
import os
import numpy as np
import json
import glob
from datetime import datetime

def process_results(input_filename, survey_id):
    """
    Process survey results and create summary files for the dashboard.
    """
    print(f"Reading results file: {input_filename}")
    df = pd.read_csv(input_filename)
    
    # Load questions data
    survey_dir = f"api/surveys/{survey_id}"
    questions_file = os.path.join(survey_dir, "questions.json")
    with open(questions_file, "r") as f:
        questions_data = json.load(f)["questions"]
    
    # Convert Response and LLM_Verification_Score to numeric
    df['Response'] = pd.to_numeric(df['Response'], errors='coerce')
    df['LLM_Verification_Score'] = pd.to_numeric(df['LLM_Verification_Score'], errors='coerce')
    
    # Filter valid responses (LLM verification score >= 4 for non-English)
    valid_responses = df[
        ((df['Language'] == 'English') | 
         (df['LLM_Verification_Score'] >= 4)) &
        (df['Response'].notna())
    ]
    
    # Create question lookup dict
    questions_lookup = {q['question_id']: q for q in questions_data}
    
    # Calculate statistics by question
    results = []
    for question_id, group in valid_responses.groupby('Question_ID'):
        if question_id in questions_lookup:
            q_data = questions_lookup[question_id]
            
            # Calculate statistics by language
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
    
    # Get timestamp from input filename (data_YYYYMMDD_HHMMSS.csv)
    timestamp = os.path.basename(input_filename).split('_')[1] + '_' + os.path.basename(input_filename).split('_')[2].split('.')[0]
    
    # Save results in survey data directory
    api_data_dir = os.path.join(survey_dir, "data")
    os.makedirs(api_data_dir, exist_ok=True)
    
    # Save the processed results with the expected filename
    results_filename = os.path.join(api_data_dir, f"results_{timestamp}.json")
    with open(results_filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nCreated results file: {results_filename}")
    
    # Print summary statistics
    print("\nProcessing complete!")
    print(f"Total questions processed: {len(results)}")
    print(f"Total valid responses: {sum(q['total_responses'] for q in results)}")
    print(f"Languages found: {sorted(set(valid_responses['Language']))}")

if __name__ == "__main__":
    print("This module should be run through run_survey.py")