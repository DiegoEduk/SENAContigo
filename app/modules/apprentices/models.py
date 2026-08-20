from datetime import datetime
from typing import List, Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Aprendiz(Base):
    __tablename__ = "aprendices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tipo_documento: Mapped[str] = mapped_column(String(10), nullable=False, default="CC")
    numero_documento: Mapped[str] = mapped_column(String(30), unique=True, index=True, nullable=False)
    nombres: Mapped[str] = mapped_column(String(100), nullable=False)
    apellidos: Mapped[str] = mapped_column(String(100), nullable=False)
    correo: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    celular: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    centro_id: Mapped[Optional[int]] = mapped_column(ForeignKey("centros.id", ondelete="SET NULL"), nullable=True)
    regional_id: Mapped[Optional[str]] = mapped_column(String(20), ForeignKey("regionales.codigo_regional", ondelete="SET NULL"), nullable=True)

    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    matriculas: Mapped[List["Matricula"]] = relationship("Matricula", back_populates="aprendiz", cascade="all, delete-orphan")


class Matricula(Base):
    __tablename__ = "matriculas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    aprendiz_id: Mapped[int] = mapped_column(ForeignKey("aprendices.id", ondelete="CASCADE"), nullable=False)
    ficha_id: Mapped[int] = mapped_column(ForeignKey("fichas.id", ondelete="CASCADE"), nullable=False)
    estado_matricula: Mapped[str] = mapped_column(String(50), nullable=False, default="En formación")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    aprendiz: Mapped["Aprendiz"] = relationship("Aprendiz", back_populates="matriculas")
    ficha: Mapped["Ficha"] = relationship("Ficha")
