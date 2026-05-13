# Fuente: ACI Prensa (Santoral)

Objetivo de uso en la automatización:

- Identificar el/los **santo(s) del día** para una fecha.
- Obtener el contenido del santo (nombre, imagen, texto/biografía corta) para crear/actualizar el “Santo del día” en el panel de la Diócesis.

## 1) URLs relevantes

### 1.1. Listado general
- `https://www.aciprensa.com/santos`

### 1.2. Listado por mes (recomendado para automatización)
- `https://www.aciprensa.com/santos/mes/{mes}`
  - `{mes}` = 1..12
  - El HTML contiene una lista de `<li>` donde aparece:
    - Un link al santo: `https://www.aciprensa.com/santo/{id}/{slug}`
    - Una etiqueta textual del día/mes: p.ej. `7 febrero`

Estrategia recomendada:
- Para una ventana de días, agrupar por mes y descargar cada mes **una sola vez**, luego filtrar.

### 1.3. Detalle del santo
- `https://www.aciprensa.com/santo/{id}/{slug}`

En esta página típicamente existen:
- Título: `<h1 class="page-title">…</h1>`
- Contenido HTML: `<div class="page-content">…</div>`
- Imagen (dentro del contenido), si existe.
- Links alternos: “Biografía…”, “Oración…”, etc. (opcionales).

## 2) Consideraciones de modelado

### Varios santos el mismo día
ACI Prensa puede listar más de un santo en el mismo día.

Política pendiente de definir:
- Opción A: usar el **primer santo** del listado (simple).
- Opción B: usar un santo “principal” (si se puede inferir).
- Opción C: crear varios santos y que la asociación en “Dios Hoy” sea manual.

## 3) Consideraciones operativas

- Respetar rate limits (p.ej. 1 request/segundo) para evitar bloqueos.
- Usar `User-Agent` estable.
- Cachear respuestas del mes si la ejecución corre con frecuencia (opcional).
- Tener tolerancia a cambios menores de HTML (parse con selectores robustos).

