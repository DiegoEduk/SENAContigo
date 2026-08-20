-- =============================================================================
-- SENAContigo - Script de Poblamiento Inicial de Base de Datos (SQL Idempotente)
-- Basado en SenaContigo02.pdf
-- =============================================================================

BEGIN;

-- -----------------------------------------------------------------------------
-- 1. ROLES DEL SISTEMA
-- -----------------------------------------------------------------------------
INSERT INTO roles (id, nombre, descripcion, activo, created_at)
VALUES 
  (1, 'superadmin', 'Administrador Global Nacional con acceso total a todos los centros y configuraciones', true, NOW()),
  (2, 'direccion', 'Dirección Regional con acceso a todos los centros de su regional', true, NOW()),
  (3, 'coordinador', 'Coordinador de Centro de Formación con acceso exclusivo a su centro', true, NOW()),
  (4, 'instructor', 'Instructor con acceso a sus fichas asignadas', true, NOW()),
  (5, 'aprendiz', 'Aprendiz SENA con acceso personal', true, NOW())
ON CONFLICT (nombre) DO UPDATE 
SET descripcion = EXCLUDED.descripcion, activo = true;

SELECT setval('roles_id_seq', (SELECT MAX(id) FROM roles));

-- -----------------------------------------------------------------------------
-- 2. CATÁLOGO DE PERMISOS
-- -----------------------------------------------------------------------------
INSERT INTO permisos (codigo, nombre, descripcion, modulo, created_at)
VALUES
  ('usuarios:read', 'Consultar Usuarios', 'Permiso para listar y ver detalle de usuarios', 'identity', NOW()),
  ('usuarios:write', 'Gestionar Usuarios', 'Permiso para crear y modificar usuarios', 'identity', NOW()),
  ('variables:read', 'Consultar Variables', 'Permiso para ver variables y versiones', 'variables', NOW()),
  ('variables:write', 'Gestionar Variables', 'Permiso para crear y versionar variables', 'variables', NOW()),
  ('encuestas:read', 'Consultar Encuestas', 'Permiso para ver encuestas y cortes', 'surveys', NOW()),
  ('encuestas:write', 'Gestionar Encuestas', 'Permiso para crear y publicar encuestas', 'surveys', NOW()),
  ('respuestas:read', 'Consultar Respuestas', 'Permiso para ver historial longitudinal', 'responses', NOW()),
  ('respuestas:write', 'Registrar Respuestas', 'Permiso para enviar mediciones de aprendices', 'responses', NOW()),
  ('casos:read', 'Consultar Casos', 'Permiso para ver casos de atención', 'cases', NOW()),
  ('casos:write', 'Gestionar Casos', 'Permiso para crear, asignar y cerrar casos', 'cases', NOW()),
  ('analytics:read', 'Consultar Analítica', 'Permiso para ver dashboards e indicadores', 'analytics', NOW()),
  ('audit:read', 'Consultar Auditoría', 'Permiso para ver trazas de auditoría', 'audit', NOW())
ON CONFLICT (codigo) DO NOTHING;

-- -----------------------------------------------------------------------------
-- 3. ESTRUCTURA ORGANIZACIONAL SENA (REGIONALES Y CENTROS)
-- -----------------------------------------------------------------------------
INSERT INTO regionales (id, codigo_regional, nombre, activo, created_at)
VALUES 
  (1, '11', 'REGIONAL DISTRITO CAPITAL', true, NOW()),
  (2, '05', 'REGIONAL ANTIOQUIA', true, NOW()),
  (3, '66', 'REGIONAL RISARALDA', true, NOW()),
  (4, '76', 'REGIONAL VALLE', true, NOW())
ON CONFLICT (codigo_regional) DO UPDATE 
SET nombre = EXCLUDED.nombre;

SELECT setval('regionales_id_seq', (SELECT MAX(id) FROM regionales));

