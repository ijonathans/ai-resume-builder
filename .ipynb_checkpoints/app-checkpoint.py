import streamlit as st
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables (optional for local dev; Streamlit Cloud uses Secrets)
load_dotenv()

# Set up page configuration
st.set_page_config(
    page_title="AI Resume and Cover Letter Builder",
    page_icon="📝",
    layout="wide"
)

def main():
    # App title and description
    st.title("AI Resume and Cover Letter Builder")
    st.markdown("""
    This application helps you create a tailored resume and cover letter using AI.
    Enter your skills, experience, and the job description to generate content optimized for applicant tracking systems.
    """)

    # API key handling
    api_key = os.getenv("OPENAI_API_KEY")  # From .env (local) or environment
    if not api_key and "OPENAI_API_KEY" in st.secrets:
        api_key = st.secrets["OPENAI_API_KEY"]  # From Streamlit Cloud Secrets
        st.sidebar.success("Using API key from Streamlit Secrets")
    elif api_key:
        st.sidebar.success("Using API key from environment variables")
    else:
        api_key = st.sidebar.text_input("Enter your OpenAI API Key", type="password")
        if not api_key:
            st.sidebar.error("OpenAI API key required")
            st.info("""
            ### API Key Required
            - **Streamlit Cloud**: Add `OPENAI_API_KEY` in app settings under 'Secrets'.
            - **Local**: Add to a `.env` file as `OPENAI_API_KEY=your-key-here`.
            """)
            return  # Stop execution until key is provided

    # Initialize OpenAI client only when we have a key
    client = OpenAI(api_key=api_key)

    # Input fields
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            skills = st.text_area("Skills", height=150, placeholder="e.g., Python, Data Analysis")
        with col2:
            job_description = st.text_area("Job Description", height=150, placeholder="Paste job description here")
        experience = st.text_area("Experience", height=200, placeholder="e.g., Intern at xAI, 2024")

    # Generate button
    if st.button("Generate Resume and Cover Letter", type="primary"):
        if not all([skills, experience, job_description]):
            st.error("Please fill in all fields.")
        else:
            with st.spinner("Generating your resume and cover letter..."):
                resume, cover_letter = generate_content(client, skills, experience, job_description)
                if resume and cover_letter:
                    st.subheader("Generated Resume")
                    st.markdown(resume)
                    st.subheader("Generated Cover Letter")
                    st.markdown(cover_letter)
                    st.download_button("Download Resume", resume, file_name="resume.txt", mime="text/plain")
                    st.download_button("Download Cover Letter", cover_letter, file_name="cover_letter.txt", mime="text/plain")

def generate_content(client, skills, experience, job_description):
    """Generate resume and cover letter using OpenAI API."""
    try:
        prompt = f"""
        Using the following information, generate a professional resume and cover letter optimized for applicant tracking systems:
        
        SKILLS:
        {skills}
        
        EXPERIENCE:
        {experience}
        
        JOB DESCRIPTION:
        {job_description}
        
        First, create a well-formatted resume with sections for Skills and Experience that highlights relevant qualifications for the job.
        Then, create a professional cover letter (1-2 paragraphs) that introduces the candidate, mentions key qualifications from the resume, and explains why they're a good fit for the position.
        Separate the resume and cover letter with '---'.
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional resume and cover letter writer with expertise in creating ATS-optimized content."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        content = response.choices[0].message.content.strip()
        
        # Split content (improved logic)
        if "---" in content:
            resume, cover_letter = content.split("---", 1)
        else:
            resume_end = int(len(content) * 0.6)  # Fallback: first 60%
            resume, cover_letter = content[:resume_end], content[resume_end:]
        
        return resume.strip(), cover_letter.strip()
    
    except Exception as e:
        st.error(f"Error generating content: {str(e)}")
        return None, None

if __name__ == "__main__":
    main()