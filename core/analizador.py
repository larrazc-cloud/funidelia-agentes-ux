"""
analizador.py
Envía código y capturas a Claude para análisis UX.
Si no hay API key, genera informe con capturas para análisis manual (Claude Code).
"""

import os
import json
from pathlib import Path

from core.funidelia_skill import FUNIDELIA_SKILL, CRITERIOS_UNIVERSALES_UX, CRITERIOS_GENERALES

API_KEY = os.environ.get("ANTHROPIC_API_KEY")
MODELO = "claude-opus-4-5"

SYSTEM_PROMPT = """
Eres PACO, un agente especializado en UX y diseño de interfaces.
Tu único trabajo es detectar problemas de usabilidad, diseño visual y experiencia
de usuario en apps Streamlit.

NUNCA opinas sobre lógica de negocio, código de backend, ni estructura de datos.
Solo te centras en lo que el usuario ve y experimenta.

Respondes SIEMPRE en JSON válido con esta estructura exacta:
{
  "problemas": [
    {
      "severidad": "alta|media|baja",
      "categoria": "graficos|decimales|redundancia|diseño_corporativo|elementos_tecnicos|jerarquia|leyendas|cursores|buscadores|otro",
      "descripcion": "Descripción clara del problema en español",
      "ubicacion": "Dónde está el problema",
      "sugerencia": "Cómo corregirlo de forma concreta"
    }
  ],
  "resumen": "Una frase resumiendo el estado general de la UX"
}
"""


def tiene_api_key() -> bool:
    return bool(API_KEY)


def _get_cliente():
    if not API_KEY:
        return None
    import anthropic
    return anthropic.Anthropic(api_key=API_KEY)


def analizar_codigo(ruta_proyecto: str, es_corporativa: bool, decisiones_previas: list[str] = None) -> dict:
    codigo_total = ""
    ruta = Path(ruta_proyecto)

    for fichero in sorted(ruta.rglob("*.py")):
        if any(x in str(fichero) for x in [".venv", "__pycache__", "agente", "documentar", "revisar"]):
            continue
        contenido = fichero.read_text(encoding="utf-8", errors="ignore")
        codigo_total += f"\n\n### {fichero.relative_to(ruta)}\n{contenido[:3000]}"

    if not codigo_total:
        return {"problemas": [], "resumen": "No se encontró código Python analizable."}

    cliente = _get_cliente()
    if not cliente:
        # Modo sin API: generar informe preparado para Claude Code
        return _analizar_codigo_local(ruta_proyecto, codigo_total, es_corporativa)

    # Prioridad: Funidelia skill > criterios universales > criterios generales
    criterios = "## CAPA BASE — Criterios generales\n" + CRITERIOS_GENERALES
    if CRITERIOS_UNIVERSALES_UX:
        criterios += "\n\n## CAPA INTERMEDIA — Criterios universales UX (Nielsen, WCAG, dashboards)\n" + CRITERIOS_UNIVERSALES_UX
    if es_corporativa and FUNIDELIA_SKILL:
        criterios += "\n\n## CAPA PRIORITARIA — Skill corporativa Funidelia (prevalece sobre las anteriores)\n" + FUNIDELIA_SKILL

    exclusiones = ""
    if decisiones_previas:
        exclusiones = "\n\nEXCLUSIONES — NO reportes problemas relacionados con:\n"
        exclusiones += "\n".join(f"- {d}" for d in decisiones_previas)

    prompt = f"""
Analiza este código Streamlit y detecta TODOS los problemas de UX.

Las reglas están organizadas por prioridad. Si hay conflicto entre capas,
la capa prioritaria prevalece sobre las inferiores.

CRITERIOS:
{criterios}
{exclusiones}

CÓDIGO:
{codigo_total[:8000]}

Responde SOLO con el JSON. Sin backticks.
"""

    try:
        respuesta = cliente.messages.create(
            model=MODELO, max_tokens=2000, system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )
        texto = respuesta.content[0].text.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(texto)
    except Exception as e:
        print(f"  ❌ Error en análisis de código: {e}")
        return {"problemas": [], "resumen": f"Error: {e}"}


