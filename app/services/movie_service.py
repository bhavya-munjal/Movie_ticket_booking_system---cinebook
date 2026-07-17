from sqlalchemy.orm import Session
from app.models import Movie, Showtime, Screen

def get_all_movies(db: Session):
    return db.query(Movie).filter(Movie.is_active == True).all()

def get_movie(db: Session, movie_id: int):
    return db.query(Movie).filter(Movie.id == movie_id).first()

def get_showtimes_for_movie(db: Session, movie_id: int):
    return db.query(Showtime).filter(
        Showtime.movie_id == movie_id, Showtime.is_active == True
    ).order_by(Showtime.show_date, Showtime.show_time).all()

def get_showtime(db: Session, showtime_id: int):
    return db.query(Showtime).filter(Showtime.id == showtime_id).first()

def create_movie(db: Session, data: dict) -> Movie:
    movie = Movie(**data)
    db.add(movie)
    db.commit()
    db.refresh(movie)
    return movie

def update_movie(db: Session, movie_id: int, data: dict) -> Movie | None:
    movie = get_movie(db, movie_id)
    if not movie:
        return None
    for k, v in data.items():
        setattr(movie, k, v)
    db.commit()
    db.refresh(movie)
    return movie

def delete_movie(db: Session, movie_id: int):
    movie = get_movie(db, movie_id)
    if movie:
        movie.is_active = False
        db.commit()

def get_all_screens(db: Session):
    return db.query(Screen).all()

def create_screen(db: Session, name: str, rows: int, seats: int) -> Screen:
    s = Screen(name=name, total_rows=rows, seats_per_row=seats)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s

def create_showtime(db: Session, data: dict) -> Showtime:
    st = Showtime(**data)
    db.add(st)
    db.commit()
    db.refresh(st)
    return st

def get_all_showtimes(db: Session):
    return db.query(Showtime).filter(Showtime.is_active == True).order_by(Showtime.show_date).all()
