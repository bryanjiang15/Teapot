# TCG Game Engine - Detailed Implementation Plan

## Overview

This document provides a detailed implementation plan for building a server-authoritative TCG game engine with Python backend, Unity WebGL client, and React creator tools. Each phase includes technical specifications, timelines, integration points, and testing strategies.

---

## Phase 1: Server-Authoritative Backend (2-3 weeks)

### 1.1 Core Infrastructure Setup (Week 1)

#### **What it is:**
Foundation layer providing authentication, database connections, and basic API structure.

#### **Tech Stack:**
- **FastAPI** with WebSocket support
- **PostgreSQL** for persistent data
- **Redis** for live state and pub/sub
- **JWT** for authentication
- **Pydantic** for data validation
- **SQLAlchemy** for ORM
- **Alembic** for migrations

#### **Timeline:** 5 days

#### **Components to Build:**

**Database Schema:**
Example data modals to have
```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Rulesets table
CREATE TABLE rulesets (
    id UUID PRIMARY KEY,
    owner_id UUID REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    version VARCHAR(50) NOT NULL,
    schema JSONB NOT NULL,
    status VARCHAR(50) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Cards table
CREATE TABLE cards (
    id UUID PRIMARY KEY,
    ruleset_id UUID REFERENCES rulesets(id),
    name VARCHAR(255) NOT NULL,
    data JSONB NOT NULL,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Matches table
CREATE TABLE matches (
    id UUID PRIMARY KEY,
    ruleset_version VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'lobby',
    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    ended_at TIMESTAMP
);

-- Match events (event sourcing)
CREATE TABLE match_events (
    match_id UUID REFERENCES matches(id),
    version INTEGER NOT NULL,
    step INTEGER NOT NULL,
    event_data JSONB NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (match_id, version, step)
);

-- Match snapshots
CREATE TABLE match_snapshots (
    match_id UUID REFERENCES matches(id),
    version INTEGER NOT NULL,
    state_data JSONB NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (match_id, version)
);
```

**FastAPI Application Structure:**
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── jwt_handler.py
│   │   └── password.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── match.py
│   │   └── card.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── match.py
│   │   └── card.py
│   └── api/
│       ├── __init__.py
│       ├── auth.py
│       ├── matches.py
│       └── cards.py
├── migrations/
├── tests/
└── requirements.txt
```

#### **Integration Points:**
- PostgreSQL connection via SQLAlchemy
- Redis connection for caching and pub/sub
- JWT middleware for protected routes
- CORS configuration for React frontend

#### **Testing Plan:**
- **Unit Tests:** Database models, auth functions, JWT handling
- **Integration Tests:** API endpoints with test database
- **Security Tests:** Password hashing, JWT validation, SQL injection
- **Performance Tests:** Database connection pooling, Redis operations

**Test Coverage Target:** 80%

---

### 1.2 Event Sourcing System (Week 2)

#### **What it is:**
Core game logic system that processes actions into events and maintains game state.

#### **Tech Stack:**
- **asyncio** for concurrent match processing
- **Redis** for match state caching
- **PostgreSQL** for event persistence
- **Pydantic** for event validation
- **UUID** for unique identifiers

#### **Timeline:** 7 days

#### **Components to Build:**

**Core Domain Models:**
```python
# schemas/match.py
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from enum import Enum

class MatchPhase(str, Enum):
    LOBBY = "LOBBY"
    PLAY = "PLAY"
    END = "END"

class MatchState(BaseModel):
    match_id: str
    version: int
    ruleset_version: str
    rng_seed: str
    phase: MatchPhase
    turn: int
    active_player: str
    players: Dict[str, Dict[str, Any]]
    board: Dict[str, Any]
    stack: List[Dict[str, Any]]

class Action(BaseModel):
    action_id: str
    match_id: str
    player_id: str
    type: str
    payload: Dict[str, Any]
    client_seq: int
    known_version: Optional[int] = None

class Event(BaseModel):
    event_id: str
    match_id: str
    version: int
    step: int
    resolution_id: str
    type: str
    data: Dict[str, Any]
    timestamp: str
    requires_ack: bool = False
    state_diff: Optional[Dict[str, Any]] = None
