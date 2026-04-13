# PACO — Criterios Universales de UX

Estas reglas se aplican a TODOS los proyectos, independientemente de si tienen skill corporativa.
Si la skill corporativa contradice alguna regla universal, la skill corporativa tiene prioridad.

---

## 1. Heurísticas de Nielsen (Jakob Nielsen, 1994)

Las 10 reglas de usabilidad más universales y reconocidas del mundo. Aplicadas a apps Streamlit:

### H1 — Visibilidad del estado del sistema
El usuario siempre debe saber qué está pasando.
- Si hay una carga o proceso en curso, debe haber un spinner o mensaje de espera
- Si una acción se completó, debe haber confirmación visible
- Si un filtro está activo, debe ser visible en todo momento
- **Problema detectado si:** la app lanza procesos sin feedback visible, o el usuario no sabe si algo está cargando o ha fallado

### H2 — Concordancia con el mundo real
La app habla el idioma del usuario, no de la tecnología.
- Los textos usan términos del negocio, no términos técnicos ni de programación
- Los números se muestran en el formato que el usuario espera (€, %, fechas)
- El orden de la información es lógico y natural
- **Problema detectado si:** aparecen términos como "dataframe", "NaN", "null", "index", "query" en la interfaz visible

### H3 — Control y libertad del usuario
El usuario puede deshacer, cancelar o salir fácilmente.
- Las acciones destructivas (borrar, sobreescribir) piden confirmación
- Hay forma de volver al estado anterior
- Los filtros se pueden resetear con un solo clic
- **Problema detectado si:** hay botones de acción sin confirmación para operaciones irreversibles, o no hay botón de "limpiar filtros"

### H4 — Consistencia y estándares
Lo mismo siempre se ve y funciona igual.
- Los botones del mismo tipo tienen el mismo color y tamaño en toda la app
- Los títulos de sección siguen el mismo estilo
- Los iconos significan siempre lo mismo
- **Problema detectado si:** el mismo tipo de botón tiene estilos distintos en diferentes partes de la app, o los iconos se usan de forma inconsistente

### H5 — Prevención de errores
Mejor evitar el error que tener que corregirlo.
- Los campos de formulario tienen validación antes de enviar
- Los selectores muestran solo opciones válidas
- Las acciones peligrosas están separadas visualmente de las acciones normales
- **Problema detectado si:** hay inputs sin validación, o botones destructivos junto a botones de acción normal sin separación visual

### H6 — Reconocimiento en lugar de memorización
El usuario no debería tener que recordar nada entre pantallas.
- Las opciones disponibles son visibles, no hay que recordarlas
- El contexto actual (qué filtros están activos, en qué paso estás) siempre es visible
- Los tooltips y leyendas están accesibles sin necesidad de ir a otra pantalla
- **Problema detectado si:** el usuario necesita recordar información de una pantalla para usarla en otra, o no hay indicación del estado actual de los filtros

### H7 — Flexibilidad y eficiencia de uso
La app funciona bien tanto para usuarios nuevos como expertos.
- Los filtros más usados están accesibles directamente, los avanzados colapsados
- Hay atajos o accesos directos para las acciones más frecuentes
- Los usuarios expertos pueden llegar al dato que buscan en pocos clics
- **Problema detectado si:** todas las opciones están al mismo nivel de visibilidad sin priorización, o hay demasiados pasos para llegar a la información principal

### H8 — Diseño estético y minimalista
Solo lo necesario. Nada más.
- Cada elemento en pantalla tiene una utilidad clara
- No hay información duplicada sin valor añadido
- No hay decoración que distraiga del contenido
- **Problema detectado si:** hay elementos repetidos sin contexto diferente, secciones vacías, o decoración que no aporta información

### H9 — Ayuda para reconocer y recuperarse de errores
Los errores se explican en lenguaje claro y con solución.
- Los mensajes de error dicen qué pasó y cómo solucionarlo
- Los errores son visibles (no solo en consola)
- No aparecen trazas de código o stack traces al usuario
- **Problema detectado si:** los errores muestran mensajes técnicos, aparecen en consola pero no en la interfaz, o no sugieren cómo resolverlos

### H10 — Ayuda y documentación
Si el usuario necesita ayuda, debe encontrarla fácilmente.
- Las métricas y términos complejos tienen tooltip o leyenda accesible
- Los pasos de procesos complejos están explicados
- La ayuda está contextualizada (cerca del elemento que necesita explicación)
- **Problema detectado si:** hay métricas o términos sin explicación, o la documentación está solo en una pestaña separada sin contexto

---

## 2. Criterios WCAG 2.1 — Accesibilidad visual

Estándar internacional de accesibilidad web. Nivel AA es el objetivo mínimo razonable.

### Contraste de colores
- Texto normal (< 18px o < 14px negrita): ratio mínimo **4.5:1**
- Texto grande (≥ 18px o ≥ 14px negrita): ratio mínimo **3:1**
- Elementos de interfaz (botones, bordes de inputs, iconos significativos): ratio mínimo **3:1**
- Gráficos y visualizaciones de datos: ratio mínimo **3:1** entre elementos
- **Problema detectado si:** texto gris claro sobre fondo blanco, texto amarillo sobre fondo blanco, o texto blanco sobre colores demasiado claros

### Tamaño de texto
- Texto de contenido principal: mínimo **14px** (recomendado 16px)
- Labels y texto secundario: mínimo **12px**
- Nunca usar texto de menos de 11px
- **Problema detectado si:** hay texto que requiere acercar la pantalla para leerlo

