from fastapi import APIRouter , Depends , HTTPException 
from sqlalchemy.orm import Session
from database.init_db import get_db 

from models.students import Student 
from models.reservation import Reservation
from models.contract import Contract
from models.account import Account

from services.auth import get_current_user

from schemas.reservation import ReservationCreate

router = APIRouter()

