from typing import Union , Optional
from pydantic import BaseModel , EmailStr
from datetime import date , datetime

from helpers.gender_enum import GenderEnum


class StudentCreate(BaseModel):
  full_name : str 
  birth : date
  gender : GenderEnum
  phone : str 
  email : EmailStr
  
class StudentResponse(StudentCreate):
  id : int
  class Config : 
    from_attributes = True

class StudentUpdate(BaseModel):
    full_name: Optional[str] = None
    birth: Optional[date] = None
    gender: Optional[GenderEnum] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
  