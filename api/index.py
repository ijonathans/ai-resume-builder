import json
import os
import requests

def handler(event, context):
    """
    Vercel serverless function handler for the API endpoint.
    """
    # Set CORS headers for all responses
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Content-Type': 'application/json'
    }
    
    # Handle CORS preflight requests
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    # Ensure this is a POST request
    if event.get('httpMethod') != 'POST':
        return {
            'statusCode': 405,
            'headers': headers,
            'body': json.dumps({'error': 'Method not allowed'})
        }
    
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        
        # Extract data from request
        skills = body.get('skills', '')
        experience = body.get('experience', '')
        job_description = body.get('job_description', '')
        api_key = body.get('api_key', os.environ.get('OPENAI_API_KEY', ''))
        
        # Validate inputs
        if not api_key:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'API key is required'})
            }
            
        if not all([skills, experience, job_description]):
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'All fields are required'})
            }
        
        # Call OpenAI API
        openai_url = "https://api.openai.com/v1/chat/completions"
        
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
        
        openai_headers = {
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
        
        response = requests.post(openai_url, headers=openai_headers, json=payload)
        
        # Handle OpenAI API response
        if response.status_code != 200:
            error_message = response.json().get("error", {}).get("message", "Error calling OpenAI API")
            return {
                'statusCode': response.status_code,
                'headers': headers,
                'body': json.dumps({'error': error_message})
            }
        
        # Process the response
        response_data = response.json()
        content = response_data["choices"][0]["message"]["content"].strip()
        
        # Split content into resume and cover letter
        if "---" in content:
            resume, cover_letter = content.split("---", 1)
        else:
            # Fallback if separator not found
            resume_end = int(len(content) * 0.6)
            resume, cover_letter = content[:resume_end], content[resume_end:]
        
        # Return the result
        result = {
            "resume": resume.strip(),
            "cover_letter": cover_letter.strip()
        }
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(result)
        }
            
    except Exception as e:
        # Log the error for debugging
        error_message = str(e)
        print(f"Error in handler: {error_message}")
        
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': error_message})
        }
