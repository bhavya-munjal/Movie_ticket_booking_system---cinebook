import uuid
from sqlalchemy.orm import Session
from app.models import Booking, Transaction, Seat
from app.services.seat_service import mark_seats_booked, release_locks
from app.utils import email_service
from app.utils.payment_service import process_payment, refund_payment

def create_booking(db: Session, user_id: int, showtime_id: int, seat_ids: list[int]) -> dict:
    from app.services.movie_service import get_showtime
    from app.services.auth_service import get_user_by_id

    showtime = get_showtime(db, showtime_id)
    user = get_user_by_id(db, user_id)
    seats = db.query(Seat).filter(Seat.id.in_(seat_ids)).all()

    unavailable = [s for s in seats if s.is_booked or (not s.is_locked) or s.locked_by != user_id]
    if unavailable:
        return {"success": False, "message": "Some seats are no longer held. Please re-select."}

    seat_labels = ", ".join(f"{s.row_label}{s.seat_number}" for s in seats)
    total = showtime.price * len(seats)
    booking_ref = f"CB{uuid.uuid4().hex[:8].upper()}"

    payment = process_payment(user_id, booking_ref, total)
    if not payment.success:
        return {"success": False, "message": "Payment failed. Please try again."}

    txn = Transaction(
        transaction_id=payment.transaction_id,
        booking_ref=booking_ref,
        user_id=user_id,
        amount=total,
        status="success",
        payment_method="mock_card"
    )
    db.add(txn)

    booking = Booking(
        booking_ref=booking_ref,
        user_id=user_id,
        showtime_id=showtime_id,
        seat_ids=",".join(str(i) for i in seat_ids),
        seat_labels=seat_labels,
        total_amount=total,
        payment_status="paid",
        transaction_id=payment.transaction_id,
        status="confirmed"
    )
    db.add(booking)
    mark_seats_booked(db, seat_ids)
    db.commit()
    db.refresh(booking)

    email_service.send_booking_confirmation(
        user.name, user.email, booking_ref,
        showtime.movie.title, showtime.show_date,
        showtime.show_time, seat_labels, total
    )
    return {"success": True, "booking_ref": booking_ref, "booking_id": booking.id}

def get_user_bookings(db: Session, user_id: int):
    return db.query(Booking).filter(Booking.user_id == user_id).order_by(Booking.created_at.desc()).all()

def get_booking(db: Session, booking_id: int):
    return db.query(Booking).filter(Booking.id == booking_id).first()

def get_all_bookings(db: Session):
    return db.query(Booking).order_by(Booking.created_at.desc()).all()

def cancel_booking(db: Session, booking_id: int, user_id: int) -> dict:
    from app.services.auth_service import get_user_by_id
    booking = db.query(Booking).filter(Booking.id == booking_id, Booking.user_id == user_id).first()
    if not booking or booking.status == "cancelled":
        return {"success": False, "message": "Booking not found or already cancelled"}

    booking.status = "cancelled"
    seat_ids = [int(x) for x in booking.seat_ids.split(",") if x]
    seats = db.query(Seat).filter(Seat.id.in_(seat_ids)).all()
    for seat in seats:
        seat.is_booked = False
    db.commit()

    if booking.transaction_id:
        refund_payment(booking.transaction_id, booking.total_amount)

    user = get_user_by_id(db, user_id)
    email_service.send_cancellation_email(user.name, user.email, booking.booking_ref,
                                           booking.showtime.movie.title)
    return {"success": True}
