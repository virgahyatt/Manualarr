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


class Manual(ManualBase):
    """
    Schema for reading Manual data.
    """
    id: int
    brand: str # Enforce str in response
    model: str # Enforce str in response
    filename: str
    filepath: str

    model_config = ConfigDict(from_attributes=True)