from sqlalchemy import Column , Integer , ForeignKey , DateTime , String 

from sqlalchemy.ext.declarative import as_declarative , declared_attr 
from sqlalchemy.sql import func 

@as_declarative
class Base : 
  __attract__ = True 
  __name__ : str 
  
  @declared_attr
  def __tablename__(cls):
    return cls.__name__.lower()
  
class BareBaseModel(Base):
  __abtract__ = True 
  
  id = Column(Integer , primary_key=True , autoincrement= True)
  