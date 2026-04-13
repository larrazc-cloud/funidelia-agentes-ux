# PACO — Agente Revisor de UX

## Que es PACO

PACO es un agente que revisa la experiencia de usuario de apps Streamlit. Analiza el codigo fuente y captura pantallas de la app corriendo, detectando problemas de usabilidad, diseno visual y coherencia con el design system de Funidelia.

## Que problema resuelve

Cuando haces cambios en la interfaz de una app, es facil romper algo visual o saltarse las guias de diseno. PACO automatiza esa revision: analiza codigo y capturas con Claude API y genera un informe con problemas priorizados y sugerencias concretas.

## Como funciona

1. **Analisis de codigo** — Lee los ficheros .py del proyecto y detecta problemas de UX en el codigo Streamlit (cursores, tooltips, decimales, jerarquia, etc.)
2. **Captura de pantallas** — Usa Playwright para capturar la app corriendo en localhost (vista completa, viewport, pestanas)
3. **Analisis visual** — Envia las capturas a Claude para detectar problemas visuales (colores, tipografia, layout, contraste)
4. **Fusion y priorizacion** — Combina ambos analisis, ordena por severidad (alta/media/baja)
5. **Informe** — Muestra el resultado en terminal y guarda `docs/ux_report.md` con historial

## Dos capas de criterios

### Criterios generales (todos los proyectos)
- Leyendas y tooltips en graficos y metricas
- Cursores correctos (pointer, text, not-allowed)
- Buscadores tolerantes a errores
- Formato de numeros y decimales
- Jerarquia visual y redundancia
- Elementos tecnicos ocultos por defecto

### Skill corporativa Funidelia (proyectos corporativos)
- Tipografia: Atelia para titulos, LexendDeca para todo lo demas
- Colores: azul #428FEC, amarillo #F1FF6D, naranja #FF6A42, rosa #F59BC9
- Header azul con texto amarillo y logo transparente
- Botones con border-radius 12px y hover
- Cards con sombra y hover
- Nunca morado, nunca azul Bootstrap por defecto

La skill se lee desde `~/Desktop/Proyectos de Claude/Funidelia/Skills/UX Funidelia.md`, asi que si se actualiza el design system, PACO usa la version nueva automaticamente.

## Decisiones previas

PACO lee la seccion "Decisiones tomadas" de `docs/ux_report.md`. Si un problema se marco como CORREGIDO o IGNORAR, no lo vuelve a reportar. Esto evita ruido en revisiones sucesivas.

## Como se usa

Desde cualquier conversacion de Claude Code, di:

> "Que PACO revise esto"

Claude Code detectara el proyecto, creara `config_docs.yaml` si no existe, y ejecutara PACO.

Tambien se puede ejecutar directamente:

```bash
python3 ~/Desktop/Proyectos\ de\ Claude/Funidelia/Agentes/agente-ux/revisar_ux.py <ruta-proyecto>
python3 .../revisar_ux.py <ruta> --solo-codigo     # sin capturas
python3 .../revisar_ux.py <ruta> --solo-visual      # sin analisis de codigo
```

## Configuracion por proyecto

Fichero `config_docs.yaml` en la raiz del proyecto:

```yaml
proyecto: Reviews Amazon
puerto: 8501
corporativa: true
```

## Stack tecnico

- **anthropic** — Claude API para analisis de codigo y capturas
- **playwright** — Captura automatica de pantallas con Chromium headless
- **pyyaml** — Configuracion por proyecto

## Informe generado

`docs/ux_report.md` contiene:
- Resumen con conteo por severidad
- Detalle de cada problema: severidad, categoria, ubicacion, sugerencia
- Seccion de decisiones (editable manualmente)
- Historial de revisiones anteriores

## Repo

`larrazc-cloud/funidelia-agentes-ux` (GitHub)
