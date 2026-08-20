# SENAContigo - Plataforma Institucional de Seguimiento Longitudinal

Plataforma profesional, escalable y mantenible para el **SENA**, diseñada para la identificación, registro, caracterización socioeconómica, seguimiento longitudinal y gestión de casos de aprendices.

Desarrollada rigurosamente a partir de las especificaciones funcionales y no funcionales de **SenaContigo02.pdf**.

---

## 🚀 Visión Arquitectónica y Portales Web

SENAContigo implementa una arquitectura **Modular Monolith** desacoplada con FastAPI en el backend y una interfaz web profesional (Tailwind CSS, HTML5 y Vanilla JS) servida mediante plantillas optimizadas:

```text
                               ┌─────────────────────────────────┐
                               │          FastAPI REST           │
                               │         API Backend v1          │
                               └────────────────┬────────────────┘
                                                │
           ┌────────────────────────────────────┼────────────────────────────────────┐
           │                                    │                                    │
           ▼                                    ▼                                    ▼
┌──────────────────────┐             ┌──────────────────────┐             ┌──────────────────────┐
│  Página de Inicio    │             │  Portal del Aprendiz │             │  Portal de Usuarios  │
│        ( / )         │             │     ( /aprendiz )    │             │     ( /usuarios )    │
│ Acceso Staff / Admin │             │ Documento + Ficha    │             │ Dashboard Staff/Admin│
└──────────────────────┘             └──────────────────────┘             └──────────────────────┘
```

---

## 🖥️ Portales de Acceso Frontend

La aplicación cuenta con portales web independientes adaptados a las necesidades de cada perfil:

1. **Página de Inicio Institucional (`/` - `index.html`)**:
   - Presentación de la plataforma SENAContigo v1.0.
   - Tarjeta de ingreso exclusivo para usuarios administrativos, instructores y staff con correo y contraseña.
   - Enlace directo al **Portal del Aprendiz** en la parte superior derecha del encabezado.

2. **Portal del Aprendiz (`/aprendiz` - `aprendiz.html`)**:
   - **Acceso Público Directo**: Autenticación sin contraseña mediante **Número de Documento** y **Número de Ficha de Formación**.
   - **Mi Perfil Personal**: Consulta y actualización de datos de contacto y residencia en tiempo real (protegiendo la inmutabilidad de documento).
   - **Encuestas Pendientes**: Diligenciamiento interactivo de encuestas socioeconómicas y medición de afectaciones.
   - **Mi Contrato de Aprendizaje**: Registro y consulta del historial de patrocinio y etapa práctica en empresas.
   - **Mis Beneficios SENA**: Solicitud y seguimiento a beneficios y auxilios institucionales (alimentación, salud mental, transporte).
   - **Evolución Histórica**: Trazabilidad longitudinal de las mediciones del aprendiz.

3. **Portal de Usuarios y Staff (`/usuarios` o `/dashboard` - `dashboard.html`)**:
   - **Dashboard Administrativo**: Tableros analíticos y métricas clave de atención.
   - **Gestión de Aprendices**: Búsqueda, caracterización y detalle de expedientes.
   - **Seguimiento a Casos y Novedades**: Gestión de afectaciones y registro de notas de evolución.
   - **Fichas y Programas**: Control académico por centro de formación y regional.
   - **Catálogo de Beneficios**: Administración y asignación directa de auxilios institucionales.
   - **Gestión de Usuarios y Roles**: Administración de accesos basados en roles SENA (`SuperAdmin`, `Dirección`, `Coordinador`, `Instructor`, `Líder Bienestar`, `Líder Contratación`).

---

## 🔑 Endpoints Clave de la API REST Backend (`/api/v1`)

### 1. Autenticación e Identidad (`/api/v1/auth`)
- `POST /api/v1/auth/login`: Autenticar usuario administrativo / instructor (Correo + Contraseña).
- `POST /api/v1/auth/aprendiz-login`: Autenticación pública del aprendiz (Documento + Ficha).
- `GET /api/v1/auth/me`: Obtener perfil e información de la sesión activa.

