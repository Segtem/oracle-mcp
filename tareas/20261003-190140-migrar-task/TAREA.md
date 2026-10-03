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

## Próximo paso

Publicar 0.1.2 en PyPI y verificar sus dependencias en una instalación nueva antes del retiro de trackertast.
