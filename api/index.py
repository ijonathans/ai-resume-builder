from http.server import BaseHTTPRequestHandler
import json
import os
import requests

class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
    def do_POST(self):
        try:
            # Get content length
            content_length = int(self.headers.get('Content-Length', 0))
            
            # Read request body
            request_body = self.rfile.read(content_length).decode('utf-8')
            body = json.loads(request_body)
            
            # Extract data from request
            skills = body.get('skills', '')
            experience = body.get('experience', '')
            job_description = body.get('job_description', '')
            api_key = body.get('api_key', os.environ.get('OPENAI_API_KEY', ''))
            
            # Validate inputs
            if not api_key:
                self._send_error_response(400, 'API key is required')
                return
                
            if not all([skills, experience, job_description]):
                self._send_error_response(400, 'All fields are required')
                return
            
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
                self._send_error_response(response.status_code, error_message)
                return
            
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
            
            self._send_json_response(200, result)
                
        except Exception as e:
            # Log the error for debugging
            error_message = str(e)
            print(f"Error in handler: {error_message}")
            self._send_error_response(500, error_message)
    
    def _send_json_response(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def _send_error_response(self, status_code, error_message):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({'error': error_message}).encode('utf-8'))
