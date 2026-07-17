from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    bookings = relationship("Booking", back_populates="user")

class Movie(Base):
    __tablename__ = "movies"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    genre = Column(String)
    language = Column(String, default="English")
    duration_mins = Column(Integer)
    rating = Column(Float, default=0.0)
    poster_url = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    showtimes = relationship("Showtime", back_populates="movie")

class Screen(Base):
    __tablename__ = "screens"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    total_rows = Column(Integer, default=8)
    seats_per_row = Column(Integer, default=10)
    showtimes = relationship("Showtime", back_populates="screen")

class Showtime(Base):
    __tablename__ = "showtimes"
    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id"))
    screen_id = Column(Integer, ForeignKey("screens.id"))
    show_date = Column(String, nullable=False)
    show_time = Column(String, nullable=False)
    price = Column(Float, default=250.0)
    is_active = Column(Boolean, default=True)
    movie = relationship("Movie", back_populates="showtimes")
    screen = relationship("Screen", back_populates="showtimes")
    seats = relationship("Seat", back_populates="showtime")
    bookings = relationship("Booking", back_populates="showtime")

class Seat(Base):
    __tablename__ = "seats"
    id = Column(Integer, primary_key=True, index=True)
    showtime_id = Column(Integer, ForeignKey("showtimes.id"))
    row_label = Column(String)
    seat_number = Column(Integer)
    is_booked = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)
    locked_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    locked_until = Column(DateTime, nullable=True)
    showtime = relationship("Showtime", back_populates="seats")

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    booking_ref = Column(String, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    showtime_id = Column(Integer, ForeignKey("showtimes.id"))
    seat_ids = Column(String)  # comma-separated seat ids
    seat_labels = Column(String)  # e.g. "A1,A2"
    total_amount = Column(Float)
    payment_status = Column(String, default="pending")  # pending, paid, failed
    transaction_id = Column(String, nullable=True)
    status = Column(String, default="confirmed")  # confirmed, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="bookings")
    showtime = relationship("Showtime", back_populates="bookings")

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, unique=True)
    booking_ref = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float)
    status = Column(String, default="success")
    payment_method = Column(String, default="mock")
    created_at = Column(DateTime, default=datetime.utcnow)
