import os
import importlib
import pytest
from fastapi.testclient import TestClient
import shutil

def test_upload_dir_env_var(tmp_path):
    # Set the environment variable
    custom_dir = tmp_path / "custom_uploads"
    os.environ["UPLOAD_DIR"] = str(custom_dir)
    
    # Force reload of the main module to pick up the new env var
    import main
    importlib.reload(main)
    
    assert main.UPLOAD_DIR == str(custom_dir)
    assert os.path.exists(custom_dir)
    
    # Cleanup env var for other tests
    del os.environ["UPLOAD_DIR"]

def test_database_url_env_var(tmp_path):
    custom_db = tmp_path / "test_custom.db"
    db_url = f"sqlite:///{custom_db}"
    os.environ["DATABASE_URL"] = db_url
    
    import database
    importlib.reload(database)
    
    assert str(database.engine.url) == db_url
    
    # Cleanup
    del os.environ["DATABASE_URL"]

def test_log_level_env_var():
    os.environ["LOG_LEVEL"] = "DEBUG"
    import main
    importlib.reload(main)
    assert main.LOG_LEVEL == "DEBUG"
    del os.environ["LOG_LEVEL"]

def test_max_search_results_env_var():
    os.environ["MAX_SEARCH_RESULTS"] = "25"
    import main
    importlib.reload(main)
    assert main.MAX_SEARCH_RESULTS == 25
    del os.environ["MAX_SEARCH_RESULTS"]
