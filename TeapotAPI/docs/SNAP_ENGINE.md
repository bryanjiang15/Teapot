## Snap Engine Design (Event-Driven Rules Engine)

### Goals
- Interpret a Ruleset IR to drive deterministic game logic
- Accept user inputs from the API and translate them into engine events
- Support reactions to any event, recursively, via a single LIFO stack
- Gate progression on required user inputs with resumable state

### Core Concepts
- **Event**: A domain occurrence (e.g., PlayCard, EnterZone, DealDamage). Each event has:
  - id, type, payload, causality (causedBy), timestamp/order, status
- **Reaction**: A rule-driven response attached to an event. Reactions have no intrinsic "pre/post" field:
  - Reactions that must happen before an event resolves are simply pushed above that event on the stack (so they resolve first)
  - Reactions that happen after resolution are discovered when an item finishes and then pushed to the stack
- **StackItem**: A unit scheduled for resolution. Can be an Event or a Reaction.
- **PendingInput**: A request for player choice needed to continue resolution (targets, modes, costs, ordering).
- **Priority**: Opportunity for players to add new actions to the stack between steps.

### Determinism & Replay
- All mutations occur by resolving StackItems into atomic persisted events
- Event sourcing: match state is derived by folding the event log with a specific Ruleset IR version
- Deterministic RNG seeded per match; no wall-clock within resolution

### Engine Lifecycle (High-Level)
1. Load Ruleset IR, initialize state, seed RNG
2. Enter match loop managed by a Match Actor (single-threaded mailbox)
3. Process inbound API messages, producing validated player Actions and translated engine Events
4. Resolve the stack until idle or a PendingInput is emitted
5. Broadcast state/events; persist to event store; await next input or action

### Event Flow and Stack Semantics
- The engine uses a LIFO stack of `StackItem`:
  - Player Actions push one or more Events onto the stack (`timing: stack` or `timing: instant`)
  - Before an Event is allowed to resolve, the engine discovers any reactions that must occur beforehand and pushes them above the Event. When those reactions finish, the Event at the top will resolve. After an item resolves, any after-effects (triggers) are discovered and pushed.

### Priority Windows
- After completing a resolution unit (e.g., after an Event or Reaction resolves and its immediate after-reactions are scheduled), the active priority window opens when the stack is empty
- Players may submit new Actions; validated Actions enqueue as Events on the stack
- If all players pass with an empty stack and no mandatory steps remain, advance phase/turn per TurnStructure in the IR

### User Input Gating
- When resolution requires a choice, the engine emits a `PendingInput` with:
  - inputId, playerId(s) requested, kind (target_select, order_select, mode_pick, pay_cost, confirm), constraints (selectors, counts), timeout policy
- Engine halts resolution and awaits API `input.submit` referencing `inputId` with answers
- Upon receipt, the engine validates answers against constraints and resumes at the paused instruction
- Multiple concurrent `PendingInput`s are supported if independent; otherwise inputs are queued with explicit ordering

### API ↔ Engine Contract (Messages)
- From API to Engine
  - `action.submit`: { matchId, playerId, actionType, params } → translates to Event(s)
  - `input.submit`: { matchId, inputId, answers }
  - `system.control` (moderation, concede, timeout)
- From Engine to API (WS broadcast + persistence)
  - `event.appended`: canonical events with causal links
  - `state.delta`: derived state diffs (optional optimization)
  - `pending.input`: input request with constraints
  - `priority.changed`: who has priority, window info
  - `error`: validation failures (action invalid, input invalid)

### Data Contracts (Sketch)
- Event
  - id: string
  - type: string
  - payload: object
  - causedBy: string | null
  - status: "pending" | "applied" | "prevented" | "failed"
- Reaction
  - id: string
  - when: { eventType, filters }
  - conditions: [Condition]
  - effects: [EffectOp]
- StackItem
  - kind: "event" | "reaction"
  - refId: string (eventId or reactionId instance)
  - createdAtOrder: number (monotonic)
  - flags: { beforeScheduled?: boolean }
