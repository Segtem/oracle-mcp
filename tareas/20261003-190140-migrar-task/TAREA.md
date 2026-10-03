# Migrar a Oracle Task 0.2.0

- ESTADO: ABIERTA
- PRIORIDAD: 50
- ETIQUETAS: 


## Pedido

El usuario pidió el 2026-10-03 migrar todos los consumidores de trackertast a oracle-task y
luego retirar el paquete anterior de PyPI. Coordinación: tarea 20261003-183936-migrar-task del
repositorio Segtem/oracle. Se conservan IDs, documentos de tareas y el alias tasks.


## Verificación

Imports oracle_task y dependencia oracle-task==0.2.0. Los fixtures de tareas usan el tracker directamente. 156 tests verdes, incluido transporte en subprocess del wheel instalado. Twine validó wheel/sdist 0.1.2. .venv actualizada, sin trackertast.


### Nota (2026-10-03 23:44:40 UTC)

Main empujado, tag v0.1.2 y release GitHub publicados con wheel/sdist/SHA256SUMS: https://github.com/Segtem/oracle-mcp/releases/tag/v0.1.2. CI exitoso. En Factory, web publicada verificada HTTP 200 e idéntica a main; en MCP, herramienta global actualizada desde release con hash y sin trackertast.


## Próximo paso

El mantenedor publica 0.1.2 en PyPI con los artefactos explícitos de dist/. Verificar hashes, metadata e instalación nueva; luego retirar trackertast según la coordinación de Oracle 20261003-183936-migrar-task.
