# from models.base import BareBaseModel 

# from sqlalchemy import Column , Integer , String , DateTime , ForeignKey , Enum as SQLENUM 
# from sqlalchemy.sql import func 
# from sqlalchemy.orm import relationship 

# from helpers.contract_status import ContractStatus 

# class Contract(BareBaseModel):
#   reservation_id = Column(Integer , ForeignKey("reservation.id") , nullable= False)
#   student_id = Column(Integer , ForeignKey("student.id") , nullable= False)
#   start_date = Column(DateTime , nullable= False)
#   end_date = Column(DateTime , nullable= False)
#   status = Column(SQLENUM(ContractStatus , name = "contract_status") , nullable= False)
  