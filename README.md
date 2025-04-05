# WALLS: Wittgenstein's Analysis of LLM Language Systems

WALLS is a project designed to investigate how a large language model (LLM) responds to standardized survey-style prompts in different languages. Inspired by Wittgenstein's assertion that "the limits of my language are the limits of my world," this project uses numeric outputs (such as Likert-scale ratings) to compare the "values" expressed by the LLM when prompted in various languages.

## Research Motivation

### Language and AI Cognition
The relationship between language and thought has been a central question in philosophy and cognitive science. Wittgenstein's famous assertion about language limiting our world raises intriguing questions when applied to artificial intelligence:

1. **Cross-Linguistic Consistency**: 
   - Do LLMs exhibit consistent "values" across different languages?
   - How do cultural nuances embedded in different languages affect AI responses?
   - Can we identify systematic biases in multi-language AI systems?

2. **Translation Effects**:
   - How does the translation process impact the semantic integrity of prompts?
   - Do certain concepts or values "get lost in translation"?
   - Can we measure and quantify translation drift in AI responses?

3. **Value Systems and Language**:
   - How do linguistic structures shape the expression of values?
   - Are certain value concepts more stable across languages than others?
   - What role does language play in the formation of AI "belief systems"?

### Methodology
We use the World Values Survey (WVS) Wave 7 questionnaire as our foundation, focusing on four key domains:

1. **Economic Values**
   - Income distribution preferences
   - Views on private vs. public ownership
   - Attitudes toward competition and work

2. **Social Values & Attitudes**
   - Trust and social capital
   - Interpersonal relationships
   - Cultural norms and practices

3. **Political Culture & Regimes**
   - Democratic values
   - Authority and leadership
   - Political ideology and orientation

4. **Religious Values**
   - Religious beliefs and practices
   - Spiritual importance
   - Moral frameworks

This structured approach allows us to:
- Compare AI responses across consistent value dimensions
- Identify patterns in cross-linguistic value expression
- Evaluate the stability of AI "belief systems" across languages

## Project Components

The project is now structured into two main components:

1. **Data Collection & Processing** (`main.py`, `format_results.py`)
   - Runs survey questions through the LLM in multiple languages
   - Processes and validates responses
   - Generates structured JSON data for analysis

2. **Interactive Dashboard** (`api/dashboard.py`)
   - Visualizes the processed data through an interactive web interface
   - Provides multiple views for data analysis
   - Can be run locally or deployed to Vercel

## File Architecture

### Data Collection & Processing
- `main.py`: Runs the LLM surveys and collects responses
- `format_results.py`: Processes raw survey data into structured JSON
- `config.py`: Configuration settings for the LLM
- `questions.json`: Survey questions and metadata
- `translation.py`: Handles multi-language translations
- `requirements.txt`: Python package dependencies

### Visualization & Analysis
- `api/dashboard.py`: Interactive Dash application for data visualization
- `vercel.json`: Configuration for Vercel deployment

## Setup and Usage

### 1. Data Collection
Follow the setup instructions for running surveys:

```bash
# Install dependencies
pip install -r requirements.txt

# Set up your OpenAI API key in .env
echo "OPENAI_API_KEY=your-key-here" > .env

# Run the survey
python main.py
```

### 2. Data Processing
Process the survey results into a format suitable for visualization:

```bash
# Process the most recent results file
python format_results.py
```

This will:
- Load the raw survey results
- Calculate statistics and summaries
- Generate a JSON file ready for visualization

### 3. Data Visualization

#### Local Development
Run the dashboard locally:

```bash
# Start the dashboard server
python api/dashboard.py

# Access the dashboard at:
# http://localhost:8080/dashboard/
```

#### Vercel Deployment
Deploy the dashboard to Vercel for online access:

1. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Configure Vercel:
   ```bash
   # Initialize Vercel in your project
   vercel
   ```

3. Set up build settings in Vercel:
   - Framework Preset: Python
   - Build Command: `pip install -r requirements.txt`
   - Output Directory: `api`
   - Install Command: `pip install -r requirements.txt`

4. Deploy:
   ```bash
   vercel --prod
   ```

## Dashboard Features

The interactive dashboard provides three main views:

1. **Matrix View**
   - Overview of all questions and languages
   - Heatmap visualization of responses
   - Summary statistics

2. **Question View**
   - Detailed analysis of individual questions
   - Configurable graph types (bar/column)
   - Mean and mode indicators
   - Scale labels and metadata

3. **Language Comparison**
   - Compare responses across languages
   - Statistical analysis with error bars
   - Z-score deviation summary

## Data Files

- **Input**: Survey results CSV files (`results_*.csv`)
- **Processed**: JSON files with statistics (`results_*_by_question.json`)
- **Output**: Interactive web dashboard

## Development Notes

### Local Testing
- The dashboard automatically finds and loads the most recent results file
- Changes to `format_results.py` will generate new JSON files
- The dashboard will pick up new data on restart

### Vercel Deployment
- Ensure your JSON data file is included in the repository
- The dashboard will serve from the root URL (`/`)
- Environment variables can be configured in Vercel dashboard

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Research Applications

The WALLS project has implications for several key areas:

1. **AI Development**
   - Improving multi-language model consistency
   - Identifying and addressing cultural biases
   - Developing more robust translation systems

2. **Social Science Research**
   - New methodologies for cross-cultural studies
   - Understanding value expression across languages
   - Comparative analysis of human and AI value systems

3. **Ethics and AI Safety**
   - Evaluating AI value alignment across cultures
   - Understanding linguistic barriers in AI safety
   - Developing culturally aware AI systems

## Future Directions

1. **Expanded Language Coverage**
   - Including more languages and dialects
   - Analyzing regional variations
   - Studying minority languages

2. **Enhanced Analysis Tools**
   - Advanced statistical methods
   - Interactive visualization tools
   - Comparative analysis frameworks

3. **Integration with Other Studies**
   - Collaboration with WVS researchers
   - Cross-validation with human studies
   - Integration with other AI evaluation frameworks

## License

MIT License

Copyright (c) 2024 [Your Name/Organization]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Credits

- Questions adapted from the World Values Survey (WVS) Wave 7 (2017-2022) Master Questionnaire, published by the World Values Survey Association (www.worldvaluessurvey.org).
- Project inspired by Ludwig Wittgenstein's work on language and meaning.
- Built with OpenAI's GPT models and modern data visualization tools.