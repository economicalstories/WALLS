"""
Functions for processing survey data and calculating statistics.
"""

from typing import Dict, List, Optional, Tuple
import numpy as np

def calculate_language_stats(data: List, selected_languages: List[str]) -> Dict:
    """Calculate statistics for each language."""
    stats = {}
    for lang in selected_languages:
        stats[lang] = {
            'means': [],
            'stds': [],
            'ns': []
        }
        for q in data:
            lang_stats = q.get('language_stats', {}).get(lang, {})
            stats[lang]['means'].append(lang_stats.get('mean'))
            stats[lang]['stds'].append(lang_stats.get('std'))
            stats[lang]['ns'].append(lang_stats.get('n', 0))
    return stats

def calculate_question_stats(data: List, question_id: str) -> Dict:
    """Calculate statistics for a specific question."""
    for q in data:
        if q.get('question_id') == question_id:
            return {
                'title': q.get('title', 'Unknown'),
                'stats': q.get('language_stats', {})
            }
    return {'title': 'Unknown', 'stats': {}}

def calculate_deviations(data: List, selected_languages: List[str]) -> Dict[str, float]:
    """Calculate mean absolute deviations for each language."""
    deviations = {}
    for lang in selected_languages:
        total_dev = 0
        count = 0
        for q in data:
            stats = q.get('language_stats', {}).get(lang, {})
            mean = stats.get('mean')
            if mean is not None:
                # Calculate deviation from overall question mean
                q_means = [
                    s.get('mean', 0) 
                    for l, s in q.get('language_stats', {}).items() 
                    if s.get('mean') is not None
                ]
                if q_means:
                    q_mean = sum(q_means) / len(q_means)
                    total_dev += abs(mean - q_mean)
                    count += 1
        
        if count > 0:
            deviations[lang] = total_dev / count
    return deviations

def prepare_hover_text(title: str, mean: Optional[float], std: Optional[float], n: int) -> str:
    """Prepare hover text with safe formatting."""
    mean_text = f"{mean:.2f}" if mean is not None else "N/A"
    std_text = f"{std:.2f}" if std is not None else "N/A"
    
    return (
        f"Question: {title}<br>"
        f"Mean: {mean_text}<br>"
        f"Std Dev: {std_text}<br>"
        f"n: {n}"
    )

def prepare_matrix_data(data: List, selected_languages: List[str]) -> Tuple[List, List, List, List]:
    """Prepare data for matrix visualization."""
    x_data = []  # Questions
    y_data = selected_languages
    z_data = []  # Values
    hover_text = []  # Custom hover text
    
    for lang in selected_languages:
        row_values = []
        row_text = []
        for q in data:
            if len(x_data) < len(data):
                x_data.append(f"{q.get('question_id', 'Unknown')}: {q.get('title', 'Unknown')[:30]}...")
            
            stats = q.get('language_stats', {}).get(lang, {})
            mean = stats.get('mean')
            std = stats.get('std')
            n = stats.get('n', 0)
            
            row_values.append(mean if mean is not None else None)
            row_text.append(prepare_hover_text(q.get('title', 'Unknown'), mean, std, n))
        
        z_data.append(row_values)
        hover_text.append(row_text)
    
    return x_data, y_data, z_data, hover_text 