from pydantic import BaseModel ,model_validator
from typing import Optional

class RoomCreate(BaseModel):
  room_code: str
  capacity: int
  price: float

class RoomUpdate(BaseModel):
  room_code: Optional[str]
  capacity: Optional[int]
  current_occupancy: Optional[int]
  price: Optional[float]
  active: Optional[bool]  
  
  @model_validator(mode="after")
  def check_occupancy_update(self):
    if self.current_occupancy > self.capacity : 
        raise ValueError("current_occupancy không được lớn hơn capacity")
    return self
  