import os
import ssl
import re
import time
import certifi
import feedparser
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
from urllib.parse import parse_qs, urlparse, urljoin
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 1. Cargar credenciales y URLs desde variables de entorno
USERNAME = os.getenv("DIOCESIS_USERNAME")
PASSWORD = os.getenv("DIOCESIS_PASSWORD")
LOGIN_URL = "https://admin.diocesisdeneiva.org/auth/login?callbackUrl=%2Fdashboard"
DIOS_HOY_URL = "https://admin.diocesisdeneiva.org/espiritualidad/dios-hoy"
YOUTUBE_FEED = "https://www.youtube.com/feeds/videos.xml?channel_id=UCydLv78Ybqcg2y74FR2VYIw"
DEFAULT_TIMEOUT = int(os.getenv("DIOCESIS_TIMEOUT", "15"))
PAGE_LOAD_TIMEOUT = int(os.getenv("DIOCESIS_PAGE_LOAD_TIMEOUT", "90"))
GET_RETRIES = int(os.getenv("DIOCESIS_GET_RETRIES", "2"))
GET_RETRY_WAIT = float(os.getenv("DIOCESIS_GET_RETRY_WAIT", "3"))
LOGIN_TIMEOUT = int(os.getenv("DIOCESIS_LOGIN_TIMEOUT", "45"))
EVANGELIO_TIMEOUT = int(os.getenv("DIOCESIS_EVANGELIO_TIMEOUT", "45"))
EVANGELIO_RETRIES = int(os.getenv("DIOCESIS_EVANGELIO_RETRIES", "1"))
EVANGELIO_DIRECT_URL = os.getenv(
    "DIOCESIS_EVANGELIO_URL",
    "https://admin.diocesisdeneiva.org/espiritualidad/evangelios",
)
VIDEO_URL_SELECTOR = os.getenv(
    "DIOCESIS_VIDEO_URL_SELECTOR",
    "input[type='url'], input[placeholder*='Embed']",
)
VIDEO_BUTTON_INDEX = os.getenv("DIOCESIS_VIDEO_BUTTON_INDEX")
VIDEO_WIDTH = int(os.getenv("DIOCESIS_VIDEO_WIDTH", "840"))
VIDEO_HEIGHT = int(os.getenv("DIOCESIS_VIDEO_HEIGHT", "472"))
LOG_DIR = os.getenv("DIOCESIS_LOG_DIR", "/Users/gabops/Downloads/Diocesis/logs")
LOG_LEVEL = os.getenv("DIOCESIS_LOG_LEVEL", "INFO").upper()

def get_latest_video_url():
    """Devuelve la URL del vídeo más reciente del feed."""
    ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())
    feed = feedparser.parse(YOUTUBE_FEED)
    if feed.bozo:
        raise RuntimeError(f"Error al leer el feed de YouTube: {feed.bozo_exception}")
    if not feed.entries:
        raise RuntimeError("El feed de YouTube no tiene entradas.")
    latest_entry = feed.entries[0]
    if not getattr(latest_entry, "link", None):
        raise RuntimeError("La entrada mas reciente no tiene enlace.")
    return latest_entry.link  # esto devuelve https://www.youtube.com/watch?v=VIDEO_ID

def extract_video_id(url):
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if host.endswith("youtu.be"):
        return parsed.path.lstrip("/")
    if "youtube.com" in host:
        params = parse_qs(parsed.query)
        if "v" in params:
            return params["v"][0]
    return None

def require_env():
    missing = []
    if not USERNAME:
        missing.append("DIOCESIS_USERNAME")
    if not PASSWORD:
        missing.append("DIOCESIS_PASSWORD")
    if missing:
        raise RuntimeError(f"Faltan variables de entorno: {', '.join(missing)}")

def setup_logger():
    os.makedirs(LOG_DIR, exist_ok=True)
    logger = logging.getLogger("diocesis")
    logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
    if not logger.handlers:
        log_path = os.path.join(LOG_DIR, "diocesis.log")
        handler = TimedRotatingFileHandler(
            log_path,
            when="midnight",
            interval=1,
            backupCount=30,
            encoding="utf-8",
        )
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s [%(name)s] %(message)s"
        )
        handler.setFormatter(formatter)
        secrets = [USERNAME, PASSWORD]
        handler.addFilter(RedactFilter(secrets))
        logger.addHandler(handler)
    return logger

