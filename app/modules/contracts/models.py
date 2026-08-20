from datetime import date, datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.modules.apprentices.models import Matricula


class ContratoAprendizaje(Base):
    __tablename__ = "contratos_aprendizaje"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    matricula_id: Mapped[int] = mapped_column(
        ForeignKey("matriculas.id", ondelete="CASCADE"), nullable=False, index=True
    )
    nombre_empresa: Mapped[str] = mapped_column(String(150), nullable=False)
    departamento: Mapped[str] = mapped_column(String(100), nullable=False)
    ciudad: Mapped[str] = mapped_column(String(100), nullable=False)
    fecha_inicio_contrato: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_fin_contrato: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    estado_contrato: Mapped[str] = mapped_column(String(50), nullable=False, default="EN PATROCINIO")
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    matricula: Mapped["Matricula"] = relationship("Matricula", back_populates="contratos")
