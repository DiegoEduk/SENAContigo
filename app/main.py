from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import settings
from app.core.database import Base, engine
from app.core.exceptions import SENAContigoException, custom_http_exception_handler
from app.seed import seed_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure tables exist and initial seed data is loaded
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        await seed_data()
    except Exception as e:
        print(f"Seed warning: {e}")
    yield
    # Shutdown: Close database pool
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="API REST Profesional, Escalable y Mantenible para SENAContigo - Plataforma Institucional de Seguimiento Longitudinal.",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Exception handlers
app.add_exception_handler(HTTPException, custom_http_exception_handler)
app.add_exception_handler(SENAContigoException, custom_http_exception_handler)

# CORS Middleware
if settings.CORS_ORIGINS:
    origins = settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else [settings.CORS_ORIGINS]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API v1 Router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Health Check"])
async def root():
    return {
        "status": "online",
        "system": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs"
    }


@app.get("/api/v1/health", tags=["Health Check"])
async def health():
    return {"status": "ok", "service": "SENAContigo API Backend"}
