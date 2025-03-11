import json
import os
import requests
from http import HTTPStatus

def handler(request):
    """
    Vercel serverless function handler for resume and cover letter generation
    """
    # Handle CORS preflight requests
    if request.method == "OPTIONS":
        return {
            "status": HTTPStatus.OK,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
            "body": ""
        }
    
    # Only accept POST requests
    if request.method != "POST":
        return {
            "status": HTTPStatus.METHOD_NOT_ALLOWED,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({"error": "Method not allowed"})
        }
    
    try:
        # Parse request body
        body = request.body.decode('utf-8') if isinstance(request.body, bytes) else request.body
        data = json.loads(body)
        
        # Extract data from request
        skills = data.get('skills', '')
        experience = data.get('experience', '')
        job_description = data.get('job_description', '')
        
        # Get API key from environment or request
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key and 'api_key' in data:
            api_key = data.get('api_key')
        
        if not api_key:
            return {
                "status": HTTPStatus.BAD_REQUEST,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({"error": "API key is required"})
            }
            
        if not all([skills, experience, job_description]):
            return {
                "status": HTTPStatus.BAD_REQUEST,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({"error": "All fields are required"})
            }
            
        # Use direct OpenAI API call with requests
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
                "status": response.status_code,
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
            "status": HTTPStatus.OK,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps(result)
        }
            
    except Exception as e:
        return {
            "status": HTTPStatus.INTERNAL_SERVER_ERROR,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({"error": str(e)})
        }
