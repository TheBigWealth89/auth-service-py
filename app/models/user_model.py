from sqlalchemy import Column, Integer, String, DateTime, func, Boolean
from ..core.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    google_id = Column(String, nullable=True)
    name = Column(String(150), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="user", nullable=False)
    provider = Column(String, default="local")
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<User id={self.id} email={self.email} hashed_password ={self.hashed_password}>"
