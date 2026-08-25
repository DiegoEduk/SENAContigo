from datetime import datetime
from typing import List, Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Regla(Base):
    __tablename__ = "reglas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    activa: Mapped[bool] = mapped_column(Boolean, default=True)
    prioridad: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    condiciones: Mapped[List["ReglaCondicion"]] = relationship("ReglaCondicion", back_populates="regla", cascade="all, delete-orphan")
    acciones: Mapped[List["ReglaAccion"]] = relationship("ReglaAccion", back_populates="regla", cascade="all, delete-orphan")


class ReglaCondicion(Base):
    __tablename__ = "regla_condiciones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    regla_id: Mapped[int] = mapped_column(ForeignKey("reglas.id", ondelete="CASCADE"), nullable=False)
    variable_id: Mapped[int] = mapped_column(ForeignKey("variables.id", ondelete="CASCADE"), nullable=False)
    opcion_id: Mapped[Optional[int]] = mapped_column(ForeignKey("opciones_variable.id", ondelete="SET NULL"), nullable=True)
    operador: Mapped[str] = mapped_column(String(20), default="EQUALS")  # EQUALS, NOT_EQUALS, GREATER_THAN, IN
    valor_comparar: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    regla: Mapped["Regla"] = relationship("Regla", back_populates="condiciones")
    variable: Mapped["Variable"] = relationship("Variable")
    opcion: Mapped[Optional["OpcionVariable"]] = relationship("OpcionVariable")


class ReglaAccion(Base):
    __tablename__ = "regla_acciones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    regla_id: Mapped[int] = mapped_column(ForeignKey("reglas.id", ondelete="CASCADE"), nullable=False)
    tipo_accion: Mapped[str] = mapped_column(String(50), nullable=False)  # CREAR_CASO, CREAR_NOTIFICACION
    tipo_caso_id: Mapped[Optional[int]] = mapped_column(ForeignKey("tipos_caso.id", ondelete="SET NULL"), nullable=True)
    prioridad_caso: Mapped[str] = mapped_column(String(50), default="MEDIA")  # ALTA, CRITICA, MEDIA, BAJA
    titulo_caso: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    mensaje_notificacion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    regla: Mapped["Regla"] = relationship("Regla", back_populates="acciones")
    tipo_caso: Mapped[Optional["TipoCaso"]] = relationship("TipoCaso")