def _analizar_codigo_local(ruta_proyecto: str, codigo: str, es_corporativa: bool) -> dict:
    """Análisis local sin API — detecta problemas básicos por patrones."""
    problemas = []
    ruta = Path(ruta_proyecto)

    # Leer CSS si existe
    css_files = list(ruta.rglob("*.css"))
    css_content = ""
    for f in css_files:
        if ".venv" not in str(f):
            css_content += f.read_text(encoding="utf-8", errors="ignore")

    codigo_lower = codigo.lower()
    css_lower = css_content.lower()

    # Checks de design system
    if es_corporativa:
        if 'atelia' not in css_lower and 'atelia' not in codigo_lower:
            problemas.append({
                "severidad": "alta", "categoria": "diseño_corporativo",
                "descripcion": "No se detecta la fuente Atelia del design system Funidelia",
                "ubicacion": "CSS/app.py", "sugerencia": "Añadir @font-face para Atelia"
            })
        if 'lexenddeca' not in css_lower and 'lexend' not in codigo_lower:
            problemas.append({
                "severidad": "alta", "categoria": "diseño_corporativo",
                "descripcion": "No se detecta la fuente LexendDeca del design system Funidelia",
                "ubicacion": "CSS/app.py", "sugerencia": "Añadir @font-face para LexendDeca"
            })
        if '#428fec' not in css_lower and '#428FEC' not in css_content:
            problemas.append({
                "severidad": "media", "categoria": "diseño_corporativo",
                "descripcion": "No se detecta el color primario Funidelia (#428FEC)",
                "ubicacion": "CSS", "sugerencia": "Usar --color-blue: #428FEC"
            })

    # Checks de formato
    if ':.4f' in codigo or ':.3f' in codigo:
        problemas.append({
            "severidad": "media", "categoria": "decimales",
            "descripcion": "Ratings con más de 2 decimales detectados",
            "ubicacion": "app.py", "sugerencia": "Usar :.2f para ratings"
        })

    # Check max-width
    if 'max-width' not in css_lower and '1540' not in css_content:
        problemas.append({
            "severidad": "media", "categoria": "jerarquia",
            "descripcion": "No hay max-width definido para el contenedor principal",
            "ubicacion": "CSS", "sugerencia": "Añadir max-width: 1540px al contenedor"
        })

    # Check responsive
    if '@media' not in css_lower:
        problemas.append({
            "severidad": "baja", "categoria": "otro",
            "descripcion": "No se detectan media queries para responsive",
            "ubicacion": "CSS", "sugerencia": "Añadir breakpoints para mobile"
        })

    # Check Altair: labels cortados (labelLimit ausente)
    if 'alt.Y(' in codigo and 'labelLimit' not in codigo:
        problemas.append({
            "severidad": "media", "categoria": "graficos",
            "descripcion": "Ejes Y de gráficos sin labelLimit — labels largos se cortan",
            "ubicacion": "app.py (gráficos Altair)",
            "sugerencia": "Añadir axis=alt.Axis(labelLimit=200) en ejes Y con texto"
        })

    # Check Altair: escalas hardcodeadas que pueden no ajustar
    if 'domain=[0,' in codigo and 'max' in codigo and '+ 10' in codigo:
        problemas.append({
            "severidad": "media", "categoria": "graficos",
            "descripcion": "Escala de eje X con margen fijo (+10) puede crear espacio excesivo",
            "ubicacion": "app.py (gráficos Altair)",
            "sugerencia": "Usar scale sin domain fijo o ajustar margen proporcional"
        })

    # Check: fechas en formato YYYY-MM-DD en tablas (debería ser Mes-Año)
    if "'fecha_pedido'" in codigo_lower or "'fecha'" in codigo_lower:
        if 'month_label' not in codigo and 'mes' not in codigo_lower:
            problemas.append({
                "severidad": "media", "categoria": "otro",
                "descripcion": "Fechas en formato YYYY-MM-DD en tablas — usar Mes-Año para legibilidad",
                "ubicacion": "app.py (dataframes)",
                "sugerencia": "Convertir fechas con month_label() antes de mostrar"
            })

    # Check: problemas sin separador legible (comas sin espacios)
    if "problemas'" in codigo_lower and "join" not in codigo:
        problemas.append({
            "severidad": "baja", "categoria": "otro",
            "descripcion": "Tags de problemas mostrados con comas sin separación visual",
            "ubicacion": "app.py (columna problemas en tablas)",
            "sugerencia": "Formatear con ' · '.join() o similar antes de mostrar"
        })

    # Check: columnas de dataframe sin width explícito
    if 'st.dataframe' in codigo and "width=" not in codigo:
        problemas.append({
            "severidad": "baja", "categoria": "otro",
            "descripcion": "Columnas de dataframe sin ancho explícito — pueden no ajustar bien",
            "ubicacion": "app.py (column_config)",
            "sugerencia": "Añadir width='small'/'medium'/'large' en column_config"
        })

    # Check: selection_mode en dataframe (no intuitivo para navegación)
    if 'selection_mode' in codigo:
        problemas.append({
            "severidad": "alta", "categoria": "cursores",
            "descripcion": "Checkbox de selección en dataframe no es intuitivo para navegar a detalle",
            "ubicacion": "app.py (st.dataframe con selection_mode)",
            "sugerencia": "Usar botones 'Ver' explícitos por fila o selector con autocompletado"
        })

    # Check: demasiadas columnas en dataframe (más de 6 causan scroll horizontal)
    import re
    cols_matches = re.findall(r"st\.dataframe\([^)]*\[([^\]]+)\]", codigo)
    for match in cols_matches:
        n_cols = match.count("'")
        if n_cols > 12:  # 6 columnas = 12 comillas
            problemas.append({
                "severidad": "media", "categoria": "otro",
                "descripcion": f"Dataframe con muchas columnas ({n_cols // 2}) — puede requerir scroll horizontal",
                "ubicacion": "app.py (st.dataframe)",
                "sugerencia": "Reducir a 5-6 columnas máximo, mover info secundaria a vista detalle"
            })

    # Check: selector/acción de navegación al final de la página
    lines = codigo.split('\n')
    has_dataframe = False
    selector_after_table = False
    for line in lines:
        if 'st.dataframe' in line:
            has_dataframe = True
        if has_dataframe and ('selectbox' in line or 'button' in line) and ('Ver' in line or 'ficha' in line.lower()):
            # Check if it's after divider (suggests it's at bottom)
            selector_after_table = True
    # This is a heuristic - the real check is visual

    return {
        "problemas": problemas,
        "resumen": f"Análisis local (sin API): {len(problemas)} problemas detectados por patrones"
    }


