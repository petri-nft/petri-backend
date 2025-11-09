# Plant a Tree - Backend API Documentation

## Overview

This is the backend service for the "Plant a Tree" NFT project. It provides a FastAPI-based REST API for managing trees, NFT tokens, health scoring, and trading.

## Table of Contents

1. [Technology Stack](#technology-stack)
2. [Project Structure](#project-structure)
3. [Setup & Installation](#setup--installation)
4. [Database Schema](#database-schema)
5. [API Endpoints](#api-endpoints)
6. [Authentication](#authentication)
7. [Integration Guide](#integration-guide)
8. [Running the Server](#running-the-server)
9. [Sample Data](#sample-data)

---

## Technology Stack

- **Framework**: FastAPI 0.104.1
- **Server**: Uvicorn 0.24.0
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT (python-jose) with bcrypt password hashing
- **ORM**: SQLAlchemy 2.0.23
- **Database Driver**: psycopg2
- **Validation**: Pydantic 2.5.0

---

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app initialization
│   ├── config.py               # Configuration from environment
│   ├── auth.py                 # Authentication utilities
│   ├── models/
│   │   └── __init__.py         # SQLAlchemy ORM models
│   ├── schemas/
│   │   └── __init__.py         # Pydantic request/response schemas
│   ├── database/
│   │   ├── __init__.py
│   │   ├── db.py               # Database connection & session
│   │   └── init.py             # Database initialization & seeding
│   ├── services/
│   │   ├── __init__.py
│   │   ├── business_logic.py   # Core business logic services
│   │   └── external_services.py # External service integrations
│   └── routes/
│       ├── __init__.py
│       ├── auth.py             # Authentication endpoints
│       ├── trees.py            # Tree management endpoints
│       ├── tokens.py           # NFT token endpoints
│       ├── trades.py           # Trading endpoints
│       └── portfolio.py        # Portfolio endpoints
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
└── README.md                  # This file
```

---

## Setup & Installation

### Prerequisites

- Python 3.9+
- PostgreSQL 12+
- pip

### Installation Steps

1. **Clone the repository**
```bash
cd backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

5. **Initialize database**
```bash
python -m app.database.init
```

This will:
- Create all database tables
- Insert sample data for testing

6. **Run the server**
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

---

## Database Schema

### Tables

#### Users
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### Trees
```sql
CREATE TABLE trees (
    id SERIAL PRIMARY KEY,
    user_id INTEGER FOREIGN KEY REFERENCES users(id),
    species ENUM ('oak', 'pine', 'birch', 'maple', 'elm', 'spruce'),
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    location_name VARCHAR(255),
    planting_date TIMESTAMP DEFAULT NOW(),
    health_score FLOAT DEFAULT 100.0,
    current_value FLOAT DEFAULT 0.0,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### Tokens (NFTs)
```sql
CREATE TABLE tokens (
    id SERIAL PRIMARY KEY,
    token_id VARCHAR(255) UNIQUE NOT NULL,
    tree_id INTEGER UNIQUE FOREIGN KEY REFERENCES trees(id),
    owner_id INTEGER FOREIGN KEY REFERENCES users(id),
    metadata_uri VARCHAR(255),
    image_uri VARCHAR(255),
    current_value FLOAT DEFAULT 0.0,
    base_value FLOAT DEFAULT 100.0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### Shares
```sql
CREATE TABLE shares (
    id SERIAL PRIMARY KEY,
    token_id INTEGER FOREIGN KEY REFERENCES tokens(id),
    owner_id INTEGER FOREIGN KEY REFERENCES users(id),
    quantity FLOAT NOT NULL,  -- Percentage ownership
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Trades
```sql
CREATE TABLE trades (
    id SERIAL PRIMARY KEY,
    token_id INTEGER FOREIGN KEY REFERENCES tokens(id),
    user_id INTEGER FOREIGN KEY REFERENCES users(id),
    trade_type ENUM ('buy', 'sell'),
    quantity FLOAT NOT NULL,
    price_per_unit FLOAT NOT NULL,
    total_value FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Health History
```sql
CREATE TABLE health_history (
    id SERIAL PRIMARY KEY,
    tree_id INTEGER FOREIGN KEY REFERENCES trees(id),
    health_score FLOAT NOT NULL,
    token_value FLOAT,
    event_type VARCHAR(50),
    description TEXT,
    recorded_at TIMESTAMP DEFAULT NOW()
);
```

---

## API Endpoints

### Authentication

#### Register User
```
POST /api/auth/register

Request:
{
    "username": "alice",
    "email": "alice@example.com",
    "password": "securepassword"
}

Response (201):
{
    "id": 1,
    "username": "alice",
    "email": "alice@example.com",
    "created_at": "2024-11-09T10:30:00"
}
```

#### Login
```
POST /api/auth/login

Request:
{
    "username": "alice",
    "password": "securepassword"
}

Response (200):
{
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "user_id": 1,
    "username": "alice"
}
```

### Trees

#### Plant a Tree
```
POST /api/trees
Authorization: Bearer {token}

Request:
{
    "species": "oak",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "location_name": "Central Park, NYC",
    "description": "A beautiful oak tree"
}

Response (201):
{
    "id": 1,
    "user_id": 1,
    "species": "oak",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "location_name": "Central Park, NYC",
    "planting_date": "2024-11-09T10:30:00",
    "health_score": 100.0,
    "current_value": 100.0,
    "description": "A beautiful oak tree",
    "created_at": "2024-11-09T10:30:00",
    "updated_at": "2024-11-09T10:30:00"
}
```

#### Get Tree by ID
```
GET /api/trees/{tree_id}
Authorization: Bearer {token}

Response (200): [Tree object]
```

#### List User's Trees
```
GET /api/trees?limit=50&offset=0
Authorization: Bearer {token}

Response (200): [Array of Tree objects]
```

#### Update Tree Health Score
```
POST /api/trees/{tree_id}/updateHealth
Authorization: Bearer {token}

Request:
{
    "health_score": 92.5,
    "event_type": "growth",
    "description": "Tree grew 2 inches this week"
}

Response (200): [Updated Tree object]
```

#### Get Tree Health History
```
GET /api/trees/{tree_id}/health-history?limit=50
Authorization: Bearer {token}

Response (200):
[
    {
        "id": 1,
        "tree_id": 1,
        "health_score": 100.0,
        "token_value": 100.0,
        "event_type": "planting",
        "description": "Tree planted",
        "recorded_at": "2024-11-09T10:30:00"
    },
    ...
]
```

### Tokens (NFTs)

#### Mint Token for Tree
```
POST /api/trees/{tree_id}/mint
Authorization: Bearer {token}

Response (200):
{
    "token_id": "TREE-1-ABC12345",
    "tree_id": 1,
    "image_uri": "https://placehold.co/400?text=Tree+1",
    "metadata_uri": "ipfs://QmMockMetadata1",
    "message": "Token successfully minted"
}
```

#### Get Token Details
```
GET /api/tokens/{token_id}
Authorization: Bearer {token}

Response (200):
{
    "id": 1,
    "token_id": "TREE-1-ABC12345",
    "tree_id": 1,
    "owner_id": 1,
    "image_uri": "https://placehold.co/400?text=Tree+1",
    "metadata_uri": "ipfs://QmMockMetadata1",
    "current_value": 100.0,
    "base_value": 100.0,
    "tree": [Tree object],
    "created_at": "2024-11-09T10:30:00"
}
```

#### List User's Tokens
```
GET /api/tokens?limit=50&offset=0
Authorization: Bearer {token}

Response (200): [Array of Token objects]
```

### Trades

#### Create Trade (Buy/Sell)
```
POST /api/tokens/{token_id}/trade
Authorization: Bearer {token}

Request:
{
    "trade_type": "buy",
    "quantity": 10.0,
    "price_per_unit": 95.0
}

Response (201):
{
    "id": 1,
    "token_id": 1,
    "user_id": 1,
    "trade_type": "buy",
    "quantity": 10.0,
    "price_per_unit": 95.0,
    "total_value": 950.0,
    "created_at": "2024-11-09T10:30:00"
}
```

#### Get Token Trades
```
GET /api/tokens/{token_id}/trades?limit=50
Authorization: Bearer {token}

Response (200): [Array of Trade objects]
```

### Portfolio

#### Get User Portfolio
```
GET /api/portfolio/me
Authorization: Bearer {token}

Response (200):
{
    "user_id": 1,
    "total_trees": 2,
    "total_value": 195.0,
    "items": [
        {
            "tree": [Tree object],
            "token": [Token object or null],
            "health_score": 100.0,
            "current_value": 100.0
        }
    ]
}
```

---

## Authentication

All endpoints (except `/health` and `/`) require JWT bearer token authentication.

### Getting a Token

1. Register a new user: `POST /api/auth/register`
2. Login: `POST /api/auth/login` to get access token
3. Use token in subsequent requests:

```bash
curl -H "Authorization: Bearer {access_token}" http://localhost:8000/api/trees
```

### Token Expiration

- Tokens expire after 30 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES` in `.env`)
- Get a new token by logging in again

---

## Integration Guide

### Integration with Role C (Card Generation)

The backend calls the card generation service when minting tokens:

```python
POST /api/trees/{tree_id}/mint
```

This triggers:
```
POST {CARD_GENERATION_SERVICE_URL}/api/generate
{
    "tree_id": 1,
    "species": "oak",
    "latitude": 40.7128,
    "longitude": -74.0060,
    "health_score": 100.0
}
```

Expected response:
```json
{
    "image_uri": "https://...",
    "metadata_uri": "ipfs://..."
}
```

**Configure**: Set `CARD_GENERATION_SERVICE_URL` in `.env`

### Integration with Role D (Health Scoring)

The frontend or external service can update health scores:

```
POST /api/trees/{tree_id}/updateHealth
Authorization: Bearer {token}
{
    "health_score": 92.5,
    "event_type": "growth",
    "description": "Tree grew 2 inches"
}
```

This updates the tree's current value based on health:
```
token_value = base_value * (health_score / 100)
```

The backend can also call the health scoring service:

```python
# In future: Call to health service
POST {HEALTH_SCORING_SERVICE_URL}/api/calculate
{
    "tree_id": 1,
    "weeks_since_planting": 4,
    "species": "oak",
    "region": "temperate"
}
```

**Configure**: Set `HEALTH_SCORING_SERVICE_URL` in `.env`

### Integration with Role A (Frontend)

The frontend consumes these endpoints:

1. **Authentication**
   - Register: `POST /api/auth/register`
   - Login: `POST /api/auth/login`

2. **Tree Management**
   - Plant tree: `POST /api/trees`
   - List trees: `GET /api/trees`
   - Get tree: `GET /api/trees/{id}`
   - Get health history: `GET /api/trees/{id}/health-history`

3. **Token/NFT**
   - Mint token: `POST /api/trees/{id}/mint`
   - Get token: `GET /api/tokens/{tokenId}`
   - List tokens: `GET /api/tokens`

4. **Trading**
   - Create trade: `POST /api/tokens/{tokenId}/trade`
   - Get trades: `GET /api/tokens/{tokenId}/trades`

5. **Portfolio**
   - Get portfolio: `GET /api/portfolio/me`

---

## Running the Server

### Development Mode (with auto-reload)
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using main.py directly
```bash
python app/main.py
```

### API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Health Check
```bash
curl http://localhost:8000/health
```

---

## Sample Data

Run database initialization to insert sample data:

```bash
python -m app.database.init
```

This creates:
- **2 Users**: alice, bob
- **3 Trees**: Oak in NYC, Pine in LA, Birch in London
- **2 Tokens**: Minted for first two trees
- **Health History**: 10 weeks of sample data for first tree

### Sample Login Credentials
```
Username: alice
Password: password123
```

---

## Error Handling

All endpoints return consistent error responses:

```json
{
    "error": "Error message",
    "detail": "Optional detailed message",
    "status_code": 400
}
```

### Common Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

---

## Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/petri_db

# Security
SECRET_KEY=your-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External Services
CARD_GENERATION_SERVICE_URL=http://localhost:8001
HEALTH_SCORING_SERVICE_URL=http://localhost:8002

# Application
DEBUG=True
```

---

## Next Steps

1. **Set up PostgreSQL database**
2. **Configure `.env` file with database credentials**
3. **Run `python -m app.database.init`**
4. **Start server with `uvicorn app.main:app --reload`**
5. **Test endpoints at `http://localhost:8000/docs`**
6. **Coordinate with other roles on API contracts**

---

## Support & Troubleshooting

### Database Connection Error
- Ensure PostgreSQL is running
- Check `DATABASE_URL` in `.env`
- Verify database exists

### Port Already in Use
```bash
# Change port
uvicorn app.main:app --port 8001
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

---

**Last Updated**: November 9, 2024
