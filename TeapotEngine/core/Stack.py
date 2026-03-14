"""
EventStack — LIFO stack for managing event resolution order.
"""
from __future__ import annotations

from typing import Optional

from .Events import StackItem


class EventStack:
    """LIFO stack for managing event resolution."""

    def __init__(self):
        self.items: list[StackItem] = []
        self._order_counter: int = 0

    def push(self, item: StackItem) -> None:
        self.items.append(item)

    def push_multiple(self, items: list[StackItem]) -> None:
        for item in items:
            self.push(item)

    def pop(self) -> Optional[StackItem]:
        return self.items.pop() if self.items else None

    def peek(self) -> Optional[StackItem]:
        return self.items[-1] if self.items else None

    def is_empty(self) -> bool:
        return len(self.items) == 0

    def size(self) -> int:
        return len(self.items)

    def clear(self) -> None:
        self.items.clear()

    def get_next_order(self) -> int:
        self._order_counter += 1
        return self._order_counter