### 2. Portal Público del Aprendiz (`/api/v1/portal`)
- `GET /api/v1/portal/perfil`: Consultar información personal del aprendiz autenticado.
- `PUT /api/v1/portal/perfil`: Actualizar datos de contacto y residencia del aprendiz.
- `GET /api/v1/portal/contratos`: Listar contratos de aprendizaje del aprendiz.
- `POST /api/v1/portal/contratos`: Registrar un nuevo contrato de aprendizaje.
- `GET /api/v1/portal/beneficios`: Consultar beneficios otorgados o disponibles.
- `POST /api/v1/portal/beneficios`: Solicitar o registrar un beneficio SENA.
- `GET /api/v1/portal/encuestas-pendientes`: Obtener encuestas socioeconómicas activas.
- `POST /api/v1/portal/respuestas-encuesta`: Enviar respuestas de medición socioeconómica.

### 3. Módulos Institucionales y Caso Management
- `/api/v1/aprendices`: Gestión integral de aprendices y matrículas.
- `/api/v1/fichas`: Gestión de fichas de formación y programas.
- `/api/v1/beneficios`: Catálogo global y asignaciones directas.
- `/api/v1/encuestas`: Definición de encuestas, cortes y motor de variables.
- `/api/v1/casos`: Gestión de casos de atención, seguimiento y novedades.
- `/api/v1/reportes`: Indicadores analíticos y cálculo de nivel de afectación.
- `/api/v1/health`: Verificación del estado del servidor API backend.

---

## ⚙️ Principios Arquitectónicos

1. **Historial Inmutable (Longitudinal)**: Las mediciones de los aprendices se registran como snapshots históricos inmutables.
2. **Configuración sobre Código**: Motor de variables socioeconómicas y opciones con escalas de afectación configurables.
3. **Motor de Reglas y Case Management**: Reglas dinámicas `IF condición THEN acción` para apertura de casos y alertas.
4. **Beneficios Institucionales Directos**: Asignación automática de derechos por matrícula (Póliza estudiantil, biblioteca, salud, deportes).
5. **Seguridad Scoped (RBAC)**: Filtrado por rol y nivel organizacional SENA.

---

## 🛠️ Stack Tecnológico

- **Lenguaje**: Python 3.10+
- **Framework Web**: FastAPI
- **Frontend**: HTML5, Vanilla JavaScript (ES6+), Tailwind CSS CDN, FontAwesome 6
- **ORM / Persistencia**: SQLAlchemy 2.0 Async engine & AsyncSession
- **Base de Datos**: SQLite (desarrollo local `senacontigo.db`) / PostgreSQL 16 (producción)
- **Validación de Datos**: Pydantic 2.x
- **Seguridad**: JWT Bearer Tokens, Hashing Bcrypt
- **Testing**: Pytest, pytest-asyncio, HTTPX AsyncClient

---

## 📦 Estructura Modular del Proyecto

```text
SENAContigo/
├── app/
│   ├── api/                # Router central /api/v1
│   ├── core/               # Configuración, BD Async, Seguridad, Excepciones
│   ├── modules/            # Módulos de dominio (identity, academic, apprentices, benefits, surveys, cases, etc.)
│   ├── main.py             # Aplicación FastAPI y rutas web
│   └── seed.py             # Poblador de datos de prueba
├── templates/
│   ├── index.html          # Página de Inicio & Ingreso Usuarios
│   ├── aprendiz.html       # Portal del Aprendiz SENAContigo v1.0
│   └── dashboard.html      # Portal de Usuarios y Staff
├── static/
│   ├── css/                # Estilos personalizados
│   └── js/
│       ├── api.js          # Cliente API centralizado y notificaciones Toast
│       ├── aprendiz.js     # Controlador del Portal del Aprendiz
│       └── dashboard.js    # Controlador del Portal de Usuarios
├── tests/                  # Suite de pruebas automatizadas con Pytest
├── requirements.txt        # Dependencias Python
└── README.md               # Documentación del proyecto
```

---

## ⚡ Ejecución Local

### 1. Preparar entorno e instalar dependencias
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Iniciar la aplicación
```bash
uvicorn app.main:app --reload --port 8000
```
- **Página de Inicio / Usuarios**: `http://localhost:8000/`
- **Portal del Aprendiz**: `http://localhost:8000/aprendiz`
- **Portal de Usuarios**: `http://localhost:8000/usuarios`
- **Documentación API Swagger UI**: `http://localhost:8000/docs`

### 3. Ejecutar Pruebas Automatizadas
```bash
PYTHONPATH=. .venv/bin/python -m pytest tests/ -v
```

---

## 📄 Licencia y Créditos
Desarrollado para el **Servicio Nacional de Aprendizaje (SENA)** - Legarda. Todos los derechos reservados.
