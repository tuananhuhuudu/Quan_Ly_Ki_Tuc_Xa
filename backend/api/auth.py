from typing import * 

from jose import jwt , JWTError 
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm , OAuth2PasswordBearer
from fastapi import APIRouter , Depends , status , HTTPException
from database.init_db import get_db 
from fastapi.responses import JSONResponse 

from models.account import Account
from schemas.account import AccountCreate 

from services.auth import create_access_token , get_current_user , admin_required 

router = APIRouter()

@router.post("/register")
def register(
    data: AccountCreate,
    db: Session = Depends(get_db)
):
    try:
        status_code, account, student = Account.create_account(db, data)

        return JSONResponse(
            status_code=status_code,
            content={
                "success": True if status_code == 201 else False,
                "message": "Đăng kí tài khoản thành công" if status_code == 201 else "Tên đăng nhập đã tồn tại",
                "payload": {
                    "account": {"username": account.username} if status_code == 201 else None,
                    "student": {
                      "id" : student.id ,
                      "name" : student.full_name , 
                      "birth" : student.birth.strftime("%Y-%m-%d"),
                      "gender" : student.gender , 
                      "phone" : student.phone ,
                      "email" : student.email
                      } if status_code == 201 else None
                }
            }
        )

    except Exception as e:
        db.rollback()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": "Đã xảy ra lỗi khi đăng ký người dùng",
                "error": str(e)
            }
        )
        
@router.post("/login")
def login(
    form_data : OAuth2PasswordRequestForm = Depends(),
    db : Session = Depends(get_db)
):
    status_code , account = Account.authenticate(db , form_data.username , form_data.password)
    if status_code != 200 : 
        raise HTTPException(
            status_code=status_code , 
            detail="Tên đăng nhập hoặc tài khoản không chính xác",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(subject=str(account.id))

    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content = {
            "success" : True , 
            "message" : "Đăng nhập thành công" ,
            "access_token": access_token,
            "token_type": "bearer",
        }
    )


    

@router.get("/me")
def read_me(
    current_user : Account = Depends(get_current_user)
): 
    return JSONResponse(
        status_code=status.HTTP_200_OK, 
        content={
            "success" : True , 
            "message" : "Thông tin người dùng",
            "payload" : {
                "id" : current_user.id ,
                "username" : current_user.username , 
                "role" : current_user.role
            }
        }
    )


