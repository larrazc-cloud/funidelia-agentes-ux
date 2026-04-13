"""
capturador.py
Captura pantallas de la app Streamlit corriendo en local.
Captura a múltiples resoluciones para detectar problemas de overflow/responsive.
Ejecuta axe-core en cada página para detectar problemas de accesibilidad.
"""

import subprocess
import sys
import json
import base64
from pathlib import Path
from datetime import datetime

VIEWPORT_DEFAULT = [
    {"width": 1440, "height": 900, "nombre": "desktop"},
]

VIEWPORTS_RESPONSIVE = [
    {"width": 1440, "height": 900, "nombre": "desktop"},
    {"width": 1280, "height": 800, "nombre": "laptop"},
    {"width": 1024, "height": 768, "nombre": "tablet"},
]


def instalar_playwright():
    try:
        from playwright.sync_api import sync_playwright
        return True
    except ImportError:
        print("  📦 Instalando playwright...")
        subprocess.run([sys.executable, "-m", "pip", "install", "playwright", "-q"])
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium", "--quiet"])
        return True


AXE_CDN = "https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.9.1/axe.min.js"


def _ejecutar_axe(page, descripcion: str) -> list[dict]:
    """Inyecta axe-core en la página y ejecuta el análisis de accesibilidad."""
    try:
        # Inyectar axe-core desde CDN
        page.evaluate(f"""
            () => new Promise((resolve, reject) => {{
                if (window.axe) {{ resolve(); return; }}
                const s = document.createElement('script');
                s.src = '{AXE_CDN}';
                s.onload = resolve;
                s.onerror = reject;
                document.head.appendChild(s);
            }})
        """)
        # Ejecutar análisis
        resultados = page.evaluate("() => axe.run().then(r => r.violations)")
        violaciones = []
        for v in resultados:
            violaciones.append({
                "id": v.get("id", ""),
                "impact": v.get("impact", "minor"),
                "descripcion": v.get("description", ""),
                "help": v.get("help", ""),
                "helpUrl": v.get("helpUrl", ""),
                "nodos": len(v.get("nodes", [])),
                "pagina": descripcion,
            })
        if violaciones:
            print(f"  ♿ axe-core: {len(violaciones)} violacion(es) en {descripcion}")
        return violaciones
    except Exception as e:
        print(f"  ⚠️  axe-core no pudo ejecutarse en {descripcion}: {e}")
        return []


def capturar_app(puerto: int, ruta_salida: str = None, responsive: bool = False) -> tuple[list[dict], list[dict]]:
    """Captura pantallas y ejecuta axe-core.

    Por defecto solo desktop. Con responsive=True captura en 3 resoluciones.
    Devuelve (capturas, resultados_axe).
    """
    instalar_playwright()
    from playwright.sync_api import sync_playwright

    url_base = f"http://localhost:{puerto}"
    capturas = []
    resultados_axe = []

    if not ruta_salida:
        ruta_salida = "/tmp/paco_capturas"

    Path(ruta_salida).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()

            viewports = VIEWPORTS_RESPONSIVE if responsive else VIEWPORT_DEFAULT
            for vp in viewports:
                page = browser.new_page(viewport={"width": vp["width"], "height": vp["height"]})

                try:
                    page.goto(url_base, timeout=15000)
                    page.wait_for_load_state("networkidle", timeout=15000)
                    page.wait_for_timeout(2000)  # Streamlit render time
                except Exception:
                    print(f"  ⚠️  No se puede conectar a localhost:{puerto}")
                    print(f"      ¿Está la app corriendo?")
                    page.close()
                    browser.close()
                    return [], []

                # Captura full page
                ruta_full = f"{ruta_salida}/captura_{timestamp}_{vp['nombre']}_full.png"
                page.screenshot(path=ruta_full, full_page=True)
                capturas.append({
                    "ruta": ruta_full,
                    "descripcion": f"Vista completa ({vp['nombre']} {vp['width']}x{vp['height']})",
                    "base64": _imagen_a_base64(ruta_full),
                    "viewport": vp['nombre'],
                })
                print(f"  📸 Captura {vp['nombre']} ({vp['width']}px) guardada")

                # Captura viewport (above the fold)
                ruta_vp = f"{ruta_salida}/captura_{timestamp}_{vp['nombre']}_viewport.png"
                page.screenshot(path=ruta_vp, full_page=False)
                capturas.append({
                    "ruta": ruta_vp,
                    "descripcion": f"Vista inicial ({vp['nombre']} {vp['width']}x{vp['height']})",
                    "base64": _imagen_a_base64(ruta_vp),
                    "viewport": vp['nombre'],
                })

                # Ejecutar axe-core (solo en desktop para evitar duplicados)
                if vp['nombre'] == 'desktop':
                    axe = _ejecutar_axe(page, "Vista principal")
                    resultados_axe.extend(axe)

                # Explorar tabs y vistas internas (solo en desktop)
                if vp['nombre'] == 'desktop':
                    tabs = page.query_selector_all("[data-baseweb='tab']")

                    # Capturar cada tab
                    for tab_idx in range(1, min(len(tabs), 4)):
                        try:
                            tabs[tab_idx].click()
                            page.wait_for_timeout(1500)
                            page.wait_for_load_state("networkidle", timeout=10000)
                            tab_name = tabs[tab_idx].inner_text().strip().lower().replace(' ', '_')
                            ruta_tab = f"{ruta_salida}/captura_{timestamp}_desktop_tab_{tab_name}.png"
                            page.screenshot(path=ruta_tab, full_page=True)
                            capturas.append({
                                "ruta": ruta_tab,
                                "descripcion": f"Tab {tab_name} (desktop)",
                                "base64": _imagen_a_base64(ruta_tab),
                                "viewport": "desktop",
                            })
                            print(f"  📸 Captura tab '{tab_name}' guardada")

                            # axe-core en cada tab
                            axe = _ejecutar_axe(page, f"Tab {tab_name}")
                            resultados_axe.extend(axe)

                            # Si es tab Productos, intentar click en primera fila para capturar ficha
                            if tab_idx == 1:
                                try:
                                    page.wait_for_timeout(1000)
                                    rows = page.query_selector_all("[data-testid='stDataFrame'] tr")
                                    if len(rows) > 1:
                                        rows[1].click()
                                        page.wait_for_timeout(3000)
                                        ruta_ficha = f"{ruta_salida}/captura_{timestamp}_desktop_ficha.png"
                                        page.screenshot(path=ruta_ficha, full_page=True)
                                        capturas.append({
                                            "ruta": ruta_ficha,
                                            "descripcion": "Ficha de producto (desktop)",
                                            "base64": _imagen_a_base64(ruta_ficha),
                                            "viewport": "desktop",
                                        })
                                        print(f"  📸 Captura ficha de producto guardada")
                                except Exception:
                                    pass
                        except Exception:
                            pass

                page.close()

            browser.close()

    except Exception as e:
        print(f"  ❌ Error en captura: {e}")

    # Guardar resultados axe en JSON
    if resultados_axe:
        ruta_axe = f"{ruta_salida}/axe_{timestamp}.json"
        with open(ruta_axe, "w", encoding="utf-8") as f:
            json.dump(resultados_axe, f, ensure_ascii=False, indent=2)
        print(f"  ♿ Resultados axe-core guardados ({len(resultados_axe)} violaciones)")

    return capturas, resultados_axe


def _imagen_a_base64(ruta: str) -> str:
    with open(ruta, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")
