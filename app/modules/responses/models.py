from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Respuesta(Base):
    __tablename__ = "respuestas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    aprendiz_id: Mapped[int] = mapped_column(ForeignKey("aprendices.id", ondelete="CASCADE"), nullable=False, index=True)
    variable_id: Mapped[int] = mapped_column(ForeignKey("variables.id", ondelete="CASCADE"), nullable=False, index=True)
    variable_version_id: Mapped[int] = mapped_column(ForeignKey("variable_versiones.id", ondelete="CASCADE"), nullable=False)
    opcion_id: Mapped[Optional[int]] = mapped_column(ForeignKey("opciones_variable.id", ondelete="SET NULL"), nullable=True)
    encuesta_id: Mapped[Optional[int]] = mapped_column(ForeignKey("encuestas.id", ondelete="SET NULL"), nullable=True)
    corte_id: Mapped[Optional[int]] = mapped_column(ForeignKey("cortes_encuesta.id", ondelete="SET NULL"), nullable=True)

    valor_texto: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    valor_numero: Mapped[Optional[float]] = mapped_column(Text, nullable=True)

    fecha_respuesta: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    registrado_por_usuario_id: Mapped[Optional[int]] = mapped_column(ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True)
    origen: Mapped[str] = mapped_column(String(50), default="web")  # web, movil, auto_registro
    ip_origen: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    aprendiz: Mapped["Aprendiz"] = relationship("Aprendiz")
    variable: Mapped["Variable"] = relationship("Variable")
    version: Mapped["VariableVersion"] = relationship("VariableVersion")
    opcion: Mapped[Optional["OpcionVariable"]] = relationship("OpcionVariable")
