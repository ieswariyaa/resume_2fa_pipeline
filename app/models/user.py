from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class User(Base):
    __tablename__='users'
    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(100))
    email: Mapped[str]=mapped_column(String(150), unique=True, index=True)
    phone: Mapped[str]=mapped_column(String(20), nullable=True)
    qualification: Mapped[str]=mapped_column(String(150), nullable=True)
    password_hash: Mapped[str]=mapped_column(String(255))
    is_active: Mapped[bool]=mapped_column(Boolean, default=False)
    totp_secret: Mapped[str]=mapped_column(String(64), nullable=True)
    created_at: Mapped[DateTime]=mapped_column(DateTime, server_default=func.now())