```

**Match Actor System:**
```python
# core/match_actor.py
import asyncio
import uuid
from typing import List, Dict, Any
from datetime import datetime

class MatchActor:
    def __init__(self, match_id: str):
        self.match_id = match_id
        self.state: Optional[MatchState] = None
        self.queue = asyncio.Queue()
        self.connections: List[WebSocket] = []
    
    async def process_action(self, action: Action) -> List[Event]:
        # Load current state
        self.state = await self.load_state()
        
        # Validate action
        if not self.validate_action(action):
            raise ValueError("Invalid action")
        
        # Generate events
        events = await self.generate_events(action)
        
        # Apply state changes
        await self.apply_events(events)
        
        # Persist events
        await self.persist_events(events)
        
        # Broadcast to clients
        await self.broadcast_events(events)
        
        return events
    
    async def generate_events(self, action: Action) -> List[Event]:
        events = []
        resolution_id = str(uuid.uuid4())
        step = 0
        
        if action.type == "ATTACK":
            events.extend(await self.handle_attack(action, resolution_id, step))
        elif action.type == "PLAY_CARD":
            events.extend(await self.handle_play_card(action, resolution_id, step))
        
        return events
```

#### **Integration Points:**
- Redis for live state storage
- PostgreSQL for event persistence
- WebSocket connections for real-time updates
- Deterministic RNG system

#### **Testing Plan:**
- **Unit Tests:** Action validation, event generation, state updates
- **Integration Tests:** Full action → event → state flow
- **Property Tests:** Random action generation and validation
- **Concurrency Tests:** Multiple actions on same match

**Test Coverage Target:** 85%

---

### 1.3 WebSocket Communication (Week 3)

#### **What it is:**
Real-time bidirectional communication between server and clients.

#### **Tech Stack:**
- **FastAPI WebSocket** for real-time communication
- **Redis Pub/Sub** for message broadcasting
- **asyncio** for concurrent connections
- **JSON** for message serialization

#### **Timeline:** 5 days

#### **Components to Build:**

**WebSocket Handler:**
```python
# api/websocket.py
from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.redis_client = redis.Redis()
    
    async def connect(self, websocket: WebSocket, match_id: str, player_id: str):
        await websocket.accept()
        if match_id not in self.active_connections:
            self.active_connections[match_id] = []
        self.active_connections[match_id].append(websocket)
        
        # Subscribe to Redis pub/sub
        await self.redis_client.subscribe(f"match:{match_id}")
    
    async def disconnect(self, websocket: WebSocket, match_id: str):
        if match_id in self.active_connections:
            self.active_connections[match_id].remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast_to_match(self, message: str, match_id: str):
        if match_id in self.active_connections:
            for connection in self.active_connections[match_id]:
                await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/matches/{match_id}")
async def websocket_endpoint(websocket: WebSocket, match_id: str):
    await manager.connect(websocket, match_id, "player1")
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "ACTION":
                action = Action(**message["action"])
                events = await match_actor.process_action(action)
                
                # Send events back to all clients
                for event in events:
                    await manager.broadcast_to_match(
                        json.dumps(event.dict()), match_id
                    )
            
            elif message["type"] == "FLOW_ACK":
                # Handle flow control acknowledgment
                await handle_flow_ack(message)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, match_id)
```

#### **Integration Points:**
- Match Actor for action processing
- Redis for pub/sub messaging
- Client reconnection handling
- Flow control with ACKs

#### **Testing Plan:**
- **Unit Tests:** WebSocket connection handling, message parsing
- **Integration Tests:** Full client-server communication
- **Load Tests:** Multiple concurrent connections
- **Reconnection Tests:** Client disconnect/reconnect scenarios

**Test Coverage Target:** 75%

---

## Phase 2: Unity Client Refactor (1-2 weeks)

### 2.1 Remove Game Logic from Unity (Week 1)

#### **What it is:**
Refactor Unity client to be a thin rendering layer that receives events and displays animations.

#### **Tech Stack:**
- **Unity WebGL** for browser deployment
- **WebSocket Client** for server communication
- **Unity Coroutines** for animation sequencing
- **Unity Events** for decoupled communication

#### **Timeline:** 5 days

#### **Components to Build:**

**WebSocket Client:**
```csharp
// Scripts/Network/WebSocketClient.cs
using System;
using System.Collections;
using UnityEngine;
using WebSocketSharp;

