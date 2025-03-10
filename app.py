import streamlit as st
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
try:
    load_dotenv()
    st.sidebar.success("Loaded environment variables from .env file")
except Exception as e:
    st.sidebar.info("No .env file found or error loading it. This is normal in cloud deployment.")

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
    
    # Display API key status
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key and hasattr(st, "secrets") and "OPENAI_API_KEY" in st.secrets:
        api_key = st.secrets["OPENAI_API_KEY"]
        st.sidebar.success("Using API key from Streamlit secrets")
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
                    resume, cover_letter = generate_content(api_key, skills, experience, job_description)
                    
                    if resume and cover_letter:
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
                    st.exception(e)  # This will display the full traceback

def generate_content(api_key, skills, experience, job_description):
    """
    Generate resume and cover letter using OpenAI API
    """
    try:
        # Initialize OpenAI client
        try:
            client = OpenAI(api_key=api_key)
            st.sidebar.success("Successfully initialized OpenAI client")
        except Exception as e:
            st.error(f"Error initializing OpenAI client: {str(e)}")
            return None, None
        
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
        
        Format both documents professionally. Separate the resume and cover letter with '---'.
        """
        
        # Call OpenAI API
        try:
            st.sidebar.info("Calling OpenAI API...")
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",  # Using a more widely available model
                messages=[
                    {"role": "system", "content": "You are a professional resume and cover letter writer with expertise in creating ATS-optimized content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            st.sidebar.success("Successfully received response from OpenAI API")
        except Exception as e:
            st.error(f"Error calling OpenAI API: {str(e)}")
            return None, None
        
        # Extract and process the response
        content = response.choices[0].message.content
        
        # Split the content into resume and cover letter
        if "---" in content:
            resume, cover_letter = content.split("---", 1)
        elif "RESUME" in content and "COVER LETTER" in content:
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
        st.exception(e)  # This will display the full traceback
        return None, None

if __name__ == "__main__":
    main()