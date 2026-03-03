# Seguridad — VOID Backend

## Configuración de credenciales

### Paso 1: Crear tu `.env`

```bash
cp .env.example .env
```

Abre el `.env` y rellena cada valor con tus credenciales reales.

### Paso 2: Obtener las credenciales

| Variable | Dónde obtenerla |
|---|---|
| `SUPABASE_URL` | [Supabase Dashboard](https://supabase.com/dashboard) → tu proyecto → Settings → API |
| `SUPABASE_KEY` | Mismo lugar — usa **service_role** (solo en este backend servidor) |
| `GOOGLE_API_KEY` | [Google AI Studio](https://aistudio.google.com/apikey) |
| `DEEPGRAM_API_KEY` | [Deepgram Console](https://console.deepgram.com) → API Keys |
| `USER_ID` | Supabase Dashboard → Authentication → Users |

---

## ⚠️ Reglas de seguridad críticas

### 1. `service_role` vs `anon` key de Supabase

| Contexto | Clave a usar | Por qué |
|---|---|---|
| **Este backend** (servidor) | `service_role` | Necesita acceso total para gestionar datos |
| **App móvil** (Flutter) | `anon` | Respeta las políticas RLS; segura para el cliente |

> **NUNCA** uses la `service_role` key en el cliente móvil. Si se filtra, cualquiera puede leer/escribir/borrar todos los datos de Supabase sin restricciones.

### 2. El `.env` nunca va al repositorio

El `.gitignore` ya lo excluye. Antes de cada `git commit`, verifica con:

```bash
git status
```

El `.env` **no debe aparecer** en la lista de archivos a confirmar.

### 3. El `.env.example` SÍ va al repositorio

Contiene solo placeholders. Sirve como guía para que cualquier desarrollador nuevo sepa qué variables necesita configurar.

---

## Si una clave se filtra accidentalmente

Actúa de inmediato — una clave filtrada en un repositorio público se detecta en segundos con bots automáticos.

1. **Supabase** → Settings → API → **Rotate** service role key
2. **Google Gemini** → [AI Studio](https://aistudio.google.com/apikey) → Eliminar la clave y crear una nueva
3. **Deepgram** → [Console](https://console.deepgram.com) → Revocar la API key
4. Actualizar el `.env` con las nuevas claves
5. Si el commit ya está en el historial público, considera el repo comprometido. Rota todas las claves sin excepción.

---

## Verificar que el historial de Git está limpio

```bash
# Buscar si .env alguna vez estuvo en el historial
git log --all --full-history -- ".env"

# Si aparecen commits, el historial está comprometido — rota todas las claves
```
