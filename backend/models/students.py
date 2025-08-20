from models.base import BareBaseModel 

from sqlalchemy import Column , String , Integer , DateTime , ForeignKey , Enum as SQLENUM
from sqlalchemy.sql import func 
from sqlalchemy.orm import relationship

from helpers.gender_enum import GenderEnum 

class Student(BareBaseModel):
    account_id = Column(Integer, ForeignKey("account.id"), unique=True, nullable=False)

    full_name = Column(String(255), nullable=False)
    birth = Column(DateTime, nullable=False)
    gender = Column(SQLENUM(GenderEnum, name="gender_enum"), nullable=False)  
    phone = Column(String(20), unique=True, nullable=False) 
    email = Column(String(255), unique=True, nullable=False) 

    account = relationship("Account", back_populates="student")