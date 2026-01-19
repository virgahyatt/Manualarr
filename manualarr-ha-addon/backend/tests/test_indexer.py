import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from main import app, get_db
import fitz
import os
import time

client = TestClient(app)

@pytest.fixture(scope="module")
def pdf_file():
    filename = "test_index.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "This is a test manual for indexing. It contains specific keywords like Zebra and Giraffe.")
    doc.save(filename)
    yield filename
    if os.path.exists(filename):
        os.remove(filename)

def test_indexing_and_search(pdf_file):
    # 1. Upload manual
    with open(pdf_file, "rb") as f:
        response = client.post(
            "/manuals/", 
            files={"file": (pdf_file, f, "application/pdf")},
            data={"brand": "TestBrand", "model": "TestModel"}
        )
    assert response.status_code == 201
    manual_id = response.json()["id"]
    
    # Wait for background task? 
    # TestClient runs background tasks synchronously by default in recent Starlette versions?
    # No, it executes them. But indexing might take a split second.
    # We can check DB manually.
    
    # Verify index
    # We can't easily access the DB session from here without creating one.
    # We'll use the search endpoint to verify.
    
    # Search for "Zebra"
    response = client.get("/search/context?q=Zebra")
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0
    assert results[0]["manual_id"] == manual_id
    assert "Zebra" in results[0]["snippet"]
    
    # Search with filter
    response = client.get("/search/context?q=Zebra&brand=TestBrand")
    assert len(response.json()) > 0
    
    response = client.get("/search/context?q=Zebra&brand=WrongBrand")
    assert len(response.json()) == 0

    # Delete manual
    client.delete(f"/manuals/{manual_id}")
    
    # Verify search empty
    response = client.get("/search/context?q=Zebra")
    assert len(response.json()) == 0
