"""
Data Generator Module
======================
Generates test datasets for sorting algorithm analysis.
"""

import random
from typing import List


class DataGenerator:
    """Generates different types of test datasets."""
    
    @staticmethod
    def random(size: int) -> List[int]:
        """Generate random integers from -10000 to 10000."""
        return [random.randint(-10000, 10000) for _ in range(size)]
    
    @staticmethod
    def reverse(size: int) -> List[int]:
        """Generate reverse-sorted data (worst case for some algorithms)."""
        return list(range(size, 0, -1))
    
    @staticmethod
    def partial(size: int) -> List[int]:
        """Generate 90% sorted data with 10% random swaps."""
        data = list(range(size))
        swaps = int(size * 0.1)
        for _ in range(swaps):
            i, j = random.randint(0, size-1), random.randint(0, size-1)
            data[i], data[j] = data[j], data[i]
        return data


# Dataset type mappings
DATASET_TYPES = {
    "Random": DataGenerator.random,
    "Reverse Sorted": DataGenerator.reverse,
    "Partially Sorted": DataGenerator.partial,
}
