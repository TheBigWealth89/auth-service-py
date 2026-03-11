from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, func
from ..core.db import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(String(64), primary_key=True)   # token_id (uuid hex)
    user_id = Column(UUID(as_uuid=True), ForeignKey(
        "users.id"), nullable=False)
    token_hash = Column(String(512), nullable=False)
    revoked = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
