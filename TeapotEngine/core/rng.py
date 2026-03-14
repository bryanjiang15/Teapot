"""
DeterministicRNG — seeded random number generator for reproducible games.

One instance lives on MatchActor and is passed to GameAPI so all
randomness in scripts goes through a single, seedable source.
"""
from __future__ import annotations

import random
from typing import Any


class DeterministicRNG:
    """Deterministic RNG seeded per match for reproducible replays."""

    def __init__(self, seed: int):
        self.seed = seed
        self._rng = random.Random(seed)

    def random(self) -> float:
        return self._rng.random()

    def randint(self, a: int, b: int) -> int:
        return self._rng.randint(a, b)

    def choice(self, seq: list[Any]) -> Any:
        return self._rng.choice(seq)

    def shuffle(self, x: list[Any]) -> None:
        self._rng.shuffle(x)

    def sample(self, population: list[Any], k: int) -> list[Any]:
        return self._rng.sample(population, k)

    def getstate(self) -> tuple:
        return self._rng.getstate()

    def setstate(self, state: tuple) -> None:
        self._rng.setstate(state)

    def reseed(self, new_seed: int) -> None:
        self.seed = new_seed
        self._rng.seed(new_seed)
