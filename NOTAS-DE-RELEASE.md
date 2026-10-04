# Oracle MCP 0.1.2

Migra la dependencia a `oracle-task==0.2.0` y los imports a `oracle_task`. La herramienta MCP
`oracle_tasks` conserva su nombre, argumentos y lectura de los mismos archivos de tareas.
Incluye el pin de Oracle 0.38.1 que ya estaba en main.

Publicado en PyPI: wheel/sdist verificados contra los hashes del release e instalación nueva sin trackertast. Las versiones 0.1.0 y 0.1.1 dependen de trackertast y no podrán
instalarse desde PyPI después de retirar ese paquete; actualizar a 0.1.2.

```bash
uv publish dist/oracle_mcp-0.1.2-py3-none-any.whl dist/oracle_mcp-0.1.2.tar.gz
```

La tarea `20261003-190140-migrar-task` registra la validación del corte.
