from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.models import user, resume, otp  
from app.routers import resume as resume_router, auth as auth_router, profile as profile_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(title="Resume Parser & 2FA Pipeline", lifespan=lifespan)
app.include_router(resume_router.router)
app.include_router(auth_router.router)
app.include_router(profile_router.router)
app.include_router(profile_router.dashboard_router)