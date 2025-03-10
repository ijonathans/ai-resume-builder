# AI Resume and Cover Letter Builder

A Streamlit web application that uses OpenAI's API to generate tailored resumes and cover letters based on user input.

## Features

- Input your skills, experience, and job description
- Generate a resume optimized for applicant tracking systems
- Create a professional cover letter tailored to the job description
- Download both documents as text files

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/ai-resume-builder.git
   cd ai-resume-builder
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your OpenAI API key:
   - Create a `.env` file in the project root directory
   - Add your OpenAI API key: `OPENAI_API_KEY=your-api-key-here`

## Usage

1. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

2. Open your web browser and navigate to the URL displayed in the terminal (usually http://localhost:8501)

3. Enter your skills, experience, and the job description in the provided fields

4. Click the "Generate Resume and Cover Letter" button

5. Review the generated content and download as needed

## Requirements

- Python 3.7+
- Streamlit
- OpenAI Python library
- python-dotenv

## License

MIT

## Acknowledgements

- [OpenAI](https://openai.com/) for providing the API
- [Streamlit](https://streamlit.io/) for the web application framework
