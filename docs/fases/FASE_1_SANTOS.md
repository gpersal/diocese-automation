# Fase 1 (Plan): Crear/Actualizar “Santos del día” (ventana futura)

## Objetivo

Automatizar la creación (o actualización) de los “Santos del día” requeridos para una ventana de fechas (p.ej. **próximos 15 días**) para que luego puedan seleccionarse en el formulario de “Dios Hoy”.

## Entradas

- `start_date`: fecha base (por defecto: hoy en `America/Bogota`).
- `days_ahead`: tamaño de ventana (por defecto: 15).
- `dry_run`: si true, no escribe en el panel; solo reporta.

## Fuente de verdad

- ACI Prensa:
  - Listado por mes: `https://www.aciprensa.com/santos/mes/{mes}`
  - Detalle del santo: `https://www.aciprensa.com/santo/{id}/{slug}`

Detalle: `docs/fuentes/ACIPRENSA.md`.

## Salida esperada

- En el panel de la Diócesis:
  - Santo creado si no existe.
  - O santo actualizado si existe pero cambió contenido (según política).
- Reporte:
  - `created[]`, `updated[]`, `skipped[]`, `errors[]`
  - mapeo `date -> santo_id_panel` (si aplica)

## Idempotencia (no duplicar)

Definir clave única para buscar santos existentes antes de crear:

Opciones (pendiente confirmar con la UI):
- Por **nombre normalizado** + **fecha (día/mes)**.
- Por **URL fuente** (ACI Prensa) almacenada en un campo “fuente”.
- Por **id ACI Prensa** almacenado en un campo custom.

Recomendación: si el panel permite un campo “fuente” (URL), usar esa como clave principal.

## Reglas (decisiones ya tomadas)

### Varios santos el mismo día
Decisión: si ACI Prensa lista varios santos para una fecha:
- Se pueden **crear todos** los santos en el panel.
- Para asociar a “Dios Hoy” (Fase 3), se escogerá **uno** de forma “aleatoria”.

Recomendación técnica:
- La selección debe ser **determinística por fecha** (misma fecha => mismo santo elegido) para:
  - evitar que re-ejecuciones cambien el santo,
  - permitir auditoría y comparaciones.

Implementación sugerida:
- Ordenar los santos del día por `aci_id` ascendente y seleccionar `index = hash(YYYY-MM-DD) % n`.

## Algoritmo recomendado (paso a paso)

1. Calcular la ventana `[start_date, start_date + days_ahead]`.
2. Agrupar fechas por `mes`.
3. Por cada mes requerido:
   - Descargar `/santos/mes/{mes}` una vez.
   - Parsear `<li>` para construir `day -> [ {name, url, aci_id, slug} ]`.
4. Para cada fecha de la ventana:
   - Obtener lista de santos para el día.
   - Aplicar política “varios santos”:
     - Crear/actualizar **todos** los santos listados para la fecha.
     - Mantener la lista de IDs del panel para que Fase 3 pueda escoger 1.
   - Para cada santo listado:
     - Descargar detalle del santo y extraer:
       - `name` (título)
       - `content_html` (div.page-content)
       - `image_url` (si existe)
       - `source_url` (URL de ACI)
   - En el panel:
     - Buscar si existe el santo (por clave única).
     - Si no existe: crear.
     - Si existe: decidir si actualizar (por hash del contenido o por política).

## Consideraciones de contenido

- El contenido de ACI viene como HTML con entidades (`&iacute;`, etc.).
  - Política: almacenar HTML “tal cual” o convertir a texto plano.
- Imágenes:
  - Confirmar si el panel soporta “URL de imagen” o requiere upload.
  - Si requiere upload, decidir estrategia (descarga+upload vs solo texto).

## Requisitos del panel (confirmado)

URL del módulo:
- `https://admin.diocesisdeneiva.org/espiritualidad/santos`

Flujo:
1. Verificar si ya existe el santo usando el cuadro de búsqueda.
2. Si no existe: click en `Agregar santo`.
3. Campos:
   - `Nombre` (requerido).
   - `Imagen del santo` (requerido):
     - 1200x700, formato web PNG/JPG, ideal < 600KB.
     - Debe incluir: escena, espacio para frase corta, texto “Santo del día”, logo/escudo Diócesis de Neiva, fecha, nombre del santo.
   - `Biografía del santo` (requerido):
     - 3 a 5 párrafos, con referencias (pueden basarse en ACI Prensa).
     - Puede incluir la virtud que mejor representó el santo.
4. Click en `Agregar santo`.

Dependencia:
- Se requiere el archivo del **escudo/logo** para componer las imágenes (pendiente de incorporar en `assets/`).

## Errores esperados y mitigación

- ACI cambia estructura HTML:
  - Mitigación: selectores robustos + tests con fixtures.
- ACI bloquea por rate:
  - Mitigación: throttling.
- Panel cambia selectores:
  - Mitigación: screenshots/HTML en fallos + fallbacks.

## Criterios de aceptación

- Para un rango de 15 días, el sistema debe:
  - Detectar santos del día para cada fecha (si ACI tiene).
  - Crear al menos 1 santo por día cuando aplique.
  - No duplicar santos ya creados.
  - Generar un reporte final con conteos.

## Preguntas abiertas (bloqueantes)

1. ¿El panel obliga a que el “Santo del día” esté ligado a una fecha específica o es un catálogo que se reutiliza en diferentes años?
2. ¿Dónde se carga/obtiene el escudo de la Diócesis para generar las imágenes?
