from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user_token, require_roles
from app.core.security import TokenData
from app.modules.audit.schemas import AuditoriaLogRead
from app.modules.audit.services import AuditService

router = APIRouter(prefix="/audit", tags=["Trazabilidad y Auditoría"])


@router.get("", response_model=List[AuditoriaLogRead])
async def list_audit_logs(
    skip: int = 0,
    limit: int = 100,
    entidad: Optional[str] = None,
    usuario_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(require_roles(["superadmin"]))
):
    """Consultar registros de auditoria del sistema (quién hizo qué y cuándo)."""
    return await AuditService.list_audit_logs(db, skip=skip, limit=limit, entidad=entidad, usuario_id=usuario_id)
