from openai import OpenAI
import config
import time
import re # Import regex for parsing the score

# Set up OpenAI API key using the new client method
client = OpenAI(api_key=config.API_KEY)

# --- New Function for LLM Verification ---
def verify_translation_meaning(original_text, back_translated_text):
    """
    Uses an LLM call to rate the semantic similarity between the original
    and back-translated text.

    Returns:
        int: A similarity score (e.g., 1-5), or None if verification fails.
    """
    print("  Running LLM verification of back-translation...")
    verification_prompt = f"""
Compare the semantic meaning of the following two sentences.
Sentence A (Original): "{original_text}"
Sentence B (Back-Translated): "{back_translated_text}"

On a scale of 1 to 5, how similar are Sentence A and Sentence B in meaning?
1 = Completely different meaning or the back-translation is nonsensical.
2 = Some overlap in meaning, but key points are different or lost.
3 = Roughly similar meaning, but with noticeable differences in nuance or detail.
4 = Very similar meaning, mostly interchangeable, minor differences possible.
5 = Identical or virtually identical meaning.

Respond with only a single digit number (1, 2, 3, 4, or 5).
"""
    try:
        response = client.chat.completions.create(
            model=config.MODEL_NAME, # Or potentially a cheaper/faster model if suitable
            messages=[
                {"role": "system", "content": "You are an evaluator comparing the semantic meaning of two sentences provided. Output only a single numeric score from 1 to 5 based on the specified scale."},
                {"role": "user", "content": verification_prompt}
            ],
            temperature=0,
            max_tokens=5 # Restrict output length to help get just the number
        )
        score_text = response.choices[0].message.content.strip()

        # Extract the first digit found
        match = re.search(r"\d", score_text)
        if match:
            score = int(match.group())
            if 1 <= score <= 5:
                print(f"  LLM Verification Score: {score}/5")
                time.sleep(config.API_DELAY) # Delay after verification call
                return score
            else:
                print(f"  LLM Verification Warning: Score ({score}) out of range (1-5).")
                return None # Score out of expected range
        else:
            print(f"  LLM Verification Warning: Could not parse numeric score from response: '{score_text}'")
            return None # Failed to parse score

    except Exception as e:
        print(f"  LLM Verification error: {e}")
        return None # Verification failed

# --- Modified translate_prompt Function ---
def translate_prompt(prompt, target_language):
    """
    Translate the prompt, back-translate, verify using LLM, print results,
    and return the forward translation, back translation, and score.

    Returns:
        tuple: (translated_text, back_translated_text, verification_score)
               Values might be placeholders if steps failed/were skipped.
    """
    print(f"  Translating to {target_language}...")
    original_prompt = prompt
    # Initialize return values with defaults/placeholders
    translated_text = prompt # Default fallback for forward translation
    back_translated_text = "[Back-translation not performed]"
    verification_score = None

    # --- 1. Forward Translation ---
    try:
        forward_instruction = f"Translate the following English text accurately into {target_language}, preserving the meaning and nuance of the original survey question and its response scale:\n\n{prompt}"
        response_fwd = client.chat.completions.create(
            model=config.MODEL_NAME,
            messages=[
                {"role": "system", "content": f"You are an expert translator specializing in English to {target_language} translations for surveys. Ensure the core question and the response instructions are clear."},
                {"role": "user", "content": forward_instruction}
            ],
            temperature=0
        )
        translated_text = response_fwd.choices[0].message.content.strip()
        print(f"  Forward translation ({target_language}) successful.")
        time.sleep(config.API_DELAY)

        # --- 2. Back Translation (only if forward succeeded and is different) ---
        if translated_text != original_prompt:
            print(f"  Performing back-translation ({target_language} -> English)...")
            back_translated_text = "[Back-translation failed]" # Update default for this block
            try:
                back_instruction = f"Translate the following {target_language} text accurately back into English:\n\n{translated_text}"
                response_back = client.chat.completions.create(
                     model=config.MODEL_NAME,
                     messages=[
                         {"role": "system", "content": f"You are an expert translator. Translate the following text from {target_language} accurately back into English."},
                         {"role": "user", "content": back_instruction}
                     ],
                     temperature=0
                 )
                back_translated_text = response_back.choices[0].message.content.strip()
                print(f"  Back-translation (English) successful.")
                time.sleep(config.API_DELAY)

                # --- 3. LLM Verification Step ---
                verification_score = verify_translation_meaning(original_prompt, back_translated_text)

            except Exception as e_back:
                print(f"  Back-translation error ({target_language} -> English): {e_back}")
                # back_translated_text remains "[Back-translation failed]"
                # verification_score remains None
        else:
            # Case where forward translation returned original prompt
             print(f"  Skipping back-translation and verification as forward translation returned the original prompt.")
             back_translated_text = "[Back-translation skipped]"

    except Exception as e_fwd:
        print(f"  Forward translation error (English -> {target_language}): {e_fwd}")
        # translated_text remains original prompt
        # back_translated_text remains "[Back-translation not performed]"
        # verification_score remains None
        print("="*20 + " VERIFICATION SKIPPED " + "="*20)
        # Return current state on forward failure
        return translated_text, back_translated_text, verification_score

    # --- 4. Print Combined Comparison ---
    print("\n" + "="*20 + f" TRANSLATION CHECK ({target_language}) " + "="*20)
    print(f"Original (English):     {original_prompt}")
    print(f"Translated ({target_language}): {translated_text}")
    print(f"Back-Translated (Eng):  {back_translated_text}")
    score_display = str(verification_score) if verification_score is not None else "N/A"
    print(f"LLM Verification Score: {score_display}/5")
    print("="*60 + "\n")

    # --- 5. Return all results ---
    return translated_text, back_translated_text, verification_score
