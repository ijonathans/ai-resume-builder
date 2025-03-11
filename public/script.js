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
            console.log('Sending request to API...');
            
            // Get the current URL to determine if we're on localhost or deployed
            const baseUrl = window.location.origin;
            const apiUrl = `${baseUrl}/api`;
            
            console.log(`Using API URL: ${apiUrl}`);
            
            // Make API request to our serverless function
            const response = await fetch(apiUrl, {
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
            
            console.log('Response status:', response.status);
            
            // Get the raw text first to debug
            let rawText;
            try {
                rawText = await response.text();
                console.log('Raw response:', rawText);
            } catch (e) {
                console.error('Error reading response text:', e);
                alert('Error reading response from server. Please try again later.');
                return;
            }
            
            // If the response is empty or not valid JSON, handle the error
            if (!rawText || rawText.includes('FUNCTION_INVOCATION_FAILED') || rawText.includes('server error')) {
                console.error('Server error response:', rawText);
                alert('Server error occurred. This might be due to the OpenAI API key being invalid or the server having issues. Please check your API key and try again.');
                return;
            }
            
            // Try to parse as JSON
            let data;
            try {
                data = JSON.parse(rawText);
                console.log('Parsed response data:', data);
            } catch (e) {
                console.error('Error parsing JSON response:', e);
                alert('Error: Invalid response from server. Please try again later.');
                return;
            }
            
            // Check if we have a successful response
            if (data.statusCode === 200 || response.status === 200) {
                // Get the actual data
                let result;
                
                if (data.body) {
                    // Parse the body if it's a string
                    if (typeof data.body === 'string') {
                        try {
                            result = JSON.parse(data.body);
                        } catch (e) {
                            console.error('Error parsing response body:', e);
                            result = { error: 'Failed to parse response' };
                        }
                    } else {
                        result = data.body;
                    }
                } else {
                    // If there's no body, use the response data directly
                    result = data;
                }
                
                console.log('Final data:', result);
                
                if (result.error) {
                    alert(`Error: ${result.error}`);
                    return;
                }
                
                // Display results
                resumeText.textContent = result.resume || '';
                coverLetterText.textContent = result.cover_letter || '';
                outputSection.style.display = 'block';
                
                // Scroll to results
                outputSection.scrollIntoView({ behavior: 'smooth' });
            } else {
                // Handle error response
                let errorMessage = 'Failed to generate content';
                
                if (data.body && typeof data.body === 'string') {
                    try {
                        const bodyData = JSON.parse(data.body);
                        if (bodyData.error) {
                            errorMessage = bodyData.error;
                        }
                    } catch (e) {
                        console.error('Error parsing error body:', e);
                    }
                } else if (data.error) {
                    errorMessage = data.error;
                }
                
                alert(`Error: ${errorMessage}`);
            }
        } catch (error) {
            console.error('Error:', error);
            alert(`An error occurred: ${error.message}`);
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