### No depender solo del color
- La información nunca se comunica SOLO con color — siempre acompañado de icono, texto o forma
- Un semáforo de colores sin etiquetas es un problema
- **Problema detectado si:** hay indicadores de estado que solo se diferencian por color, sin texto ni icono de apoyo

### Elementos interactivos identificables
- Los botones deben parecer botones (borde, fondo o forma reconocible)
- Los inputs deben tener borde visible
- El foco del teclado debe ser visible (focus ring)
- **Problema detectado si:** botones sin borde ni fondo reconocible, inputs sin borde visible, o no hay indicación visual del elemento seleccionado

---

## 3. Buenas prácticas específicas para dashboards y apps de datos

### Gráficos
- Altura fija definida — sin altura fija el gráfico puede cortarse o colapsar
- Eje Y con rango explícito cuando los valores son pequeños o muy similares
- Título del gráfico descriptivo (no genérico como "Gráfico 1")
- Etiquetas de ejes presentes y legibles
- Leyenda visible y no solapada con el gráfico
- Colores de series con contraste suficiente entre sí
- Para gráficos con muchas series, limitar a 6-7 máximo o usar interactividad para filtrar
- **Problema detectado si:** gráfico sin título, ejes sin etiqueta, leyenda tapando datos, o colores de series prácticamente iguales

### Tablas de datos
- Máximo 7-8 columnas visibles por defecto — las demás colapsadas o bajo demanda
- Las columnas más importantes van a la izquierda
- Números alineados a la derecha, texto a la izquierda
- Cabeceras descriptivas, no nombres de variables (no "marg_m4" sino "Margen M4")
- Filas con hover para facilitar la lectura horizontal
- Paginación si hay más de 50 filas
- **Problema detectado si:** nombres de columna técnicos, números mal alineados, o tabla sin paginación con cientos de filas

### Números y formato
- Máximo 2 decimales en métricas de negocio (precio, margen, ratio)
- Máximo 0-1 decimales en conteos o cantidades enteras
- Separador de miles para números ≥ 1.000
- Porcentajes siempre con símbolo % y sin más de 1 decimal
- Moneda siempre con símbolo (€, $) y formato consistente
- **Problema detectado si:** números con 4+ decimales, miles sin separador, o porcentajes sin símbolo

### Filtros y buscadores
- Filtros globales (mercado, fecha, categoría) en sidebar, no en el cuerpo de la página
- Filtros locales cerca del contenido que afectan
- Botón de "Limpiar filtros" siempre visible cuando hay filtros activos
- Buscadores con placeholder descriptivo ("Buscar por nombre, SKU o categoría...")
- Buscadores que toleren mayúsculas/minúsculas y acentos
- Mostrar número de resultados tras filtrar ("23 de 150 productos")
- **Problema detectado si:** no hay botón de reset de filtros, buscador sin placeholder, o sin indicación del número de resultados

### Jerarquía y navegación
- Una sola acción principal por pantalla, claramente identificada
- Máximo 5-6 pestañas principales
- Las pestañas agrupan contenido relacionado, no funciones técnicas
- Elementos técnicos (logs, importadores, configuración avanzada) siempre colapsados o en pestaña secundaria
- **Problema detectado si:** más de 6 pestañas, logs visibles por defecto, o no hay jerarquía clara entre acciones principales y secundarias

### Leyendas y contexto
- Métricas con nombres no obvios deben tener tooltip o expander explicativo
- Tooltips colapsables (no texto fijo que ocupe espacio permanente)
- Iconos ℹ️ junto a términos que necesitan explicación
- Los gráficos con lógica de cálculo no evidente deben tener nota explicativa
- **Problema detectado si:** métricas como "M4", "ACOS", "CVR" sin explicación accesible para usuarios nuevos

### Cursores
- Elementos clicables (botones, links, cards interactivas): `cursor: pointer`
- Texto seleccionable: `cursor: text`
- Elementos deshabilitados: `cursor: not-allowed`
- Zona de arrastre: `cursor: grab`
- **Problema detectado si:** botones o cards clicables sin cambio de cursor al pasar el ratón

### Feedback y estados
- Toda acción que tarda más de 1 segundo debe mostrar spinner o barra de progreso
- Tras una acción exitosa, confirmación visible (mensaje verde, toast, etc.)
- Tras un error, mensaje claro con causa y solución
- Estados vacíos (sin datos) deben tener mensaje explicativo, no pantalla en blanco
- **Problema detectado si:** hay procesos sin indicador de carga, pantallas en blanco sin mensaje, o errores sin explicación para el usuario

---

## 4. Reglas de prioridad

Cuando hay conflicto entre capas:

```
Skill corporativa Funidelia  >  Criterios universales  >  Preferencia estética
```

Es decir:
- Si Funidelia define el azul como color primario y WCAG dice que ese azul no tiene suficiente contraste sobre un fondo concreto, se resuelve ajustando el fondo, no cambiando el azul.
- Si una regla universal no está cubierta por la skill corporativa, se aplica igualmente.
- Las decisiones marcadas como IGNORAR en `ux_report.md` tienen prioridad sobre todo — son decisiones conscientes del equipo.

---

## 5. Severidad de problemas

| Severidad | Cuándo aplicar |
|-----------|----------------|
| 🔴 Alta | Impide o dificulta gravemente el uso. El usuario no puede completar su tarea. |
| 🟡 Media | Molesta o confunde pero no bloquea. El usuario puede continuar con esfuerzo. |
| 🟢 Baja | Detalle de pulido. No afecta al uso pero deteriora la experiencia. |

---

*Fuentes: Nielsen Norman Group (nngroup.com), W3C WCAG 2.1 (w3.org), Dashboard UX best practices (pencil&paper, uxpin)*
*Versión: 1.0 — Abril 2026*