public class WebSocketClient : MonoBehaviour
{
    private WebSocket ws;
    private string matchId;
    private bool connected = false;
    
    public event Action<GameEvent> OnEventReceived;
    public event Action OnConnected;
    public event Action OnDisconnected;
    
    public void Connect(string serverUrl, string matchId)
    {
        this.matchId = matchId;
        ws = new WebSocket(serverUrl);
        
        ws.OnOpen += (sender, e) => {
            connected = true;
            OnConnected?.Invoke();
        };
        
        ws.OnMessage += (sender, e) => {
            var gameEvent = JsonUtility.FromJson<GameEvent>(e.Data);
            OnEventReceived?.Invoke(gameEvent);
        };
        
        ws.OnClose += (sender, e) => {
            connected = false;
            OnDisconnected?.Invoke();
        };
        
        ws.Connect();
    }
    
    public void SendAction(GameAction action)
    {
        if (connected)
        {
            var json = JsonUtility.ToJson(action);
            ws.Send(json);
        }
    }
}
```

**Event Animation System:**
```csharp
// Scripts/Animation/EventAnimator.cs
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class EventAnimator : MonoBehaviour
{
    private Queue<GameEvent> eventQueue = new Queue<GameEvent>();
    private bool isAnimating = false;
    
    public void QueueEvent(GameEvent gameEvent)
    {
        eventQueue.Enqueue(gameEvent);
        if (!isAnimating)
        {
            StartCoroutine(ProcessEventQueue());
        }
    }
    
    private IEnumerator ProcessEventQueue()
    {
        isAnimating = true;
        
        while (eventQueue.Count > 0)
        {
            var gameEvent = eventQueue.Dequeue();
            yield return StartCoroutine(AnimateEvent(gameEvent));
            
            if (gameEvent.requiresAck)
            {
                SendAck(gameEvent);
            }
        }
        
        isAnimating = false;
    }
    
    private IEnumerator AnimateEvent(GameEvent gameEvent)
    {
        switch (gameEvent.type)
        {
            case "ACTION_BEGIN":
                yield return StartCoroutine(HighlightActors(gameEvent.data));
                break;
            case "ATTACK_DECLARED":
                yield return StartCoroutine(ShowAttackAnimation(gameEvent.data));
                break;
            case "DAMAGE_APPLIED":
                yield return StartCoroutine(ShowDamageEffect(gameEvent.data));
                break;
            case "CARD_DRAWN":
                yield return StartCoroutine(AnimateCardDraw(gameEvent.data));
                break;
        }
    }
}
```

#### **Integration Points:**
- WebSocket connection to backend
- Event queue for animation sequencing
- State diff application system
- Input collection for user actions

#### **Testing Plan:**
- **Unit Tests:** Event parsing, animation triggers
- **Integration Tests:** WebSocket communication
- **Visual Tests:** Animation playback verification
- **Performance Tests:** Frame rate during animations

**Test Coverage Target:** 70%

---

### 2.2 State Management System (Week 2)

#### **What it is:**
Client-side state mirror that applies server diffs and maintains local game state.

#### **Tech Stack:**
- **Unity ScriptableObjects** for state management
- **Unity Events** for state change notifications
- **JSON** for state serialization

#### **Timeline:** 5 days

#### **Components to Build:**

**Game State Manager:**
```csharp
// Scripts/State/GameStateManager.cs
using System;
using UnityEngine;
using System.Collections.Generic;

[CreateAssetMenu(fileName = "GameState", menuName = "Game/State")]
public class GameState : ScriptableObject
{
    public string matchId;
    public int version;
    public string phase;
    public int turn;
    public string activePlayer;
    public Dictionary<string, PlayerState> players;
    public Dictionary<string, object> board;
    
