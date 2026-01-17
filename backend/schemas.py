from pydantic import BaseModel, ConfigDict

class ManualBase(BaseModel):
    brand: str
    model: str

class ManualCreate(ManualBase):
    pass

class Manual(ManualBase):
    id: int
    filename: str
    filepath: str

    model_config = ConfigDict(from_attributes=True)