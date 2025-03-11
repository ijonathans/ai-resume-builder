from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from openai import OpenAI

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        # Extract data from request
        skills = data.get('skills', '')
        experience = data.get('experience', '')
        job_description = data.get('job_description', '')
        api_key = data.get('api_key', os.getenv("OPENAI_API_KEY"))
        
        if not api_key:
            self.send_error(400, "API key is required")
            return
            
        if not all([skills, experience, job_description]):
            self.send_error(400, "All fields are required")
            return
            
        try:
            # Initialize OpenAI client
            client = OpenAI(api_key=api_key)
            
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
            
            # Send response
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
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def run(server_class=HTTPServer, handler_class=handler):
    server_address = ('', 8000)
    httpd = server_class(server_address, handler_class)
    print('Starting httpd...')
    httpd.serve_forever()

if __name__ == "__main__":
    run()
