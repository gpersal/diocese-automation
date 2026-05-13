# Fuente: Ordo Colombiano (CEC)

Objetivo de uso en la automatización:

- Determinar **tiempo litúrgico**, **semana**, **celebración** y **color** por fecha.
- Obtener **referencias** de lecturas (incluyendo referencia del evangelio).
- Usar el `encabezado` como apoyo para construir el “Título del día”.

## 1) Formas de consumo

### 1.1. Web (Angular)
Sitio:
- `https://web-ordo-colombiano.cec.org.co/`

Rutas relevantes (UI):
- `/liturgico`
- `/detalle-liturgico`
- `/inicio`
- `/detalle-dia-liturgico`
- `/lectura-dia`

#### Ruta “Lecturas del día” (UI) (confirmado)
Para obtener el **texto completo** de cada lectura (incluyendo el evangelio), se debe navegar así:

1. Entrar a `https://web-ordo-colombiano.cec.org.co/inicio`.
2. Seleccionar la fecha usando las flechas `ANTERIOR` / `SIGUIENTE` (en la vista de inicio).
3. Hacer click en la tarjeta superior del día (fecha/semana).
4. Click en el botón/tarjeta `Lecturas del día`.
5. En la vista final se ve el texto por secciones:
   - `Primera lectura`, `Salmo`, `Segunda lectura`, `Aclamación`, `Evangelio`.

Implicación:
- El texto completo **sí existe** en la UI; por tanto Fase 2 puede obtenerlo por automatización de navegador.
- Nota técnica: `/lectura-dia` depende del estado de navegación del SPA; abrir la URL directamente puede redirigir a `/inicio`.

Limitación confirmada:
- La navegación por flechas parece permitir solo **~3 días adelante y ~3 días atrás**.
  - Implicación: no alcanza por sí sola para preparar 15 días en una sola ejecución.
  - Mitigación: correr extracción diaria (rolling window) o usar otra fuente oficial/confiable para el texto cuando se requiera un rango mayor (ver `docs/fuentes/LECTURAS_OFICIALES_ALTERNAS.md`).

### 1.2. API (recomendada para automatización)

El frontend del Ordo consume una API con headers fijos (`API-KEY`, `API-TOKEN`, `API-NAME`).

Endpoint útil para obtener el **año litúrgico completo**:
- `GET https://74j2tngwfd.execute-api.us-east-1.amazonaws.com/api-app/ediciones/obtener-contenido-completo`

Headers requeridos:
- `Content-Type: application/json`
- `API-KEY: ...`
- `API-TOKEN: ...`
- `API-NAME: APP-ORDO`

> Nota operativa: estos valores existen en el frontend del Ordo. Aun así, se recomienda tratarlos como **configurables por variables de entorno** para evitar hardcode.

## 2) Campos relevantes (según respuesta del endpoint)

En cada objeto del array `data` (por fecha) existen campos como:

- `fecha` (YYYY-MM-DD)
- `tiempo_liturgico` (p.ej. “I TIEMPO ORDINARIO”, “CUARESMA”, etc.)
- `encabezado` (string humano, suele incluir semana y color)
- `colores_dia` (string, a veces con alternativas como “Verde o Blanco”)
- `celebracion` / `nombre_celebracion` (cuando aplica)
- `misa` (HTML con referencias del leccionario)
- `primera_lectura` / `segunda_lectura` (HTML, si está disponible)
- `reflexion` / `reflexion_audio` (si existe en el Ordo)

### Observación importante (impacta Fase 2)
En la data consultada, los campos `evangelio`, `salmo` y `aclamacion` vienen como string vacío.

Implicación:
- Para obtener la **referencia** del evangelio, se recomienda extraerla del HTML `misa`, donde suele aparecer al final (p.ej. `Mc 6,30-34.`).
- Si el panel de la Diócesis requiere **texto completo** del evangelio, debe definirse una fuente adicional o confirmar si hay otro endpoint del Ordo que lo entregue.

## 3) Estrategia de extracción recomendada

1. Descargar `obtener-contenido-completo` una vez por ejecución (cachear en disco si se desea).
2. Filtrar por ventana objetivo (p.ej. hoy..hoy+15).
3. Para cada día:
   - Derivar `color` desde `colores_dia` (aplicando política para alternativas).
   - Derivar semana/tiempo desde `encabezado` y `tiempo_liturgico`.
   - Extraer referencia del evangelio desde `misa` (regex).
   - Nota: para Fase 2, el panel requiere el **texto completo** del evangelio. Con el API actual, esto es un bloqueante (ver abajo).

## 4) Riesgos

- Respuestas HTTP 5xx transitorias (recomendado: retries con backoff).
- Cambios de formato del HTML `misa` (recomendado: tests con fixtures y regex tolerantes).

## 5) Gap actual (bloqueante para “contenido del evangelio”)

En las consultas realizadas al endpoint `obtener-contenido-completo`, los campos:
- `evangelio`
- `salmo`
- `aclamacion`
llegan vacíos.

El HTML `misa` sí trae las **referencias** (p.ej. `Mc 6,30-34`) pero no el **texto completo**.

Acción requerida para poder implementar Fase 2 correctamente:
- Identificar dentro del Ordo una fuente que entregue el texto completo por cita (endpoint, HTML, PDF, etc.), o validar con el equipo editorial si existe otro camino autorizado.

### Solución acordada (cierra el gap)
Se usará la **UI** del Ordo (`/inicio` -> `Lecturas del día`) para extraer el texto completo del evangelio.

Implementación propuesta (PoC):
- Script Selenium: `scripts/ordo_lecturas_selenium.py`
