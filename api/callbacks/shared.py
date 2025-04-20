# -*- coding: utf-8 -*-
"""
Shared utilities for callbacks.
"""

import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional

def load_survey_data(survey_id: str, model_id: str) -> Tuple[Optional[List[Dict]], Optional[str]]:
    """
    Load survey response data for a given survey and model.
    Merges data from all results files in the directory.
    
    Args:
        survey_id: ID of the survey to load
        model_id: ID of the model to load (should include data_ prefix if needed)
        
    Returns:
        Tuple of:
        - List of response dictionaries or None if error
        - Error message or None if successful
    """
    try:
        # Ensure model_id has data_ prefix
        model_dir = model_id if model_id.startswith('data_') else f'data_{model_id}'
        
        # Find the results files in data/{survey_id}/{model_id}/
        data_dir = Path(__file__).parent.parent.parent / 'data' / survey_id / model_dir
        print(f"Looking for data in directory: {data_dir}")  # Debug print
        print(f"Directory exists: {data_dir.exists()}")  # Debug print
        
        if not data_dir.exists():
            return None, f"Data directory not found: {data_dir}"
            
        # Find all results files with timestamp pattern
        result_files = list(data_dir.glob('results_*.json'))
        if not result_files:
            return None, f"No results files found in {data_dir}"
            
        print(f"Found {len(result_files)} results files: {[f.name for f in result_files]}")  # Debug print
        
        # Load and merge data from all files
        all_data = []
        for file_path in result_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and 'results' in data:
                        all_data.extend(data['results'])
                    elif isinstance(data, list):
                        all_data.extend(data)
                    else:
                        all_data.append(data)
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")
                continue
                
        if not all_data:
            return None, "No valid data found in results files"
            
        return all_data, None
        
    except Exception as e:
        import traceback
        error_msg = f"Error loading survey data: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)  # Debug print
        return None, error_msg

def load_question_metadata(survey_id: str, question_id: Optional[str] = None) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Load metadata for questions.
    
    Args:
        survey_id: ID of the survey
        question_id: Optional ID of a specific question. If None, returns all questions.
        
    Returns:
        Tuple of:
        - Question metadata (list or dict) or None if error
        - Error message or None if successful
    """
    try:
        # Load metadata from data/{survey_id}/questions.json
        metadata_path = Path(__file__).parent.parent.parent / 'data' / survey_id / 'questions.json'
        print(f"Loading question metadata from: {metadata_path}")  # Debug print
        
        if not metadata_path.exists():
            return None, f"Metadata file not found: {metadata_path}"
            
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
            
        print(f"Raw metadata type: {type(metadata)}")  # Debug print
        print(f"Raw metadata structure: {metadata[:2] if isinstance(metadata, list) else list(metadata.items())[:2]}")  # Debug print
            
        if question_id is None:
            # Return all questions if no specific question requested
            print(f"Loaded metadata with {len(metadata)} questions")  # Debug print
            return metadata, None
            
        # Find the specific question if requested
        if isinstance(metadata, dict):
            question_data = metadata.get(question_id)
            if not question_data:
                return None, f"Question {question_id} not found in metadata"
        else:
            # If metadata is a list, find question by ID in the list
            question_data = next(
                (q for q in metadata if isinstance(q, dict) and str(q.get('id')) == str(question_id)),
                None
            )
            if not question_data:
                return None, f"Question {question_id} not found in metadata"
            
        print(f"Loaded metadata for question {question_id}")  # Debug print
        return question_data, None
        
    except Exception as e:
        print(f"Error loading question metadata: {e}")  # Debug print
        import traceback
        print(traceback.format_exc())
        return None, str(e)

def validate_languages(languages: List[str], data: List[Dict]) -> List[str]:
    """
    Validate and filter language codes against available data.
    
    Args:
        languages: List of language codes to validate
        data: List of response dictionaries
        
    Returns:
        List of valid language codes
    """
    if not data:
        print("No data provided to validate_languages")  # Debug print
        return []
        
    # Get all unique languages from the language_stats
    available_languages = set()
    for item in data:
        if isinstance(item, dict) and 'language_stats' in item:
            available_languages.update(item['language_stats'].keys())
    
    print(f"Available languages in data: {sorted(list(available_languages))}")  # Debug print
    valid_languages = [lang for lang in languages if lang in available_languages]
    print(f"Valid languages after filtering: {valid_languages}")  # Debug print
    
    return valid_languages
