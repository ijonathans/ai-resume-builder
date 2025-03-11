from http.server import BaseHTTPRequestHandler
import json
import os
import requests

class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Extract data from request
            skills = data.get('skills', '')
            experience = data.get('experience', '')
            job_description = data.get('job_description', '')
            
            # Get API key from environment or request
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key and 'api_key' in data:
                api_key = data.get('api_key')
            
            if not api_key:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "API key is required"}).encode())
                return
                
            if not all([skills, experience, job_description]):
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "All fields are required"}).encode())
                return
                
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
                self.send_response(response.status_code)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": response_data.get("error", {}).get("message", "Error calling OpenAI API")}).encode())
                return
            
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
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
                
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
