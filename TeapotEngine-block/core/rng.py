"""
Deterministic random number generator for game engine
"""

import random
from typing import List, Any


class DeterministicRNG:
    """Deterministic RNG seeded per match for reproducible games"""
    
    def __init__(self, seed: int):
        self.seed = seed
        self.rng = random.Random(seed)
    
    def random(self) -> float:
        """Get a random float between 0.0 and 1.0"""
        return self.rng.random()
    
    def randint(self, a: int, b: int) -> int:
        """Get a random integer between a and b (inclusive)"""
        return self.rng.randint(a, b)
    
    def choice(self, seq: List[Any]) -> Any:
        """Choose a random element from a sequence"""
        return self.rng.choice(seq)
    
    def shuffle(self, x: List[Any]) -> None:
        """Shuffle a list in place"""
        self.rng.shuffle(x)
    
    def sample(self, population: List[Any], k: int) -> List[Any]:
        """Get k random samples from population"""
        return self.rng.sample(population, k)
    
    def getstate(self) -> tuple:
        """Get the current state of the RNG"""
        return self.rng.getstate()
    
    def setstate(self, state: tuple) -> None:
        """Set the state of the RNG"""
        self.rng.setstate(state)
    
    def reseed(self, new_seed: int) -> None:
        """Reseed the RNG with a new seed"""
        self.seed = new_seed
        self.rng.seed(new_seed)
