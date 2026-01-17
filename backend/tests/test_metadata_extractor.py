import pytest
from unittest.mock import MagicMock, patch
from services.metadata_extractor import MetadataExtractor

@pytest.fixture
def extractor():
    return MetadataExtractor()

def test_find_brand(extractor):
    text = "This is a User Manual for a Sony television."
    assert extractor._find_brand(text) == "Sony"

    text_no_brand = "This is a generic manual."
    assert extractor._find_brand(text_no_brand) is None

    text_case = "operating instructions for samsung galaxy."
    assert extractor._find_brand(text_case) == "Samsung"

def test_find_model(extractor):
    text = "Model: WH-1000XM4"
    assert extractor._find_model(text) == "WH-1000XM4"

    text_mn = "M/N: XPS-13-9310"
    assert extractor._find_model(text_mn) == "XPS-13-9310"
    
    text_implicit = "Setup Guide for AB1234XYZ"
    # Matches the alphanumeric heuristic
    assert extractor._find_model(text_implicit) == "AB1234XYZ"

@patch("services.metadata_extractor.PdfReader")
def test_extract_from_pdf(mock_pdf_reader, extractor):
    # Mock PDF content
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "User Manual\nSony Corporation\nModel: BRAVIA-XR"
    
    mock_reader_instance = MagicMock()
    mock_reader_instance.pages = [mock_page]
    mock_reader_instance.__len__.return_value = 1
    mock_pdf_reader.return_value = mock_reader_instance

    brand, model = extractor.extract("dummy_path.pdf")
    
    assert brand == "Sony"
    assert model == "BRAVIA-XR"

