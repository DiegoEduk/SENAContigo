from fastapi import APIRouter
import app.models  # noqa: F401

from app.modules.academic.router import fichas_router, programas_router

from app.modules.analytics.router import router as analytics_router
from app.modules.apprentices.router import aprendices_router, matriculas_router
from app.modules.audit.router import router as audit_router
from app.modules.benefits.router import router as beneficios_router
from app.modules.cases.router import router as casos_router
from app.modules.contracts.router import router as contratos_router
from app.modules.followups.router import router as seguimientos_router
from app.modules.identity.router import router as auth_router, users_router
from app.modules.needs.router import router as necesidades_router
from app.modules.notifications.router import router as notificaciones_router
from app.modules.organization.router import centros_router, regionales_router
from app.modules.portal.router import router as portal_router
from app.modules.responses.router import router as respuestas_router
from app.modules.rules.router import router as reglas_router
from app.modules.segments.router import router as segmentos_router
from app.modules.surveys.router import router as encuestas_router
from app.modules.variables.router import router as variables_router

api_router = APIRouter()

# Identidad, Autenticación y Portal del Aprendiz
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(portal_router)


# Estructura SENA
api_router.include_router(regionales_router)
api_router.include_router(centros_router)

# Gestión Académica
api_router.include_router(programas_router)
api_router.include_router(fichas_router)

# Aprendices y Matrículas
api_router.include_router(aprendices_router)
api_router.include_router(matriculas_router)

# Contratación de Aprendices
api_router.include_router(contratos_router)

# Beneficios Institucionales del Aprendiz
api_router.include_router(beneficios_router)

# Engine de Variables y Encuestas
api_router.include_router(variables_router)
api_router.include_router(encuestas_router)

# Respuestas y Medición Longitudinal
api_router.include_router(respuestas_router)
api_router.include_router(segmentos_router)

# Reglas y Casos de Atención
api_router.include_router(reglas_router)
api_router.include_router(necesidades_router)
api_router.include_router(casos_router)
api_router.include_router(seguimientos_router)


# Analítica, Notificaciones y Auditoría
api_router.include_router(analytics_router)
api_router.include_router(notificaciones_router)
api_router.include_router(audit_router)

