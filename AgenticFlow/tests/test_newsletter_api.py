"""
Tests for the Newsletter API endpoints.
"""
import pytest
import os
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from backend.main import create_app
from backend.api.newsletter_endpoints import router

# Create test client
app = create_app()
client = TestClient(app)

# Test data
TEST_NEWSLETTER_CONTENT = """
# Weekly Tech Digest

Welcome to our weekly tech digest! Here are the top stories this week.

## AI Breakthrough
Researchers have made significant progress in AI safety.

## Web Development
New JavaScript framework released with improved performance.
"""

@patch('backend.api.newsletter_endpoints.newsletter_processor')
def test_process_newsletter_success(mock_processor):
    """Test processing a newsletter with valid content."""
    # Mock the processor response
    mock_result = {
        "title": "Weekly Tech Digest",
        "content_type": "text/plain",
        "summary": "Weekly tech digest with AI and web development updates.",
        "articles": [
            {
                "title": "AI Breakthrough",
                "summary": "Researchers have made significant progress in AI safety.",
                "content": "Researchers have made significant progress in AI safety."
            },
            {
                "title": "Web Development",
                "summary": "New JavaScript framework released with improved performance.",
                "content": "New JavaScript framework released with improved performance."
            }
        ]
    }
    mock_processor.process_newsletter.return_value = mock_result
    
    # Make the request
    response = client.post(
        "/api/newsletters/process",
        json={
            "content": TEST_NEWSLETTER_CONTENT,
            "content_type": "text/plain"
        },
        headers={"Authorization": "Bearer test-token"}
    )
    
    # Assert the response
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "processed"
    assert data["title"] == "Weekly Tech Digest"
    assert data["article_count"] == 2

@patch('backend.api.newsletter_endpoints.newsletter_processor')
def test_upload_newsletter_file(mock_processor, tmp_path):
    """Test uploading a newsletter file."""
    # Create a test file
    test_file = tmp_path / "test_newsletter.html"
    test_file.write_text("<html><body><h1>Test Newsletter</h1></body></html>")
    
    # Mock the processor response
    mock_processor.process_newsletter.return_value = {
        "title": "Test Newsletter",
        "content_type": "text/html",
        "summary": "Test newsletter content.",
        "articles": []
    }
    
    # Make the request
    with open(test_file, 'rb') as f:
        response = client.post(
            "/api/newsletters/upload",
            files={"file": ("test_newsletter.html", f, "text/html")},
            data={"content_type": "article"},
            headers={"Authorization": "Bearer test-token"}
        )
    
    # Assert the response
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "processed"
    assert data["title"] == "test_newsletter.html"

@patch('backend.api.newsletter_endpoints.newsletter_processor')
def test_publish_newsletter(mock_processor):
    """Test publishing a newsletter to social media."""
    # Mock the processor response
    mock_processor.process_newsletter.return_value = {
        "title": "Test Newsletter",
        "content_type": "text/plain",
        "summary": "Test newsletter content.",
        "articles": []
    }
    
    # Make the request
    response = client.post(
        "/api/newsletters/123/publish",
        json={"platforms": ["twitter", "linkedin"]},
        headers={"Authorization": "Bearer test-token"}
    )
    
    # Assert the response
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "twitter" in data["message"]
    assert "linkedin" in data["message"]

def test_get_nonexistent_newsletter():
    """Test retrieving a non-existent newsletter."""
    response = client.get(
        "/api/newsletters/nonexistent-id",
        headers={"Authorization": "Bearer test-token"}
    )
    assert response.status_code == 501  # Not Implemented

def test_get_nonexistent_articles():
    """Test retrieving articles from a non-existent newsletter."""
    response = client.get(
        "/api/newsletters/nonexistent-id/articles",
        headers={"Authorization": "Bearer test-token"}
    )
    assert response.status_code == 501  # Not Implemented
