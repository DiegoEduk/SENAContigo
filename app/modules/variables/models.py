from datetime import datetime
from typing import List, Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CategoriaVariable(Base):
    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    activa: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    variables: Mapped[List["Variable"]] = relationship("Variable", back_populates="categoria")


class Variable(Base):
    __tablename__ = "variables"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categorias.id", ondelete="CASCADE"), nullable=False)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tipo_respuesta: Mapped[str] = mapped_column(String(50), nullable=False, default="opcion_unica")  # opcion_unica, opcion_multiple, texto, numero
    version_actual: Mapped[int] = mapped_column(Integer, default=1)
    es_sensible: Mapped[bool] = mapped_column(Boolean, default=False)
    es_obligatoria: Mapped[bool] = mapped_column(Boolean, default=True)
    activa: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    categoria: Mapped["CategoriaVariable"] = relationship("CategoriaVariable", back_populates="variables")
    versiones: Mapped[List["VariableVersion"]] = relationship("VariableVersion", back_populates="variable", cascade="all, delete-orphan")


class VariableVersion(Base):
    __tablename__ = "variable_versiones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    variable_id: Mapped[int] = mapped_column(ForeignKey("variables.id", ondelete="CASCADE"), nullable=False)
    numero_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    titulo_pregunta: Mapped[str] = mapped_column(String(255), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    activa: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    variable: Mapped["Variable"] = relationship("Variable", back_populates="versiones")
    opciones: Mapped[List["OpcionVariable"]] = relationship("OpcionVariable", back_populates="version", cascade="all, delete-orphan")


class OpcionVariable(Base):
    __tablename__ = "opciones_variable"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    variable_version_id: Mapped[int] = mapped_column(ForeignKey("variable_versiones.id", ondelete="CASCADE"), nullable=False)
    codigo: Mapped[str] = mapped_column(String(50), nullable=False)
    texto: Mapped[str] = mapped_column(String(255), nullable=False)
    valor_numerico: Mapped[int] = mapped_column(Integer, default=0)
    orden: Mapped[int] = mapped_column(Integer, default=0)
    nivel_afectacion: Mapped[int] = mapped_column(Integer, default=0)  # 0=Sin afectacion, 1=Leve, 2=Moderada, 3=Grave, 4=Critica
    activa: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    version: Mapped["VariableVersion"] = relationship("VariableVersion", back_populates="opciones")
