# oracle-mcp

Servidor MCP (Model Context Protocol) oficial para consultar, evaluar y falsar medidas de un proyecto Oracle sin modificar el sistema de archivos.

## Sólo lectura

`oracle-mcp` es estrictamente de **sólo lectura** respecto del proyecto fijado al inicio. Un agente no puede crear, modificar ni borrar archivos del proyecto, ni alterar las reglas o evidencias para darse la razón a sí mismo. La autoridad y el alcance quedan determinados en el arranque y ninguna llamada puede ampliarlos.

## Instalación

Instalá `oracle-mcp` como herramienta global con `uv`:

```bash
uv tool install oracle-mcp
```

O agregalo a un entorno virtual de desarrollo:

```bash
uv pip install oracle-mcp
```

## Configuración en clientes MCP

El servidor se comunica a través de `stdio`. Al iniciarlo se especifica la raíz del proyecto a inspeccionar mediante `--proyecto <ruta>`.

### Claude Code

Configurá el servidor en tu archivo de configuración de Claude Code (por ejemplo en `~/.claude/claude.json` o a nivel de proyecto):

```json
{
  "mcpServers": {
    "oracle": {
      "command": "oracle-mcp",
      "args": ["--proyecto", "."]
    }
  }
}
```

O agregalo mediante el CLI:

```bash
claude mcp add oracle oracle-mcp -- --proyecto .
```

### Codex

En la configuración de MCP de Codex:

```json
{
  "mcpServers": {
    "oracle": {
      "command": "oracle-mcp",
      "args": ["--proyecto", "."]
    }
  }
}
```

## Herramientas disponibles

El servidor expone exactamente cinco herramientas de sólo lectura:

| Herramienta | Qué hace |
|---|---|
| `oracle_effective_catalog` | Consulta las medidas efectivas del proyecto fijado según su jurisdicción y ámbito. Sin `ids` devuelve el índice compacto; con `ids` devuelve el detalle normativo completo con umbrales, alcance y estado de fijación. |
| `oracle_evaluate` | Evalúa una medida por identificador efectivo o por texto en memoria contra evidencia JSON. Distingue tres estados (`verde`, `rojo`, `sin_evidencia`) e informa valor, umbral, testigos y estado de sombra con cotas y perdón. |
| `oracle_challenge` | Desafía una medida por id o texto contra casos de corpus y efímeros. Exige ambas polaridades y corre mutantes algebraicos para reportar discordancias y sobrevivientes sin tocar el disco. |
| `oracle_judge` | Juzga evidencia JSON contra el catálogo efectivo del proyecto (o un subconjunto de `ids`). Evalúa cumplimiento de reglas, aplica sombras con cotas e informa medidas no aplicadas. |
| `oracle_tasks` | Lee el tracker de tareas (`tareas/`) del proyecto para agentes sin acceso a terminal: listar tareas abiertas o cerradas por estado o etiqueta, ver detalle y notas de una tarea por id o prefijo, buscar texto o extraer hechos relacionales. |

## Contrato

Para consultar los esquemas JSON de entrada y salida, la especificación de errores tipados, el cálculo determinista de huellas criptográficas y las garantías de concurrencia y transporte, revisá el [Contrato MCP](docs/contract.md).
