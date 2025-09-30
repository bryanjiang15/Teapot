# TeapotAPI - Architecture Documentation

## Overview

TeapotAPI is the server-authoritative backend for the TCG game engine, handling authentication, game logic, real-time communication, and creator tools. This document outlines the API structure, startup requirements, and design patterns.

---

## API Routes Structure

### **Authentication Routes (`/auth`)**
```
POST   /auth/register          # User registration
POST   /auth/login             # User login
POST   /auth/refresh           # Token refresh
POST   /auth/logout            # User logout
GET    /auth/me                # Get current user info
```

### **User Management Routes (`/users`)**
```
GET    /users/{user_id}        # Get user profile
PUT    /users/{user_id}        # Update user profile
GET    /users/{user_id}/decks  # Get user's decks
GET    /users/{user_id}/cards  # Get user's cards
```

### **Ruleset Management Routes (`/rulesets`)**
```
GET    /rulesets               # List all rulesets
POST   /rulesets               # Create new ruleset
GET    /rulesets/{id}          # Get specific ruleset
PUT    /rulesets/{id}          # Update ruleset
DELETE /rulesets/{id}          # Delete ruleset
POST   /rulesets/{id}/publish  # Publish ruleset
GET    /rulesets/{id}/versions # Get ruleset versions
```

### **Card Management Routes (`/cards`)**
```
GET    /cards                  # List cards (with filters)
POST   /cards                  # Create new card
GET    /cards/{id}             # Get specific card
PUT    /cards/{id}             # Update card
DELETE /cards/{id}             # Delete card
POST   /cards/{id}/validate    # Validate card abilities
```

### **Deck Management Routes (`/decks`)**
```
GET    /decks                  # List user's decks
POST   /decks                  # Create new deck
GET    /decks/{id}             # Get specific deck
PUT    /decks/{id}             # Update deck
DELETE /decks/{id}              # Delete deck
POST   /decks/{id}/validate    # Validate deck legality
```

### **Match Management Routes (`/matches`)**
```
GET    /matches                # List matches (with filters)
POST   /matches                # Create new match
GET    /matches/{id}           # Get match details
POST   /matches/{id}/join      # Join match
POST   /matches/{id}/leave     # Leave match
GET    /matches/{id}/state     # Get current match state
GET    /matches/{id}/replay    # Get match replay
```

### **WebSocket Routes**
```
WS     /ws/matches/{id}        # Real-time match communication
WS     /ws/lobby               # Lobby updates
WS     /ws/notifications       # User notifications
```

### **AI Generation Routes (`/ai`)**
```
POST   /ai/cards/suggest       # Generate card suggestions
POST   /ai/abilities/suggest   # Generate ability code
POST   /ai/validate            # Validate generated code
POST   /ai/test                # Test ability in sandbox
```

### **Moderation Routes (`/mod`)**
```
GET    /mod/rulesets           # List rulesets for review
POST   /mod/rulesets/{id}/approve    # Approve ruleset
POST   /mod/rulesets/{id}/reject     # Reject ruleset
GET    /mod/banlist            # Get banlist
POST   /mod/banlist            # Update banlist
```

### **Health & Monitoring Routes**
```
GET    /health                 # Health check
GET    /metrics                # Application metrics
GET    /status                 # System status
```

---

## Startup Requirements

### **1. Environment Configuration**
```python
# Required environment variables
DATABASE_URL=postgresql://user:pass@localhost:5432/tcg_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-key
ENVIRONMENT=development|staging|production
```

### **2. Database Initialization**
```python
# Database setup tasks
- Create database tables (users, rulesets, cards, matches, events)
- Run Alembic migrations
- Create indexes for performance
- Set up connection pooling
```

### **3. Redis Configuration**
```python
# Redis setup tasks
- Configure connection pool
- Set up pub/sub channels
- Configure memory limits
- Set up persistence settings
```

### **4. Application Startup Sequence**
```python
async def startup():
    # 1. Load configuration
    config = load_config()
    
    # 2. Initialize database
    await init_database()
    
    # 3. Initialize Redis
    await init_redis()
    
    # 4. Load game rules
    await load_rulesets()
    
    # 5. Start background tasks
    await start_background_tasks()
    
    # 6. Initialize WebSocket manager
    await init_websocket_manager()
    
    # 7. Start match actors
    await start_match_actors()
```

### **5. Background Tasks**
```python
# Required background tasks
- Event persistence worker
- Match cleanup worker
- Metrics collection
- Health monitoring
- AI generation queue processor
```

---

## Design Pattern Analysis

### **1. Repository Pattern**
**Use Case**: Data access abstraction
```python
# Pros: Clean separation, testable, flexible
# Cons: Additional complexity
# Verdict: ✅ RECOMMENDED for database operations

class MatchRepository:
    async def get_match(self, match_id: str) -> Match:
        pass
    
    async def save_match(self, match: Match) -> None:
        pass
```

### **2. Actor Pattern**
**Use Case**: Match state management
```python
# Pros: Encapsulation, concurrency, fault isolation
# Cons: Message passing overhead
# Verdict: ✅ RECOMMENDED for match actors

class MatchActor:
    def __init__(self, match_id: str):
        self.match_id = match_id
        self.state = None
        self.queue = asyncio.Queue()
    
    async def process_action(self, action: Action):
        pass
```

