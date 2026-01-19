import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app

client = TestClient(app)

def test_scan_barcode_no_barcode():
    # Test with an image that has no barcode
    with patch("services.product_lookup.decode", return_value=[]):
        with patch("services.product_lookup.Image.open", return_value=MagicMock()):
            response = client.post(
                "/products/scan-barcode",
                files={"file": ("test.jpg", b"fake-image-content", "image/jpeg")}
            )
            assert response.status_code == 404
            assert response.json()["detail"] == "No barcode detected in the image."

def test_scan_barcode_success():
    # Mock barcode detection and product lookup
    mock_barcode = MagicMock()
    mock_barcode.data.decode.return_value = "123456789012"
    mock_barcode.type = "EAN13"
    
    mock_product_info = ("Sony", "WH-1000XM4")
    
    with patch("services.product_lookup.decode", return_value=[mock_barcode]):
        with patch("services.product_lookup.Image.open", return_value=MagicMock()):
            with patch("services.product_lookup.ProductLookupService.lookup", return_value=mock_product_info):
                response = client.post(
                    "/products/scan-barcode",
                    files={"file": ("test.jpg", b"fake-image-content", "image/jpeg")}
                )
                assert response.status_code == 200
                assert response.json() == {"brand": "Sony", "model": "WH-1000XM4", "barcode": "123456789012"}

def test_scan_barcode_only_barcode_no_product():
    # Mock barcode detection but lookup fails
    mock_barcode = MagicMock()
    mock_barcode.data.decode.return_value = "123456789012"
    mock_barcode.type = "EAN13"
    
    with patch("services.product_lookup.decode", return_value=[mock_barcode]):
        with patch("services.product_lookup.Image.open", return_value=MagicMock()):
            with patch("services.product_lookup.ProductLookupService.lookup", return_value=(None, None)):
                response = client.post(
                    "/products/scan-barcode",
                    files={"file": ("test.jpg", b"fake-image-content", "image/jpeg")}
                )
                assert response.status_code == 200
                assert response.json() == {"brand": None, "model": None, "barcode": "123456789012"}

def test_scan_barcode_invalid_image():
    # Test with invalid image data
    with patch("services.product_lookup.Image.open", side_effect=Exception("Invalid image")):
        response = client.post(
            "/products/scan-barcode",
            files={"file": ("test.jpg", b"invalid-content", "image/jpeg")}
        )
        assert response.status_code == 404
