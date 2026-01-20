"""
Pydantic schemas for API data validation and serialization.
"""
from typing import Optional
from pydantic import BaseModel, ConfigDict

class ManualBase(BaseModel):
    """
    Base schema for Manual data.
    """
    brand: Optional[str] = None
    model: Optional[str] = None

class ManualCreate(ManualBase):
    """
    Schema for creating a new Manual.
    """


class ManualUpdate(BaseModel):
    """
    Schema for updating a Manual.
    """
    brand: Optional[str] = None
    model: Optional[str] = None
    filename: Optional[str] = None


class Manual(ManualBase):
    """
    Schema for reading Manual data.
    """
    id: int
    brand: str
    model: str
    filename: str
    filepath: str

    model_config = ConfigDict(from_attributes=True)

class ManualSearchResult(BaseModel):
    """
    Result from external manual search.
    """
    source: str
    title: str
    identifier: str
    filename: str
    url: str
    size: int

class ManualImport(BaseModel):
    """
    Request to import a manual from a URL.
    """
    brand: Optional[str] = None
    model: Optional[str] = None
    url: str
    filename: Optional[str] = None # Optional, can be derived from URL

class SearchQuery(BaseModel):
    """
    Search parameters for manual content.
    """
    q: str
    brand: Optional[str] = None
    model: Optional[str] = None
    limit: int = 10