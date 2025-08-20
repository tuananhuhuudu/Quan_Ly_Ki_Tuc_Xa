from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from core.config import settings
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database.init_db import get_db
from schemas.token import TokenData
from models.account import Account

# OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# Tạo access token
def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = {"sub": str(subject)}
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

# Giải mã token
def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]  
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Lấy user từ token
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Account:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Không thể xác thực người dùng",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)
    user_id: str = payload.get("sub")
    if not user_id:
        raise credentials_exception

    token_data = TokenData(user_id=user_id)

    account = db.query(Account).filter(Account.id == int(token_data.user_id)).first()
    if not account:
        raise credentials_exception

    return account

# Check quyền admin
def admin_required(current_account: Account = Depends(get_current_user)) -> Account:
    if current_account.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không đủ thẩm quyền để truy cập"
        )
    return current_account
