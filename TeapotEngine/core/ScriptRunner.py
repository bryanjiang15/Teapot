"""
ScriptRunner — restricted Python sandbox for component lifecycle scripts.

Security model
--------------
Scripts are AST-parsed before execution. Any forbidden node type
(import, global, nonlocal) causes validate() to raise ScriptValidationError.
At runtime the script executes in a namespace containing only:
  - `game`  : the GameAPI instance
  - a small set of safe builtins (no __import__, no open, no exec, etc.)

Performance
-----------
Compiled code objects are cached by script text so each unique script
is compiled only once per ScriptRunner lifetime.
"""
from __future__ import annotations

import ast
import builtins
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .GameAPI import GameAPI
    from .Events import Event


# ---------------------------------------------------------------------------
# Safety constants
# ---------------------------------------------------------------------------

_SAFE_BUILTIN_NAMES: frozenset[str] = frozenset({
    "len", "range", "min", "max", "sum", "abs", "round",
    "any", "all", "sorted", "list", "dict", "set", "tuple",
    "filter", "map", "enumerate", "zip", "reversed",
    "int", "float", "str", "bool",
    "True", "False", "None",
    "print",       # useful for debugging; can be removed in production
    "isinstance", "type",
})

_SAFE_BUILTINS: dict[str, Any] = {
    name: getattr(builtins, name)
    for name in _SAFE_BUILTIN_NAMES
    if hasattr(builtins, name)
}

_FORBIDDEN_NODE_TYPES: frozenset[type] = frozenset({
    ast.Import,
    ast.ImportFrom,
    ast.Global,
    ast.Nonlocal,
})


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class ScriptValidationError(Exception):
    """Raised by validate() when a script contains unsafe constructs."""
    pass


class ScriptRuntimeError(Exception):
    """Wraps an exception raised during script execution."""
    def __init__(self, component_name: str, hook: str, original: Exception):
        self.component_name = component_name
        self.hook = hook
        self.original = original
        super().__init__(
            f"[{component_name}] {hook}() raised {type(original).__name__}: {original}"
        )


# ---------------------------------------------------------------------------
# ScriptRunner
# ---------------------------------------------------------------------------

class ScriptRunner:
    """Compile, validate, and execute component lifecycle scripts."""

    def __init__(self):
        self._compile_cache: dict[str, Any] = {}  # script_text → compiled code object

    # ------------------------------------------------------------------
    # Validation (call before storing or running a script)
    # ------------------------------------------------------------------

    def validate(self, script: str) -> None:
        """Parse and static-check the script.

        Raises ScriptValidationError if the script contains forbidden
        constructs (imports, global/nonlocal statements) or syntax errors.
        """
        try:
            tree = ast.parse(script)
        except SyntaxError as exc:
            raise ScriptValidationError(f"Syntax error: {exc}") from exc

        for node in ast.walk(tree):
            if type(node) in _FORBIDDEN_NODE_TYPES:
                raise ScriptValidationError(
                    f"Forbidden construct: {type(node).__name__} "
                    f"at line {getattr(node, 'lineno', '?')}"
                )

    # ------------------------------------------------------------------
    # Lifecycle hook dispatchers
    # ------------------------------------------------------------------

    def call_on_init(self, script: str, api: "GameAPI") -> None:
        """Execute the on_init(game) hook if it is defined in the script."""
        ns = self._exec_script(script, api)
        hook = ns.get("on_init")
        if callable(hook):
            hook(api)

    def call_on_event(self, script: str, event: "Event", api: "GameAPI") -> None:
        """Execute the on_event(event, game) hook if defined."""
        ns = self._exec_script(script, api)
        hook = ns.get("on_event")
        if callable(hook):
            hook(event, api)

    def call_on_update(self, script: str, api: "GameAPI") -> None:
        """Execute the on_update(game) hook if defined."""
        ns = self._exec_script(script, api)
        hook = ns.get("on_update")
        if callable(hook):
            hook(api)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _compile(self, script: str):
        """Return a cached compiled code object for the script."""
        if script not in self._compile_cache:
            try:
                self._compile_cache[script] = compile(
                    ast.parse(script), "<component_script>", "exec"
                )
            except SyntaxError as exc:
                raise ScriptValidationError(f"Syntax error during compile: {exc}") from exc
        return self._compile_cache[script]

    def _make_namespace(self, api: "GameAPI") -> dict[str, Any]:
        return {
            "__builtins__": _SAFE_BUILTINS,
            "game": api,
        }

    def _exec_script(self, script: str, api: "GameAPI") -> dict[str, Any]:
        """Execute a script and return its namespace (which contains the hook functions)."""
        code = self._compile(script)
        ns = self._make_namespace(api)
        exec(code, ns)  # noqa: S102  (intentional sandbox exec)
        return ns
