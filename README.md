# WALLS: Wittgenstein’s Analysis of LLM Language Systems

WALLS is a project designed to investigate how a large language model (LLM) responds to standardized survey-style prompts in different languages. Inspired by Wittgenstein’s assertion that “the limits of my language are the limits of my world,” this project uses numeric outputs (such as Likert-scale ratings) to compare the “values” expressed by the LLM when prompted in various languages. By systematically simulating survey responses, WALLS explores whether—and how—the translation of questions affects the distribution of responses produced by the AI.

The survey questions are drawn from the World Values Survey (WVS) Wave 7 (2017–2022) questionnaire. In particular, WALLS focuses on items from the **Economic Values**, **Social Values & Attitudes**, **Political Culture & Political Regimes**, and **Religious Values** sections. These sections provide a rich basis for investigating how an LLM “values” different aspects of life—from economic policy and social trust to political systems and religious belief—across linguistic contexts.

---

# AI Values Survey Runner

This repository contains scripts and configuration files that enable you to simulate surveys using an AI model (e.g., OpenAI's GPT series). The project:
- Translates survey questions from English into multiple target languages.
- Runs each question multiple times to capture variability in the model’s numeric outputs.
- Performs automated translation verification (forward translation, back translation, and semantic similarity scoring) to ensure prompt fidelity.
- Logs detailed trial data and outputs summary statistics for further analysis.

---

## Motivation and Theoretical Background

### Language and Cognition
Wittgenstein famously argued that our language limits our world. WALLS extends this idea into the realm of AI by asking: Does the language in which a prompt is given alter the “values” produced by an LLM? In other words, can the AI’s responses differ meaningfully if a survey question is asked in English versus Spanish, French, or other languages?

### Source of Survey Questions: World Values Survey Wave 7
WALLS draws its survey items from key sections of the WVS Wave 7 questionnaire:
- **Economic Values:** Questions on income distribution, private versus public ownership, and the perceived benefits of competition and hard work.
- **Social Values & Attitudes:** Items addressing trust, social norms, and interpersonal relationships.
- **Political Culture & Political Regimes:** Questions that assess opinions on political systems, the role of leaders, and left–right orientations.
- **Religious Values:** Questions on the importance of religion in life, religious beliefs, and practices.

Using these established questions, the project leverages a well-validated social science instrument to evaluate the impact of language on AI-generated survey responses.

### Research Questions
- Does an LLM produce consistent numeric “values” across different languages?
- How do translation and back-translation processes affect the semantic integrity of survey prompts?
- What does the variability in responses tell us about the internal representation of values in the LLM?

---

## File Architecture and Key Components

### 1. `requirements.txt`
Lists the necessary Python packages:
- **openai:** For accessing OpenAI’s API.
- **pandas:** For data handling and statistical analysis.
- **python-dotenv:** For secure management of API keys.

### 2. `config.py`
Contains configuration settings:
- **API_KEY:** Your OpenAI API key (loaded from a `.env` file).
- **MODEL_NAME:** The OpenAI model to use (e.g., `"gpt-4"`).
- **NUM_TRIALS_TEST / NUM_TRIALS_PROD:** Number of trials per question.
- **API_DELAY:** Delay (in seconds) between API calls.
- **USE_TRANSLATION:** Enables/disables prompt translation.
- **LANGUAGES:** A list of target languages. Derived from the WVS-7 dataset, it includes:
        "Catalan", "English", "Spanish", "French", "Armenian", "Bengali",
      "Portuguese", "Chinese", "Greek", "Turkish", "Czech", "Arabic",
      "Amharic", "Oromo", "Tigris", "German", "Cantonese", "Putonghua",
      "Hindu", "Indonesian", "Persian", "Japanese", "Kazakh", "Russian",
      "Swahili", "Kirghiz", "Malay", "Dhivehi", "Mongolian", "Burmese",
      "Dutch", "Hausa", "Igbo", "Yoruba", "Urdu", "Bikol", "Cebuano",
      "Filipino", "Ikolo", "Tausug", "Waray", "Hiligaynon", "Romanian",
      "Serbian", "Slovak", "Korean", "Tajik", "Thai", "Ukrainian",
      "Uzbek", "Vietnamese", "Shona", "Ndebele"
  
### 3. `questions.json`
Stores the survey questions. Each entry includes:
- **question_id:** A unique identifier (e.g., "Q106").
- **prompt_text:** The full text of the survey prompt (with instructions and scale details).

### 4. `translation.py`
Provides functions for translating prompts:
- **Forward Translation:** Converts the English prompt to a target language.
- **Back Translation:** Converts the translated prompt back to English.
- **LLM Verification:** Uses an additional API call to compare the original and back-translated prompts, generating a semantic similarity score.

### 5. `main.py`
The main orchestrator script:
- **Loads Questions:** Reads `questions.json`.
- **Handles Translation:** Translates prompts when needed.
- **Runs Trials:** Calls the OpenAI API for each question and language over multiple trials.
- **Logs Data:** Saves each trial’s details (language, question ID, trial number, responses, translation data) to a date-stamped CSV file.
- **Computes Statistics:** Calculates and prints summary statistics (mean, standard deviation, count) for each question and language.
- **Displays Final Summary:** Outputs a summary table comparing mean responses across languages and questions.

---

## Setup

### Prerequisites
- Python 3.7 or higher.
- An active OpenAI API key.

### Repository Setup
1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd <your-repo-directory>
   ```

2. **Install Dependencies:**
   Create a `requirements.txt` file with the following content:
   ```text
   openai>=1.0.0
   pandas
   python-dotenv
   ```
   Then run:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API Key:**
   - Create a `.env` file in the project root:
     ```dotenv
     OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
     ```
   - Add `.env` to your `.gitignore` file to prevent committing sensitive data:
     ```gitignore
     .env
     __pycache__/
     *.py[cod]
     *$py.class
     results_*.csv
     ```

4. **Configure Script Settings:**
   - Edit `config.py` to adjust:
     - `MODEL_NAME` (e.g., `"gpt-4"`).
     - `NUM_TRIALS_TEST` for testing and `NUM_TRIALS_PROD` for production.
     - `API_DELAY` and `USE_TRANSLATION`.
     - `LANGUAGES` as shown above.

---

## Running the Script

Execute the main script from your terminal:

```bash
python main.py
```

### What to Expect:
- **Console Output:**  
  Live updates including:
  - The current language and question being processed.
  - Details of translation verification (forward, back translation, LLM similarity scores).
  - Incremental summary statistics for each question.
- **CSV Output:**  
  A date-stamped CSV file (e.g., `results_20231028_103000.csv`) will be created with detailed trial data:
  - **Language, Question_ID, Trial_Number, Response**
  - **Original_Prompt, Translated_Prompt, Back_Translation, LLM_Verification_Score**
- **Final Summary Table:**  
  A printed summary comparing mean responses and standard deviations across languages and questions.

---

## Translation Verification Process

For non-English languages, the script follows these steps:
1. **Forward Translation:**  
   Translate the original English prompt to the target language.
2. **Back Translation:**  
   Translate the target language prompt back into English.
3. **LLM Verification:**  
   Use a dedicated API call to compare the original and back-translated English texts, producing a semantic similarity score (1–5). Lower scores may indicate translation drift.
4. **Logging:**  
   All translation-related data is recorded in the CSV file.

---

## Theoretical Implications

By drawing questions from the **Economic Values**, **Social Values & Attitudes**, **Political Culture & Political Regimes**, and **Religious Values** sections of the WVS Wave 7 questionnaire, WALLS situates its investigation within a well-validated social science framework. This allows for:
- **Cross-Linguistic Consistency Analysis:**  
  Determining if the LLM’s “values” remain stable or shift when survey prompts are delivered in different languages.
- **Semantic Integrity in Translation:**  
  Assessing whether translation introduces biases or semantic shifts that affect the model's responses.
- **Exploration of AI Limitations:**  
  Understanding the boundaries of an LLM's “world” as defined by the language used, echoing Wittgenstein’s insights about language and thought.

This research not only contributes to discussions about AI reliability and cultural bias but also advances our understanding of how language shapes both human and artificial cognition.

---

This README.md provides a comprehensive overview of the project's motivation, technical setup, and theoretical underpinnings, ensuring that WALLS is well-positioned for both experimental use and academic inquiry.