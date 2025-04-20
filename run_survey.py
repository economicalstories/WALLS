#!/usr/bin/env python3
"""
WALLS Survey Runner
Main entry point for running surveys and processing results.
"""

import os
import json
import argparse
from datetime import datetime
import sys
from survey_tools.survey_runner import run_survey
from survey_tools.result_processor import process_results
import config
import openai
import glob

def get_available_surveys():
    """Get list of available surveys."""
    surveys = []
    survey_dir = "data"
    if os.path.exists(survey_dir):
        for item in os.listdir(survey_dir):
            if os.path.isdir(os.path.join(survey_dir, item)):
                if os.path.exists(os.path.join(survey_dir, item, "questions.json")):
                    surveys.append(item)
    return sorted(surveys)

def select_survey():
    """Interactive menu to select a survey."""
    surveys = get_available_surveys()
    if not surveys:
        print("Error: No surveys found in data directory")
        sys.exit(1)
    
    print("\nAvailable surveys:")
    for i, survey in enumerate(surveys, 1):
        print(f"{i}. {survey}")
    
    while True:
        try:
            choice = input("\nSelect survey number: ").strip()
            if not choice:  # Empty input
                return None
            idx = int(choice) - 1
            if 0 <= idx < len(surveys):
                return surveys[idx]
            print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

def select_languages(default_languages):
    """Interactive menu to select languages."""
    print("\nEnter languages (comma-separated, press Enter for defaults):")
    print(f"Default languages: {', '.join(default_languages)}")
    languages_input = input("Languages: ").strip()
    if not languages_input:
        return default_languages
    return [lang.strip() for lang in languages_input.split(",")]

def select_trials(recommended_trials):
    """Interactive menu to select number of trials."""
    print(f"\nEnter number of trials (press Enter for recommended: {recommended_trials}):")
    while True:
        trials_input = input("Trials: ").strip()
        if not trials_input:
            return recommended_trials
        try:
            trials = int(trials_input)
            if trials > 0:
                return trials
            print("Please enter a positive number.")
        except ValueError:
            print("Please enter a valid number.")

def load_survey_data(survey_id):
    """Load survey questions and configuration."""
    questions_file = os.path.join("data", survey_id, "questions.json")
    if not os.path.exists(questions_file):
        raise FileNotFoundError(f"Survey questions not found: {questions_file}")
    
    with open(questions_file, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
        return json_data["questions"], json_data["survey"]["metadata"]

def find_latest_results(survey_id):
    """Find the most recent results file for a given survey."""
    data_dir = f"data/{survey_id}/data"
    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"No data directory found for survey {survey_id}")
    
    # Look for CSV files with results prefix
    result_files = [f for f in os.listdir(data_dir) if f.startswith("results_") and f.endswith(".csv")]
    if not result_files:
        raise FileNotFoundError(f"No result files found for survey {survey_id}")
    
    # Sort by timestamp in filename
    latest_file = sorted(result_files)[-1]
    return os.path.join(data_dir, latest_file)

def confirm_survey_run(survey_id, languages, trials, questions):
    """Display survey details and get user confirmation."""
    num_questions = len(questions)
    non_english = len([lang for lang in languages if lang.lower() != 'english'])
    
    # API call calculations
    survey_calls = len(languages) * num_questions * trials
    forward_translation_calls = non_english * num_questions  # One per non-English question
    back_translation_calls = non_english * num_questions    # One per non-English question
    verification_calls = non_english * num_questions        # One per non-English question
    total_api_calls = survey_calls + forward_translation_calls + back_translation_calls + verification_calls
    
    print("\nSurvey Configuration:")
    print("=" * 50)
    print(f"Survey ID: {survey_id}")
    print(f"Languages: {', '.join(languages)}")
    print(f"Trials per question: {trials}")
    if trials < 10:
        print("⚠️  WARNING: For research purposes, 10 or more trials per question are recommended")
        print("             to ensure statistical significance of the results.")
    print(f"Number of questions: {num_questions}")
    print(f"Model: {config.MODEL_NAME or 'gpt-4'} (from config)")
    
    print("\nQuestions to be processed:")
    print("-" * 50)
    for i, q in enumerate(questions, 1):
        print(f"{i}. [{q['question_id']}] {q.get('question_title', 'Untitled')}")
        print(f"   Prompt: {q['prompt_text']}")
        print(f"   Scale: {q['scale_min']} to {q['scale_max']}")
        if i < len(questions):  # Don't print separator after last question
            print("-" * 25)
    
    print("\nEstimated API Calls:")
    print("-" * 50)
    print(f"Survey responses: {survey_calls} ({trials} trials × {num_questions} questions × {len(languages)} languages)")
    if non_english > 0:
        print(f"Forward translations: {forward_translation_calls} (1 call × {num_questions} questions × {non_english} non-English)")
        print(f"Back translations: {back_translation_calls} (1 call × {num_questions} questions × {non_english} non-English)")
        print(f"Translation verification: {verification_calls} (1 call × {num_questions} questions × {non_english} non-English)")
        print(f"Total API calls: {total_api_calls}")
        print(f"\nNote: All API calls will use the OpenAI {config.MODEL_NAME or 'gpt-4'} model")
    
    while True:
        response = input("\nProceed with survey? (yes/no): ").lower().strip()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        print("Please answer 'yes' or 'no'")

