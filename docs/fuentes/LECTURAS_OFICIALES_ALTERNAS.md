# Fuentes alternas (oficiales/confiables) para “Lecturas del día”

Este documento define opciones para obtener el **texto completo** de las lecturas cuando:

- el Ordo Colombiano (UI) no alcanza por su limitación de navegación (~±3 días), o
- se requiera redundancia ante fallas del Ordo.

## 1) Reglas de uso (política)

1. **Primera fuente (preferida):** Ordo Colombiano (CEC) para:
   - calendario litúrgico y color (Colombia),
   - referencia/cita por fecha,
   - y texto completo cuando el rango lo permita.
2. **Fuentes alternas:** se permiten si son reconocidas oficialmente y confiables.
3. **Trazabilidad obligatoria:**
   - Registrar para cada día cuál fuente se usó para el texto completo.
   - Validar que la **cita bíblica** obtenida de la fuente alterna coincide con la cita derivada del Ordo.
   - Si no coincide: marcar como “requiere revisión humana” (no publicar automáticamente).

## 2) Opción A: Vatican News (Dicasterio para la Comunicación)

Vatican News publica “Evangelio y palabra del día” en español por fecha, con texto completo.

URLs:
- RSS: `https://www.vaticannews.va/es/evangelio-de-hoy.rss.xml`
- Por fecha: `https://www.vaticannews.va/es/evangelio-de-hoy/YYYY/MM/DD.html`
  - Ejemplo: `https://www.vaticannews.va/es/evangelio-de-hoy/2026/02/07.html`

Ventajas:
- Fuente vinculada directamente a la Santa Sede (Vatican News).
- No depende de navegación por flechas; se puede pedir cualquier fecha.
- Incluye al menos:
  - “Lectura del Día” (1ra lectura o lectura principal),
  - “Evangelio del Día” (texto completo).
- Incluye una nota de copyright del leccionario utilizado en esa publicación.

Riesgos:
- Puede usar una edición/permiso de leccionarios no idéntica al Ordo colombiano (por calendario local o edición bíblica).
- Puede no incluir todas las secciones en algunos días (p.ej. 2da lectura) o variar el formato.

Uso recomendado:
- Como respaldo para **texto completo** si:
  - la cita bíblica coincide con la del Ordo (por fecha),
  - y el formato cumple los campos requeridos por el panel.

## 3) Opción B: CEC (Conferencia Episcopal de Colombia) – “Evangelio diario”

La CEC publica el “Evangelio diario” por fecha con:
- Cita (p.ej. `Mc 6, 30-34`)
- Texto completo del evangelio
- Imagen 1200x700 (útil como insumo si se decide reutilizarla)

URLs:
- Categoría: `https://www.cec.org.co/categorias-articulos/evangelio-diario`
- RSS (taxonomía): `https://www.cec.org.co/taxonomy/term/8097/feed`
- Artículo por día (ejemplo):
  - `https://www.cec.org.co/evangelio-diario/07-de-febrero-lectura-del-santo-evangelio-segun-san-marcos-mc-6-30-34`

Ventajas:
- Fuente nacional (CEC), muy alineada con el uso en Colombia.
- URLs estables por artículo + RSS para descubrir publicaciones.
- Contenido ya viene en HTML limpio (párrafos y saltos de línea).

Riesgos:
- Es “solo evangelio” (no necesariamente incluye primera/segunda lectura, salmo, etc.).
- Puede existir variación editorial en títulos/encabezados; por eso se debe validar que la **cita** coincida con la del Ordo.

Uso recomendado:
- Como segunda fuente para el **texto completo del evangelio** cuando el Ordo UI no alcance por la limitación de ±3 días.

## 4) Opción C: USCCB (Conferencia Episcopal de EEUU) – Biblia y lecturas

USCCB publica lecturas diarias (incluye español) y expone RSS.

Ejemplo (RSS español):
- `https://bible.usccb.org/readings/rss/es`

Ventajas:
- Fuente institucional (conferencia episcopal).
- Estructura relativamente consistente.

Riesgos:
- Puede diferir del Ordo colombiano por calendario local, traducción aprobada y permisos/copyright.
- Requiere revisar condiciones de uso para redistribución.

Uso recomendado:
- Solo como respaldo si Vatican News no está disponible o si se aprueba explícitamente su uso editorial/legal.

## 5) Algoritmo propuesto (selección automática con control)

Para cada fecha `D`:
1. Obtener desde Ordo (API) el día litúrgico y **cita** esperada (evangelio) para `D`.
2. Intentar obtener texto completo desde Ordo (UI) si `D` está dentro de ±3 días.
3. Si no se puede:
   - Consultar CEC “Evangelio diario” para `D` (vía RSS o búsqueda por fecha).
   - Extraer texto y cita.
   - Si la cita coincide con la del Ordo: aceptar el texto.
   - Si no coincide: fallback a Vatican News y marcar `requires_review` si persiste la discrepancia.
4. Guardar `source_used` (`ordo_ui` / `cec` / `vatican_news` / `usccb`) para auditoría.
