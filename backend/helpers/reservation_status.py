from enum import Enum 

from pydantic import BaseModel 

class ReservationStatus(str , Enum):
  pending = "pending"
  approved = "approved"
  rejected = "rejected"

