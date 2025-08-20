from pydantic import BaseModel 
from datetime import date
from typing import Optional

class ReservationCreate(BaseModel):
  room_id : int 
  start_date : date 
  end_date : date 