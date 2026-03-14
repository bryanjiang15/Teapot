"""
SystemEvent — primitive event constants automatically emitted by the engine.

These are the ONLY events the engine fires on its own initiative.
All domain events (turn_started, card_played, damage_dealt, etc.)
must be emitted explicitly by game scripts via game.emit().
"""

GAME_STARTED        = "game_started"        # fired by MatchActor.begin_game()
GAME_ENDED          = "game_ended"          # fired by GameAPI.end_game()
OBJECT_MOVED        = "object_moved"        # fired by GameAPI.move()
PROPERTY_CHANGED    = "property_changed"    # fired by GameAPI.set_property()
OBJECT_INSTANTIATED = "object_instantiated" # fired by GameAPI.instantiate()
OBJECT_DESTROYED    = "object_destroyed"    # fired by GameAPI.destroy()
INPUT_RECEIVED      = "input_received"      # fired when submit_input() resolves

# All primitive system events as a frozenset (for validation / filtering).
SYSTEM_EVENTS: frozenset[str] = frozenset({
    GAME_STARTED,
    GAME_ENDED,
    OBJECT_MOVED,
    PROPERTY_CHANGED,
    OBJECT_INSTANTIATED,
    OBJECT_DESTROYED,
    INPUT_RECEIVED,
})
