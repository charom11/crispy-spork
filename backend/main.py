from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting Algorithmic Trading Platform Backend...")
    
    # Initialize database
    try:
        from app.db.database import init_db
        init_db()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Algorithmic Trading Platform Backend...")

app = FastAPI(
    title="Algorithmic Trading Platform API",
    description="Full-stack algorithmic trading platform with multiple strategies",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
from app.api.auth import router as auth_router
from app.api.strategies import router as strategies_router

app.include_router(auth_router)
app.include_router(strategies_router)

@app.get("/")
async def root():
    return {
        "message": "Algorithmic Trading Platform API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "authentication": "/auth",
            "api_docs": "/docs",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)