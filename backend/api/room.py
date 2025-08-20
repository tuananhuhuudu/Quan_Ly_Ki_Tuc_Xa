from fastapi import APIRouter , Depends , HTTPException  , status
from sqlalchemy.orm import Session
from database.init_db import get_db 
from fastapi.responses import JSONResponse

from schemas.room import RoomCreate , RoomUpdate
from models.room import Room
from models.account import Account 

router = APIRouter()

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
                        "current_occupancy": room.current_occupancy,
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
  room_id : int ,
  db : Session = Depends(get_db),
):
  room = db.query(Room).filter(Room.id == room_id).first()
  if not room : 
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND
    )
  return room
# Tạo phòng mới 
@router.post("/")
def create_room(
  data : RoomCreate ,
  db : Session = Depends(get_db)
):
  new_room = Room(
    room_code = data.room_code,
    capacity = data.capacity,
    price = data.price,
    current_occupancy = data.capacity,
    active = True
  )
  db.add(new_room)
  db.commit()
  db.refresh(new_room)
  return JSONResponse(
    status_code=status.HTTP_200_OK , 
    content = {
      "success" : True , 
      "message" : "Tạo phòng mới thành công",
      "payload" : {
        "room" : {
          "id" : new_room.id , 
          "room_code" : new_room.room_code , 
          "capacity" : new_room.capacity,
          "current_occupancy" : new_room.current_occupancy , 
          "price" : new_room.price ,
          "active" : new_room.active 
        }
      }
    }
  )
  
# Cập nhập phòng 
@router.put("/{room_id}")
def update_room(
  room_id : int , 
  room_update : RoomUpdate ,
  db : Session = Depends(get_db)
):
  room = db.query(Room).filter(Room.id == room_id).first()
  if not room:
      raise HTTPException(status_code=404, detail="Room not found")
  
  for field, value in room_update.dict(exclude_unset=True).items():
      setattr(room, field, value)
  
  # Kiểm tra lại occupancy <= capacity
  if room.current_occupancy > room.capacity:
      raise HTTPException(status_code=400, detail="current_occupancy không được lớn hơn capacity")
  
  db.commit()
  db.refresh(room)
  return room


@router.patch("/{room_id}/active")
def update_room_active(room_id: int, active: bool, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    room.active = active
    db.commit()
    db.refresh(room)
    return room