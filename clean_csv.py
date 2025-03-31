import pandas as pd
import os

def clean_csv(input_filename, output_filename=None):
    """
    Clean a results CSV file by replacing problematic translations with 'NA'.
    
    Args:
        input_filename: Path to the input CSV file
        output_filename: Path for the output CSV file. If None, will append '_cleaned' to input filename
    """
    # Generate output filename if not provided
    if output_filename is None:
        base, ext = os.path.splitext(input_filename)
        output_filename = f"{base}_cleaned{ext}"

    print(f"Reading CSV file: {input_filename}")
    df = pd.read_csv(input_filename)
    
    # Store original row count
    original_rows = len(df)
    
    # Function to check if a string is more than 2x longer than the reference
    def is_too_long(text, reference):
        if pd.isna(text) or pd.isna(reference):
            return False
        return len(str(text)) > 2 * len(str(reference))

    # Initialize counters for reporting
    translations_cleaned = 0
    back_translations_cleaned = 0
    
    # Process each row
    for idx in df.index:
        orig_prompt = df.at[idx, 'Original_Prompt']
        
        # Check Translated_Prompt
        if is_too_long(df.at[idx, 'Translated_Prompt'], orig_prompt):
            df.at[idx, 'Translated_Prompt'] = 'NA'
            df.at[idx, 'Response'] = 'NA'  # Invalid translation means response is invalid
            translations_cleaned += 1
            
        # Check Back_Translation
        if is_too_long(df.at[idx, 'Back_Translation'], orig_prompt):
            df.at[idx, 'Back_Translation'] = 'NA'
            back_translations_cleaned += 1

    # Save cleaned DataFrame
    df.to_csv(output_filename, index=False)
    
    # Print summary
    print("\nCleaning Summary:")
    print(f"Total rows processed: {original_rows}")
    print(f"Translations marked as NA: {translations_cleaned}")
    print(f"Back-translations marked as NA: {back_translations_cleaned}")
    print(f"\nCleaned file saved as: {output_filename}")

    return df  # Return the cleaned DataFrame for further inspection if needed

# Example usage:
if __name__ == "__main__":
    # Replace with your actual CSV filename
    input_file = "results_20250330_220534.csv"  # Update this to your CSV filename
    
    try:
        cleaned_df = clean_csv(input_file)
        
        # Print some statistics about the cleaned data
        print("\nData Statistics After Cleaning:")
        print("\nResponse Types:")
        print(cleaned_df['Response'].value_counts())
        
        print("\nLanguages with NA Responses:")
        na_responses = cleaned_df[cleaned_df['Response'] == 'NA']
        print(na_responses['Language'].value_counts())
        
    except Exception as e:
        print(f"Error processing file: {e}")