### **3. Event Sourcing Pattern**
**Use Case**: Game state management
```python
# Pros: Audit trail, replay capability, scalability
# Cons: Complexity, storage overhead
# Verdict: ✅ RECOMMENDED for game state

class EventStore:
    async def append_events(self, events: List[Event]):
        pass
    
    async def get_events(self, match_id: str) -> List[Event]:
        pass
```

### **4. Model-View-Controller (MVC)**
**Use Case**: API structure and data flow
```python
# Pros: Clear separation, testable, familiar
# Cons: Can become bloated, tight coupling
# Verdict: ✅ RECOMMENDED for API structure

class MatchController:
    def __init__(self, match_service: MatchService):
        self.match_service = match_service
    
    async def create_match(self, request: CreateMatchRequest):
        match = await self.match_service.create_match(request.ruleset_id)
        return MatchResponse.from_domain(match)
```

### **5. Observer Pattern**
**Use Case**: Event broadcasting
```python
# Pros: Decoupling, flexibility
# Cons: Memory leaks, debugging difficulty
# Verdict: ✅ RECOMMENDED for WebSocket broadcasting

class EventObserver:
    def notify(self, event: Event):
        pass
```

### **6. Factory Pattern**
**Use Case**: Object creation
```python
# Pros: Encapsulation, flexibility
# Cons: Over-engineering for simple cases
# Verdict: ✅ RECOMMENDED for match creation

class MatchFactory:
    @staticmethod
    def create_match(ruleset_id: str, players: List[str]) -> Match:
        pass
```

### **7. Strategy Pattern**
**Use Case**: Game rules implementation
```python
# Pros: Flexibility, extensibility
# Cons: Complexity
# Verdict: ✅ RECOMMENDED for different game modes

class GameRulesStrategy:
    async def validate_action(self, action: Action) -> bool:
        pass

class StandardRules(GameRulesStrategy):
    pass

class DraftRules(GameRulesStrategy):
    pass
```

---

## Recommended Architecture

### **Core Patterns to Implement:**

1. **Repository Pattern** - For data access
2. **Actor Pattern** - For match management
3. **Event Sourcing** - For game state
4. **Observer Pattern** - For real-time updates
5. **Factory Pattern** - For object creation
6. **Strategy Pattern** - For game rules
7. **MVC Pattern** - For API structure

### **Pattern Implementation Priority:**

```
High Priority:
- Repository Pattern (data access)
- Actor Pattern (match management)
- Event Sourcing (game state)

Medium Priority:
- Observer Pattern (WebSocket broadcasting)
- Strategy Pattern (game rules)
- MVC Pattern (API structure)

Low Priority:
- Factory Pattern (object creation)
```

### **Anti-Patterns to Avoid:**

- **God Object**: Don't put everything in one class
- **Anemic Domain Model**: Keep business logic in domain objects
- **Tight Coupling**: Use dependency injection
- **Premature Optimization**: Start simple, optimize later

---

## Simplified Architecture (Repository-First Approach)

### **Phase 1: Simple Service Layer**
```python
# Simple structure without MVC complexity
TeapotAPI/
├── models/           # Domain models
│   ├── user.py
│   ├── match.py
│   └── card.py
├── repositories/     # Data access layer
│   ├── user_repository.py
│   ├── match_repository.py
│   └── card_repository.py
├── services/        # Business logic layer
│   ├── auth_service.py
│   ├── match_service.py
│   └── card_service.py
└── api/             # FastAPI routes (simple)
    ├── auth.py
    ├── matches.py
    └── cards.py
```

### **Simple Data Flow:**
```python
# Direct route → service → repository flow
@app.post("/matches")
async def create_match(request: CreateMatchRequest):
    # Service handles business logic
    match = await match_service.create_match(
        ruleset_id=request.ruleset_id,
        players=request.players
    )
    
    # Repository handles data persistence
    await match_repository.save(match)
    
    # Return simple response
    return {"match_id": match.id, "status": match.status}
```

### **Benefits of Repository-First Approach:**

1. **Simplicity**: Start with what you know (Repository pattern)
2. **Faster Development**: No MVC overhead initially
3. **Easy Testing**: Mock repositories for unit tests
4. **Gradual Evolution**: Add MVC later when needed
5. **Clear Data Flow**: Route → Service → Repository → Database

### **When to Add MVC:**
- When you have 10+ endpoints
- When response formatting becomes complex
- When you need consistent error handling
- When team grows and needs structure

---

## Implementation Timeline

### **Phase 1: Foundation (Week 1)**
- Repository pattern for data access
- Simple service layer (no MVC yet)
- Basic authentication routes
- Database setup and migrations
- Health check endpoints

### **Phase 2: Core Game Logic (Week 2)**
- Actor pattern for match management
- Event sourcing implementation
- WebSocket communication
- Basic match routes

### **Phase 3: Advanced Features (Week 3)**
- Observer pattern for broadcasting
- Factory pattern for match creation
- MVC pattern for API structure
- AI generation routes

### **Phase 4: Optimization (Week 4)**
- Performance monitoring
- Caching strategies
- Load testing
- Security hardening

---

## Success Metrics

### **Technical Metrics:**
- API response time < 50ms (P95)
- WebSocket latency < 10ms
- Database query time < 5ms
- Memory usage < 512MB per instance

### **Business Metrics:**
- Match completion rate > 95%
- User registration conversion > 80%
- Creator tool usage > 50% of users
- System uptime > 99.9%

---

This architecture provides a solid foundation for the TCG game engine with clear patterns, scalable design, and measurable success criteria.
