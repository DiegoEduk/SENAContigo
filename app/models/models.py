from datetime import datetime
from typing import Optional, List
from enum import Enum as PyEnum
from sqlalchemy import (
    String, Integer, Float, Boolean, Text, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


# Enums de Dominio
class RolUsuario(str, PyEnum):
    SUPERADMIN = "superadmin"
    DIRECCION = "direccion"
    COORDINADOR = "coordinador"
    INSTRUCTOR = "instructor"
    APRENDIZ = "aprendiz"


class TipoRespuesta(str, PyEnum):
    OPCION = "opcion"
    TEXTO = "texto"
    NUMERO = "numero"


class EstadoEncuesta(str, PyEnum):
    BORRADOR = "borrador"
    ACTIVA = "activa"
    CERRADA = "cerrada"


class TipoEncuesta(str, PyEnum):
    INICIAL = "inicial"
    SEGUIMIENTO = "seguimiento"
    EMERGENCIA = "emergencia"


class Prioridad(str, PyEnum):
    BAJA = "BAJA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"
    CRITICA = "CRITICA"


class EstadoCaso(str, PyEnum):
    ABIERTO = "ABIERTO"
    EN_PROCESO = "EN_PROCESO"
    RESUELTO = "RESUELTO"
    CANCELADO = "CANCELADO"


class Regional(Base):
    __tablename__ = "regionales"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo_regional: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)

    centros: Mapped[List["CentroFormacion"]] = relationship("CentroFormacion", back_populates="regional", cascade="all, delete-orphan")
    usuarios: Mapped[List["Usuario"]] = relationship("Usuario", back_populates="regional")


class CentroFormacion(Base):
    __tablename__ = "centros_formacion"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo_centro: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    regional_id: Mapped[int] = mapped_column(Integer, ForeignKey("regionales.id", ondelete="CASCADE"), nullable=False)

    regional: Mapped["Regional"] = relationship("Regional", back_populates="centros")
    fichas: Mapped[List["Ficha"]] = relationship("Ficha", back_populates="centro", cascade="all, delete-orphan")
    usuarios: Mapped[List["Usuario"]] = relationship("Usuario", back_populates="centro")


class ProgramaFormacion(Base):
    __tablename__ = "programas_formacion"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo_programa: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    version: Mapped[str] = mapped_column(String(20), nullable=False)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    nivel_formacion: Mapped[str] = mapped_column(String(100), nullable=False)
    estado: Mapped[str] = mapped_column(String(50), default="ACTIVO", nullable=False)

    fichas: Mapped[List["Ficha"]] = relationship("Ficha", back_populates="programa")


class Ficha(Base):
    __tablename__ = "fichas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ficha_caracterizacion: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    fecha_inicial: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    fecha_final: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    estado_ficha: Mapped[str] = mapped_column(String(50), default="LECTIVA", nullable=False)
    centro_id: Mapped[int] = mapped_column(Integer, ForeignKey("centros_formacion.id"), nullable=False)
    programa_id: Mapped[int] = mapped_column(Integer, ForeignKey("programas_formacion.id"), nullable=False)

    centro: Mapped["CentroFormacion"] = relationship("CentroFormacion", back_populates="fichas")
    programa: Mapped["ProgramaFormacion"] = relationship("ProgramaFormacion", back_populates="fichas")
    aprendices: Mapped[List["AprendizFicha"]] = relationship("AprendizFicha", back_populates="ficha", cascade="all, delete-orphan")


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tipo_documento: Mapped[str] = mapped_column(String(20), nullable=False)
    numero_documento: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    nombres: Mapped[str] = mapped_column(String(100), nullable=False)
    apellidos: Mapped[str] = mapped_column(String(100), nullable=False)
    celular: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    correo_electronico: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    rol: Mapped[str] = mapped_column(String(50), nullable=False)  # 'superadmin', 'direccion', 'coordinador', 'instructor', 'aprendiz'
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    centro_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("centros_formacion.id", ondelete="SET NULL"), nullable=True)
    regional_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("regionales.id", ondelete="SET NULL"), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    centro: Mapped[Optional["CentroFormacion"]] = relationship("CentroFormacion", back_populates="usuarios")
    regional: Mapped[Optional["Regional"]] = relationship("Regional", back_populates="usuarios")
    fichas_aprendiz: Mapped[List["AprendizFicha"]] = relationship("AprendizFicha", back_populates="aprendiz", cascade="all, delete-orphan")
    respuestas: Mapped[List["Respuesta"]] = relationship("Respuesta", back_populates="aprendiz", cascade="all, delete-orphan")
    casos_reportados: Mapped[List["Caso"]] = relationship("Caso", foreign_keys="Caso.aprendiz_id", back_populates="aprendiz")
    casos_asignados: Mapped[List["Caso"]] = relationship("Caso", foreign_keys="Caso.asignado_a_id", back_populates="asignado_a")
    seguimientos: Mapped[List["SeguimientoCaso"]] = relationship("SeguimientoCaso", back_populates="usuario")


