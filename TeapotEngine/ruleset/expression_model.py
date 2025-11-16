from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, Iterable, List, Literal, Optional, Protocol, Sequence, Union, Tuple, TYPE_CHECKING, Annotated
from pydantic import BaseModel, Field, ConfigDict

if TYPE_CHECKING:
    from core.component import Component
    from core.state import GameState

@dataclass
class EvalContext:
    source: "Component"
    event: Optional[Dict[str, Any]]
    targets: Sequence["Component"]
    game: "GameState"
    phase: str
    turn: int


# -------------------------
# Expression interfaces
# -------------------------
class Expr(Protocol):
    def evaluate(self, ctx: EvalContext) -> Any: ...
    def dependencies(self) -> Iterable[Tuple[str, str]]:  # (component_id, field)
        return ()

class BoolExpr(Expr, Protocol):
    def evaluate(self, ctx: EvalContext) -> bool: ...

class NumExpr(Expr, Protocol):
    def evaluate(self, ctx: EvalContext) -> int: ...

class SelectorExpr(Expr, Protocol):
    def evaluate(self, ctx: EvalContext) -> Iterable[Component]: ...


# -------------------------
# Numeric Expressions
# -------------------------
class ConstNumber(BaseModel):
    kind: Literal["const.number"]
    value: int

    def evaluate(self, ctx: EvalContext) -> int:
        return self.value

    def dependencies(self):  # no deps
        return ()

class PropNumber(BaseModel):
    """
    Path like ["self", "power"] or ["it", "power"].
    Here we'll support only ["self", field] for brevity; Filter will rewrite ctx.source.
    """
    kind: Literal["prop.number"]
    path: Tuple[Literal["self", "it"], str]

    def evaluate(self, ctx: EvalContext) -> int:
        root, field = self.path
        obj = ctx.source if root in ("self", "it") else None
        if obj is None:
            raise ValueError(f"Unsupported path root: {root}")
        return getattr(obj, field)

    def dependencies(self):
        # We don't know concrete component id at authoring time; at runtime you could
        # return (ctx.source.id, field). For a static AST, advertise a symbolic dep:
        yield ("<dynamic:current-source>", self.path[1])

class Add(BaseModel):
    kind: Literal["op.add"]
    a: "Num"
    b: "Num"

    def evaluate(self, ctx: EvalContext) -> int:
        return self.a.evaluate(ctx) + self.b.evaluate(ctx)

    def dependencies(self):
        yield from self.a.dependencies()
        yield from self.b.dependencies()

class Sub(BaseModel):
    kind: Literal["op.sub"]
    a: "Num"
    b: "Num"

    def evaluate(self, ctx: EvalContext) -> int:
        return self.a.evaluate(ctx) - self.b.evaluate(ctx)

    def dependencies(self):
        yield from self.a.dependencies()
        yield from self.b.dependencies()

Num = Annotated[Union[ConstNumber, PropNumber, Add, Sub], Field(discriminator="kind")]

# -------------------------
# Boolean Expressions
# -------------------------
class Gt(BaseModel):
    kind: Literal["pred.gt"]
    a: Num
    b: Num

    def evaluate(self, ctx: EvalContext) -> bool:
        return self.a.evaluate(ctx) > self.b.evaluate(ctx)

    def dependencies(self):
        yield from self.a.dependencies()
        yield from self.b.dependencies()

class And(BaseModel):
    kind: Literal["pred.and"]
    all: List["Predicate"]

    def evaluate(self, ctx: EvalContext) -> bool:
        for p in self.all:
            if not p.evaluate(ctx):
                return False
        return True

    def dependencies(self):
        for p in self.all:
            yield from p.dependencies()

Predicate = Annotated[Union[Gt, And], Field(discriminator="kind")]

# -------------------------
# Selector Expressions
# -------------------------
class ZoneSelector(BaseModel):
    kind: Literal["sel.zone"]
    name: str

    def evaluate(self, ctx: EvalContext) -> Iterable[Component]:
        # Resolve zone name to zone component ID and find all components of this zone name
        zone_component = ctx.game.find_zone_component_by_name(self.name)
        if zone_component is None:
            return []
        return list(ctx.game.get_components_by_zone(zone_component.id))

    def dependencies(self):
        # If you track deps for zones, you could announce ("<zone>", name)
        return ()

class FilterSelector(BaseModel):
    kind: Literal["sel.filter"]
    in_: "Selector"
    where: Predicate

    model_config = ConfigDict(
        populate_by_name=True  # allow 'in' in JSON
    )

    def evaluate(self, ctx: EvalContext) -> Iterable[Component]:
        result: List[Component] = []
        for c in self.in_.evaluate(ctx):
            # Rebind 'self/it' to the current candidate (classic map/filter pattern)
            subctx = EvalContext(
                source=c, event=ctx.event, targets=ctx.targets,
                game=ctx.game, phase=ctx.phase, turn=ctx.turn
            )
            if self.where.evaluate(subctx):
                result.append(c)
        return result

    def dependencies(self):
        # deps of input + deps of predicate
        yield from self.in_.dependencies()
        yield from self.where.dependencies()

class UnionSelector(BaseModel):
    kind: Literal["sel.union"]
    selectors: List["Selector"]

    def evaluate(self, ctx: EvalContext) -> Iterable[Component]:
        return list(set(c for s in self.selectors for c in s.evaluate(ctx)))

    def dependencies(self):
        for s in self.selectors:
            yield from s.dependencies()

Selector = Annotated[Union[ZoneSelector, FilterSelector, UnionSelector], Field(discriminator="kind")]
