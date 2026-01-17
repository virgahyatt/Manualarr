import pytest
from unittest.mock import MagicMock, patch
from services.metadata_extractor import MetadataExtractor

@pytest.fixture
def extractor():
    return MetadataExtractor()

def test_find_brand(extractor):
    text = "This is a User Manual for a Sony television."
    assert extractor._find_brand(text) == "Sony"

    text_eco = "ECO-WORTHY LiFePO4 Battery Manual"
    assert extractor._find_brand(text_eco) == "ECO-WORTHY"

def test_find_model(extractor):
    text = "Model: WH-1000XM4"
    assert extractor._find_model(text) == "WH-1000XM4"

    # Plural Models
    text_models = "MODELS E1-E2-E3"
    assert extractor._find_model(text_models) == "E1-E2-E3"

    # Dirty text case (simulated from pypdf output)
    # Using explicit newline char
    text_dirty = "čModel\nCO-LFP4810002Ď"
    assert extractor._find_model(text_dirty) == "CO-LFP4810002"

    text_eco = "（Model: ECO-LFP4810002）"
    assert extractor._find_model(text_eco) == "ECO-LFP4810002"

    text_fw_colon = "Model： ECO-LFP4810002"
    assert extractor._find_model(text_fw_colon) == "ECO-LFP4810002"
    
    text_duplicate = "ECO-WORTHY LiFePO4 Battery"
    assert extractor._find_model(text_duplicate, exclude="ECO-WORTHY") is None

@patch("services.metadata_extractor.PdfReader")
def test_extract_from_pdf(mock_pdf_reader, extractor):
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "User Manual\nECO-WORTHY\nModel: ECO-LFP4810002"
    
    mock_reader_instance = MagicMock()
    mock_reader_instance.pages = [mock_page]
    mock_reader_instance.__len__.return_value = 1
    mock_pdf_reader.return_value = mock_reader_instance

    brand, model = extractor.extract("dummy_path.pdf")
    
    assert brand == "ECO-WORTHY"
    assert model == "ECO-LFP4810002"