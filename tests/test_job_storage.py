import pytest
import os
import json
from datetime import datetime
from utils.job_storage import (
    save_jobs_to_local,
    load_saved_jobs,
    remove_saved_job,
    process_dict_datetime,
    DateTimeEncoder
)

def test_save_jobs_to_local(sample_job_data, temp_saved_jobs_dir):
    """Test saving job data to a local JSON file."""
    # Add a datetime object to test encoding
    sample_job_data['posted_date'] = datetime(2023, 1, 1, 12, 0, 0)
    
    file_path = save_jobs_to_local(sample_job_data)
    
    assert os.path.exists(file_path)
    assert file_path.endswith(".json")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        saved_data = json.load(f)
        
    assert saved_data['title'] == sample_job_data['title']
    assert saved_data['company'] == sample_job_data['company']
    assert saved_data['posted_date'] == "2023-01-01 12:00:00"
    assert "date_saved" in saved_data

def test_load_saved_jobs(sample_job_data, temp_saved_jobs_dir):
    """Test loading saved jobs from JSON files."""
    # Initially empty
    assert len(load_saved_jobs()) == 0
    
    # Save a job
    save_jobs_to_local(sample_job_data)
    
    # Load and verify
    jobs = load_saved_jobs()
    assert len(jobs) == 1
    assert jobs[0]['title'] == sample_job_data['title']

def test_remove_saved_job(sample_job_data, temp_saved_jobs_dir):
    """Test removing a saved job."""
    # Save a job
    save_jobs_to_local(sample_job_data)
    
    # Remove the job
    result = remove_saved_job(sample_job_data['title'], sample_job_data['company'])
    assert result is True
    assert len(load_saved_jobs()) == 0
    
    # Remove non-existent job
    result = remove_saved_job("Non Existent", "Company")
    assert result is False

def test_process_dict_datetime():
    """Test processing a dictionary with datetime objects."""
    dt = datetime(2023, 1, 1, 12, 0, 0)
    data = {
        'date': dt,
        'nested': {
            'inner_date': dt
        },
        'list': [dt, {'list_dict_date': dt}]
    }
    
    process_dict_datetime(data)
    
    assert data['date'] == "2023-01-01 12:00:00"
    assert data['nested']['inner_date'] == "2023-01-01 12:00:00"
    assert data['list'][0] == "2023-01-01 12:00:00"
    assert data['list'][1]['list_dict_date'] == "2023-01-01 12:00:00"

def test_datetime_encoder():
    """Test DateTimeEncoder directly."""
    dt = datetime(2023, 1, 1, 12, 0, 0)
    encoder = DateTimeEncoder()
    assert encoder.default(dt) == "2023-01-01 12:00:00"
    
    with pytest.raises(TypeError):
        encoder.default(set([1, 2]))
