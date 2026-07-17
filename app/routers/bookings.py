from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import booking_service, seat_service, movie_service
from app.services.auth_service import get_user_by_id
from app.utils.auth import get_current_user_id

router = APIRouter(prefix="/bookings", tags=["bookings"])
templates = Jinja2Templates(directory="app/templates")

def _require_user(request: Request, db: Session):
    uid = get_current_user_id(request)
    if not uid:
        return None, None
    return uid, get_user_by_id(db, uid)

@router.get("/seats/{showtime_id}", response_class=HTMLResponse)
def seat_selection(showtime_id: int, request: Request, db: Session = Depends(get_db)):
    uid, user = _require_user(request, db)
    if not uid:
        return RedirectResponse("/auth/login", 302)
    showtime = movie_service.get_showtime(db, showtime_id)
    if not showtime:
        return HTMLResponse("Showtime not found", 404)
    seats = seat_service.get_seats_for_showtime(db, showtime_id)
    rows = {}
    for seat in seats:
        rows.setdefault(seat.row_label, []).append(seat)
    return templates.TemplateResponse("bookings/seats.html", {
        "request": request, "user": user, "showtime": showtime,
        "rows": rows, "lock_minutes": 5
    })

@router.post("/lock-seats", response_class=JSONResponse)
def lock_seats(request: Request, data: dict, db: Session = Depends(get_db)):
    uid = get_current_user_id(request)
    if not uid:
        return JSONResponse({"success": False, "message": "Login required"}, 401)
    seat_ids = data.get("seat_ids", [])
    if not seat_ids:
        return JSONResponse({"success": False, "message": "No seats selected"})
    result = seat_service.lock_seats(db, seat_ids, uid)
    return JSONResponse(result)

@router.post("/release-seats", response_class=JSONResponse)
def release_seats(request: Request, data: dict, db: Session = Depends(get_db)):
    uid = get_current_user_id(request)
    if not uid:
        return JSONResponse({"success": False})
    seat_service.release_locks(db, data.get("seat_ids", []), uid)
    return JSONResponse({"success": True})

@router.get("/checkout/{showtime_id}", response_class=HTMLResponse)
def checkout(showtime_id: int, seats: str, request: Request, db: Session = Depends(get_db)):
    uid, user = _require_user(request, db)
    if not uid:
        return RedirectResponse("/auth/login", 302)
    showtime = movie_service.get_showtime(db, showtime_id)
    seat_ids = [int(x) for x in seats.split(",") if x]
    from app.models import Seat
    seat_objs = db.query(Seat).filter(Seat.id.in_(seat_ids)).all()
    total = showtime.price * len(seat_ids)
    seat_labels = ", ".join(f"{s.row_label}{s.seat_number}" for s in seat_objs)
    return templates.TemplateResponse("bookings/checkout.html", {
        "request": request, "user": user, "showtime": showtime,
        "seat_ids": seats, "seat_labels": seat_labels,
        "total": total, "seat_count": len(seat_ids)
    })

@router.post("/confirm", response_class=JSONResponse)
async def confirm_booking(request: Request, db: Session = Depends(get_db)):
    uid = get_current_user_id(request)
    if not uid:
        return JSONResponse({"success": False, "message": "Login required"}, 401)
    data = await request.json()
    showtime_id = data.get("showtime_id")
    seat_ids = data.get("seat_ids", [])
    result = booking_service.create_booking(db, uid, showtime_id, seat_ids)
    return JSONResponse(result)

@router.get("/confirmation/{booking_id}", response_class=HTMLResponse)
def confirmation(booking_id: int, request: Request, db: Session = Depends(get_db)):
    uid, user = _require_user(request, db)
    if not uid:
        return RedirectResponse("/auth/login", 302)
    booking = booking_service.get_booking(db, booking_id)
    if not booking or booking.user_id != uid:
        return HTMLResponse("Booking not found", 404)
    return templates.TemplateResponse("bookings/confirmation.html", {
        "request": request, "user": user, "booking": booking
    })

@router.get("/my-bookings", response_class=HTMLResponse)
def my_bookings(request: Request, db: Session = Depends(get_db)):
    uid, user = _require_user(request, db)
    if not uid:
        return RedirectResponse("/auth/login", 302)
    bookings = booking_service.get_user_bookings(db, uid)
    return templates.TemplateResponse("bookings/my_bookings.html", {
        "request": request, "user": user, "bookings": bookings
    })

@router.post("/cancel/{booking_id}", response_class=JSONResponse)
def cancel(booking_id: int, request: Request, db: Session = Depends(get_db)):
    uid = get_current_user_id(request)
    if not uid:
        return JSONResponse({"success": False}, 401)
    result = booking_service.cancel_booking(db, booking_id, uid)
    return JSONResponse(result)
