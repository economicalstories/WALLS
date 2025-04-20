from typing import Dict
import numpy as np
from api.data_structures.matrix_data import MatrixData

class MatrixProcessor:
    def process_matrix(self, matrix_data: MatrixData) -> Dict:
        """Process matrix data into a format suitable for plotting."""
        print("DEBUG: Starting matrix processing")
        
        # Get matrix representation
        q_ids, languages, values = matrix_data.get_matrix()
        print(f"DEBUG: Matrix shape: {values.shape}")
        print(f"DEBUG: Languages: {languages}")
        print(f"DEBUG: Value ranges - Min: {np.min(values)}, Max: {np.max(values)}")
        print(f"DEBUG: Non-zero values count: {np.count_nonzero(values)}")
        
        # Add detailed debugging for Hebrew data
        if 'he' in languages or 'heb' in languages:
            hebrew_idx = languages.index('he' if 'he' in languages else 'heb')
            print(f"\nDEBUG: Hebrew Data Analysis:")
            print(f"Hebrew index in matrix: {hebrew_idx}")
            hebrew_values = values[hebrew_idx]
            print(f"Hebrew values: {hebrew_values}")
            print(f"Hebrew values type: {hebrew_values.dtype}")
            print(f"Hebrew non-zero count: {np.count_nonzero(hebrew_values)}")
            print(f"Hebrew value range: [{np.min(hebrew_values)}, {np.max(hebrew_values)}]")
            
            # Check for any potential data anomalies
            print(f"Hebrew NaN values: {np.isnan(hebrew_values).sum()}")
            print(f"Hebrew infinite values: {np.isinf(hebrew_values).sum()}")
            
            # Compare with other languages
            other_langs_values = values[np.arange(len(languages)) != hebrew_idx]
            print(f"\nDEBUG: Other Languages Stats:")
            print(f"Other languages value range: [{np.min(other_langs_values)}, {np.max(other_langs_values)}]")
            print(f"Other languages mean: {np.mean(other_langs_values)}")
            print(f"Hebrew values mean: {np.mean(hebrew_values)}")
        
        # Create the heatmap data
        heatmap_data = {
            'z': values.tolist(),
            'x': q_ids,
            'y': languages,
            'type': 'heatmap',
            'colorscale': 'Viridis'
        }
        
        print("\nDEBUG: Final heatmap data structure:")
        print(f"z shape: {np.array(heatmap_data['z']).shape}")
        print(f"x length: {len(heatmap_data['x'])}")
        print(f"y length: {len(heatmap_data['y'])}")
        
        print("DEBUG: Finished processing matrix")
        return heatmap_data 