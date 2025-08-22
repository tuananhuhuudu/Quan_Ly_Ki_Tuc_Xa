from typing import *
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database.init_db import get_db
from models.students import Student
from models.account import Account
from schemas.student import StudentUpdate
from services.auth import get_current_user

router = APIRouter(
    prefix="/students",
    tags=["Student"]
)

# ----------------- Lấy thông tin sinh viên hiện tại -----------------
@router.get("/me")
def get_info_me(
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_user)
):
    student = db.query(Student).filter(Student.account_id == current_user.id).first()
    if not student:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "success": False,
                "message": "Người dùng không tồn tại",
            }
        )
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": "Lấy thông tin người dùng thành công",
            "payload": {
                "student": {
                    "id": student.id,
                    "full_name": student.full_name,
                    "birth": student.birth.strftime("%Y-%m-%d") if student.birth else None,
                    "gender": student.gender,
                    "phone": student.phone,
                    "email": student.email
                }
            }
        }
    )

# ----------------- Cập nhật thông tin sinh viên hiện tại -----------------
@router.patch("/me")
def update_my_profile(
    data: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_user)
):
    student = db.query(Student).filter(Student.account_id == current_user.id).first()
    if not student:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "success": False,
                "message": "Người dùng không tồn tại",
            }
        )
    
    # Cập nhật các field được gửi
    for key, value in data.dict(exclude_unset=True).items():
        setattr(student, key, value)
    
    db.commit()
    db.refresh(student)
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": "Cập nhật thông tin thành công",
            "payload": {
                "student": {
                    "id": student.id,
                    "full_name": student.full_name,
                    "birth": student.birth.strftime("%Y-%m-%d") if student.birth else None,
                    "gender": student.gender,
                    "phone": student.phone,
                    "email": student.email
                }
            }
        }
    )
