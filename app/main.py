from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.database import engine
from app import models
from app.routers import auth, movies, bookings, admin
from app.seed import seed

models.Base.metadata.create_all(bind=engine)
seed()

app = FastAPI(title="CineBook", version="1.0.0")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(auth.router)
app.include_router(movies.router)
app.include_router(bookings.router)
app.include_router(admin.router)
