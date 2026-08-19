from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Segmento(Base):
    __tablename__ = "segmentos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Filtros dinámicos
    regional_id: Mapped[Optional[int]] = mapped_column(ForeignKey("regionales.id", ondelete="SET NULL"), nullable=True)
    centro_id: Mapped[Optional[int]] = mapped_column(ForeignKey("centros.id", ondelete="SET NULL"), nullable=True)
    programa_id: Mapped[Optional[int]] = mapped_column(ForeignKey("programas.id", ondelete="SET NULL"), nullable=True)
    ficha_id: Mapped[Optional[int]] = mapped_column(ForeignKey("fichas.id", ondelete="SET NULL"), nullable=True)
    solo_afectados: Mapped[bool] = mapped_column(Boolean, default=False)
    nivel_afectacion_minimo: Mapped[int] = mapped_column(Integer, default=0)

    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
