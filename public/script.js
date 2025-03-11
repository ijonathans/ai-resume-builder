document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const apiKeyInput = document.getElementById('api-key');
    const saveApiKeyBtn = document.getElementById('save-api-key');
    const apiKeyStatus = document.getElementById('api-key-status');
    const skillsInput = document.getElementById('skills');
    const experienceInput = document.getElementById('experience');
    const jobDescriptionInput = document.getElementById('job-description');
    const generateBtn = document.getElementById('generate-btn');
    const outputSection = document.getElementById('output-section');
    const resumeText = document.getElementById('resume-text');
    const coverLetterText = document.getElementById('cover-letter-text');
    const loadingIndicator = document.getElementById('loading');
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');
    const copyResumeBtn = document.getElementById('copy-resume');
    const copyCoverLetterBtn = document.getElementById('copy-cover-letter');
    const downloadResumeBtn = document.getElementById('download-resume');
    const downloadCoverLetterBtn = document.getElementById('download-cover-letter');

    // Check for saved API key
    const savedApiKey = localStorage.getItem('openai_api_key');
    if (savedApiKey) {
        apiKeyInput.value = savedApiKey;
        apiKeyStatus.textContent = 'API key is saved in your browser';
        apiKeyStatus.classList.add('success');
    }

    // Save API Key
    saveApiKeyBtn.addEventListener('click', () => {
        const apiKey = apiKeyInput.value.trim();
        if (apiKey) {
            localStorage.setItem('openai_api_key', apiKey);
            apiKeyStatus.textContent = 'API key saved successfully!';
            apiKeyStatus.classList.add('success');
            apiKeyStatus.classList.remove('error');
        } else {
            apiKeyStatus.textContent = 'Please enter a valid API key';
            apiKeyStatus.classList.add('error');
            apiKeyStatus.classList.remove('success');
        }
    });

    // Tab functionality
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove active class from all buttons and panes
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabPanes.forEach(pane => pane.classList.remove('active'));
            
            // Add active class to clicked button and corresponding pane
            button.classList.add('active');
            const tabId = button.getAttribute('data-tab');
            document.getElementById(`${tabId}-content`).classList.add('active');
        });
    });

    // Generate content
    generateBtn.addEventListener('click', async () => {
        const skills = skillsInput.value.trim();
        const experience = experienceInput.value.trim();
        const jobDescription = jobDescriptionInput.value.trim();
        const apiKey = apiKeyInput.value.trim();
        
        if (!apiKey) {
            apiKeyStatus.textContent = 'Please enter your OpenAI API key';
            apiKeyStatus.classList.add('error');
            apiKeyStatus.classList.remove('success');
            return;
        }
        
        if (!skills || !experience || !jobDescription) {
            alert('Please fill in all fields');
            return;
        }
        
        // Show loading indicator
        loadingIndicator.style.display = 'flex';
        
        try {
            // Make API request to our serverless function
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    skills,
                    experience,
                    job_description: jobDescription,
                    api_key: apiKey
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Display results
                resumeText.textContent = data.resume;
                coverLetterText.textContent = data.cover_letter;
                outputSection.style.display = 'block';
                
                // Scroll to results
                outputSection.scrollIntoView({ behavior: 'smooth' });
            } else {
                alert(`Error: ${data.error || 'Failed to generate content'}`);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred. Please try again later.');
        } finally {
            // Hide loading indicator
            loadingIndicator.style.display = 'none';
        }
    });

    // Copy functionality
    copyResumeBtn.addEventListener('click', () => copyToClipboard(resumeText.textContent));
    copyCoverLetterBtn.addEventListener('click', () => copyToClipboard(coverLetterText.textContent));

    // Download functionality
    downloadResumeBtn.addEventListener('click', () => downloadText(resumeText.textContent, 'resume.txt'));
    downloadCoverLetterBtn.addEventListener('click', () => downloadText(coverLetterText.textContent, 'cover_letter.txt'));
});

// Helper function to copy text to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text)
        .then(() => {
            alert('Copied to clipboard!');
        })
        .catch(err => {
            console.error('Failed to copy text: ', err);
            alert('Failed to copy text. Please try again.');
        });
}

// Helper function to download text as a file
function downloadText(text, filename) {
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}
