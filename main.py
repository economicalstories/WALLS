from openai import OpenAI
import json
import time
import re
import pandas as pd
import config
from translation import translate_prompt
import datetime
import os

# Set up OpenAI API key using the new client method
client = OpenAI(api_key=config.API_KEY)

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
        # Extract the first number from the response
        match = re.search(r"[-+]?\d*\.\d+|\d+", text)
        if match:
            return float(match.group())
        else:
            print("No numeric response found. Response was:", text)
            return None
    except Exception as e:
        print("Error during API call:", e)
        return None

def main():
    # Load questions from the JSON file
    with open("questions.json", "r") as f:
        json_data = json.load(f)
        questions = json_data["questions"]  # Extract the questions array
    
    # Get settings from config
    num_trials_per_question = config.NUM_TRIALS
    languages = config.LANGUAGES
    num_languages = len(languages)
    num_questions = len(questions)

    # --- Calculate and Display Total Trials ---
    total_api_calls = num_languages * num_questions * num_trials_per_question
    print(f"Configuration loaded:")
    print(f"  Languages: {num_languages} ({', '.join(languages)})")
    print(f"  Questions: {num_questions}")
    print(f"  Trials per Question: {num_trials_per_question}")
    print(f"--- Total Estimated API Calls for Responses: {total_api_calls} ---")
    # Note: This doesn't include translation/verification calls.

    results = []
    completed_api_calls = 0 # Initialize counter for response calls

    print("\nStarting Survey Trials...")
    print("=" * 80) # Wider separator

    for language in languages:
        print(f"\nLanguage: {language}")
        print("-" * 80)

        for q_index, q in enumerate(questions): # Use enumerate for question index
            question_id = q["question_id"]
            prompt_text = q["prompt_text"] # Original English

            translated_prompt_for_api = prompt_text
            back_translation_text = ""
            llm_verification_score = ""

            # --- Translation & Verification Step ---
            if language.lower() != "english" and config.USE_TRANSLATION:
                translated_prompt_for_api, back_translation_text, llm_verification_score_obj = \
                    translate_prompt(prompt_text, language)
                llm_verification_score = str(llm_verification_score_obj) if llm_verification_score_obj is not None else "N/A"
            else:
                back_translation_text = "[N/A - English]"
                llm_verification_score = "N/A"

            # --- Run Trials ---
            print(f"\nQuestion ID: {question_id} ({q_index + 1}/{num_questions})")
            print(f"Prompt Sent ({language}): {translated_prompt_for_api}")

            current_question_responses = []
            for trial in range(1, num_trials_per_question + 1):
                response_number = call_openai(translated_prompt_for_api)
                completed_api_calls += 1 # Increment counter after the call

                # --- Append results including ALL details for final CSV ---
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

                # --- Combined Incremental Update Line (Inside Trial Loop) ---
                current_question_responses.append(response_number)
                response_str = str(response_number) if response_number is not None else 'NAA'

                # Calculate running statistics
                valid_responses_so_far = [r for r in current_question_responses if r is not None]
                stats_str = ""
                if valid_responses_so_far:
                    series_so_far = pd.Series(valid_responses_so_far)
                    mean_val = series_so_far.mean()
                    std_val = series_so_far.std() if len(valid_responses_so_far) > 1 else 0.0
                    stats_str = f"| Running Stats ({len(valid_responses_so_far)}/{trial}): Mean={mean_val:.2f}, Std={std_val:.2f}"
                else:
                    stats_str = f"| Running Stats (0/{trial}): No valid responses"

                # Print the combined line with overall progress
                # Calculate progress percentage
                progress_percent = (completed_api_calls / total_api_calls) * 100 if total_api_calls > 0 else 0
                print(f"  Trial {trial}/{num_trials_per_question} (Overall {completed_api_calls}/{total_api_calls} - {progress_percent:.1f}%): {response_str:<5} {stats_str}")

                time.sleep(config.API_DELAY)

            print("-" * 30) # Separator after question trials

    print("\n" + "=" * 80)
    print("All Trials Completed.")
    print("=" * 80)

    # --- Final Processing (save CSV, print overall summary) ---
    df = pd.DataFrame(results)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"results_{timestamp}.csv"
    column_order = [
        "Language", "Question_ID", "Trial_Number", "Response",
        "Original_Prompt", "Translated_Prompt", "Back_Translation", "LLM_Verification_Score"
    ]
    actual_columns = [col for col in column_order if col in df.columns]
    df = df[actual_columns]
    df.to_csv(output_filename, index=False)
    print(f"\nComplete results saved to: {output_filename}")

    print("\n" + "=" * 70)
    print("Processing Final Summary...")
    print("=" * 70)

    # --- Final Summary Table Generation ---
    if not df.empty and 'Response' in df.columns and not df['Response'].isnull().all():
        # 1. Calculate mean for each Language/Question combination
        mean_summary = df.groupby(["Language", "Question_ID"])["Response"].mean().reset_index()

        # 2. Pivot the table: Languages as index, Questions as columns, Mean as values
        try:
            # Use pivot_table for robustness, especially if combinations are missing
            summary_table = mean_summary.pivot_table(index='Language',
                                                     columns='Question_ID',
                                                     values='Response')

            # 3. Calculate standard deviation of means across languages for each question (column)
            #    This tells us how much the average answer varies between languages for a given question.
            #    Need at least 2 languages for std dev, fillna(0) handles cases with only one language.
            std_dev_across_languages = summary_table.std(axis=0).fillna(0)

            # 4. Add the standard deviation as a new row named 'StdDev Across Languages'
            #    Convert Series to DataFrame row before appending (newer pandas versions might need concat)
            std_dev_row = pd.DataFrame([std_dev_across_languages], index=['StdDev Across Languages'])
            summary_table = pd.concat([summary_table, std_dev_row])


            # 5. Print the formatted table
            print("\nFinal Summary Table (Mean Response per Language/Question):")
            # Format the numbers to 2 decimal places for display
            print(summary_table.to_string(float_format="%.2f"))

        except Exception as e:
            print(f"\nError creating pivot table summary: {e}")
            # Fallback: Print the original long-form summary if pivoting fails
            print("\nOriginal Summary Stats (Fallback):")
            original_summary = df.groupby(["Language", "Question_ID"])["Response"].agg(["mean", "std", "count"]).reset_index()
            print(original_summary.to_string(index=False, float_format="%.2f"))

    else:
        print("\nNo valid data to generate summary statistics.")

def save_results(results_data):
    """Save results to a CSV file with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    data_dir = "data"
    os.makedirs(data_dir, exist_ok=True)
    filename = os.path.join(data_dir, f"results_{timestamp}.csv")
    
    # Convert results to DataFrame and save
    df = pd.DataFrame(results_data)
    df.to_csv(filename, index=False)
    print(f"\nResults saved to: {filename}")
    return filename

if __name__ == "__main__":
    main()
