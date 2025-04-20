"""
Data validation utilities for survey data.
"""

import os
import json
from typing import List, Dict, Union, Optional

def validate_survey_data(data: List[Dict]) -> bool:
    """
    Validates survey data structure.
    
    Args:
        data: List of survey question dictionaries
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not isinstance(data, list):
        return False
        
    required_fields = {'question_id', 'title', 'language_stats'}
    
    for item in data:
        if not isinstance(item, dict):
            return False
            
        # Check required fields
        if not all(field in item for field in required_fields):
            return False
            
        # Validate language_stats structure
        lang_stats = item.get('language_stats', {})
        if not isinstance(lang_stats, dict):
            return False
            
        for lang, stats in lang_stats.items():
            if not isinstance(stats, dict):
                return False
                
            # Check required statistics
            if not all(field in stats for field in ['mean', 'std', 'n']):
                return False
                
            # Validate numeric fields
            if not all(isinstance(stats[field], (int, float)) for field in ['mean', 'std', 'n']):
                return False
    
    return True

def validate_languages(data: List[Dict], languages: List[str]) -> List[str]:
    """
    Validates and filters language selections against available languages.
    
    Args:
        data: Survey data
        languages: List of language codes to validate
        
    Returns:
        List[str]: List of valid language codes
    """
    available_langs = set()
    for item in data:
        available_langs.update(item.get('language_stats', {}).keys())
    
    return [lang for lang in languages if lang in available_langs]

def validate_question_id(data: List[Dict], question_id: str) -> bool:
    """
    Verifies existence of question ID in data.
    
    Args:
        data: Survey data
        question_id: Question ID to verify
        
    Returns:
        bool: True if question exists, False otherwise
    """
    return any(item.get('question_id') == question_id for item in data)

def validate_file_path(file_path: str, extension: Optional[str] = None) -> bool:
    """
    Validates file path existence and optionally checks extension.
    
    Args:
        file_path: Path to file
        extension: Optional file extension to check (e.g. '.json')
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not os.path.exists(file_path):
        return False
        
    if extension and not file_path.lower().endswith(extension.lower()):
        return False
        
    return True

def validate_json_data(file_path: str) -> Union[Dict, List, None]:
    """
    Validates and loads JSON data from file.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Union[Dict, List, None]: Parsed JSON data if valid, None otherwise
    """
    if not validate_file_path(file_path, '.json'):
        return None
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except (json.JSONDecodeError, UnicodeDecodeError, OSError):
        return None 