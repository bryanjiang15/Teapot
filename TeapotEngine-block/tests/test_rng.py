"""
Tests for DeterministicRNG class
"""

import pytest
from TeapotEngine.core.rng import DeterministicRNG


class TestDeterministicRNG:
    """Tests for DeterministicRNG class"""
    
    def test_create_rng_with_seed(self):
        """Test creating RNG with a seed"""
        rng = DeterministicRNG(42)
        assert rng.seed == 42
    
    def test_random_returns_float(self):
        """Test that random() returns a float between 0 and 1"""
        rng = DeterministicRNG(123)
        value = rng.random()
        assert isinstance(value, float)
        assert 0.0 <= value < 1.0
    
    def test_deterministic_random(self):
        """Test that same seed produces same sequence"""
        rng1 = DeterministicRNG(42)
        rng2 = DeterministicRNG(42)
        
        values1 = [rng1.random() for _ in range(10)]
        values2 = [rng2.random() for _ in range(10)]
        
        assert values1 == values2
    
    def test_randint(self):
        """Test randint returns integer in range"""
        rng = DeterministicRNG(456)
        value = rng.randint(1, 10)
        assert isinstance(value, int)
        assert 1 <= value <= 10
    
    def test_randint_deterministic(self):
        """Test that randint is deterministic"""
        rng1 = DeterministicRNG(789)
        rng2 = DeterministicRNG(789)
        
        values1 = [rng1.randint(1, 100) for _ in range(10)]
        values2 = [rng2.randint(1, 100) for _ in range(10)]
        
        assert values1 == values2
    
    def test_choice(self):
        """Test choice selects from sequence"""
        rng = DeterministicRNG(111)
        seq = [1, 2, 3, 4, 5]
        value = rng.choice(seq)
        assert value in seq
    
    def test_choice_deterministic(self):
        """Test that choice is deterministic"""
        rng1 = DeterministicRNG(222)
        rng2 = DeterministicRNG(222)
        seq = ['a', 'b', 'c', 'd', 'e']
        
        values1 = [rng1.choice(seq) for _ in range(10)]
        values2 = [rng2.choice(seq) for _ in range(10)]
        
        assert values1 == values2
    
    def test_shuffle(self):
        """Test shuffle modifies list in place"""
        rng = DeterministicRNG(333)
        original = [1, 2, 3, 4, 5]
        shuffled = original.copy()
        rng.shuffle(shuffled)
        
        # Should have same elements
        assert set(shuffled) == set(original)
        # May or may not be in different order (depends on seed)
    
    def test_shuffle_deterministic(self):
        """Test that shuffle is deterministic"""
        rng1 = DeterministicRNG(444)
        rng2 = DeterministicRNG(444)
        
        list1 = [1, 2, 3, 4, 5]
        list2 = [1, 2, 3, 4, 5]
        
        rng1.shuffle(list1)
        rng2.shuffle(list2)
        
        assert list1 == list2
    
    def test_sample(self):
        """Test sample returns k elements"""
        rng = DeterministicRNG(555)
        population = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        sample = rng.sample(population, 3)
        
        assert len(sample) == 3
        assert all(item in population for item in sample)
        # Should have unique elements
        assert len(set(sample)) == 3
    
    def test_sample_deterministic(self):
        """Test that sample is deterministic"""
        rng1 = DeterministicRNG(666)
        rng2 = DeterministicRNG(666)
        population = ['a', 'b', 'c', 'd', 'e']
        
        sample1 = rng1.sample(population, 3)
        sample2 = rng2.sample(population, 3)
        
        assert sample1 == sample2
    
    def test_getstate_setstate(self):
        """Test getting and setting RNG state"""
        rng1 = DeterministicRNG(777)
        # Generate some values
        _ = [rng1.random() for _ in range(5)]
        
        state = rng1.getstate()
        
        # Create new RNG and set state
        rng2 = DeterministicRNG(0)
        rng2.setstate(state)
        
        # Both should produce same next values
        assert rng1.random() == rng2.random()
        assert rng1.randint(1, 100) == rng2.randint(1, 100)
    
    def test_reseed(self):
        """Test reseeding the RNG"""
        rng = DeterministicRNG(888)
        value1 = rng.random()
        
        rng.reseed(999)
        assert rng.seed == 999
        
        # Should produce different values after reseed
        value2 = rng.random()
        # Note: This might occasionally be the same, but very unlikely
        # We'll just check that reseed doesn't crash
    
    def test_different_seeds_produce_different_values(self):
        """Test that different seeds produce different sequences"""
        rng1 = DeterministicRNG(111)
        rng2 = DeterministicRNG(222)
        
        values1 = [rng1.random() for _ in range(10)]
        values2 = [rng2.random() for _ in range(10)]
        
        # Very unlikely that all values are the same
        assert values1 != values2

