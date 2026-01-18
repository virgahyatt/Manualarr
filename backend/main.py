from typing import List, Optional, Dict, Any
from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException, Query, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import os
import shutil
import logging
from io import BytesIO
from urllib.parse import urlparse, unquote

from database import engine, get_db, init_fts, SessionLocal
from services.metadata_extractor import MetadataExtractor
from services.discovery_service import DiscoveryService
from services.indexer import IndexerService
from services.product_lookup import ProductLookupService
import models
import schemas

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure database directory exists if using SQLite with a path
if engine.url.drivername == 'sqlite':
    db_path = engine.url.database
    if db_path and db_path != ':memory:':
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

# Create database tables
models.Base.metadata.create_all(bind=engine)
# Initialize FTS
init_fts(engine)

app = FastAPI(title="Manualarr API")

UPLOAD_DIR = "backend/uploads"
# In Docker, this might be just "uploads" relative to WORKDIR /app
if os.path.exists("uploads"):
    UPLOAD_DIR = "uploads"
else:
    # Fallback for local dev if not running in docker or different structure
    os.makedirs(UPLOAD_DIR, exist_ok=True)

# Mount the uploads directory to serve files
app.mount("/files", StaticFiles(directory=UPLOAD_DIR), name="files")

# Initialize services
extractor = MetadataExtractor()
discovery_service = DiscoveryService()
indexer = IndexerService()
product_lookup = ProductLookupService()

@app.get("/products/lookup")
def lookup_product(barcode: str = Query(...)):
    """
    Lookup product metadata by barcode.
    """
    logger.info(f"Looking up product by barcode: {barcode}")
    brand, model = product_lookup.lookup(barcode)
    if not brand and not model:
        logger.warning(f"Product not found for barcode: {barcode}")
        raise HTTPException(status_code=404, detail="Product not found")
    logger.info(f"Product found: {brand} {model}")
    return {"brand": brand, "model": model}

@app.post("/products/scan-barcode")
async def scan_barcode(file: UploadFile = File(...)):
    """
    Scan an uploaded image for a barcode and lookup product metadata.
    """
    logger.info(f"Received image for barcode scanning: {file.filename}")
    content = await file.read()
    brand, model = product_lookup.scan_barcode(content)
    if not brand and not model:
        logger.warning(f"No barcode detected or product not found in image: {file.filename}")
        raise HTTPException(status_code=404, detail="No barcode detected or product not found")
    logger.info(f"Barcode scan successful: {brand} {model}")
    return {"brand": brand, "model": model}

