from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.init_db import get_db
from fastapi.responses import JSONResponse

from schemas.room import RoomCreate, RoomUpdate
from models.room import Room
from models.account import Account
from services.auth import admin_required

router = APIRouter(
    prefix="/rooms",
    tags=["Room"]
)

@router.get("/")
def get_rooms(db: Session = Depends(get_db)):
    rooms = db.query(Room).filter(Room.active == True).all()
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": "Lấy tất cả các phòng thành công",
            "payload": {
                "rooms": [
                    {
                        "id": room.id,
                        "room_code": room.room_code,
                        "capacity": room.capacity,
                        "price": room.price,
                        "active": room.active
                    }
                    for room in rooms
                ]
            }
        }
    )

@router.get("/{room_id}")
def get_room_id(
    room_id: int,
    db: Session = Depends(get_db),
):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
        )
    return room

# Tạo phòng mới 
@router.post("/")
def create_room(
    data: RoomCreate,
    db: Session = Depends(get_db),
    current_user: Account = Depends(admin_required)
):
    new_room = Room(
        room_code=data.room_code,
        capacity=data.capacity,
        price=data.price,
        active=True
    )
    db.add(new_room)
    db.commit()
    db.refresh(new_room)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": "Tạo phòng mới thành công",
            "payload": {
                "room": {
                    "id": new_room.id,
                    "room_code": new_room.room_code,
                    "capacity": new_room.capacity,
                    "price": new_room.price,
                    "active": new_room.active
                }
            }
        }
    )
  
# Cập nhập phòng 
@router.put("/{room_id}")
def update_room(
    room_id: int,
    room_update: RoomUpdate,
    db: Session = Depends(get_db),
    current_user: Account = Depends(admin_required)
):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "success": False,
                "message": "Phòng không tồn tại"
            }
        )
  
    for field, value in room_update.dict(exclude_unset=True).items():
        setattr(room, field, value)
  
    db.commit()
    db.refresh(room)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": "Cập nhật phòng thành công",
            "payload": {
                "room": {
                    "id": room.id,
                    "room_code": room.room_code,
                    "capacity": room.capacity,
                    "price": room.price,
                    "active": room.active
                }
            }
        }
    )


@router.patch("/{room_id}/active")
def update_room_active(
    room_id: int,
    active: bool,
    db: Session = Depends(get_db),
    current_user: Account = Depends(admin_required)
):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "success": False,
                "message": "Phòng không tồn tại"
            }
        )
    room.active = active
    db.commit()
    db.refresh(room)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "message": "Cập nhật trạng thái phòng thành công",
            "payload": {
                "room": {
                    "id": room.id,
                    "room_code": room.room_code,
                    "capacity": room.capacity,
                    "price": room.price,
                    "active": room.active
                }
            }
        }
    )
