from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Beneficio(Base):
    __tablename__ = "beneficios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tipo_beneficio: Mapped[str] = mapped_column(String(50), default="INSTITUCIONAL_AUTOMATICO")  # INSTITUCIONAL_AUTOMATICO, SALUD_Y_PROTECCION, CULTURA_Y_DEPORTE, APOYO_FINANCIERO
    es_automatico_matricula: Mapped[bool] = mapped_column(Boolean, default=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AprendizBeneficio(Base):
    __tablename__ = "aprendiz_beneficios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    aprendiz_id: Mapped[int] = mapped_column(ForeignKey("aprendices.id", ondelete="CASCADE"), nullable=False, index=True)
    beneficio_id: Mapped[int] = mapped_column(ForeignKey("beneficios.id", ondelete="CASCADE"), nullable=False, index=True)
    fecha_asignacion: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    estado: Mapped[str] = mapped_column(String(50), default="ACTIVO")  # ACTIVO, SUSPENDIDO, VENCIDO, FINALIZADO
    origen: Mapped[str] = mapped_column(String(50), default="MATRICULA_AUTOMATICA")  # MATRICULA_AUTOMATICA, ASIGNACION_DIRECTA, GESTION_BIENESTAR
    caso_id: Mapped[Optional[int]] = mapped_column(ForeignKey("casos.id", ondelete="SET NULL"), nullable=True)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    aprendiz: Mapped["Aprendiz"] = relationship("Aprendiz")
    beneficio: Mapped["Beneficio"] = relationship("Beneficio")
    caso: Mapped[Optional["Caso"]] = relationship("Caso")
