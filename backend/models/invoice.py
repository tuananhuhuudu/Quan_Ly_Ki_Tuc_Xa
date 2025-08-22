from models.base import BareBaseModel 

from sqlalchemy import Column , Integer , String , DateTime , ForeignKey , Enum as SQLENUM , Text , Float
from sqlalchemy.sql import func 
from sqlalchemy.orm import relationship 

from helpers.invoice_status import InvoiceStatus 

class Invoice(BareBaseModel):
    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contract.id"), nullable=False)
    amount = Column(Float, nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    status = Column(SQLENUM(InvoiceStatus, name="invoice_status"), default=InvoiceStatus.UNPAID)
    created_at = Column(DateTime, server_default=func.now())
    paid_at = Column(DateTime, nullable=True)
    
    #Quan hệ
    contract = relationship("Contract", back_populates="invoices")