class RedactFilter(logging.Filter):
    def __init__(self, secrets):
        super().__init__()
        self.secrets = [secret for secret in secrets if secret]

    def filter(self, record):
        if not self.secrets:
            return True
        message = record.getMessage()
        for secret in self.secrets:
            message = message.replace(secret, "***")
        record.msg = message
        record.args = ()
        return True

def log_phase(logger, message):
    logger.info("fase=%s", message)

def dump_debug_artifacts(driver, logger, label):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    safe_label = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in label)
    base = os.path.join(LOG_DIR, f"debug-{safe_label}-{timestamp}")
    try:
        driver.save_screenshot(f"{base}.png")
    except WebDriverException as exc:
        logger.warning("no_se_pudo_guardar_screenshot error=%s", exc)
    try:
        with open(f"{base}.html", "w", encoding="utf-8") as handle:
            handle.write(driver.page_source or "")
    except OSError as exc:
        logger.warning("no_se_pudo_guardar_html error=%s", exc)

def safe_get(driver, url, logger, label=None):
    max_attempts = max(1, GET_RETRIES + 1)
    for attempt in range(1, max_attempts + 1):
        try:
            logger.info("navegar url=%s intento=%s", label or url, attempt)
            driver.get(url)
            return
        except (TimeoutException, WebDriverException) as exc:
            if attempt >= max_attempts:
                raise
            try:
                driver.execute_script("window.stop();")
            except WebDriverException:
                pass
            time.sleep(GET_RETRY_WAIT)

def safe_click(driver, element):
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    try:
        element.click()
    except WebDriverException:
        driver.execute_script("arguments[0].click();", element)

def do_login(driver, wait, logger):
    safe_get(driver, LOGIN_URL, logger, "login")
    wait.until(EC.visibility_of_element_located((By.ID, "email"))).send_keys(USERNAME)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    login_wait = WebDriverWait(driver, LOGIN_TIMEOUT)
    try:
        login_wait.until(
            EC.any_of(
                EC.url_contains("/dashboard"),
                EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/espiritualidad']")),
            )
        )
    except TimeoutException as exc:
        current_url = driver.current_url
        page_lower = (driver.page_source or "").lower()
        if "captcha" in page_lower or "recaptcha" in page_lower:
            logger.warning("posible_captcha_detectado url=%s", current_url)
        dump_debug_artifacts(driver, logger, "login_timeout")
        raise RuntimeError(f"No se pudo iniciar sesion en el panel. url={current_url}") from exc

def find_day_button(driver, wait, day):
    buttons = wait.until(
        EC.presence_of_all_elements_located((By.XPATH, f"//button[normalize-space()='{day}']"))
    )
    for button in buttons:
        if button.is_displayed() and button.is_enabled():
            return button
    raise RuntimeError(f"No se encontro el boton del dia {day}.")

def infer_evangelio_url(driver):
    source = driver.page_source or ""
    match = re.search(r"href=[\"']([^\"']*evangelios-y-santo[^\"']*)[\"']", source)
    if not match:
        return None
    return match.group(1)

def find_evangelio_link(driver):
    wait = WebDriverWait(driver, EVANGELIO_TIMEOUT)
    selectors = [
        (By.CSS_SELECTOR, "a[href*='/espiritualidad/evangelios']"),
        (By.XPATH, "//a[contains(@href,'/espiritualidad/evangelios')]"),
        (By.XPATH, "//*[self::a or self::button][normalize-space()='Evangelios']"),
        (By.XPATH, "//*[normalize-space()='Evangelios']/ancestor::a[1]"),
    ]
    last_error = None
    for by, selector in selectors:
        try:
            return wait.until(EC.presence_of_element_located((by, selector)))
        except TimeoutException as exc:
            last_error = exc
    raise last_error if last_error else TimeoutException("No se encontro el enlace de evangelio.")

def wait_for_evangelio_section(driver):
    wait = WebDriverWait(driver, EVANGELIO_TIMEOUT)
    return wait.until(
        EC.any_of(
            EC.presence_of_element_located((By.XPATH, "//*[normalize-space()='Evangelios actuales']")),
            EC.presence_of_element_located((By.XPATH, "//*[normalize-space()='Evangelios disponibles']")),
        )
    )

def find_editor_root(editor):
    try:
        return editor.find_element(
            By.XPATH, "ancestor::*[.//button[@type='button'] or .//span[@role='button']][1]"
        )
    except NoSuchElementException:
        return editor

