# Automations: Diócesis de Neiva (Dios Hoy)

Repositorio para automatizar, por fases, la publicación diaria de contenido en el módulo **“Dios Hoy”** del panel de administración de la Diócesis de Neiva.

## Estado actual

- ✅ **Fase 0 (implementada):** inserta/actualiza el **video de YouTube** dentro del editor WYSIWYG de la **reflexión del día** (en la fecha actual).
  - Workflow: `.github/workflows/diocesis-schedule.yml`
  - Script: `import os.py`

## Plan (en diseño)

- **Fase 1:** Crear/actualizar “Santos del día” (siguiente ventana de días).
- **Fase 2:** Crear/actualizar “Evangelio del día” (siguiente ventana de días).
- **Fase 3:** Publicar “Dios Hoy” (crear el día y asociar Evangelio + Santo + color + autor + texto base de reflexión).

La documentación (plan + especificaciones) está en `docs/`.

## Documentación

- Índice: `docs/README.md`
- Plan maestro: `docs/PLAN_AUTOMATIZACION.md`
- Liturgia (títulos, fechas, colores): `docs/liturgia/TIEMPOS_LITURGICOS_Y_TITULOS.md`
- Fases: `docs/fases/`
- Fuentes: `docs/fuentes/`
- Runbook operación: `docs/runbook/`

