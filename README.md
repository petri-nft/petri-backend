# 🌲 Petri Backend API

> REST API powering tree NFTs with AI chat, health tracking, and voice generation

A FastAPI-based backend that verifies tree health through satellite data (NDVI), powers AI personality chat via Groq LLM, and generates voice responses using ElevenLabs TTS.

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14-336791?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL 12+
- API Keys:
  - [Groq API](https://console.groq.com) (LLM - free tier available)
  - [ElevenLabs API](https://elevenlabs.io) (TTS - free tier available)

### Installation

```bash
# Clone and navigate
git clone https://github.com/Xeeshan85/petri-backend.git
cd petri-backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials (see Configuration section)

# Initialize database
python app/database/init.py

# Start server
uvicorn app.main:app --reload
```

Server runs at: **http://localhost:8000**

---

## 📋 Features

### 🌳 Core Functionality

- **Tree Management** - CRUD operations for trees with GPS tracking
- **Health Monitoring** - NDVI-based health scoring and recommendations
- **AI Personality** - Groq-powered tree companions with customizable tones
- **Voice Generation** - ElevenLabs TTS for audio responses
- **NFT Integration** - Dynamic metadata generation based on tree health
- **Marketplace** - Trading system for TreeTokens
- **Authentication** - JWT-based secure user auth

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Framework** | FastAPI (async Python) |
| **Server** | Uvicorn ASGI |
| **Database** | PostgreSQL + SQLAlchemy ORM |
| **Authentication** | JWT (python-jose) |
| **Validation** | Pydantic v2 |
| **LLM** | Groq API (llama-3.1-8b-instant) |
| **Text-to-Speech** | ElevenLabs API |
| **Image Processing** | Pillow |
| **Migrations** | Alembic |

---

## ⚙️ Configuration

Create a `.env` file with the following variables:

```env
# ========== DATABASE ==========
DATABASE_URL=postgresql://user:password@localhost:5432/petri_db

# ========== AUTHENTICATION ==========
SECRET_KEY=your-secret-key-here  # Generate: openssl rand -hex 32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ========== AI SERVICES ==========
GROQ_API_KEY=gsk_...              # Get from https://console.groq.com
ELEVENLABS_API_KEY=sk_...         # Get from https://elevenlabs.io

# ========== OPTIONAL SERVICES ==========
CARD_GENERATION_SERVICE_URL=http://localhost:8001
HEALTH_SCORING_SERVICE_URL=http://localhost:8002
```


---

## 🗄️ Database Setup

### Option 1: Auto-Initialize (Recommended)

```bash
python app/database/init.py
```

### Option 2: Manual Setup

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database and user
CREATE DATABASE petri_db;
CREATE USER petri_user WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE petri_db TO petri_user;

# Run migrations
alembic upgrade head
```

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration settings
│   ├── auth.py              # JWT authentication
│   │
│   ├── database/
│   │   ├── db.py            # Database connection
│   │   └── init.py          # Schema initialization
│   │
│   ├── models/              # SQLAlchemy ORM models
│   │   ├── User.py
│   │   ├── Tree.py
│   │   ├── TreePersonality.py
│   │   └── ChatMessage.py
│   │
│   ├── schemas/             # Pydantic request/response schemas
│   │
│   ├── services/            # Business logic
│   │   ├── ai_service.py    # Groq LLM + ElevenLabs TTS
│   │   ├── business_logic.py
│   │   ├── nft_service.py
│   │   └── voice_service.py
│   │
│   └── routes/              # API endpoints
│       ├── auth.py          # /api/auth/*
│       ├── trees.py         # /api/trees/*
│       ├── portfolio.py
│       ├── trades.py
│       └── tokens.py
│
├── static/audio/            # Generated audio files
├── migrations/              # Alembic migrations
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🔌 API Endpoints

### Authentication
```
POST   /api/auth/register     # Create account
POST   /api/auth/login        # Get JWT token
POST   /api/auth/refresh      # Refresh token
```

### Trees
```
GET    /api/trees             # List user's trees
POST   /api/trees             # Plant new tree
GET    /api/trees/{id}        # Get tree details
PUT    /api/trees/{id}        # Update tree
DELETE /api/trees/{id}        # Delete tree
POST   /api/trees/{id}/water  # Log watering action
```

### AI & Chat
```
GET    /api/trees/{id}/personality        # Get AI personality
POST   /api/trees/{id}/personality        # Set personality tone
POST   /api/trees/{id}/chat               # Send message (text/audio)
GET    /api/trees/{id}/chat-history       # Get conversation history
```

### Voice Generation
```
GET    /api/voices            # List available voices
POST   /api/trees/{id}/chat?include_audio=true  # Get audio response
```

### NFT & Trading
```
POST   /api/trees/{id}/nft    # Generate NFT metadata
POST   /api/trees/{id}/sell   # List for sale
GET    /api/trades            # Browse marketplace
POST   /api/trades/{id}/buy   # Purchase tree
```

---

## 📚 Interactive Documentation

FastAPI automatically generates interactive API docs:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## 🤖 AI Personality System

### How It Works

1. **Personality Setup**: User selects tone (wise, humorous, poetic, etc.)
2. **Context Building**: System gathers tree health, weather, care history
3. **LLM Generation**: Groq API generates personality-driven response
4. **Voice Synthesis**: ElevenLabs converts text to audio
5. **Audio Delivery**: MP3 file returned to frontend

### Setup Tones/Personality
Some defaults are shared below.
| Tone | Voice | Personality |
|------|-------|-------------|
| **Wise** | Rachel | Calm, philosophical mentor |
| **Humorous** | Bella | Witty, sarcastic friend |
| **Poetic** | Ember | Lyrical, nature-inspired |

### Example Chat Flow

```json
// Request
POST /api/trees/123/chat
{
  "message": "How are you feeling today?",
  "include_audio": true
}

// Response
{
  "response": "My NDVI is looking strong at 0.75! Those clouds finally delivered, and I'm soaking it up. Keep this up and we'll hit Silver Badge by next week! 🌱",
  "audio_url": "/static/audio/chat_123_1699999999.mp3",
  "health_data": {
    "ndvi": 0.75,
    "health_score": 82
  }
}
```

---

## 🧪 Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest

# With coverage
pytest --cov=app --cov-report=html
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## 🐳 Docker Deployment

```bash
# Build image
docker build -t petri-backend .

# Run container
docker run -p 8000:8000 --env-file .env petri-backend

# Or use docker-compose
docker-compose up -d
```

---

## 🔒 Security Features

- ✅ JWT authentication with token expiration
- ✅ Password hashing with bcrypt
- ✅ Pydantic validation for all inputs
- ✅ SQL injection prevention via SQLAlchemy ORM
- ✅ CORS configuration for frontend integration
- ✅ Environment variable protection
- ✅ Rate limiting ready (implement in production)

---

## 🐛 Troubleshooting

### Database Connection Issues

```bash
# Test connection
psql -U postgres -d petri_db -c "SELECT 1"

# Check .env
cat .env | grep DATABASE_URL

# Reinitialize
python app/database/init.py
```
---

## 🚧 Roadmap

- [ ] WebSocket support for real-time updates
- [ ] Celery task queue for async processing
- [ ] Redis caching layer
- [ ] Prometheus metrics endpoint
- [ ] GraphQL API option
- [ ] Rate limiting middleware
- [ ] Admin dashboard
- [ ] Automated testing suite


## 📄 License

MIT License - see [LICENSE](LICENSE) file

---

## 🌟 Team ISTARI

**Built by:**
- Muhammad Masab Hammad
- Asim Iqbal
- Muhammad Zeeshan Naveed
- Mahad Rehman Durrani

---

## 📞 Support

- **API Docs**: http://localhost:8000/docs
- **Issues**: [GitHub Issues](https://github.com/Xeeshan85/petri-backend/issues)
- **Email**: i220615@nu.edu.pk

---

<p align="center">
  <strong>🌲 Powering the future of environmental stewardship 🌍</strong>
</p>
