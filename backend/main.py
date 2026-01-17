import os
import shutil
from typing import List
from fastapi import FastAPI, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session

from database import engine, get_db, Base
import models
import schemas

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
    manuals = db.query(models.Manual).offset(skip).limit(limit).all()
    return manuals