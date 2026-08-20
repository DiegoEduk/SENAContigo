# Diagrama de Flujo de Datos (DFD) y Estructura de Base de Datos - SENAContigo

Este documento proporciona una visión integral del **flujo de datos** y el **modelo entidad-relación (ERD)** de la base de datos de la plataforma **SENAContigo**.

---

## 1. Diagrama del Flujo General de Datos (DFD Nivel 0 / Nivel 1)

El siguiente diagrama representa cómo viaja la información desde la entrada de datos (Aprendices y Usuarios), su almacenamiento en el catálogo de variables/encuestas, su evaluación por el **Motor de Reglas**, la asignación de **Beneficios Institucionales Directos**, la apertura y seguimiento de **Casos de Atención**, hasta la generación de **Notificaciones, Auditoría y Analítica**.

```mermaid
flowchart TD
    subgraph Actores["Actores del Sistema"]
        A[👨‍🎓 Aprendiz]
        U[👨‍💼 Usuario / Profesional Bienestar / Admin]
    end

    subgraph ModuloEstructura["1. Estructura Organizacional y Académica"]
        regionales[(regionales)]
        centros[(centros)]
        programas[(programas)]
        fichas[(fichas)]
        aprendices[(aprendices)]
        matriculas[(matriculas)]
    end

    subgraph ModuloBeneficios["2. Módulo de Beneficios Institucionales Directos"]
        beneficios[(beneficios - Catálogo)]
        aprendiz_beneficios[(aprendiz_beneficios)]
    end

    subgraph ModuloConfig["3. Motor de Variables y Encuestas"]
        categorias[(categorias)]
        variables[(variables)]
        variable_versiones[(variable_versiones)]
        opciones[(opciones_variable)]
        encuestas[(encuestas)]
        cortes[(cortes_encuesta)]
    end

    subgraph ModuloCaptura["4. Captura y Procesamiento de Respuestas"]
        respuestas[(respuestas)]
    end

    subgraph ModuloReglas["5. Motor de Reglas y Automatización"]
        reglas[(reglas)]
        condiciones[(regla_condiciones)]
        acciones_regla[(regla_acciones)]
    end

    subgraph ModuloGestion["6. Gestión de Casos y Seguimiento"]
        necesidades[(necesidades)]
        casos[(casos)]
        caso_necesidades[(caso_necesidades)]
        acciones_caso[(acciones)]
        seguimientos[(seguimientos)]
    end

    subgraph ModuloSalida["7. Analítica, Auditoría y Notificaciones"]
        notificaciones[(notificaciones)]
        auditoria[(auditoria)]
        indicadores[(indicadores / pesos_indicadores)]
    end

    %% Beneficios por Matrícula Directa
    aprendices -->|Al registrar o matricular| AsignadorBeneficios[Process: Asignación Automática de Beneficios Institucionales]
    beneficios --> AsignadorBeneficios
    AsignadorBeneficios -->|Otorga Póliza, Biblioteca, Salud| aprendiz_beneficios

    %% Flujos de entrada
    A -->|Diligencia Encuesta / Responde| RespuestasProc[Process: Registro de Respuestas]
    U -->|Crea/Edita Encuestas, Reglas y Estructura| ConfigProc[Process: Administración del Sistema]

    ConfigProc -->|Modifica| ModuloEstructura
    ConfigProc -->|Modifica| ModuloConfig
    ConfigProc -->|Modifica| ModuloReglas
    ConfigProc -->|Modifica Catálogo| beneficios

    RespuestasProc -->|Escribe datos| respuestas
    respuestas -.->|Dispara| MotorReglas[Process: Evaluador de Reglas]

    %% Motor de reglas
    reglas --> MotorReglas
    condiciones --> MotorReglas
    acciones_regla --> MotorReglas

    MotorReglas -->|Si cumple condiciones| GeneradorCasos[Process: Generador Automático de Casos y Alertas]
    GeneradorCasos -->|Crea Caso| casos
    GeneradorCasos -->|Asocia Necesidad| caso_necesidades
    GeneradorCasos -->|Genera Notificación| notificaciones

    %% Gestión de Casos
    U -->|Asigna y gestiona| casos
    U -->|Registra Plan de Acción| acciones_caso
    U -->|Registra Seguimiento| seguimientos

    %% Auditoría y Analítica
    RespuestasProc -.->|Registra Log| auditoria
    ConfigProc -.->|Registra Log| auditoria
    respuestas -->|Cálculo de Indicadores| CalcIndicadores[Process: Motor de Analítica]
    categorias --> CalcIndicadores
    indicadores --> CalcIndicadores
```

