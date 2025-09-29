awesome—here’s a compact but complete “engineering doc + build plan” you can hand to teammates. it covers the python authoritative backend (AI gen + rules + orchestration), the unity webgl runtime, and the react app.

---

# product vision

A browser-playable platform where creators design custom trading card / board games, publish rulesets and card sets, and play head-to-head.

* **Players**: low-latency, cheat-resistant matches, replays, ladders.
* **Creators**: intuitive editors + AI helpers to generate cards, art, and rules (Python abilities).
* **Moderators**: patch rules, ban broken combos, and audit matches.

---

# high-level architecture

```
[React App]  ── HTTPS/WSS ──>  [Gateway/API]
   |  auth, UGC, lobby, store        |
   |                                  v
   |                            [Python Backend]
   |                      ┌─ Rules/Reducer (authoritative)
   |                      ├─ Lua Sandbox (abilities)
   |                      ├─ AI Gen (cards, art prompts, rules)
   |                      ├─ Matchmaking / Sessions
   |                      ├─ Event Sourcing (actions→events→snapshots)
   |                      └─ WebSocket Fanout
   |                                  |
   |                       Redis <────┼────> Postgres
   |                       (live)     |      (durable)
   v                                  |
[Unity WebGL Runtime] <───── WSS ─────┘
(state diffs, stepwise events; client acks)
```

**Key decisions**

* **Server-authoritative** turn/priority system; Unity is a thin renderer/input layer.
* **Event-sourced** matches (append-only event log + periodic snapshots).
* **Deterministic** rules: seeded RNG; Python abilities run in a sandbox.
* **Stepwise event stream** with client ACKs for cinematic pacing.

---

# functional scope (v1)

* **Accounts & Auth**: email+password (later SSO). JWT access tokens, refresh flow.
* **Game discovery**: browse rulesets, decks, custom boards; ratings and version pinning.
* **Creators**:

  * Card editor (stats/keywords/art); deck builder.
  * Rules editor (triggers/effects) + AI assist to draft Python.
  * Validation & dry-run simulator.
* **Play**:

  * Lobby + matchmaking (casual).
  * Turn-based battles; surrender; timeout handling.
  * Replays (event log) & basic spectating.
* **Moderation**: global patches/banlist; per-ruleset versioning and deprecation.

---

# non-functional targets (v1)

* Latency (server process): **< 50ms** per action on P95.
* Throughput: **1k concurrent matches** with horizontal scale.
* Cheat-resistance: server is single source of truth; idempotent action API.
* Observability: per-match traces + structured logs.
* Security: sandboxed Lua, rate limiting, authz on game endpoints.
* Cost: single small cluster (e.g., k8s or docker swarm) + managed Postgres/Redis.

---

# backend (python) — design

## stack

* **FastAPI** (HTTP + WebSocket), **uvicorn**, **pydantic** schemas.
* **Redis** (hot state, locks, pub/sub, recent event ring).
* **Postgres** (users, decks, rulesets, matches, events, snapshots).
* **Python Sandbox**: `restrictedpython` with strict policy for ability execution.
* **Task runner**: `asyncio` / `dramatiq`/`rq` for AI gen and heavy jobs.

## core domain types (abridged)

```ts
type MatchState = {
  matchId: string; version: number; rulesetVersion: string;
  rngSeed: string; phase: "LOBBY"|"PLAY"|"END"; turn: number;
  activePlayer: PlayerId;
  players: Record<PlayerId, PlayerState>;
  board: BoardState;           // zones, tiles, etc.
  stack: EffectStackItem[];    // TCG-style resolution
};

type Action = {
  actionId: string; matchId: string; playerId: string;
  type: "ATTACK"|"PLAY_CARD"|...; payload: any;
  clientSeq: number; knownVersion?: number;
};

type Event = {
  eventId: string; matchId: string; version: number; step: number;
  resolutionId: string; type: string; data: any; ts: string;
  requiresAck?: boolean; stateDiff?: Diff;
};
```

## event flow

* client → `Action` over WS/HTTP.
* server validates, runs reducer + Python triggers → **ordered events** with a shared `resolutionId`.
* events are **streamed stepwise**; some require `FLOW_ACK` to advance.
* on completion: persist events (and maybe snapshot), broadcast final state version.

## determinism

* RNG: SplitMix64/PCG seeded by `(match.rngSeed, version, step)`.
* Python: only expose pure helpers (no time/I/O), fixed iteration order, capped CPU/mem.

