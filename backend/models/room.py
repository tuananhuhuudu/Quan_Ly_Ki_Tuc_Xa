from models.base import BareBaseModel 

from sqlalchemy import Column , String , Integer , ForeignKey , DateTime , Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class Room(BareBaseModel):
  room_code = Column(String(255) , nullable= False)
  capacity = Column(Integer , nullable= False)
  current_occupancy = Column(Integer , nullable = False)
  price = Column(Float , nullable = False)
  
  # Quan hệ 
  reservations = relationship("Reservation" , back_populates= "room")
  