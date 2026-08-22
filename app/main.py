import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

import app.models  # noqa: F401
from app.api.router import api_router
from app.core.config import settings
from app.core.database import Base, engine
from app.core.exceptions import SENAContigoException, custom_http_exception_handler
from app.core.time import setup_colombia_timezone
from app.seed import seed_data

# Configurar zona horaria de Colombia (America/Bogota, UTC-5)
setup_colombia_timezone()


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

# CORS Middleware (Permite peticiones cross-origin desde cualquier origen sin bloqueos)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 Router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Remote API Transparent Proxy (Bypasses Browser CORS restrictions when running locally)
import httpx
REMOTE_API_BASE = "http://uc0w0o00cgwg4wk0kkogog4g.72.62.13.66.sslip.io/api/v1"

@app.api_route("/proxy-api/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"], include_in_schema=False)
async def proxy_remote_api(request: Request, path: str):
    url = f"{REMOTE_API_BASE}/{path}"
    if request.url.query:
        url += f"?{request.url.query}"

    headers = {}
    if "authorization" in request.headers:
        headers["Authorization"] = request.headers["authorization"]
    if "content-type" in request.headers:
        headers["Content-Type"] = request.headers["content-type"]

    body = await request.body()
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            resp = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=body
            )
            return Response(
                content=resp.content,
                status_code=resp.status_code,
                headers={"Content-Type": resp.headers.get("content-type", "application/json")}
            )
        except httpx.HTTPError as exc:
            return JSONResponse(
                status_code=502,
                content={"detail": f"Error conectando a la API remota: {str(exc)}"}
            )


# Mount Static Files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Web Frontend Routes
@app.get("/", include_in_schema=False)
async def serve_index():
    return FileResponse("templates/index.html")

@app.get("/dashboard", include_in_schema=False)
@app.get("/usuarios", include_in_schema=False)
async def serve_dashboard():
    return FileResponse("templates/dashboard.html")

@app.get("/aprendiz", include_in_schema=False)
@app.get("/portal-aprendiz", include_in_schema=False)
async def serve_aprendiz():
    return FileResponse("templates/aprendiz.html")

@app.get("/api/v1/health", tags=["Health Check"])
async def health():
    return {"status": "ok", "service": "SENAContigo API Backend"}