## persistence model

* **events**: append-only table (index by `matchId, version, step`).
* **snapshots**: every N events save full `MatchState` (JSONB).
* **replay**: load latest snapshot + replay tail events.

## concurrency & scaling

* **Actor per match**: route all actions for a `matchId` to the same asyncio task (or pod via consistent hashing).
* **Locking**: per-match redis lock only if needed (actor model prefers single writer).
* **Fanout**: redis pub/sub topic `room:{matchId}` to all websocket connections.

## AI generation service

* **Prompts** turn text specs → (a) card text + stats, (b) Python ability skeletons, (c) image prompts.
* **Lint/validate** generated Python: static checks + dry-run in sandbox with mock state.
* **Safety**: bound CPU time/instructions, deny globals, whitelist API surface.

## HTTP/WS API (selected)

**Auth**

* `POST /auth/register`, `POST /auth/login`, `POST /auth/refresh`

**UGC**

* `POST /cards` (create/update), `POST /rulesets`, `POST /decks`
* `POST /ai/cards/suggest` → returns card JSON + suggested Python
* `POST /ai/abilities/suggest` → Python skeleton + tests

**Lobby/Match**

* `POST /matches` (create or join)
* `GET /matches/{id}/state` (snapshot)
* `WS /matches/{id}`  (bidirectional)

  * client → `{type:"ACTION", action:Action}`
  * server → `Event` messages (ordered, with optional `requiresAck`)
  * client → `{type:"FLOW_ACK", resolutionId, step}`

**Moderation**

* `POST /rulesets/{id}/patch` (new rulesetVersion)
* `POST /banlist` (entity/ability bans)

---

# unity webgl runtime — design

## responsibilities

* render authoritative state; collect user inputs.
* run **prediction (optional)** for feel; reconcile on events.
* drive animations per **event type** with a coroutine queue.
* maintain a **local mirror** of state; apply server **diffs** immediately.

## core client loop (pseudo)

```csharp
void OnServerEvent(Event ev) {
    ApplyDiff(localState, ev.stateDiff);
    animationQueue.Enqueue(ev);
}
IEnumerator Player() {
    while (true) {
        var ev = animationQueue.Dequeue();
        yield return Animate(ev);             // play VFX/SFX/camera
        if (ev.requiresAck) SendAck(ev);
    }
}
```

## mapping events → visuals

* `ACTION_BEGIN`: highlight actors, lock input.
* `ATTACK_DECLARED`: line render / movement tween.
* `DAMAGE_APPLIED`: hit flash, number pop, shake.
* `TRIGGER_QUEUED/RESOLVED`: stack UI; glow source.
* `CARD_DRAWN`: deck→hand slide; update counters.
* `PRIORITY_WINDOW_OPENED`: show response UI & timer.
* `ACTION_END`: clear highlights; unlock input (if active player).

## net considerations (webgl)

* WebSocket transport only; heartbeat/ping; exponential reconnect.
* On reconnect send `{lastVersion, lastResolutionId, lastStep}` → server streams delta.

---

# react app — design

## responsibilities

* authentication, profiles, inventory (cards/decks), and creator tools.
* lobby, matchmaking, match list, replays, spectating.
* settings, accessibility, and content moderation UI.

## key pages

* **Home/Discover**: top rulesets, recent decks, trending creators.
* **Creator Studio**: Card Editor (form), Rules Editor (Lua with lint), AI Assist panel, Deck Builder (drag/drop).
* **Play**: Lobbies, Match browser, “Launch Game” (opens Unity).
* **Replay Viewer**: timeline scrubber reading event log.
* **Account**: purchases, linked accounts, preferences.

## tech

* React + Router + Zustand/Redux for app state; Tailwind/Chakra for UI.
* WebSocket client for lobby + notifications.
* Monaco editor for Lua with diagnostics.
* Uploads to object storage (images) with signed URLs.

---

# data contracts (starter)

**Card JSON**

```json
{
  "id":"card_fire_imp",
  "name":"Fire Imp",
  "cost":2,
  "stats":{"attack":3,"health":2},
  "keywords":["demon"],
  "text":"On damage: opponent draws a card.",
  "abilities":[{"id":"a_on_dmg","trigger":"ON_TAKES_DAMAGE","python":"..."}],
  "art":{"imageUrl":"...","artist":"AI/Prompt v1"}
}
```

