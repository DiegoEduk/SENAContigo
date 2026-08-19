from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Notificacion(Base):
    __tablename__ = "notificaciones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    usuario_id: Mapped[Optional[int]] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=True)
    aprendiz_id: Mapped[Optional[int]] = mapped_column(ForeignKey("aprendices.id", ondelete="CASCADE"), nullable=True)
    
    titulo: Mapped[str] = mapped_column(String(150), nullable=False)
    mensaje: Mapped[str] = mapped_column(Text, nullable=False)
    tipo: Mapped[str] = mapped_column(String(50), default="INFO")  # INFO, ALERTA, URGENTE
    leida: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
