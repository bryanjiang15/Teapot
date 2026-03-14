"""
RulesetValidator — validates a compiled RulesetIR before it is run.

Call validate() after loading; check get_errors() / get_warnings()
before handing the RulesetIR to MatchActor.
"""
from __future__ import annotations

import ast
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .IR import RulesetIR


class ValidationError(Exception):
    pass


class RulesetValidator:
    """Validates structural integrity of a RulesetIR."""

    def __init__(self, ruleset: "RulesetIR"):
        self._ruleset = ruleset
        self._errors: list[str] = []
        self._warnings: list[str] = []

    def validate(self) -> bool:
        """Run all checks. Returns True if no errors (warnings are allowed)."""
        self._errors.clear()
        self._warnings.clear()
        self._check_game_component()
        self._check_player_components()
        self._check_script_syntax()
        self._check_event_subscriptions()
        return len(self._errors) == 0

    def get_errors(self) -> list[str]:
        return list(self._errors)

    def get_warnings(self) -> list[str]:
        return list(self._warnings)

    # ------------------------------------------------------------------
    # Internal checks
    # ------------------------------------------------------------------

    def _check_game_component(self) -> None:
        from .ScriptedComponent import ComponentKind
        games = self._ruleset.get_components_by_kind(ComponentKind.GAME)
        if not games:
            self._warnings.append(
                "No GAME component defined; engine will start without a root component."
            )
        elif len(games) > 1:
            self._errors.append(
                f"Multiple GAME components defined ({len(games)}); only one is allowed."
            )

    def _check_player_components(self) -> None:
        from .ScriptedComponent import ComponentKind
        players = self._ruleset.get_components_by_kind(ComponentKind.PLAYER)
        if not players:
            self._warnings.append("No PLAYER component defined.")

    def _check_script_syntax(self) -> None:
        for comp in self._ruleset.component_definitions:
            if comp.script is None:
                continue
            try:
                ast.parse(comp.script)
            except SyntaxError as e:
                self._errors.append(
                    f"Component '{comp.name}' ({comp.id}): script syntax error — {e}"
                )

    def _check_event_subscriptions(self) -> None:
        for comp in self._ruleset.component_definitions:
            if comp.event_subscriptions and comp.script is None:
                self._warnings.append(
                    f"Component '{comp.name}' ({comp.id}) has event_subscriptions "
                    f"but no script — events will be silently ignored."
                )
