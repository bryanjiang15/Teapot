"""
MatchActor — the central game loop coordinator.

Responsibilities
----------------
1. Initialise component instances from RulesetIR at match start.
2. Dispatch lifecycle hooks (on_init, on_event, on_update) via ScriptRunner.
3. Maintain the event Stack and EventBus.
4. Pause / resume when a script calls game.wait_for_input().
5. Provide submit_input() for the host application to supply player answers.

Architecture
------------
- No WorkflowExecutor, no Interpreter, no EffectInterpreter.
- All game logic lives in component scripts executed by ScriptRunner.
- The only built-in events are the seven primitive SystemEvents emitted by GameAPI.
- Domain events (turn_started, card_played, …) are emitted by scripts.

Loop contract
-------------
begin_game() → on_init all instances → emit game_started → resolve_stack()

resolve_stack():
  while stack not empty:
    pop event
    record in event_log
    for each subscribed instance:
      call ScriptRunner.call_on_event()
      push any emitted events back onto the stack
  if state is dirty:
    call ScriptRunner.call_on_update() for all instances
    if new events were emitted: goto resolve_stack()

If a script raises WaitForInputSignal the loop stops and returns
WAITING_FOR_INPUT. submit_input() resumes by emitting INPUT_RECEIVED.
"""
from __future__ import annotations

import uuid
from typing import Any, Optional

from .Component import ComponentInstance
from .EventBus import EventBus
from .EventRegistry import EventRegistry
from .Events import Event, StackItem, StackItemType, PendingInput
from .GameAPI import GameAPI, WaitForInputSignal
from .GameLoopResult import GameLoopResult
from .GameState import GameState
from .ScriptRunner import ScriptRunner, ScriptRuntimeError
from .Stack import EventStack
from .StateWatcherEngine import StateWatcherEngine
from .rng import DeterministicRNG
from TeapotEngine.ruleset.IR import RulesetIR
from TeapotEngine.ruleset.ScriptedComponent import ComponentKind
from TeapotEngine.ruleset.system_models.SystemEvent import (
    GAME_STARTED,
    GAME_ENDED,
    INPUT_RECEIVED,
)