INSERT INTO centros (id, codigo_centro, nombre, regional_id, activo, created_at)
VALUES 
  (1, '9201', 'CENTRO DE DISEÑO Y METROLOGÍA', 1, true, NOW()),
  (2, '9202', 'CENTRO DE ELECTRICIDAD, ELECTRÓNICA Y TELECOMUNICACIONES', 1, true, NOW()),
  (3, '9101', 'CENTRO DE TECNOLOGÍA DE LA MANUFACTURA AVANZADA', 2, true, NOW()),
  (4, '9121', 'CENTRO ATENCION SECTOR AGROPECUARIO', 3, true, NOW()),
  (5, '9308', 'CENTRO DE COMERCIO Y SERVICIOS', 3, true, NOW()),
  (6, '9223', 'CENTRO DE DISEÑO E INNOVACIÓN TECNOLÓGICA INDUSTRIAL', 3, true, NOW())
ON CONFLICT (codigo_centro) DO UPDATE 
SET nombre = EXCLUDED.nombre, regional_id = EXCLUDED.regional_id;

SELECT setval('centros_id_seq', (SELECT MAX(id) FROM centros));

-- -----------------------------------------------------------------------------
-- 4. USUARIOS INICIALES (SUPERADMIN, DIRECCIÓN, COORDINADOR, INSTRUCTOR)
-- Contraseñas:
-- admin@senacontigo.edu.co       -> Admin123456*
-- direccion.dc@senacontigo.edu.co -> Direccion123*
-- coordinador.cdm@senacontigo.edu.co -> Coordinador123*
-- instructor.adso@senacontigo.edu.co -> Instructor123*
-- -----------------------------------------------------------------------------
INSERT INTO usuarios (id, tipo_documento, numero_documento, nombres, apellidos, correo, hashed_password, celular, regional_id, centro_id, aprendiz_id, activo, created_at, updated_at)
VALUES 
  (1, 'CC', '1000000000', 'SuperAdmin', 'SENAContigo', 'admin@senacontigo.edu.co', '$2b$12$2Xoo0pTv/wvCg569gCggAuMCUSwlWWflyhiKN2y1PphopYmKFj9A.', '3000000000', 1, 1, NULL, true, NOW(), NOW()),
  (2, 'CC', '1000000001', 'Carlos Enrique', 'Martínez Dirección', 'direccion.dc@senacontigo.edu.co', '$2b$12$EG3l0FOTFljlLNdk02uXpO7c9QvNXnrnxCIjWBYG4Ija02C/4/Jp2', '3001112233', 1, NULL, NULL, true, NOW(), NOW()),
  (3, 'CC', '1000000002', 'Martha Cecilia', 'López Coordinación', 'coordinador.cdm@senacontigo.edu.co', '$2b$12$NFJoK8pRe2HNnqkUHyUMOemVHCm3uzYABJ.qEPiWqxAhfnf5X23jq', '3002223344', 1, 1, NULL, true, NOW(), NOW()),
  (4, 'CC', '1000000003', 'Jorge Alberto', 'Ramírez Instructor', 'instructor.adso@senacontigo.edu.co', '$2b$12$hcLqT2JL/zucnN2zqhFgK.GKiH8lzHmLhRUmqfp56uNMGmN2ynvbO', '3003334455', 1, 1, NULL, true, NOW(), NOW())
ON CONFLICT (correo) DO UPDATE 
SET hashed_password = EXCLUDED.hashed_password, activo = true;

SELECT setval('usuarios_id_seq', (SELECT MAX(id) FROM usuarios));

-- Asignación de Roles a Usuarios
INSERT INTO usuario_roles (usuario_id, rol_id)
VALUES 
  (1, 1), -- SuperAdmin
  (2, 2), -- Dirección
  (3, 3), -- Coordinador
  (4, 4)  -- Instructor
ON CONFLICT (usuario_id, rol_id) DO NOTHING;

