from models.base import BareBaseModel 

from sqlalchemy import Column , Integer , String , ForeignKey , DateTime , Enum as SQLENUM , Date
from sqlalchemy.sql import func 
from sqlalchemy.orm import relationship 

from helpers.reservation_status import ReservationStatus

class Reservation(BareBaseModel):
  student_id = Column(Integer , ForeignKey("student.id") , nullable= False)
  room_id = Column(Integer , ForeignKey("room.id") , nullable = False)
  booking_date = Column(DateTime(timezone=True), server_default=func.now())
  start_date = Column(Date, nullable=False , default= None)
  status = Column(SQLENUM(ReservationStatus), default=ReservationStatus.PENDING)
  
  # Quana hệ 
  room = relationship("Room" , back_populates= "reservations")
  contract = relationship("Contract" , back_populates="reservation" , uselist= False)
  student = relationship("Student" , back_populates = "reservations")
  
