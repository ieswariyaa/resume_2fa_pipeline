from datetime import datetime, timedelta
from email.message import EmailMessage
import aiosmtplib
import pyotp
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.models.otp import OtpChallenge
from app.models.user import User
from app.services.security import generate_otp, hash_otp

async def send_email(to: str, otp: str):
    if not settings.SMTP_HOST:
        print(f"[MOCK EMAIL] To: {to} | OTP: {otp}", flush=True)
        return
    msg = EmailMessage()
    msg["From"] = settings.SMTP_USER
    msg["To"] = to
    msg["Subject"] = "Your verification code"
    msg.set_content(f"Your OTP is {otp}. It expires in {settings.OTP_EXPIRE_MINUTES} minutes.")
    await aiosmtplib.send(
        msg,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD,
        start_tls=True,
    )

async def send_whatsapp(phone: str, otp: str):
    
    print(f"[MOCK WHATSAPP] To: {phone} | OTP: {otp}", flush=True)

async def dispatch_2fa(db: AsyncSession, user: User, channel: str) -> dict:
    if channel == "totp":
        if not user.totp_secret:
            user.totp_secret = pyotp.random_base32()
        uri = pyotp.TOTP(user.totp_secret).provisioning_uri(
            name=user.email, issuer_name="EdTech Platform"
        )
        db.add(OtpChallenge(
            user_id=user.id, channel="totp",
            expires_at=datetime.utcnow() + timedelta(minutes=10),
        ))
        return {"totp_secret": user.totp_secret, "totp_uri": uri}

    otp = generate_otp()
    db.add(OtpChallenge(
        user_id=user.id,
        channel=channel,
        otp_hash=hash_otp(otp),
        expires_at=datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES),
    ))
    if channel == "email":
        await send_email(user.email, otp)
    else:
        await send_whatsapp(user.phone or "unknown", otp)
    return {}