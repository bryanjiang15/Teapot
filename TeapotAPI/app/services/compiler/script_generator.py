"""
ScriptGenerator — AI Scripter Agent wrapper.

Takes a ComponentBlueprint and returns a validated Python lifecycle script.

In production this service calls an LLM (GPT-4 / Claude / etc.) with a
carefully crafted prompt describing the GameAPI interface and the component's
intent. The generated script is then validated by ScriptRunner.validate()
before being saved.

For development / testing a deterministic template generator is used so the
compilation pipeline can be exercised end-to-end without an LLM key.
"""
from __future__ import annotations

import textwrap
from typing import Optional

from .graph_compiler import ComponentBlueprint


class ScriptGenerationError(Exception):
    """Raised when the AI fails to produce a valid script after max retries."""
    pass


class ScriptGenerator:
    """Wraps the AI Scripter Agent call.

    Parameters
    ----------
    llm_client : any, optional
        An LLM client (e.g. ``openai.AsyncOpenAI``).  When None (default)
        the generator falls back to the template-based stub.
    max_retries : int
        How many times to retry the LLM + validate cycle before giving up.
    """

    GAMEAPI_CONTEXT = textwrap.dedent("""
        # GameAPI reference (the `game` object passed to each hook)
        # -------------------------------------------------------
        # game.self                            → ObjectView of this component
        # game.game                            → ObjectView of the GAME instance
        # game.players                         → list[ObjectView]
        # game.active_player                   → ObjectView | None
        # game.events.count(type)              → int
        # game.events.last(type)               → dict | None
        # game.find(kind, container, owner, filter_fn) → list[ObjectView]
        # game.get_property(obj, key, default) → Any
        # game.set_property(obj, key, value)
        # game.move(obj, to_container)
        # game.instantiate(name, owner, props) → ObjectView
        # game.destroy(obj)
        # game.set_active_player(player)
        # game.emit(event_type, payload={})
        # game.wait_for_input(player, prompt, options)
        # game.end_game(winner=None)
        # game.shuffle(container)
        # game.random_pick(container, count)   → list[ObjectView]
        # game.random_int(min, max)            → int
        # -------------------------------------------------------
    """).strip()

    def __init__(self, llm_client=None, max_retries: int = 3):
        self._llm = llm_client
        self._max_retries = max_retries

    def generate(self, blueprint: ComponentBlueprint) -> str:
        """Generate and validate a lifecycle script for the given blueprint.

        Returns a syntactically valid Python script string.
        Raises ScriptGenerationError if all retries fail.
        """
        if self._llm is not None:
            return self._generate_with_llm(blueprint)
        return self._generate_template(blueprint)

    # ------------------------------------------------------------------
    # Template-based stub (used when no LLM is configured)
    # ------------------------------------------------------------------

    def _generate_template(self, blueprint: ComponentBlueprint) -> str:
        """Generate a minimal but syntactically valid script from the blueprint."""
        lines: list[str] = [
            f'# Component: {blueprint.component_name}',
            f'# Kind: {blueprint.kind}',
            f'# {blueprint.description}',
            '',
        ]

        # on_init — always included
        lines += [
            'def on_init(game):',
        ]
        if blueprint.initial_properties:
            for key, value in blueprint.initial_properties.items():
                lines.append(f'    game.set_property(game.self, {key!r}, {value!r})')
        else:
            lines.append('    pass')
        lines.append('')

        # on_event — only if needed
        if blueprint.needs_on_event:
            lines += [
                'def on_event(event, game):',
            ]
            if blueprint.event_subscriptions:
                for i, event_type in enumerate(blueprint.event_subscriptions):
                    keyword = 'if' if i == 0 else 'elif'
                    lines += [
                        f'    {keyword} event.type == {event_type!r}:',
                        '        pass  # TODO: implement event logic',
                    ]
            else:
                lines.append('    pass')
            lines.append('')

        # on_update — only if needed
        if blueprint.needs_on_update:
            lines += [
                'def on_update(game):',
                '    pass  # TODO: implement update logic',
                '',
            ]

        return '\n'.join(lines)

    # ------------------------------------------------------------------
    # LLM path (production)
    # ------------------------------------------------------------------

    def _generate_with_llm(self, blueprint: ComponentBlueprint) -> str:
        """Call the LLM with a structured prompt and validate the result.

        This method is synchronous. For async LLM calls, subclass and
        override, or call from an async endpoint via run_in_executor.
        """
        prompt = self._build_prompt(blueprint)

        last_error: Optional[str] = None
        for attempt in range(1, self._max_retries + 1):
            try:
                raw = self._call_llm(prompt, last_error=last_error)
                script = self._extract_code(raw)
                self._validate_script(script)
                return script
            except Exception as exc:
                last_error = str(exc)

        raise ScriptGenerationError(
            f"Failed to generate a valid script for '{blueprint.component_name}' "
            f"after {self._max_retries} attempts. Last error: {last_error}"
        )

    def _build_prompt(self, blueprint: ComponentBlueprint) -> str:
        node_ctx = ""
        if blueprint.node_summary:
            node_ctx = "\n\nNode graph summary:\n" + "\n".join(
                f"  - [{n['type']}] {n['label']}" for n in blueprint.node_summary
            )

        props_ctx = ""
        if blueprint.initial_properties:
            props_ctx = "\n\nInitial properties:\n" + "\n".join(
                f"  - {k}: {v!r}" for k, v in blueprint.initial_properties.items()
            )

        events_ctx = ""
        if blueprint.event_subscriptions:
            events_ctx = "\n\nEvent subscriptions: " + ", ".join(blueprint.event_subscriptions)

        hooks = []
        if blueprint.needs_on_init:
            hooks.append("on_init(game)")
        if blueprint.needs_on_event:
            hooks.append("on_event(event, game)")
        if blueprint.needs_on_update:
            hooks.append("on_update(game)")

        return textwrap.dedent(f"""
            You are a game scripting assistant. Write a Python lifecycle script for a game component.

            {self.GAMEAPI_CONTEXT}

            Component name: {blueprint.component_name}
            Component kind: {blueprint.kind}
            Description: {blueprint.description}
            Required hooks: {", ".join(hooks)}{node_ctx}{props_ctx}{events_ctx}

            Rules:
            - Only use the GameAPI (`game` object) — no imports, no global/nonlocal
            - Use only: len, range, min, max, sum, abs, any, all, sorted, list, dict, set,
              filter, map, enumerate, zip, reversed, int, float, str, bool, round, isinstance
            - Keep logic concise and correct
            - Return ONLY the Python code, no markdown fences

            Write the script:
        """).strip()

    def _call_llm(self, prompt: str, last_error: Optional[str] = None) -> str:
        """Synchronous LLM call. Override in subclasses for different providers."""
        # Placeholder — replace with your LLM SDK call
        raise NotImplementedError("LLM client not configured")

    def _extract_code(self, raw: str) -> str:
        """Strip markdown fences from LLM output if present."""
        raw = raw.strip()
        if raw.startswith("```"):
            lines = raw.split("\n")
            # Remove opening fence (```python or ```)
            lines = lines[1:]
            # Remove closing fence
            if lines and lines[-1].strip().startswith("```"):
                lines = lines[:-1]
            return "\n".join(lines).strip()
        return raw

    def _validate_script(self, script: str) -> None:
        """Use ScriptRunner.validate() to check the script."""
        try:
            from TeapotEngine.core.ScriptRunner import ScriptRunner, ScriptValidationError
            runner = ScriptRunner()
            runner.validate(script)
        except ImportError:
            # TeapotEngine not installed in API env; fall back to ast-only check
            import ast
            ast.parse(script)
