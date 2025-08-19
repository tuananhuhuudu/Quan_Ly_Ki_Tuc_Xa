from typing import Optional
from pydantic import BaseModel 
from schemas.student import StudentCreate
class AccountBase(BaseModel):
  username : str 
  
class AccountCreate(AccountBase):
  password : str 
  student : StudentCreate

class UpdateAccount(BaseModel):
  password : str 