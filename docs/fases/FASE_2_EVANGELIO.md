# Fase 2 (Plan): Crear/Actualizar “Evangelio del día” (ventana futura)

## Objetivo

Automatizar la creación (o actualización) de “Evangelios” para una ventana de fechas (p.ej. **próximos 15 días**) basándose en el Ordo Colombiano, para que luego:

- puedan ser seleccionados en el formulario de “Dios Hoy” (Fase 3), y
- puedan ser usados por la automatización de video (Fase 0) en el día actual.

## Entradas

- `start_date`: fecha base (por defecto: hoy en `America/Bogota`).
- `days_ahead`: tamaño de ventana (por defecto: 15).
- `dry_run`: si true, no escribe en el panel; solo reporta.

## Fuente de verdad

- Ordo Colombiano (API):
  - Recomendado: `api-app/ediciones/obtener-contenido-completo`
  - Para texto completo del evangelio: UI `https://web-ordo-colombiano.cec.org.co/inicio` -> `Lecturas del día`
  - Nota: la UI parece permitir solo ~3 días adelante/atrás por flechas.

Detalle: `docs/fuentes/ORDO_COLOMBIANO.md`.

## Requisitos del panel (confirmado)

URL del módulo:
- `https://admin.diocesisdeneiva.org/espiritualidad/evangelios`

Flujo:
1. Verificar si ya existe el evangelio usando el cuadro de búsqueda.
   - Usar expresiones para consultar y luego validar resultados con capítulo y versículo.
2. Si no existe: click en `Agregar evangelio`.
3. Campos:
   - `Título` (requerido): frase corta que resuma (p.ej. “Parábola del sembrador”).
   - `Cita bíblica` (requerido): p.ej. “Mateo 4, 5-8”.
   - `Evangelio según` (requerido): seleccionar una opción entre:
     - `San Mateo`, `San Marcos`, `San Lucas`, `San Juan`.
   - `Imagen del evangelio` (requerido):
     - 1200x700, PNG/JPG, ideal < 600KB.
     - Debe incluir: escena, espacio para frase corta (título), texto “Evangelio del día”, cita bíblica completa con libro abreviado, logo/escudo Diócesis de Neiva.
   - `Contenido del evangelio` (requerido):
     - Debe ser el texto completo correspondiente a la cita bíblica, tomado del Ordo.
4. Click en `Agregar evangelio`.

Dependencia:
- Se requiere el archivo del **escudo/logo** para componer las imágenes (pendiente de incorporar en `assets/`).

## Salida esperada

- En el panel de la Diócesis:
  - Evangelio creado si no existe.
  - O evangelio actualizado si existe pero cambió referencia/contenido (según política).
- Reporte:
  - `created[]`, `updated[]`, `skipped[]`, `errors[]`
  - mapeo `date -> evangelio_id_panel`

## Idempotencia (no duplicar)

Clave única recomendada (pendiente confirmar con la UI):
- Por **fecha** del evangelio (si el panel modela por fecha).
- O por **referencia bíblica** + **fecha** (si hay duplicados por año/ciclo).

## Algoritmo recomendado (paso a paso)

1. Calcular la ventana `[start_date, start_date + days_ahead]`.
2. Descargar el dataset del Ordo (año completo o cache local) y filtrar por fechas.
3. Por cada fecha:
   - Derivar la **referencia del evangelio**.
     - Recomendado: parsear desde `misa` (HTML) con regex tolerante.
     - Ejemplo en `misa`: `... / Mc 6,30-34.`
   - (Opcional) Derivar otras lecturas de apoyo si el panel las necesita.
4. En el panel:
   - Buscar si ya existe el evangelio por clave única.
   - Crear/actualizar según política.

## Consideraciones y limitaciones del Ordo

En la data consultada, los campos `evangelio`, `salmo` y `aclamacion` aparecen vacíos, aunque `misa` contiene referencias.

Preguntas para cerrar:
- Confirmado: el panel requiere **texto completo** del evangelio.
  - Se usará Ordo como primera fuente y otras fuentes oficiales/confiables cuando sea necesario.

### Bloqueante actual detectado (para el plan)
En las consultas realizadas al API del Ordo, los campos `evangelio`, `salmo` y `aclamacion` llegan vacíos; el HTML de `misa` sí trae las **referencias**, pero no el **texto completo** del evangelio.

Implicación para Fase 2:
- La automatización puede determinar la **cita** del evangelio por fecha.
- Para cumplir “Contenido del evangelio (texto completo) tomado del Ordo” se usará la **UI** del Ordo, donde el texto completo está disponible por secciones.

### Solución acordada (UI scraping)
Se implementará extracción del evangelio (y otras lecturas) desde:

`/inicio` -> seleccionar día (flechas) -> abrir detalle -> `Lecturas del día` -> extraer secciones.

PoC: `scripts/ordo_lecturas_selenium.py`

### Impacto de la limitación +/-3 días (decisión pendiente)
Dado que la UI del Ordo parece limitar la navegación por flechas a ~3 días:
- Opción A (rolling window): la automatización prepara solo `hoy..hoy+3` y corre diariamente.
- Opción B (rango 15 días): usar Ordo como primera fuente cuando alcance; para el resto, usar otra fuente oficial/confiable para obtener el texto completo, manteniendo trazabilidad de la fuente usada.

Decisión tomada:
- Se correrá diario (Opción A).
- Para cubrir fechas fuera del alcance del Ordo UI (si se necesita), la segunda fuente aprobada es:
  - CEC (Conferencia Episcopal de Colombia): `https://www.cec.org.co/categorias-articulos/evangelio-diario`
  - Detalle en: `docs/fuentes/LECTURAS_OFICIALES_ALTERNAS.md`

## Errores esperados y mitigación

- Respuestas 5xx del API del Ordo:
  - Mitigación: retries con backoff; cache de respuesta por día.
- Cambios en el HTML `misa`:
  - Mitigación: fixtures y tests para regex.
- Cambios en el UI del panel para evangelios:
  - Mitigación: screenshots/HTML en fallos, selectores por texto/rol.

## Criterios de aceptación

- Para 15 días futuros, el sistema debe:
  - Determinar referencia del evangelio por fecha.
  - Crear/actualizar registros sin duplicar.
  - Reportar conteos y mapeos.

## Preguntas abiertas (bloqueantes)

1. ¿Dónde se carga/obtiene el escudo de la Diócesis para generar las imágenes?
2. ¿Qué traducción/biblia usa el Ordo para el texto completo? (solo para trazabilidad editorial)
3. Para el caso de rango > 3 días: ¿cuál(es) fuentes alternas oficiales/confiables aprobadas se usarán para el texto completo (y en qué orden de preferencia)?
