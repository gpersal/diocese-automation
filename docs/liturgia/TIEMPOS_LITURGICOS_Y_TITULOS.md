# Especificación: Tiempos Litúrgicos, Fechas, Colores y “Título del día”

Documento guía (Rito Romano) para estandarizar:

- **Tiempo litúrgico** por fecha.
- **Color litúrgico** a seleccionar.
- **Formato del campo “Título del día”** del módulo “Dios Hoy”.

> Recomendación: usar Ordo Colombiano como fuente operativa para derivar semana/tiempo/color y solo caer en reglas manuales cuando el Ordo no alcance (ver `docs/fuentes/ORDO_COLOMBIANO.md`).
>
> Referencia oficial para resolver dudas de colores: `docs/liturgia/FUENTES_OFICIALES_VATICANO.md`.

## 1) Colores litúrgicos (reglas generales)

- **Verde:** Tiempo Ordinario.
- **Morado:** Adviento y Cuaresma (tiempos penitenciales).
- **Blanco:** Tiempo de Navidad y Tiempo Pascual; celebraciones del Señor (excepto Pasión), de la Virgen María, ángeles y santos no mártires.
- **Rojo:** Domingo de Ramos y Viernes Santo; Pentecostés; apóstoles, evangelistas y mártires.
- **Rosa:** opcional (si existe la opción en el portal) en:
  - **III Domingo de Adviento** (Gaudete).
  - **IV Domingo de Cuaresma** (Laetare).
- **Negro:** opcional en Misas de difuntos (según costumbre local).
- **Azul:** no es color “universal” del Rito Romano; su uso puede depender de privilegios/indultos y costumbre local (p.ej. algunas celebraciones marianas). En el portal existe en el select; definir política editorial antes de automatizar su uso.

### Casos “Verde o Blanco”
Es común que el Ordo indique alternativas (p.ej. “Feria o BMV, Verde o Blanco”).

Política (pendiente definir con el equipo editorial):
- Opción A: siempre elegir el primer color (p.ej. Verde).
- Opción B: elegir Blanco solo si se decide celebrar BMV.
- Opción C: dejar “pendiente de revisión” (si el portal lo permite) y que lo ajuste un encargado.

## 2) Reglas de “Título del día” (formato)

### 2.1. Regla base (días de feria)
Formato recomendado:

`{DíaSemana} de la {SEMANA_EN_ROMANO} semana de {tiempo}`

Ejemplos:
- `Martes de la IV semana de Adviento`
- `Jueves de la II semana de Cuaresma`
- `Sábado de la XXVII semana del tiempo ordinario`

### 2.2. Regla base (domingos)
Formato recomendado:

`Domingo {SEMANA_EN_ROMANO} de {tiempo}`

Ejemplos:
- `Domingo II de Adviento`
- `Domingo IV de Cuaresma`
- `Domingo IV del tiempo ordinario`

### 2.3. Tiempo Ordinario (no diferenciar I/II)
Aunque el año tiene dos bloques (antes y después de Pascua), en el título:

- Se escribe **siempre** `del tiempo ordinario`.
- No se escribe “I/II Tiempo Ordinario”.

Ejemplos válidos:
- `Miércoles de la V semana del tiempo ordinario`
- `Domingo XXXI del tiempo ordinario`

### 2.4. Semana Santa y Triduo Pascual (títulos por día)
En **Semana Santa** no se usa “semana I/II…”, sino nombres propios:

- `Domingo de Ramos` (o “Domingo de Ramos de la Pasión del Señor”, si desean el nombre largo)
- `Lunes Santo`
- `Martes Santo`
- `Miércoles Santo`
- `Jueves Santo`
- `Viernes Santo`
- `Sábado Santo`
- `Domingo de Pascua`

### 2.5. Octava de Pascua
Los días posteriores a Pascua hasta el sábado:

- `Lunes de la Octava de Pascua`
- `Martes de la Octava de Pascua`
- …
- `Sábado de la Octava de Pascua`

El domingo siguiente:
- `Domingo de la Misericordia` (también es `II Domingo de Pascua`).

Luego:
- `Lunes de la II semana de Pascua` … hasta `Domingo de Pentecostés`.

