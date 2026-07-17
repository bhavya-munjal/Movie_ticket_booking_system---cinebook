from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import movie_service, booking_service
from app.services.auth_service import get_user_by_id
from app.utils.auth import get_current_user_id

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")

def _require_admin(request: Request, db: Session):
    uid = get_current_user_id(request)
    if not uid:
        return None
    user = get_user_by_id(db, uid)
    return user if (user and user.is_admin) else None

@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    user = _require_admin(request, db)
    if not user:
        return RedirectResponse("/auth/login", 302)
    movies = movie_service.get_all_movies(db)
    bookings = booking_service.get_all_bookings(db)
    showtimes = movie_service.get_all_showtimes(db)
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request, "user": user,
        "movies": movies, "bookings": bookings[:10], "showtimes": showtimes,
        "total_revenue": sum(b.total_amount for b in bookings if b.payment_status == "paid")
    })

@router.get("/movies", response_class=HTMLResponse)
def movies_list(request: Request, db: Session = Depends(get_db)):
    user = _require_admin(request, db)
    if not user:
        return RedirectResponse("/auth/login", 302)
    movies = movie_service.get_all_movies(db)
    return templates.TemplateResponse("admin/movies.html", {"request": request, "user": user, "movies": movies})

@router.get("/movies/add", response_class=HTMLResponse)
def add_movie_page(request: Request, db: Session = Depends(get_db)):
    user = _require_admin(request, db)
    if not user:
        return RedirectResponse("/auth/login", 302)
    return templates.TemplateResponse("admin/movie_form.html", {"request": request, "user": user, "movie": None})

@router.post("/movies/add")
def add_movie(request: Request, db: Session = Depends(get_db),
              title: str = Form(...), description: str = Form(""),
              genre: str = Form(""), language: str = Form("English"),
              duration_mins: int = Form(120), rating: float = Form(0.0),
              poster_url: str = Form("")):
    user = _require_admin(request, db)
    if not user:
        return RedirectResponse("/auth/login", 302)
    movie_service.create_movie(db, {
        "title": title, "description": description, "genre": genre,
        "language": language, "duration_mins": duration_mins,
        "rating": rating, "poster_url": poster_url
    })
    return RedirectResponse("/admin/movies", 302)

@router.get("/movies/edit/{movie_id}", response_class=HTMLResponse)
def edit_movie_page(movie_id: int, request: Request, db: Session = Depends(get_db)):
    user = _require_admin(request, db)
    if not user:
        return RedirectResponse("/auth/login", 302)
    movie = movie_service.get_movie(db, movie_id)
    return templates.TemplateResponse("admin/movie_form.html", {"request": request, "user": user, "movie": movie})

@router.post("/movies/edit/{movie_id}")
def edit_movie(movie_id: int, request: Request, db: Session = Depends(get_db),
               title: str = Form(...), description: str = Form(""),
               genre: str = Form(""), language: str = Form("English"),
               duration_mins: int = Form(120), rating: float = Form(0.0),
               poster_url: str = Form("")):
    user = _require_admin(request, db)
    if not user:
        return RedirectResponse("/auth/login", 302)
    movie_service.update_movie(db, movie_id, {
        "title": title, "description": description, "genre": genre,
        "language": language, "duration_mins": duration_mins,
        "rating": rating, "poster_url": poster_url
    })
    return RedirectResponse("/admin/movies", 302)

@router.post("/movies/delete/{movie_id}")
def delete_movie(movie_id: int, request: Request, db: Session = Depends(get_db)):
    user = _require_admin(request, db)
    if not user:
        return RedirectResponse("/auth/login", 302)
    movie_service.delete_movie(db, movie_id)
    return RedirectResponse("/admin/movies", 302)

@router.get("/showtimes", response_class=HTMLResponse)
def showtimes_page(request: Request, db: Session = Depends(get_db)):
    user = _require_admin(request, db)
    if not user:
        return RedirectResponse("/auth/login", 302)
    showtimes = movie_service.get_all_showtimes(db)
    movies = movie_service.get_all_movies(db)
    screens = movie_service.get_all_screens(db)
    return templates.TemplateResponse("admin/showtimes.html", {
        "request": request, "user": user, "showtimes": showtimes,
        "movies": movies, "screens": screens
    })

@router.post("/showtimes/add")
def add_showtime(request: Request, db: Session = Depends(get_db),
                 movie_id: int = Form(...), screen_id: int = Form(...),
                 show_date: str = Form(...), show_time: str = Form(...),
                 price: float = Form(250.0)):
    user = _require_admin(request, db)
    if not user:
        return RedirectResponse("/auth/login", 302)
    movie_service.create_showtime(db, {
        "movie_id": movie_id, "screen_id": screen_id,
        "show_date": show_date, "show_time": show_time, "price": price
    })
    return RedirectResponse("/admin/showtimes", 302)

@router.get("/bookings", response_class=HTMLResponse)
def all_bookings(request: Request, db: Session = Depends(get_db)):
    user = _require_admin(request, db)
    if not user:
        return RedirectResponse("/auth/login", 302)
    bookings = booking_service.get_all_bookings(db)
    return templates.TemplateResponse("admin/bookings.html", {
        "request": request, "user": user, "bookings": bookings
    })