-- -----------------------------------------------------------------------------
-- 5. GESTIÓN ACADÉMICA (PROGRAMAS Y FICHAS)
-- -----------------------------------------------------------------------------
INSERT INTO programas (id, codigo_programa, version, nombre, nivel_formacion, activo, created_at)
VALUES 
  (1, '228106', '1', 'ANÁLISIS Y DESARROLLO DE SOFTWARE (ADSO)', 'Tecnólogo', true, NOW()),
  (2, '233108', '1', 'GESTIÓN DE REDES DE DATOS', 'Tecnólogo', true, NOW()),
  (3, '220101', '1', 'MANTENIMIENTO DE EQUIPOS DE CÓMPUTO', 'Técnico', true, NOW())
ON CONFLICT (codigo_programa) DO UPDATE 
SET nombre = EXCLUDED.nombre;

SELECT setval('programas_id_seq', (SELECT MAX(id) FROM programas));

INSERT INTO fichas (id, ficha_caracterizacion, fecha_inicial, fecha_final, estado_ficha, centro_id, programa_id, created_at)
VALUES 
  (1, '2670123', '2025-02-01', '2026-11-30', 'En ejecución', 1, 1, NOW()),
  (2, '2670124', '2025-02-01', '2026-11-30', 'En ejecución', 1, 1, NOW())
ON CONFLICT (ficha_caracterizacion) DO UPDATE 
SET estado_ficha = EXCLUDED.estado_ficha;

SELECT setval('fichas_id_seq', (SELECT MAX(id) FROM fichas));

-- -----------------------------------------------------------------------------
-- 6. APRENDICES Y MATRÍCULAS DE DEMOSTRACIÓN
-- -----------------------------------------------------------------------------
INSERT INTO aprendices (id, tipo_documento, numero_documento, nombres, apellidos, correo, celular, centro_id, regional_id, activo, created_at, updated_at)
VALUES 
  (1, 'CC', '1098765432', 'Juan Carlos', 'Pérez Gómez', 'juan.perez@misena.edu.co', '3111111111', 1, 1, true, NOW(), NOW()),
  (2, 'CC', '1098765433', 'María Fernanda', 'Rodríguez Silva', 'maria.rodriguez@misena.edu.co', '3112222222', 1, 1, true, NOW(), NOW())
ON CONFLICT (numero_documento) DO UPDATE 
SET nombres = EXCLUDED.nombres, apellidos = EXCLUDED.apellidos;

SELECT setval('aprendices_id_seq', (SELECT MAX(id) FROM aprendices));

INSERT INTO matriculas (id, aprendiz_id, ficha_id, estado_matricula, created_at)
VALUES 
  (1, 1, 1, 'En formación', NOW()),
  (2, 2, 1, 'En formación', NOW())
ON CONFLICT DO NOTHING;

SELECT setval('matriculas_id_seq', (SELECT MAX(id) FROM matriculas));

-- -----------------------------------------------------------------------------
-- 7. MOTOR DE VARIABLES DINÁMICAS (CATEGORÍAS, VARIABLES, VERSIONES, OPCIONES)
-- -----------------------------------------------------------------------------
INSERT INTO categorias (id, codigo, nombre, descripcion, activa, created_at)
VALUES 
  (1, 'VIVIENDA', 'Vivienda y Habitabilidad', 'Evaluación del estado de la vivienda y alojamiento', true, NOW()),
  (2, 'TRANSPORTE', 'Transporte y Movilidad', 'Desplazamiento y transporte hacia el centro de formación', true, NOW()),
  (3, 'CONECTIVIDAD', 'Tecnología y Conectividad', 'Acceso a computador e internet', true, NOW()),
  (4, 'FAMILIA', 'Situación Familiar', 'Entorno familiar y personas a cargo', true, NOW()),
  (5, 'EMPLEO', 'Situación Laboral', 'Vinculación laboral u ocupación actual', true, NOW()),
  (6, 'ECONOMIA', 'Situación Económica', 'Ingresos y sostenibilidad financiera', true, NOW()),
  (7, 'ALIMENTACION', 'Alimentación y Nutrición', 'Acceso a alimentación diaria', true, NOW())
ON CONFLICT (codigo) DO UPDATE 
SET nombre = EXCLUDED.nombre;

