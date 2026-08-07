import pytest
from config import COLORS, JOB_PLATFORMS, LLM_MODEL, DEFAULT_JOB_COUNT

def test_colors_dict_contains_required_keys():
    """Test that COLORS dict has all required keys."""
    required_keys = ['primary', 'secondary', 'success', 'error']
    for key in required_keys:
        assert key in COLORS

def test_job_platforms_is_list():
    """Test that JOB_PLATFORMS is a list with specific elements."""
    assert isinstance(JOB_PLATFORMS, list)
    assert "LinkedIn" in JOB_PLATFORMS
    assert "Indeed" in JOB_PLATFORMS
    assert "Glassdoor" in JOB_PLATFORMS
    assert "Naukri" in JOB_PLATFORMS

def test_llm_model_is_valid():
    """Test that LLM_MODEL is a non-empty string."""
    assert isinstance(LLM_MODEL, str)
    assert len(LLM_MODEL) > 0

def test_default_job_count():
    """Test that DEFAULT_JOB_COUNT is a positive integer."""
    assert isinstance(DEFAULT_JOB_COUNT, int)
    assert DEFAULT_JOB_COUNT > 0