@app.post("/manuals/extract-metadata")
async def extract_metadata(file: UploadFile = File(...)):
    """
    Extract metadata from an uploaded PDF without saving it permanently.
    Returns suggested brand and model.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is missing")
    
    logger.info(f"Extracting metadata from file: {file.filename}")
    
    # Read file content into memory/temp
    content = await file.read()
    file_obj = BytesIO(content)
    
    try:
        brand, model = extractor.extract(file_obj)
        logger.info(f"Metadata extracted: {brand} {model}")
        return {"brand": brand, "model": model}
    except Exception as e:
        logger.error(f"Extraction error: {e}")
        return {"brand": None, "model": None}

@app.get("/manuals/search", response_model=List[schemas.ManualSearchResult])
def search_manuals(brand: str = Query(...), model: str = Query(...)):
    """
    Search for manuals on the Internet Archive.
    """
    logger.info(f"Searching manuals for: {brand} {model}")
    return discovery_service.search(brand, model)

@app.post("/manuals/import", response_model=schemas.Manual, status_code=201)
def import_manual(request: schemas.ManualImport, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Import a manual from a URL.
    """
    logger.info(f"Importing manual from URL: {request.url}")
    # Create filename
    if request.filename:
        base_name = os.path.basename(request.filename)
    else:
        # Derive from URL
        parsed = urlparse(request.url)
        path = unquote(parsed.path)
        base_name = os.path.basename(path)
        if not base_name or not base_name.lower().endswith('.pdf'):
            base_name = "manual_download.pdf"

    name, ext = os.path.splitext(base_name)
    counter = 1
    target_filename = base_name
    while os.path.exists(os.path.join(UPLOAD_DIR, target_filename)):
        target_filename = f"{name}_{counter}{ext}"
        counter += 1
        
    dest_path = os.path.join(UPLOAD_DIR, target_filename)
    
    # Download
    success = discovery_service.download(request.url, dest_path)
    if not success:
        logger.error(f"Failed to download manual from {request.url}")
        raise HTTPException(status_code=400, detail="Failed to download manual")
    
    # Auto-extract if missing metadata
    final_brand = request.brand
    final_model = request.model
    
    if not final_brand or not final_model:
        extracted_brand, extracted_model = extractor.extract(dest_path)
        if not final_brand:
            final_brand = extracted_brand or "Unknown"
        if not final_model:
            final_model = extracted_model or "Unknown"

    # Save to DB
    db_manual = models.Manual(
        brand=final_brand,
        model=final_model,
        filename=target_filename,
        filepath=dest_path
    )
    db.add(db_manual)
    db.commit()
    db.refresh(db_manual)
    
    logger.info(f"Manual imported successfully: {db_manual.id} - {final_brand} {final_model}")
    
    # Trigger indexing
    background_tasks.add_task(indexer_task, db_manual.id, dest_path)
    
    return db_manual

@app.post("/manuals/", response_model=schemas.Manual, status_code=201)
def create_manual(
    background_tasks: BackgroundTasks,
    brand: Optional[str] = Form(None),
    model: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a new manual PDF and save metadata to the database.
    If brand/model are not provided, attempts to extract them from the PDF.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is missing")
        
    logger.info(f"Uploading manual: {file.filename}")

    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Auto-extraction if fields are missing (Fallback)
    if not brand or not model:
        extracted_brand, extracted_model = extractor.extract(file_location)
        if not brand:
            brand = extracted_brand or "Unknown"
        if not model:
            model = extracted_model or "Unknown"

    db_manual = models.Manual(
        brand=brand,
        model=model,
        filename=file.filename,
        filepath=file_location
    )
    db.add(db_manual)
    db.commit()
    db.refresh(db_manual)
    
    logger.info(f"Manual uploaded successfully: {db_manual.id} - {brand} {model}")
    
    # Trigger indexing
    background_tasks.add_task(indexer_task, db_manual.id, file_location)
    
    return db_manual

def indexer_task(manual_id: int, filepath: str):
    # Need a new DB session for background task
    db = SessionLocal()
    try:
        indexer.index_manual(db, manual_id, filepath)
    finally:
        db.close()

@app.get("/manuals/", response_model=List[schemas.Manual])
def list_manuals(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    List all manuals stored in the database.
    """
    manuals = db.query(models.Manual).offset(skip).limit(limit).all()
    return manuals

@app.delete("/manuals/{manual_id}")
def delete_manual(manual_id: int, db: Session = Depends(get_db)):
    """
    Delete a manual by ID.
    """
    manual = db.query(models.Manual).filter(models.Manual.id == manual_id).first()
    if not manual:
        raise HTTPException(status_code=404, detail="Manual not found")
    
    # Delete index
    indexer.delete_manual_index(db, manual_id)
    
    # Delete file from disk
    if os.path.exists(manual.filepath):
        try:
            os.remove(manual.filepath)
        except OSError:
            pass # Log error in production
            
    db.delete(manual)
    db.commit()
    return {"message": "Manual deleted successfully"}

@app.get("/search/context")
def search_context(
    q: str = Query(..., min_length=3),
    brand: Optional[str] = Query(None),
    model: Optional[str] = Query(None),
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Search manual content for LLM context retrieval.
    Returns snippets of matching text.
    """
    results = indexer.search(db, q, brand, model, limit)
    return results