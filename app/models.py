# This file describes the content that should be stored into the database.
from sqlalchemy import Boolean, Column, Integer, String

from .database import Base


# Creates a Database model with the name URL
class URL(Base):
    __tablename__ = "urls"

    # If primary_key=True unique is also sets to True
    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, index=True)
    secret_key = Column(String, unique=True, index=True)
    target_url = Column(String, index=True)
    is_active = Column(Boolean, default=True)
    clicks = Column(Integer, default=0)
