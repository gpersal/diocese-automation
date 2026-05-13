#!/usr/bin/env python3

"""
Extrae las lecturas del Ordo Colombiano navegando el sitio web (SPA) con Selenium.

Motivacion:
- El API del Ordo (ediciones/obtener-contenido-*) trae referencias y algunos campos, pero en consultas
  realizadas no entrega de forma consistente el texto completo del evangelio en campos JSON.
- La UI de https://web-ordo-colombiano.cec.org.co/lectura-dia SI muestra el texto completo, pero esa vista
  depende del estado de navegacion interno (no se puede abrir directo sin pasar por /inicio).

Este script reproduce el flujo:
/inicio -> seleccionar fecha (flechas) -> click en la tarjeta del dia -> click "Lecturas del dia" -> extraer secciones.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from datetime import date, datetime, timedelta

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


INICIO_URL = "https://web-ordo-colombiano.cec.org.co/inicio"


@dataclass(frozen=True)
class ReadingDay:
    iso_date: str
    header: str
    sections: dict[str, str]


def _parse_iso(d: str) -> date:
    return datetime.strptime(d, "%Y-%m-%d").date()


def _today_bogota_iso() -> str:
    # GitHub Actions ya define TZ=America/Bogota en workflows del repo.
    # Local: respetamos TZ si el usuario la configura; si no, es hora local.
    return datetime.now().date().isoformat()


def _new_driver(headless: bool = True) -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1400,900")
    options.page_load_strategy = "eager"
    return webdriver.Chrome(options=options)


def _click_by_text(wait: WebDriverWait, text: str) -> None:
    # XPath por texto visible. El Ordo usa componentes Ionic, asi que evitamos selectores fragiles.
    el = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                f"//*[normalize-space()='{text}']"
                f"|//*[self::ion-button or self::button or self::a][normalize-space()='{text}']"
                f"|//*[contains(@class,'button')][normalize-space()='{text}']",
            )
        )
    )
    el.click()


def _goto_day_by_arrows(driver: webdriver.Chrome, wait: WebDriverWait, delta_days: int) -> None:
    if delta_days == 0:
        return
    label = "SIGUIENTE" if delta_days > 0 else "ANTERIOR"
    steps = abs(delta_days)
    for _ in range(steps):
        _click_by_text(wait, label)
        # Debounce: la UI actualiza header/estado sin navegar.
        time.sleep(0.2)


def _open_day_detail(driver: webdriver.Chrome, wait: WebDriverWait) -> None:
    # En /inicio el "dia" se abre al hacer click en la tarjeta superior (fecha).
    # Selector robusto: primer elemento grande con la fecha (suele contener el icono de calendario).
    candidates = driver.find_elements(By.CSS_SELECTOR, "ion-card, .card, .carta, div")
    for el in candidates[:30]:
        try:
            if not el.is_displayed() or not el.is_enabled():
                continue
            txt = (el.text or "").strip()
            # Heuristica: la tarjeta superior contiene el nombre del mes (Enero..Diciembre) o un numero + mes.
            if any(m in txt for m in ("Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Setiembre", "Octubre", "Noviembre", "Diciembre")):
                el.click()
                return
        except WebDriverException:
            continue
    # Fallback: click al header grande si existe.
    header = driver.find_elements(By.CSS_SELECTOR, "ion-title, h1, h2")
    if header:
        header[0].click()
        return
    raise RuntimeError("No se pudo abrir el detalle del dia desde /inicio.")


def _open_lecturas_del_dia(wait: WebDriverWait) -> None:
    _click_by_text(wait, "Lecturas del día")


def _extract_lecturas(driver: webdriver.Chrome) -> tuple[str, dict[str, str]]:
    # Extraemos:
    # - header: barra superior verde con fecha/tiempo/color
    # - secciones: Primera lectura, Salmo, Segunda lectura, Aclamacion, Evangelio
    script = r"""
      const header =
        document.querySelector('ion-title h2')?.innerText?.trim()
        || document.querySelector('ion-toolbar h2')?.innerText?.trim()
        || document.querySelector('h2')?.innerText?.trim()
        || '';

      const root = document.querySelector('ion-content') || document.body;
      const headings = Array.from(root.querySelectorAll('h2'));
      const wanted = new Set(['Primera lectura','Salmo','Segunda lectura','Aclamación','Evangelio']);

      function collectTextFrom(node) {
        const parts = [];
        const walker = document.createTreeWalker(node, NodeFilter.SHOW_TEXT, null);
        let t;
        while ((t = walker.nextNode())) {
          const s = (t.nodeValue || '').replace(/\s+/g,' ').trim();
          if (s) parts.push(s);
        }
        return parts.join('\n');
      }

      const sections = {};
      for (let i = 0; i < headings.length; i++) {
        const h = headings[i];
        const title = (h.innerText || '').trim();
        if (!wanted.has(title)) continue;

        // Contenedor: desde el heading hasta antes del siguiente heading wanted o el final.
        const start = h.parentElement || h;
        const nodes = [];
        let cur = h;
        while (cur) {
          cur = cur.nextElementSibling;
          if (!cur) break;
          const maybeH2 = cur.querySelector?.('h2');
          if (cur.tagName === 'H2') break;
          if (maybeH2 && wanted.has((maybeH2.innerText||'').trim())) break;
          nodes.push(cur);
        }
        const block = nodes.map(n => n.innerText || '').join('\n').replace(/\n{3,}/g,'\n\n').trim();
        sections[title] = block;
      }

      return [header, sections];
    """
    header, sections = driver.execute_script(script)
    if not isinstance(header, str):
        header = ""
    if not isinstance(sections, dict):
        sections = {}
    # Limpieza: strings vacios fuera
    cleaned = {k: (v or "").strip() for k, v in sections.items() if (v or "").strip()}
    return header.strip(), cleaned


def fetch_reading_days(start_iso: str, days_ahead: int, headless: bool = True) -> list[ReadingDay]:
    start = _parse_iso(start_iso)
    out: list[ReadingDay] = []

    # Limitacion operativa confirmada por el equipo:
    # En la UI del Ordo las flechas suelen permitir navegar solo ~3 dias adelante/atras desde "hoy".
    # Para evitar ejecuciones "a medias", validamos el rango aqui.
    max_delta = int(os.getenv("ORDO_MAX_DELTA_DAYS", "3"))
    if days_ahead > max_delta:
        raise RuntimeError(
            f"El Ordo (UI) parece limitar la navegacion por flechas a +/- {max_delta} dias. "
            f"days_ahead={days_ahead} excede el limite. "
            f"Usa --days-ahead {max_delta} o ajusta la estrategia de extraccion."
        )

    driver = _new_driver(headless=headless)
    driver.set_page_load_timeout(int(os.getenv("ORDO_PAGE_LOAD_TIMEOUT", "90")))
    wait = WebDriverWait(driver, int(os.getenv("ORDO_TIMEOUT", "30")))

    try:
        driver.get(INICIO_URL)
        # Esperar a que cargue algo representativo.
        wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(normalize-space(),'Inicio')]")))

        today = datetime.now().date()
        # Navegamos a start date desde "hoy" usando flechas.
        delta = (start - today).days
        if abs(delta) > max_delta:
            raise RuntimeError(
                f"El Ordo (UI) parece limitar la navegacion por flechas a +/- {max_delta} dias desde hoy. "
                f"start_date={start_iso} delta={delta} esta fuera del rango."
            )
        _goto_day_by_arrows(driver, wait, delta)

        for i in range(days_ahead + 1):
            current = (start + timedelta(days=i)).isoformat()
            _open_day_detail(driver, wait)
            _open_lecturas_del_dia(wait)

            # Esperar header en lectura
            try:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ion-content")))
            except TimeoutException:
                pass

            header, sections = _extract_lecturas(driver)
            out.append(ReadingDay(iso_date=current, header=header, sections=sections))

            # Volver a inicio para continuar con el siguiente dia.
            # El app suele tener un boton de volver (flecha) en la barra superior.
            back = driver.find_elements(By.CSS_SELECTOR, "ion-button, button")
            clicked = False
            for b in back[:25]:
                try:
                    if not b.is_displayed() or not b.is_enabled():
                        continue
                    label = (b.text or "").strip().lower()
                    icon = (b.get_attribute("name") or "").lower()
                    if "volver" in label or "back" in label or "arrow-back" in icon:
                        b.click()
                        clicked = True
                        break
                except WebDriverException:
                    continue
            if not clicked:
                driver.get(INICIO_URL)
            # Avanzar un dia en inicio si falta
            if i < days_ahead:
                _goto_day_by_arrows(driver, wait, 1)
    finally:
        driver.quit()
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Extrae lecturas del dia desde Ordo (UI) usando Selenium.")
    parser.add_argument("--start-date", default=None, help="YYYY-MM-DD (default: hoy)")
    parser.add_argument("--days-ahead", type=int, default=15, help="Ventana futura (incluye start_date)")
    parser.add_argument("--headed", action="store_true", help="Mostrar navegador (no headless)")
    parser.add_argument("--out", default=None, help="Ruta de salida JSON (opcional; default stdout)")
    args = parser.parse_args()

    start_iso = args.start_date or _today_bogota_iso()
    days_ahead = max(0, int(args.days_ahead))

    data = fetch_reading_days(start_iso, days_ahead, headless=not args.headed)
    payload = {
        "source": "ordo-ui",
        "start_date": start_iso,
        "days_ahead": days_ahead,
        "items": [
            {"date": d.iso_date, "header": d.header, "sections": d.sections} for d in data
        ],
    }

    encoded = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(encoded)
            f.write("\n")
    else:
        sys.stdout.write(encoded + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