**Action (client→server)**

```json
{"matchId":"m1","actionId":"a123","playerId":"p1",
 "type":"ATTACK","payload":{"attacker":"c_p1_12","defender":"c_p2_7"},
 "clientSeq":17,"knownVersion":41}
```

**Event (server→client)**

```json
{"version":42,"resolutionId":"r775","step":3,
 "type":"DAMAGE_APPLIED","requiresAck":true,
 "data":{"target":"c_p2_7","amount":3},
 "stateDiff":{"entities":{"c_p2_7":{"hp":{"old":5,"new":2}}}}}
```

---

# database sketch (postgres)

* `users(id, email, hash, created_at, …)`
* `rulesets(id, owner_id, version, schema, status, ... )`
* `cards(id, ruleset_id, jsonb, version)`
* `decks(id, owner_id, ruleset_version, jsonb)`
* `matches(id, ruleset_version, status, created_at, …)`
* `match_events(match_id, version, step, event jsonb, ts)`
* `match_snapshots(match_id, version, state jsonb, ts)`
* `banlist(id, ruleset_version, items jsonb, ts)`

Indexes: `(match_id, version, step)` on events; GIN on `jsonb` fields used for queries.

---

# security & safety

* **Python sandbox**: deny `import`, `os`, `sys`; no globals; capped instruction count; memory limit; timeouts; pre-execution static AST checks.
* **Input validation**: pydantic for all payloads; length/shape limits; rate-limit actions per second.
* **AuthZ**: only match participants can send actions; spectators get read-only streams.
* **Moderation**: patch pipeline; shadow-ban abusive decks; revoke ruleset versions.

---

# observability

* Structured logs: `matchId`, `resolutionId`, `step`, `latency_ms`.
* Tracing: action→validation→reducer→persist→broadcast spans.
* Metrics:

  * P95 action latency
  * VM CPU timeouts
  * Ack wait durations
  * Redis hit ratio
  * Event queue depth

---

# testing strategy

* **Reducer golden tests**: YAML action scripts → expected events/state.
* **Property tests/fuzzing**: random legal action generation per ruleset.
* **Python unit tests**: creator-authored tests stored alongside abilities.
* **Replay determinism**: event log re-execution must equal final snapshot.
* **Load tests**: synthetic matches at scale; per-actor throughput.
* **Security tests**: sandbox escape attempts; payload fuzz; rate-limit.

---

# CI/CD

* Lint/format (black, flake8), mypy (py), eslint/tsc (react), analyzer for python abilities.
* Unit & integration tests; ephemeral DB/Redis via docker in CI.
* Containerize services; deploy to staging with seed data; e2e smoke (create match, play 5 actions, verify replay).
* Blue/green or canary deploys for backend; static hosting + CDN for React & Unity builds.

---

# phased delivery plan

## Phase 0 — Foundations (1–2 weeks)

* Repo mono-layout: `backend/`, `unity/`, `web/`, `infra/`.
* Auth (register/login/refresh), JWT middleware.
* DB/Redis provisioning; migrations.
* Hello-world WS echo.

**Acceptance**: can auth, open WS, ping/pong.

## Phase 1 — Match Core (2–3 weeks)

* Actor-per-match loop; `Action` → reducer → `Event` stream.
* Event sourcing tables; snapshots; reconnect with `lastVersion`.
* Basic turn system, zones, play/attack/damage.

**Acceptance**: two bots can finish a simple match; replay works.

## Phase 2 — Unity Runtime (2 weeks)

* WebGL project, WS client, event animation queue, diff applier.
* Visuals for `ACTION_BEGIN/END`, `ATTACK_DECLARED`, `DAMAGE_APPLIED`, `CARD_DRAWN`.
* FLOW_ACK pacing.

**Acceptance**: human can play via Unity; stepwise animations occur in order.

## Phase 3 — Creator Tools (2–3 weeks)

* React Card Editor + Deck Builder.
* Lua editor with lint; run “dry-run” against sandbox.
* AI assist endpoints (cards/abilities) with validation.

**Acceptance**: create a small card set + deck; validate; play with it.

## Phase 4 — Matchmaking & Spectate (1–2 weeks)

* Lobbies, invite links, basic queue.
* Read-only spectator stream; rate-limited chat.

**Acceptance**: spectators can watch with auto-advance.

