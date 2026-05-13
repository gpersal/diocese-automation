# Fase 0 (Implementada): Inserción de Video en “Reflexión del día”

## Objetivo

Actualizar el contenido del editor WYSIWYG de la **reflexión** del día actual en “Dios Hoy” para:

- Insertar el video más reciente de YouTube (serie “Gotitas de esperanza”) embebido.
- Evitar duplicados (si ya existe un embed del mismo video).
- Normalizar tamaño/alineación del iframe.

## Implementación actual

- Workflow: `.github/workflows/diocesis-schedule.yml`
- Script: `import os.py`

### Flujo (alto nivel)
1. Leer credenciales `DIOCESIS_USERNAME` / `DIOCESIS_PASSWORD`.
2. Leer feed de YouTube y seleccionar el video más reciente (con heurísticas de título).
3. Abrir Chrome headless (Selenium).
4. Login al panel.
5. Ir a “Dios Hoy” y seleccionar el **día del mes actual**.
6. Abrir “Evangelio y santo” (evita caer en listado global).
7. Seleccionar “evangelio actual” y habilitar “Editar reflexión”.
8. Encontrar el editor y:
   - Si ya existe un iframe del video: normalizar.
   - Si no existe: insertar después del marcador `Reflexión del día` (o al final si no lo encuentra).
9. Guardar.

## Variables de entorno (workflow)

Principales:

- `DIOCESIS_USERNAME` (secret)
- `DIOCESIS_PASSWORD` (secret)
- `DIOCESIS_LOG_DIR` (por defecto: `logs/` en Actions)
- `DIOCESIS_LOG_LEVEL` (INFO)

Selección del video:
- `DIOCESIS_VIDEO_TITLE_REGEX`
- `DIOCESIS_VIDEO_TITLE_REQUIRE` (CSV tokens)
- `DIOCESIS_VIDEO_TITLE_FORBID` (CSV tokens)

Robustez:
- `DIOCESIS_PAGE_LOAD_TIMEOUT`
- `DIOCESIS_LOGIN_TIMEOUT`
- `DIOCESIS_EVANGELIO_TIMEOUT`
- `DIOCESIS_GET_RETRIES`
- `DIOCESIS_GET_RETRY_WAIT`

Render:
- `DIOCESIS_VIDEO_WIDTH`
- `DIOCESIS_VIDEO_HEIGHT`

## Requisitos / precondiciones

- Debe existir el “día” en **Dios Hoy** para la fecha actual.
- Debe existir al menos un “evangelio actual” seleccionable para que se habilite la edición de reflexión (según estado del panel).
- El editor debe contener (idealmente) el marcador `Reflexión del día` para insertar el video en el lugar correcto.

## Observabilidad

- Se escribe `logs/diocesis.log`.
- En fallos, se guardan artefactos de depuración:
  - PNG (screenshot)
  - HTML de la página
- El workflow sube `logs/` como artifact y deja tail en el summary.

## Riesgos conocidos

- CAPTCHA en login (bloquea automatización).
- Cambios en textos/botones (“Editar reflexión”, “Evangelios actuales”, etc.).
- Cambios del editor (Quill/selector `.ql-video`, modal de inserción).

