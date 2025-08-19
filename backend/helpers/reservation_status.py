from enum import Enum 

from pydantic import BaseModel 

class ReservationStatus(str , Enum):
  Pending = "pending"
  Approved = "approved"
  Rejected = "rejected"

