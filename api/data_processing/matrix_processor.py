"""
Functions for processing survey data into MatrixData format.
"""

from typing import Dict, List, Any, Tuple, Optional
import json
import os

from api.data_structures.matrix_data import MatrixData

def process_result_file(data: List[Dict[str, Any]], source_file: str) -> MatrixData:
    """Process a single result file into MatrixData format.
    
    Args:
        data: List of question data from result file
        source_file: Name/path of source file for tracking
        
    Returns:
        MatrixData object containing the processed data
    """
    matrix = MatrixData()
    
    # First pass - collect all questions and metadata
    for question in data:
        q_id = question.get('question_id')
        title = question.get('title', '')
        if not q_id:
            continue
            
        # Get metadata
        metadata = {
            'scale_min': question.get('scale_min'),
            'scale_max': question.get('scale_max'),
            'scale_labels': question.get('scale_labels', {}),
            'category': question.get('category', '')
        }
        
        matrix.add_question(q_id, title, metadata)
        
        # Process language stats
        lang_stats = question.get('language_stats', {})
        for lang, stats in lang_stats.items():
            if not isinstance(stats, dict):
                continue
                
            mean = stats.get('mean')
            if mean is not None:
                if lang not in matrix.languages:
                    matrix.add_language(lang)
                matrix.set_value(lang, q_id, float(mean), source_file)
                
    return matrix

def load_and_process_file(file_path: str) -> Tuple[Optional[MatrixData], Optional[str]]:
    """Load and process a result file.
    
    Args:
        file_path: Path to the result file
        
    Returns:
        Tuple of (MatrixData or None, error message or None)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        if not isinstance(data, dict) or 'results' not in data:
            return None, "Invalid data format - missing 'results' key"
            
        results = data['results']
        if not isinstance(results, list):
            return None, "Invalid results format - expected list"
            
        matrix = process_result_file(results, os.path.basename(file_path))
        return matrix, None
        
    except Exception as e:
        return None, f"Error processing file: {str(e)}"

def merge_result_files(file_paths: List[str]) -> Tuple[Optional[MatrixData], Optional[str]]:
    """Load and merge multiple result files.
    
    Args:
        file_paths: List of paths to result files
        
    Returns:
        Tuple of (merged MatrixData or None, error message or None)
    """
    if not file_paths:
        return None, "No files provided"
        
    merged_matrix = None
    errors = []
    
    for file_path in file_paths:
        matrix, error = load_and_process_file(file_path)
        if error:
            errors.append(f"{file_path}: {error}")
            continue
            
        if matrix is None:
            continue
            
        if merged_matrix is None:
            merged_matrix = matrix
        else:
            merged_matrix = merged_matrix.merge(matrix)
            
    if errors:
        error_msg = "Errors processing files:\n" + "\n".join(errors)
        if merged_matrix is None:
            return None, error_msg
        # If we have some data, return it with warnings
        print(f"Warning: {error_msg}")
        
    return merged_matrix, None

def debug_matrix_data(matrix: MatrixData) -> str:
    """Generate debug information about the matrix data.
    
    Args:
        matrix: MatrixData object to debug
        
    Returns:
        Debug information string
    """
    info = [
        "=== Matrix Data Debug Info ===",
        matrix.debug_info(),
        "\nValue Ranges:",
    ]
    
    # Add value range info per question
    for q in matrix.questions:
        q_id = q['id']
        values = []
        for lang in matrix.languages:
            if q_id in matrix.values[lang]:
                values.append(matrix.values[lang][q_id])
        if values:
            min_val = min(values)
            max_val = max(values)
            info.append(f"  {q_id}: range [{min_val:.1f}, {max_val:.1f}], {len(values)} values")
            
    # Add source file info
    sources = set()
    for lang in matrix.languages:
        sources.update(matrix.sources[lang].values())
    info.append("\nSource Files:")
    for source in sorted(sources):
        info.append(f"  {source}")
        
    return "\n".join(info) 