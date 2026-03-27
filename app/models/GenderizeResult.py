from app.database import Base
from sqlalchemy import Column, Integer, String, Enum as SqlEnum
from app.enums.GenderEnum import GenderEnum

class GenderizeResult(Base):
    __tablename__ = "genderize_results"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    gender = Column(SqlEnum(GenderEnum), nullable=False)
    probability = Column(Integer, nullable=False) 
    source = Column(String, nullable=False) # api or dataset

    def to_dict(self):
        return {
            "name": self.name,
            "gender": self.gender.value,
            "probability": self.probability,
            "source": self.source
        }