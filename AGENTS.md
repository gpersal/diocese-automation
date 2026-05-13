# AGENTS.md (diocese-automation)

Este repositorio mantiene automatizaciones (GitHub Actions + automatización de navegador) para el módulo **“Dios Hoy”** del panel de administración de la Diócesis de Neiva.

## Skills (Codex)

Los skills NO se guardan dentro del repositorio: se instalan de forma global en el perfil del usuario en:

`~/.codex/skills/`

En este entorno ya están instalados:

- `doc` (para documentación y `.docx`)
- `playwright` (para automatización de navegador desde terminal)
- `security-best-practices` (solo cuando se solicite revisión de seguridad)

Uso:
- Nómbralos en el prompt como `$doc`, `$playwright`, `$security-best-practices` para que Codex los aplique.

Más detalle: `docs/skills/SKILLS_RECOMENDADOS.md`

