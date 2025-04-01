import os
import logging
from contextlib import asynccontextmanager
from datetime import date
from typing import AsyncGenerator
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import uvicorn
from auth import router as auth_router
from database import Base, engine, get_db
from models import Category
from routes import router as main_router

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Handle startup and shutdown events for the FastAPI application."""
    logger.info("Starting application...")
    
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")

        db: Session = next(get_db())
        default_categories = [
            {"name": "Nhà", "created_date": date(2023, 5, 1)},
            {"name": "Đồ ăn", "created_date": date(2023, 5, 1)},
            {"name": "Phương tiện", "created_date": date(2023, 5, 1)},
            {"name": "Giải trí", "created_date": date(2023, 5, 1)},
            {"name": "Mua sắm", "created_date": date(2023, 5, 1)},
            {"name": "Khác", "created_date": date(2023, 5, 1)},
        ]

        for cat in default_categories:
            if not db.query(Category).filter(Category.name == cat["name"]).first():
                category = Category(name=cat["name"], created_date=cat["created_date"])
                db.add(category)
                logger.info(f"Added default category: {cat['name']}")
        db.commit()
        logger.info("Default categories added successfully")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise
    finally:
        db.close()

    yield
    
    logger.info("Application is shutting down...")

app = FastAPI(
    title="Expense Tracker API",
    description="A FastAPI-based application for managing expenses, budgets, bills, shared expenses, accounts, and saving goals.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unhandled exceptions and return a generic error response."""
    logger.error(f"Unhandled error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

app.include_router(auth_router)
app.include_router(main_router)

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 5000))
    log_level = os.getenv("LOG_LEVEL", "info")

    logger.info(f"Starting server on {host}:{port} with log level {log_level}")
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level=log_level,
        workers=1,  
        timeout_keep_alive=30, 
    )