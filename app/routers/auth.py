from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import auth_service
from app.utils.auth import create_session_token, get_current_user_id

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    if get_current_user_id(request):
        return RedirectResponse("/", 302)
    return templates.TemplateResponse("auth/login.html", {"request": request})

@router.post("/login")
def login(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = auth_service.login_user(db, email, password)
    if not user:
        return templates.TemplateResponse("auth/login.html", {"request": request, "error": "Invalid email or password"})
    response = RedirectResponse("/admin" if user.is_admin else "/", 302)
    response.set_cookie("session", create_session_token(user.id), httponly=True, max_age=86400)
    return response

@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request})

@router.post("/register")
def register(request: Request, name: str = Form(...), email: str = Form(...),
             password: str = Form(...), db: Session = Depends(get_db)):
    user = auth_service.register_user(db, name, email, password)
    if not user:
        return templates.TemplateResponse("auth/register.html", {"request": request, "error": "Email already registered"})
    response = RedirectResponse("/", 302)
    response.set_cookie("session", create_session_token(user.id), httponly=True, max_age=86400)
    return response

@router.get("/logout")
def logout():
    response = RedirectResponse("/auth/login", 302)
    response.delete_cookie("session")
    return response
