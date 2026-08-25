from datetime import datetime
from typing import List, Optional
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Caso(Base):
    __tablename__ = "casos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    aprendiz_id: Mapped[int] = mapped_column(ForeignKey("aprendices.id", ondelete="CASCADE"), nullable=False, index=True)
    tipo_caso_id: Mapped[Optional[int]] = mapped_column(ForeignKey("tipos_caso.id", ondelete="SET NULL"), nullable=True, index=True)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    prioridad: Mapped[str] = mapped_column(String(50), default="MEDIA")  # BAJA, MEDIA, ALTA, CRITICA
    estado: Mapped[str] = mapped_column(String(50), default="NUEVO")  # NUEVO, ASIGNADO, EN_ATENCION, EN_ESPERA, ESCALADO, RESUELTO, CERRADO, CANCELADO
    
    responsable_id: Mapped[Optional[int]] = mapped_column(ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    origen: Mapped[str] = mapped_column(String(50), default="MANUAL")  # MANUAL, MOTOR_DE_REGLAS, MANUAL_APRENDIZ

    fecha_creacion: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    fecha_cierre: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    aprendiz: Mapped["Aprendiz"] = relationship("Aprendiz")
    responsable: Mapped[Optional["Usuario"]] = relationship("Usuario")
    tipo_caso: Mapped[Optional["TipoCaso"]] = relationship("TipoCaso")
    seguimientos: Mapped[List["SeguimientoCaso"]] = relationship("SeguimientoCaso", back_populates="caso", cascade="all, delete-orphan")

