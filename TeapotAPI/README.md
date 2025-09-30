# TeapotAPI - TCG Game Engine Backend

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set up Environment
```bash
cp env.example .env
# Edit .env with your database and API keys
```

### 3. Run the Server
```bash
python run.py
```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Project Structure

```
TeapotAPI/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── config.py            # Configuration
│   ├── database.py          # Database setup
│   ├── models/              # SQLAlchemy models
│   │   ├── user.py
│   │   ├── match.py
│   │   ├── card.py
│   │   └── ruleset.py
│   ├── schemas/              # Pydantic schemas
│   │   └── user.py
│   ├── repositories/         # Repository pattern
│   │   └── user_repository.py
│   ├── services/            # Business logic
│   │   └── auth_service.py
│   └── api/                 # API routes
│       └── auth.py
├── requirements.txt
├── env.example
└── run.py
```

## Features Implemented

- ✅ FastAPI application setup
- ✅ Database models (User, Match, Card, Ruleset)
- ✅ Repository pattern for data access
- ✅ Authentication service with JWT
- ✅ User registration and login
- ✅ Password hashing with bcrypt
- ✅ CORS middleware
- ✅ Health check endpoint

## Next Steps

1. Add more API endpoints (matches, cards, rulesets)
2. Implement WebSocket support
3. Add Redis integration
4. Implement game logic
5. Add AI generation endpoints