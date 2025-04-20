# -*- coding: utf-8 -*-
"""
Global state management for the dashboard application.

This module handles:
- Global state initialization and management
- State validation
- Error handling utilities
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from pathlib import Path
import json


@dataclass
class ModelInfo:
    """Model information container."""
    name: str
    call_count: int
    avg_tokens: float


@dataclass
class AppState:
    """Application state container."""
    selected_survey: Optional[str] = None
    selected_model: Optional[str] = None
    selected_languages: List[str] = field(default_factory=list)
    selected_question: Optional[str] = None
    error_message: Optional[str] = None
    model_info: Optional[ModelInfo] = None


class StateManager:
    """Manages global application state and validation."""
    
    def __init__(self):
        """Initialize state manager."""
        self.state = AppState()
        self._data_dir = Path('data')
    
    def update_state(self, **kwargs) -> None:
        """Update state with provided values.
        
        Args:
            **kwargs: Key-value pairs to update in state
        """
        for key, value in kwargs.items():
            if hasattr(self.state, key):
                setattr(self.state, key, value)
            else:
                self.set_error(f"Invalid state key: {key}")
    
    def set_error(self, message: str) -> None:
        """Set error message in state.
        
        Args:
            message: Error message to store
        """
        self.state.error_message = message
        print(f"Error: {message}")  # For debugging
    
    def clear_error(self) -> None:
        """Clear error message from state."""
        self.state.error_message = None
    
    def get_error(self) -> Optional[str]:
        """Get current error message.
        
        Returns:
            Current error message or None
        """
        return self.state.error_message
    
    def validate_survey_id(self, survey_id: str) -> bool:
        """Validate survey ID exists.
        
        Args:
            survey_id: Survey ID to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not survey_id:
            self.set_error("Survey ID is required")
            return False
            
        survey_dir = self._data_dir / survey_id
        if not survey_dir.exists():
            self.set_error(f"Survey directory not found: {survey_id}")
            return False
            
        return True
    
    def validate_model_id(self, survey_id: str, model_id: str) -> bool:
        """Validate model ID exists for survey.
        
        Args:
            survey_id: Survey ID to check
            model_id: Model ID to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not all([survey_id, model_id]):
            self.set_error("Survey ID and Model ID are required")
            return False
            
        model_dir = self._data_dir / survey_id / model_id
        if not model_dir.exists():
            self.set_error(f"Model directory not found: {model_id}")
            return False
            
        return True
    
    def validate_languages(self, languages: List[str], available_languages: List[str]) -> List[str]:
        """Validate and filter language codes.
        
        Args:
            languages: List of language codes to validate
            available_languages: List of valid language codes
            
        Returns:
            List of valid language codes
        """
        if not languages:
            self.set_error("No languages provided")
            return []
            
        valid_languages = [lang for lang in languages if lang in available_languages]
        
        if not valid_languages:
            self.set_error("No valid languages found")
            return []
            
        return valid_languages
    
    def load_survey_metadata(self, survey_id: str) -> Optional[Dict]:
        """Load survey metadata.
        
        Args:
            survey_id: Survey ID to load metadata for
            
        Returns:
            Survey metadata dictionary or None if error
        """
        if not self.validate_survey_id(survey_id):
            return None
            
        try:
            metadata_path = self._data_dir / survey_id / 'metadata.json'
            with open(metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.set_error(f"Error loading survey metadata: {e}")
            return None
    
    def load_model_data(self, survey_id: str, model_id: str) -> Optional[List[Dict]]:
        """Load model response data.
        
        Args:
            survey_id: Survey ID to load data for
            model_id: Model ID to load data for
            
        Returns:
            List of response dictionaries or None if error
        """
        if not self.validate_model_id(survey_id, model_id):
            return None
            
        try:
            data_dir = self._data_dir / survey_id / model_id
            result_files = list(data_dir.glob('results_*.json'))
            
            if not result_files:
                self.set_error(f"No results files found in {data_dir}")
                return None
                
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
                self.set_error("No valid data found in results files")
                return None
                
            return all_data
            
        except Exception as e:
            self.set_error(f"Error loading model data: {e}")
            return None
    
    def update_model_info(self, data: List[Dict]) -> None:
        """Update model info from response data.
        
        Args:
            data: List of response dictionaries
        """
        if not data:
            return
            
        total_calls = sum(q.get('model_stats', {}).get('total_calls', 0) for q in data)
        total_tokens = sum(q.get('model_stats', {}).get('total_tokens', 0) for q in data)
        total_responses = sum(q.get('model_stats', {}).get('total_responses', 0) for q in data)
        
        self.state.model_info = ModelInfo(
            name=self.state.selected_model or "Unknown",
            call_count=total_calls,
            avg_tokens=total_tokens / total_responses if total_responses > 0 else 0
        )


# Global state instance
_state_manager = None


def init_state() -> None:
    """Initialize global state manager."""
    global _state_manager
    _state_manager = StateManager()


def get_state() -> StateManager:
    """Get global state manager instance.
    
    Returns:
        Global StateManager instance
    """
    if _state_manager is None:
        init_state()
    return _state_manager
