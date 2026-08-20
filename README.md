# SENAContigo - Plataforma Institucional de Seguimiento Longitudinal

Plataforma backend profesional, escalable y mantenible para el **SENA**, diseñada para la identificación, registro, seguimiento longitudinal y gestión de casos de aprendices afectados por emergencias u otras eventualidades socioeconómicas y ambientales.

Desarrollada rigurosamente a partir de las especificaciones funcionales y no funcionales de **SenaContigo02.pdf**.

---

## 🚀 Visión Arquitectónica

SENAContigo implementa un patrón **Modular Monolith** desacoplado, exponiendo una **API REST OpenAPI** consumible por aplicaciones web (React/Vite) y móviles (Android/iOS) sin alterar la lógica de negocio.

```text
                 ┌─────────────────────────────────┐
                 │          FastAPI REST           │
                 │         API Backend v1          │
                 └────────────────┬────────────────┘
                                  │
             ┌────────────────────┼────────────────────┐
             │                    │                    │
             ▼                    ▼                    ▼
     Web Client (React)    Android Native App    iOS Native App
```

### Principios Fundamentales
1. **Historial Inmutable (Longitudinal)**: Las mediciones de los aprendices nunca se sobrescriben. Cada consulta genera un nuevo registro preservando la evolución temporal real.
2. **Configuración sobre Código (Motor de Variables)**: Nuevas preguntas, categorías y opciones con escalas de afectación configurables (0 a 4) se administran dinámicamente sin redesplegar código.
3. **Versionamiento de Variables**: Preserva la interpretación histórica de las preguntas aunque cambien en el tiempo.
4. **Motor de Reglas y Case Management**: Motor autónomo `IF condición THEN acción` para auto-generación de Necesidades, Alertas y Casos con prioridades.
5. **Beneficios Institucionales Directos**: Catálogo de derechos y beneficios SENA otorgados automáticamente por el hecho de la matrícula activa (Póliza de seguro estudiantil, biblioteca digital, salud preventiva, deportes), desacoplados de los casos y necesidades de atención de riesgo.
6. **Seguridad Scoped (RBAC)**: Permisos filtrados por nivel organizacional SENA (`SuperAdmin` Nacional, `Dirección` Regional, `Coordinador` de Centro, `Instructor` de Ficha, `Aprendiz`).

---

## 🛠️ Stack Tecnológico

- **Lenguaje**: Python 3.11+
- **Framework Web**: FastAPI
- **ORM / Persistencia**: SQLAlchemy 2.x (usando `DeclarativeBase`, `Mapped`, `mapped_column`)
- **Driver Async DB**: `asyncpg` con `AsyncSession`
- **Base de Datos**: PostgreSQL 16
- **Caché y Tareas**: Redis 7
- **Migraciones**: Alembic (asíncrono)
- **Validación de Datos**: Pydantic 2.x & Pydantic Settings
- **Seguridad y JWT**: OAuth2 Password Bearer, Bcrypt, PyJWT (`python-jose`)
- **Contenedores**: Docker & Docker Compose
- **Testing**: Pytest, pytest-asyncio, HTTPX

---

## 📦 Estructura Modular del Proyecto

```text
app/
├── core/
│   ├── config.py           # Configuración Pydantic BaseSettings
│   ├── database.py         # SQLAlchemy 2.0 AsyncEngine & AsyncSession
│   ├── security.py         # JWT tokens & Hashing Bcrypt
│   ├── exceptions.py       # Exception Handlers centralizados
│   └── dependencies.py     # Inyección de dependencias & Scoped RBAC
├── modules/
│   ├── identity/           # Usuarios, Roles, Permisos
│   ├── organization/       # Regionales, Centros de Formación
│   ├── academic/           # Programas de Formación, Fichas
│   ├── apprentices/        # Aprendices, Matrículas
│   ├── benefits/           # Beneficios Institucionales Directos del Aprendiz
│   ├── variables/          # Categorías, Variables, Versiones, Opciones
│   ├── surveys/            # Encuestas, Cortes de Medición
│   ├── responses/          # Respuestas Longitudinales Inmutables
│   ├── segments/           # Segmentación Dinámica de Aprendices
│   ├── rules/              # Motor de Reglas (IF condition THEN action)
│   ├── needs/              # Catálogo de Necesidades
│   ├── cases/              # Gestión de Casos
│   ├── actions/            # Acciones por Caso
│   ├── followups/          # Seguimiento Longitudinal de Casos
│   ├── analytics/          # Indicadores y Calculador de Afectación
│   ├── notifications/      # Sistema de Alertas y Notificaciones
│   └── audit/              # Trazabilidad y Audit Trail
├── api/
│   └── router.py           # Agregador central /api/v1
├── seed.py                 # Poblador de datos iniciales
└── main.py                 # Entrada principal FastAPI
```

---

## ⚙️ Configuración y Ejecución Local

### 1. Clonar el repositorio
```bash
git clone https://github.com/DiegoEduk/SENAContigo.git
cd SENAContigo
```

### 2. Configurar variables de entorno
```bash
cp .env.example .env
```

### 3. Ejecutar con Docker Compose
```bash
docker-compose up -d --build
```
El backend estará disponible en `http://localhost:8000`.
La documentación Swagger UI interactiva en `http://localhost:8000/docs`.

### 4. Ejecutar suite de pruebas
```bash
PYTHONPATH=. pytest tests/ -v
```

---

## 🌐 Despliegue en VPS con Coolify

El proyecto está listo para ser desplegado en el servidor VPS mediante **Coolify**:

### Pasos para Configurar en Coolify:
1. Acceder al panel de Coolify en `http://72.62.13.66:8000/login`.
2. Crear un nuevo servicio **PostgreSQL 16** con volumen de persistencia.
3. Crear una instancia de **Redis 7**.
4. Crear una nueva aplicación desde el repositorio de GitHub `https://github.com/DiegoEduk/SENAContigo`.
5. Configurar las variables de entorno en Coolify:
   - `DATABASE_URL=postgresql+asyncpg://postgres:<PASSWORD>@<DB_HOST>:5432/senacontigo`
   - `REDIS_URL=redis://<REDIS_HOST>:6379/0`
   - `SECRET_KEY=<CLAVE_SECRETA_PRODUCCION>`
   - `ENVIRONMENT=production`
   - `CORS_ORIGINS=*`
6. Definir el Health Check Endpoint: `/api/v1/health`.
7. Desplegar. El contenedor ejecutará automáticamente `alembic upgrade head`, el poblador inicial `seed.py` y levantará el servidor con Uvicorn.

---

## 📄 Licencia y Créditos
Desarrollado para el **Servicio Nacional de Aprendizaje (SENA)**. Todos los derechos reservados.
