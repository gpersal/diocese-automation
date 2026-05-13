# Skills recomendados (skills.sh) para esta automatización

Este proyecto mezcla:

- Automatización de navegador (panel admin).
- Scraping/consumo de fuentes externas (Ordo, ACI Prensa).
- Manejo de secretos y observabilidad (logs, artifacts).

Para acelerar desarrollo/mantenimiento con agentes (Codex u otros), se recomienda incorporar skills del ecosistema de [skills.sh](https://skills.sh).

## 1) Skills recomendados (mínimo)

1. `doc`
   - Para mantener documentación consistente (plan, fases, runbooks).
2. `playwright`
   - Para fortalecer automatización de navegador (alternativa a Selenium; mejor tooling para waits, traces y selectors).
3. `security-best-practices`
   - Para endurecer manejo de secretos, logs y artefactos.

## 2) Instalación (Codex)

Si usas Codex, puedes instalar skills usando el “skill-installer” (repo `openai/skills`).

Comando de referencia:
```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo openai/skills \
  --path skills/.curated/doc skills/.curated/playwright skills/.curated/security-best-practices
```

Luego:
- Reiniciar Codex para que cargue los skills.

### Nota importante: “no se ven en el proyecto”
Los skills se instalan de forma global (perfil del usuario) en `~/.codex/skills/` y por diseño **no** aparecen como archivos dentro del repo.

En este entorno se confirmó que existen en:
- `~/.codex/skills/doc`
- `~/.codex/skills/playwright`
- `~/.codex/skills/security-best-practices`

## 3) Preguntas abiertas

- ¿Se quiere migrar la automatización del panel a Playwright (en vez de Selenium) para trazas y debugs más fáciles?
