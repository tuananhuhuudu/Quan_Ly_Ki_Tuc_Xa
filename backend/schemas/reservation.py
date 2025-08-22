from pydantic import BaseModel 
from datetime import date
from typing import Optional

class ReservationCreate(BaseModel):
  room_id : int 
  booking_date : date 
  
class ChangeRoomRequest(BaseModel):
  new_room_id: int