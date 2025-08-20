import os 
from typing import * 

from fastapi import APIRouter , Depends , status , HTTPException
from database.init_db import get_db 
from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session

from models.students import Student 
from models.account import Account
from schemas.student import StudentUpdate , StudentResponse
from services.auth import get_current_user

router = APIRouter()

@router.get("/info")
def get_info_me(
  db : Session = Depends(get_db),
  current_user : Account = Depends(get_current_user)
):
  user_info = db.query(Student).filter(current_user.id == Student.account_id).first()
  if not user_info : 
    return JSONResponse(
      status_code=status.HTTP_404_NOT_FOUND,
      content = {
        "success" : False , 
        "message" : "Người dùng không tồn tại",
      }
    )
  
  return JSONResponse(
    status_code= status.HTTP_200_OK , 
    content = {
      "success" : True , 
      "message" : "Lấy thông tin người dùng thành công" , 
      "payload" : {
        "student" : {
          "id" : user_info.id ,
          "full_name" : user_info.full_name,
          "birth" : user_info.birth.strftime("%Y-%m-%d"),
          "gender" : user_info.gender,
          "phone" : user_info.phone , 
          "email" : user_info.email 
        }
      }
    }
  )

@router.patch("/me/student")
def update_my_profile(
  data : StudentUpdate,
  db : Session = Depends(get_db),
  current_user : Account = Depends(get_current_user)
): 
  student = db.query(Student).filter(Student.account_id == current_user.id).first()
  if not student : 
    return JSONResponse(
    status_code=status.HTTP_404_NOT_FOUND,
    content = {
      "success" : False , 
      "message" : "Người dùng không tồn tại",
    }
  )
    
  
  for key, value in data.dict(exclude_unset=True).items():
    setattr(student, key, value)
  
  db.commit()
  db.refresh(student)
  return JSONResponse(
    status_code=status.HTTP_200_OK , 
    content = {
      "success" : True ,
      "message" : "Cập nhập thông tin thành công",
      "payload" : {
        "student" : {
          "id" : student.id , 
          "fullname" : student.full_name,
          "birth" : student.birth.strftime("%Y-%m-%d"),
          "gender" : student.gender , 
          "phone" : student.phone ,
          "email" : student.email
        }
      }
    }
  )