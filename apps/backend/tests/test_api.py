import pytest
from fastapi.testclient import TestClient
from app.main import app

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "version" in response.json()

def test_health_endpoint():
    """Test health endpoint"""
    response = client.get("/api/v1/system/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_unauthorized_access():
    """Test unauthorized access to protected endpoints"""
    response = client.get("/api/v1/agents/")
    assert response.status_code == 401

def test_invalid_token():
    """Test invalid token"""
    headers = {"Authorization": "Bearer invalid-token"}
    response = client.get("/api/v1/agents/", headers=headers)
    assert response.status_code == 401 