def find_visible_by_css(driver, selector):
    for element in driver.find_elements(By.CSS_SELECTOR, selector):
        if element.is_displayed():
            return element
    return None

def open_video_dialog(driver, wait, editor):
    url_input = find_visible_by_css(driver, VIDEO_URL_SELECTOR)
    if url_input:
        return url_input

    root = find_editor_root(editor)
    video_button = find_visible_by_css(root, ".ql-video")
    if video_button:
        safe_click(driver, video_button)
        return wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, VIDEO_URL_SELECTOR)))
    buttons = root.find_elements(By.CSS_SELECTOR, "button[type='button'], span[role='button']")
    candidates = []
    for button in buttons:
        if not button.is_displayed() or not button.is_enabled():
            continue
        if button.text.strip():
            continue
        candidates.append(button)

    if VIDEO_BUTTON_INDEX is not None:
        try:
            index = int(VIDEO_BUTTON_INDEX)
        except ValueError as exc:
            raise RuntimeError("DIOCESIS_VIDEO_BUTTON_INDEX debe ser un entero.") from exc
        if index < 0 or index >= len(candidates):
            raise RuntimeError("DIOCESIS_VIDEO_BUTTON_INDEX esta fuera de rango.")
        safe_click(driver, candidates[index])
        return wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, VIDEO_URL_SELECTOR)))

    for button in candidates:
        safe_click(driver, button)
        try:
            return WebDriverWait(driver, 1).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, VIDEO_URL_SELECTOR))
            )
        except TimeoutException:
            try:
                if button.get_attribute("aria-pressed") == "true":
                    safe_click(driver, button)
            except WebDriverException:
                pass
            try:
                driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
            except WebDriverException:
                pass
            continue

    raise RuntimeError("No se pudo abrir el dialogo para insertar video.")

def find_modal_submit(url_input):
    containers = [
        "ancestor::*[@role='dialog'][1]",
        "ancestor::*[@aria-modal='true'][1]",
        "ancestor::*[contains(@class,'modal')][1]",
        "ancestor::form[1]",
    ]
    container = None
    for path in containers:
        try:
            container = url_input.find_element(By.XPATH, path)
            break
        except NoSuchElementException:
            continue
    if container is None:
        raise RuntimeError("No se encontro el contenedor del dialogo de video.")

    for button in container.find_elements(By.CSS_SELECTOR, "button"):
        if not button.is_displayed() or not button.is_enabled():
            continue
        if button.get_attribute("type") == "submit":
            return button
    for button in container.find_elements(By.CSS_SELECTOR, "button"):
        if not button.is_displayed() or not button.is_enabled():
            continue
        label = button.text.strip().lower()
        if label and label not in ("cancelar", "cerrar"):
            return button
    raise RuntimeError("No se encontro un boton para confirmar el video.")

def find_save_button(driver, editor):
    try:
        form = editor.find_element(By.XPATH, "ancestor::form[1]")
        buttons = form.find_elements(By.CSS_SELECTOR, "button")
        for button in buttons:
            if not button.is_displayed() or not button.is_enabled():
                continue
            label = button.text.strip().lower()
            if "guardar" in label or "actualizar" in label or "publicar" in label:
                return button
        for button in buttons:
            if button.get_attribute("type") == "submit":
                return button
    except NoSuchElementException:
        pass

    for label in ("Guardar", "Guardar cambios", "Actualizar", "Publicar"):
        matches = driver.find_elements(By.XPATH, f"//button[normalize-space()='{label}']")
        for button in matches:
            if button.is_displayed() and button.is_enabled():
                return button

    raise RuntimeError("No se encontro el boton de guardado.")

def build_embed_url(video_id, fallback_url):
    if video_id:
        return f"https://www.youtube.com/embed/{video_id}"
    return fallback_url

def place_cursor_after_title(driver, editor):
    script = """
    const editor = arguments[0];
    const marker = "Reflexión del día";
    const blocks = Array.from(editor.querySelectorAll("p, h1, h2, h3, h4, h5, h6, div"));
    let target = null;
    for (const block of blocks) {
      const text = (block.textContent || "").trim();
      if (text.includes(marker)) {
        target = block;
        break;
      }
    }
    if (!target) return false;
    const range = document.createRange();
    range.setStartAfter(target);
    range.collapse(true);
    const sel = window.getSelection();
    sel.removeAllRanges();
    sel.addRange(range);
    editor.focus();
    return true;
    """
    return driver.execute_script(script, editor)