- PendingInput
  - inputId: string
  - forPlayerIds: [string]
  - kind: string
  - constraints: object
  - expiresAt: number | null

### Discovery and Ordering
- Reaction discovery uses IR indexes by event type and zone/state predicates
- Ordering rules:
  - Pre-event reactions are discovered when an Event first attempts to resolve and are pushed above it
  - Post-event reactions (post triggers) are discovered once an item resolves and are then pushed
  - Within the same discovery set: active player’s sources first, then others; stable sort by rule id; preserve IR declaration order within a source

### Guardrails
- Max stack depth, max reactions per event, max iterations per effect
- Deterministic RNG via engine context; no system time within resolution
- Static validation of IR at publish; runtime assertion checks in debug builds

### Turn/Phase Integration
- TurnStructure in IR defines steps and mandatory system events (e.g., DrawStep.Start)
- At each step boundary, engine enqueues step-start Events which can be reacted to
- If the stack is empty and all players pass priority, proceed to the next step; emit step-end Events

### Error Handling
- Validation errors on action submission return `error` and do not mutate state
- Runtime contraction violations abort current StackItem, mark as failed, and continue if safe; otherwise pause and require moderator/system input

### Minimal Resolution Loop (Pseudocode)
```text
loop:
  if pendingInput exists: await input.submit
  else if inbox action exists: translate → push Events
  else if stack not empty: resolveTop()
  else if in priority window: if all pass → advance turn/step
  else: open priority window

resolveTop():
  item = stack.pop()
  if item.kind == event:
    if not item.flags.beforeScheduled:
      before = discover_before_reactions(item)
      if before not empty:
        item.flags.beforeScheduled = true
        stack.push(item)
        push_all(stack, before)  # pushed on top so they resolve first
        return
  # apply the item now
  applied = apply(item)  # may emit pendingInput
  if pendingInput: pause
  after = discover_after_reactions(applied)
  push_all(stack, after)
```

### Event Fan-out and Trigger Materialization
- Many effects impact multiple entities (e.g., "deal 1 damage to all cards"). To preserve causality and enable triggers like "When this is damaged, draw a card", the engine performs a fan-out and materialization step.

#### Algorithm
1. Event attempts to resolve: `DealDamage(area=all_cards, amount=1)`
2. Discover and schedule any before-event reactions (e.g., shields/replacements) above it; resolve them first, which may annotate/transform/prevent parts of the damage
3. Compute Affected Set using IR selectors (deterministic ordering by id) after replacements
4. For each affected entity, emit an atomic projection event (e.g., `Damaged { target: card_i, amount: 1, causedBy: sourceEventId }`)
5. Persist projection events and fold them into state
6. Discover after-reactions for each projection event, materialize as stack items, and push in deterministic order

#### Once/Limiters
- Triggers may declare limiters (IR): `oncePerTurn`, `oncePerSource`, `maxPerEvent: N`.
- The engine tracks trigger fire counters keyed by (ruleId, sourceId, scope) to avoid duplicates within the same causal chain

#### Example 1: 
User input to attack an enemy card with their own card -> 
enemy card take damage -> 
enemy card's ability (draw card when damage) trigger ->
ability activate and enemy draw 1 card
Workflow:

1. API receives `action.submit { type: "attack", attackerId, defenderId }` and forwards to engine.
2. Engine validates legality; on success, push `Attack(attackerId, defenderId)` Event to stack.
3. Stack resolves top:
   - pre-reactions for `Attack` (e.g., none) would have been scheduled above if any.
   - Apply `Attack`: compute damage outcome (e.g., defender takes N). Emit atomic domain events:
     - `CombatResolved { attackerId, defenderId, damage }`
     - `Damaged { target: defenderId, amount: N, causedBy: Attack }`
   - Persist events; fold into state.
   - Frontend updates:
     - Broadcast `event.appended` for `CombatResolved`, `Damaged`
     - Broadcast `state.delta` (hp/armor changes, visual damage)
