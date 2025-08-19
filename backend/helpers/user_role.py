from enum import Enum 

from pydantic import BaseModel

class UserRole(str , Enum):
  STUDENT = "student"
  ADMIN = "admin"
  
