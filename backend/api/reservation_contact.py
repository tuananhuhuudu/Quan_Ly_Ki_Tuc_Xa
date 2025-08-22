from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Body, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, joinedload
from datetime import date, datetime, timedelta

from database.init_db import get_db
from models.students import Student
from models.reservation import Reservation
from models.account import Account
from models.room import Room
from models.contract import Contract
from services.auth import get_current_user, admin_required
from helpers.reservation_status import ReservationStatus
from helpers.contract_status import ContractStatus
from schemas.reservation import ReservationCreate
from schemas.contract import ContractExtendRequest


# ----------------- Router chính -----------------
router = APIRouter(prefix="/api", tags=["Reservation & Contract"])

# ----------------- Helper -----------------
def get_first_day_of_next_month(d: date) -> date:
    """Trả về ngày 01 của tháng kế tiếp từ ngày d"""
    year = d.year + (d.month // 12)
    month = d.month % 12 + 1
    return date(year, month, 1)


# ----------------- API Sinh viên -----------------
student_router = APIRouter(prefix="/student", tags=["Student Reservation"])

@student_router.post("/reservations/")
def create_reservation(
    data: ReservationCreate,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_user)
):
    student = db.query(Student).filter(Student.account_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    room = db.query(Room).filter(Room.id == data.room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    # check full
    approved_count = db.query(Reservation).filter(
        Reservation.room_id == room.id,
        Reservation.status == ReservationStatus.APPROVED
    ).count()
    if approved_count >= room.capacity:
        raise HTTPException(status_code=400, detail="Room is full")

    # check student đã có booking chưa
    existing_res = db.query(Reservation).filter(
        Reservation.student_id == student.id,
        Reservation.status.in_([ReservationStatus.PENDING, ReservationStatus.APPROVED])
    ).first()
    if existing_res:
        raise HTTPException(status_code=400, detail="Student already has a reservation")

    new_res = Reservation(
        student_id=student.id,
        room_id=data.room_id,
        booking_date=data.booking_date,
    )
    db.add(new_res)
    db.commit()
    db.refresh(new_res)

    return JSONResponse({
        "message": "Reservation created successfully",
        "data": {
            "reservation_id": new_res.id,
            "room_id": new_res.room_id,
            "start_date": str(new_res.start_date),
            "status": new_res.status.value
        }
    })

@student_router.get("/contracts")
def get_my_contracts(
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_user)
):
    student = db.query(Student).filter(Student.account_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    contracts = (
        db.query(Contract)
        .join(Reservation, Contract.reservation_id == Reservation.id)
        .filter(Reservation.student_id == student.id)
        .all()
    )

    if not contracts:
        raise HTTPException(status_code=404, detail="No contracts found")

    return JSONResponse({
        "count": len(contracts),
        "data": [
            {
                "id": c.id,
                "reservation_id": c.reservation_id,
                "start_date": str(c.start_date),
                "end_date": str(c.end_date),
                "status": c.status.value,
                "room_id": c.reservation.room_id
            }
            for c in contracts
        ]
    })
    
@student_router.delete("/booking/{reservation_id}/cancel")
def cancel_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_user)
):
    student = db.query(Student).filter(Student.account_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    reservation = db.query(Reservation).filter(
        Reservation.id == reservation_id,
        Reservation.student_id == student.id
    ).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Booking not found")

    if reservation.status != ReservationStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail="Booking cannot be canceled because it is already approved or rejected"
        )

    db.delete(reservation)
    db.commit()

    return JSONResponse({"message": "Booking canceled successfully"})


@student_router.get("/info/reservations")
def get_reservations(
    status: Optional[ReservationStatus] = Query(None, description="Lọc theo trạng thái"),
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_user),
):
    student = db.query(Student).filter(Student.account_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=400, detail="Không tìm thấy sinh viên")

    query = db.query(Reservation).filter(Reservation.student_id == student.id)
    if status:
        query = query.filter(Reservation.status == status)

    reservations = query.all()
    if not reservations:
        raise HTTPException(status_code=404, detail="Không có dữ liệu đặt phòng")

    return JSONResponse({
        "count": len(reservations),
        "data": [
            {
                "id": r.id,
                "room_id": r.room_id,
                "start_date": str(r.start_date) if r.start_date else None,
                "status": r.status.value,
            }
            for r in reservations
        ]
    })


# ----------------- API Admin -----------------
admin_router = APIRouter(prefix="/admin", tags=["Admin Reservation & Contract"])

@admin_router.get("/contract/{contract_id}")
def get_contract_detail(
    contract_id: int,
    db: Session = Depends(get_db),
    current_user: Account = Depends(admin_required),
):
    contract = (
        db.query(Contract)
        .join(Reservation, Contract.reservation_id == Reservation.id)
        .join(Student, Reservation.student_id == Student.id)
        .filter(Contract.id == contract_id)
        .first()
    )
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    return JSONResponse({
        "id": contract.id,
        "reservation_id": contract.reservation_id,
        "start_date": str(contract.start_date),
        "end_date": str(contract.end_date),
        "status": contract.status.value,
        "student": {
            "id": contract.reservation.student.id,
            "name": contract.reservation.student.full_name,
            "email": contract.reservation.student.email,
        },
        "room_id": contract.reservation.room_id
    })


