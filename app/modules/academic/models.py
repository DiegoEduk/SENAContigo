from datetime import date, datetime
from typing import List, Optional
from app.modules.organization.models import CentroFormacion
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, ForeignKeyConstraint, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ProgramaFormacion(Base):
    __tablename__ = "programas"

    codigo_programa: Mapped[str] = mapped_column(String(50), primary_key=True, index=True, nullable=False)
    version: Mapped[str] = mapped_column(String(20), primary_key=True, nullable=False, default="1")
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    nivel_formacion: Mapped[str] = mapped_column(String(50), nullable=False)  # Auxiliar, Operario, Técnico, Tecnólogo, Curso especial
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    fichas: Mapped[List["Ficha"]] = relationship("Ficha", back_populates="programa")


class Ficha(Base):
    __tablename__ = "fichas"

    __table_args__ = (
        ForeignKeyConstraint(
            ["programa_codigo", "programa_version"],
            ["programas.codigo_programa", "programas.version"],
            ondelete="CASCADE"
        ),
    )

    ficha_caracterizacion: Mapped[str] = mapped_column(String(50), primary_key=True, index=True, nullable=False)
    fecha_inicial: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_final: Mapped[date] = mapped_column(Date, nullable=False)
    estado_ficha: Mapped[str] = mapped_column(String(50), nullable=False, default="En ejecución")  # En ejecución, Cancelada, Terminada, etc.
    centro_id: Mapped[str] = mapped_column(String(20), ForeignKey("centros.codigo_centro", ondelete="CASCADE"), nullable=False, index=True)
    programa_codigo: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    programa_version: Mapped[str] = mapped_column(String(20), nullable=False, default="1")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    centro: Mapped["CentroFormacion"] = relationship("CentroFormacion")
    programa: Mapped["ProgramaFormacion"] = relationship("ProgramaFormacion", back_populates="fichas")
