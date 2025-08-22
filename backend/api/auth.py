from typing import Any, Dict

from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database.init_db import get_db
from models.account import Account
from schemas.account import AccountCreate
from services.auth import create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", summary="Đăng ký tài khoản mới")
def register(
    data: AccountCreate,
    db: Session = Depends(get_db)
) -> JSONResponse:
    """
    API đăng ký tài khoản mới cho sinh viên.
    - Kiểm tra username trùng.
    - Tạo mới Account + Student.
    """
    try:
        status_code, account, student = Account.create_account(db, data)

        success = status_code == 201
        message = "Đăng ký tài khoản thành công" if success else "Tên đăng nhập đã tồn tại"

        return JSONResponse(
            status_code=status_code,
            content={
                "success": success,
                "message": message,
                "payload": {
                    "account": {"username": account.username} if success else None,
                    "student": {
                        "id": student.id,
                        "name": student.full_name,
                        "birth": student.birth.strftime("%Y-%m-%d"),
                        "gender": student.gender,
                        "phone": student.phone,
                        "email": student.email,
                    } if success else None,
                },
            },
        )

    except Exception as e:
        db.rollback()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": "Đã xảy ra lỗi khi đăng ký người dùng",
                "error": str(e),
            },
        )


@router.post("/login", summary="Đăng nhập và lấy access token")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> JSONResponse:
    """
    API đăng nhập.
    - Kiểm tra username + password.
    - Trả về JWT access_token nếu thành công.
    """
    status_code, account = Account.authenticate(db, form_data.username, form_data.password)
    if status_code != 200:
        raise HTTPException(
            status_code=status_code,
            detail="Tên đăng nhập hoặc mật khẩu không chính xác",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=str(account.id))

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": "Đăng nhập thành công",
            "access_token": access_token,
            "token_type": "bearer",
        },
    )


@router.get("/me", summary="Lấy thông tin người dùng hiện tại")
def read_me(current_user: Account = Depends(get_current_user)) -> JSONResponse:
    """
    API lấy thông tin tài khoản hiện tại từ JWT token.
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": "Thông tin người dùng",
            "payload": {
                "id": current_user.id,
                "username": current_user.username,
                "role": current_user.role,
            },
        },
    )
