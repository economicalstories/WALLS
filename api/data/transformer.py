"""
Data transformation utilities for survey data.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Union, Tuple

def to_dataframe(data: List[Dict], languages: List[str]) -> pd.DataFrame:
    """
    Converts survey data to a DataFrame format.
    
    Args:
        data: List of survey question dictionaries
        languages: List of languages to include
        
    Returns:
        pd.DataFrame: DataFrame with questions and languages as rows
    """
    rows = []
    for item in data:
        for lang in languages:
            stats = item.get('language_stats', {}).get(lang, {})
            if stats:  # Only add row if language stats exist
                rows.append({
                    'question_id': item['question_id'],
                    'title': item['title'],
                    'language': lang,
                    'mean': stats.get('mean'),
                    'std': stats.get('std'),
                    'n': stats.get('n')
                })
    
    return pd.DataFrame(rows)

def to_matrix(data: List[Dict], languages: List[str]) -> Tuple[np.ndarray, List[str], List[str]]:
    """
    Converts survey data to a matrix format.
    
    Args:
        data: List of survey question dictionaries
        languages: List of languages to include
        
    Returns:
        Tuple containing:
        - np.ndarray: Matrix of mean values (questions x languages)
        - List[str]: Question IDs
        - List[str]: Language codes
    """
    if not data:
        return np.array([]), [], languages
        
    question_ids = [item['question_id'] for item in data]
    matrix = np.zeros((len(data), len(languages)))
    
    for i, item in enumerate(data):
        for j, lang in enumerate(languages):
            mean = item.get('language_stats', {}).get(lang, {}).get('mean')
            matrix[i, j] = mean if mean is not None else np.nan
            
    return matrix, question_ids, languages

def to_dict(data: List[Dict], languages: List[str]) -> Dict:
    """
    Converts survey data to a nested dictionary format.
    
    Args:
        data: List of survey question dictionaries
        languages: List of languages to include
        
    Returns:
        Dict: Nested dictionary with questions and language stats
    """
    result = {}
    for item in data:
        qid = item['question_id']
        result[qid] = {
            'title': item['title'],
            'language_stats': {}
        }
        
        for lang in languages:
            if lang in item.get('language_stats', {}):
                result[qid]['language_stats'][lang] = item['language_stats'][lang]
                
    return result

def normalize_values(data: List[Dict], min_val: float = 0, max_val: float = 1) -> List[Dict]:
    """
    Normalizes mean values to specified range.
    
    Args:
        data: List of survey question dictionaries
        min_val: Minimum value for normalization
        max_val: Maximum value for normalization
        
    Returns:
        List[Dict]: Data with normalized mean values
    """
    # Find global min/max
    all_means = []
    for item in data:
        for stats in item.get('language_stats', {}).values():
            if stats.get('mean') is not None:
                all_means.append(stats['mean'])
                
    if not all_means:
        return data
        
    data_min = min(all_means)
    data_max = max(all_means)
    
    # Skip if no range
    if data_max == data_min:
        return data
    
    normalized = []
    for item in data:
        new_item = item.copy()
        new_stats = {}
        
        for lang, stats in item.get('language_stats', {}).items():
            new_stats[lang] = stats.copy()
            if stats.get('mean') is not None:
                norm_val = (stats['mean'] - data_min) / (data_max - data_min)
                new_stats[lang]['mean'] = min_val + norm_val * (max_val - min_val)
                
        new_item['language_stats'] = new_stats
        normalized.append(new_item)
        
    return normalized

def aggregate_by_language(data: List[Dict]) -> Dict[str, Dict]:
    """
    Aggregates statistics by language.
    
    Args:
        data: List of survey question dictionaries
        
    Returns:
        Dict[str, Dict]: Aggregated statistics per language
    """
    aggregates = {}
    
    for item in data:
        for lang, stats in item.get('language_stats', {}).items():
            if lang not in aggregates:
                aggregates[lang] = {
                    'total_responses': 0,
                    'questions_answered': 0,
                    'mean_responses_per_question': 0
                }
            
            if stats.get('n') is not None:
                aggregates[lang]['total_responses'] += stats['n']
                aggregates[lang]['questions_answered'] += 1
    
    # Calculate averages
    for lang_stats in aggregates.values():
        if lang_stats['questions_answered'] > 0:
            lang_stats['mean_responses_per_question'] = (
                lang_stats['total_responses'] / lang_stats['questions_answered']
            )
            
    return aggregates 