import pandas as pd
import os
import numpy as np
import json
import glob
from datetime import datetime
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'  # Simple format without timestamps
)
logger = logging.getLogger(__name__)

class NumpyJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle numpy types."""
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        return super().default(obj)

# Quality thresholds
QUALITY_THRESHOLDS = {
    'min_llm_verification': 4.0,  # Minimum LLM verification score
    'min_responses_per_question': 5,  # Minimum responses needed per question
    'min_questions_per_language': 1.0,  # Changed to 1.0 to require all questions
    'max_std_dev': 3.0,  # Maximum allowed standard deviation for responses
}

def evaluate_language_quality(df: pd.DataFrame, total_questions: int) -> Dict[str, Dict[str, Any]]:
    """
    Evaluate the quality of translations for each language.
    
    Args:
        df: DataFrame with survey responses
        total_questions: Total number of unique questions in the survey
    
    Returns:
        Dictionary with language quality metrics
    """
    language_quality = {}
    
    # Get scale_min for each question from questions data - use survey_dir from outer scope
    questions_file = os.path.join("data", "World Values Survey", "questions.json")
    with open(questions_file, "r") as f:
        questions_data = json.load(f)["questions"]
    scale_mins = {q['question_id']: int(q['scale_min']) for q in questions_data}
    
    for language in df['Language'].unique():
        lang_data = df[df['Language'] == language]
        
        # Calculate quality metrics
        # Check for valid responses (not NaN and >= scale_min) per question
        valid_responses_per_question = {}
        for qid in scale_mins:
            q_data = lang_data[lang_data['Question_ID'] == qid]
            min_scale = scale_mins[qid]
            valid_count = q_data[
                (q_data['Response'].notna()) & 
                (q_data['Response'] >= min_scale)
            ].shape[0]
            valid_responses_per_question[qid] = valid_count > 0
        
        questions_with_valid_responses = sum(valid_responses_per_question.values())
        
        # For non-English, we care about verification scores
        if language != 'English':
            avg_verification = lang_data['LLM_Verification_Score'].mean()
            if pd.isna(avg_verification):
                avg_verification = 0.0
        else:
            # For English, set verification score to maximum (5.0)
            avg_verification = 5.0  # Perfect verification score for reference language
            
        # Calculate std dev only for valid responses
        response_stds = []
        for qid in scale_mins:
            q_data = lang_data[lang_data['Question_ID'] == qid]
            min_scale = scale_mins[qid]
            valid_responses = q_data[
                (q_data['Response'].notna()) & 
                (q_data['Response'] >= min_scale)
            ]['Response']
            if len(valid_responses) > 0:
                response_stds.append(valid_responses.std())
        
        response_std = np.mean(response_stds) if response_stds else 0.0
        
        # Compute coverage ratio based on questions with valid responses
        coverage_ratio = questions_with_valid_responses / total_questions
        
        # Store metrics
        language_quality[language] = {
            'questions_answered': int(questions_with_valid_responses),
            'total_questions': total_questions,
            'coverage_ratio': coverage_ratio,
            'avg_verification_score': avg_verification,
            'avg_response_std': response_std if not pd.isna(response_std) else 0.0,
            'passes_threshold': (
                # Include English if it has any valid responses
                (language == 'English' and questions_with_valid_responses > 0) or
                (
                    questions_with_valid_responses == total_questions and  # Must have valid responses for all questions
                    avg_verification >= QUALITY_THRESHOLDS['min_llm_verification'] and
                    (response_std <= QUALITY_THRESHOLDS['max_std_dev'] if not pd.isna(response_std) else True)
                )
            )
        }
        
        logger.debug(f"Language {language} metrics:")
        logger.debug(f"  Valid Questions: {questions_with_valid_responses}/{total_questions}")
        logger.debug(f"  Coverage: {coverage_ratio:.2f}")
        logger.debug(f"  Verification Score: {avg_verification:.2f}")
        logger.debug(f"  Response StdDev: {response_std:.2f}")
    
    return language_quality

def process_results(results_file, survey_id):
    """
    Legacy function to process survey results.
    This function is maintained for backward compatibility.
    Args:
        results_file: Path to the results CSV file
        survey_id: ID of the survey to process
    """
    # Extract model name from results file path if present
    path_parts = results_file.split(os.sep)
    model_name = None
    for part in path_parts:
        if part.startswith('data_'):
            model_name = part[5:]  # Remove 'data_' prefix
            break
    
    print(f"Processing file: {results_file}")  # Add explicit print for clarity
    return process_survey_results(survey_id, model_name, specific_file=results_file)

def process_survey_results(survey_id: str, model_name: str = None, specific_file: str = None) -> str:
    """
    Process survey results and create summary files for dashboard.
    Args:
        survey_id: ID of the survey to process
        model_name: Name of the model used for the survey
        specific_file: Optional specific data file to process. If None, processes all files.
    """
    survey_dir = f"data/{survey_id}"
    model_dir = f"data_{model_name}" if model_name else "data"
    data_dir = os.path.join(survey_dir, model_dir)
    
    # Find data files to process
    if specific_file:
        data_files = [specific_file] if os.path.exists(specific_file) else []
    else:
        data_files = sorted(glob.glob(os.path.join(data_dir, "data_*.csv")))
    
    if not data_files:
        logger.error(f"No data files found in {data_dir}")
        return
    
    logger.info(f"Found {len(data_files)} data file(s) to process")
    for file in data_files:
        logger.info(f"Will process: {os.path.basename(file)}")
    
    results_files = []
    for data_file in data_files:
        logger.info(f"\nProcessing results from: {data_file}")
        
        # Load questions data
        questions_file = os.path.join(survey_dir, "questions.json")
        with open(questions_file, "r") as f:
            questions_data = json.load(f)["questions"]
        
        # Read and process the results
        df = pd.read_csv(data_file)
        
        # Convert Response and LLM_Verification_Score to numeric
        df['Response'] = pd.to_numeric(df['Response'], errors='coerce')
        df['LLM_Verification_Score'] = pd.to_numeric(df['LLM_Verification_Score'], errors='coerce')
        
        # Evaluate language quality
        total_questions = len(questions_data)
        language_quality = evaluate_language_quality(df, total_questions)
        
        # Filter for languages that pass quality thresholds
        valid_languages = [lang for lang, metrics in language_quality.items() 
                         if metrics['passes_threshold']]
        
        logger.info(f"Languages passing quality thresholds: {valid_languages}")
        logger.info("Language quality metrics:")
        for lang, metrics in language_quality.items():
            logger.info(f"{lang}: {'PASS' if metrics['passes_threshold'] else 'FAIL'} - "
                       f"Coverage: {metrics['coverage_ratio']:.2f}, "
                       f"Verification: {metrics['avg_verification_score']:.2f}")
        
        # Filter valid responses - simplified filtering
        valid_responses = df[
            (df['Language'].isin(valid_languages)) &
            (df['Response'].notna())
        ]
        
        # Create question lookup dict
        questions_lookup = {q['question_id']: q for q in questions_data}
        
        # Calculate statistics by question
        results = []
        for question_id, group in valid_responses.groupby('Question_ID'):
            if question_id in questions_lookup:
                q_data = questions_lookup[question_id]
                
                # Calculate statistics by language
                lang_stats_dict = {}
                for lang, lang_group in group.groupby('Language'):
                    # Filter for valid responses (not NaN and >= scale_min)
                    valid_responses = lang_group['Response'][
                        (lang_group['Response'].notna()) & 
                        (lang_group['Response'] >= q_data['scale_min'])
                    ]
                    
                    if len(valid_responses) >= QUALITY_THRESHOLDS['min_responses_per_question']:
                        lang_stats_dict[lang] = {
                            'count': int(len(valid_responses)),
                            'mean': float(valid_responses.mean()),
                            'std': float(valid_responses.std()),
                            'quality_metrics': language_quality[lang]
                        }
                
                # Only add questions that have valid responses
                if lang_stats_dict:
                    all_means = [stats['mean'] for stats in lang_stats_dict.values()]
                    total_responses = sum(stats['count'] for stats in lang_stats_dict.values())
                    
                    results.append({
                        'question_id': question_id,
                        'title': q_data['question_title'],
                        'category': q_data['category'],
                        'scale_min': int(q_data['scale_min']),
                        'scale_max': int(q_data['scale_max']),
                        'scale_labels': q_data['scale_labels'],
                        'num_languages': len(lang_stats_dict),
                        'total_responses': total_responses,
                        'overall_mean': float(np.mean(all_means)),
                        'language_stats': lang_stats_dict,
                        'prompt_text': q_data['prompt_text']
                    })
        
        # Get timestamp from data file
        timestamp = os.path.basename(data_file).split('_')[1] + '_' + os.path.basename(data_file).split('_')[2].split('.')[0]
        
        # Save results with quality metrics
        results_filename = os.path.join(data_dir, f"results_{timestamp}.json")
        try:
            with open(results_filename, 'w', encoding='utf-8') as f:
                json.dump({
                    'results': results,
                    'quality_metrics': {
                        'thresholds': QUALITY_THRESHOLDS,
                        'language_quality': language_quality,
                        'timestamp': timestamp,
                        'total_questions': total_questions,
                        'valid_languages': valid_languages,
                        'source_file': os.path.basename(data_file)
                    }
                }, f, indent=2, ensure_ascii=False, cls=NumpyJSONEncoder)
            
            results_files.append(results_filename)
            logger.info(f"Created results file: {results_filename}")
            
        except Exception as e:
            logger.error(f"Error saving results file: {e}")
            import traceback
            traceback.print_exc()
            continue
        
        logger.info(f"Total questions processed: {len(results)}")
        logger.info(f"Total valid responses: {sum(q['total_responses'] for q in results)}")
        logger.info(f"Valid languages: {sorted(valid_languages)}")
    
    return results_files[-1] if results_files else None

def get_friendly_model_name(model_name):
    """Convert model name to friendly display name"""
    if not model_name:
        return "Default"
    # Extract date if present
    if '-' in model_name:
        base_name, version = model_name.rsplit('-', 1)
        try:
            # Try to parse date from version (YYMM format)
            date = datetime.strptime(version, "%y%m")
            return f"{base_name.upper()} ({date.strftime('%b %Y')})"
        except ValueError:
            return model_name.upper()
    return model_name.upper()

if __name__ == "__main__":
    print("This module should be run through run_survey.py")