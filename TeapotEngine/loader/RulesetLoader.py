"""
RulesetLoader — deserialises an API JSON payload into a validated RulesetIR.

Usage
-----
    loader = RulesetLoader()
    ruleset = loader.from_api_response(response_json_dict)

The loader performs structural validation after deserialisation.
If validation fails with errors (not just warnings), it raises
RulesetLoadError containing all error messages.
"""
from __future__ import annotations

from typing import Any

from TeapotEngine.models.api_models import RulesetIRResponse, ScriptedComponentResponse
from TeapotEngine.ruleset.IR import RulesetIR
from TeapotEngine.ruleset.ScriptedComponent import ScriptedComponent, ComponentKind
from TeapotEngine.ruleset.Validator import RulesetValidator


class RulesetLoadError(Exception):
    """Raised when the loaded RulesetIR fails validation."""

    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("RulesetIR validation failed:\n" + "\n".join(f"  - {e}" for e in errors))


class RulesetLoader:
    """Converts API JSON → validated RulesetIR ready for MatchActor."""

    def from_api_response(self, data: dict[str, Any]) -> RulesetIR:
        """Parse and validate the JSON payload from GET /projects/{id}/ruleset.

        Parameters
        ----------
        data : dict
            Raw JSON dict as returned by the TeapotAPI ruleset endpoint.

        Returns
        -------
        RulesetIR
            Validated, engine-ready ruleset.

        Raises
        ------
        RulesetLoadError
            If the data contains validation errors (schema problems or
            invalid component kinds / syntax errors in scripts).
        """
        # Deserialise via the API mirror models
        api_response = RulesetIRResponse.model_validate(data)

        # Convert to engine-internal models
        component_defs = [
            self._convert_component(c) for c in api_response.component_definitions
        ]

        ruleset = RulesetIR(
            version=api_response.version,
            metadata=api_response.metadata,
            component_definitions=component_defs,
            constants=api_response.constants,
        )

        # Validate
        validator = RulesetValidator(ruleset)
        if not validator.validate():
            raise RulesetLoadError(validator.get_errors())

        # Surface warnings without raising
        for warning in validator.get_warnings():
            print(f"[RulesetLoader] WARNING: {warning}")

        return ruleset

    def from_dict(self, data: dict[str, Any]) -> RulesetIR:
        """Alias for from_api_response — accepts any dict."""
        return self.from_api_response(data)

    # ------------------------------------------------------------------
    # Internal conversion
    # ------------------------------------------------------------------

    def _convert_component(self, c: ScriptedComponentResponse) -> ScriptedComponent:
        try:
            kind = ComponentKind(c.kind)
        except ValueError:
            # Unknown kind — default to OBJECT; validator will warn/error
            kind = ComponentKind.OBJECT

        return ScriptedComponent(
            id=c.id,
            kind=kind,
            name=c.name,
            description=c.description,
            script=c.script,
            properties=dict(c.properties),
            event_subscriptions=list(c.event_subscriptions),
        )
