# WALLS: Wittgenstein's Analysis of LLM Language Systems

A project investigating how large language models respond to standardized survey-style prompts in different languages.

## Project Structure

```
WALLS/
├── api/                    # Dashboard and survey data
│   ├── dashboard.py        # Interactive web dashboard
│   ├── surveys/           # Survey data and results
│   │   └── wvs/          # Example survey (World Values Survey)
│   │       ├── questions.json  # Survey questions
│   │       └── data/     # Survey results
│   └── assets/           # Dashboard assets
├── survey_tools/         # Survey processing tools
│   ├── survey_runner.py  # Runs surveys using OpenAI API
│   ├── translator.py     # Handles translation of questions
│   └── result_processor.py  # Processes results for dashboard
├── run_survey.py        # Main entry point
└── config.py           # Configuration settings
```

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure your OpenAI API key in `config.py`:
   ```python
   API_KEY = "your-api-key-here"
   ```

3. Run a survey:
   ```bash
   # Run new survey and process results
   python run_survey.py wvs

   # Or just process existing results
   python run_survey.py wvs --skip-survey
   ```

4. View results in the dashboard:
   ```bash
   python api/dashboard.py
   ```
   Then open http://localhost:8080 in your browser.

## Adding a New Survey

1. Create a new survey directory:
   ```bash
   mkdir -p api/surveys/your_survey_id/data
   ```

2. Create `questions.json` in your survey directory:
   ```json
   {
     "questions": [
       {
         "question_id": "Q1",
         "question_title": "Example Question",
         "category": "Category",
         "prompt_text": "On a scale of 1-5, how much...",
         "scale_min": 1,
         "scale_max": 5,
         "scale_labels": {
           "1": "Not at all",
           "5": "Very much"
         }
       }
     ]
   }
   ```

3. Run your survey:
   ```bash
   python run_survey.py your_survey_id
   ```

## Dashboard Views

The dashboard provides three views:
1. **Matrix View**: Overview of all questions and languages
2. **Question View**: Detailed analysis of individual questions
3. **Language Comparison**: Compare responses across languages

## Configuration

Edit `config.py` to configure:
- OpenAI API settings (key, model, delay)
- Languages to test
- Number of trials per question
- Translation settings

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

## Project Components

### 1. Data Collection & Processing
- **Surveys:**  
  Runs LLM-based surveys in multiple languages.
- **Processing:**  
  Validates responses and converts raw data into structured JSON for analysis.

**Key Files:**
- `main.py` – Executes surveys and collects responses.
- `format_results.py` – Processes and summarizes survey data.
- `config.py` – LLM configuration settings.
- `questions.json` – Survey questions and metadata.
- `translation.py` – Manages multi-language translations.
- `requirements.txt` – Lists Python dependencies.

### 2. Interactive Dashboard
- **Visualization:**  
  Provides multiple views to analyze the processed data.
- **Deployment:**  
  Can be run locally or deployed online via Vercel.

**Key Files:**
- `api/dashboard.py` – Interactive dashboard application.
- `vercel.json` – Vercel deployment configuration.

---

## Setup and Usage

### Data Collection
1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Configure API Key:**
   ```bash
   echo "OPENAI_API_KEY=your-key-here" > .env
   ```
3. **Run the Survey:**
   ```bash
   python main.py
   ```

### Data Processing
Process the survey results to generate the JSON file for visualization:
```bash
python format_results.py
```

### Data Visualization

#### Local Development
Start the dashboard locally:
```bash
python api/dashboard.py
```
Access the dashboard at [http://localhost:8080](http://localhost:8080).

#### Vercel Deployment
1. Fork or clone the repository.
2. Connect it to Vercel (vercel.com will auto-detect the Python configuration).
3. Deploy your application—future pushes to the main branch will trigger automatic deployments.

---

## Dashboard Features

- **Matrix View (Desktop Only):**  
  Displays an overview of all survey questions and languages using a heatmap.

- **Question View:**  
  Provides detailed, mobile-optimized analysis of individual questions with configurable graphs (bar/column), including mean/mode indicators and scale metadata.

- **Language Comparison:**  
  Enables statistical comparisons across languages with error bars and Z-score summaries.

---

## Data Files & Development Notes

- **Input:** CSV files (e.g., `results_*.csv`)
- **Processed:** JSON files (e.g., `results_*_by_question.json`)
- **Development:**  
  - The dashboard auto-loads the latest results.  
  - Changes in `format_results.py` regenerate new JSON files.  
  - Uses Python 3.12.  
  - For Vercel, ensure the JSON data file is included and configure environment variables accordingly.

---

## Contributing
1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Push the branch.
5. Open a Pull Request.

---

## Research Applications & Future Directions

### Applications
- Enhance multi-language model consistency and address cultural biases.
- Develop robust translation systems.
- Innovate cross-cultural methodologies in social science and AI ethics.

### Future Directions
- **Expanded Language Coverage:**  
  Include more languages, dialects, and regional variations.
- **Enhanced Analysis Tools:**  
  Integrate advanced statistical methods and interactive visualization techniques.
- **Collaborative Studies:**  
  Collaborate with WVS researchers and cross-validate findings with human studies.

---

## License

MIT License (see included license text for full details).

---

## Credits
- **Survey Questions:** Adapted from the WVS Wave 7 Master Questionnaire.
- **Inspiration:** Based on Ludwig Wittgenstein's work on language and meaning.
- **Technology:** Built using OpenAI's GPT models and modern data visualization tools.

---
