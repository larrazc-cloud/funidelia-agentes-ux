"""
reporter.py
Muestra el informe en terminal y guarda en docs/ux_report.md
"""

from pathlib import Path
from datetime import datetime

ICONOS_SEVERIDAD = {"alta": "🔴", "media": "🟡", "baja": "🟢"}
ICONOS_CATEGORIA = {
    "graficos": "📊", "decimales": "🔢", "redundancia": "♻️",
    "diseño_corporativo": "🎨", "elementos_tecnicos": "⚙️",
    "jerarquia": "📐", "leyendas": "💬", "cursores": "🖱️",
    "buscadores": "🔍", "accesibilidad": "♿", "otro": "📌"
}
ICONOS_FUENTE = {"claude": "🤖", "axe-core": "♿", "local": "🔧"}


def mostrar_en_terminal(resultado: dict, nombre_proyecto: str, es_corporativa: bool):
    print(f"\n{'='*60}")
    print(f"  🎨 PACO — Informe UX: {nombre_proyecto}")
    if es_corporativa:
        print(f"  🏢 Revisión corporativa Funidelia activada")
    print(f"  📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}")
    print(f"\n  Total: {resultado.get('total', 0)} problemas")
    print(f"  🔴 Alta:  {resultado.get('altos', 0)}")
    print(f"  🟡 Media: {resultado.get('medios', 0)}")
    print(f"  🟢 Baja:  {resultado.get('bajos', 0)}")
    if resultado.get("de_axe", 0):
        print(f"\n  🤖 Claude: {resultado.get('de_claude', 0)}  |  ♿ axe-core: {resultado.get('de_axe', 0)}")

    if not resultado.get("problemas"):
        print(f"\n  ✅ Sin problemas detectados.")
        return

    print(f"\n{'─'*60}")
    for i, p in enumerate(resultado["problemas"], 1):
        sev = p.get("severidad", "baja")
        cat = p.get("categoria", "otro")
        fuente = p.get("fuente", "claude")
        icono_fuente = ICONOS_FUENTE.get(fuente, "")
        print(f"\n  {ICONOS_SEVERIDAD.get(sev,'⚪')} #{i} [{sev.upper()}] {ICONOS_CATEGORIA.get(cat,'📌')} {cat.upper()} {icono_fuente} {fuente}")
        print(f"  📍 {p.get('ubicacion', '—')}")
        print(f"  ❗ {p.get('descripcion', '')}")
        print(f"  💡 {p.get('sugerencia', '')}")

    print(f"\n{'─'*60}")
    if resultado.get("resumen_codigo"):
        print(f"  Código:  {resultado['resumen_codigo']}")
    if resultado.get("resumen_visual"):
        print(f"  Visual:  {resultado['resumen_visual']}")
    if resultado.get("resumen_axe"):
        print(f"  axe-core: {resultado['resumen_axe']}")
    print(f"{'='*60}")

    # Si no hay API key, imprimir instrucciones para Claude Code
    if resultado.get("modo") == "local" and resultado.get("capturas_pendientes"):
        print(f"\n  CLAUDE_CODE_ANALISIS_VISUAL_PENDIENTE")
        print(f"  CAPTURAS_PARA_ANALIZAR:")
        for ruta in resultado["capturas_pendientes"]:
            print(f"    {ruta}")
        print(f"  ES_CORPORATIVA: {es_corporativa}")
        print(f"  CRITERIOS: Skill UX Funidelia + Criterios universales UX")
        print(f"  INSTRUCCION: Lee cada captura con Read, analiza problemas de UX")
        print(f"  visibles (overflow, texto cortado, colores incorrectos, layout")
        print(f"  roto, elementos solapados) y reporta en el mismo formato de PACO.")
    print()


def guardar_md(resultado: dict, ruta_proyecto: str, nombre_proyecto: str, es_corporativa: bool):
    ruta_docs = Path(ruta_proyecto) / "docs"
    ruta_docs.mkdir(exist_ok=True)
    ruta_report = ruta_docs / "ux_report.md"

    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
    total = resultado.get("total", 0)
    altos = resultado.get("altos", 0)
    medios = resultado.get("medios", 0)
    bajos = resultado.get("bajos", 0)

    de_claude = resultado.get("de_claude", 0)
    de_axe = resultado.get("de_axe", 0)

    lineas = [
        f"# Informe UX (PACO) — {nombre_proyecto}", "",
        f"**Última revisión:** {fecha}  ",
        f"**Revisión corporativa Funidelia:** {'Sí' if es_corporativa else 'No'}  ", "",
        "## Resumen", "",
        "| Severidad | Cantidad |", "|-----------|----------|",
        f"| 🔴 Alta   | {altos}  |",
        f"| 🟡 Media  | {medios} |",
        f"| 🟢 Baja   | {bajos}  |",
        f"| **Total** | **{total}** |", "",
    ]

    if de_axe:
        lineas += [
            "| Fuente | Cantidad |", "|--------|----------|",
            f"| 🤖 Claude | {de_claude} |",
            f"| ♿ axe-core | {de_axe} |", "",
        ]

    if resultado.get("problemas"):
        lineas += ["## Problemas detectados", ""]
        for i, p in enumerate(resultado["problemas"], 1):
            sev = p.get("severidad", "baja")
            fuente = p.get("fuente", "claude")
            icono_fuente = ICONOS_FUENTE.get(fuente, "")
            lineas += [
                f"### {ICONOS_SEVERIDAD.get(sev,'⚪')} #{i} — {p.get('descripcion', '')}",
                f"- **Severidad:** {sev}",
                f"- **Categoría:** {p.get('categoria', '—')}",
                f"- **Ubicación:** {p.get('ubicacion', '—')}",
                f"- **Sugerencia:** {p.get('sugerencia', '—')}",
                f"- **Fuente:** {icono_fuente} {fuente}", "",
            ]

    lineas += ["## Decisiones tomadas", "",
               "<!-- Añade aquí las decisiones tras revisar la app: -->",
               "<!-- - Descripción del problema → CORREGIDO el YYYY-MM-DD -->",
               "<!-- - Descripción del problema → IGNORAR, motivo -->", ""]

    historial = ""
    if ruta_report.exists():
        contenido_existente = ruta_report.read_text(encoding="utf-8")
        if "## Decisiones tomadas" in contenido_existente:
            seccion = contenido_existente.split("## Decisiones tomadas")[1].split("## Historial")[0]
            if seccion.strip():
                lineas += [seccion.strip(), ""]
        if "## Historial" in contenido_existente:
            historial = contenido_existente[contenido_existente.index("## Historial"):]

    lineas += ["## Historial", "", f"- **{fecha}** — {total} problemas ({altos} altos, {medios} medios, {bajos} bajos)"]
    if historial:
        for linea in historial.split("\n")[3:]:
            if linea.strip():
                lineas.append(linea)

    ruta_report.write_text("\n".join(lineas), encoding="utf-8")
    print(f"  💾 Informe guardado en: docs/ux_report.md")
