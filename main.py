from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import logging

from app.config import settings
from app.database import db_manager, get_db, Base
from app.models import SurveyResponse
from app.routes import survey, results

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.is_production else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=db_manager.engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Wallis Social Research Style Student Satisfaction Survey",
    version="2.0.0",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None
)

# Security Middleware
if settings.is_production:
    # Force HTTPS in production
    app.add_middleware(HTTPSRedirectMiddleware)
    
    # Trusted hosts
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=settings.allowed_hosts
    )

# CORS Middleware
if settings.cors_origins and settings.cors_origins[0]:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

# Include routers
app.include_router(survey.router, prefix="/survey", tags=["survey"])
app.include_router(results.router, prefix="/results", tags=["results"])

# Templates
templates = Jinja2Templates(directory="app/templates")

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info(f"Starting {settings.app_name} in {settings.environment} mode")
    
    # Test database connection
    if not db_manager.test_connection():
        raise Exception("Failed to connect to database on startup")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "app_name": settings.app_name,
        "environment": settings.environment
    })

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Comprehensive health check endpoint"""
    try:
        # Test database connection
        db.execute("SELECT 1")
        
        # Get basic stats
        total_responses = db.query(SurveyResponse).count()
        
        return {
            "status": "healthy",
            "service": settings.app_name,
            "environment": settings.environment,
            "database": "connected",
            "total_surveys": total_responses,
            "version": "2.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )

@app.get("/api/info")
async def api_info():
    """API information endpoint"""
    return {
        "app_name": settings.app_name,
        "version": "2.0.0",
        "environment": settings.environment,
        "debug": settings.debug
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse("500.html", {"request": request}, status_code=500)