from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from ..core.db import Base


class EmailVerificationToken(Base):
    __tablename__ = "email_verification_tokens"

    id = Column(String(64), primary_key=True)   # token_id (uuid hex)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    hashed_token = Column(String(255), nullable=False)
    last_email_sent_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)
