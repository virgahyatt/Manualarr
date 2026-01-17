import pytest
from unittest.mock import MagicMock, patch
from services.discovery_service import DiscoveryService

@pytest.fixture
def discovery():
    return DiscoveryService()

@patch("services.discovery_service.search_items")
@patch("services.discovery_service.get_item")
def test_search(mock_get_item, mock_search_items, discovery):
    # Mock search results
    mock_search_items.return_value = [{'identifier': 'test-item'}]
    
    # Mock item details
    mock_item = MagicMock()
    mock_item.metadata = {'title': 'Test Manual', 'collection': 'manuals'}
    mock_item.files = [{'name': 'manual.pdf', 'size': 1024}]
    mock_get_item.return_value = mock_item
    
    results = discovery.search("TestBrand", "TestModel")
    
    assert len(results) == 1
    assert results[0]['title'] == 'Test Manual'
    assert results[0]['filename'] == 'manual.pdf'
    assert results[0]['url'] == 'https://archive.org/download/test-item/manual.pdf'

@patch("services.discovery_service.requests.get")
def test_download(mock_get, discovery):
    mock_response = MagicMock()
    mock_response.iter_content.return_value = [b"chunk1", b"chunk2"]
    mock_get.return_value = mock_response
    
    # Use a temp file path
    dest = "test_download.pdf"
    try:
        success = discovery.download("http://example.com/manual.pdf", dest)
        assert success
        with open(dest, "rb") as f:
            content = f.read()
            assert content == b"chunk1chunk2"
    finally:
        import os
        if os.path.exists(dest):
            os.remove(dest)