def place_cursor_end(driver, editor):
    script = """
    const editor = arguments[0];
    const range = document.createRange();
    range.selectNodeContents(editor);
    range.collapse(false);
    const sel = window.getSelection();
    sel.removeAllRanges();
    sel.addRange(range);
    editor.focus();
    """
    driver.execute_script(script, editor)

def format_inserted_video(driver, editor, video_id, width, height):
    script = """
    const editor = arguments[0];
    const videoId = arguments[1];
    const width = arguments[2];
    const height = arguments[3];
    const iframes = Array.from(editor.querySelectorAll("iframe.ql-video"));
    const target = iframes.find((node) => {
      const src = node.getAttribute("src") || "";
      return !videoId || src.includes(videoId) || src.includes("youtube.com");
    });
    if (!target) return false;
    target.setAttribute("width", String(width));
    target.setAttribute("height", String(height));
    target.style.width = `${width}px`;
    target.style.height = `${height}px`;
    target.style.maxWidth = "100%";
    target.style.border = "0";
    target.style.display = "block";
    target.style.margin = "0 auto";
    const block = target.closest("p, div");
    if (block) {
      block.classList.add("ql-align-center");
      block.style.textAlign = "center";
      block.style.width = "100%";
    }
    return true;
    """
    return driver.execute_script(script, editor, video_id, width, height)

def normalize_existing_video(driver, editor, video_id, embed_url):
    script = """
    const editor = arguments[0];
    const videoId = arguments[1];
    const embedUrl = arguments[2];
    const isYouTube = (src) => src.includes("youtube.com") || src.includes("youtu.be");
    const iframes = Array.from(editor.querySelectorAll("iframe.ql-video"));
    const matches = [];
    const others = [];
    for (const node of iframes) {
      const src = node.getAttribute("src") || "";
      const match = (videoId && src.includes(videoId)) || (embedUrl && src.includes(embedUrl));
      if (match) {
        matches.push(node);
      } else if (isYouTube(src)) {
        others.push(node);
      }
    }
    if (matches.length) {
      for (const node of matches.slice(1).concat(others)) {
        node.remove();
      }
      return true;
    }
    for (const node of others) {
      node.remove();
    }
    return false;
    """
    return driver.execute_script(script, editor, video_id, embed_url)

def find_current_gospel_button(driver, wait):
    header = wait.until(EC.presence_of_element_located((By.XPATH, "//*[normalize-space()='Evangelios actuales']")))
    container = header.find_element(By.XPATH, "ancestor::*[self::div or self::section][1]")
    buttons = container.find_elements(By.CSS_SELECTOR, "button")
    for button in buttons:
        if button.is_displayed() and button.is_enabled() and button.text.strip():
            return button
    raise RuntimeError("No se encontro un evangelio actual para seleccionar.")

def find_edit_reflection_button(wait):
    label = wait.until(EC.presence_of_element_located((By.XPATH, "//*[normalize-space()='Editar reflexión']")))
    try:
        return label.find_element(By.XPATH, "ancestor::button[1]")
    except NoSuchElementException:
        try:
            return label.find_element(By.XPATH, "ancestor::a[1]")
        except NoSuchElementException:
            return label

def wait_for_edit_enabled(wait, button):
    def is_enabled(_):
        classes = (button.get_attribute("class") or "").lower()
        disabled = button.get_attribute("disabled")
        return disabled is None and "text-gray-400" not in classes
    wait.until(is_enabled)

