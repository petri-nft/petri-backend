# 🌳 Petri Backend - Complete Setup Guide

A FastAPI-based REST API for tree NFTs with AI chat, health tracking, trading, and voice generation capabilities.

## 📋 Table of Contents

- [What's in the Backend?](#whats-in-the-backend)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Configuration](#configuration)
- [Running the Backend](#running-the-backend)
- [Database Setup](#database-setup)
- [Project Structure](#project-structure)
- [Key Features](#key-features)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)

---

## 🏗 What's in the Backend?

The Petri backend provides a complete REST API for:

### 1. *Tree Management* 🌲
- Create, read, update, delete trees
- Track tree health and care history
- Location-based tree discovery
- Tree photos and metadata

### 2. *AI Personality & Chat* 🤖💬
- AI-powered tree personalities using Groq LLM
- Tree chat with personality-aware responses
- Conversation history tracking
- Multiple tone options (wise, humorous, poetic, etc.)

### 3. *Voice Generation* 🎙
- Text-to-speech using ElevenLabs API
- 3 voice options (Rachel, Bella, Ember)
- Voice tone-based voice selection
- MP3 audio file generation and storage

### 4. *User Authentication* 🔐
- JWT-based authentication
- User registration and login
- Secure password hashing (bcrypt)
- Token-based API access

### 5. *NFT Features* 🎨
- NFT metadata generation
- Card image generation
- NFT minting capabilities
- Trading and marketplace

### 6. *Health Tracking* 💚
- Tree health scoring system
- NDVI (vegetation health) tracking
- Care history logging
- Health recommendations

### 7. *Portfolio Management* 💼
- User portfolio tracking
- Tree valuation
- Trading history
- Investment tracking

---

## 🛠 Tech Stack

| Component | Technology |
|-----------|-----------|
| *Framework* | FastAPI (async Python web framework) |
| *Server* | Uvicorn (ASGI server) |
| *Database* | PostgreSQL + SQLAlchemy ORM |
| *Authentication* | JWT (python-jose) |
| *Validation* | Pydantic |
| *LLM* | Groq API (llama-3.1-8b-instant) |
| *TTS* | ElevenLabs API |
| *Image Processing* | Pillow |
| *Environment* | python-dotenv |
| *Migration* | Alembic |

---

## 📦 Prerequisites

Before you start, ensure you have:

### System Requirements
- *Python*: 3.9 or higher
- *PostgreSQL*: 12 or higher
- *pip*: Python package manager
- *Git*: Version control (optional)

### API Keys (Required)
1. *Groq API Key* - For LLM
   - Get from: https://console.groq.com
   - Free tier available with generous limits

2. *ElevenLabs API Key* - For text-to-speech
   - Get from: https://elevenlabs.io
   - Free tier includes monthly character limit

3. *PostgreSQL Database*
   - Local or remote PostgreSQL instance
   - Database name, user, and password

---

## 🚀 Installation & Setup

### Step 1: Clone the Repository

bash
cd /home/admin/Desktop/Petri/backend
# or
git clone <repository-url>
cd backend


### Step 2: Create Virtual Environment

bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate


You should see (venv) prefix in your terminal.

### Step 3: Install Dependencies

bash
# Install all required packages
pip install -r requirements.txt


*What gets installed:*
- FastAPI & Uvicorn - Web framework and server
- SQLAlchemy - ORM for database
- psycopg2-binary - PostgreSQL adapter
- Pydantic - Data validation
- python-jose - JWT authentication
- passlib & bcrypt - Password hashing
- requests - HTTP client
- elevenlabs - TTS API
- google-generativeai - AI integration
- Pillow - Image processing
- python-dotenv - Environment variables
- alembic - Database migrations

### Step 4: Configure Environment Variables

bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your settings (see Configuration section below)
nano .env
# or use your preferred editor


### Step 5: Set Up Database

bash
# Initialize the database schema
python app/database/init.py

# Or if using migrations:
alembic upgrade head


### Step 6: Start the Backend

bash
# Run with auto-reload (development)
python -m uvicorn app.main:app --reload

# Or use the provided script
bash start.sh

# Or run on specific host/port
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000


Server will be available at: *http://localhost:8000*

---

## ⚙ Configuration

### Environment Variables (.env file)

Create a .env file in the backend root directory:

bash
# ============ DATABASE ============
# PostgreSQL connection string
# Format: postgresql://username:password@host:port/database
DATABASE_URL=postgresql://user:password@localhost:5432/petri_db

# ============ AUTHENTICATION ============
# Secret key for JWT signing (generate a random string)
# Example: openssl rand -hex 32
SECRET_KEY=your-super-secret-key-change-this-in-production

# JWT algorithm
ALGORITHM=HS256

# Token expiration time in minutes
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ============ EXTERNAL SERVICES ============
# Groq API for LLM (chat/personality)
GROQ_API_KEY=your-groq-api-key-here

# ElevenLabs API for text-to-speech
ELEVENLABS_API_KEY=your-elevenlabs-api-key-here

# ============ MICROSERVICES ============
# Card generation service (optional)
CARD_GENERATION_SERVICE_URL=http://localhost:8001

# Health scoring service (optional)
HEALTH_SCORING_SERVICE_URL=http://localhost:8002


### Getting API Keys

#### Groq API Key
1. Visit https://console.groq.com
2. Sign up for free account
3. Create API key
4. Copy and paste into .env as GROQ_API_KEY

#### ElevenLabs API Key
1. Visit https://elevenlabs.io
2. Sign up for free account
3. Go to Settings → API Keys
4. Copy and paste into .env as ELEVENLABS_API_KEY

#### PostgreSQL Connection String

postgresql://username:password@localhost:5432/database_name

Example:
postgresql://postgres:mypassword@localhost:5432/petri_db


---

## 🏃 Running the Backend

### Development Mode (with auto-reload)

bash
# Terminal 1: Start the backend
python -m uvicorn app.main:app --reload

# Output should show:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# INFO:     Application startup complete


Access at: http://localhost:8000

### Production Mode

bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4


### Using the Start Script

bash
bash start.sh


### Check If Backend is Running

bash
curl http://localhost:8000/docs
# Should open FastAPI interactive documentation


---

## 🗄 Database Setup

### Prerequisites
- PostgreSQL installed and running
- Database user created
- Database created

### Option 1: Using Database Init Script

bash
# Creates database schema automatically
python app/database/init.py


### Option 2: Manual Setup

bash
# 1. Connect to PostgreSQL
psql -U postgres

# 2. Create database
CREATE DATABASE petri_db;

# 3. Create user (if needed)
CREATE USER petri_user WITH PASSWORD 'your_password';

# 4. Grant privileges
GRANT ALL PRIVILEGES ON DATABASE petri_db TO petri_user;

# 5. Exit PostgreSQL
\q

# 6. Run initialization
python app/database/init.py


### Option 3: Using Alembic Migrations

bash
# View migration status
alembic current

# Run pending migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "migration message"

# Rollback one migration
alembic downgrade -1


### Verify Database Connection

python
# Test connection with Python
python << 'EOF'
from app.database.db import SessionLocal
try:
    db = SessionLocal()
    print("✓ Database connection successful!")
    db.close()
except Exception as e:
    print(f"✗ Database connection failed: {e}")
EOF


---

## 📁 Project Structure


backend/
├── app/
│   ├── __init__.py
│   ├── main.py                      # Application entry point
│   ├── config.py                    # Configuration & settings
│   ├── auth.py                      # JWT authentication
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── db.py                    # Database connection
│   │   └── init.py                  # Database initialization
│   │
│   ├── models/                      # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── User                     # User model
│   │   ├── Tree                     # Tree model
│   │   ├── TreePersonality          # AI personality
│   │   ├── ChatMessage              # Chat history
│   │   └── ...
│   │
│   ├── schemas/                     # Pydantic schemas (request/response)
│   │   ├── __init__.py
│   │   └── (various schemas)
│   │
│   ├── services/                    # Business logic & integrations
│   │   ├── __init__.py
│   │   ├── ai_service.py            # Groq LLM + ElevenLabs TTS
│   │   ├── business_logic.py        # Core business logic
│   │   ├── external_services.py     # External API calls
│   │   ├── nft_service.py           # NFT generation
│   │   └── voice_service.py         # Voice transcription
│   │
│   └── routes/                      # API endpoints
│       ├── __init__.py
│       ├── auth.py                  # Auth endpoints
│       ├── trees.py                 # Tree endpoints (main)
│       ├── portfolio.py             # Portfolio endpoints
│       ├── trades.py                # Trading endpoints
│       └── tokens.py                # Token endpoints
│
├── migrations/                      # Alembic database migrations
│
├── static/
│   └── audio/                       # Generated audio files
│
├── .env.example                     # Example environment variables
├── .env                             # Your configuration (not committed)
├── requirements.txt                 # Python dependencies
├── start.sh                         # Start script
├── README.md                        # Original README
└── BACKEND_README.md                # This file


---

## ⭐ Key Features

### 1. Tree Management

GET    /api/trees              # List user's trees
POST   /api/trees              # Plant new tree
GET    /api/trees/{id}         # Get tree details
PUT    /api/trees/{id}         # Update tree
DELETE /api/trees/{id}         # Delete tree


### 2. AI Chat & Personality

GET    /api/trees/{id}/personality        # Get personality
POST   /api/trees/{id}/personality        # Set personality
POST   /api/trees/{id}/chat               # Chat with tree
GET    /api/trees/{id}/chat-history       # Get chat history


### 3. Voice Generation

GET    /api/voices             # Get available voices
POST   /api/trees/{id}/chat    # Chat with audio (include_audio=true)


### 4. Authentication

POST   /api/auth/login         # Login
POST   /api/auth/register      # Register
POST   /api/auth/refresh       # Refresh token


### 5. NFT & Trading

POST   /api/trees/{id}/nft     # Generate NFT
POST   /api/trees/{id}/sell    # List for sale
GET    /api/trades             # Get market listings
POST   /api/trades/{id}/buy    # Purchase tree


---

## 📚 API Documentation

### Interactive Docs (Swagger UI)
Available at: *http://localhost:8000/docs*

Features:
- Try API endpoints directly
- See request/response examples
- View schema definitions
- Test authentication

### Alternative Docs (ReDoc)
Available at: *http://localhost:8000/redoc*

### OpenAPI Schema
Available at: *http://localhost:8000/openapi.json*

---

## 🔧 Common Tasks

### Adding a New Tree Route

1. Create endpoint in app/routes/trees.py:
python
@router.post("/{tree_id}/my-feature")
def my_feature(tree_id: int, db: Session = Depends(get_db)):
    # Your code here
    pass


2. The route is automatically included via app.include_router()

### Adding a New Database Model

1. Create model in app/models/:
python
class MyModel(Base):
    __tablename__ = "my_models"
    id = Column(Integer, primary_key=True)
    # ... other fields


2. Import in app/models/__init__.py

3. Run migration:
bash
alembic revision --autogenerate -m "Add MyModel"
alembic upgrade head


### Calling External APIs

Use the services in app/services/:
- ai_service.py - Groq LLM & ElevenLabs
- external_services.py - Other APIs
- nft_service.py - NFT generation

---

## 🐛 Troubleshooting

### Issue: "Connection refused" (Port 8000)

*Solution:*
bash
# Check if port is in use
lsof -i :8000

# Kill process using port
kill -9 <PID>

# Run on different port
python -m uvicorn app.main:app --port 8001


### Issue: "Database connection failed"

*Solution:*
bash
# Check DATABASE_URL in .env
echo $DATABASE_URL

# Verify PostgreSQL is running
pg_isready -h localhost -p 5432

# Test connection
psql -U postgres -d petri_db -c "SELECT 1"


### Issue: "ModuleNotFoundError"

*Solution:*
bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate      # Windows

# Reinstall dependencies
pip install -r requirements.txt


### Issue: "Groq API key invalid"

*Solution:*
bash
# Check GROQ_API_KEY in .env
cat .env | grep GROQ

# Get new key from https://console.groq.com
# Update .env and restart backend


### Issue: "ElevenLabs audio not generating"

*Solution:*
bash
# Check ELEVENLABS_API_KEY in .env
cat .env | grep ELEVENLABS

# Verify voice IDs are valid (Rachel, Bella, Ember)
# Check backend logs for errors


### Issue: Virtual environment not working

*Solution:*
bash
# Deactivate and recreate
deactivate
rm -rf venv

# Create fresh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt


---

## 📊 Health Checks

### Verify Backend is Running

bash
# Basic check
curl http://localhost:8000/

# Check documentation
curl http://localhost:8000/docs

# Test database
python app/database/init.py


### View Logs

bash
# Live logs (if running with --reload)
# Check terminal where uvicorn started

# Or check log files
tail -f uvicorn.log
tail -f output.log


---

## 🔒 Security Best Practices

1. *Environment Variables*
   - Never commit .env file
   - Change SECRET_KEY in production
   - Use strong API keys

2. *Database*
   - Use strong passwords
   - Enable PostgreSQL authentication
   - Restrict database access

3. *JWT Tokens*
   - Set reasonable expiration times
   - Refresh tokens regularly
   - Store securely on client

4. *API Security*
   - Validate all inputs with Pydantic
   - Use HTTPS in production
   - Implement rate limiting
   - Add CORS configuration

---

## 📈 Performance Tips

1. *Database Optimization*
   - Use indexes on frequently queried columns
   - Batch database operations
   - Use connection pooling

2. *Caching*
   - Cache personality data
   - Cache voice options
   - Cache frequently accessed trees

3. *Async Operations*
   - Offload long operations (audio generation)
   - Use background tasks for processing
   - Implement job queues

4. *Monitoring*
   - Log important events
   - Track API response times
   - Monitor database connections

---

## 🚢 Deployment

### Local Development
bash
python -m uvicorn app.main:app --reload


### Production on Linux
bash
# Create systemd service
sudo nano /etc/systemd/system/petri-backend.service

# Start service
sudo systemctl start petri-backend
sudo systemctl enable petri-backend

# View logs
sudo journalctl -u petri-backend -f


### Docker Deployment
bash
# Build image
docker build -t petri-backend .

# Run container
docker run -p 8000:8000 --env-file .env petri-backend


---

## 📞 Support & Documentation

- *API Docs*: http://localhost:8000/docs
- *Issues*: Check backend logs for errors
- *Environment Setup*: See .env.example
- *Database*: Check SETUP_DATABASE.md

---

## 📝 Summary

*Quick Start:*
bash
# 1. Setup environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure
cp .env.example .env
# Edit .env with your settings

# 4. Initialize database
python app/database/init.py

# 5. Run backend
python -m uvicorn app.main:app --reload


*Access:*
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

*Status: ✅ READY TO USE*

---

*Last Updated*: 2025-11-09
*Version*: 1.0 Complete
*Status*: Production Ready