    public event Action<GameState> OnStateChanged;
    
    public void ApplyDiff(Dictionary<string, object> diff)
    {
        // Apply state differences
        foreach (var change in diff)
        {
            ApplyChange(change.Key, change.Value);
        }
        
        OnStateChanged?.Invoke(this);
    }
    
    private void ApplyChange(string path, object value)
    {
        // Apply specific state change
        // Implementation depends on state structure
    }
}
```

#### **Integration Points:**
- WebSocket client for receiving events
- Animation system for visual updates
- Input system for user actions

#### **Testing Plan:**
- **Unit Tests:** State diff application, change notifications
- **Integration Tests:** State synchronization with server
- **Visual Tests:** State change visual feedback

**Test Coverage Target:** 75%

---

## Phase 3: Basic Match Flow (1 week)

### 3.1 Simple Game Rules Implementation

#### **What it is:**
Core game mechanics including turn system, card play, combat, and basic zones.

#### **Tech Stack:**
- **Python** for game logic
- **Pydantic** for rule validation
- **asyncio** for concurrent processing

#### **Timeline:** 5 days

#### **Components to Build:**

**Game Rules Engine:**
```python
# core/game_rules.py
from typing import Dict, List, Any
from enum import Enum

class Zone(str, Enum):
    HAND = "hand"
    FIELD = "field"
    DECK = "deck"
    GRAVEYARD = "graveyard"

class GameRules:
    def __init__(self, ruleset_version: str):
        self.ruleset_version = ruleset_version
        self.zones = [Zone.HAND, Zone.FIELD, Zone.DECK, Zone.GRAVEYARD]
    
    async def validate_action(self, state: MatchState, action: Action) -> bool:
        if action.type == "PLAY_CARD":
            return await self.validate_play_card(state, action)
        elif action.type == "ATTACK":
            return await self.validate_attack(state, action)
        return False
    
    async def validate_play_card(self, state: MatchState, action: Action) -> bool:
        card_id = action.payload["card_id"]
        player_id = action.player_id
        
        # Check if player has the card
        if not self.has_card(state, player_id, card_id):
            return False
        
        # Check if player has enough resources
        if not self.can_afford(state, player_id, card_id):
            return False
        
        return True
    
    async def process_play_card(self, state: MatchState, action: Action) -> List[Event]:
        events = []
        card_id = action.payload["card_id"]
        player_id = action.player_id
        
        # Move card from hand to field
        events.append(Event(
            type="CARD_PLAYED",
            data={"card_id": card_id, "player": player_id}
        ))
        
        # Apply card effects
        card_effects = await self.get_card_effects(card_id)
        for effect in card_effects:
            events.append(Event(
                type="EFFECT_APPLIED",
                data={"effect": effect, "source": card_id}
            ))
        
        return events
```

#### **Integration Points:**
- Match Actor for event processing
- Database for card data
- Validation system for rule checking

#### **Testing Plan:**
- **Unit Tests:** Rule validation, action processing
- **Integration Tests:** Full game flow
- **Property Tests:** Random valid actions
- **Edge Case Tests:** Invalid actions, boundary conditions

**Test Coverage Target:** 90%

---

### 3.2 Bot Testing System

#### **What it is:**
Automated testing system using AI bots to validate game logic.

#### **Tech Stack:**
- **Python** for bot logic
- **asyncio** for concurrent bot execution
- **pytest** for test framework

#### **Timeline:** 3 days

#### **Components to Build:**

**Simple AI Bot:**
```python
# testing/bot.py
import asyncio
import random
from typing import List, Dict, Any

