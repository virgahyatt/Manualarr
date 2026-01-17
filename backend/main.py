"""
Main API application for Manualarr.
"""
import os
import shutil
from typing import List
from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from database import engine, get_db
import models
import schemas

# Ensure database directory exists if using SQLite with a path
if engine.url.drivername == 'sqlite':
    db_path = engine.url.database
    if db_path and db_path != ':memory:':
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Manualarr API")

UPLOAD_DIR = "backend/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/manuals/", response_model=schemas.Manual, status_code=201)
def create_manual(
    brand: str = Form(...),
    model: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a new manual PDF and save metadata to the database.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is missing")

    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    db_manual = models.Manual(
        brand=brand,
        model=model,
        filename=file.filename,
        filepath=file_location
    )
    db.add(db_manual)
    db.commit()
    db.refresh(db_manual)
    return db_manual

@app.get("/manuals/", response_model=List[schemas.Manual])
def list_manuals(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    List all manuals stored in the database.
    """
    manuals = db.query(models.Manual).offset(skip).limit(limit).all()
    return manuals
