import pytest
from fastapi.testclient import TestClient
from main import app
import os

client = TestClient(app)

def test_upload_manual():
    # Create a dummy pdf file
    file_content = b"dummy pdf content"
    file_name = "test_manual.pdf"
    
    files = {"file": (file_name, file_content, "application/pdf")}
    data = {"brand": "TestBrand", "model": "TestModel"}
    
    response = client.post("/manuals/", files=files, data=data)
    
    assert response.status_code == 201
    assert response.json()["brand"] == "TestBrand"
    assert response.json()["model"] == "TestModel"
    assert "id" in response.json()

def test_list_manuals():
    response = client.get("/manuals/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