class AprendizFicha(Base):
    __tablename__ = "aprendices_ficha"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    aprendiz_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    ficha_id: Mapped[int] = mapped_column(Integer, ForeignKey("fichas.id", ondelete="CASCADE"), nullable=False)
    estado_matricula: Mapped[str] = mapped_column(String(50), default="EN_FORMACION", nullable=False)

    aprendiz: Mapped["Usuario"] = relationship("Usuario", back_populates="fichas_aprendiz")
    ficha: Mapped["Ficha"] = relationship("Ficha", back_populates="aprendices")


class Categoria(Base):
    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    icono: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    orden: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    variables: Mapped[List["Variable"]] = relationship("Variable", back_populates="categoria", cascade="all, delete-orphan")
    necesidades: Mapped[List["Necesidad"]] = relationship("Necesidad", back_populates="categoria")


class Variable(Base):
    __tablename__ = "variables"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    categoria_id: Mapped[int] = mapped_column(Integer, ForeignKey("categorias.id", ondelete="CASCADE"), nullable=False)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tipo_respuesta: Mapped[str] = mapped_column(String(50), nullable=False)  # 'opcion', 'texto', 'numero'
    obligatoria: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    activa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    categoria: Mapped["Categoria"] = relationship("Categoria", back_populates="variables")
    versiones: Mapped[List["VariableVersion"]] = relationship("VariableVersion", back_populates="variable", cascade="all, delete-orphan")
    opciones: Mapped[List["OpcionVariable"]] = relationship("OpcionVariable", back_populates="variable", cascade="all, delete-orphan")
    preguntas_encuesta: Mapped[List["PreguntaEncuesta"]] = relationship("PreguntaEncuesta", back_populates="variable")
    respuestas: Mapped[List["Respuesta"]] = relationship("Respuesta", back_populates="variable")
    reglas: Mapped[List["Regla"]] = relationship("Regla", back_populates="variable")


class VariableVersion(Base):
    __tablename__ = "variable_versiones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    variable_id: Mapped[int] = mapped_column(Integer, ForeignKey("variables.id", ondelete="CASCADE"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    descripcion_cambio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    variable: Mapped["Variable"] = relationship("Variable", back_populates="versiones")
    opciones: Mapped[List["OpcionVariable"]] = relationship("OpcionVariable", back_populates="version")


class OpcionVariable(Base):
    __tablename__ = "opciones_variable"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    variable_id: Mapped[int] = mapped_column(Integer, ForeignKey("variables.id", ondelete="CASCADE"), nullable=False)
    version_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("variable_versiones.id", ondelete="CASCADE"), nullable=True)
    codigo: Mapped[str] = mapped_column(String(50), nullable=False)
    texto: Mapped[str] = mapped_column(String(255), nullable=False)
    valor_numerico: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    orden: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    nivel_afectacion: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 0: Sin afectación, 1: Leve, 2: Moderada, 3: Grave, 4: Crítica
    activa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    variable: Mapped["Variable"] = relationship("Variable", back_populates="opciones")
    version: Mapped[Optional["VariableVersion"]] = relationship("VariableVersion", back_populates="opciones")
    respuestas: Mapped[List["Respuesta"]] = relationship("Respuesta", back_populates="opcion")
    reglas: Mapped[List["Regla"]] = relationship("Regla", back_populates="opcion")


class Encuesta(Base):
    __tablename__ = "encuestas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    fecha_inicio: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    fecha_fin: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    estado: Mapped[str] = mapped_column(String(50), default="borrador", nullable=False)  # 'borrador', 'activa', 'cerrada'
    tipo: Mapped[str] = mapped_column(String(50), default="emergencia", nullable=False)  # 'inicial', 'seguimiento', 'emergencia'
    segmento_filtro_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    preguntas: Mapped[List["PreguntaEncuesta"]] = relationship("PreguntaEncuesta", back_populates="encuesta", cascade="all, delete-orphan")
    respuestas: Mapped[List["Respuesta"]] = relationship("Respuesta", back_populates="encuesta", cascade="all, delete-orphan")


class PreguntaEncuesta(Base):
    __tablename__ = "preguntas_encuesta"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    encuesta_id: Mapped[int] = mapped_column(Integer, ForeignKey("encuestas.id", ondelete="CASCADE"), nullable=False)
    variable_id: Mapped[int] = mapped_column(Integer, ForeignKey("variables.id", ondelete="CASCADE"), nullable=False)
    orden: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    obligatoria: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    encuesta: Mapped["Encuesta"] = relationship("Encuesta", back_populates="preguntas")
    variable: Mapped["Variable"] = relationship("Variable", back_populates="preguntas_encuesta")


