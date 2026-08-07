import pytest
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Interview.livekit_token import app

@pytest.fixture
def sample_resume_text():
    """Returns a sample multiline resume text."""
    return """
    John Doe
    john.doe@example.com | 123-456-7890
    
    Education:
    B.S. Computer Science, University of Technology
    
    Skills:
    Python, Java, React, SQL, Machine Learning
    
    Experience:
    Software Engineer at Tech Corp
    - Developed web applications using React and Python
    - Implemented RESTful APIs
    """

@pytest.fixture
def sample_job_data():
    """Returns a generic job data dictionary."""
    return {
        "title": "Software Engineer",
        "company": "Tech Corp",
        "location": "Remote",
        "description": "Looking for a skilled software engineer with Python experience.",
        "platform": "LinkedIn",
        "url": "http://example.com/job"
    }

@pytest.fixture
def sample_job_data_developer(sample_job_data):
    """Returns a developer job data dictionary."""
    data = sample_job_data.copy()
    data["title"] = "Python Developer"
    return data

@pytest.fixture
def sample_job_data_manager(sample_job_data):
    """Returns a manager job data dictionary."""
    data = sample_job_data.copy()
    data["title"] = "Engineering Manager"
    return data

@pytest.fixture
def mock_groq_api_key():
    """Returns a mock Groq API key."""
    return 'test-api-key-12345'

@pytest.fixture
def temp_saved_jobs_dir(tmp_path, monkeypatch):
    """Creates a temp directory and patches saved_jobs path."""
    monkeypatch.chdir(tmp_path)
    os.makedirs("saved_jobs", exist_ok=True)
    return tmp_path / "saved_jobs"

@pytest.fixture
def flask_test_client():
    """Creates a Flask test client."""
    app.config.update({"TESTING": True})
    return app.test_client()
