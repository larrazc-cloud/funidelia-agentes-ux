"""
revisar_ux.py — PACO
Agente de revisión UX. Coloca en la raíz de cada proyecto.

Uso:
    python revisar_ux.py
    python revisar_ux.py --solo-codigo
    python revisar_ux.py --solo-visual
"""

import sys
import yaml
import webbrowser
import time
from pathlib import Path

AGENTE_PATH = "/Users/carlos/Desktop/Proyectos de Claude/Funidelia/Agentes/agente-ux"
sys.path.insert(0, AGENTE_PATH)

from core.capturador import capturar_app
from core.analizador import analizar_codigo, analizar_capturas, convertir_axe, fusionar_resultados
from core.reporter import mostrar_en_terminal, guardar_md


def cargar_config(ruta_proyecto: str) -> dict:
    ruta_config = Path(ruta_proyecto) / "config_docs.yaml"
    if not ruta_config.exists():
        print("⚠️  No encuentro config_docs.yaml.")
        return {}
    with open(ruta_config, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def cargar_decisiones_previas(ruta_proyecto: str) -> list[str]:
    ruta_report = Path(ruta_proyecto) / "docs" / "ux_report.md"
    if not ruta_report.exists():
        return []

    decisiones = []
    contenido = ruta_report.read_text(encoding="utf-8")
    if "## Decisiones tomadas" not in contenido:
        return []

    seccion = contenido.split("## Decisiones tomadas")[1].split("##")[0]
    for linea in seccion.strip().split("\n"):
        linea = linea.strip()
        if linea.startswith("-") and ("CORREGIDO" in linea or "IGNORAR" in linea):
            parte = linea.lstrip("- ").split("→")[0].strip()
            if parte:
                decisiones.append(parte.lower())

    if decisiones:
        print(f"  📋 {len(decisiones)} decisión(es) previa(s) — no se repetirán")
    return decisiones


def main():
    solo_codigo = "--solo-codigo" in sys.argv
    solo_visual = "--solo-visual" in sys.argv
    responsive = "--responsive" in sys.argv

    # Aceptar ruta como argumento o usar directorio actual
    ruta_proyecto = None
    for arg in sys.argv[1:]:
        if not arg.startswith("--"):
            ruta_proyecto = str(Path(arg).resolve())
            break
    if not ruta_proyecto:
        ruta_proyecto = str(Path.cwd().resolve())

    config = cargar_config(ruta_proyecto)

    nombre_proyecto = config.get("proyecto", Path(ruta_proyecto).name)
    puerto = config.get("puerto", 8501)

    from core.analizador import tiene_api_key
    modo = "API Claude" if tiene_api_key() else "Local (capturas para Claude Code)"

    print(f"\n{'='*60}")
    print(f"  🎨 PACO — Revisión UX: {nombre_proyecto}")
    print(f"  Modo: {modo}")
    print(f"{'='*60}")

    es_corporativa = config.get("corporativa", None)
    if es_corporativa is None:
        respuesta = input("\n  ¿Es una app corporativa de Funidelia? (s/n): ").strip().lower()
        es_corporativa = respuesta == "s"

    decisiones_previas = cargar_decisiones_previas(ruta_proyecto)

    resultado_codigo = {"problemas": [], "resumen": ""}
    resultado_visual = {"problemas": [], "resumen": ""}
    resultado_axe = {"problemas": [], "resumen": ""}

    if not solo_visual:
        print(f"\n  🔎 Analizando código...")
        resultado_codigo = analizar_codigo(ruta_proyecto, es_corporativa, decisiones_previas)
        print(f"  ✅ {len(resultado_codigo.get('problemas', []))} problema(s) en código")

    if not solo_codigo:
        print(f"\n  📸 Capturando app en localhost:{puerto}...")
        capturas, resultados_axe_raw = capturar_app(puerto, responsive=responsive)
        if capturas:
            print(f"  🔎 Analizando capturas...")
            resultado_visual = analizar_capturas(capturas, es_corporativa, decisiones_previas)
            print(f"  ✅ {len(resultado_visual.get('problemas', []))} problema(s) visual(es)")
        else:
            print(f"  ⚠️  Sin capturas. Solo análisis de código.")
            resultados_axe_raw = []

        if resultados_axe_raw:
            resultado_axe = convertir_axe(resultados_axe_raw)
            print(f"  ♿ {len(resultado_axe.get('problemas', []))} problema(s) de accesibilidad (axe-core)")

    resultado_final = fusionar_resultados(resultado_codigo, resultado_visual, resultado_axe)
    mostrar_en_terminal(resultado_final, nombre_proyecto, es_corporativa)
    guardar_md(resultado_final, ruta_proyecto, nombre_proyecto, es_corporativa)

    if not solo_codigo:
        print(f"\n  🌐 Abriendo app en localhost:{puerto}...")
        time.sleep(1)
        webbrowser.open(f"http://localhost:{puerto}")

    if not tiene_api_key():
        print(f"\n  📸 Capturas guardadas para análisis visual.")
        print(f"     Dile a Claude Code:")
        print(f"     'Lee las capturas en /tmp/paco_capturas/ y analiza la UX'")
    print(f"\n  📝 Tras revisar, dile a Claude Code:")
    print(f"     'Corrige el #X, ignora el #Y'\n")


if __name__ == "__main__":
    main()
