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

def test_upload_manual_auto_metadata():
    # Upload without brand/model
    file_content = b"%PDF-1.4 empty pdf" # Minimal PDF header to maybe avoid immediate parser crash? 
    # Actually pypdf will likely fail on malformed PDF, causing None/None return -> "Unknown"
    
    file_name = "auto_meta.pdf"
    files = {"file": (file_name, file_content, "application/pdf")}
    # No data dict
    
    response = client.post("/manuals/", files=files)
    
    assert response.status_code == 201
    json_resp = response.json()
    assert json_resp["brand"] == "Unknown"
    assert json_resp["model"] == "Unknown"

def test_list_manuals():
    response = client.get("/manuals/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_delete_manual():
    # First upload a manual
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
