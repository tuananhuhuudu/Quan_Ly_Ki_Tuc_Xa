from fastapi import FastAPI 
from api import auth
from models.base import Base
from database.init_db import create_table_db
def create_app()->FastAPI:
  app = FastAPI()
  
  create_table_db()
  app.include_router(router=auth.router)
  
  return app 