from sqlalchemy import String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class OtpChallenge(Base):
    __tablename__ = 'otp_challenges'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    channel: Mapped[str] = mapped_column(String(20))  
    otp_hash: Mapped[str] = mapped_column(String(128), nullable=True)
    expires_at: Mapped[DateTime] = mapped_column(DateTime)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())