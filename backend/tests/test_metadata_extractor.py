import pytest
from unittest.mock import MagicMock, patch
from services.metadata_extractor import MetadataExtractor

@pytest.fixture
def extractor():
    return MetadataExtractor()

def test_ocr_reproduction(extractor):
    # Text provided by user from the OCR of the problematic PDF
    ocr_text = """
    51.2V 100AH LIFEPO4 
    BATTERY 3U
    MANUAL
    Operation and Maintenance
    LiFePO4
    Manual Version: 3.1.1
    SUPPORT
    If you are experiencing technical problems and cannot find 
    a solution in this manual,please contact ECO-WORTHY for 
    further assistance.
    ·Call:+1 866-939-8222(US&CA)
    +49 6175-6514-999(DE)
    +44 7553-406-988(UK)
    ·Web://www.eco-worthy.com/
    ·E-mail: customer.service@eco-worthy.com
    （Model: ECO-LFP4810002）
    V3
    """
    
    brand, model = extractor._analyze_text(ocr_text)
    
    assert brand == "ECO-WORTHY"
    assert model == "ECO-LFP4810002"

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