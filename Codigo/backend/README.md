# VOID Backend - Quick Start Guide

## 🚀 Quick Deployment

### 1. Set Up Database (Supabase)

```bash
# Open Supabase SQL Editor and run:
supabase_schema.sql
```

### 2. Configure Environment

Ensure your `.env` file has:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key
DEEPGRAM_API_KEY=your-deepgram-key
GOOGLE_API_KEY=your-google-api-key
```

### 3. Run with Docker

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f void-backend
```

### 4. Test the API

```bash
# Install requests if needed
pip install requests

# Run test script
python test_api.py
```

## 📚 Documentation

- **API Reference**: See `API_DOCUMENTATION.md`
- **Full Walkthrough**: See walkthrough artifact
- **Implementation Plan**: See implementation_plan artifact

## 🏗️ Architecture

```
PC Client → POST /input/voice → FastAPI → Supabase → Mobile Device
            (Audio File)         (STT+Brain)  (Queue)   (Poll)
```

## 📁 Project Structure

```
backend/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   └── server.py          # FastAPI application
│   ├── services/
│   │   ├── transcriber.py     # Deepgram STT
│   │   └── intelligence.py    # DSPy Brain
│   ├── config.py              # Configuration
│   └── schemas.py             # Pydantic models
├── supabase_schema.sql        # Database schema
├── Dockerfile                 # Container definition
├── docker-compose.yml         # Orchestration
├── requirements.txt           # Python dependencies
├── test_api.py               # Test script
└── API_DOCUMENTATION.md      # API reference
```

## 🔧 Development

Run locally without Docker:
```bash
pip install -r requirements.txt
uvicorn src.api.server:app --reload
```

## 📱 Mobile Integration

Poll for signals:
```sql
SELECT * FROM device_signals
WHERE user_id = '<uuid>'
AND is_delivered = FALSE
ORDER BY created_at ASC;
```

Mark as delivered:
```sql
UPDATE device_signals
SET is_delivered = TRUE
WHERE id = '<signal_id>';
```

## ✅ Verification Checklist

- [ ] SQL schema deployed to Supabase
- [ ] Environment variables configured
- [ ] Docker container running
- [ ] Health check returns 200 OK
- [ ] Voice input endpoint processes audio
- [ ] Signals appear in database
- [ ] Mobile can poll and retrieve signals