## Phase 5 — Moderation & Patching (1–2 weeks)

* Ruleset versioning, banlist, hotfix pipeline.
* Telemetry dashboard (metrics + logs).

**Acceptance**: push a rules patch; existing matches remain pinned; new matches use latest.

*(Future)* Phase 6+

* Ranked ladder & MMR, tournaments, economy/skins, mobile UX, AI opponents, deck legality checks, creator marketplace.

---

# prioritized backlog (moscow)

**Must**

* Server-authoritative reducer & event stream with acks
* Python sandbox + deterministic RNG
* Redis/Postgres plumbing; replay & snapshots
* Unity WebGL WS client + event animations
* React auth + creator editors + deck builder
* Basic matchmaking/lobbies

**Should**

* Reconnect/spectate; replay viewer in React
* AI ability assistant with lint & dry-run
* Moderation tools & banlist
* Tracing/metrics dashboards

**Could**

* Client-side prediction with reconciliation
* Cross-ruleset validation tests
* In-browser Python unit test runner for creators

**Won’t (v1)**

* Real-time physics gameplay
* Native mobile builds
* Complex economy/marketplace

---

# example reducer skeleton (python, illustrative)

```python
async def submit_action(action: Action) -> list[Event]:
    actor = get_actor_for_match(action.matchId)
    return await actor.process(action)

class MatchActor:
    def __init__(self, match_id):
        self.state = load_state(match_id)  # from redis/db
        self.queue = asyncio.Queue()

    async def process(self, action):
        # idempotency
        if seen(action.actionId): return cached_result(action.actionId)

        validate(self.state, action)
        res_id = new_resolution_id()
        step = 0
        events = []

        def emit(type_, data, diff=None, ack=False):
            nonlocal step, events
            step += 1
            ev = Event(
                eventId=ulid(), matchId=self.state.matchId,
                version=self.state.version + 1, step=step,
                resolutionId=res_id, type=type_, data=data,
                requiresAck=ack, stateDiff=diff, ts=now()
            )
            events.append(ev)
            broadcast(ev)    # WS fanout (may await ACK before next)

        # Example: ATTACK
        if action.type == "ATTACK":
            a, d = action.payload["attacker"], action.payload["defender"]
            emit("ACTION_BEGIN", {"action":"ATTACK","attacker":a,"defender":d})
            emit("ATTACK_DECLARED", {"attacker":a,"defender":d}, ack=True)

            dmg = calc_damage(self.state, a, d)
            apply_damage(self.state, d, dmg)
            diff = make_diff_for_damage(d, dmg)
            emit("DAMAGE_APPLIED", {"target":d,"amount":dmg}, diff, ack=True)

            triggers = find_triggers(self.state, on="ON_TAKES_DAMAGE", target=d)
            for t in triggers:
                emit("TRIGGER_QUEUED", {"triggerId":t.id,"source":t.source})
                effects = run_python_trigger(self.state, t)
                for eff in effects:
                    apply_effect(self.state, eff)
                    emit("TRIGGER_RESOLVED", {"triggerId":t.id,"effect":eff.kind})
                    if eff.kind == "OPPONENT_DRAWS":
                        diff = hand_deck_diff(eff.player, +1)
                        emit("CARD_DRAWN", {"player":eff.player}, diff, ack=True)

            emit("ACTION_END", {})
            self.state.version += 1

        persist_events_and_maybe_snapshot(self.state, events)
        save_live_state(self.state)
        return events
```

---

# risks & mitigations

* **Sandbox escapes / infinite loops** → strict Python sandbox, instruction quotas, pre-flight static checks, kill switch.
* **Desyncs** (client prediction) → keep prediction minimal; always reconcile on event.
* **Hot rules exploits** → moderation pipeline, patch/bans, version pinning.
* **Cost blow-ups** (AI/art) → queue + quotas + caching; human-in-the-loop for publish.

---

# developer environment

* `docker compose up` ⇒ Postgres, Redis, API, React, Unity local server.
* Seed script: demo ruleset, 20 cards, two decks, and a sample replay.
* Make targets: `make test`, `make loadtest`, `make fmt`, `make seed`.

---

this gives you a clear path to build: a deterministic, server-authoritative core; a beautiful unity client with beat-by-beat animations; and creator tools that stay safe and productive thanks to AI assistance with guardrails. if you want, i can draft the initial pydantic schemas + fastapi endpoints or a unity event-player script next.
