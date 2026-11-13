import hmac
from datetime import datetime
import pyotp
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.otp import OtpChallenge
from app.models.user import User
from app.schemas.auth import RegisterRequest, VerifyRequest
from app.services.otp import dispatch_2fa
from app.services.security import hash_password, hash_otp, create_access_token
from app.models.resume import UserResume

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])

@router.post("/register", status_code=201)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(400, "Email already registered")

    user = User(
        name=data.name,
        email=data.email,
        phone=data.phone,
        qualification=data.qualification,
        password_hash=hash_password(data.password),
        is_active=False,
    )
    db.add(user)
    await db.flush()  

    if data.resume_id:
        resume=await db.get(UserResume, data.resume_id)
        if resume and resume.user_id is None:
            resume.user_id=user.id

    extra = await dispatch_2fa(db, user, data.channel)
    await db.commit()
    return {
        "message": f"Registered. Verify using {data.channel}",
        "user_id": user.id,
        "channel": data.channel,
        **extra,
    }

@router.post("/verify-2fa")
async def verify_2fa(data: VerifyRequest, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, data.user_id)
    if not user:
        raise HTTPException(404, "User not found")

    if data.channel == "totp":
        if not user.totp_secret or not pyotp.TOTP(user.totp_secret).verify(data.code, valid_window=1):
            raise HTTPException(400, "Invalid TOTP code")
    else:
        result = await db.execute(
            select(OtpChallenge)
            .where(
                OtpChallenge.user_id == user.id,
                OtpChallenge.channel == data.channel,
                OtpChallenge.is_used == False,
            )
            .order_by(OtpChallenge.id.desc())
            .limit(1)
        )
        challenge = result.scalar_one_or_none()
        if not challenge:
            raise HTTPException(400, "No active OTP. Register again")
        if challenge.expires_at < datetime.utcnow():
            raise HTTPException(400, "OTP expired")
        if not hmac.compare_digest(challenge.otp_hash, hash_otp(data.code)):
            raise HTTPException(400, "Invalid OTP")
        challenge.is_used = True

    user.is_active = True
    await db.commit()
    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
        "user_id": user.id,
    }