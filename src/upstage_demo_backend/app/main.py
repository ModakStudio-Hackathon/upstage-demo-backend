from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List
from . import crud, models, schemas
from .database import SessionLocal, engine, get_db
from .config import settings

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="장부 관리 시스템 API",
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)
