from sqlalchemy import Column, Integer, String
from database import Base

class Manual(Base):
    __tablename__ = "manuals"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String, index=True)
    model = Column(String, index=True)
    filename = Column(String)
    filepath = Column(String)
