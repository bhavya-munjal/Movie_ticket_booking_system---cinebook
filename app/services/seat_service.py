from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models import Seat, Showtime, Screen
from app.config import settings

def _get_or_create_seats(db: Session, showtime: Showtime):
    seats = db.query(Seat).filter(Seat.showtime_id == showtime.id).all()
    if not seats:
        screen = showtime.screen
        rows = [chr(65 + i) for i in range(screen.total_rows)]
        for row in rows:
            for num in range(1, screen.seats_per_row + 1):
                db.add(Seat(showtime_id=showtime.id, row_label=row, seat_number=num))
        db.commit()
        seats = db.query(Seat).filter(Seat.showtime_id == showtime.id).all()
    return seats

def get_seats_for_showtime(db: Session, showtime_id: int):
    from app.services.movie_service import get_showtime
    showtime = get_showtime(db, showtime_id)
    if not showtime:
        return []
    _expire_locks(db)
    seats = _get_or_create_seats(db, showtime)
    return seats

def _expire_locks(db: Session):
    now = datetime.utcnow()
    expired = db.query(Seat).filter(Seat.is_locked == True, Seat.locked_until < now).all()
    for seat in expired:
        seat.is_locked = False
        seat.locked_by = None
        seat.locked_until = None
    if expired:
        db.commit()

def lock_seats(db: Session, seat_ids: list[int], user_id: int) -> dict:
    _expire_locks(db)
    seats = db.query(Seat).filter(Seat.id.in_(seat_ids)).all()
    unavailable = [s for s in seats if s.is_booked or (s.is_locked and s.locked_by != user_id)]
    if unavailable:
        return {"success": False, "message": f"{len(unavailable)} seat(s) no longer available"}
    until = datetime.utcnow() + timedelta(minutes=settings.SEAT_LOCK_MINUTES)
    for seat in seats:
        seat.is_locked = True
        seat.locked_by = user_id
        seat.locked_until = until
    db.commit()
    return {"success": True, "locked_until": until.isoformat()}

def release_locks(db: Session, seat_ids: list[int], user_id: int):
    seats = db.query(Seat).filter(Seat.id.in_(seat_ids), Seat.locked_by == user_id).all()
    for seat in seats:
        seat.is_locked = False
        seat.locked_by = None
        seat.locked_until = None
    db.commit()

def mark_seats_booked(db: Session, seat_ids: list[int]):
    seats = db.query(Seat).filter(Seat.id.in_(seat_ids)).all()
    for seat in seats:
        seat.is_booked = True
        seat.is_locked = False
        seat.locked_by = None
        seat.locked_until = None
    db.commit()
