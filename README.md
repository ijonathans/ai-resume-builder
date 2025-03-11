# AI Resume and Cover Letter Builder

A web application that uses OpenAI's API to generate tailored resumes and cover letters based on user input. This project is configured for both local development with Streamlit and deployment on Vercel.

## Features

- Input your skills, experience, and job description
- Generate a resume optimized for applicant tracking systems
- Create a professional cover letter tailored to the job description
- Download both documents as text files

## Local Development with Streamlit

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

4. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

5. Open your web browser and navigate to the URL displayed in the terminal (usually http://localhost:8501)

## Deploying to Vercel

This project is configured for deployment on Vercel, which provides serverless functions and static site hosting.

### Prerequisites

1. [Create a Vercel account](https://vercel.com/signup) if you don't have one
2. Install the [Vercel CLI](https://vercel.com/download):
   ```
   npm install -g vercel
   ```

### Deployment Steps

1. Login to Vercel from the CLI:
   ```
   vercel login
   ```

2. Deploy the project:
   ```
   vercel
   ```

3. During deployment, you'll be prompted to set up environment variables. Add your `OPENAI_API_KEY`.

4. Alternatively, you can add environment variables through the Vercel dashboard:
   - Go to your project settings
   - Navigate to the "Environment Variables" section
   - Add `OPENAI_API_KEY` with your OpenAI API key

### Project Structure for Vercel

The project has been restructured to work with Vercel:

- `/api/generate.py` - Serverless function that handles API requests to OpenAI
- `/public/` - Static files for the frontend (HTML, CSS, JS)
- `vercel.json` - Configuration file for Vercel deployment

## Requirements

- Python 3.7+
- Streamlit (for local development)
- OpenAI Python library
- python-dotenv

## License

MIT

## Acknowledgements

- [OpenAI](https://openai.com/) for providing the API
- [Streamlit](https://streamlit.io/) for the local development framework
- [Vercel](https://vercel.com/) for serverless deployment