@admin_router.get("/reservations")
def list_reservations(
    status: Optional[str] = None,
    room_id: Optional[int] = None,
    student_id: Optional[int] = None,
    sort_by: str = "created_at",
    order: str = "asc",
    db: Session = Depends(get_db),
    current_user: Account = Depends(admin_required),
):
    query = db.query(Reservation).options(joinedload(Reservation.student))

    if status:
        query = query.filter(Reservation.status == status)
    if room_id:
        query = query.filter(Reservation.room_id == room_id)
    if student_id:
        query = query.filter(Reservation.student_id == student_id)

    order_by = Reservation.start_date if sort_by == "start_date" else Reservation.booking_date
    if order == "desc":
        order_by = order_by.desc()

    reservations = query.order_by(order_by).all()

    return JSONResponse({
        "count": len(reservations),
        "data": [
            {
                "reservation_id": r.id,
                "status": r.status.value,
                "room_id": r.room_id,
                "created_at": str(r.booking_date),
                "start_date": str(r.start_date) if r.start_date else None,
                "student": {
                    "id": r.student.id,
                    "name": r.student.full_name,
                    "birth": str(r.student.birth),
                    "gender": r.student.gender,
                    "phone": r.student.phone,
                    "email": r.student.email,
                }
            }
            for r in reservations
        ]
    })


@admin_router.put("/reservations/{reservation_id}/status")
def update_reservation_status(
    reservation_id: int,
    new_status: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: Account = Depends(admin_required),
):
    if new_status not in [ReservationStatus.APPROVED, ReservationStatus.REJECTED]:
        raise HTTPException(status_code=400, detail="Invalid status value")

    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    if reservation.status != ReservationStatus.PENDING:
        raise HTTPException(status_code=400, detail="Reservation already processed")

    room = db.query(Room).filter(Room.id == reservation.room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    if new_status == ReservationStatus.APPROVED:
        approved_count = db.query(Reservation).filter(
            Reservation.room_id == room.id,
            Reservation.status == ReservationStatus.APPROVED
        ).count()
        if approved_count >= room.capacity:
            raise HTTPException(status_code=400, detail="Room is already full")

        today = date.today()
        start_date = get_first_day_of_next_month(today)

        reservation.status = ReservationStatus.APPROVED
        reservation.start_date = start_date

        end_date = date(
            start_date.year + (start_date.month + 11) // 12,
            (start_date.month + 11) % 12 + 1,
            1
        )
        new_contract = Contract(
            reservation_id=reservation.id,
            start_date=start_date,
            end_date=end_date,
            status=ContractStatus.ACTIVE
        )
        db.add(new_contract)
    else:
        reservation.status = ReservationStatus.REJECTED
        reservation.start_date = None

    db.commit()
    db.refresh(reservation)

    return JSONResponse({
        "message": f"Reservation {new_status} successfully",
        "data": {
            "reservation_id": reservation.id,
            "status": reservation.status.value,
            "start_date": str(reservation.start_date) if reservation.start_date else None
        }
    })


@admin_router.put("/contract/{contract_id}/extend")
def extend_contract(
    contract_id: int,
    data: ContractExtendRequest,
    db: Session = Depends(get_db),
    current_user: Account = Depends(admin_required),
):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    if contract.status != ContractStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Only active contracts can be extended")

    if data.new_end_date <= contract.end_date:
        raise HTTPException(status_code=400, detail="New end date must be after current end date")

    old_end_date = contract.end_date
    contract.end_date = data.new_end_date
    db.commit()
    db.refresh(contract)

    return JSONResponse({
        "message": "Contract extended successfully",
        "data": {
            "contract_id": contract.id,
            "old_end_date": str(old_end_date),
            "new_end_date": str(contract.end_date),
            "status": contract.status.value
        }
    })


@admin_router.get("/contracts/expiring-soon")
def get_expiring_contracts(
    days: int = Query(30, ge=1, le=365, description="Số ngày sắp hết hạn, mặc định 30"),
    db: Session = Depends(get_db),
    current_user: Account = Depends(admin_required),
):
    today = datetime.utcnow().date()
    deadline = today + timedelta(days=days)

    contracts = (
        db.query(Contract)
        .join(Reservation, Contract.reservation_id == Reservation.id)
        .join(Student, Reservation.student_id == Student.id)
        .filter(
            Contract.status == ContractStatus.ACTIVE,
            Contract.end_date >= today,
            Contract.end_date <= deadline,
        )
        .all()
    )

    return JSONResponse({
        "count": len(contracts),
        "expiring_within_days": days,
        "data": [
            {
                "id": c.id,
                "reservation_id": c.reservation_id,
                "start_date": str(c.start_date),
                "end_date": str(c.end_date),
                "status": c.status.value,
                "student": {
                    "id": c.reservation.student.id,
                    "name": c.reservation.student.full_name,
                    "email": c.reservation.student.email,
                    "phone": c.reservation.student.phone,
                }
            }
            for c in contracts
        ]
    })


# ----------------- Gắn router con vào router chính -----------------
router.include_router(student_router)
router.include_router(admin_router)
