# Generación de imágenes (Santo del día / Evangelio del día)

Este documento estandariza cómo generar las imágenes requeridas por el panel:

- **Santo del día** (Fase 1)
- **Evangelio del día** (Fase 2)

## 1) Especificación (confirmada)

### Formato
- Tamaño: **1200 x 700**
- Tipo: **PNG o JPG**
- Peso recomendado: **< 600 KB**

### Contenido requerido (Santo del día)
- Escena representativa del santo.
- Espacio para una frase corta.
- Texto: `Santo del día`.
- Logo: escudo de la Diócesis de Neiva.
- Fecha.
- Nombre del santo.

### Contenido requerido (Evangelio del día)
- Escena representativa del evangelio.
- Espacio para frase corta (título).
- Texto: `Evangelio del día`.
- Cita bíblica completa con nombre del libro abreviado.
- Logo: escudo de la Diócesis de Neiva.

## 2) Dependencias (assets)

Requerido:
- `assets/branding/escudo-diocesis-neiva.png` (ideal: PNG con transparencia).

## 3) Recomendación técnica (para la automatización)

Para evitar generar imágenes “desde cero” cada vez:

- Mantener 2 plantillas base (fondos) en `assets/branding/templates/`:
  - `santo_base.png`
  - `evangelio_base.png`
- Renderizar overlays de texto (fecha, nombre, cita) con una fuente definida.
- Para “escena”:
  - Opción A (más simple): usar una imagen ilustrativa por santo/evangelio (requiere fuente/licencia).
  - Opción B: generar imagen por IA (solo si se define proveedor, costos y licencias) y luego componer overlays.

Nota: antes de implementar generación automática por IA, hay que definir política de derechos de autor y estilo.

## 4) Validación automática (recomendado)

En CI (o local) validar:
- Dimensiones exactas 1200x700.
- Formato permitido.
- Tamaño de archivo (bytes) por debajo del umbral.