4. After `Damaged` is appended, discover post-reactions that match it (e.g., defender has ability "On Damaged: Draw 1"). Materialize `DrawCard(controller=owner(defenderId), count=1)` Reaction and push to stack.
5. Resolve `DrawCard`:
   - Apply draw; if deck->hand requires revealing or target selection, emit `PendingInput` (not typical for simple draw):
     - If no input required: emit `CardDrawn { playerId, cardId }` and `ZoneMoved { cardId, from: deck, to: hand }`
     - Persist and fold.
   - Frontend updates:
     - Broadcast `event.appended` for draw-related events
     - Broadcast `state.delta` (hand size, known/unknown card visuals per visibility rules)
6. If the stack is empty, open priority window. Broadcast `priority.changed`.

Notes:
- If draw triggers further abilities (e.g., OnDraw), they will be discovered as after-reactions and pushed, repeating steps 5–6.

#### Example 2:
User input to attack ->
Enemy activate an ability that counters the attack ->
Counter succeeds ->
attck gets countered and fail
Workflow:

1. API receives `action.submit { type: "attack", attackerId, defenderId }`; engine validates and pushes `Attack` Event.
2. Priority window before resolution allows opponent to respond:
   - Opponent submits `action.submit { type: "activate_ability", sourceId, abilityId: "CounterAttack" }`.
   - Engine validates and pushes `ActivateAbility(sourceId, CounterAttack)` above `Attack` on the stack.
   - Frontend updates: broadcast `event.appended` for the ability activation intent; optionally a short `state.delta` (e.g., pay costs).
3. Resolve `ActivateAbility(CounterAttack)`:
   - Apply effects that mark the targeted `Attack` as countered/prevented (e.g., set a prevention flag on the `Attack` Event or enqueue a `Counter { targetEventId: Attack }`).
   - Emit `AbilityResolved { sourceId, abilityId }` and any cost/flag events.
   - Persist and fold; broadcast `event.appended` and `state.delta`.
4. The `Attack` Event now attempts to resolve at the top of stack:
   - Engine detects it has been countered/prevented by prior resolution.
   - Mark `Attack` as `prevented`; emit `EventPrevented { eventId: Attack }`.
   - Persist and fold.
   - Frontend updates: broadcast `event.appended` (prevented), `state.delta` (no damage applied), and an animation cue that attack fizzled.
5. Discover after-reactions for `AbilityResolved` or `EventPrevented` if any; schedule and resolve similarly.
6. With stack empty, broadcast `priority.changed`.

Notes:
- All “before” counterplay exists as stack items scheduled above the target event; no separate pre-phase is needed.

#### Example 3:
User attacks ->
Attacks suceed ->
enemy card get damaged and trigger its effect (deal 1 damage to a target card) ->
enemy choose to activate ability and choose a target ->
reaction succeed and damage target card
Workflow:

1. API: `action.submit { type: "attack", attackerId, defenderId }` → push `Attack`.
2. Resolve `Attack` (no counters in this scenario):
   - Emit `CombatResolved` and `Damaged { target: defenderId, amount: N }`.
   - Persist and broadcast `event.appended`, `state.delta`.
3. Discover after-reactions for `Damaged`. Defender has triggered ability: "When damaged, you may deal 1 damage to a target card".
   - Materialize a Reaction `PromptAbility(abilityId, controller=defenderOwner)` because it is optional ("may"). Push to stack.
4. Resolve `PromptAbility`:
   - Emit `PendingInput` for defenderOwner to decide activation and to select target (constraints: selector=tgt:card in battlefield, count=1).
   - Broadcast `pending.input` with UI metadata (prompt text, allowed targets, highlights). Pause resolution.
5. API receives `input.submit { inputId, activate: true, targetId }` (or `activate:false` to decline).
   - Engine validates selection; if valid and activated, push `DealDamage { target: targetId, amount: 1, causedBy: abilityId }`.
   - Broadcast `event.appended` for the newly enqueued effect (optional preview), or wait until apply depending on UX policy.
6. Resolve `DealDamage`:
   - Apply damage and emit `Damaged { target: targetId, amount: 1 }`; persist and broadcast `event.appended`, `state.delta`.
   - Discover after-reactions from this new `Damaged` event (including possible chains); push and resolve as usual.
