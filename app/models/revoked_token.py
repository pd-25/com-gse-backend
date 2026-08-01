from datetime import datetime

from sqlalchemy import Column, DateTime, String, text

from app.database.base_class import Base


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    jti = Column(String(32), primary_key=True)
    token_type = Column(String(20), nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.now,
        server_default=text("CURRENT_TIMESTAMP"),
    )