---

## 2. Diagramas de Flujo Específicos por Ciclo de Vida

### A. Flujo de Asignación Directa de Beneficios Institucionales (Desacoplado de Casos/Necesidades)
```mermaid
sequenceDiagram
    autonumber
    actor A as Aprendiz
    participant API as API SENAContigo
    participant DB_B as DB: Catálogo de Beneficios
    participant DB_AB as DB: Aprendiz Beneficios

    A->>API: 1. Registro / Matrícula Activa en el SENA
    API->>DB_B: Consultar beneficios activos con `es_automatico_matricula = True`
    DB_B-->>API: Retorna Póliza Seguro, Biblioteca, Salud Preventiva, Orientación Psicosocial, Deportes
    API->>DB_AB: Guardar registros en `aprendiz_beneficios` (origen='MATRICULA_AUTOMATICA', caso_id=NULL)
    Note over DB_AB: El aprendiz adquiere sus derechos institucionales automáticamente.
```

---

### B. Flujo de Entrada de Datos: Respuestas de Encuestas
```mermaid
sequenceDiagram
    autonumber
    actor A as Aprendiz
    participant API as API SENAContigo
    participant DB_V as DB: Encuestas y Variables
    participant DB_R as DB: Respuestas
    participant DB_AUD as DB: Auditoría Log

    A->>API: 1. Solicita Encuesta Activa
    API->>DB_V: Consultar encuestas, variables_versiones y opciones
    DB_V-->>API: Devuelve esquema de preguntas
    API-->>A: Renderiza formulario de encuesta
    A->>API: 2. Envía Respuestas (opcion_id, valor_texto, etc.)
    API->>DB_R: Guarda registros en la tabla `respuestas`
    API->>DB_AUD: Registra acción `RESPONSE_SUBMIT` en `auditoria`
    API-->>A: Confirmación de recepción exitosa
```

---

### C. Flujo de Evaluación de Reglas y Generación de Casos (Motor de Automatización)
```mermaid
sequenceDiagram
    autonumber
    participant DB_R as DB: Respuestas
    participant Engine as Motor de Reglas (Backend)
    participant DB_RULE as DB: Reglas / Condiciones
    participant DB_CASE as DB: Casos / Necesidades
    participant DB_NOTIF as DB: Notificaciones

    DB_R->>Engine: Evento: Nueva respuesta registrada
    Engine->>DB_RULE: Consultar reglas activas y sus condiciones (`regla_condiciones`)
    DB_RULE-->>Engine: Devuelve catálogo de reglas activas
    Engine->>Engine: Evalúa coincidencia (EQUALS, IN, GREATER_THAN)
    alt Condición Cumplida (Afectación o Alerta)
        Engine->>DB_CASE: Insertar nuevo `caso` (Tipo, Prioridad)
        Engine->>DB_CASE: Insertar relación en `caso_necesidades`
        Engine->>DB_NOTIF: Insertar registro en `notificaciones` (ALERTA/URGENTE)
    end
```

---

## 3. Modelo Entidad-Relación de la Base de Datos (ERD)

