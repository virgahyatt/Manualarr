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

def test_delete_manual():
    # First upload a manual (duplicate logic to avoid dependency on return value of test function)
    file_content = b"dummy pdf content for delete"
    file_name = "delete_me.pdf"
    files = {"file": (file_name, file_content, "application/pdf")}
    data = {"brand": "DeleteBrand", "model": "DeleteModel"}
    upload_response = client.post("/manuals/", files=files, data=data)
    manual_id = upload_response.json()["id"]
    
    # Delete it
    response = client.delete(f"/manuals/{manual_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Manual deleted successfully"
    
    # Verify it's gone
    response = client.get("/manuals/")
    manuals = response.json()
    assert not any(m["id"] == manual_id for m in manuals)
    
    # Verify file is gone (optional, but good practice if test uses real FS)
    # Note: TestClient uses the same app instance, so UPLOAD_DIR is consistent