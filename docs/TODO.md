# TODO (Dinámico) – Diocese Automation

Este archivo se actualiza a medida que avanzamos. Mantiene el estado real del trabajo.

## Now (en progreso)

- [ ] Implementar PoC Playwright para Ordo UI (para reemplazar/robustecer Selenium cuando sea posible).

## Next (siguiente)

- [ ] Integrar el scraper de CEC como fallback en la implementación real de Fase 2 (cuando exista la Fase 2 real).
- [ ] Definir e incorporar `assets/branding/escudo-diocesis-neiva.png` (insumo bloqueante para generación de imágenes).
- [ ] Definir estrategia final de imágenes (plantillas vs IA vs reutilización de CEC) y criterios de aprobación editorial/legal.

## Blocked (bloqueado)

- [ ] Confirmar de dónde proviene el escudo/logo oficial en formato usable (PNG con transparencia) y si puede versionarse en el repo.

## Done (completado)

- [x] Documentar Ordo UI como fuente para texto completo (con limitación ±3 días).
- [x] Confirmar `node/npm/npx` instalados para habilitar Playwright.
- [x] Documentar CEC como segunda fuente de verdad y Vatican News como respaldo.
- [x] Implementar scraper CEC “Evangelio diario” (RSS -> artículo -> extracción de cita + texto): `scripts/cec_evangelio_scraper.py`
