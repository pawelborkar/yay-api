# This file contains all the information regarding database connection.
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .config import get_settings

engine = create_engine(get_settings().db_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False,  autoflush=False, bind=engine)

# declarative_baseq returns the class which connects the sqlalchemy functionality of the models. 
# We'll use this class in our models.py
Base = declarative_base()