def get_available_models():
    """Get list of available GPT models from OpenAI API."""
    try:
        # Using the new OpenAI API format
        response = client.models.list()
        
        # Filter for relevant GPT models and their variants
        gpt_models = []
        for model in response.data:
            model_id = model.id
            # Include main models and their variants
            if any(prefix in model_id for prefix in [
                'gpt-4-turbo',  # Latest GPT-4 Turbo
                'gpt-4-0125',   # GPT-4 Turbo Preview
                'gpt-4-1106',   # Previous GPT-4 Turbo
                'gpt-4-vision', # GPT-4 Vision
                'gpt-4-32k',    # GPT-4 32k context
                'gpt-4',        # Base GPT-4
                'gpt-3.5-turbo',# Latest GPT-3.5 Turbo
                'gpt-3.5-turbo-16k', # GPT-3.5 Turbo 16k
                'gpt-3.5-turbo-1106', # Specific GPT-3.5 version
                'gpt-3.5-turbo-0125'  # Latest GPT-3.5 version
            ]):
                gpt_models.append(model_id)
        
        return sorted(gpt_models, key=lambda x: (
            # Sort by model family and capability
            '4-turbo' in x,  # GPT-4 Turbo first
            '4-0125' in x,   # Then GPT-4 latest
            '4' in x,        # Then other GPT-4
            '3.5' in x,      # Then GPT-3.5
            x  # Then alphabetically
        ), reverse=True)
    except Exception as e:
        print(f"\nWarning: Could not fetch models from OpenAI API: {e}")
        print("Using default model list instead.\n")
        # Return comprehensive default list if API call fails
        return [
            'gpt-4-turbo-preview',
            'gpt-4-0125-preview',
            'gpt-4-1106-preview',
            'gpt-4',
            'gpt-4-32k',
            'gpt-3.5-turbo',
            'gpt-3.5-turbo-16k',
            'gpt-3.5-turbo-1106',
            'gpt-3.5-turbo-0125'
        ]

def select_model(current_model=None):
    """Interactive menu to select an OpenAI model."""
    models = get_available_models()
    
    print("\nAvailable models:")
    print("Note: Newer models generally have better performance and lower costs.")
    print("      Models with larger context windows (16k, 32k) are available for longer inputs.\n")
    
    for i, model in enumerate(models, 1):
        marker = '*' if model == current_model else ' '
        description = ""
        if "4-turbo" in model:
            description = "(Latest & Most Capable)"
        elif "4-0125" in model:
            description = "(Latest GPT-4)"
        elif "4-32k" in model:
            description = "(32k context)"
        elif "3.5-turbo-16k" in model:
            description = "(16k context)"
        elif "3.5-turbo" in model:
            description = "(Fast & Cost-effective)"
        
        print(f"{i}. [{marker}] {model:<30} {description}")
    
    if current_model:
        print(f"\nCurrent model: {current_model}")
        print("Press Enter to keep current model, or select a number to change.")
    
    while True:
        try:
            choice = input("\nSelect model number: ").strip()
            if not choice and current_model:  # Empty input with current model
                return current_model
            if not choice:  # Empty input without current model
                return models[0]  # Default to first model
            idx = int(choice) - 1
            if 0 <= idx < len(models):
                return models[idx]
            print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

def find_data_files(survey_id, model_dir=None):
    """Find all data files for a given survey and model directory."""
    base_dir = os.path.join("data", survey_id)
    if model_dir:
        data_dir = os.path.join(base_dir, model_dir)
    else:
        # Look for any data_* directory
        data_dirs = [d for d in os.listdir(base_dir) 
                    if os.path.isdir(os.path.join(base_dir, d)) and d.startswith('data_')]
        if not data_dirs:
            raise FileNotFoundError(f"No data directories found for survey {survey_id}")
        data_dir = os.path.join(base_dir, data_dirs[0])
    
    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"Data directory not found: {data_dir}")
    
    # Look for CSV files with data prefix, excluding tmp directory
    data_files = []
    for f in os.listdir(data_dir):
        if f.startswith("data_") and f.endswith(".csv"):
            full_path = os.path.join(data_dir, f)
            if "tmp" not in os.path.normpath(full_path).split(os.sep):
                data_files.append(full_path)
    
    if not data_files:
        raise FileNotFoundError(f"No data files found in {data_dir}")
    
    # Sort files by name for consistent ordering
    return sorted(data_files)

