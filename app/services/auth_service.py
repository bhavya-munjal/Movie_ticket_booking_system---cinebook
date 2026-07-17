from sqlalchemy.orm import Session
from app.models import User
from app.utils.auth import hash_password, verify_password
from app.utils import email_service

def register_user(db: Session, name: str, email: str, password: str) -> User | None:
    if db.query(User).filter(User.email == email).first():
        return None
    user = User(name=name, email=email, hashed_password=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    email_service.send_welcome_email(user.name, user.email)
    return user

def login_user(db: Session, email: str, password: str) -> User | None:
    user = db.query(User).filter(User.email == email).first()
    if user and verify_password(password, user.hashed_password):
        return user
    return None

def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()
