from datetime import datetime
from sqlalchemy import Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class KeyBundle(Base):
    __tablename__ = "key_bundles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    x25519_public: Mapped[str] = mapped_column(Text)
    ml_kem_public: Mapped[str] = mapped_column(Text)
    ed25519_public: Mapped[str] = mapped_column(Text)
    ml_dsa_public: Mapped[str] = mapped_column(Text)
    x25519_signature: Mapped[str] = mapped_column(Text)
    ml_kem_signature: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())