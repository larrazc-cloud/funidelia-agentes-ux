"""
analizador.py
Envía código y capturas a Claude para análisis UX.
"""

import os
import json
from pathlib import Path
import anthropic

from core.funidelia_skill import FUNIDELIA_SKILL, CRITERIOS_GENERALES

cliente = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
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

    criterios = CRITERIOS_GENERALES
    if es_corporativa:
        criterios += "\n\n" + FUNIDELIA_SKILL

    exclusiones = ""
    if decisiones_previas:
        exclusiones = "\n\nEXCLUSIONES — NO reportes problemas relacionados con:\n"
        exclusiones += "\n".join(f"- {d}" for d in decisiones_previas)

    prompt = f"""
Analiza este código Streamlit y detecta TODOS los problemas de UX.

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


def analizar_capturas(capturas: list[dict], es_corporativa: bool, decisiones_previas: list[str] = None) -> dict:
    if not capturas:
        return {"problemas": [], "resumen": "No hay capturas disponibles."}

    criterios = CRITERIOS_GENERALES
    if es_corporativa:
        criterios += "\n\n" + FUNIDELIA_SKILL

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


def fusionar_resultados(resultado_codigo: dict, resultado_visual: dict) -> dict:
    todos = resultado_codigo.get("problemas", []) + resultado_visual.get("problemas", [])
    orden = {"alta": 0, "media": 1, "baja": 2}
    todos.sort(key=lambda x: orden.get(x.get("severidad", "baja"), 2))
    return {
        "problemas": todos,
        "total": len(todos),
        "altos": len([p for p in todos if p.get("severidad") == "alta"]),
        "medios": len([p for p in todos if p.get("severidad") == "media"]),
        "bajos": len([p for p in todos if p.get("severidad") == "baja"]),
        "resumen_codigo": resultado_codigo.get("resumen", ""),
        "resumen_visual": resultado_visual.get("resumen", ""),
    }