def analizar_capturas(capturas: list[dict], es_corporativa: bool, decisiones_previas: list[str] = None) -> dict:
    if not capturas:
        return {"problemas": [], "resumen": "No hay capturas disponibles."}

    cliente = _get_cliente()
    if not cliente:
        # Modo sin API: guardar capturas para análisis manual
        return _analizar_capturas_local(capturas)

    # Prioridad: Funidelia skill > criterios universales > criterios generales
    criterios = "## CAPA BASE — Criterios generales\n" + CRITERIOS_GENERALES
    if CRITERIOS_UNIVERSALES_UX:
        criterios += "\n\n## CAPA INTERMEDIA — Criterios universales UX (Nielsen, WCAG, dashboards)\n" + CRITERIOS_UNIVERSALES_UX
    if es_corporativa and FUNIDELIA_SKILL:
        criterios += "\n\n## CAPA PRIORITARIA — Skill corporativa Funidelia (prevalece sobre las anteriores)\n" + FUNIDELIA_SKILL

    exclusiones = ""
    if decisiones_previas:
        exclusiones = "\n\nEXCLUSIONES — NO reportes problemas relacionados con:\n"
        exclusiones += "\n".join(f"- {d}" for d in decisiones_previas)

    contenido = []
    for captura in capturas:
        contenido.append({"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": captura["base64"]}})
        contenido.append({"type": "text", "text": f"Imagen: {captura['descripcion']}"})

    contenido.append({"type": "text", "text": f"""
Analiza estas capturas y detecta problemas de UX visibles.

Las reglas están organizadas por prioridad. Si hay conflicto entre capas,
la capa prioritaria prevalece sobre las inferiores.

CRITERIOS:
{criterios}
{exclusiones}

Responde SOLO con el JSON. Sin backticks.
"""})

    try:
        respuesta = cliente.messages.create(
            model=MODELO, max_tokens=2000, system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": contenido}]
        )
        texto = respuesta.content[0].text.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(texto)
    except Exception as e:
        print(f"  ❌ Error en análisis visual: {e}")
        return {"problemas": [], "resumen": f"Error: {e}"}