7. When stack empties, broadcast `priority.changed`.

Frontend communication guidelines for all scenarios:
- On every persisted event: send `event.appended` (for replay and animations).
- After state folds: send `state.delta` with minimal diffs for efficient UI updates.
- When waiting on players: send `pending.input` with full constraints, hints, and highlights.
- When control changes: send `priority.changed`.
- Surface validation failures as `error` with user-friendly messages.

---

## Ruleset-Driven Game Logic

The engine interprets a Ruleset IR to drive all game behavior. Two critical components handle game flow and player interactions:

### 1. Phase System (Game Flow Control)

The ruleset defines how the game progresses from start to end through a structured phase system.

#### Phase Definition in IR
```json
{
  "turnStructure": {
    "phases": [
      {
        "id": "start",
        "name": "Start Phase",
        "steps": [
          { "id": "untap", "name": "Untap Step", "mandatory": true },
          { "id": "upkeep", "name": "Upkeep Step", "mandatory": true },
          { "id": "draw", "name": "Draw Step", "mandatory": true }
        ]
      },
      {
        "id": "main",
        "name": "Main Phase",
        "steps": [
          { "id": "main1", "name": "Main Phase 1", "mandatory": false }
        ]
      },
      {
        "id": "combat",
        "name": "Combat Phase",
        "steps": [
          { "id": "declare_attackers", "name": "Declare Attackers", "mandatory": false },
          { "id": "declare_blockers", "name": "Declare Blockers", "mandatory": false },
          { "id": "combat_damage", "name": "Combat Damage", "mandatory": true }
        ]
      },
      {
        "id": "end",
        "name": "End Phase",
        "steps": [
          { "id": "end", "name": "End Step", "mandatory": true },
          { "id": "cleanup", "name": "Cleanup Step", "mandatory": true }
        ]
      }
    ],
    "priorityWindows": [
      { "phase": "main", "step": "main1" },
      { "phase": "combat", "step": "declare_attackers" },
      { "phase": "combat", "step": "declare_blockers" }
    ]
  }
}
```

#### Phase State Machine
- **Current State**: `{ phase: "main", step: "main1", activePlayer: "p1", turnNumber: 3 }`
- **Transitions**: Engine automatically advances phases/steps based on IR rules
- **Mandatory Steps**: Cannot be skipped; engine forces progression
- **Optional Steps**: Players can pass priority to skip
- **System Events**: Each step transition emits `StepStart` and `StepEnd` events

#### Phase Transition Logic
```python
def advance_phase_if_ready():
    current = get_current_phase_step()
    if stack_empty() and all_players_passed():
        if current.step.mandatory:
            # Execute mandatory step effects
            emit_system_events(current.step)
            resolve_stack()
        
        # Move to next step/phase
        next = get_next_step(current)
        if next:
            set_current_phase_step(next)
            emit_phase_changed_event()
            if next.mandatory:
                emit_system_events(next)
        else:
            # End turn, start next player's turn
            end_turn()
```

### 2. Input Action System (Player Interactions)

The ruleset defines what actions players can take and how they're validated/executed.

