# WALLS: Wittgenstein's Analysis of LLM Language Systems

A project investigating how large language models respond to standardized survey-style prompts in different languages.

**Live Dashboard:** [https://walls-dashboard.vercel.app/](https://walls-dashboard.vercel.app/)

## Project Overview

This project aims to:
1.  Run standardized surveys (like the World Values Survey) against Large Language Models (LLMs) in multiple languages.
2.  Process and analyze the responses to understand cross-linguistic consistency, translation effects, and potential biases.
3.  Provide an interactive dashboard to visualize and explore the results.

## Project Structure (High Level)

```
WALLS/
├── api/                    # Core dashboard logic & application factory
│   ├── app.py             # Dash app factory (run locally with `python api/app.py`)
│   ├── layout/            # Defines UI structure
│   ├── callbacks/         # Defines interactivity
│   ├── state/             # Manages shared state
│   └── assets/            # Static files (CSS, etc.)
│   └── ... (other internal modules)
├── data/                   # Processed JSON data for the dashboard
│   └── World Values Survey/ # Example survey results
│       ├── questions.json   # Copy of the questions for the dashboard
│       └── results_*.json # Processed results used by dashboard
├── survey_tools/         # Scripts & modules for running surveys
│   ├── survey_runner.py   # Interacts with LLM API
│   ├── result_processor.py # Converts raw results to JSON for `data/`
│   ├── translator.py      # Handles prompt translation (if used)
│   └── ... (other helper modules)
├── run_survey.py         # Main script to execute the survey & processing pipeline
├── config.py             # Root configuration (API Key source, languages, models)
├── requirements.txt      # Python dependencies (for local dev & deployment)
├── vercel.json           # Vercel deployment settings
├── vercel_app.py         # Vercel WSGI entry point (imports app from api/app.py)
├── .env                  # Local environment variables (e.g., OPENAI_API_KEY) - Not in Git
├── .vercelignore         # Files/directories excluded from Vercel deployment
└── runtime.txt           # Specifies Python runtime (e.g., python-3.9) for Vercel
```
*Note: Raw survey results (e.g., CSVs) are typically generated during the `run_survey.py` process and might not be stored directly in the repository or included in deployments.* 

## Setup & Usage

### Prerequisites
- Python 3.9+ (Vercel deployment uses 3.9 as per `runtime.txt`)
- `pip` for installing packages

### Installation
1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd WALLS
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *(The root `requirements.txt` file manages all dependencies.)*

### Running Surveys (Optional - Requires API Key)
1.  **Configure API Key:** Create a `.env` file in the project root (this file is ignored by Git):
    ```bash
    echo "OPENAI_API_KEY=your-key-here" > .env
    ```
    *(Refer to `config.py` for other settings like model, languages, trials.)*
2.  **Execute Survey Pipeline:** Run the main script (likely the one in the root directory), specifying the survey ID (e.g., `wvs`):
    ```bash
    python run_survey.py wvs
    ```
    *(This typically runs the survey via the LLM, processes the raw results, and saves the processed JSON data to the `data/` directory.)*

    To only re-process existing raw data (if available and handled by the script):
    ```bash
    python run_survey.py wvs --skip-survey
    ```

### Viewing the Dashboard

#### Local Development
1.  Ensure processed JSON data exists in the `data/` directory (either from running the survey or by adding pre-processed files).
2.  Run the Dash application directly:
    ```bash
    python api/app.py
    ```
3.  Access the dashboard in your browser, typically at [http://localhost:8050](http://localhost:8050).

#### Vercel Deployment
1.  Connect your Git repository to Vercel.
2.  Vercel uses `vercel.json` and `vercel_app.py` for deployment.
3.  Dependencies are installed from `requirements.txt`.
4.  Files specified in `.vercelignore` are excluded.
5.  **Crucially:** The processed JSON files in the `data/` directory **must** be included in the deployment for the dashboard to function. Ensure `.vercelignore` does not exclude them and `vercel.json`'s `includeFiles` includes `data/**/*` if necessary.
6.  The deployed dashboard is read-only; it uses the included JSON data. Environment variables like `OPENAI_API_KEY` are not needed for the deployed view-only application.

## Configuration

- **`config.py` (Root):** Main configuration for survey parameters (languages, models, trials), API key loading (`.env`), etc.
- **`survey_tools/config.py`:** Appears to be specific configuration for the survey tools themselves (needs verification).

---

## Development Notes

- **Data Flow:** `run_survey.py` -> `survey_tools` (generates raw data, often CSV) -> `result_processor.py` (creates JSON in `data/`) -> `api/app.py` (reads JSON from `data/`).
- **Dependencies:** Managed solely by the root `requirements.txt`.
- **Deployment:** Relies on Vercel finding the `app` object in `vercel_app.py`, which imports it from `api/app.py`. File inclusion (`.vercelignore`, `vercel.json`) is key to ensuring `api/` and `data/` contents are deployed.
- **Python Version:** Vercel uses Python 3.9 (per `runtime.txt`). Ensure local development aligns or is compatible.

---

## Recent Updates

- Code refactoring for better modularity.
- Vercel deployment fixes (file inclusion, WSGI entry point).
- Dependency consolidation to root `requirements.txt`.

---

## Research Motivation

### Language & AI Cognition
- **Cross-Linguistic Consistency:**
  - Do LLMs show consistent "values" across languages?
  - How do cultural nuances affect AI responses?
  - Can systematic biases be identified?

- **Translation Effects:**
  - How does translation impact semantic integrity?
  - Are some concepts "lost in translation"?
  - Can translation drift be measured?

- **Value Systems and Language:**
  - How do linguistic structures influence the expression of values?
  - Which value concepts remain stable across languages?
  - What role does language play in forming AI "belief systems"?

### Methodology
Building on the World Values Survey (WVS) Wave 7 questionnaire, the study focuses on four domains:

- **Economic Values:** Income distribution, private vs. public ownership, and attitudes toward competition.
- **Social Values:** Trust, interpersonal relationships, and cultural norms.
- **Political Culture:** Democratic values, authority, and political ideology.
- **Religious Values:** Beliefs, practices, and moral frameworks.

This structured approach enables a consistent comparison of AI responses, highlighting cross-linguistic patterns and the stability of AI "belief systems."


---

## Dashboard Views

The dashboard provides three views:
1.  **Matrix View**: Overview of all questions and languages
2.  **Question View**: Detailed analysis of individual questions
3.  **Deviation Analysis**: Statistical analysis of response patterns

---

## Research Applications & Future Directions

### Applications
- Enhance multi-language model consistency and address cultural biases
- Develop robust translation systems
- Innovate cross-cultural methodologies in social science and AI ethics
- Compare LLM responses with human survey data
- Analyze model-specific response patterns

### Future Directions
- **Language Translation Integration**
  - Integrate official WVS translations
  - Validate against human survey data
  - Analyze translation effects on responses

- **Multi-Model Analysis**
  - Support for multiple LLM providers
  - Comparative analysis across models
  - Model-specific pattern identification

- **Expanded Coverage**
  - More languages and regional variations
  - Additional cross-cultural surveys
  - Different survey methodologies

- **Collaborative Studies**
  - Partner with WVS researchers
  - Contribute to cross-cultural research
  - Develop standardized evaluation frameworks

---

## Related Project: BabelLM

For a more interactive and engaging way to explore the linguistic variation aspect of this research for a single question, check out the **BabelLM** project:

- **GitHub:** [https://github.com/economicalstories/babellm](https://github.com/economicalstories/babellm)
- **Live App:** [https://babel-lm.vercel.app/](https://babel-lm.vercel.app/)

BabelLM presents a question translated into multiple languages and gamifies the process of understanding AI responses. Users can:
- Predict how an AI model would rank the different translations.
- Compare their predictions against the actual AI model's scoring.
- Visualize the results and share their insights.

It provides a fun, hands-on way to experience some of the core concepts explored in the WALLS project.

---

## License

MIT License (see included license text for full details).

---

## Credits
- **Survey Questions:** Adapted from the WVS Wave 7 Master Questionnaire.
- **Inspiration:** Based on Ludwig Wittgenstein's work on language and meaning.
- **Technology:** Built using OpenAI's GPT models and modern data visualization tools.

---

## Contributing
1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Push the branch.
5. Open a Pull Request.