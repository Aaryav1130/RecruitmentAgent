import pytest
import json
from unittest.mock import patch, MagicMock
from agents.interview_agent import InterviewAgent

def test_generate_basic_questions_developer(sample_job_data_developer):
    """Test generating basic questions for a developer role."""
    agent = InterviewAgent()
    questions = agent._generate_basic_questions(sample_job_data_developer, question_count=3)
    assert len(questions) == 3
    assert all('question' in q for q in questions)
    
    all_questions = agent._generate_basic_questions(sample_job_data_developer, question_count=10)
    assert any("version control" in q.get("tips", "") for q in all_questions)

def test_generate_basic_questions_manager(sample_job_data_manager):
    """Test generating basic questions for a manager role."""
    agent = InterviewAgent()
    questions = agent._generate_basic_questions(sample_job_data_manager, question_count=10)
    assert len(questions) == 10
    assert any("motivate team members" in q.get("question", "") for q in questions)

def test_generate_basic_questions_analyst():
    """Test generating basic questions for a data analyst role."""
    agent = InterviewAgent()
    job_data = {"title": "Data Analyst", "company": "Tech"}
    questions = agent._generate_basic_questions(job_data, question_count=10)
    assert len(questions) == 10
    assert any("SQL" in q.get("question", "") for q in questions)

def test_generate_basic_questions_generic(sample_job_data):
    """Test generating basic questions for a generic role."""
    agent = InterviewAgent()
    questions = agent._generate_basic_questions(sample_job_data, question_count=10)
    assert len(questions) == 10
    assert any("multiple deadlines" in q.get("question", "") for q in questions)

@patch('agents.interview_agent.ChatGroq')
def test_generate_interview_questions_valid_json(mock_chatgroq, sample_job_data):
    """Test generating interview questions with valid JSON response from LLM."""
    mock_instance = MagicMock()
    mock_chatgroq.return_value = mock_instance
    
    mock_response = MagicMock()
    mock_response.content = json.dumps([
        {"question": "Q1", "context": "C1", "tips": "T1", "suggested_answer": "A1"}
    ])
    mock_instance.invoke.return_value = mock_response
    
    agent = InterviewAgent()
    agent.api_key = "test-key"
    
    questions = agent.generate_interview_questions(sample_job_data, question_count=1)
    assert len(questions) == 1
    assert questions[0]["question"] == "Q1"

@patch('agents.interview_agent.ChatGroq')
def test_generate_interview_questions_invalid_response(mock_chatgroq, sample_job_data):
    """Test generating interview questions with invalid response (fallback)."""
    mock_instance = MagicMock()
    mock_chatgroq.return_value = mock_instance
    
    mock_response = MagicMock()
    mock_response.content = "Just some random text without JSON."
    mock_instance.invoke.return_value = mock_response
    
    agent = InterviewAgent()
    agent.api_key = "test-key"
    
    questions = agent.generate_interview_questions(sample_job_data, question_count=2)
    assert len(questions) > 0
    assert questions[0]["question"] == "Just some random text without JSON."