SELECT setval('categorias_id_seq', (SELECT MAX(id) FROM categorias));

-- Variable 1: Estado de Vivienda
INSERT INTO variables (id, categoria_id, codigo, nombre, descripcion, tipo_respuesta, version_actual, es_sensible, es_obligatoria, activa, created_at, updated_at)
VALUES 
  (1, 1, 'ESTADO_VIVIENDA', 'Estado de la Vivienda', 'Medición del nivel de afectación habitacional', 'opcion_unica', 1, false, true, true, NOW(), NOW())
ON CONFLICT (codigo) DO NOTHING;

SELECT setval('variables_id_seq', (SELECT MAX(id) FROM variables));

INSERT INTO variable_versiones (id, variable_id, numero_version, titulo_pregunta, descripcion, activa, created_at)
VALUES 
  (1, 1, 1, '¿En qué estado se encuentra su vivienda actual?', 'Versión inicial de pregunta habitacional', true, NOW())
ON CONFLICT DO NOTHING;

SELECT setval('variable_versiones_id_seq', (SELECT MAX(id) FROM variable_versiones));

INSERT INTO opciones_variable (id, variable_version_id, codigo, texto, valor_numerico, orden, nivel_afectacion, activa, created_at)
VALUES 
  (1, 1, 'NORMAL', 'Sin afectación / Normal', 0, 1, 0, true, NOW()),
  (2, 1, 'LEVE', 'Afectada levemente', 1, 2, 1, true, NOW()),
  (3, 1, 'INHABITABLE', 'Vivienda Inhabitable', 2, 3, 3, true, NOW()),
  (4, 1, 'DESTRUIDA', 'Vivienda Destruida', 3, 4, 4, true, NOW())
ON CONFLICT DO NOTHING;

SELECT setval('opciones_variable_id_seq', (SELECT MAX(id) FROM opciones_variable));

-- -----------------------------------------------------------------------------
-- 8. CATÁLOGO DE NECESIDADES
-- -----------------------------------------------------------------------------
INSERT INTO necesidades (id, codigo, nombre, descripcion, categoria_relacionada, activa, created_at)
VALUES 
  (1, 'ALOJAMIENTO', 'Alojamiento Temporal', 'Necesidad de reubicación o alojamiento de emergencia', 'VIVIENDA', true, NOW()),
  (2, 'CONECTIVIDAD', 'Internet y Equipo Computacional', 'Necesidad de plan de datos o préstamo de computador', 'CONECTIVIDAD', true, NOW()),
  (3, 'ALIMENTARIO', 'Apoyo Alimentario', 'Bono o paquete alimentario de emergencia', 'ALIMENTACION', true, NOW()),
  (4, 'ECONOMICO', 'Apoyo Económico de Emergencia', 'Auxilio económico temporal', 'ECONOMIA', true, NOW()),
  (5, 'PSICOLOGICO', 'Acompañamiento Psicosocial', 'Atención psicosocial por Bienestar al Aprendiz', 'FAMILIA', true, NOW()),
  (6, 'FORMATIVO', 'Riesgo de Deserción / Continuidad Formativa', 'Plan de mejoramiento o reprogramación académica', 'EMPLEO', true, NOW())
ON CONFLICT (codigo) DO UPDATE 
SET nombre = EXCLUDED.nombre;

SELECT setval('necesidades_id_seq', (SELECT MAX(id) FROM necesidades));

-- -----------------------------------------------------------------------------
-- 9. MOTOR DE REGLAS (EJEMPLO REGULA AUTOMÁTICA DE CASO CRÍTICO)
-- -----------------------------------------------------------------------------
INSERT INTO reglas (id, nombre, descripcion, activa, prioridad, created_at)
VALUES 
  (1, 'Regla Alojamiento por Vivienda Inhabitable', 'Genera automáticamente un caso crítico de atención cuando la vivienda se encuentra inhabitable o destruida', true, 1, NOW())
ON CONFLICT DO NOTHING;

