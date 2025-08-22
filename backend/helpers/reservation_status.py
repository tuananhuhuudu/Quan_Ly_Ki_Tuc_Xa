from enum import Enum 

from pydantic import BaseModel 

class ReservationStatus(str , Enum):
  PENDING = "pending"
  APPROVED = "approved"
  REJECTED = "rejected"

