from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.audit.models import AuditoriaLog
from app.modules.audit.schemas import AuditoriaLogCreate


class AuditService:
    @staticmethod
    async def record_audit(session: AsyncSession, audit_in: AuditoriaLogCreate) -> AuditoriaLog:
        log = AuditoriaLog(**audit_in.model_dump())
        session.add(log)
        await session.commit()
        await session.refresh(log)
        return log

    @staticmethod
    async def list_audit_logs(
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        entidad: Optional[str] = None,
        usuario_id: Optional[int] = None
    ) -> List[AuditoriaLog]:
        stmt = select(AuditoriaLog).options(selectinload(AuditoriaLog.usuario)).order_by(AuditoriaLog.created_at.desc())
        if entidad:
            stmt = stmt.where(AuditoriaLog.entidad == entidad)
        if usuario_id:
            stmt = stmt.where(AuditoriaLog.usuario_id == usuario_id)

        stmt = stmt.offset(skip).limit(limit)
        res = await session.execute(stmt)
        return list(res.scalars().all())
