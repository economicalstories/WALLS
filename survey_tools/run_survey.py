import argparse
import os
import json
from survey_runner import run_survey
from model_manager import get_model_id

def get_available_surveys():
    """Find all available surveys in the surveys directory"""
    surveys = []
    survey_dir = "api/surveys"
    
    if not os.path.exists(survey_dir):
        print(f"Survey directory not found: {survey_dir}")
        return []
    
    for item in os.listdir(survey_dir):
        survey_path = os.path.join(survey_dir, item)
        questions_path = os.path.join(survey_path, "questions.json")
        
        if os.path.isdir(survey_path) and os.path.exists(questions_path):
            try:
                with open(questions_path, "r", encoding="utf-8") as f:
                    questions_data = json.load(f)
                    survey_title = questions_data.get("survey", {}).get("title", item)
                    surveys.append({
                        "id": item,
                        "title": survey_title,
                        "path": survey_path
                    })
            except json.JSONDecodeError:
                print(f"Warning: Invalid questions.json in survey {item}")
                continue
    
    return surveys

def select_survey_interactive():
    """Present an interactive menu to select a survey"""
    surveys = get_available_surveys()
    
    if not surveys:
        raise ValueError("No surveys found in api/surveys directory")
    
    print("\nAvailable Surveys:")
    print("-" * 50)
    for idx, survey in enumerate(surveys, 1):
        print(f"{idx}. {survey['title']}")
        print(f"   ID: {survey['id']}")
        print()
    
    while True:
        try:
            choice = input("\nSelect a survey (enter number): ")
            idx = int(choice) - 1
            if 0 <= idx < len(surveys):
                return surveys[idx]["id"]
            print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

def main():
    parser = argparse.ArgumentParser(description="Run a survey using OpenAI models")
    parser.add_argument("--survey", help="Survey ID to run (if not specified, will show interactive menu)")
    parser.add_argument("--model", help="OpenAI model ID to use (if not specified, will show interactive menu)")
    parser.add_argument("--languages", nargs="+", help="List of languages to run the survey in")
    parser.add_argument("--num-samples", type=int, default=1, help="Number of samples per question")
    
    args = parser.parse_args()
    
    # Get survey ID either from command line or interactive selection
    try:
        if args.survey:
            survey_id = args.survey
            # Verify the survey exists
            surveys = get_available_surveys()
            if not any(s["id"] == survey_id for s in surveys):
                print(f"Error: Survey '{survey_id}' not found")
                return
        else:
            survey_id = select_survey_interactive()
        print(f"\nSelected survey: {survey_id}")
    except Exception as e:
        print(f"Error selecting survey: {e}")
        return
    
    # Get model ID either from command line or interactive selection
    try:
        model_id = get_model_id(args.model)
        print(f"\nUsing model: {model_id}")
    except Exception as e:
        print(f"Error selecting model: {e}")
        return
    
    # Run the survey
    run_survey(
        survey_id=survey_id,
        model_id=model_id,
        languages=args.languages,
        num_samples=args.num_samples
    )

if __name__ == "__main__":
    main() 