```mermaid
erDiagram
    REGIONALES ||--o{ CENTROS : "posee"
    CENTROS ||--o{ FICHAS : "contiene"
    PROGRAMAS ||--o{ FICHAS : "pertenece"
    CENTROS ||--o{ APRENDICES : "adscrito"
    REGIONALES ||--o{ APRENDICES : "pertenece"
    APRENDICES ||--o{ MATRICULAS : "tiene"
    FICHAS ||--o{ MATRICULAS : "asociada"

    BENEFICIOS ||--o{ APRENDIZ_BENEFICIOS : "otorga"
    APRENDICES ||--o{ APRENDIZ_BENEFICIOS : "goza"

    USUARIOS ||--o{ USUARIO_ROLES : "asignado"
    ROLES ||--o{ USUARIO_ROLES : "tiene"
    ROLES ||--o{ ROL_PERMISOS : "posee"
    PERMISOS ||--o{ ROL_PERMISOS : "concedido"

    CATEGORIAS ||--o{ VARIABLES : "agrupa"
    VARIABLES ||--o{ VARIABLE_VERSIONES : "versiona"
    VARIABLE_VERSIONES ||--o{ OPCIONES_VARIABLE : "contiene"

    ENCUESTAS ||--o{ ENCUESTA_VARIABLES : "incluye"
    VARIABLES ||--o{ ENCUESTA_VARIABLES : "asociada"
    ENCUESTAS ||--o{ CORTES_ENCUESTA : "registra"
    SEGMENTOS ||--o{ ENCUESTAS : "aplica_a"

    APRENDICES ||--o{ RESPUESTAS : "emite"
    VARIABLES ||--o{ RESPUESTAS : "referencia"
    VARIABLE_VERSIONES ||--o{ RESPUESTAS : "aplica_version"
    OPCIONES_VARIABLE ||--o{ RESPUESTAS : "selecciona"
    ENCUESTAS ||--o{ RESPUESTAS : "pertenece"
    CORTES_ENCUESTA ||--o{ RESPUESTAS : "corta"
    USUARIOS ||--o{ RESPUESTAS : "registrado_por"

    REGLAS ||--o{ REGLA_CONDICIONES : "evalua"
    REGLAS ||--o{ REGLA_ACCIONES : "ejecuta"
    VARIABLES ||--o{ REGLA_CONDICIONES : "compara"
    OPCIONES_VARIABLE ||--o{ REGLA_CONDICIONES : "compara_opcion"
    NECESIDADES ||--o{ REGLA_ACCIONES : "asocia"

    APRENDICES ||--o{ CASOS : "sufre_situacion"
    USUARIOS ||--o{ CASOS : "atiende"
    CASOS ||--o{ CASO_NECESIDADES : "requiere"
    NECESIDADES ||--o{ CASO_NECESIDADES : "clasifica"
    CASOS ||--o{ ACCIONES : "genera"
    USUARIOS ||--o{ ACCIONES : "ejecuta_accion"
    CASOS ||--o{ SEGUIMIENTOS : "tiene_historial"
    USUARIOS ||--o{ SEGUIMIENTOS : "registra_seguimiento"

    CASOS ||--o| APRENDIZ_BENEFICIOS : "vincular_opcional"

    BENEFICIOS {
        int id PK
        string codigo UK
        string nombre
        string descripcion
        string tipo_beneficio
        boolean es_automatico_matricula
        boolean activo
    }

    APRENDIZ_BENEFICIOS {
        int id PK
        int aprendiz_id FK
        int beneficio_id FK
        datetime fecha_asignacion
        string estado
        string origen
        int caso_id FK "Nullable=True"
        string observaciones
    }

    REGIONALES {
        int id PK
        string codigo_regional UK
        string nombre
        boolean activo
    }

    CENTROS {
        int id PK
        string codigo_centro UK
        string nombre
        int regional_id FK
    }

    APRENDICES {
        int id PK
        string tipo_documento
        string numero_documento UK
        string nombres
        string apellidos
        string correo UK
        int centro_id FK
        int regional_id FK
    }

    CASOS {
        int id PK
        int aprendiz_id FK
        string tipo
        string prioridad
        string estado
        int responsable_id FK
        string origen
    }
```

---

## 4. Descripción de los Módulos de Datos

1. **Beneficios Institucionales Directos (`beneficios`, `aprendiz_beneficios`)**:
   - Gestiona los derechos y beneficios por defecto que posee todo aprendiz SENA (Póliza de seguro, biblioteca, servicios de salud, deportes) de forma independiente y sin pasar por casos de riesgo.
2. **Estructura Académica y Organizacional (`regionales`, `centros`, `programas`, `fichas`, `aprendices`, `matriculas`)**:
   - Mantiene la jerarquía administrativa del SENA y el registro académico de los aprendices inscritos.
3. **Control de Acceso e Identidad (`usuarios`, `roles`, `permisos`)**:
   - Gestiona la autenticación RBAC con restricciones por Regional/Centro.
4. **Parametrización de Encuestas y Variables (`categorias`, `variables`, `variable_versiones`, `opciones_variable`, `encuestas`, `cortes_encuesta`, `segmentos`)**:
   - Versionamiento dinámico de preguntas, respuestas y niveles de afectación.
5. **Respuestas de Aprendices (`respuestas`)**:
   - Registro longitudinal de respuestas tomadas a los aprendices.
6. **Motor de Reglas y Automatización (`reglas`, `regla_condiciones`, `regla_acciones`)**:
   - Analiza las respuestas recibidas y genera automáticamente casos, necesidades y alertas de riesgo.
7. **Gestión de Atención de Casos y Seguimiento (`necesidades`, `casos`, `caso_necesidades`, `acciones`, `seguimientos`)**:
   - Plan de atención para situaciones de riesgo de bienestar.
