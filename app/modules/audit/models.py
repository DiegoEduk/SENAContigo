from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AuditoriaLog(Base):
    __tablename__ = "auditoria"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    usuario_id: Mapped[Optional[int]] = mapped_column(ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    accion: Mapped[str] = mapped_column(String(50), nullable=False)  # CREATE, UPDATE, DELETE, LOGIN, RESPONSE_SUBMIT
    entidad: Mapped[str] = mapped_column(String(100), nullable=False)  # usuarios, variables, respuestas, casos
    entidad_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    valor_anterior: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    valor_nuevo: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ip_origen: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    usuario: Mapped[Optional["Usuario"]] = relationship("Usuario")