## 3) Tiempos litúrgicos: inicio, fin y títulos típicos

### 3.1. Adviento
- **Inicio:** I Domingo de Adviento (entre 27 de noviembre y 3 de diciembre).
- **Fin:** antes de las I Vísperas de Navidad (en la práctica, antes de la Misa de Noche del 24 de diciembre).
- **Color:** morado (rosa opcional en III Domingo: Gaudete).
- **Títulos:**
  - `Domingo I/II/III/IV de Adviento`
  - `{DíaSemana} de la I/II/III/IV semana de Adviento`

### 3.2. Navidad
- **Inicio:** Navidad del Señor (desde la tarde del 24 de diciembre).
- **Fin:** Fiesta del Bautismo del Señor.
- **Color:** blanco.
- **Títulos:**
  - `Navidad del Señor` / `Sagrada Familia` / `Santa María, Madre de Dios` / `Epifanía` / `Bautismo del Señor`
  - En la Octava: `{DíaSemana} de la Octava de Navidad`

### 3.3. Tiempo Ordinario
- **Inicio (primer bloque):** día siguiente al Bautismo del Señor.
- **Pausa:** se interrumpe con el inicio de Cuaresma.
- **Reinicio (segundo bloque):** después de Pentecostés.
- **Fin:** antes del I Domingo de Adviento.
- **Color:** verde.
- **Títulos:**
  - `Domingo {N} del tiempo ordinario`
  - `{DíaSemana} de la {N} semana del tiempo ordinario`

### 3.4. Cuaresma
- **Inicio:** Miércoles de Ceniza.
- **Fin:** antes de la Misa de la Cena del Señor (Jueves Santo).
- **Color:** morado (rosa opcional en IV Domingo: Laetare).
- **Títulos:**
  - `Miércoles de Ceniza`
  - `Domingo I/II/III/IV/V de Cuaresma`
  - `{DíaSemana} de la I/II/III/IV/V semana de Cuaresma`

### 3.5. Triduo Pascual
- **Inicio:** Misa de la Cena del Señor (Jueves Santo por la tarde/noche).
- **Fin:** concluye con las Vísperas del Domingo de Pascua.
- **Colores típicos:**
  - Jueves Santo: blanco
  - Viernes Santo: rojo
  - Vigilia Pascual y Pascua: blanco

### 3.6. Tiempo Pascual
- **Inicio:** Domingo de Pascua.
- **Fin:** Domingo de Pentecostés.
- **Color:** blanco (Pentecostés rojo).
- **Títulos:**
  - Octava: `… de la Octava de Pascua`
  - Luego: `{DíaSemana} de la II/III/IV/V/VI/VII semana de Pascua`
  - **Ascensión del Señor:** tradicionalmente jueves de la VI semana de Pascua (40 días después de Pascua); en algunos lugares se traslada al domingo.
  - `Domingo de Pentecostés`

### 3.7. Cierre del año litúrgico
Al final del Tiempo Ordinario:
- `Nuestro Señor Jesucristo, Rey del Universo` (solemnidad que cierra el año litúrgico).

## 4) Implementación recomendada (para automatización)

Para construir el “Título del día” y el “Color del día” de manera robusta:

1. Tomar **fecha objetivo** (YYYY-MM-DD) en `America/Bogota`.
2. Consultar Ordo Colombiano para obtener al menos:
   - `tiempo_liturgico`
   - `encabezado` (contiene semana y a veces nombres propios)
   - `colores_dia`
3. Aplicar reglas:
   - Si el `encabezado` contiene una celebración con nombre propio (Semana Santa/Triduo), usar el nombre.
   - Si no, construir desde (día semana + semana + tiempo) usando números romanos.

### Nota: colores disponibles en el portal (confirmado)
El select “Color del día” del panel permite exactamente:
- `Verde`, `Morado`, `Rojo`, `Rosado`, `Negro`, `Azul`, `Blanco`.

Si no se selecciona un color, el portal usa el color por defecto del tiempo/celebración y puede sobrescribirlo por celebraciones particulares.

> Las reglas de excepción (Domingo de Misericordia, Octavas, etc.) deben estar cubiertas por tests con fechas reales.
