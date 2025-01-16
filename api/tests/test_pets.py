import pytest
from fastapi.testclient import TestClient

def test_create_pet(client, auth_headers):
    """Test creating a pet"""
    response = client.post(
        "/api/v1/pets",
        headers=auth_headers,
        json={
            "name": "Fluffy",
            "species": "cat",
            "gender": "female",
            "breed": "Persian"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Fluffy"
    assert data["species"] == "cat"

def test_list_pets(client, auth_headers):
    """Test getting pet list"""
    response = client.get("/api/v1/pets", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
