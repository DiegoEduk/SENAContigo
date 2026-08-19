from datetime import date, datetime
from typing import List, Optional
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Encuesta(Base):
    __tablename__ = "encuestas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tipo: Mapped[str] = mapped_column(String(50), default="seguimiento_emergencia")  # inicial, seguimiento, caracterizacion
    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_fin: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    estado: Mapped[str] = mapped_column(String(50), default="publicada")  # borrador, publicada, cerrada
    segmento_id: Mapped[Optional[int]] = mapped_column(ForeignKey("segmentos.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    variables_asociadas: Mapped[List["EncuestaVariable"]] = relationship("EncuestaVariable", back_populates="encuesta", cascade="all, delete-orphan")
    cortes: Mapped[List["CorteEncuesta"]] = relationship("CorteEncuesta", back_populates="encuesta", cascade="all, delete-orphan")


class EncuestaVariable(Base):
    __tablename__ = "encuesta_variables"

    encuesta_id: Mapped[int] = mapped_column(ForeignKey("encuestas.id", ondelete="CASCADE"), primary_key=True)
    variable_id: Mapped[int] = mapped_column(ForeignKey("variables.id", ondelete="CASCADE"), primary_key=True)
    orden: Mapped[int] = mapped_column(Integer, default=0)

    encuesta: Mapped["Encuesta"] = relationship("Encuesta", back_populates="variables_asociadas")
    variable: Mapped["Variable"] = relationship("Variable")


class CorteEncuesta(Base):
    __tablename__ = "cortes_encuesta"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    encuesta_id: Mapped[int] = mapped_column(ForeignKey("encuestas.id", ondelete="CASCADE"), nullable=False)
    nombre_corte: Mapped[str] = mapped_column(String(100), nullable=False)  # ej. "Medición Inicial 18/08", "Corte 25/08"
    fecha_corte: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    encuesta: Mapped["Encuesta"] = relationship("Encuesta", back_populates="cortes")
