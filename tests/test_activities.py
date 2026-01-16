"""Tests for activity endpoints"""

import pytest


def test_list_activities_empty(client, auth_headers):
    """Test listing activities when database is empty"""
    response = client.get("/activities/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_list_activities(client, auth_headers, sample_activities):
    """Test listing all activities"""
    response = client.get("/activities/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 7  # 2 level 1, 4 level 2, 1 level 3
    assert all("name" in activity for activity in data)
    assert all("level" in activity for activity in data)


def test_get_activity_by_id(client, auth_headers, sample_activities):
    """Test getting a specific activity by ID"""
    activity_id = sample_activities["food"].id
    response = client.get(f"/activities/{activity_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == activity_id
    assert data["name"] == "Food"
    assert data["level"] == 1
    assert data["parent_id"] is None


def test_get_nonexistent_activity(client, auth_headers):
    """Test getting a non-existent activity"""
    response = client.get("/activities/9999", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_get_activities_tree(client, auth_headers, sample_activities):
    """Test getting activities as a tree structure"""
    response = client.get("/activities/tree", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()

    # Should have 2 root level activities
    assert len(data) == 2

    # Check that tree structure is present
    assert all("children" in activity for activity in data)

    # Find Food activity and check its children
    food_activity = next((a for a in data if a["name"] == "Food"), None)
    assert food_activity is not None
    assert len(food_activity["children"]) == 2  # Meat and Dairy

    # Find Cars activity
    cars_activity = next((a for a in data if a["name"] == "Cars"), None)
    assert cars_activity is not None
    assert len(cars_activity["children"]) == 2  # Trucks and Passenger

    # Check level 3 (Parts under Passenger)
    passenger = next(
        (c for c in cars_activity["children"] if c["name"] == "Passenger"), None
    )
    assert passenger is not None
    assert len(passenger["children"]) == 1  # Parts


def test_activity_level_constraints(sample_activities):
    """Test that activity levels are within valid range (1-3)"""
    for key, activity in sample_activities.items():
        assert 1 <= activity.level <= 3


def test_activity_hierarchy(sample_activities):
    """Test that activity hierarchy is correctly established"""
    # Level 1 activities should have no parent
    assert sample_activities["food"].parent_id is None
    assert sample_activities["cars"].parent_id is None

    # Level 2 activities should have level 1 parent
    assert sample_activities["meat"].parent_id == sample_activities["food"].id
    assert sample_activities["dairy"].parent_id == sample_activities["food"].id
    assert sample_activities["trucks"].parent_id == sample_activities["cars"].id
    assert sample_activities["passenger"].parent_id == sample_activities["cars"].id

    # Level 3 activity should have level 2 parent
    assert sample_activities["parts"].parent_id == sample_activities["passenger"].id


def test_activities_tree_structure_empty(client, auth_headers):
    """Test getting activities tree when database is empty"""
    response = client.get("/activities/tree", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []
