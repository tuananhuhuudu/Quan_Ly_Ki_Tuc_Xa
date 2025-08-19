from models.base import BareBaseModel

from sqlalchemy import Column , String , Integer ,DateTime ,ForeignKey , Enum as SQLENUM
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from helpers.user_role import UserRole

from schemas.account import AccountCreate 
from models.students import Student
from helpers.pwd import hash_password , verify_password

class Account(BareBaseModel):
  username = Column(String(255) , nullable= False)
  password = Column(String(255) , nullable= False)
  role = Column(SQLENUM(UserRole, name="user_role_enum"), nullable=False, default=UserRole.STUDENT)
  created_at = Column(DateTime(timezone=True), server_default=func.now())
  updated_at = Column(DateTime(timezone=True), onupdate=func.now())
  
  ## Quan hệ 
  student = relationship("Student" , back_populates = "account")
  
  @staticmethod
  def create_account(db , data : AccountCreate):
    check_account = db.query(Account).filter(Account.username == data.username).first()
    
    if check_account : 
      return 409 , None 
    
    else : 
      data.password = hash_password(data.password)
      account = Account(
        username = data.username , 
        password = data.password ,
        role = UserRole.STUDENT
      )
      db.add(account)
      db.commit()
      db.refresh(account)
      
      # Tạo student liên kết với account 
      student_data = data.student 
      student = Student(
        full_name = student_data.full_name ,
        birth=student_data.birth,
        gender=student_data.gender,
        phone=student_data.phone,
        email=student_data.email,
        account_id=account.id
      )
      db.add(student)
      db.commit()
      db.refresh(student)
    return 201 , account 
  
  @staticmethod 
  def authenticate(db , username : str , password : str) : 
    account = db.query(Account).filter(Account.username == username).first()
    if not account or not verify_password(password, account.password):
      return 401 , None 
    
    return 200 , account 
  
  