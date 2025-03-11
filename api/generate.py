from http.server import BaseHTTPRequestHandler
import json
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def handler(request):
    if request.method == "OPTIONS":
        # Handle CORS preflight request
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        }
        return {"statusCode": 200, "headers": headers, "body": ""}
    
    if request.method == "POST":
        try:
            # Parse request body
            data = json.loads(request.body)
            
            # Extract data from request
            skills = data.get('skills', '')
            experience = data.get('experience', '')
            job_description = data.get('job_description', '')
            
            # Get API key from environment or request
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key and 'api_key' in data:
                api_key = data.get('api_key')
            
            if not api_key:
                return {
                    "statusCode": 400,
                    "headers": {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": "*"
                    },
                    "body": json.dumps({"error": "API key is required"})
                }
                
            if not all([skills, experience, job_description]):
                return {
                    "statusCode": 400,
                    "headers": {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": "*"
                    },
                    "body": json.dumps({"error": "All fields are required"})
                }
                
            # Use direct OpenAI API call with requests instead of the OpenAI package
            url = "https://api.openai.com/v1/chat/completions"
            
            # Generate content
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
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "You are a professional resume and cover letter writer with expertise in creating ATS-optimized content."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 2000,
                "temperature": 0.7
            }
            
            response = requests.post(url, headers=headers, json=payload)
            response_data = response.json()
            
            if response.status_code != 200:
                return {
                    "statusCode": response.status_code,
                    "headers": {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": "*"
                    },
                    "body": json.dumps({"error": response_data.get("error", {}).get("message", "Error calling OpenAI API")})
                }
            
            content = response_data["choices"][0]["message"]["content"].strip()
            
            # Split content
            if "---" in content:
                resume, cover_letter = content.split("---", 1)
            else:
                resume_end = int(len(content) * 0.6)  # Fallback: first 60%
                resume, cover_letter = content[:resume_end], content[resume_end:]
            
            # Prepare response
            result = {
                "resume": resume.strip(),
                "cover_letter": cover_letter.strip()
            }
            
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps(result)
            }
                
        except Exception as e:
            return {
                "statusCode": 500,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({"error": str(e)})
            }
    
    # Method not allowed
    return {
        "statusCode": 405,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({"error": "Method not allowed"})
    }
