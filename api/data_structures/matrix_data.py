"""
Matrix data structure for handling survey response data from multiple sources.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any

class MatrixData:
    def __init__(self):
        self.questions: List[Dict[str, str]] = []  # List of {id: str, title: str}
        self.languages: List[str] = []
        self.values: Dict[str, Dict[str, float]] = {}  # {lang: {q_id: value}}
        self.metadata: Dict[str, Dict[str, Any]] = {}  # {q_id: {scale_min, scale_max, etc}}
        self.sources: Dict[str, Dict[str, str]] = {}  # {lang: {q_id: source_file}}
        
    def add_question(self, q_id: str, title: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add a question to the matrix.
        
        Args:
            q_id: Question identifier
            title: Question title/description
            metadata: Optional metadata like scale_min, scale_max, etc.
        """
        if not any(q['id'] == q_id for q in self.questions):
            self.questions.append({'id': q_id, 'title': title})
            if metadata:
                self.metadata[q_id] = metadata
                
    def add_language(self, lang: str) -> None:
        """Add a language to the matrix.
        
        Args:
            lang: Language identifier
        """
        if lang not in self.languages:
            self.languages.append(lang)
            self.values[lang] = {}
            self.sources[lang] = {}
            
    def set_value(self, lang: str, q_id: str, value: float, source_file: str) -> None:
        """Set a value in the matrix.
        
        Args:
            lang: Language identifier
            q_id: Question identifier
            value: Response value
            source_file: Source result file
        """
        # Ensure language and question exist
        if lang not in self.languages:
            self.add_language(lang)
        if not any(q['id'] == q_id for q in self.questions):
            raise ValueError(f"Question {q_id} not found. Add it first with add_question()")
            
        # Validate value range if metadata exists
        if q_id in self.metadata:
            scale_min = self.metadata[q_id].get('scale_min')
            scale_max = self.metadata[q_id].get('scale_max')
            if scale_min is not None and scale_max is not None:
                if not (scale_min <= value <= scale_max):
                    raise ValueError(f"Value {value} out of range [{scale_min}, {scale_max}] for question {q_id}")
        
        self.values[lang][q_id] = float(value)
        self.sources[lang][q_id] = source_file
        
    def merge(self, other: 'MatrixData') -> 'MatrixData':
        """Merge another MatrixData object into this one.
        
        Args:
            other: Another MatrixData object
            
        Returns:
            New merged MatrixData object
        """
        merged = MatrixData()
        
        # Merge questions and metadata
        for q in self.questions + other.questions:
            q_id = q['id']
            if not any(existing['id'] == q_id for existing in merged.questions):
                merged.add_question(q_id, q['title'])
                if q_id in self.metadata:
                    merged.metadata[q_id] = self.metadata[q_id]
                elif q_id in other.metadata:
                    merged.metadata[q_id] = other.metadata[q_id]
                    
        # Merge languages and values
        for lang in set(self.languages + other.languages):
            merged.add_language(lang)
            
            # Copy values from both sources
            if lang in self.values:
                for q_id, value in self.values[lang].items():
                    merged.set_value(lang, q_id, value, self.sources[lang][q_id])
            if lang in other.values:
                for q_id, value in other.values[lang].items():
                    if lang not in self.values or q_id not in self.values[lang]:
                        merged.set_value(lang, q_id, value, other.sources[lang][q_id])
                        
        return merged
        
    def get_matrix(self) -> Tuple[List[str], List[str], np.ndarray]:
        """Get the matrix representation of the data.
        
        Returns:
            Tuple of (question_ids, languages, values_array)
        """
        # Create ordered lists of questions and languages
        q_ids = [q['id'] for q in self.questions]
        
        # Create the matrix
        matrix = np.full((len(self.languages), len(q_ids)), np.nan)  # Initialize with NaN
        
        # Fill the matrix
        for i, lang in enumerate(self.languages):
            for j, q_id in enumerate(q_ids):
                value = self.values[lang].get(q_id)
                if value is not None:
                    try:
                        matrix[i, j] = float(value)
                    except (ValueError, TypeError) as e:
                        print(f"WARNING: Could not convert value for {lang}, {q_id}: {value} (type: {type(value)})")
                        matrix[i, j] = np.nan
                else:
                    matrix[i, j] = np.nan
        
        # Replace any remaining NaN values with 0.0 for visualization
        matrix = np.nan_to_num(matrix, nan=0.0)
                
        return q_ids, self.languages, matrix
        
    def validate(self) -> bool:
        """Validate the data structure.
        
        Returns:
            True if valid, raises ValueError otherwise
        """
        # Check questions exist
        if not self.questions:
            raise ValueError("No questions defined")
            
        # Check languages exist
        if not self.languages:
            raise ValueError("No languages defined")
            
        # Check all languages have values
        for lang in self.languages:
            if lang not in self.values:
                raise ValueError(f"No values for language {lang}")
                
        # Check all values have sources
        for lang in self.languages:
            if lang not in self.sources:
                raise ValueError(f"No sources for language {lang}")
            if set(self.values[lang].keys()) != set(self.sources[lang].keys()):
                raise ValueError(f"Mismatch between values and sources for language {lang}")
                
        # Check value ranges
        for lang in self.languages:
            for q_id, value in self.values[lang].items():
                if q_id in self.metadata:
                    scale_min = self.metadata[q_id].get('scale_min')
                    scale_max = self.metadata[q_id].get('scale_max')
                    if scale_min is not None and scale_max is not None:
                        if not (scale_min <= value <= scale_max):
                            raise ValueError(f"Value {value} out of range [{scale_min}, {scale_max}] for question {q_id} in language {lang}")
                            
        return True
        
    def __str__(self) -> str:
        """String representation for debugging."""
        return f"MatrixData with {len(self.questions)} questions and {len(self.languages)} languages"
        
    def debug_info(self) -> str:
        """Detailed debug information."""
        info = [
            "=== MatrixData Debug Info ===",
            f"Questions: {len(self.questions)}",
            f"Languages: {len(self.languages)}",
            "\nQuestion IDs:",
            *[f"  {q['id']}: {q['title'][:30]}..." for q in self.questions],
            "\nLanguages:",
            *[f"  {lang}: {len(self.values[lang])} values" for lang in self.languages],
            "\nSample Values:",
            *[f"  {lang} - {list(self.values[lang].items())[:3]}" for lang in self.languages],
            "\nSources:",
            *[f"  {lang} - {set(self.sources[lang].values())}" for lang in self.languages]
        ]
        return "\n".join(info) 