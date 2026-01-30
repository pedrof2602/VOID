# Prompt actualizado para analyze_input() con contexto temporal y herramientas

## Reemplazar el prompt actual (línea 67-116) con este:

```python
        prompt = f"""
CONTEXTO TEMPORAL:
Fecha y hora actual: {current_datetime}
Zona horaria: America/Argentina/Buenos_Aires

Analiza el siguiente input de voz y extrae TODA la información en un solo JSON:

Input: "{text}"

Tareas:
1. Limpia ruido (ehh, umm, saludos, repeticiones)
2. Detecta si es ACTION (tarea/evento/recordatorio) o MEMORY (nota/idea/información)
3. Clasifica categoría específica:
   - Para ACTION: 
     * CALENDAR: Cualquier evento con fecha/hora específica (incluso si menciona "recordatorio")
     * TODO: Tareas sin fecha específica
     * REMINDER: Solo recordatorios vagos SIN fecha/hora específica (ej: "recordarme comprar leche")
   - Para MEMORY: FACT (hechos), IDEA (ideas), JOURNAL (diario), GOAL (metas)
4. Extrae entidades: fecha, hora, personas, lugares, ubicación física
5. Para eventos CALENDAR: genera un título corto y descriptivo (máximo 5 palabras)
6. Extrae ubicación física completa si se menciona (dirección, lugar, calle y número)
7. Extrae recordatorio si se menciona (ejemplos: "2 horas antes" → 120, "30 minutos antes" → 30, "1 día antes" → 1440)
8. Reescribe el texto limpio en 3ra persona de forma técnica

🔧 HERRAMIENTAS DISPONIBLES:
Si necesitas AGENDAR un evento en Google Calendar, usa la herramienta "calendar_add":
- Calcula la fecha ISO 8601 exacta (YYYY-MM-DDTHH:MM:SS)
- Ejemplo: "mañana a las 3pm" → "{tomorrow_date}T15:00:00"
- Ejemplo: "pasado mañana 10am" → "{day_after_tomorrow}T10:00:00"

Ejemplos:
- "Reunión con Juan mañana a las 3pm en calle Perón 342"
  → type: ACTION, category: CALENDAR, title: "Reunión con Juan", location: "Calle Perón 342",
     tool_name: "calendar_add", tool_args: {{"summary": "Reunión con Juan", "start_iso": "{tomorrow_date}T15:00:00", "duration_minutes": 60, "location": "Calle Perón 342"}}

- "Inscribirme a materias mañana 10 AM"
  → type: ACTION, category: CALENDAR, title: "Inscripción a materias",
     tool_name: "calendar_add", tool_args: {{"summary": "Inscripción a materias", "start_iso": "{tomorrow_date}T10:00:00", "duration_minutes": 60}}

- "Recordarme comprar leche" (SIN fecha/hora específica)
  → type: ACTION, category: REMINDER, title: "Comprar leche", tool_name: null

- "Pedro me comentó que le gusta el café"
  → type: MEMORY, category: FACT, refined_text: "A Pedro le gusta el café", tool_name: null

Responde SOLO con JSON válido (sin markdown):
{{
  "type": "ACTION" | "MEMORY",
  "category": "CALENDAR" | "TODO" | "REMINDER" | "FACT" | "IDEA" | "JOURNAL" | "GOAL",
  "refined_text": "texto limpio en 3ra persona",
  "title": "título corto del evento (solo para CALENDAR, máx 5 palabras)",
  "date": "fecha si se menciona (ej: mañana, pasado mañana, 25 de enero)",
  "time": "hora si se menciona (ej: 3pm, 15:00, mañana)",
  "location": "dirección completa si se menciona",
  "reminder_minutes": número entero de minutos antes para recordatorio (null si no se menciona),
  "entities": {{"person": "nombre", "place": "lugar"}},
  "tags": ["tag1", "tag2"],
  "confidence": 0.0-1.0,
  "tool_name": "calendar_add" (solo si es CALENDAR y necesitas agendar) | null,
  "tool_args": {{"summary": "...", "start_iso": "YYYY-MM-DDTHH:MM:SS", "duration_minutes": 60, "location": "..."}} (solo si tool_name no es null) | null
}}
"""
```

## Instrucciones de reemplazo manual:

1. Abrir `src/services/intelligence.py`
2. Ir a la línea 67 (donde empieza el prompt actual)
3. Reemplazar TODO el prompt (hasta la línea 116) con el nuevo prompt de arriba
4. Asegurarse de que las f-strings `{current_datetime}`, `{tomorrow_date}`, `{day_after_tomorrow}` estén correctamente interpoladas
