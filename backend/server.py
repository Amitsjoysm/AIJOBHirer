from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
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
app = FastAPI(title="HireFlow AI", version="1.0.0")
api_router = APIRouter(prefix="/api")

# Import routes
from routes import auth_routes, company_routes, job_routes, application_routes, candidate_routes, interview_routes, analytics_routes

# Include all routes
api_router.include_router(auth_routes.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(company_routes.router, prefix="/companies", tags=["Companies"])
api_router.include_router(job_routes.router, prefix="/jobs", tags=["Jobs"])
api_router.include_router(application_routes.router, prefix="/applications", tags=["Applications"])
api_router.include_router(candidate_routes.router, prefix="/candidates", tags=["Candidates"])
api_router.include_router(interview_routes.router, prefix="/interviews", tags=["Interviews"])
api_router.include_router(analytics_routes.router, prefix="/analytics", tags=["Analytics"])

app.include_router(api_router)

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
    logger.info("Database indexes created")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
    logger.info("Database connection closed")

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}
