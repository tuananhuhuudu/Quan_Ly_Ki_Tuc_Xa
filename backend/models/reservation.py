# from models.base import BareBaseModel 

# from sqlalchemy import Column , Integer , String , ForeignKey , DateTime , Enum as SQLENUM
# from sqlalchemy.sql import func 
# from sqlalchemy.orm import relationship 

# from helpers.reservation_status import ReservationStatus

# class Reservation(BareBaseModel):
#   student_id = Column(Integer , ForeignKey("student.id") , nullable= False)
#   room_id = Column(Integer , ForeignKey("room.id") , nullable = False)
#   request_date = Column(DateTime , nullable= False)
#   status = Column(SQLENUM(ReservationStatus , name = "reservation_status") , nullable= False)
  
#   # Quan hệ 
#   room = relationship("Room" , back_populates= "reservations")
  
  
