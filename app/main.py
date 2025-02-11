# app/main.py
from fastapi import FastAPI
from app.routers import auth as auth_router, inv as inv_router
from app.database import engine
from app.models import Base

# Create database tables on startup if they do not exist.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI MySQL Auth Example")

# Include routers
app.include_router(auth_router.router)  # Token endpoint at /token
app.include_router(inv_router.router)   # Secured inventory endpoint
