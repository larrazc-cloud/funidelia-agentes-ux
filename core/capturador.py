"""
capturador.py
Captura pantallas de la app Streamlit corriendo en local.
"""

import subprocess
import sys
import base64
from pathlib import Path
from datetime import datetime


def instalar_playwright():
    try:
        from playwright.sync_api import sync_playwright
        return True
    except ImportError:
        print("  📦 Instalando playwright...")
        subprocess.run([sys.executable, "-m", "pip", "install", "playwright", "-q"])
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium", "--quiet"])
        return True


def capturar_app(puerto: int, ruta_salida: str = None) -> list[dict]:
    instalar_playwright()
    from playwright.sync_api import sync_playwright

    url_base = f"http://localhost:{puerto}"
    capturas = []

    if not ruta_salida:
        ruta_salida = "/tmp/paco_capturas"

    Path(ruta_salida).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1440, "height": 900})

            try:
                page.goto(url_base, timeout=5000)
                page.wait_for_load_state("networkidle", timeout=8000)
            except Exception:
                print(f"  ⚠️  No se puede conectar a localhost:{puerto}")
                print(f"      ¿Está la app corriendo?")
                browser.close()
                return []

            ruta_full = f"{ruta_salida}/captura_{timestamp}_full.png"
            page.screenshot(path=ruta_full, full_page=True)
            capturas.append({"ruta": ruta_full, "descripcion": "Vista completa", "base64": _imagen_a_base64(ruta_full)})
            print(f"  📸 Captura completa guardada")

            ruta_viewport = f"{ruta_salida}/captura_{timestamp}_viewport.png"
            page.screenshot(path=ruta_viewport, full_page=False)
            capturas.append({"ruta": ruta_viewport, "descripcion": "Vista inicial", "base64": _imagen_a_base64(ruta_viewport)})
            print(f"  📸 Captura viewport guardada")

            tabs = page.query_selector_all("[data-baseweb='tab']")
            if len(tabs) > 1:
                try:
                    tabs[1].click()
                    page.wait_for_load_state("networkidle", timeout=3000)
                    ruta_tab2 = f"{ruta_salida}/captura_{timestamp}_tab2.png"
                    page.screenshot(path=ruta_tab2, full_page=True)
                    capturas.append({"ruta": ruta_tab2, "descripcion": "Segunda pestaña", "base64": _imagen_a_base64(ruta_tab2)})
                    print(f"  📸 Captura segunda pestaña guardada")
                except Exception:
                    pass

            browser.close()

    except Exception as e:
        print(f"  ❌ Error en captura: {e}")

    return capturas


def _imagen_a_base64(ruta: str) -> str:
    with open(ruta, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")
