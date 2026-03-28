from app.extensions import Base
from sqlalchemy import Column, Integer, Float, String, Enum as SqlEnum
from app.enums.GenderEnum import GenderEnum

class Setting(Base):
    __tablename__ = "settings"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, nullable=False)
    value = Column(String, nullable=False)