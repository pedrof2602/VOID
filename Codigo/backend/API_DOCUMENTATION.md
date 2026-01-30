# VOID Backend API Documentation

## Overview

The VOID Backend API provides a decoupled IoT architecture for processing voice input from PC clients and queuing device signals for mobile consumption.

**Architecture Flow:**
```
PC Client → POST /input/voice → Backend (STT + DSPy Brain) → Supabase Queue → Mobile Device
```

## Base URL

```
http://localhost:8000
```

## Authentication

> ⚠️ **Current Version**: No authentication implemented. The `user_id` is passed in the request body.
> 
> **Production TODO**: Implement JWT token authentication or API key validation.

## Endpoints

### Health Check

**GET** `/health`

Check if the API is running and healthy.

**Response:**
```json
{
  "status": "healthy",
  "service": "VOID Backend API",
  "version": "1.0.0"
}
```

---

### Process Voice Input

**POST** `/input/voice`

Process voice input from PC client, transcribe it, analyze with DSPy Brain, and queue the result for mobile device.

**Request:**

- **Content-Type:** `multipart/form-data`
- **Parameters:**
  - `file` (required): Audio file (WAV, MP3, M4A, or OGG format)
  - `user_id` (required): User UUID string

**Example (cURL):**
```bash
curl -X POST http://localhost:8000/input/voice \
  -F "file=@recording.wav" \
  -F "user_id=98181061-0369-4267-9a9a-72f480744a2b"
```

**Example (Python):**
```python
import requests

url = "http://localhost:8000/input/voice"
files = {"file": open("recording.wav", "rb")}
data = {"user_id": "98181061-0369-4267-9a9a-72f480744a2b"}

response = requests.post(url, files=files, data=data)
print(response.json())
```

**Success Response (200 OK):**
```json
{
  "status": "success",
  "message": "Signal queued for mobile device",
  "signal_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "signal_type": "ACTION"
}
```

**Signal Types:**
- `HAPTIC_ONLY`: Only vibration feedback
- `TEXT`: Display text message on mobile
- `ACTION`: Trigger app action (calendar, notes, etc.)

**Error Responses:**

**400 Bad Request** - Invalid user_id format:
```json
{
  "detail": "Invalid user_id format. Must be a valid UUID."
}
```

**400 Bad Request** - Invalid file type:
```json
{
  "detail": "Invalid file type. Supported formats: WAV, MP3, M4A, OGG"
}
```

**422 Unprocessable Entity** - Transcription failed:
```json
{
  "detail": "Could not transcribe audio. Please try again with clearer audio."
}
```

**500 Internal Server Error** - Server error:
```json
{
  "detail": "Internal server error: <error message>"
}
```

---

## Database Schema

### device_signals Table

Stores queued signals for mobile devices.

**Columns:**
- `id` (UUID): Primary key, auto-generated
- `user_id` (UUID): Foreign key to users table
- `type` (ENUM): Signal type (`HAPTIC_ONLY`, `TEXT`, `ACTION`)
- `payload` (JSONB): Flexible data structure
- `is_delivered` (BOOLEAN): Delivery status (default: FALSE)
- `created_at` (TIMESTAMPTZ): Creation timestamp

**Payload Examples:**

Text signal:
```json
{
  "text": "Reminder: Meeting at 3 PM",
  "haptic": "LIGHT"
}
```

Action signal:
```json
{
  "action": "CALENDAR",
  "params": {
    "title": "Team Meeting",
    "date": "2026-01-23",
    "time": "15:00",
    "location": "Conference Room A"
  },
  "haptic": "MEDIUM"
}
```

Haptic only:
```json
{
  "haptic": "HEAVY"
}
```

---

## Mobile Integration

### Polling for Signals

Mobile devices should poll for undelivered signals:

```sql
SELECT * FROM device_signals
WHERE user_id = '<user_uuid>'
AND is_delivered = FALSE
ORDER BY created_at ASC;
```

### Marking as Delivered

After processing a signal, mark it as delivered:

```sql
UPDATE device_signals
SET is_delivered = TRUE
WHERE id = '<signal_uuid>';
```

---

## Running the API

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run with uvicorn
uvicorn src.api.server:app --host 0.0.0.0 --port 8000 --reload
```

### Docker

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f void-backend

# Stop
docker-compose down
```

---

## Environment Variables

Required environment variables (set in `.env` file):

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key

# API Keys
DEEPGRAM_API_KEY=your-deepgram-key
GOOGLE_API_KEY=your-google-api-key

# Optional
USER_ID=your-default-user-uuid
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=*
```

---

## Rate Limiting

> ⚠️ **Production TODO**: Implement rate limiting per user to prevent abuse.

Recommended limits:
- 60 requests per minute per user
- 1000 requests per hour per user

---

## CORS Configuration

Currently configured to allow all origins (`*`). For production, update `CORS_ORIGINS` in `.env`:

```env
CORS_ORIGINS=https://yourapp.com,https://admin.yourapp.com
```

---

## Error Handling

All errors follow FastAPI's standard error response format:

```json
{
  "detail": "Error message here"
}
```

HTTP Status Codes:
- `200`: Success
- `400`: Bad Request (invalid input)
- `422`: Unprocessable Entity (transcription failed)
- `500`: Internal Server Error

---

## Logging

The API logs all operations with structured logging:

```
2026-01-23 11:00:00 - INFO - 📥 Received audio file from user ...7890: recording.wav
2026-01-23 11:00:01 - INFO - 👂 Transcribing audio...
2026-01-23 11:00:02 - INFO - 🗣️ Transcription: Schedule meeting tomorrow at 3 PM
2026-01-23 11:00:03 - INFO - 🧠 Processing with Intelligence Service...
2026-01-23 11:00:04 - INFO - 🎯 Analysis result - Type: ACTION, Category: CALENDAR
2026-01-23 11:00:05 - INFO - ✅ Signal queued successfully: a1b2c3d4-...
```

---

## Future Enhancements

- [ ] JWT authentication
- [ ] Rate limiting
- [ ] WebSocket support for real-time push notifications
- [ ] Signal retry mechanism
- [ ] Analytics and monitoring
- [ ] Multi-language support