class MatchActor:
    """Single-threaded actor that owns and drives one match."""

    MAX_STACK_DEPTH = 500

    def __init__(
        self,
        match_id: str,
        ruleset: RulesetIR,
        player_ids: Optional[list[str]] = None,
        seed: Optional[int] = None,
        verbose: bool = False,
    ):
        self.match_id = match_id
        self.ruleset = ruleset
        self.verbose = verbose

        self.rng = DeterministicRNG(seed if seed is not None else abs(hash(match_id)))
        self.runner = ScriptRunner()
        self.event_bus = EventBus()
        self.event_registry = EventRegistry()
        self.stack = EventStack()
        self.state_watcher = StateWatcherEngine()

        effective_player_ids: list[str] = player_ids or ["player1", "player2"]

        self.state = GameState(
            match_id=match_id,
            player_instance_ids=[],
        )

        self._initialise_instances(effective_player_ids)

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def _initialise_instances(self, player_ids: list[str]) -> None:
        """Create runtime instances for GAME, PLAYER, and CONTAINER/OBJECT
        definitions in the RulesetIR.

        - GAME   → one instance
        - PLAYER → one instance per entry in player_ids
        - CONTAINER / OBJECT → one instance per definition (at start of game;
          scripts can instantiate more at runtime via game.instantiate())
        """
        # 1. GAME component
        game_def = self.ruleset.get_game_component()
        if game_def:
            game_inst = self._create_instance(game_def, owner_id=None)
            self.state.game_instance_id = game_inst.id
        else:
            # No GAME definition; create a bare placeholder
            game_inst_id = str(uuid.uuid4())
            self.state.game_instance_id = game_inst_id

        # 2. PLAYER components — one per player_id
        player_defs = self.ruleset.get_player_components()
        player_def = player_defs[0] if player_defs else None
        for player_id in player_ids:
            if player_def:
                p_inst = self._create_instance(
                    player_def,
                    owner_id=self.state.game_instance_id,
                    name_override=player_id,
                )
            else:
                # No PLAYER definition; bare instance
                p_inst = ComponentInstance(
                    id=str(uuid.uuid4()),
                    definition_id="",
                    kind=ComponentKind.PLAYER,
                    name=player_id,
                    owner_id=self.state.game_instance_id,
                )
                self.state.manager.add(p_inst)
                self.state.properties[p_inst.id] = {}
            self.state.player_instance_ids.append(p_inst.id)

        if self.state.player_instance_ids:
            self.state.active_player_id = self.state.player_instance_ids[0]

        # 3. CONTAINER and OBJECT definitions — one initial instance each
        for comp_def in self.ruleset.component_definitions:
            if comp_def.kind in (ComponentKind.CONTAINER, ComponentKind.OBJECT):
                self._create_instance(comp_def, owner_id=self.state.game_instance_id)

    def _create_instance(
        self,
        definition,
        owner_id: Optional[str],
        name_override: Optional[str] = None,
    ) -> ComponentInstance:
        """Create a ComponentInstance, seed its properties, and register
        it with the EventBus."""
        inst_id = str(uuid.uuid4())
        instance = ComponentInstance(
            id=inst_id,
            definition_id=definition.id,
            kind=definition.kind,
            name=name_override or definition.name,
            owner_id=owner_id,
        )
        self.state.manager.add(instance)
        self.state.init_properties(inst_id, definition.properties)

        if definition.event_subscriptions:
            self.event_bus.subscribe(inst_id, definition.event_subscriptions)

        return instance

    # ------------------------------------------------------------------
    # Game loop entry point
    # ------------------------------------------------------------------

    def begin_game(self) -> GameLoopResult:
        """Initialise all on_init hooks then emit game_started.

        Returns WAITING_FOR_INPUT if any on_init calls wait_for_input(),
        otherwise the result of the first resolve_stack() call.
        """
        # Call on_init for every instance that has a script
        for instance in list(self.state.manager.all()):
            definition = self.ruleset.get_component(instance.definition_id)
            if definition and definition.script:
                api = self._make_api(instance.id)
                try:
                    self.runner.call_on_init(definition.script, api)
                    self._flush_api(api)
                except WaitForInputSignal as sig:
                    self._flush_api(api)
                    return GameLoopResult.WAITING_FOR_INPUT
                except Exception as exc:
                    self._log(f"[on_init] {instance.name}: {exc}")

        # Emit the root game_started event
        self._push_event(Event(
            type=GAME_STARTED,
            payload={"match_id": self.match_id},
        ))

        return self.resolve_stack()

    # ------------------------------------------------------------------
    # Core loop
    # ------------------------------------------------------------------

    def resolve_stack(self) -> GameLoopResult:
        """Drain the event stack, dispatching on_event for each event.

        Returns when:
          - The stack is empty and state is clean  → may return GAME_ENDED
          - A script calls wait_for_input()        → WAITING_FOR_INPUT
          - The game ends (state.game_ended)       → GAME_ENDED
        """
        depth = 0
        while not self.stack.is_empty():
            if self.state.game_ended:
                return GameLoopResult.GAME_ENDED
            if self.state.pending_input:
                return GameLoopResult.WAITING_FOR_INPUT

            depth += 1
            if depth > self.MAX_STACK_DEPTH:
                raise RecursionError("MatchActor: event stack depth exceeded limit")

            item = self.stack.pop()
            event = self.event_registry.get(item.ref_id)
            if event is None:
                continue

            # Record in event log
            self.state.record_event(event)
            self.state_watcher.mark_dirty()

            if self._verbose_log(event):
                pass

            # Check for terminal event
            if event.type == GAME_ENDED:
                self.state.game_ended = True
                return GameLoopResult.GAME_ENDED

            # Dispatch to subscribed instances
            result = self._dispatch_event(event)
            if result is not None:
                return result

            self.event_registry.unregister(item.ref_id)

        # Stack is empty — run on_update if state changed
        if self.state_watcher.check_and_clear():
            result = self._run_on_update()
            if result is not None:
                return result
            # on_update may have pushed new events — recurse
            if not self.stack.is_empty():
                return self.resolve_stack()

        if self.state.game_ended:
            return GameLoopResult.GAME_ENDED
        return GameLoopResult.GAME_ENDED  # stack empty and game not ended → idle

    def _dispatch_event(self, event: Event) -> Optional[GameLoopResult]:
        """Call on_event for every subscribed instance. Returns early on input wait."""
        subscribers = self.event_bus.get_subscribers(event.type)
        for inst_id in subscribers:
            instance = self.state.manager.get(inst_id)
            if not instance or not instance.is_active():
                continue
            definition = self.ruleset.get_component(instance.definition_id)
            if not definition or not definition.script:
                continue

            api = self._make_api(inst_id)
            try:
                self.runner.call_on_event(definition.script, event, api)
                self._flush_api(api)
            except WaitForInputSignal:
                self._flush_api(api)
                return GameLoopResult.WAITING_FOR_INPUT
            except Exception as exc:
                self._log(f"[on_event:{event.type}] {instance.name}: {exc}")

        return None

    def _run_on_update(self) -> Optional[GameLoopResult]:
        """Call on_update for all instances. Returns early on input wait."""
        for instance in list(self.state.manager.all()):
            if not instance.is_active():
                continue
            definition = self.ruleset.get_component(instance.definition_id)
            if not definition or not definition.script:
                continue

            api = self._make_api(instance.id)
            try:
                self.runner.call_on_update(definition.script, api)
                self._flush_api(api)
            except WaitForInputSignal:
                self._flush_api(api)
                return GameLoopResult.WAITING_FOR_INPUT
            except Exception as exc:
                self._log(f"[on_update] {instance.name}: {exc}")

        return None

    # ------------------------------------------------------------------
    # Player input
    # ------------------------------------------------------------------

    def submit_input(self, answer: Any) -> GameLoopResult:
        """Supply the player's answer to a pending wait_for_input() call.

        Clears the pending input, emits INPUT_RECEIVED, and resumes the loop.
        """
        if not self.state.pending_input:
            raise ValueError("No pending input to submit")

        pending = self.state.pending_input
        self.state.pending_input = None

        self._push_event(Event(
            type=INPUT_RECEIVED,
            payload={
                "input_id": pending.input_id,
                "player_id": pending.for_player_id,
                "answer": answer,
            },
        ))
        return self.resolve_stack()

    # ------------------------------------------------------------------
    # Public state accessors
    # ------------------------------------------------------------------

    def get_state_dict(self) -> dict[str, Any]:
        return self.state.to_dict()

    def get_pending_input(self) -> Optional[dict[str, Any]]:
        if not self.state.pending_input:
            return None
        p = self.state.pending_input
        return {
            "input_id": p.input_id,
            "for_player_id": p.for_player_id,
            "prompt": p.prompt,
            "options": p.options,
        }

    def is_game_over(self) -> bool:
        return self.state.game_ended

    def get_winner(self) -> Optional[str]:
        """Return the name of the winning PLAYER instance, or None."""
        if not self.state.winner_id:
            return None
        inst = self.state.manager.get(self.state.winner_id)
        return inst.name if inst else self.state.winner_id

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _make_api(self, instance_id: str) -> GameAPI:
        return GameAPI(
            state=self.state,
            current_id=instance_id,
            ruleset=self.ruleset,
            event_bus=self.event_bus,
            runner=self.runner,
            rng=self.rng,
        )

    def _flush_api(self, api: GameAPI) -> None:
        """Push any events the script emitted onto the stack."""
        for event in api._collect_events():
            self._push_event(event)

    def _push_event(self, event: Event) -> None:
        event_id = self.event_registry.register(event)
        self.stack.push(StackItem(
            kind=StackItemType.EVENT,
            ref_id=event_id,
            created_at_order=self.stack.get_next_order(),
        ))

    def _log(self, msg: str) -> None:
        if self.verbose:
            print(f"[MatchActor] {msg}")

    def _verbose_log(self, event: Event) -> bool:
        if self.verbose:
            print(f"[event] {event.type} {event.payload}")
        return self.verbose
