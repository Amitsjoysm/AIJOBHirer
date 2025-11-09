from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.exceptions import RequestValidationError
from starlette.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
from slowapi.errors import RateLimitExceeded
import os
import logging

# Load environment
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection with connection pooling
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(
    mongo_url,
    maxPoolSize=100,
    minPoolSize=10,
    maxIdleTimeMS=45000,
    waitQueueTimeoutMS=5000
)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI(
    title="HireFlow AI",
    version="1.0.0",
    description="Production-ready AI-powered hiring platform for SMBs",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    redirect_slashes=False
)
api_router = APIRouter(prefix="/api")

# Import routes
from routes import (
    auth_routes, 
    oauth_routes,
    email_config_routes,
    company_routes, 
    job_routes, 
    application_routes, 
    candidate_routes, 
    interview_routes, 
    analytics_routes,
    chat_routes
)

# Include all routes
api_router.include_router(auth_routes.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(oauth_routes.router, prefix="/oauth", tags=["OAuth"])
api_router.include_router(email_config_routes.router, prefix="/email-config", tags=["Email Configuration"])
api_router.include_router(company_routes.router, prefix="/companies", tags=["Companies"])
api_router.include_router(job_routes.router, prefix="/jobs", tags=["Jobs"])
api_router.include_router(application_routes.router, prefix="/applications", tags=["Applications"])
api_router.include_router(candidate_routes.router, prefix="/candidates", tags=["Candidates"])
api_router.include_router(interview_routes.router, prefix="/interviews", tags=["Interviews"])
api_router.include_router(analytics_routes.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(chat_routes.router, prefix="/chat", tags=["Chat"])

# Add health endpoint to api_router
@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

app.include_router(api_router)

# Import middleware
from middleware.rate_limiter import limiter, RateLimits
from middleware.error_handler import (
    validation_exception_handler,
    http_exception_handler,
    general_exception_handler
)
from middleware.security import SecurityHeadersMiddleware, RequestLoggingMiddleware
from slowapi import _rate_limit_exceeded_handler

# Add rate limiter to app state
app.state.limiter = limiter

# Exception handlers
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Security middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_db():
    # Create indexes for performance
    await db.users.create_index("email", unique=True)
    await db.companies.create_index("slug", unique=True)
    await db.companies.create_index("user_id")
    await db.jobs.create_index("company_id")
    await db.jobs.create_index("status")
    await db.applications.create_index("job_id")
    await db.applications.create_index("candidate_id")
    await db.applications.create_index(["job_id", "status"])
    await db.email_configs.create_index("company_id", unique=True)
    logger.info("Database indexes created")
    
    # Initialize Redis connection
    try:
        from services.redis_service import RedisService
        redis_service = RedisService()
        if redis_service.ping():
            logger.info("Redis connection established")
        else:
            logger.warning("Redis connection failed - background jobs will not work")
    except Exception as e:
        logger.warning(f"Redis initialization failed: {str(e)} - background jobs will not work")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
    logger.info("Database connection closed")