class Respuesta(Base):
    """
    IMPORTANTE: Respuestas longitudinales históricas (nunca se borran ni sobrescriben).
    Permite registrar la evolución del estado de vulnerabilidad/necesidad del aprendiz en el tiempo.
    """
    __tablename__ = "respuestas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    aprendiz_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    encuesta_id: Mapped[int] = mapped_column(Integer, ForeignKey("encuestas.id", ondelete="CASCADE"), nullable=False)
    variable_id: Mapped[int] = mapped_column(Integer, ForeignKey("variables.id", ondelete="CASCADE"), nullable=False)
    opcion_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("opciones_variable.id", ondelete="SET NULL"), nullable=True)
    respuesta_texto: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    fecha_respuesta: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    observacion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    aprendiz: Mapped["Usuario"] = relationship("Usuario", back_populates="respuestas")
    encuesta: Mapped["Encuesta"] = relationship("Encuesta", back_populates="respuestas")
    variable: Mapped["Variable"] = relationship("Variable", back_populates="respuestas")
    opcion: Mapped[Optional["OpcionVariable"]] = relationship("OpcionVariable", back_populates="respuestas")
    casos: Mapped[List["Caso"]] = relationship("Caso", back_populates="respuesta_origen")


class Necesidad(Base):
    __tablename__ = "necesidades"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    prioridad_defecto: Mapped[str] = mapped_column(String(50), default="MEDIA", nullable=False)  # 'BAJA', 'MEDIA', 'ALTA', 'CRITICA'
    categoria_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("categorias.id", ondelete="SET NULL"), nullable=True)

    categoria: Mapped[Optional["Categoria"]] = relationship("Categoria", back_populates="necesidades")
    reglas: Mapped[List["Regla"]] = relationship("Regla", back_populates="necesidad")
    casos: Mapped[List["Caso"]] = relationship("Caso", back_populates="necesidad")


class Regla(Base):
    __tablename__ = "reglas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    variable_id: Mapped[int] = mapped_column(Integer, ForeignKey("variables.id", ondelete="CASCADE"), nullable=False)
    opcion_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("opciones_variable.id", ondelete="CASCADE"), nullable=True)
    nivel_afectacion_minimo: Mapped[Optional[int]] = mapped_column(Integer, default=0, nullable=True)
    necesidad_id: Mapped[int] = mapped_column(Integer, ForeignKey("necesidades.id", ondelete="CASCADE"), nullable=False)
    prioridad: Mapped[str] = mapped_column(String(50), default="ALTA", nullable=False)  # 'BAJA', 'MEDIA', 'ALTA', 'CRITICA'
    activa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    variable: Mapped["Variable"] = relationship("Variable", back_populates="reglas")
    opcion: Mapped[Optional["OpcionVariable"]] = relationship("OpcionVariable", back_populates="reglas")
    necesidad: Mapped["Necesidad"] = relationship("Necesidad", back_populates="reglas")


class Caso(Base):
    __tablename__ = "casos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    aprendiz_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    respuesta_origen_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("respuestas.id", ondelete="SET NULL"), nullable=True)
    necesidad_id: Mapped[int] = mapped_column(Integer, ForeignKey("necesidades.id", ondelete="CASCADE"), nullable=False)
    titulo: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    prioridad: Mapped[str] = mapped_column(String(50), default="MEDIA", nullable=False)  # 'BAJA', 'MEDIA', 'ALTA', 'CRITICA'
    estado: Mapped[str] = mapped_column(String(50), default="ABIERTO", nullable=False)  # 'ABIERTO', 'EN_PROCESO', 'RESUELTO', 'CANCELADO'
    asignado_a_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_cierre: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    aprendiz: Mapped["Usuario"] = relationship("Usuario", foreign_keys=[aprendiz_id], back_populates="casos_reportados")
    respuesta_origen: Mapped[Optional["Respuesta"]] = relationship("Respuesta", back_populates="casos")
    necesidad: Mapped["Necesidad"] = relationship("Necesidad", back_populates="casos")
    asignado_a: Mapped[Optional["Usuario"]] = relationship("Usuario", foreign_keys=[asignado_a_id], back_populates="casos_asignados")
    seguimientos: Mapped[List["SeguimientoCaso"]] = relationship("SeguimientoCaso", back_populates="caso", cascade="all, delete-orphan")


class SeguimientoCaso(Base):
    __tablename__ = "seguimientos_caso"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    caso_id: Mapped[int] = mapped_column(Integer, ForeignKey("casos.id", ondelete="CASCADE"), nullable=False)
    usuario_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    fecha: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    comentario: Mapped[str] = mapped_column(Text, nullable=False)
    nuevo_estado: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    caso: Mapped["Caso"] = relationship("Caso", back_populates="seguimientos")
    usuario: Mapped["Usuario"] = relationship("Usuario", back_populates="seguimientos")
