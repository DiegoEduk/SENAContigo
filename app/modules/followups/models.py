from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class SeguimientoCaso(Base):
    __tablename__ = "seguimientos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    caso_id: Mapped[int] = mapped_column(ForeignKey("casos.id", ondelete="CASCADE"), nullable=False, index=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    
    observacion: Mapped[str] = mapped_column(Text, nullable=False)
    estado_caso_resultante: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    caso: Mapped["Caso"] = relationship("Caso", back_populates="seguimientos")
    usuario: Mapped["Usuario"] = relationship("Usuario")