def _analizar_capturas_local(capturas: list[dict]) -> dict:
    """Sin API: las capturas se guardan para revisión manual con Claude Code.
    También hace checks básicos comparando viewports."""
    problemas = []
    rutas = [c['ruta'] for c in capturas]

    # Detectar viewports disponibles
    viewports = set(c.get('viewport', 'unknown') for c in capturas)

    problemas.append({
        "severidad": "media",
        "categoria": "otro",
        "descripcion": f"Capturas en {len(viewports)} resoluciones guardadas para revisión visual",
        "ubicacion": ", ".join(rutas),
        "sugerencia": "Pide a Claude Code: 'Lee las capturas en /tmp/paco_capturas/ y analiza la UX'"
    })

    return {
        "problemas": problemas,
        "resumen": f"Sin API key — {len(capturas)} capturas en {len(viewports)} resoluciones guardadas para Claude Code"
    }


def convertir_axe(resultados_axe: list[dict]) -> dict:
    """Convierte violaciones de axe-core al formato de problemas de PACO."""
    if not resultados_axe:
        return {"problemas": [], "resumen": ""}

    SEVERIDAD_MAP = {
        "critical": "alta",
        "serious": "media",
        "moderate": "baja",
        "minor": "baja",
    }

    problemas = []
    for v in resultados_axe:
        problemas.append({
            "severidad": SEVERIDAD_MAP.get(v.get("impact", "minor"), "baja"),
            "categoria": "accesibilidad",
            "descripcion": v.get("help", v.get("descripcion", "")),
            "ubicacion": f"{v.get('pagina', '—')} ({v.get('nodos', 0)} elemento(s))",
            "sugerencia": v.get("helpUrl", ""),
            "fuente": "axe-core",
        })

    return {
        "problemas": problemas,
        "resumen": f"axe-core: {len(problemas)} violaciones de accesibilidad",
    }


def fusionar_resultados(resultado_codigo: dict, resultado_visual: dict, resultado_axe: dict = None) -> dict:
    todos_claude = resultado_codigo.get("problemas", []) + resultado_visual.get("problemas", [])
    # Marcar los de Claude con fuente
    for p in todos_claude:
        if "fuente" not in p:
            p["fuente"] = "claude"

    todos_axe = (resultado_axe or {}).get("problemas", [])
    todos = todos_claude + todos_axe

    orden = {"alta": 0, "media": 1, "baja": 2}
    todos.sort(key=lambda x: orden.get(x.get("severidad", "baja"), 2))
    return {
        "problemas": todos,
        "total": len(todos),
        "altos": len([p for p in todos if p.get("severidad") == "alta"]),
        "medios": len([p for p in todos if p.get("severidad") == "media"]),
        "bajos": len([p for p in todos if p.get("severidad") == "baja"]),
        "de_claude": len(todos_claude),
        "de_axe": len(todos_axe),
        "resumen_codigo": resultado_codigo.get("resumen", ""),
        "resumen_visual": resultado_visual.get("resumen", ""),
        "resumen_axe": (resultado_axe or {}).get("resumen", ""),
        "modo": "api" if tiene_api_key() else "local",
    }