#### Action Definitions in IR
```json
{
  "actions": [
    {
      "id": "play_card",
      "name": "Play a Card",
      "timing": "stack",
      "preconditions": [
        { "op": "has_resource", "resource": "mana", "atLeast": { "ref": "card.cost" } },
        { "op": "in_zone", "target": "self", "zone": "hand" },
        { "op": "phase_allows", "phase": "main" }
      ],
      "costs": [
        { "op": "pay_resource", "resource": "mana", "amount": { "ref": "card.cost" } }
      ],
      "targets": [
        { "id": "card", "selector": { "zone": "hand", "count": 1, "controller": "self" } }
      ],
      "effects": [
        { "op": "move_zone", "target": "card", "to": "battlefield" }
      ]
    },
    {
      "id": "attack",
      "name": "Attack",
      "timing": "stack",
      "preconditions": [
        { "op": "phase_allows", "phase": "combat", "step": "declare_attackers" },
        { "op": "can_attack", "target": "self" },
        { "op": "not_tapped", "target": "self" }
      ],
      "targets": [
        { "id": "attacker", "selector": { "zone": "battlefield", "controller": "self", "count": 1 } },
        { "id": "defender", "selector": { "zone": "battlefield", "controller": "opponent", "count": 1 } }
      ],
      "effects": [
        { "op": "declare_attack", "attacker": "attacker", "defender": "defender" }
      ]
    },
    {
      "id": "activate_ability",
      "name": "Activate Ability",
      "timing": "stack",
      "preconditions": [
        { "op": "has_ability", "target": "source", "ability": { "ref": "abilityId" } },
        { "op": "can_activate", "target": "source", "ability": { "ref": "abilityId" } }
      ],
      "costs": [
        { "op": "pay_ability_cost", "source": "source", "ability": { "ref": "abilityId" } }
      ],
      "targets": [
        { "id": "source", "selector": { "zone": "battlefield", "count": 1 } }
      ],
      "effects": [
        { "op": "execute_ability", "source": "source", "ability": { "ref": "abilityId" } }
      ]
    }
  ]
}
```

#### Action Validation Pipeline
1. **API Receives Action**: `{ type: "play_card", cardId: "c123", targetId: "t456" }`
2. **Find Action Definition**: Lookup `play_card` in ruleset actions
3. **Validate Preconditions**: Check all `preconditions` against current state
4. **Validate Targets**: Ensure selected targets match `targets` selectors
5. **Check Costs**: Verify player can pay all `costs`
6. **Create Action Intent**: If valid, create concrete action with resolved targets
7. **Push to Stack**: Convert to engine Event and push to stack

#### Action Execution Flow
```python
def execute_action(action_intent):
    # 1. Pay costs immediately
    for cost in action_intent.costs:
        apply_cost(cost)
    
    # 2. Create engine event
    event = create_event(action_intent)
    push_to_stack(event)
    
    # 3. Resolve stack (handles reactions, timing, etc.)
    resolve_stack_until_idle()
    
    # 4. Check for phase transitions
    advance_phase_if_ready()
```

#### Dynamic Action Discovery
- **Available Actions**: Engine queries ruleset to find all actions player can currently take
- **UI Hints**: Return action metadata (name, cost, targets) for client UI
- **Context Sensitivity**: Actions available change based on phase, resources, board state

```python
def get_available_actions(player_id):
    actions = []
    for action_def in ruleset.actions:
        if can_take_action(player_id, action_def):
            actions.append({
                "id": action_def.id,
                "name": action_def.name,
                "cost": evaluate_costs(action_def.costs),
                "targets": get_target_options(action_def.targets),
                "timing": action_def.timing
            })
    return actions
```

### Integration with Engine Core

#### Ruleset Loading
```python
def load_match_ruleset(match_id):
    ruleset_id = get_match_ruleset(match_id)
    ruleset_ir = load_ruleset_from_db(ruleset_id)
    validate_ruleset_ir(ruleset_ir)
    return compile_ruleset(ruleset_ir)
```

#### Match Initialization
```python
def initialize_match(ruleset):
    # Set initial phase
    set_current_phase(ruleset.turnStructure.phases[0])
    
    # Emit system events for first step
    emit_system_events(get_current_step())
    
    # Open priority window
    open_priority_window()
```

#### Continuous Integration
- **Phase Changes**: Engine automatically emits phase transition events
- **Action Validation**: Every player action validated against current ruleset
- **System Events**: Mandatory step effects triggered by phase transitions
- **Priority Windows**: Opened/closed based on ruleset priority window definitions

This design allows the engine to run any ruleset by interpreting the IR, making the system completely flexible to different game modes and rule variations.

---

## Client-Action Communication Strategy

The client needs to know what actions are available and how to send them. There are two main approaches:

### Approach 1: Semantic Actions (Recommended)
Client sends high-level semantic actions that the engine maps to ruleset actions.

**Client sends**: `{ type: "play_card", cardId: "c123" }`
**Engine does**: Lookup `play_card` action in ruleset, validate, execute

