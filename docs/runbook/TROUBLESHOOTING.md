# Troubleshooting: Dios Hoy Automation

## Login falla / Timeout en login

Síntomas:
- Error “No se pudo iniciar sesión…”

Posibles causas:
- CAPTCHA / reCAPTCHA.
- Cambió el formulario o IDs (`email`, `password`).
- Latencia del panel.

Acciones:
- Revisar artifacts `debug-login_timeout-*.png/html`.
- Confirmar manualmente si aparece CAPTCHA.
- Ajustar `DIOCESIS_LOGIN_TIMEOUT` y `DIOCESIS_PAGE_LOAD_TIMEOUT`.

## No se abre “Evangelio y santo”

Síntomas:
- Se cae en `/espiritualidad/evangelios` (listado global) en vez de la vista del día.

Acciones:
- Revisar logs `pagina_incorrecta_evangelios_listado`.
- Revisar artifacts del label `open_evangelio_santo`.
- Ajustar heurísticas de `infer_evangelio_url()` si cambió el DOM.

## No encuentra editor WYSIWYG

Síntomas:
- Timeout esperando `div[contenteditable='true']`.

Acciones:
- Revisar si el botón “Editar reflexión” cambió.
- Aumentar `EVANGELIO_TIMEOUT`.
- Guardar artifacts antes y después de click.

## Video no se inserta / se duplica

Síntomas:
- No aparece iframe o aparecen varios.

Acciones:
- Revisar si el editor cambió la clase del iframe (`iframe.ql-video`).
- Revisar el selector `DIOCESIS_VIDEO_URL_SELECTOR`.
- Verificar `DIOCESIS_VIDEO_TITLE_REQUIRE/FORBID/REGEX` (selección de video).

## Cambios del panel (UI/DOM)

Acción recomendada:
- Evitar selectores por posición.
- Preferir:
  - texto visible exacto (cuando es estable)
  - atributos `href` con subrutas
  - roles (`role=dialog`) y ancestros de formularios

