"""
StateWatcherEngine — dirty-flag tracker for on_update dispatch.

After every stack flush in MatchActor.resolve_stack(), the watcher engine
is checked. If the state has been marked dirty (any mutation occurred),
MatchActor calls ScriptRunner.call_on_update() for all component instances.
"""
from __future__ import annotations


class StateWatcherEngine:
    """Dirty-flag optimisation for on_update calls.

    Rather than calling on_update unconditionally every cycle, the engine
    only calls it when something actually changed. Scripts and GameAPI
    mutations call mark_dirty(); the main loop calls check_and_clear()
    to decide whether to dispatch on_update.
    """

    def __init__(self):
        self._is_dirty: bool = False

    def mark_dirty(self) -> None:
        """Signal that game state has changed since the last on_update pass."""
        self._is_dirty = True

    def is_dirty(self) -> bool:
        return self._is_dirty

    def check_and_clear(self) -> bool:
        """Return True if dirty (and reset the flag). False means no-op."""
        if self._is_dirty:
            self._is_dirty = False
            return True
        return False

    def clear(self) -> None:
        self._is_dirty = False
