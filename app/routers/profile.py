import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.database import get_db
from app.models.resume import UserResume
from app.models.user import User
from app.schemas.profile import ProfileUpdate

router = APIRouter(prefix="/api/v1/profile", tags=["Profile"])
dashboard_router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard"])
bearer = HTTPBearer()

async def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    try:
        payload = jwt.decode(creds.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise HTTPException(401, "Invalid or expired token")
    user = await db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(401, "User not active")
    return user

async def get_resume(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(UserResume)
        .where(UserResume.user_id == user_id)
        .order_by(UserResume.id.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()

def build_profile(user: User, resume) -> dict:
    extra = resume.extracted_json if resume else {}
    return {
        "user_id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "qualification": user.qualification,
        "skills": extra.get("skills", []),
        "experience": extra.get("experience"),
    }

@router.get("")
async def get_profile(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return build_profile(user, await get_resume(db, user.id))

@router.patch("")
async def update_profile(
    data: ProfileUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    changes = data.model_dump(exclude_unset=True)

    for field in ("name", "phone", "qualification"):
        if field in changes:
            setattr(user, field, changes[field])

    if "skills" in changes or "experience" in changes:
        resume = await get_resume(db, user.id)
        if not resume:
            resume = UserResume(user_id=user.id, filename="manual_entry", extracted_json={})
            db.add(resume)
        extra = dict(resume.extracted_json or {})
        if "skills" in changes:
            extra["skills"] = changes["skills"]
        if "experience" in changes:
            extra["experience"] = changes["experience"]
        resume.extracted_json = extra  

    await db.commit()
    return build_profile(user, await get_resume(db, user.id))

@dashboard_router.get("")
async def dashboard(user: User = Depends(get_current_user)):
    return {
        "user_state": "active",
        "user_id": user.id,
        "name": user.name,
        "redirect_url": "/dashboard/student",
    }