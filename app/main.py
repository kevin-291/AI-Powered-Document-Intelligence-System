from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging

from app.database import init_db
from app.api import router as api_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("Startup complete: DB initialized.")
    yield
    logger.info("Shutdown complete.")

app = FastAPI(
    lifespan=lifespan,
    title="AI Document Intelligence",
    description="AI-Powered Document Intelligence System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    api_router, 
    prefix="/api/v1", 
    tags=["Documents"]
)

@app.get("/")
def root():
    return {
        "message": "Welcome to AI Document Intelligence",
        "status": "running",
        "docs_url": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True
    )