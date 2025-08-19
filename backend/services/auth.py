from jose import JWTError , jwt 
from datetime import datetime , timedelta 
from typing import Optional 
from core.config import settings
from fastapi import FastAPI , HTTPException , status , Depends
from fastapi.security import OAuth2PasswordBearer , OAuth2PasswordRequestForm

from database.init_db import get_db 
from sqlalchemy.orm import Session
from schemas.token import TokenData
from models.account import Account

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")

def create_access_token(subject : dict , expires_delta : Optional[timedelta] = None):
  to_encode = subject.copy()
  expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
  to_encode.update({"exp" : expire})
  return jwt.encode(to_encode , settings.SECRET_KEY , algorithm= settings.ALGORITHM)
  
def decode_token(token : str) -> dict : 
  try : 
    payload = jwt.decode(token , settings.SECRET_KEY , settings.ALGORITHM)
    return payload
  except JWTError:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Token không hợp lệ",
      headers={"WWW-Authenticate": "Bearer"},
      )

def get_current_user(
  token : str = Depends(oauth2_scheme),
  db : Session = Depends(get_db)
) : 
  credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
  )
  try : 
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.SECURITY_ALGORITHM])
    user_id: str = payload.get("sub")
    if user_id is None:
      raise credentials_exception
    token_data = TokenData(user_id=user_id)
  except JWTError as err:
    raise credentials_exception
  
  account = db.query(Account).filter(account.id == token_data.id).first()
  if account is None : 
    raise credentials_exception
  
  return account 

def admin_required(curent_account : Account = Depends(get_current_user)):
  if curent_account.role != "admin":
    raise HTTPException(
      status_code=status.HTTP_403_FORBIDDEN,
      detail="Bạn không đủ thẩm quyển để truy cập"
    )
  return curent_account 
