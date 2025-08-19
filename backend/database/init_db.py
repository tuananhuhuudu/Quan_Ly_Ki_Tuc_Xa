from typing import * 

from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker 

from core.config import settings 
from models.base import Base 

engine = create_engine(settings.DATABASE_URL , pool_pre_ping=True)

SessionLocal = sessionmaker(autoflush= False , autocommit = False , bind = engine)
def create_table_db():
  return Base.metadata.create_all(bind = engine)

def get_db() -> Generator : 
  try : 
    db = SessionLocal()
    yield db 
  finally : 
    db.close()
    
