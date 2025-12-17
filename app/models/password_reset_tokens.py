from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean, func
from ..core.db import Base


class PasswordResetToken(Base):
    __tablename__ = "reset_password_tokens"

    id = Column(String(64), primary_key=True)   # token_id (uuid hex)
    user_id = Column(Integer, ForeignKey("users.id"),
                     unique=True, nullable=False)
    hashed_token = Column(String(255), nullable=False)
    last_email_sent_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)
