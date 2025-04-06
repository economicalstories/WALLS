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

def load_survey_data(survey_id):
    """Load survey questions and configuration."""
    questions_file = os.path.join("api/surveys", survey_id, "questions.json")
    if not os.path.exists(questions_file):
        raise FileNotFoundError(f"Survey questions not found: {questions_file}")
    
    with open(questions_file, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
        return json_data["questions"], json_data["survey"]["metadata"]

def find_latest_results(survey_id):
    """Find the most recent results file for a given survey."""
    data_dir = f"api/surveys/{survey_id}/data"
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

def main():
    parser = argparse.ArgumentParser(description='Run WALLS survey and process results')
    parser.add_argument('survey_id', help='ID of the survey to run (e.g., wvs)')
    parser.add_argument('--skip-survey', action='store_true', 
                       help='Skip running survey and only process existing results')
    parser.add_argument('--trials', type=int,
                       help='Number of trials per question. For research use 10 or more.')
    parser.add_argument('--languages', nargs='+',
                       help='List of languages to run the survey in.')
    args = parser.parse_args()

    survey_dir = f"api/surveys/{args.survey_id}"
    if not os.path.exists(survey_dir):
        raise FileNotFoundError(f"Survey directory not found: {survey_dir}")

    # Load survey data
    questions, survey_config = load_survey_data(args.survey_id)
    
    if not args.skip_survey:
        # Set up survey parameters
        trials = args.trials if args.trials is not None else survey_config.get('recommended_trials', 10)
        languages = args.languages if args.languages else survey_config.get('default_languages', ['English'])
        
        # Get user confirmation
        if not confirm_survey_run(args.survey_id, languages, trials, questions):
            print("\nSurvey cancelled by user.")
            sys.exit(0)
        
        print("\nStarting survey...")
        print("=" * 50)
        
        results_file = run_survey(
            args.survey_id,
            num_trials=trials,
            languages=languages,
            translation_settings=survey_config.get('translation_settings', {})
        )
        print(f"\nSurvey complete. Results saved to: {results_file}")
    else:
        print(f"\nSkipping survey, processing existing results...")
        results_file = find_latest_results(args.survey_id)
        print(f"Using latest results file: {results_file}")

    print("\nProcessing results...")
    print("=" * 50)
    process_results(results_file, args.survey_id)

    print("\nTo view results:")
    print("1. Start the dashboard:")
    print("   python api/dashboard.py")
    print("2. Open http://localhost:8080 in your browser")

if __name__ == "__main__":
    main() 