class SimpleBot:
    def __init__(self, player_id: str):
        self.player_id = player_id
        self.actions_taken = 0
    
    async def get_action(self, state: MatchState) -> Action:
        # Simple random action selection
        available_actions = await self.get_available_actions(state)
        
        if not available_actions:
            return Action(
                action_id=str(uuid.uuid4()),
                match_id=state.match_id,
                player_id=self.player_id,
                type="END_TURN",
                payload={},
                client_seq=self.actions_taken
            )
        
        action = random.choice(available_actions)
        self.actions_taken += 1
        return action
    
    async def get_available_actions(self, state: MatchState) -> List[Action]:
        actions = []
        
        # Add play card actions
        for card_id in state.players[self.player_id]["hand"]:
            actions.append(Action(
                action_id=str(uuid.uuid4()),
                match_id=state.match_id,
                player_id=self.player_id,
                type="PLAY_CARD",
                payload={"card_id": card_id},
                client_seq=self.actions_taken
            ))
        
        return actions
```

#### **Integration Points:**
- Match Actor for action processing
- Game Rules for validation
- Event system for state updates

#### **Testing Plan:**
- **Bot Tests:** Bot action selection, game completion
- **Stress Tests:** Multiple bots in same match
- **Regression Tests:** Bot behavior consistency
- **Performance Tests:** Bot response times

**Test Coverage Target:** 80%

---

## Phase 4: Python Sandbox Integration (1-2 weeks)

### 4.1 Lua Sandbox Implementation

#### **What it is:**
Secure Python execution environment for custom card abilities.

#### **Tech Stack:**
- **restrictedpython** for sandboxing
- **asyncio** for async ability execution
- **ast** for code analysis
- **timeout** for execution limits

#### **Timeline:** 7 days

#### **Components to Build:**

**Python Sandbox:**
```python
# core/python_sandbox.py
import ast
import asyncio
import time
from restrictedpython import compile_restricted
from typing import Dict, Any, List

class PythonSandbox:
    def __init__(self):
        self.safe_globals = {
            'draw_card': self.draw_card,
            'deal_damage': self.deal_damage,
            'get_entity': self.get_entity,
            'create_effect': self.create_effect,
            'wait_for_trigger': self.wait_for_trigger,
        }
        self.execution_timeout = 1.0  # 1 second max
        self.memory_limit = 1024 * 1024  # 1MB max
    
    async def execute_ability(self, code: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            # Compile with restrictions
            compiled = compile_restricted(code, '<ability>', 'exec')
            
            # Create execution context
            exec_context = {
                **self.safe_globals,
                **context,
                'effects': []
            }
            
            # Execute with timeout
            start_time = time.time()
            exec(compiled, exec_context)
            
            if time.time() - start_time > self.execution_timeout:
                raise TimeoutError("Ability execution timeout")
            
            return exec_context.get('effects', [])
            
        except Exception as e:
            raise ValueError(f"Ability execution failed: {str(e)}")
    
    def draw_card(self, player_id: str, count: int = 1):
        # Safe API for drawing cards
        return {"type": "draw_card", "player": player_id, "count": count}
    
    def deal_damage(self, target: str, amount: int):
        # Safe API for dealing damage
        return {"type": "deal_damage", "target": target, "amount": amount}
```

#### **Integration Points:**
- Match Actor for ability execution
- Game Rules for validation
- Event system for effect application

#### **Testing Plan:**
- **Security Tests:** Sandbox escape attempts
- **Performance Tests:** Execution time limits
- **Functionality Tests:** Ability execution correctness
- **Edge Case Tests:** Malicious code, infinite loops

**Test Coverage Target:** 95%

---

### 4.2 AI Integration

#### **What it is:**
Integration with existing OpenAI API for card and ability generation.

#### **Tech Stack:**
- **OpenAI API** for AI generation
- **FastAPI** for API endpoints
- **Pydantic** for request/response validation
- **asyncio** for async processing

#### **Timeline:** 5 days

#### **Components to Build:**

**AI Generation Service:**
```python
# services/ai_generation.py
import openai
from typing import Dict, Any, List
import asyncio

class AIGenerationService:
    def __init__(self, api_key: str):
        self.client = openai.AsyncOpenAI(api_key=api_key)
    
    async def generate_card(self, prompt: str) -> Dict[str, Any]:
        response = await self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a TCG card designer. Generate cards in JSON format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        # Parse and validate response
        card_data = self.parse_card_response(response.choices[0].message.content)
        return card_data
    
    async def generate_ability(self, card_description: str) -> str:
        response = await self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a Python developer. Generate safe Python code for TCG abilities."},
                {"role": "user", "content": f"Create Python code for: {card_description}"}
            ],
            temperature=0.5
        )
        
        return response.choices[0].message.content
    
    def parse_card_response(self, response: str) -> Dict[str, Any]:
        # Parse AI response into card data
        # Implementation depends on AI response format
        pass
