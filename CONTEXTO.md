# PACO — Agente Revisor UX

## Qué es
Agente que revisa la experiencia de usuario de apps Streamlit. Analiza código fuente, captura pantallas con Playwright, ejecuta axe-core para accesibilidad, y detecta problemas visuales y de usabilidad.

## Cómo se ejecuta
- **Bajo demanda**: el usuario dice "que PACO revise esto" en cualquier conversación de Claude Code.
- **Directamente**: `python3 revisar_ux.py <ruta-proyecto> [--solo-codigo] [--solo-visual] [--responsive]`

## Cómo funciona el análisis
1. **Código** — analiza .py/.css buscando patrones de problemas UX
2. **Capturas** — Playwright captura la app en localhost (desktop por defecto, `--responsive` para 3 resoluciones)
3. **axe-core** — se inyecta en cada página para detectar problemas de accesibilidad (WCAG)
4. **Análisis visual** — si hay API key de Anthropic, usa Claude API. Si no, Claude Code lee las capturas directamente con su visión

## Tres capas de criterios (por prioridad)
1. **Skill UX Funidelia** (máxima) — lee de `~/Desktop/Proyectos de Claude/Funidelia/Skills/UX Funidelia.md`. Tipografía, colores, componentes corporativos.
2. **Criterios universales** — heurísticas de Nielsen, WCAG 2.1, buenas prácticas de dashboards. En `PACO_criterios_universales_UX.md`.
3. **Criterios generales** (base) — leyendas, cursores, formato de números, jerarquía visual.

## Configuración por proyecto
Fichero `config_docs.yaml` en la raíz del proyecto:
```yaml
proyecto: Nombre
puerto: 8501
corporativa: true
```
Si no existe, Claude Code lo crea al lanzar PACO.

## Informe
- Terminal: resumen + problemas priorizados con fuente (Claude/axe-core)
- `docs/ux_report.md`: informe persistente con historial y sección de decisiones
- Decisiones marcadas como CORREGIDO/IGNORAR no se repiten en futuras revisiones
- Siempre referencia "Skill UX Funidelia" en problemas de diseño corporativo

## Repo
larrazc-cloud/funidelia-agentes-ux

## Stack
Python 3.14, Playwright, anthropic (opcional), PyYAML. Sin venv propio (usa el de sistema).
