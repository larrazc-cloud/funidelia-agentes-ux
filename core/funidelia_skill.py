"""
funidelia_skill.py
Skill de diseño corporativo de Funidelia, embebida en PACO.
Lee la skill desde el fichero externo para mantenerse actualizada.
"""

from pathlib import Path

SKILL_PATH = Path.home() / "Desktop" / "Proyectos de Claude" / "Funidelia" / "Skills" / "UX Funidelia.md"


def _cargar_skill() -> str:
    if SKILL_PATH.exists():
        return SKILL_PATH.read_text(encoding="utf-8")
    print(f"  ⚠️  No se encuentra la skill en {SKILL_PATH}")
    print(f"      Usando reglas corporativas por defecto.")
    return ""


FUNIDELIA_SKILL = _cargar_skill()

CRITERIOS_GENERALES = """
# Criterios generales de UX (todos los proyectos)

## Leyendas y contexto
- Si un término, métrica o gráfico puede no ser autoexplicativo, debe tener leyenda o tooltip.
- Las leyendas deben poder abrirse y cerrarse (expander, tooltip, icono ℹ️).
- Gráficos con números que no se explican solos = problema medio.
- Términos técnicos sin explicación visible = problema medio.
- NO poner explicaciones fijas que ocupen espacio permanente — siempre colapsables.

## Cursores del ratón
- Elementos clicables: cursor pointer.
- Elementos de texto seleccionable: cursor text.
- Elementos deshabilitados: cursor not-allowed.
- Si el cursor no cambia al pasar por un elemento interactivo = problema medio.

## Buscadores
- Un buscador que solo filtra por texto exacto = problema medio.
- Deben tolerar errores tipográficos menores.
- Deben buscar en múltiples campos relevantes.
- Deben mostrar cuántos resultados hay tras filtrar.
- Si no hay resultados, mostrar mensaje claro y sugerencia.
- Sin placeholder descriptivo = problema bajo.

## Gráficos
- Altura fija definida. Sin altura fija = posible corte.
- Ejes Y con rango explícito si los valores son pequeños.
- Títulos de ejes presentes y legibles.
- Leyenda visible y no solapada con el gráfico.
- Colores con contraste suficiente.

## Números y decimales
- Máximo 2 decimales en métricas de negocio (precio, margen, %).
- Máximo 0-1 decimales en conteos o unidades enteras.
- Formato de miles con separador.
- Porcentajes siempre con símbolo %.

## Información y redundancia
- Cada elemento en pantalla debe tener utilidad clara.
- Si un dato aparece dos veces sin añadir contexto = redundante.

## Elementos técnicos / de sistema
- Logs, importadores, configuraciones avanzadas, mensajes de debug:
  NUNCA como pestaña principal o elemento visible por defecto.
  Siempre colapsados, en modal, o en sección secundaria.

## Jerarquía visual
- Una sola acción principal por pantalla claramente identificada.
- Acciones secundarias visualmente subordinadas.
- No más de 3 niveles de jerarquía visual en una misma pantalla.

## Pestañas y navegación
- Máximo 5-6 pestañas principales. Más = problema de arquitectura.

## Responsive / legibilidad
- Texto mínimo 14px en contenido, 12px en labels secundarios.
- Contraste suficiente en texto sobre fondos de color.
"""
