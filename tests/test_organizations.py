"""Tests for organization endpoints"""

import pytest


def test_list_organizations_empty(client, auth_headers):
    """Test listing organizations when database is empty"""
    response = client.get("/organizations/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_list_organizations(client, auth_headers, sample_organizations):
    """Test listing all organizations"""
    response = client.get("/organizations/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert all("name" in org for org in data)
    assert all("building" in org for org in data)


def test_get_organization_by_id(client, auth_headers, sample_organizations):
    """Test getting a specific organization by ID"""
    org_id = sample_organizations[0].id
    response = client.get(f"/organizations/{org_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == org_id
    assert data["name"] == "Test Org 1"
    assert "building" in data
    assert "phone_numbers" in data
    assert len(data["phone_numbers"]) == 2


def test_get_nonexistent_organization(client, auth_headers):
    """Test getting a non-existent organization"""
    response = client.get("/organizations/9999", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Organization not found"


def test_get_organizations_by_building(
    client, auth_headers, sample_organizations, sample_buildings
):
    """Test getting organizations in a specific building"""
    building_id = sample_buildings[0].id
    response = client.get(
        f"/organizations/building/{building_id}", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2  # org1 and org3 are in building 1
    assert all(org["building_id"] == building_id for org in data)


def test_get_organizations_by_nonexistent_building(client, auth_headers):
    """Test getting organizations from a non-existent building"""
    response = client.get("/organizations/building/9999", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Building not found"


def test_get_organizations_by_activity_with_children(
    client, auth_headers, sample_organizations, sample_activities
):
    """Test getting organizations by activity including children"""
    food_id = sample_activities["food"].id
    response = client.get(
        f"/organizations/activity/{food_id}?include_children=true", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    # Should include org1 (has meat and dairy) and org3 (has food directly)
    assert len(data) == 2


def test_get_organizations_by_activity_without_children(
    client, auth_headers, sample_organizations, sample_activities
):
    """Test getting organizations by activity without children"""
    food_id = sample_activities["food"].id
    response = client.get(
        f"/organizations/activity/{food_id}?include_children=false",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    # Should only include org3 (has food directly)
    assert len(data) == 1
    assert data[0]["name"] == "Test Org 3"


def test_get_organizations_by_nonexistent_activity(client, auth_headers):
    """Test getting organizations by non-existent activity"""
    response = client.get("/organizations/activity/9999", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_search_organizations_by_name(client, auth_headers, sample_organizations):
    """Test searching organizations by name"""
    response = client.get(
        "/organizations/search/by-name?name=Test%20Org%201", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Org 1"


def test_search_organizations_by_partial_name(
    client, auth_headers, sample_organizations
):
    """Test searching organizations by partial name"""
    response = client.get(
        "/organizations/search/by-name?name=Test", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3  # All test organizations


def test_search_organizations_by_name_no_results(
    client, auth_headers, sample_organizations
):
    """Test searching organizations with no matching results"""
    response = client.get(
        "/organizations/search/by-name?name=NonExistent", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


def test_search_organizations_by_location_radius(
    client, auth_headers, sample_organizations
):
    """Test searching organizations by location with radius"""
    search_data = {"latitude": 55.751244, "longitude": 37.618423, "radius": 10.0}
    response = client.post(
        "/organizations/search/by-location", headers=auth_headers, json=search_data
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1  # At least one organization should be in radius


def test_search_organizations_by_location_rectangle(
    client, auth_headers, sample_organizations
):
    """Test searching organizations by rectangular area"""
    search_data = {
        "latitude": 55.751244,
        "longitude": 37.618423,
        "min_latitude": 55.74,
        "max_latitude": 55.76,
        "min_longitude": 37.60,
        "max_longitude": 37.64,
    }
    response = client.post(
        "/organizations/search/by-location", headers=auth_headers, json=search_data
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_search_organizations_by_location_invalid_params(client, auth_headers):
    """Test searching organizations with invalid location parameters"""
    search_data = {
        "latitude": 55.751244,
        "longitude": 37.618423,
        # Missing both radius and rectangle params
    }
    response = client.post(
        "/organizations/search/by-location", headers=auth_headers, json=search_data
    )
    assert response.status_code == 400
