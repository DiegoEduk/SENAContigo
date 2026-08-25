from datetime import date, datetime
from typing import Optional
from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


# TABLA 'acciones' ELIMINADA / DEPRECADA
# Toda la trazabilidad de casos ahora se almacena en la tabla 'seguimientos' (SeguimientoCaso)
"""
class AccionCaso(Base):
    __tablename__ = "acciones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    caso_id: Mapped[int] = mapped_column(ForeignKey("casos.id", ondelete="CASCADE"), nullable=False, index=True)
    responsable_id: Mapped[Optional[int]] = mapped_column(ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    fecha_compromiso: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    fecha_ejecucion: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    estado: Mapped[str] = mapped_column(String(50), default="PENDIENTE")
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    evidencia_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    caso: Mapped["Caso"] = relationship("Caso")
    responsable: Mapped[Optional["Usuario"]] = relationship("Usuario")
"""


