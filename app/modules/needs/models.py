from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TipoCaso(Base):
    __tablename__ = "tipos_caso"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    categoria_relacionada: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    activa: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# Alias para retrocompatibilidad
Necesidad = TipoCaso

