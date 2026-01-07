"""
Performance Analyzer Module
============================

This module provides utilities for measuring the performance of sorting algorithms
including execution time and memory usage.

Author: Sorting Algorithm Analysis System
"""

import time
import tracemalloc
from typing import Callable, Dict, List, Any
from dataclasses import dataclass


@dataclass
class PerformanceResult:
    """
    Data class to store performance metrics for a sorting operation.
    
    Attributes:
        algorithm_name: Name of the sorting algorithm
        time_ms: Execution time in milliseconds
        memory_kb: Peak memory usage in kilobytes
        data_size: Size of the input data
        data_type: Type of data (Random, Reverse, Partial)
        success: Whether the sort completed successfully
        error_message: Error message if sort failed
    """
    algorithm_name: str
    time_ms: float
    memory_kb: float
    data_size: int
    data_type: str
    success: bool = True
    error_message: str = ""
    
    @property
    def time_seconds(self) -> float:
        """Return execution time in seconds."""
        return self.time_ms / 1000
    
    @property
    def memory_mb(self) -> float:
        """Return memory usage in megabytes."""
        return self.memory_kb / 1024
    
    def format_time(self) -> str:
        """Format time with appropriate unit."""
        if self.time_ms >= 1000:
            return f"{self.time_seconds:.2f}s"
        return f"{self.time_ms:.2f}ms"
    
    def format_memory(self) -> str:
        """Format memory with appropriate unit."""
        if self.memory_kb >= 1024:
            return f"{self.memory_mb:.2f} MB"
        return f"{self.memory_kb:.2f} KB"
    
    def __str__(self) -> str:
        if not self.success:
            return f"{self.algorithm_name}: ERROR - {self.error_message}"
        return f"{self.algorithm_name}: {self.format_time()}, {self.format_memory()}"


class PerformanceAnalyzer:
    """
    A class for measuring sorting algorithm performance.
    
    Uses time.perf_counter() for precise timing and tracemalloc
    for memory usage measurement.
    """
    
    @staticmethod
    def measure_sort(
        sort_function: Callable[[List[int]], List[int]],
        data: List[int],
        algorithm_name: str,
        data_type: str
    ) -> PerformanceResult:
        """
        Measure the performance of a sorting function.
        
        Args:
            sort_function: The sorting function to measure
            data: The input data to sort
            algorithm_name: Name of the algorithm for reporting
            data_type: Type of data for reporting
            
        Returns:
            PerformanceResult containing timing and memory metrics
        """
        data_copy = data.copy()
        data_size = len(data)
        
        try:
            # Start memory tracking
            tracemalloc.start()
            
            # Measure execution time
            start_time = time.perf_counter()
            sorted_data = sort_function(data_copy)
            end_time = time.perf_counter()
            
            # Get memory usage
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            # Calculate metrics
            time_ms = (end_time - start_time) * 1000
            memory_kb = peak / 1024
            
            # Verify sorting was successful
            if not PerformanceAnalyzer._verify_sorted(sorted_data):
                return PerformanceResult(
                    algorithm_name=algorithm_name,
                    time_ms=time_ms,
                    memory_kb=memory_kb,
                    data_size=data_size,
                    data_type=data_type,
                    success=False,
                    error_message="Sorting verification failed"
                )
            
            return PerformanceResult(
                algorithm_name=algorithm_name,
                time_ms=time_ms,
                memory_kb=memory_kb,
                data_size=data_size,
                data_type=data_type,
                success=True
            )
            
        except Exception as e:
            # Ensure tracemalloc is stopped even on error
            if tracemalloc.is_tracing():
                tracemalloc.stop()
            
            return PerformanceResult(
                algorithm_name=algorithm_name,
                time_ms=0,
                memory_kb=0,
                data_size=data_size,
                data_type=data_type,
                success=False,
                error_message=str(e)
            )
    
    @staticmethod
    def _verify_sorted(arr: List[int]) -> bool:
        """Verify that an array is correctly sorted in ascending order."""
        for i in range(len(arr) - 1):
            if arr[i] > arr[i + 1]:
                return False
        return True
    
    @staticmethod
    def run_analysis(
        algorithms: Dict[str, Callable],
        data: List[int],
        data_type: str,
        progress_callback: Callable[[str, int, int], None] = None
    ) -> List[PerformanceResult]:
        """
        Run performance analysis on multiple algorithms.
        
        Args:
            algorithms: Dictionary mapping algorithm names to functions
            data: Input data to sort
            data_type: Type of data for reporting
            progress_callback: Optional callback for progress updates
                              (algorithm_name, current_index, total_count)
            
        Returns:
            List of PerformanceResult for each algorithm
        """
        results = []
        total = len(algorithms)
        
        for idx, (name, func) in enumerate(algorithms.items()):
            if progress_callback:
                progress_callback(name, idx + 1, total)
            
            result = PerformanceAnalyzer.measure_sort(func, data, name, data_type)
            results.append(result)
        
        return results
