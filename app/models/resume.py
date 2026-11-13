from sqlalchemy import String, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class UserResume(Base):
    __tablename__ = 'user_resumes'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=True)
    filename: Mapped[str] = mapped_column(String(255))
    extracted_json: Mapped[dict] = mapped_column(JSONB)