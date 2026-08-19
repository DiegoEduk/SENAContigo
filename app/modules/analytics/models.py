from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PesoIndicador(Base):
    __tablename__ = "pesos_indicadores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categorias.id", ondelete="CASCADE"), nullable=False)
    peso: Mapped[float] = mapped_column(Numeric(5, 2), default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    categoria: Mapped["CategoriaVariable"] = relationship("CategoriaVariable")


class IndicadorLog(Base):
    __tablename__ = "indicadores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre_indicador: Mapped[str] = mapped_column(String(100), nullable=False)
    nivel_agregacion: Mapped[str] = mapped_column(String(50), nullable=False)  # SENA, REGIONAL, CENTRO, FICHA
    entidad_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    valor_calculado: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    fecha_calculo: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
