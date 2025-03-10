import streamlit as st
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
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
    
    # Create input fields
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            skills = st.text_area("Skills", 
                                height=150,
                                placeholder="Enter your skills (e.g., Python, Data Analysis, Project Management)")
            
        with col2:
            job_description = st.text_area("Job Description", 
                                        height=150,
                                        placeholder="Paste the job description here")
        
        experience = st.text_area("Experience", 
                                height=200,
                                placeholder="Describe your work experience, education, and relevant projects")
    
    # Generate button
    if st.button("Generate Resume and Cover Letter", type="primary"):
        if not skills or not experience or not job_description:
            st.error("Please fill in all fields before generating content.")
        else:
            with st.spinner("Generating your resume and cover letter..."):
                try:
                    # Call the function to generate content
                    resume, cover_letter = generate_content(skills, experience, job_description)
                    
                    # Display the results
                    st.subheader("Generated Resume")
                    st.markdown(resume)
                    
                    st.subheader("Generated Cover Letter")
                    st.markdown(cover_letter)
                    
                    # Add download buttons
                    st.download_button(
                        label="Download Resume as Text",
                        data=resume,
                        file_name="resume.txt",
                        mime="text/plain"
                    )
                    
                    st.download_button(
                        label="Download Cover Letter as Text",
                        data=cover_letter,
                        file_name="cover_letter.txt",
                        mime="text/plain"
                    )
                    
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

def generate_content(skills, experience, job_description):
    """
    Generate resume and cover letter using OpenAI API
    """
    try:
        # Try to get API key from environment variables first (for local development)
        api_key = os.getenv("OPENAI_API_KEY")
        
        # If not found in environment, try to get from Streamlit secrets (for Streamlit Cloud)
        if not api_key and hasattr(st, "secrets") and "OPENAI_API_KEY" in st.secrets:
            api_key = st.secrets["OPENAI_API_KEY"]
            
        if not api_key:
            st.error("OpenAI API key not found. Please add it to your .env file or Streamlit secrets.")
            st.info("For Streamlit Cloud deployment, add your API key in the app settings under 'Secrets'.")
            return None, None
        
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)
        
        # Create prompt for the AI
        prompt = f"""
        Using the following information, generate a professional resume and cover letter optimized for applicant tracking systems:
        
        SKILLS:
        {skills}
        
        EXPERIENCE:
        {experience}
        
        JOB DESCRIPTION:
        {job_description}
        
        First, create a well-formatted resume with sections for Skills and Experience that highlights relevant qualifications for the job.
        
        Then, create a professional cover letter (1-2 paragraphs) that introduces the candidate, mentions key qualifications from the resume, and explains why they're a good fit for the position described in the job description.
        
        Format both documents professionally.
        """
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # or another appropriate model
            messages=[
                {"role": "system", "content": "You are a professional resume and cover letter writer with expertise in creating ATS-optimized content."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        # Extract and process the response
        content = response.choices[0].message.content
        
        # Split the content into resume and cover letter
        # This is a simple split - you might need to adjust based on actual output
        if "RESUME" in content and "COVER LETTER" in content:
            parts = content.split("COVER LETTER")
            resume = parts[0].replace("RESUME", "").strip()
            cover_letter = parts[1].strip()
        else:
            # Fallback if the expected format isn't found
            resume_end_index = int(len(content) * 0.6)  # Assume first 60% is resume
            resume = content[:resume_end_index].strip()
            cover_letter = content[resume_end_index:].strip()
        
        return resume, cover_letter
        
    except Exception as e:
        st.error(f"Error in generating content: {str(e)}")
        return None, None

if __name__ == "__main__":
    main()
