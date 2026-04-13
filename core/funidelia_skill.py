"""
funidelia_skill.py
Skill de diseño corporativo de Funidelia y criterios universales de UX.
Lee ambos desde ficheros externos para mantenerse actualizada.
"""

from pathlib import Path

AGENTE_DIR = Path(__file__).resolve().parent.parent
SKILL_PATH = Path.home() / "Desktop" / "Proyectos de Claude" / "Funidelia" / "Skills" / "UX Funidelia.md"
UNIVERSALES_PATH = AGENTE_DIR / "PACO_criterios_universales_UX.md"


def _cargar_fichero(ruta: Path, nombre: str) -> str:
    if ruta.exists():
        return ruta.read_text(encoding="utf-8")
    print(f"  ⚠️  No se encuentra {nombre} en {ruta}")
    return ""


FUNIDELIA_SKILL = _cargar_fichero(SKILL_PATH, "skill Funidelia")
CRITERIOS_UNIVERSALES_UX = _cargar_fichero(UNIVERSALES_PATH, "criterios universales UX")

# Mantener CRITERIOS_GENERALES como alias por compatibilidad
CRITERIOS_GENERALES = CRITERIOS_UNIVERSALES_UX
