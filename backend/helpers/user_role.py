from enum import Enum 

from pydantic import BaseModel

class UserRole(str , Enum):
  user = "student"
  admin = "admin"
  