def find_all_data_files(survey_id):
    """Find all data files across all model directories."""
    survey_dir = f"data/{survey_id}"
    all_files = []
    
    # Look for model directories (data_*)
    for item in os.listdir(survey_dir):
        if item.startswith('data_') and os.path.isdir(os.path.join(survey_dir, item)):
            model_dir = os.path.join(survey_dir, item)
            # Find CSV files in this model directory
            csv_files = glob.glob(os.path.join(model_dir, "data_*.csv"))
            for file in csv_files:
                all_files.append({
                    'path': file,
                    'model': item[5:],  # Remove 'data_' prefix
                    'filename': os.path.basename(file)
                })
    
    return all_files

def main():
    parser = argparse.ArgumentParser(description='Run WALLS survey and process results')
    parser.add_argument('--survey-id', help='ID of the survey to run (e.g., wvs)')
    parser.add_argument('--skip-survey', action='store_true', 
                       help='Skip running survey and only process existing results')
    parser.add_argument('--trials', type=int,
                       help='Number of trials per question. For research use 10 or more.')
    parser.add_argument('--languages', nargs='+',
                       help='List of languages to run the survey in.')
    parser.add_argument('--model', help='OpenAI model to use (e.g., gpt-4, gpt-3.5-turbo)')
    parser.add_argument('--data-file', help='Specific data file to process (optional)')
    parser.add_argument('--model-dir', help='Specific model directory to process (e.g., data_gpt-4o-2024-08-06)')
    args = parser.parse_args()

    # Get survey ID from command line or menu
    survey_id = args.survey_id
    if not survey_id:
        survey_id = select_survey()
        if not survey_id:
            print("\nNo survey selected. Exiting.")
            sys.exit(0)

    survey_dir = f"data/{survey_id}"
    if not os.path.exists(survey_dir):
        raise FileNotFoundError(f"Survey directory not found: {survey_dir}")

    # Load survey data
    questions, survey_config = load_survey_data(survey_id)
    
    if not args.skip_survey:
        # Get model from command line or menu
        model = args.model
        if model is None:
            current_model = config.MODEL_NAME if hasattr(config, 'MODEL_NAME') else None
            model = select_model(current_model)
        # Update config model
        config.MODEL_NAME = model
        
        # Get trials from command line or menu
        trials = args.trials
        if trials is None:
            recommended_trials = survey_config.get('recommended_trials', 10)
            trials = select_trials(recommended_trials)
        
        # Get languages from command line or menu
        languages = args.languages
        if languages is None:
            default_languages = survey_config.get('default_languages', ['English'])
            languages = select_languages(default_languages)
        
        # Get user confirmation
        if not confirm_survey_run(survey_id, languages, trials, questions):
            print("\nSurvey cancelled by user.")
            sys.exit(0)
        
        print("\nStarting survey...")
        print("=" * 50)
        
        results_file = run_survey(
            survey_id,
            num_trials=trials,
            languages=languages,
            translation_settings=survey_config.get('translation_settings', {}),
            model=model  # Pass model to run_survey
        )
        print(f"\nSurvey complete. Results saved to: {results_file}")
    else:
        print(f"\nSkipping survey, processing existing results...")
        if args.data_file:
            data_files = [{'path': args.data_file, 'model': None, 'filename': os.path.basename(args.data_file)}]
        else:
            data_files = find_all_data_files(survey_id)
            if not data_files:
                print(f"No data files found in {survey_dir}")
                sys.exit(1)
            
            print(f"\nFound {len(data_files)} data file(s) to process:")
            for i, file_info in enumerate(data_files, 1):
                print(f"{i}. Model: {file_info['model']}")
                print(f"   File: {file_info['filename']}")

        for file_info in data_files:
            while True:
                response = input(f"\nProcess {file_info['filename']} for model {file_info['model']}? (y/n/q): ").lower()
                if response == 'q':
                    print("\nExiting...")
                    sys.exit(0)
                elif response in ['y', 'n']:
                    break
                print("Please enter 'y' for yes, 'n' for no, or 'q' to quit.")

            if response == 'y':
                print(f"\nProcessing {file_info['filename']}...")
                process_results(file_info['path'], survey_id)
            else:
                print(f"Skipping {file_info['filename']}...")

        print("\nTo view results:")
        print("1. Start the dashboard:")
        print("   python api/app.py")
        print("2. Open http://localhost:8050 in your browser")

if __name__ == "__main__":
    main() 