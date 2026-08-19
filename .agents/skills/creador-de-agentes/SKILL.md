---
name: creador-de-agentes
description: Guía y herramienta para diseñar, configurar y desplegar Custom Agents (Agentes Personalizados) en Google Antigravity. Permite crear agentes especializados con instrucciones de sistema, herramientas acotadas y modelos específicos a nivel de proyecto (.agents/agents/) o global.
---

# Creador de Agentes (Custom Agents en Google Antigravity)

Esta habilidad proporciona las instrucciones, estándares y plantillas necesarios para crear y gestionar **Custom Agents** en Google Antigravity (Antigravity 2.0, CLI `agy` y IDE).

---

## 1. ¿Qué es un Custom Agent?

Un **Custom Agent** en Antigravity es un agente de IA especializado definido mediante archivos de configuración en el repositorio o a nivel global. A diferencia de un asistente genérico, un Custom Agent tiene:

- **Propósito y Rol Específico:** Instrucciones claras para tareas concretas (p. ej., revisión de código, auditorías de seguridad, pruebas automatizadas, diseño UI).
- **Herramientas Acotadas (`toolNames`):** Acceso restringido únicamente a las herramientas que requiere para su tarea, protegiendo la seguridad y evitando ejecuciones no deseadas.
- **Eficiencia de Contexto:** Elimina la sobrecarga de tokens ("context window bloat") al cargar únicamente las reglas e instrucciones necesarias para su función.
- **Simetría Total:** Se puede invocar como un agente principal en la CLI/UI (`agy --agent <nombre>`) o como subagente dentro de un flujo multitarea (`invoke_subagent`).

---

## 2. Ubicación de los Archivos de Agente

Antigravity descubre automáticamente los Custom Agents según la siguiente jerarquía de carpetas:

- **Específico del Proyecto (Workspace):**
  `{workspace}/.agents/agents/{nombre-del-agente}/agent.md`
  *(Recomendado: se comparte con todo el equipo a través del repositorio git)*

- **Global (A nivel de usuario):**
  `~/.gemini/config/agents/{nombre-del-agente}/agent.md`

> **Regla de Oro:** Cada agente debe residir en su propia carpeta con el nombre del agente, y el archivo de definición debe llamarse obligatoriamente `agent.md`.

---

## 3. Estructura y Anatomía de `agent.md`

Un archivo `agent.md` consta de un **encabezado YAML (frontmatter)** y un **cuerpo en Markdown** que define las instrucciones de sistema.

```yaml
---
name: nombre-del-agente
description: Breve descripción (1-2 líneas) sobre el propósito del agente y cuándo usarlo.
hidden: false
config:
  toolNames:
    - view_file
    - run_command
    - replace_file_content
  model: gemini-3.6-pro
---

# Instrucciones del Sistema del Agente

Eres un agente especializado en [ÁREA DE ESPECIALIZACIÓN].

## Responsabilidades Principales
1. ...
2. ...

## Directivas y Restricciones
- ...
- ...
```

### Campos de Configuración (Frontmatter YAML)

| Campo | Tipo | Requerido | Descripción |
| :--- | :--- | :--- | :--- |
| `name` | String | Sí | Identificador único del agente (usar minúsculas y guiones). |
| `description` | String | Sí | Descripción que aparecerá en el menú `/agents` y en el CLI. |
| `hidden` | Boolean | No | `false` por defecto. Si se establece en `true`, no se muestra en selecciones públicas. |
| `config.toolNames` | List[String] | No | Lista explícita de herramientas autorizadas (p. ej. `view_file`, `run_command`, `replace_file_content`, `search_web`). |
| `config.model` | String | No | Modelo preferido para este agente (p. ej. `gemini-3.6-pro`, `gemini-3.6-flash`). |

---

## 4. Guía Paso a Paso para Crear un Custom Agent

### Paso 1: Definir la Necesidad del Agente
Determina:
- ¿Qué rol específico desempeñará? (Ej: Tester, Revisor, Documentador, Refactorizador).
- ¿Qué herramientas estrictamente necesita?
- ¿Cuáles son sus criterios de éxito?

### Paso 2: Crear el Archivo de Agente
En tu proyecto, crea la estructura de directorios:
```bash
mkdir -p .agents/agents/mi-nuevo-agente
```
Crea el archivo `.agents/agents/mi-nuevo-agente/agent.md`.

### Paso 3: Configurar el Encabezado YAML
Define `name`, `description` y restringe las herramientas necesarias en `toolNames`.

### Paso 4: Escribir el System Prompt
En el cuerpo de `agent.md`:
- Define la personalidad y rol.
- Especifica el flujo paso a paso.
- Define formatos de salida (Markdown, tablas, diffs).
- Agrega reglas de seguridad o límites operativos.

### Paso 5: Validar y Probar
- Ejecuta `/agents` en la TUI de Antigravity para verificar que el agente aparece en la lista.
- En la CLI, pruébalo con: `agy --agent mi-nuevo-agente "tu petición"`

---

## 5. Recursos Adicionales de la Habilidad

Para obtener más información y ver plantillas avanzadas, consulta:
- **Guía de Referencia Técnica:** [custom-agents-guide.md](file://.agents/skills/creador-de-agentes/references/custom-agents-guide.md)
- **Ejemplo: Revisor de Código:** [code-reviewer/agent.md](file://.agents/skills/creador-de-agentes/examples/code-reviewer/agent.md)
- **Ejemplo: Auditor de Seguridad:** [security-auditor/agent.md](file://.agents/skills/creador-de-agentes/examples/security-auditor/agent.md)
