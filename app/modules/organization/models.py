from datetime import datetime
from typing import List, Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Regional(Base):
    __tablename__ = "regionales"

    codigo_regional: Mapped[str] = mapped_column(String(20), primary_key=True, index=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    centros: Mapped[List["CentroFormacion"]] = relationship("CentroFormacion", back_populates="regional", cascade="all, delete-orphan")


class CentroFormacion(Base):
    __tablename__ = "centros"

    codigo_centro: Mapped[str] = mapped_column(String(20), primary_key=True, index=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    regional_id: Mapped[str] = mapped_column(ForeignKey("regionales.codigo_regional", ondelete="CASCADE"), nullable=False, index=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    regional: Mapped["Regional"] = relationship("Regional", back_populates="centros")
