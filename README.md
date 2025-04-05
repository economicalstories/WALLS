# WALLS: Wittgenstein's Analysis of LLM Language Systems

WALLS explores how a large language model (LLM) responds to standardized survey prompts in multiple languages. Inspired by Wittgenstein’s idea that “the limits of my language are the limits of my world,” the project uses Likert-scale ratings to compare the “values” expressed by the AI across different linguistic contexts.

---

## Research Motivation

### Language & AI Cognition
- **Cross-Linguistic Consistency:**  
  - Do LLMs show consistent “values” across languages?  
  - How do cultural nuances affect AI responses?  
  - Can systematic biases be identified?

- **Translation Effects:**  
  - How does translation impact semantic integrity?  
  - Are some concepts “lost in translation”?  
  - Can translation drift be measured?

- **Value Systems and Language:**  
  - How do linguistic structures influence the expression of values?  
  - Which value concepts remain stable across languages?  
  - What role does language play in forming AI “belief systems”?

### Methodology
Building on the World Values Survey (WVS) Wave 7 questionnaire, the study focuses on four domains:

- **Economic Values:** Income distribution, private vs. public ownership, and attitudes toward competition.
- **Social Values:** Trust, interpersonal relationships, and cultural norms.
- **Political Culture:** Democratic values, authority, and political ideology.
- **Religious Values:** Beliefs, practices, and moral frameworks.

This structured approach enables a consistent comparison of AI responses, highlighting cross-linguistic patterns and the stability of AI “belief systems.”

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
- **Inspiration:** Based on Ludwig Wittgenstein’s work on language and meaning.
- **Technology:** Built using OpenAI’s GPT models and modern data visualization tools.

---