```

#### **Integration Points:**
- OpenAI API for generation
- Python Sandbox for validation
- Database for storing generated content

#### **Testing Plan:**
- **Unit Tests:** AI response parsing, validation
- **Integration Tests:** Full generation pipeline
- **Quality Tests:** Generated content quality
- **Rate Limit Tests:** API usage limits

**Test Coverage Target:** 80%

---

## Phase 5: React Creator Tools (2-3 weeks)

### 5.1 Card Editor Interface (Week 1)

#### **What it is:**
React-based interface for creating and editing TCG cards.

#### **Tech Stack:**
- **React** with TypeScript
- **Tailwind CSS** for styling
- **React Hook Form** for form handling
- **Monaco Editor** for code editing

#### **Timeline:** 7 days

#### **Components to Build:**

**Card Editor Component:**
```tsx
// components/CardEditor.tsx
import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import MonacoEditor from '@monaco-editor/react';

interface CardData {
  name: string;
  cost: number;
  stats: {
    attack: number;
    health: number;
  };
  text: string;
  abilities: Array<{
    id: string;
    trigger: string;
    python: string;
  }>;
}

export const CardEditor: React.FC = () => {
  const [cardData, setCardData] = useState<CardData>({
    name: '',
    cost: 0,
    stats: { attack: 0, health: 0 },
    text: '',
    abilities: []
  });

  const { register, handleSubmit, watch } = useForm<CardData>();

  const onSubmit = async (data: CardData) => {
    try {
      const response = await fetch('/api/cards', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      
      if (response.ok) {
        console.log('Card saved successfully');
      }
    } catch (error) {
      console.error('Error saving card:', error);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <div>
          <label className="block text-sm font-medium mb-2">Card Name</label>
          <input
            {...register('name')}
            className="w-full p-2 border rounded"
            placeholder="Enter card name"
          />
        </div>
        
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">Cost</label>
            <input
              {...register('cost', { valueAsNumber: true })}
              type="number"
              className="w-full p-2 border rounded"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Attack</label>
            <input
              {...register('stats.attack', { valueAsNumber: true })}
              type="number"
              className="w-full p-2 border rounded"
            />
          </div>
        </div>
        
        <div>
          <label className="block text-sm font-medium mb-2">Card Text</label>
          <textarea
            {...register('text')}
            className="w-full p-2 border rounded h-20"
            placeholder="Enter card description"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium mb-2">Python Ability</label>
          <MonacoEditor
            height="300px"
            language="python"
            value={cardData.abilities[0]?.python || ''}
            onChange={(value) => {
              setCardData(prev => ({
                ...prev,
                abilities: [{
                  id: 'ability_1',
                  trigger: 'ON_PLAY',
                  python: value || ''
                }]
              }));
            }}
            options={{
              minimap: { enabled: false },
              fontSize: 14,
              lineNumbers: 'on',
              roundedSelection: false,
              scrollBeyondLastLine: false,
              automaticLayout: true,
            }}
          />
        </div>
        
        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700"
        >
          Save Card
        </button>
      </form>
    </div>
  );
};
```

#### **Integration Points:**
- Backend API for card storage
- Monaco Editor for Python editing
- Form validation and submission

#### **Testing Plan:**
- **Unit Tests:** Component rendering, form handling
- **Integration Tests:** API communication
- **User Tests:** Form validation, error handling
- **Accessibility Tests:** Keyboard navigation, screen readers

**Test Coverage Target:** 85%

---

### 5.2 Deck Builder Interface (Week 2)

#### **What it is:**
Drag-and-drop interface for building card decks.

#### **Tech Stack:**
- **React** with TypeScript
- **React DnD** for drag and drop
- **Tailwind CSS** for styling
- **Zustand** for state management

#### **Timeline:** 7 days

#### **Components to Build:**

**Deck Builder Component:**
```tsx
// components/DeckBuilder.tsx
import React, { useState } from 'react';
import { DndProvider, useDrag, useDrop } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';

interface Card {
  id: string;
  name: string;
  cost: number;
  imageUrl: string;
}

interface DeckBuilderProps {
  availableCards: Card[];
  deckCards: Card[];
  onDeckChange: (cards: Card[]) => void;
}

export const DeckBuilder: React.FC<DeckBuilderProps> = ({
  availableCards,
  deckCards,
  onDeckChange
}) => {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredCards = availableCards.filter(card =>
    card.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <DndProvider backend={HTML5Backend}>
      <div className="flex h-screen">
        {/* Available Cards */}
        <div className="w-1/2 p-4 border-r">
          <h2 className="text-xl font-bold mb-4">Available Cards</h2>
          <input
            type="text"
            placeholder="Search cards..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full p-2 border rounded mb-4"
          />
          <div className="grid grid-cols-2 gap-2">
            {filteredCards.map(card => (
              <CardItem key={card.id} card={card} type="available" />
            ))}
          </div>
        </div>
        
        {/* Deck */}
        <div className="w-1/2 p-4">
          <h2 className="text-xl font-bold mb-4">Deck ({deckCards.length})</h2>
          <div className="grid grid-cols-2 gap-2">
            {deckCards.map(card => (
              <CardItem key={card.id} card={card} type="deck" />
            ))}
          </div>
        </div>
      </div>
    </DndProvider>
  );
};

const CardItem: React.FC<{ card: Card; type: 'available' | 'deck' }> = ({ card, type }) => {
  const [{ isDragging }, drag] = useDrag(() => ({
    type: 'card',
    item: { card, source: type },
    collect: (monitor) => ({
      isDragging: monitor.isDragging(),
    }),
  }));

  const [{ isOver }, drop] = useDrop(() => ({
    accept: 'card',
    drop: (item: { card: Card; source: string }) => {
      // Handle drop logic
    },
    collect: (monitor) => ({
      isOver: monitor.isOver(),
    }),
  }));

  return (
    <div
      ref={(node) => drag(drop(node))}
      className={`p-2 border rounded cursor-move ${
        isDragging ? 'opacity-50' : ''
      } ${isOver ? 'bg-blue-100' : ''}`}
    >
      <img src={card.imageUrl} alt={card.name} className="w-full h-32 object-cover" />
      <div className="mt-2">
        <h3 className="font-semibold">{card.name}</h3>
        <p className="text-sm text-gray-600">Cost: {card.cost}</p>
      </div>
    </div>
  );
};
```

#### **Integration Points:**
- Card database for available cards
- Deck storage API
- Drag and drop functionality

#### **Testing Plan:**
- **Unit Tests:** Component rendering, drag/drop logic
- **Integration Tests:** API communication
- **User Tests:** Drag and drop functionality
- **Performance Tests:** Large card collections

**Test Coverage Target:** 80%

---

### 5.3 AI Assist Panel (Week 3)

#### **What it is:**
AI-powered assistance for card and ability generation.

#### **Tech Stack:**
- **React** with TypeScript
- **OpenAI API** for AI generation
- **Monaco Editor** for code editing
- **Tailwind CSS** for styling

#### **Timeline:** 7 days

#### **Components to Build:**

**AI Assist Panel:**
```tsx
// components/AIAssistPanel.tsx
import React, { useState } from 'react';
import MonacoEditor from '@monaco-editor/react';

interface AIAssistPanelProps {
  onCardGenerated: (card: any) => void;
  onAbilityGenerated: (ability: string) => void;
}

export const AIAssistPanel: React.FC<AIAssistPanelProps> = ({
  onCardGenerated,
  onAbilityGenerated
}) => {
  const [prompt, setPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedCode, setGeneratedCode] = useState('');

  const generateCard = async () => {
    setIsGenerating(true);
    try {
      const response = await fetch('/api/ai/cards/suggest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt })
      });
      
      const data = await response.json();
      onCardGenerated(data.card);
    } catch (error) {
      console.error('Error generating card:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const generateAbility = async () => {
    setIsGenerating(true);
    try {
      const response = await fetch('/api/ai/abilities/suggest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt })
      });
      
      const data = await response.json();
      setGeneratedCode(data.python);
      onAbilityGenerated(data.python);
    } catch (error) {
      console.error('Error generating ability:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-6">
      <h2 className="text-2xl font-bold mb-6">AI Assist Panel</h2>
      
      <div className="space-y-6">
        <div>
          <label className="block text-sm font-medium mb-2">Describe what you want to create:</label>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            className="w-full p-3 border rounded h-24"
            placeholder="e.g., 'A fire dragon that deals damage when it attacks'"
          />
        </div>
        
        <div className="flex space-x-4">
          <button
            onClick={generateCard}
            disabled={isGenerating}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {isGenerating ? 'Generating...' : 'Generate Card'}
          </button>
          
          <button
            onClick={generateAbility}
            disabled={isGenerating}
            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
          >
            {isGenerating ? 'Generating...' : 'Generate Ability'}
          </button>
        </div>
        
        {generatedCode && (
          <div>
            <label className="block text-sm font-medium mb-2">Generated Python Code:</label>
            <MonacoEditor
              height="300px"
              language="python"
              value={generatedCode}
              options={{
                readOnly: true,
                minimap: { enabled: false },
                fontSize: 14,
                lineNumbers: 'on',
              }}
            />
          </div>
        )}
      </div>
    </div>
  );
};
```

#### **Integration Points:**
- OpenAI API for generation
- Card editor for integration
- Ability validation system

#### **Testing Plan:**
- **Unit Tests:** Component rendering, API calls
- **Integration Tests:** AI generation pipeline
- **User Tests:** Prompt handling, result display
- **Quality Tests:** Generated content validation

**Test Coverage Target:** 75%

---

## Testing Strategy Overview

### **Testing Pyramid:**

1. **Unit Tests (70% of tests)**
   - Individual component testing
   - Function-level validation
   - Mock external dependencies

2. **Integration Tests (20% of tests)**
   - API endpoint testing
   - Database integration
   - WebSocket communication

3. **End-to-End Tests (10% of tests)**
   - Full user workflows
   - Cross-system integration
   - Performance validation

### **Testing Tools:**

- **Backend:** pytest, pytest-asyncio, httpx
- **Frontend:** Jest, React Testing Library, Cypress
- **Unity:** Unity Test Framework, NUnit
- **Load Testing:** Locust, Artillery

### **Continuous Integration:**

- **GitHub Actions** for automated testing
- **Docker** for consistent environments
- **Code coverage** reporting
- **Performance regression** detection

---

## Deployment Strategy

### **Development Environment:**
- Local development with Docker Compose
- Hot reloading for all services
- Seed data for testing

### **Staging Environment:**
- Kubernetes cluster
- Production-like configuration
- Automated testing pipeline

### **Production Environment:**
- Kubernetes with auto-scaling
- CDN for static assets
- Monitoring and alerting

---

## Risk Mitigation

### **Technical Risks:**
- **Sandbox Security:** Regular security audits, penetration testing
- **Performance:** Load testing, monitoring, optimization
- **Data Loss:** Backup strategies, event sourcing recovery

### **Project Risks:**
- **Scope Creep:** Clear phase boundaries, regular reviews
- **Timeline Delays:** Buffer time, parallel development
- **Team Coordination:** Daily standups, clear communication

---

## Success Metrics

### **Technical Metrics:**
- **Latency:** < 50ms per action (P95)
- **Throughput:** 1k concurrent matches
- **Uptime:** 99.9% availability
- **Test Coverage:** > 80% across all components

### **User Metrics:**
- **Match Completion Rate:** > 95%
- **Creator Tool Usage:** Daily active creators
- **AI Generation Quality:** User satisfaction scores

---

This implementation plan provides a comprehensive roadmap for building the TCG game engine with clear technical specifications, timelines, and testing strategies for each phase.
