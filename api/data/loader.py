"""
Functions for loading survey data and results from files.
"""

import os
import json
import glob
from typing import Dict, List, Optional

def get_available_surveys(survey_dir: str) -> List[Dict]:
    """Get list of available surveys."""
    surveys = []
    for survey_dir in glob.glob(os.path.join(survey_dir, "*")):
        if os.path.isdir(survey_dir):
            survey_id = os.path.basename(survey_dir)
            surveys.append({'label': f"Survey {survey_id}", 'value': survey_id})
    return surveys

def get_available_models(survey_dir: str, survey_name: str) -> List[str]:
    """Get list of available models for a given survey.
    
    Args:
        survey_dir: Base directory containing survey data
        survey_name: Name of the survey
        
    Returns:
        List of model names available for this survey
    """
    survey_path = os.path.join(survey_dir, survey_name)
    if not os.path.exists(survey_path):
        return []
        
    models = set()
    
    # Check data directories
    for item in os.listdir(survey_path):
        if item.startswith('data_'):
            models.add(item[5:])  # Remove 'data_' prefix
        elif item.startswith('results_'):
            models.add(item[8:])  # Remove 'results_' prefix
            
    return sorted(list(models))

def get_available_results(survey_dir: str, survey_id: str, model_name: str) -> List[Dict]:
    """Get list of available result sets for a survey and model."""
    results = []
    data_dir = os.path.join(survey_dir, survey_id, f"data_{model_name}")
    if os.path.exists(data_dir):
        for file_name in os.listdir(data_dir):
            if file_name.startswith('results_') and file_name.endswith('.json'):
                timestamp = file_name[8:-5]  # Remove 'results_' and '.json'
                results.append({'label': timestamp, 'value': timestamp})
    return results

def load_result_data(survey_dir: str, survey_id: str, model_name: str, result_id: str) -> Optional[List]:
    """Load result data from a JSON file."""
    result_file = os.path.join(
        survey_dir, survey_id,
        f"data_{model_name}",
        f"results_{result_id}.json"
    )
    
    if not os.path.exists(result_file):
        return None
        
    with open(result_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_available_languages(data: List) -> List[str]:
    """Get list of all languages in the result data."""
    languages = set()
    for q in data:
        languages.update(q.get('language_stats', {}).keys())
    return sorted(list(languages))

def get_available_questions(data: List) -> List[Dict]:
    """Get list of all questions in the result data."""
    return [
        {'label': f"{q.get('question_id', 'Unknown')}: {q.get('title', 'Unknown')[:50]}...", 
         'value': q.get('question_id')}
        for q in data
    ] 