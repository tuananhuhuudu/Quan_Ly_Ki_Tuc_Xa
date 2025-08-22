from fastapi import FastAPI 
from models.base import Base
from database.init_db import create_table_db

from api import auth
from api import student
from api import room
from api import reservation_contact
from api import invoice
def create_app()->FastAPI:
  app = FastAPI()
  
  create_table_db()
  app.include_router(router=auth.router)
  app.include_router(router=student.router)
  app.include_router(router=room.router)
  app.include_router(router=reservation_contact.router)
  app.include_router(router=invoice.router)
  return app 