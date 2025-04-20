"""
Utility functions for statistical calculations and data processing.
"""

import numpy as np
import pandas as pd
import math

def get_language_summary(result_data):
    """Get language summary for a result set"""
    if not result_data:
        return "No languages"
    languages = set()
    for q in result_data:
        languages.update(q.get('language_stats', {}).keys())
    if len(languages) == 1:
        return next(iter(languages))
    return f"{len(languages)} languages"

def get_all_languages(data):
    """Get list of all languages"""
    languages = set()
    for q in data:
        languages.update(q['language_stats'].keys())
    return sorted(list(languages), reverse=True)

def get_filtered_languages(data):
    """Get list of languages after filtering out those with NaN values"""
    valid_languages = {'English'}  # Always include English
    all_languages = get_all_languages(data)
    for lang in all_languages:
        if lang == 'English':
            continue
        # Check if language has any NaN values across all questions
        has_missing_data = False
        for q in data:
            if lang not in q['language_stats'] or q['language_stats'][lang]['mean'] is None:
                has_missing_data = True
                break
        if not has_missing_data:
            valid_languages.add(lang)
    return sorted(list(valid_languages))

def calculate_summary_stats(matrix_data):
    """Calculate summary statistics for each column"""
    summary_stats = []
    
    # Calculate mean for each column
    means = []
    for col in zip(*matrix_data):
        valid_values = [x for x in col if x is not None]
        mean = sum(valid_values) / len(valid_values) if valid_values else None
        means.append(mean)
    summary_stats.append(means)
    
    # Calculate standard deviation for each column
    stds = []
    for col in zip(*matrix_data):
        valid_values = [x for x in col if x is not None]
        if valid_values:
            mean = sum(valid_values) / len(valid_values)
            variance = sum((x - mean) ** 2 for x in valid_values) / len(valid_values)
            std = math.sqrt(variance)
            stds.append(std)
        else:
            stds.append(None)
    summary_stats.append(stds)
    
    # Calculate mode for each column
    modes = []
    for col in zip(*matrix_data):
        valid_values = [x for x in col if x is not None]
        if valid_values:
            # Count occurrences of each value
            value_counts = {}
            for value in valid_values:
                value_counts[value] = value_counts.get(value, 0) + 1
            # Find the most common value
            mode = max(value_counts.items(), key=lambda x: x[1])[0]
            modes.append(mode)
        else:
            modes.append(None)
    summary_stats.append(modes)
    
    return summary_stats

def get_scale_labels(question):
    """Convert scale labels from any format to a list of labels."""
    scale_labels = question['scale_labels']
    if isinstance(scale_labels, dict):
        # If it's a min/max format
        if 'min' in scale_labels and 'max' in scale_labels:
            num_points = question['scale_max'] - question['scale_min'] + 1
            if num_points == 2:
                return [scale_labels['min'], scale_labels['max']]
            # For scales > 2 points, create intermediate labels
            labels = [scale_labels['min']]
            for i in range(num_points - 2):
                labels.append(f"Level {i + 2}")
            labels.append(scale_labels['max'])
            return labels
        # If it's a numbered format (e.g., "1": "Very good", "4": "Very bad")
        else:
            labels = [""] * (question['scale_max'] - question['scale_min'] + 1)
            for i in range(question['scale_min'], question['scale_max'] + 1):
                if str(i) in scale_labels:
                    labels[i - question['scale_min']] = scale_labels[str(i)]
                else:
                    labels[i - question['scale_min']] = f"Level {i}"
            return labels
    return [str(i) for i in range(question['scale_min'], question['scale_max'] + 1)]

def calculate_normalized_deviation(raw_mean, q_mean, scale_min, scale_max):
    """Calculate normalized deviation from mean relative to scale range."""
    if np.isnan(raw_mean) or np.isnan(q_mean):
        return np.nan
        
    # Calculate deviation relative to scale range
    # This will give us a value between -1 and 1
    max_possible_dev = max(abs(scale_max - q_mean), abs(scale_min - q_mean))
    if max_possible_dev == 0:
        return 0
    return (raw_mean - q_mean) / max_possible_dev 