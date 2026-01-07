"""
Sorting Algorithms Module
==========================

This module contains implementations of 5 sorting algorithms with optimizations
and comprehensive docstrings including Big-O complexity analysis.

Author: Sorting Algorithm Analysis System
"""

import sys

# Increase recursion limit for large datasets in recursive algorithms
sys.setrecursionlimit(20000)


class SortAlgorithms:
    """
    A class containing implementations of various sorting algorithms.
    
    All methods are static and return a sorted copy of the input array
    to preserve the original data for comparison purposes.
    """
    
    @staticmethod
    def quick_sort(arr: list) -> list:
        """
        Quick Sort implementation with median-of-three pivot selection.
        
        Time Complexity:
            - Best Case: O(n log n)
            - Average Case: O(n log n)
            - Worst Case: O(n²) - mitigated by median-of-three pivot
        
        Space Complexity: O(log n) for recursion stack
        
        Args:
            arr: List of integers to sort
            
        Returns:
            Sorted list of integers
        """
        arr = arr.copy()
        
        def median_of_three(a: list, low: int, high: int) -> int:
            """Select median of first, middle, and last elements as pivot."""
            mid = (low + high) // 2
            candidates = [(a[low], low), (a[mid], mid), (a[high], high)]
            candidates.sort(key=lambda x: x[0])
            return candidates[1][1]
        
        def partition(a: list, low: int, high: int) -> int:
            """Partition array around pivot using median-of-three."""
            pivot_idx = median_of_three(a, low, high)
            a[pivot_idx], a[high] = a[high], a[pivot_idx]
            pivot = a[high]
            i = low - 1
            
            for j in range(low, high):
                if a[j] <= pivot:
                    i += 1
                    a[i], a[j] = a[j], a[i]
            
            a[i + 1], a[high] = a[high], a[i + 1]
            return i + 1
        
        def quick_sort_helper(a: list, low: int, high: int) -> None:
            """Recursive helper function for quick sort."""
            if low < high:
                pi = partition(a, low, high)
                quick_sort_helper(a, low, pi - 1)
                quick_sort_helper(a, pi + 1, high)
        
        if len(arr) > 1:
            quick_sort_helper(arr, 0, len(arr) - 1)
        return arr
    
    @staticmethod
    def heap_sort(arr: list) -> list:
        """
        Heap Sort implementation using max-heap (in-place).
        
        Time Complexity:
            - Best Case: O(n log n)
            - Average Case: O(n log n)
            - Worst Case: O(n log n)
        
        Space Complexity: O(1) - in-place sorting
        
        Args:
            arr: List of integers to sort
            
        Returns:
            Sorted list of integers
        """
        arr = arr.copy()
        n = len(arr)
        
        def heapify(a: list, size: int, root: int) -> None:
            """Maintain max-heap property for subtree rooted at index root."""
            largest = root
            left = 2 * root + 1
            right = 2 * root + 2
            
            if left < size and a[left] > a[largest]:
                largest = left
            
            if right < size and a[right] > a[largest]:
                largest = right
            
            if largest != root:
                a[root], a[largest] = a[largest], a[root]
                heapify(a, size, largest)
        
        # Build max heap
        for i in range(n // 2 - 1, -1, -1):
            heapify(arr, n, i)
        
        # Extract elements from heap one by one
        for i in range(n - 1, 0, -1):
            arr[0], arr[i] = arr[i], arr[0]
            heapify(arr, i, 0)
        
        return arr
    
    @staticmethod
    def shell_sort(arr: list) -> list:
        """
        Shell Sort implementation using Knuth's gap sequence.
        
        Gap sequence: 3^k - 1 / 2 (1, 4, 13, 40, 121, ...)
        
        Time Complexity:
            - Best Case: O(n log n)
            - Average Case: O(n^1.25) to O(n^1.5)
            - Worst Case: O(n²) - depends on gap sequence
        
        Space Complexity: O(1) - in-place sorting
        
        Args:
            arr: List of integers to sort
            
        Returns:
            Sorted list of integers
        """
        arr = arr.copy()
        n = len(arr)
        
        # Calculate initial gap using Knuth's sequence
        gap = 1
        while gap < n // 3:
            gap = gap * 3 + 1
        
        # Perform gapped insertion sort
        while gap > 0:
            for i in range(gap, n):
                temp = arr[i]
                j = i
                
                while j >= gap and arr[j - gap] > temp:
                    arr[j] = arr[j - gap]
                    j -= gap
                
                arr[j] = temp
            
            gap //= 3
        
        return arr
    
    @staticmethod
    def merge_sort(arr: list) -> list:
        """
        Merge Sort implementation (stable, divide-and-conquer).
        
        Time Complexity:
            - Best Case: O(n log n)
            - Average Case: O(n log n)
            - Worst Case: O(n log n)
        
        Space Complexity: O(n) - requires auxiliary space for merging
        
        Args:
            arr: List of integers to sort
            
        Returns:
            Sorted list of integers
        """
        arr = arr.copy()
        
        def merge(a: list, left: int, mid: int, right: int) -> None:
            """Merge two sorted subarrays."""
            # Create temporary arrays
            left_half = a[left:mid + 1]
            right_half = a[mid + 1:right + 1]
            
            i = j = 0
            k = left
            
            # Merge the two halves
            while i < len(left_half) and j < len(right_half):
                if left_half[i] <= right_half[j]:
                    a[k] = left_half[i]
                    i += 1
                else:
                    a[k] = right_half[j]
                    j += 1
                k += 1
            
            # Copy remaining elements
            while i < len(left_half):
                a[k] = left_half[i]
                i += 1
                k += 1
            
            while j < len(right_half):
                a[k] = right_half[j]
                j += 1
                k += 1
        
        def merge_sort_helper(a: list, left: int, right: int) -> None:
            """Recursive helper function for merge sort."""
            if left < right:
                mid = (left + right) // 2
                merge_sort_helper(a, left, mid)
                merge_sort_helper(a, mid + 1, right)
                merge(a, left, mid, right)
        
        if len(arr) > 1:
            merge_sort_helper(arr, 0, len(arr) - 1)
        return arr
    
    @staticmethod
    def radix_sort(arr: list) -> list:
        """
        Radix Sort implementation using LSD (Least Significant Digit).
        
        This implementation handles non-negative integers only.
        Uses counting sort as the stable subroutine.
        
        Time Complexity:
            - Best Case: O(nk) where k is the number of digits
            - Average Case: O(nk)
            - Worst Case: O(nk)
        
        Space Complexity: O(n + k) where k is the range of digits (10 for decimal)
        
        Args:
            arr: List of non-negative integers to sort
            
        Returns:
            Sorted list of integers
        """
        if not arr:
            return arr.copy()
        
        arr = arr.copy()
        
        def counting_sort_by_digit(a: list, exp: int) -> None:
            """Counting sort based on digit at position exp."""
            n = len(a)
            output = [0] * n
            count = [0] * 10
            
            # Count occurrences of each digit
            for num in a:
                index = (num // exp) % 10
                count[index] += 1
            
            # Build cumulative count
            for i in range(1, 10):
                count[i] += count[i - 1]
            
            # Build output array (traverse from right to maintain stability)
            for i in range(n - 1, -1, -1):
                index = (a[i] // exp) % 10
                output[count[index] - 1] = a[i]
                count[index] -= 1
            
            # Copy output back to original array
            for i in range(n):
                a[i] = output[i]
        
        # Find maximum value to determine number of digits
        max_val = max(arr)
        
        # Apply counting sort for each digit position
        exp = 1
        while max_val // exp > 0:
            counting_sort_by_digit(arr, exp)
            exp *= 10
        
        return arr


# Dictionary mapping algorithm names to their functions
ALGORITHM_MAP = {
    "Quick Sort": SortAlgorithms.quick_sort,
    "Heap Sort": SortAlgorithms.heap_sort,
    "Shell Sort": SortAlgorithms.shell_sort,
    "Merge Sort": SortAlgorithms.merge_sort,
    "Radix Sort": SortAlgorithms.radix_sort,
}

ALGORITHM_NAMES = list(ALGORITHM_MAP.keys())
