"""
Shared utilities for data processing and visualization.
"""

from typing import Dict, List, Optional
import numpy as np

def consolidate_question_data(data: List[Dict]) -> Dict[str, Dict]:
    """Consolidate question data from multiple result files.
    
    Args:
        data: List of question dictionaries from multiple result files
        
    Returns:
        Dictionary mapping question IDs to consolidated question data
    """
    consolidated = {}
    
    for q in data:
        qid = q.get('question_id')
        if not qid:
            continue
            
        if qid not in consolidated:
            # First time seeing this question, initialize with current data
            consolidated[qid] = q.copy()
        else:
            # Update existing question data
            existing = consolidated[qid]
            
            # Update basic question info if needed
            for key in ['title', 'category', 'scale_min', 'scale_max', 'scale_labels', 'prompt_text']:
                if key not in existing or not existing[key]:
                    existing[key] = q.get(key)
            
            # Update language stats
            for lang, stats in q.get('language_stats', {}).items():
                if lang not in existing['language_stats']:
                    # New language, add its stats
                    existing['language_stats'][lang] = stats.copy()
                else:
                    # Update existing language stats
                    existing_stats = existing['language_stats'][lang]
                    new_stats = stats
                    
                    # Update count and mean
                    total_count = existing_stats.get('count', 0) + new_stats.get('count', 0)
                    if total_count > 0:
                        # Weighted average of means
                        existing_mean = existing_stats.get('mean', 0)
                        new_mean = new_stats.get('mean', 0)
                        existing_count = existing_stats.get('count', 0)
                        new_count = new_stats.get('count', 0)
                        
                        existing_stats['mean'] = (
                            (existing_mean * existing_count + new_mean * new_count) / total_count
                        )
                        
                        # Take the larger std dev as a conservative estimate
                        existing_stats['std'] = max(
                            existing_stats.get('std', 0),
                            new_stats.get('std', 0)
                        )
                        
                        # Update count
                        existing_stats['count'] = total_count
    
    return consolidated 