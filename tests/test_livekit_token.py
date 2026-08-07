import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from Interview.livekit_token import app, messages_add

@pytest.fixture
def client():
    app.config.update({"TESTING": True})
    with app.test_client() as client:
        yield client
        
@pytest.fixture(autouse=True)
def clear_messages():
    """Clear messages before each test."""
    messages_add.clear()
    yield

@patch('Interview.livekit_token.api.AccessToken')
def test_get_token(mock_access_token, client):
    """Test getting a token."""
    # We patch generate_room_name to avoid async issues with test_client
    with patch('Interview.livekit_token.generate_room_name', new_callable=AsyncMock) as mock_generate_room:
        mock_generate_room.return_value = "room-test"
        
        # Setup mock AccessToken builder chain
        mock_token_instance = mock_access_token.return_value
        mock_token_instance.with_identity.return_value = mock_token_instance
        mock_token_instance.with_name.return_value = mock_token_instance
        mock_token_instance.with_grants.return_value = mock_token_instance
        mock_token_instance.to_jwt.return_value = "mock_jwt_token"
        
        response = client.get('/getToken')
        assert response.status_code == 200
        assert response.data.decode('utf-8') == "mock_jwt_token"
        
        # Test with specific name
        response = client.get('/getToken?name=TestUser')
        assert response.status_code == 200
        mock_token_instance.with_identity.assert_called_with("TestUser")

def test_process_chat_valid(client):
    """Test processing chat with valid JSON."""
    payload = [{"role": "user", "content": "Hello"}]
    response = client.post('/process-chat', json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert len(messages_add) == 1
    assert messages_add[0]["content"] == "Hello"

def test_process_chat_empty(client):
    """Test processing chat with empty body."""
    response = client.post('/process-chat', json=[])
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    
    # Missing JSON payload returns 415 or 400
    response2 = client.post('/process-chat')
    assert response2.status_code in [400, 415]

def test_get_messages(client):
    """Test getting messages."""
    # Add a message first
    client.post('/process-chat', json=[{"role": "user", "content": "Test"}])
    
    response = client.get('/get-messages')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["content"] == "Test"
