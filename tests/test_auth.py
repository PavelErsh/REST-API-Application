"""Tests for API authentication"""

import pytest


def test_root_endpoint_no_auth(client):
    """Test that root endpoint doesn't require authentication"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "Organizations Directory API"


def test_organizations_without_api_key(client):
    """Test that protected endpoints require API key"""
    response = client.get("/organizations/")
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authenticated"


def test_organizations_with_invalid_api_key(client):
    """Test that invalid API key is rejected"""
    response = client.get("/organizations/", headers={"X-API-Key": "invalid-key"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid API Key"


def test_organizations_with_valid_api_key(client, auth_headers):
    """Test that valid API key grants access"""
    response = client.get("/organizations/", headers=auth_headers)
    assert response.status_code == 200


def test_buildings_without_api_key(client):
    """Test that buildings endpoint requires API key"""
    response = client.get("/buildings/")
    assert response.status_code == 403


def test_activities_without_api_key(client):
    """Test that activities endpoint requires API key"""
    response = client.get("/activities/")
    assert response.status_code == 403
