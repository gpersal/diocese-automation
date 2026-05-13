# Fase 3 (Plan): Publicación “Dios Hoy” (día + asociaciones)

## Objetivo

Automatizar la creación (o actualización) de entradas del módulo **“Dios Hoy”** para una ventana de fechas (p.ej. próximos 15 días), llenando el formulario del panel con la información estandarizada:

- Título del día (según liturgia)
- Fecha
- Evangelio del día (selección)
- Santo del día (selección opcional)
- Color del día
- Autor (Obispo)
- Reflexión del día (texto base con marcador para el video)

## Entradas

- `start_date`: fecha base (por defecto: hoy en `America/Bogota`).
- `days_ahead`: ventana (por defecto: 15).
- `author_name`: texto exacto del autor (configurable).
- Mapeos creados por fases previas:
  - `date -> evangelio_id_panel` (Fase 2)
  - `date -> santo_id_panel` (Fase 1, opcional)
- `dry_run`

## Fuente de verdad

- Ordo Colombiano: tiempo litúrgico, color y construcción del “Título del día”.
- Panel de la Diócesis: formulario de “Agregar día” en “Dios Hoy”.

Reglas litúrgicas: `docs/liturgia/TIEMPOS_LITURGICOS_Y_TITULOS.md`.

## URL del módulo (confirmado)

- `https://admin.diocesisdeneiva.org/espiritualidad/dios-hoy`

## Salida esperada

- En el panel:
  - Día creado para la fecha si no existe.
  - Día actualizado si existe (según política de “reparación”).

## Idempotencia (no duplicar)

Claves recomendadas (pendiente confirmar con UI):
- Por **fecha** del “día” (ideal).
- O por `title + fecha` (fallback).

Política recomendada:
- Si el día ya existe:
  - Verificar si están completos `evangelio`, `color`, `autor`.
  - Completar faltantes sin borrar contenido manual (especialmente la reflexión).

## Pasos detallados (flujo UI)

1. Login al panel con credenciales (GitHub Secrets).
2. Navegar a `Dios Hoy`.
3. Seleccionar el día en el calendario (por fecha objetivo, no solo “hoy”).
4. Determinar si el día ya existe:
   - Si la celda del calendario está en blanco: probablemente no existe.
   - Si la celda está en un color diferente a blanco (p.ej. azul o rojo): probablemente existe.
   - Confirmación al hacer click:
     - Si existe: el modal muestra el “Título del día” y botones `Editar día` y `Evangelio y santo`.
     - Si no existe: el modal muestra `Día sin registros` y botón `Agregar día`.
5. Clic en **`Agregar día`** (si no existe) o **`Editar día`** (si existe).
5. Completar formulario:

### 5.1. Campos del formulario

#### Título del día (Requerido)
- Formato y reglas: `docs/liturgia/TIEMPOS_LITURGICOS_Y_TITULOS.md`.
- Notas clave:
  - La **semana** en números romanos.
  - En tiempo ordinario: siempre `del tiempo ordinario` (sin I/II).
  - En Semana Santa: títulos por **día** (Domingo de Ramos, Lunes Santo, etc.).
  - En Octava de Pascua: `… de la Octava de Pascua`.

#### Fecha (Requerido)
- Debe coincidir con la fecha seleccionada en el calendario.

#### Evangelio del día (Requerido)
- Debe seleccionarse el evangelio correcto.
- Fuente para determinar cuál corresponde:
  - Ordo Colombiano (referencia bíblica).
- Dependencia:
  - Idealmente ya existe el evangelio (Fase 2). Si no existe, definir comportamiento:
    - Error (bloquea publicación) o
    - Crear en caliente (acopla Fase 2 dentro de Fase 3).

#### Santo del día (Opcional)
- Seleccionar según ACI Prensa (Fase 1).
- Si no existe en el panel: puede dejarse en blanco (según tu proceso actual).
- Si existen varios santos del día (Fase 1 crea varios):
  - Seleccionar **uno** usando selección “aleatoria determinística” por fecha para mantener idempotencia.
  - Recomendación: ordenar por `aci_id` ascendente y elegir `index = hash(YYYY-MM-DD) % n`.

#### Color del día
- Derivar del Ordo Colombiano.
- Valores exactos del select (confirmado):
  - `Verde`, `Morado`, `Rojo`, `Rosado`, `Negro`, `Azul`, `Blanco`.
- Nota del portal (confirmado):
  - Si no se selecciona un color, el portal usa el color por defecto del tiempo/celebración y puede sobrescribirlo por fiestas/memorias/martirios, etc.
- Política recomendada:
  - Si el Ordo indica 1 color: seleccionar ese color.
  - Si el Ordo indica alternativas (p.ej. “Verde o Blanco”): dejar sin seleccionar o aplicar criterio editorial definido.

#### Autor (Requerido)
- Obispo actual en formato:
  - `Monseñor [NOMBRE_COMPLETO]`
- Recomendación: variable `DIOCESIS_AUTHOR_NAME` para evitar cambios de código cuando cambie el obispo.

#### Reflexión del día (Requerido)
- Insertar el texto base: `Reflexión del día:`
- Importante:
  - Existe un workflow (Fase 0) que inserta el video de YouTube **después** de este marcador.
  - No cambiar el marcador sin actualizar Fase 0.

6. Guardar/Publicar.
7. Validar que el registro quedó creado:
  - Se ve en el listado del día.
  - Los selects quedaron con los valores correctos.

## Validaciones post-ejecución (automáticas y humanas)

### Automáticas (recomendadas)
- Releer el día creado y validar:
  - `title` no vacío y coincide con patrón esperado.
  - `color` coincide con Ordo.
  - `author` coincide con config.
  - `reflexion` contiene el marcador.

### Revisión humana (checklist)
Ver `docs/runbook/OPERACION_DIARIA.md`.

## Errores esperados y mitigación

- El calendario del panel no permite seleccionar fechas futuras:
  - Bloqueante: requiere cambio de estrategia (navegación por URL o paginación).
- Selects con valores dinámicos:
  - Mitigación: seleccionar por texto visible + normalización.
- Contenido WYSIWYG cambia:
  - Mitigación: insertar como HTML mínimo y validar.

## Criterios de aceptación

- Dado un rango de 15 días, el sistema:
  - Crea/actualiza cada día sin duplicar.
  - Asigna evangelio (requerido) y color correctamente.
  - Deja el marcador `Reflexión del día:` en el editor.

## Preguntas abiertas (bloqueantes)

1. ¿Qué pasa si el evangelio no existe aún? ¿Se permite publicar sin evangelio? (parece que no)
2. ¿Hay un estado “borrador” o todo queda visible al guardar?
