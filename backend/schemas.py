"""
Pydantic schemas for API data validation and serialization.
"""
from pydantic import BaseModel, ConfigDict

class ManualBase(BaseModel):
    """
    Base schema for Manual data.
    """
    brand: str
    model: str

class ManualCreate(ManualBase):
    """
    Schema for creating a new Manual.
    """


class Manual(ManualBase):
    """
    Schema for reading Manual data.
    """
    id: int
    filename: str
    filepath: str

    model_config = ConfigDict(from_attributes=True)
