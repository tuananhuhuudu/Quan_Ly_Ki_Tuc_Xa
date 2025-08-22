from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session
from datetime import datetime
from database.init_db import get_db
from models.contract import Contract
from models.invoice import Invoice
from models.reservation import Reservation
from models.students import Student
from models.account import Account
from helpers.contract_status import ContractStatus
from services.auth import admin_required, get_current_user

router = APIRouter(prefix="/invoices", tags=["Invoices"])

# ============================
# Admin generate invoices
# ============================
@router.post("/generate")
def generate_invoices(
    month: int,
    year: int,
    db: Session = Depends(get_db),
    current_user=Depends(admin_required),
):
    today = datetime.utcnow().date()

    contracts = (
        db.query(Contract)
        .filter(
            Contract.status == ContractStatus.ACTIVE,
            Contract.start_date <= today,
            Contract.end_date >= today,
        )
        .all()
    )

    invoices = []
    for c in contracts:
        # check nếu contract đã có invoice cho tháng này rồi thì bỏ qua
        existing = (
            db.query(Invoice)
            .filter(
                Invoice.contract_id == c.id,
                Invoice.month == month,
                Invoice.year == year,
            )
            .first()
        )
        if existing:
            continue

        room = c.reservation.room
        if not room:
            continue

        # Chia đều theo số lượng sinh viên active trong phòng
        active_reservations = [
            r for r in room.reservations
            if r.contract and r.contract.status == ContractStatus.ACTIVE
        ]
        if not active_reservations:
            continue

        amount = room.price / len(active_reservations)

        invoice = Invoice(
            contract_id=c.id,
            amount=amount,
            month=month,
            year=year,
            status="UNPAID",
        )
        db.add(invoice)
        invoices.append(invoice)

    db.commit()

    return {
        "message": f"Đã tạo {len(invoices)} phiếu thu cho tháng {month}/{year}",
        "invoices": [
            {
                "invoice_id": inv.id,
                "contract_id": inv.contract_id,
                "amount": inv.amount,
                "month": inv.month,
                "year": inv.year,
                "status": inv.status,
            }
            for inv in invoices
        ],
    }


# ============================
# Admin get all invoices
# ============================
@router.get("")
def get_all_invoices(
    month: int = Query(None, description="Tháng cần lọc"),
    year: int = Query(None, description="Năm cần lọc"),
    status: str = Query(None, description="Trạng thái hóa đơn: PAID/UNPAID"),
    db: Session = Depends(get_db),
    current_user=Depends(admin_required),
):
    query = db.query(Invoice)

    if month:
        query = query.filter(Invoice.month == month)
    if year:
        query = query.filter(Invoice.year == year)
    if status:
        query = query.filter(Invoice.status == status)

    invoices = query.all()

    return {
        "count": len(invoices),
        "invoices": [
            {
                "invoice_id": inv.id,
                "contract_id": inv.contract_id,
                "amount": inv.amount,
                "month": inv.month,
                "year": inv.year,
                "status": inv.status,
                "paid_at": str(inv.paid_at) if inv.paid_at else None,
            }
            for inv in invoices
        ],
    }


# ============================
# Student get my invoices
# ============================
@router.get("/my")
def get_my_invoices(
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_user),
):
    student = db.query(Student).filter(Student.account_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=400, detail="Không tìm thấy thông tin sinh viên")

    invoices = (
        db.query(Invoice)
        .join(Contract, Invoice.contract_id == Contract.id)
        .join(Reservation, Contract.reservation_id == Reservation.id)
        .filter(Reservation.student_id == student.id)
        .all()
    )

    if not invoices:
        raise HTTPException(status_code=404, detail="Bạn chưa có hóa đơn nào")

    return {
        "student_id": student.id,
        "invoices": [
            {
                "invoice_id": inv.id,
                "contract_id": inv.contract_id,
                "amount": inv.amount,
                "month": inv.month,
                "year": inv.year,
                "status": inv.status,
                "paid_at": str(inv.paid_at) if inv.paid_at else None,
            }
            for inv in invoices
        ],
    }


# ============================
# Student pay invoice
# ============================
@router.put("/pay/{invoice_id}")
def pay_invoice(
    invoice_id: int = Path(..., description="ID của hóa đơn cần thanh toán"),
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_user),
):
    student = db.query(Student).filter(Student.account_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=400, detail="Không tìm thấy thông tin sinh viên")

    invoice = (
        db.query(Invoice)
        .join(Contract, Invoice.contract_id == Contract.id)
        .join(Reservation, Contract.reservation_id == Reservation.id)
        .filter(Invoice.id == invoice_id, Reservation.student_id == student.id)
        .first()
    )
    if not invoice:
        raise HTTPException(status_code=404, detail="Không tìm thấy hóa đơn này của bạn")

    if invoice.status == "PAID":
        raise HTTPException(status_code=400, detail="Hóa đơn này đã được thanh toán")

    invoice.status = "PAID"
    invoice.paid_at = datetime.utcnow()
    db.commit()
    db.refresh(invoice)

    return {
        "message": "Thanh toán hóa đơn thành công",
        "invoice": {
            "invoice_id": invoice.id,
            "amount": invoice.amount,
            "month": invoice.month,
            "year": invoice.year,
            "status": invoice.status,
            "paid_at": str(invoice.paid_at),
        },
    }


# ============================
# Admin revenue statistics
# ============================
@router.get("/stats")
def get_invoice_stats(
    month: int = Query(None, description="Tháng cần thống kê"),
    year: int = Query(None, description="Năm cần thống kê"),
    db: Session = Depends(get_db),
    current_user=Depends(admin_required),
):
    query = db.query(Invoice)

    if month:
        query = query.filter(Invoice.month == month)
    if year:
        query = query.filter(Invoice.year == year)

    invoices = query.all()

    total_amount = sum(inv.amount for inv in invoices)
    paid_amount = sum(inv.amount for inv in invoices if inv.status == "PAID")
    unpaid_amount = total_amount - paid_amount

    return {
        "month": month,
        "year": year,
        "total_invoices": len(invoices),
        "total_amount": total_amount,
        "paid_amount": paid_amount,
        "unpaid_amount": unpaid_amount,
    }
