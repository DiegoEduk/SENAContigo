# Guía Técnica Completa de Custom Agents en Google Antigravity

Esta guía ofrece una visión profunda sobre la arquitectura, ciclo de vida, integración de herramientas y ejecución de los **Custom Agents** en la plataforma Google Antigravity.

---

## 1. Arquitectura de Simetría Total (True Symmetry)

En Google Antigravity 2.0, los Custom Agents no están limitados a ser simples subagentes auxiliares. Cuentan con **simetría total**, lo que significa que cualquier Custom Agent configurado puede ser ejecutado como:

1. **Agente Principal (Top-level Agent):**
   Iniciado directamente por el usuario para liderar una sesión completa de desarrollo.
   - En CLI: `agy --agent <nombre-del-agente>`
   - En TUI/IDE: Seleccionando el agente a través del menú `/agents`.

2. **Subagente Dinámico (Invoked Subagent):**
   Invocado por otro agente mediante la herramienta `invoke_subagent` para delegar un subproblema específico de forma aislada.

---

## 2. Aislamiento de Contexto y Gestión de Tokens

El beneficio principal de los Custom Agents es la eliminación del "context bloat":

```
[ Sin Custom Agent ]
Prompt del Usuario -> Carga de 500+ líneas de instrucciones genéricas -> Consumo masivo de Tokens

[ Con Custom Agent ]
Prompt del Usuario -> Carga de agent.md acotado (50 líneas específicas) -> Respuesta rápida y económica
```

Al asignar herramientas específicas (`config.toolNames`), se evita que el agente intente realizar acciones fuera de su competencia, incrementando la confiabilidad y previsibilidad.

---

## 3. Matriz de Herramientas Disponibles (`toolNames`)

Al configurar el campo `config.toolNames` en `agent.md`, puedes seleccionar entre las herramientas estándar de Antigravity:

- `view_file`: Leer contenido de archivos en el workspace.
- `replace_file_content`: Editar un bloque continuo de código en un archivo existente.
- `multi_replace_file_content`: Editar múltiples bloques no adyacentes en el mismo archivo.
- `write_to_file`: Crear un nuevo archivo en el sistema de archivos.
- `run_command`: Ejecutar comandos Bash en el sistema operativo Linux.
- `list_dir`: Listar la estructura de carpetas y archivos.
- `grep_search`: Realizar búsquedas por patrón exacto o regex usando ripgrep.
- `search_web`: Consultar fuentes y documentación externa en la web.
- `read_url_content`: Extraer contenido de páginas web HTTP.
- `invoke_subagent`: Invocar otros subagentes registrados.
- `ask_question`: Solicitar aclaraciones interactivas al usuario.

---

## 4. Buenas Prácticas de Redacción del System Prompt

Para que tu Custom Agent sea de alta calidad:

1. **Establece un Rol Claro:** Comienza siempre con `# Rol y Propósito`.
2. **Establece Reglas Innegociables:** Define qué DEBE y qué NO DEBE hacer el agente.
3. **Paso a Paso Explícito:** Describe el flujo de pensamiento o pasos que debe seguir antes de generar la respuesta final.
4. **Validación:** Requiere que el agente verifique sus cambios mediante comandos de prueba antes de dar por completada la tarea.
