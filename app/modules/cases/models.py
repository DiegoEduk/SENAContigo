from datetime import datetime
from typing import List, Optional
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Caso(Base):
    __tablename__ = "casos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    aprendiz_id: Mapped[int] = mapped_column(ForeignKey("aprendices.id", ondelete="CASCADE"), nullable=False, index=True)
    tipo: Mapped[str] = mapped_column(String(100), nullable=False)  # ej. SITUACIÓN HABITACIONAL, RIESGO CONTINUIDAD
    prioridad: Mapped[str] = mapped_column(String(50), default="MEDIA")  # BAJA, MEDIA, ALTA, CRITICA
    estado: Mapped[str] = mapped_column(String(50), default="NUEVO")  # NUEVO, ASIGNADO, EN_ATENCION, EN_ESPERA, ESCALADO, RESUELTO, CERRADO, CANCELADO
    
    responsable_id: Mapped[Optional[int]] = mapped_column(ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    origen: Mapped[str] = mapped_column(String(50), default="MANUAL")  # MANUAL, MOTOR_DE_REGLAS

    fecha_creacion: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    fecha_cierre: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    aprendiz: Mapped["Aprendiz"] = relationship("Aprendiz")
    responsable: Mapped[Optional["Usuario"]] = relationship("Usuario")
    necesidades_asociadas: Mapped[List["CasoNecesidad"]] = relationship("CasoNecesidad", back_populates="caso", cascade="all, delete-orphan")
    acciones: Mapped[List["AccionCaso"]] = relationship("AccionCaso", back_populates="caso", cascade="all, delete-orphan")
    seguimientos: Mapped[List["SeguimientoCaso"]] = relationship("SeguimientoCaso", back_populates="caso", cascade="all, delete-orphan")


class CasoNecesidad(Base):
    __tablename__ = "caso_necesidades"

    caso_id: Mapped[int] = mapped_column(ForeignKey("casos.id", ondelete="CASCADE"), primary_key=True)
    necesidad_id: Mapped[int] = mapped_column(ForeignKey("necesidades.id", ondelete="CASCADE"), primary_key=True)

    caso: Mapped["Caso"] = relationship("Caso", back_populates="necesidades_asociadas")
    necesidad: Mapped["Necesidad"] = relationship("Necesidad")
