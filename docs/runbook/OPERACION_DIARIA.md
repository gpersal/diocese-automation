# Runbook: Operación diaria (Dios Hoy)

## Objetivo

Describir la operación diaria recomendada (automatización + revisión humana) para minimizar errores visibles en la página de la Diócesis.

## Ejecuciones recomendadas

1. **Preparación de ventana futura (Fases 1-3)**
   - Decisión tomada: **diaria**.
   - Resultado: próximos días listos (título, color, evangelio, santo, autor, reflexión base).
   - Nota: por limitación del Ordo UI, el rango mínimo garantizado para texto completo vía Ordo es `hoy..hoy+3`.
     - Para rangos mayores, aplicar fuentes alternas con verificación de cita (ver `docs/fuentes/LECTURAS_OFICIALES_ALTERNAS.md`).

2. **Ejecución diaria del video (Fase 0)**
   - Frecuencia: varias veces al día (para tolerar retrasos en publicación del video).
   - Resultado: el día actual queda con el video embebido.

## Checklist de revisión humana (post-ejecución)

### Previos al día de publicación (ventana futura)
Para una muestra (o todos los días si se requiere):
- Título del día:
  - Semana en romano, tiempo correcto, nombres propios en Semana Santa/Octavas.
- Evangelio:
  - Coincide con Ordo (referencia y/o contenido).
- Santo:
  - Coincide con ACI Prensa (si aplica).
- Color:
  - Coincide con Ordo y con política en casos “Verde o Blanco”.
- Autor:
  - Es el Obispo y el texto está exactamente en el formato requerido.

### Durante el día de publicación (día actual)
- Verificar que el video se insertó correctamente:
  - Está dentro del editor de “Reflexión del día”.
  - Se visualiza en la página pública (si aplica).

## Qué hacer si falla una automatización

1. Revisar artifacts del workflow:
   - `logs/diocesis.log`
   - `debug-*.png` / `debug-*.html` (si existen)
2. Identificar fase donde falló (buscar `fase=` en logs).
3. Acción correctiva:
   - Si fue un selector roto: ajustar selectores y reintentar.
   - Si fue timeout: aumentar timeout o retries.
   - Si fue CAPTCHA: ejecutar manual o reducir frecuencia.
