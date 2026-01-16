"""Tests for building endpoints"""

import pytest


def test_list_buildings_empty(client, auth_headers):
    """Test listing buildings when database is empty"""
    response = client.get("/buildings/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_list_buildings(client, auth_headers, sample_buildings):
    """Test listing all buildings"""
    response = client.get("/buildings/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert all("address" in building for building in data)
    assert all("latitude" in building for building in data)
    assert all("longitude" in building for building in data)


def test_get_building_by_id(client, auth_headers, sample_buildings):
    """Test getting a specific building by ID"""
    building_id = sample_buildings[0].id
    response = client.get(f"/buildings/{building_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == building_id
    assert data["address"] == "Test Address 1"
    assert data["latitude"] == 55.751244
    assert data["longitude"] == 37.618423


def test_get_nonexistent_building(client, auth_headers):
    """Test getting a non-existent building"""
    response = client.get("/buildings/9999", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Building not found"


def test_building_coordinates_validation(sample_buildings):
    """Test that building coordinates are within valid ranges"""
    for building in sample_buildings:
        assert -90 <= building.latitude <= 90
        assert -180 <= building.longitude <= 180
