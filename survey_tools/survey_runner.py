from openai import OpenAI
import json
import time
import re
import pandas as pd
import config
from .translator import translate_prompt
import datetime
import os

# Set up OpenAI API key using the new client method
client = OpenAI(api_key=config.API_KEY)

def run_survey(survey_id, num_trials=None, languages=None, translation_settings=None):
    """
    Run a survey with the given ID.
    Args:
        survey_id: ID of the survey to run
        num_trials: Number of trials per question (overrides config)
        languages: List of languages to run (overrides config)
        translation_settings: Translation settings (overrides config)
    Returns:
        Path to the results file.
    """
    survey_dir = f"api/surveys/{survey_id}"
    questions_file = os.path.join(survey_dir, "questions.json")
    
    # Load questions and survey config from the JSON file
    with open(questions_file, "r") as f:
        json_data = json.load(f)
        questions = json_data["questions"]
        survey_config = json_data["survey"]["metadata"]
    
    # Use provided values or defaults from survey config
    num_trials = num_trials or survey_config.get("recommended_trials", config.DEFAULT_NUM_TRIALS)
    languages = languages or survey_config.get("default_languages", config.DEFAULT_LANGUAGES)
    
    # Set up translation settings
    use_translation = translation_settings.get('use_translation', survey_config.get('translation_settings', {}).get('use_translation', config.USE_TRANSLATION)) if translation_settings else survey_config.get('translation_settings', {}).get('use_translation', config.USE_TRANSLATION)
    
    num_languages = len(languages)
    num_questions = len(questions)

    # Calculate and Display Total Trials
    total_api_calls = num_languages * num_questions * num_trials
    print(f"Configuration loaded:")
    print(f"  Languages: {num_languages} ({', '.join(languages)})")
    print(f"  Questions: {num_questions}")
    print(f"  Trials per Question: {num_trials}")
    print(f"--- Total Estimated API Calls for Responses: {total_api_calls} ---")

    results = []
    completed_api_calls = 0

    print("\nStarting Survey Trials...")
    print("=" * 80)

    for language in languages:
        print(f"\nLanguage: {language}")
        print("-" * 80)

        for q_index, q in enumerate(questions):
            question_id = q["question_id"]
            prompt_text = q["prompt_text"]

            translated_prompt_for_api = prompt_text
            back_translation_text = ""
            llm_verification_score = ""

            if language.lower() != "english" and use_translation:
                translated_prompt_for_api, back_translation_text, llm_verification_score_obj = \
                    translate_prompt(prompt_text, language)
                llm_verification_score = str(llm_verification_score_obj) if llm_verification_score_obj is not None else "N/A"
            else:
                back_translation_text = "[N/A - English]"
                llm_verification_score = "N/A"

            print(f"\nQuestion ID: {question_id} ({q_index + 1}/{num_questions})")
            print(f"Prompt Sent ({language}): {translated_prompt_for_api}")

            current_question_responses = []
            for trial in range(1, num_trials + 1):
                response_number = call_openai(translated_prompt_for_api)
                completed_api_calls += 1

                results.append({
                    "Language": language,
                    "Question_ID": question_id,
                    "Trial_Number": trial,
                    "Original_Prompt": prompt_text,
                    "Translated_Prompt": translated_prompt_for_api if language.lower() != "english" else "[N/A - English]",
                    "Back_Translation": back_translation_text,
                    "LLM_Verification_Score": llm_verification_score,
                    "Response": response_number
                })

                current_question_responses.append(response_number)
                response_str = str(response_number) if response_number is not None else 'N/A'

                valid_responses_so_far = [r for r in current_question_responses if r is not None]
                stats_str = ""
                if valid_responses_so_far:
                    series_so_far = pd.Series(valid_responses_so_far)
                    mean_val = series_so_far.mean()
                    std_val = series_so_far.std() if len(valid_responses_so_far) > 1 else 0.0
                    stats_str = f"| Running Stats ({len(valid_responses_so_far)}/{trial}): Mean={mean_val:.2f}, Std={std_val:.2f}"
                else:
                    stats_str = f"| Running Stats (0/{trial}): No valid responses"

                progress_percent = (completed_api_calls / total_api_calls) * 100 if total_api_calls > 0 else 0
                print(f"  Trial {trial}/{num_trials} (Overall {completed_api_calls}/{total_api_calls} - {progress_percent:.1f}%): {response_str:<5} {stats_str}")

                time.sleep(config.API_DELAY)

            print("-" * 30)

    print("\n" + "=" * 80)
    print("All Trials Completed.")
    print("=" * 80)

    # Save results
    df = pd.DataFrame(results)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    data_dir = os.path.join(survey_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    output_filename = os.path.join(data_dir, f"data_{timestamp}.csv")
    
    column_order = [
        "Language", "Question_ID", "Trial_Number", "Response",
        "Original_Prompt", "Translated_Prompt", "Back_Translation", "LLM_Verification_Score"
    ]
    actual_columns = [col for col in column_order if col in df.columns]
    df = df[actual_columns]
    df.to_csv(output_filename, index=False)
    
    return output_filename

def call_openai(prompt):
    """
    Calls the OpenAI API with the provided prompt and extracts a numeric response.
    """
    try:
        response = client.chat.completions.create(
            model=config.MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a respondent in a values survey. Answer the following question with just one number that best represents your view, according to the scale provided. Do not include any extra commentary."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        text = response.choices[0].message.content.strip()
        match = re.search(r"[-+]?\d*\.\d+|\d+", text)
        if match:
            return float(match.group())
        else:
            print("No numeric response found. Response was:", text)
            return None
    except Exception as e:
        print("Error during API call:", e)
        return None

if __name__ == "__main__":
    print("This module should be run through run_survey.py")