SELECT setval('reglas_id_seq', (SELECT MAX(id) FROM reglas));

INSERT INTO regla_condiciones (id, regla_id, variable_id, opcion_id, operador, valor_comparar)
VALUES 
  (1, 1, 1, 3, 'EQUALS', NULL)
ON CONFLICT DO NOTHING;

SELECT setval('regla_condiciones_id_seq', (SELECT MAX(id) FROM regla_condiciones));

INSERT INTO regla_acciones (id, regla_id, tipo_accion, necesidad_id, prioridad_caso, titulo_caso, mensaje_notificacion)
VALUES 
  (1, 1, 'CREAR_CASO', 1, 'CRITICA', 'EMERGENCIA HABITACIONAL - ALOJAMIENTO REQUERIDO', 'Alerta: Aprendiz requiere alojamiento temporal de emergencia')
ON CONFLICT DO NOTHING;

SELECT setval('regla_acciones_id_seq', (SELECT MAX(id) FROM regla_acciones));

-- -----------------------------------------------------------------------------
-- 10. CATÁLOGO DE BENEFICIOS INSTITUCIONALES SENA
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS beneficios (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT,
    tipo_beneficio VARCHAR(50) DEFAULT 'INSTITUCIONAL_AUTOMATICO',
    es_automatico_matricula BOOLEAN DEFAULT true,
    activo BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS aprendiz_beneficios (
    id SERIAL PRIMARY KEY,
    aprendiz_id INTEGER NOT NULL REFERENCES aprendices(id) ON DELETE CASCADE,
    beneficio_id INTEGER NOT NULL REFERENCES beneficios(id) ON DELETE CASCADE,
    fecha_asignacion TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    estado VARCHAR(50) DEFAULT 'ACTIVO',
    origen VARCHAR(50) DEFAULT 'MATRICULA_AUTOMATICA',
    caso_id INTEGER REFERENCES casos(id) ON DELETE SET NULL,
    observaciones TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

INSERT INTO beneficios (id, codigo, nombre, descripcion, tipo_beneficio, es_automatico_matricula, activo, created_at)
VALUES
  (1, 'BEN-SEGURO', 'Póliza de Seguro Estudiantil contra Accidentes', 'Cobertura médica y seguro de accidentes personales durante el proceso formativo en el SENA', 'SALUD_Y_PROTECCION', true, true, NOW()),
  (2, 'BEN-BIBLIOTECA', 'Acceso a Sistema de Bibliotecas y Repositorio Digital', 'Préstamo de material bibliográfico físico y acceso ilimitado a bases de datos digitales institucionales', 'INSTITUCIONAL_AUTOMATICO', true, true, NOW()),
  (3, 'BEN-SALUD-PREV', 'Atención Médica Preventiva y Enfermería de Centro', 'Primeros auxilios, atención básica de enfermería y campañas de prevención de salud en el centro de formación', 'SALUD_Y_PROTECCION', true, true, NOW()),
  (4, 'BEN-ORIENTACION-PSICO', 'Orientación Psicosocial y Apoyo Emocional', 'Acompañamiento y asesoría psicológica preventiva impartida por el equipo de Bienestar al Aprendiz', 'INSTITUCIONAL_AUTOMATICO', true, true, NOW()),
  (5, 'BEN-ALIMENTACION', 'Apoyo Alimentario Institucional / Refrigerios', 'Apoyo nutricional de refrigerios o almuerzos asignado por la coordinación de bienestar', 'APOYO_FINANCIERO', false, true, NOW()),
  (6, 'BEN-DEPORTES', 'Programas de Cultura, Deporte y Recreación', 'Participación libre en selecciones deportivas, actividades culturales y áreas de esparcimiento del SENA', 'CULTURA_Y_DEPORTE', true, true, NOW())
ON CONFLICT (codigo) DO UPDATE
SET nombre = EXCLUDED.nombre;

SELECT setval('beneficios_id_seq', (SELECT MAX(id) FROM beneficios));

COMMIT;