**Benefits**:
- Client doesn't need to know game rules
- Ruleset changes don't break client
- Natural language actions (play, attack, activate)
- Easy to implement different game modes

### Approach 2: Direct State Manipulation
Client sends low-level state changes that the engine validates.

**Client sends**: `{ type: "move_card", cardId: "c123", from: "hand", to: "battlefield" }`
**Engine does**: Check if this move is legal given current ruleset

**Benefits**:
- More flexible for custom interactions
- Client has more control
- Easier to implement complex UI interactions

### Recommended Hybrid Approach

Use semantic actions as primary, with direct manipulation as fallback:

#### 1. Primary: Semantic Actions
```json
// Client requests available actions
GET /matches/{id}/actions
Response: {
  "actions": [
    {
      "id": "play_card",
      "name": "Play Card",
      "description": "Play a card from your hand",
      "cost": "3 mana",
      "targets": {
        "card": {
          "selector": "hand",
          "count": 1,
          "constraints": ["affordable", "playable"]
        }
      },
      "ui": {
        "icon": "play_card",
        "highlight": "hand_zone",
        "animation": "card_play"
      }
    }
  ]
}

// Client sends action
POST /matches/{id}/actions
{
  "type": "play_card",
  "cardId": "c123",
  "targets": { "card": "c123" }
}
```

#### 2. Fallback: Direct Manipulation
```json
// For complex interactions not covered by semantic actions
POST /matches/{id}/actions
{
  "type": "direct_manipulation",
  "action": "move_card",
  "cardId": "c123",
  "from": "hand",
  "to": "battlefield",
  "metadata": {
    "drag_drop": true,
    "ui_context": "hand_to_play"
  }
}
```

### Action Discovery Flow

#### 1. Client Requests Available Actions
```python
# API endpoint
@app.get("/matches/{match_id}/actions")
async def get_available_actions(match_id: str, player_id: str):
    match = await get_match(match_id)
    ruleset = match.ruleset
    
    # Get all possible actions for current game state
    actions = []
    for action_def in ruleset.actions:
        if can_take_action(player_id, action_def, match.state):
            actions.append({
                "id": action_def.id,
                "name": action_def.name,
                "description": action_def.description,
                "cost": evaluate_costs(action_def.costs, match.state),
                "targets": get_target_options(action_def.targets, match.state),
                "timing": action_def.timing,
                "ui": action_def.ui_metadata  # From ruleset
            })
    
    return {"actions": actions}
```

#### 2. Client Sends Action
```python
# API endpoint
@app.post("/matches/{match_id}/actions")
async def submit_action(match_id: str, player_id: str, action: ActionRequest):
    match = await get_match(match_id)
    
    if action.type == "semantic":
        # Validate against ruleset action
        action_def = find_action_definition(action.action_id, match.ruleset)
        if not action_def:
            return {"error": "Unknown action"}
        
        # Validate preconditions, targets, costs
        if not validate_action(action_def, action, match.state):
            return {"error": "Invalid action"}
        
        # Execute
        await execute_semantic_action(match, action_def, action)
        
    elif action.type == "direct_manipulation":
        # Validate direct state change
        if not validate_direct_manipulation(action, match.state, match.ruleset):
            return {"error": "Invalid manipulation"}
        
        # Execute
        await execute_direct_manipulation(match, action)
    
    return {"success": True}
```

### Benefits of This Approach

1. **Semantic Actions**: Natural, ruleset-driven interactions
2. **Direct Manipulation**: Flexible for complex UI interactions
3. **UI Metadata**: Ruleset can define how actions should look/feel
4. **Validation**: All actions validated against current ruleset
5. **Flexibility**: Easy to add new game modes without client changes
6. **Performance**: Client only gets actions they can actually take

### Implementation Priority

1. **Start with semantic actions** for basic gameplay (play, attack, activate)
2. **Add direct manipulation** for complex interactions (drag-drop, multi-select)
3. **Enhance with UI metadata** for better user experience
4. **Add action hints** for new players (tutorial mode)