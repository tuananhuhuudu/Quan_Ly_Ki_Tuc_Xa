# from models.base import BareBaseModel 

# from sqlalchemy import Column , Integer , String , DateTime , ForeignKey , Enum as SQLENUM , Text , Float
# from sqlalchemy.sql import func 
# from sqlalchemy.orm import relationship 

# from helpers.invoice_status import InvoiceStatus 

# class Invoice(BareBaseModel):
#   contract_id = Column(Integer , ForeignKey("contract.id") , nullable= False)
#   description = Column(Text , nullable= True)
#   amount = Column(Float , nullable=False)
#   due_date = Column(DateTime , nullable= False)
#   is_paid = Column(SQLENUM(InvoiceStatus , name = "invoice_date") , nullable= False)
#   paid_date = Column(DateTime , nullable= False)
  
#   # Quan hệ 
#   pass 

