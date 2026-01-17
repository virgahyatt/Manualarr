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

    text_eco = "（Model: ECO-LFP4810002）"
    assert extractor._find_model(text_eco) == "ECO-LFP4810002"

    text_fw_colon = "Model： ECO-LFP4810002"
    assert extractor._find_model(text_fw_colon) == "ECO-LFP4810002"
    
    text_duplicate = "ECO-WORTHY LiFePO4 Battery"
    assert extractor._find_model(text_duplicate, exclude="ECO-WORTHY") is None

@patch("services.metadata_extractor.pymupdf")
def test_extract_from_pdf(mock_pymupdf, extractor):
    mock_page = MagicMock()
    mock_page.get_text.return_value = "User Manual\nECO-WORTHY\nModel: ECO-LFP4810002"
    
    mock_doc = MagicMock()
    mock_doc.__getitem__.return_value = mock_page
    mock_doc.__len__.return_value = 1
    
    mock_pymupdf.open.return_value = mock_doc

    brand, model = extractor.extract("dummy_path.pdf")
    
    assert brand == "ECO-WORTHY"
    assert model == "ECO-LFP4810002"
