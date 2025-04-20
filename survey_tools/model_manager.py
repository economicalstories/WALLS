import os
import requests
from typing import List, Dict
import json

def fetch_available_models() -> List[Dict]:
    """
    Fetch available models from OpenAI API.
    Returns a list of model information dictionaries.
    """
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    try:
        response = requests.get(
            "https://api.openai.com/v1/models",
            headers=headers
        )
        response.raise_for_status()
        models = response.json()['data']
        
        # Filter for GPT models and sort by created date
        gpt_models = [
            model for model in models 
            if any(prefix in model['id'].lower() 
                  for prefix in ['gpt-4', 'gpt-3.5'])
        ]
        gpt_models.sort(key=lambda x: x['created'], reverse=True)
        
        return gpt_models
    except requests.exceptions.RequestException as e:
        print(f"Error fetching models: {e}")
        return []

def select_model_interactive() -> str:
    """
    Present an interactive menu to select a model.
    Returns the selected model ID.
    """
    models = fetch_available_models()
    
    if not models:
        raise ValueError("No models available. Please check your API key and connection.")
    
    print("\nAvailable Models:")
    print("-" * 50)
    for idx, model in enumerate(models, 1):
        created_date = model.get('created', 'N/A')
        print(f"{idx}. {model['id']}")
        print(f"   Created: {created_date}")
        print(f"   Owner: {model.get('owned_by', 'N/A')}")
        print()
    
    while True:
        try:
            choice = input("\nSelect a model (enter number): ")
            idx = int(choice) - 1
            if 0 <= idx < len(models):
                return models[idx]['id']
            print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

def get_model_id(specified_model: str = None) -> str:
    """
    Get model ID either from specified value or interactive selection.
    Args:
        specified_model: Optional model ID specified via command line
    Returns:
        Selected model ID
    """
    if specified_model:
        return specified_model
    
    try:
        return select_model_interactive()
    except Exception as e:
        print(f"Error selecting model: {e}")
        print("Please specify a model ID directly or check your API key.")
        raise 