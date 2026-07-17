from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import movie_service
from app.utils.auth import get_current_user_id
from app.services.auth_service import get_user_by_id

router = APIRouter(tags=["movies"])
templates = Jinja2Templates(directory="app/templates")

def _ctx(request: Request, db: Session, **kwargs):
    uid = get_current_user_id(request)
    user = get_user_by_id(db, uid) if uid else None
    return {"request": request, "user": user, **kwargs}

@router.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    movies = movie_service.get_all_movies(db)
    return templates.TemplateResponse("movies/home.html", _ctx(request, db, movies=movies))

@router.get("/movies/{movie_id}", response_class=HTMLResponse)
def movie_detail(movie_id: int, request: Request, db: Session = Depends(get_db)):
    movie = movie_service.get_movie(db, movie_id)
    if not movie:
        return HTMLResponse("Movie not found", 404)
    showtimes = movie_service.get_showtimes_for_movie(db, movie_id)
    from itertools import groupby
    grouped = {}
    for st in showtimes:
        grouped.setdefault(st.show_date, []).append(st)
    return templates.TemplateResponse("movies/detail.html", _ctx(request, db, movie=movie, grouped_showtimes=grouped))