def main():
    require_env()
    logger = setup_logger()
    logger.info(
        "timezone=%s utc_offset_seconds=%s now_local=%s now_utc=%s",
        time.tzname,
        -time.timezone,
        datetime.now(),
        datetime.utcnow(),
    )
    logger.info("inicio_ejecucion")

    # 2. Obtener el video mas reciente
    log_phase(logger, "obtener_video")
    video_url = get_latest_video_url()
    video_id = extract_video_id(video_url)
    logger.info("video_url=%s", video_url)

    # 3. Lanzar el navegador (asegurate de tener chromedriver instalado y en PATH)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.page_load_strategy = "eager"
    options.add_argument("--window-size=1400,900")
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
    wait = WebDriverWait(driver, DEFAULT_TIMEOUT)

    try:
        # 4. Iniciar sesión en el panel
        log_phase(logger, "login")
        do_login(driver, wait, logger)

        # 5. Navegar a Dios Hoy
        log_phase(logger, "navegar_dios_hoy")
        safe_get(driver, DIOS_HOY_URL, logger, "dios_hoy")

        # 6. Seleccionar la fecha actual
        today = datetime.now().day
        # Esperar hasta que cargue el calendario y hacer clic en el día actual
        log_phase(logger, "seleccionar_dia")
        day_button = find_day_button(driver, wait, today)
        safe_click(driver, day_button)

        # 7. Acceder a "Evangelio y santo"
        log_phase(logger, "abrir_evangelio_santo")
        evangelio_link = None
        for attempt in range(EVANGELIO_RETRIES + 1):
            current_url = driver.current_url or ""
            if "/auth/login" in current_url:
                logger.warning("sesion_expirada url=%s", current_url)
                do_login(driver, wait, logger)
                safe_get(driver, DIOS_HOY_URL, logger, "dios_hoy_relogin")
            target_url = None
            try:
                evangelio_link = find_evangelio_link(driver)
                target_url = evangelio_link.get_attribute("href")
            except TimeoutException:
                inferred = infer_evangelio_url(driver)
                target_url = inferred or EVANGELIO_DIRECT_URL
                if target_url and target_url.startswith("/"):
                    target_url = urljoin(DIOS_HOY_URL, target_url)
                logger.warning("no_se_encontro_enlace_evangelio intento=%s url=%s usando_url_directa=%s", attempt + 1, driver.current_url, target_url)
                dump_debug_artifacts(driver, logger, f"evangelio_link_{attempt + 1}")
            safe_get(driver, target_url, logger, f"evangelio_santo_{attempt + 1}")
            try:
                wait_for_evangelio_section(driver)
                break
            except TimeoutException:
                logger.warning("no_se_confirmo_evangelio intento=%s url=%s", attempt + 1, driver.current_url)
                dump_debug_artifacts(driver, logger, f"evangelio_section_{attempt + 1}")
                if attempt < EVANGELIO_RETRIES:
                    safe_get(driver, DIOS_HOY_URL, logger, f"dios_hoy_reintento_{attempt + 1}")
                else:
                    raise
        if not evangelio_link:
            logger.warning("no_se_pudo_confirmar_enlace_evangelio url=%s", driver.current_url)
        
        # 8. Seleccionar el evangelio actual y habilitar "Editar reflexion"
        log_phase(logger, "seleccionar_evangelio_actual")
        current_evangelio = find_current_gospel_button(driver, wait)
        safe_click(driver, current_evangelio)

        editar_reflexion_button = find_edit_reflection_button(wait)
        wait_for_edit_enabled(wait, editar_reflexion_button)
        safe_click(driver, editar_reflexion_button)

        # 9. Insertar el vídeo en el editor:
        # Esperar a que aparezca el área de edición
        log_phase(logger, "abrir_editor")
        editor = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div[contenteditable='true']")))
        log_phase(logger, "insertar_video")
        embed_url = build_embed_url(video_id, video_url)
        if normalize_existing_video(driver, editor, video_id, embed_url):
            wait.until(lambda d: format_inserted_video(d, editor, video_id, VIDEO_WIDTH, VIDEO_HEIGHT))
        else:
            if not place_cursor_after_title(driver, editor):
                place_cursor_end(driver, editor)

            url_input = open_video_dialog(driver, wait, editor)
            url_input.clear()
            url_input.send_keys(embed_url)
            url_input.send_keys(Keys.ENTER)
            try:
                wait.until(lambda d: not find_visible_by_css(d, VIDEO_URL_SELECTOR))
            except TimeoutException:
                submit_button = find_modal_submit(url_input)
                safe_click(driver, submit_button)
                wait.until(lambda d: not find_visible_by_css(d, VIDEO_URL_SELECTOR))

            wait.until(lambda d: format_inserted_video(d, editor, video_id, VIDEO_WIDTH, VIDEO_HEIGHT))

        # 10. Guardar cambios
        log_phase(logger, "guardar_cambios")
        save_button = find_save_button(driver, editor)
        safe_click(driver, save_button)

        logger.info("fin_ejecucion ok")
        print("Reflexion del dia actualizada con el nuevo video.")
    except Exception:
        logger.exception("fin_ejecucion error")
        raise
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
