from app.database.base_class import Base
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text

class Country(Base):
    __tablename__ = 'countries'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    country_code = Column(String(50), unique=True, nullable=True)
    dial_code = Column(String(50), nullable=True)
    country_flag = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    deleted_at = Column(DateTime, nullable=True)