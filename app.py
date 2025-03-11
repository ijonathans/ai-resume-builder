import streamlit as st
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables (optional for local testing; Streamlit Cloud uses Secrets)
load_dotenv()

# Page configuration
st.set_page_config(page_title="AI Resume and Cover Letter Builder", page_icon="📝", layout="wide")

def main():
    st.title("AI Resume and Cover Letter Builder")
    st.markdown("Generate ATS-optimized resumes and cover letters using AI.")

    # API key handling
    api_key = os.getenv("OPENAI_API_KEY") or st.secrets["OPENAI_API_KEY"]
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
            with st.spinner("Generating..."):
                resume, cover_letter = generate_content(client, skills, experience, job_description)
                if resume and cover_letter:
                    st.subheader("Generated Resume")
                    st.markdown(resume)
                    st.subheader("Generated Cover Letter")
                    st.markdown(cover_letter)
                    st.download_button("Download Resume", resume, file_name="resume.txt", mime="text/plain")
                    st.download_button("Download Cover Letter", cover_letter, file_name="cover_letter.txt", mime="text/plain")

def generate_content(client, skills, experience, job_description):
    try:
        prompt = f"""
        Using the following information, generate a professional resume and cover letter optimized for applicant tracking systems:
        SKILLS: {skills}
        EXPERIENCE: {experience}
        JOB DESCRIPTION: {job_description}
        Create a resume with bullet-point sections for Skills and Experience.
        Then, create a 1-2 paragraph cover letter introducing the candidate and explaining their fit.
        Separate with '---'.
        """
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional resume and cover letter writer."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        content = response.choices[0].message.content.strip()
        resume, cover_letter = content.split("---", 1) if "---" in content else (content[:int(len(content)*0.6)], content[int(len(content)*0.6):])
        return resume.strip(), cover_letter.strip()
    except Exception as e:
        st.error(f"Error: {e}")
        return None, None

if __name__ == "__main__":
    main()