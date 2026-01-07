"""
GUI Module - Enhanced Algorithm Visualizations
================================================
Each algorithm shows its key concept visually.
Heap Sort includes a tree structure view!
"""

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import random
import numpy as np


class SortingVisualization(ctk.CTkToplevel):
    """Step-by-step visualization with algorithm-specific highlights."""
    
    COLORS = {
        'bg': '#0d1117',
        'bar_normal': '#58a6ff',
        'bar_comparing': '#f85149',
        'bar_swapping': '#3fb950',
        'bar_sorted': '#a371f7',
        'bar_pivot': '#ff6b6b',
        'bar_gap': '#ffd93d',
        'bar_merging': '#4ecdc4',
    }
    
    def __init__(self, parent, algorithm_name: str, algorithm_info: dict):
        super().__init__(parent)
        
        self.algorithm_name = algorithm_name
        self.algorithm_info = algorithm_info
        self.title(f"{algorithm_name} - Step by Step Visualization")
        
        # Larger window for Heap Sort (has tree view)
        if algorithm_name == "Heap Sort":
            self.geometry("1000x900")
        else:
            self.geometry("950x800")
        
        self.configure(fg_color=self.COLORS['bg'])
        
        self.array = [random.randint(5, 50) for _ in range(10 if algorithm_name == "Heap Sort" else 12)]
        self.original_array = self.array.copy()
        
        self.is_running = False
        self.current_step = 0
        self.steps = []
        self.animation_speed = 0.5
        
        self._create_ui()
        self._generate_steps()
        self._draw_bars(self.array, {})
        
        self.step_label.configure(text=f"Step: 0 / {len(self.steps)}")
        self.action_label.configure(text="Press STEP or AUTO PLAY to begin")
    
    def _create_ui(self):
        header = ctk.CTkFrame(self, fg_color="#161b22", height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkLabel(header, text=f"{self.algorithm_name} Visualization",
                    font=ctk.CTkFont(size=22, weight="bold"), text_color="#58a6ff").pack(pady=15)
        
        # Chart area
        chart_frame = ctk.CTkFrame(self, fg_color=self.COLORS['bg'])
        chart_frame.pack(fill="both", expand=True, padx=15, pady=5)
        
        if self.algorithm_name == "Heap Sort":
            # Two plots: tree on top, bars on bottom
            self.fig = Figure(figsize=(11, 6), facecolor=self.COLORS['bg'])
            self.ax_tree = self.fig.add_subplot(211)  # Tree view
            self.ax = self.fig.add_subplot(212)        # Bar view
            self.ax_tree.set_facecolor(self.COLORS['bg'])
            self.fig.subplots_adjust(hspace=0.3)
        else:
            self.fig = Figure(figsize=(10, 4), facecolor=self.COLORS['bg'])
            self.ax = self.fig.add_subplot(111)
            self.ax_tree = None
        
        self.ax.set_facecolor(self.COLORS['bg'])
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Info panel
        info_frame = ctk.CTkFrame(self, fg_color="#161b22", corner_radius=10)
        info_frame.pack(fill="x", padx=15, pady=5)
        
        self.step_label = ctk.CTkLabel(info_frame, text="Step: 0 / 0",
                                       font=ctk.CTkFont(size=16, weight="bold"))
        self.step_label.pack(pady=(8, 3))
        
        self.action_label = ctk.CTkLabel(info_frame, text="Ready...",
                                         font=ctk.CTkFont(size=13), text_color="#ffffff")
        self.action_label.pack(pady=(0, 8))
        
        legend_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        legend_frame.pack(pady=(0, 8))
        self._create_legend(legend_frame)
        
        # Controls
        ctrl_frame = ctk.CTkFrame(self, fg_color="#161b22", corner_radius=10)
        ctrl_frame.pack(fill="x", padx=15, pady=5)
        
        btn_frame = ctk.CTkFrame(ctrl_frame, fg_color="transparent")
        btn_frame.pack(pady=12)
        
        self.step_btn = ctk.CTkButton(btn_frame, text="STEP →", width=120, height=42,
                                      font=ctk.CTkFont(size=15, weight="bold"),
                                      fg_color="#3fb950", command=self._step_forward)
        self.step_btn.pack(side="left", padx=6)
        
        self.play_btn = ctk.CTkButton(btn_frame, text="▶ AUTO", width=90, height=42,
                                      font=ctk.CTkFont(size=13, weight="bold"),
                                      fg_color="#58a6ff", command=self._toggle_auto)
        self.play_btn.pack(side="left", padx=6)
        
        ctk.CTkButton(btn_frame, text="↺ RESTART", width=90, height=42,
                     fg_color="#d29922", command=self._restart).pack(side="left", padx=6)
        
        ctk.CTkButton(btn_frame, text="Slower", width=60, height=42, fg_color="#30363d",
                     command=lambda: self._change_speed(0.15)).pack(side="left", padx=3)
        ctk.CTkButton(btn_frame, text="Faster", width=60, height=42, fg_color="#30363d",
                     command=lambda: self._change_speed(-0.15)).pack(side="left", padx=3)
        
        # Input row
        input_frame = ctk.CTkFrame(self, fg_color="#161b22", corner_radius=10)
        input_frame.pack(fill="x", padx=15, pady=5)
        
        inp_row = ctk.CTkFrame(input_frame, fg_color="transparent")
        inp_row.pack(pady=8)
        
        ctk.CTkLabel(inp_row, text="Numbers:").pack(side="left", padx=5)
        self.input_entry = ctk.CTkEntry(inp_row, width=220, placeholder_text="e.g., 8,3,5,1,9")
        self.input_entry.pack(side="left", padx=5)
        ctk.CTkButton(inp_row, text="Apply", width=55, fg_color="#3fb950", command=self._apply_custom).pack(side="left", padx=3)
        ctk.CTkButton(inp_row, text="Random", width=65, fg_color="#a371f7", command=self._randomize).pack(side="left", padx=3)
        
        # How it works
        how_frame = ctk.CTkFrame(self, fg_color="#161b22", corner_radius=10)
        how_frame.pack(fill="x", padx=15, pady=(5, 12))
        
        ctk.CTkLabel(how_frame, text=f"How {self.algorithm_name} Works:",
                    font=ctk.CTkFont(size=13, weight="bold"), text_color="#3fb950").pack(anchor="w", padx=12, pady=(8, 3))
        how_text = self.algorithm_info.get('how_it_works', '')
        ctk.CTkLabel(how_frame, text=how_text, font=ctk.CTkFont(size=11),
                    text_color="#8b949e", justify="left").pack(anchor="w", padx=12, pady=(0, 8))
    
    def _create_legend(self, parent):
        if self.algorithm_name == "Quick Sort":
            items = [("PIVOT", self.COLORS['bar_pivot']), ("Comparing", self.COLORS['bar_comparing']),
                    ("Swapping", self.COLORS['bar_swapping']), ("Sorted", self.COLORS['bar_sorted'])]
        elif self.algorithm_name == "Heap Sort":
            items = [("Root/Max", self.COLORS['bar_pivot']), ("Comparing", self.COLORS['bar_comparing']),
                    ("Swapping", self.COLORS['bar_swapping']), ("Sorted", self.COLORS['bar_sorted'])]
        elif self.algorithm_name == "Shell Sort":
            items = [("Gap Element", self.COLORS['bar_gap']), ("Comparing", self.COLORS['bar_comparing']),
                    ("Shifting", self.COLORS['bar_swapping']), ("Normal", self.COLORS['bar_normal'])]
        elif self.algorithm_name == "Merge Sort":
            items = [("Merging", self.COLORS['bar_merging']), ("Left Half", self.COLORS['bar_comparing']),
                    ("Right Half", self.COLORS['bar_gap']), ("Sorted", self.COLORS['bar_sorted'])]
        else:
            items = [("Current", self.COLORS['bar_pivot']), ("Placing", self.COLORS['bar_swapping']),
                    ("Normal", self.COLORS['bar_normal']), ("Sorted", self.COLORS['bar_sorted'])]
        
        for text, color in items:
            frame = ctk.CTkFrame(parent, fg_color="transparent")
            frame.pack(side="left", padx=8)
            ctk.CTkLabel(frame, text="■", font=ctk.CTkFont(size=14), text_color=color).pack(side="left")
            ctk.CTkLabel(frame, text=text, font=ctk.CTkFont(size=10)).pack(side="left", padx=2)
    
    def _draw_bars(self, array, highlights):
        self.ax.clear()
        self.ax.set_facecolor(self.COLORS['bg'])
        
        colors = []
        for i in range(len(array)):
            hl = highlights.get(i, 'normal')
            if hl == 'pivot':
                colors.append(self.COLORS['bar_pivot'])
            elif hl == 'comparing':
                colors.append(self.COLORS['bar_comparing'])
            elif hl == 'swapping':
                colors.append(self.COLORS['bar_swapping'])
            elif hl == 'sorted':
                colors.append(self.COLORS['bar_sorted'])
            elif hl == 'gap':
                colors.append(self.COLORS['bar_gap'])
            elif hl == 'merging':
                colors.append(self.COLORS['bar_merging'])
            else:
                colors.append(self.COLORS['bar_normal'])
        
        bars = self.ax.bar(range(len(array)), array, color=colors, edgecolor='white', linewidth=2, width=0.75)
        
        for i, (bar, val) in enumerate(zip(bars, array)):
            hl = highlights.get(i, '')
            
            self.ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                        str(val), ha='center', va='bottom', color='white', fontsize=10, fontweight='bold')
            
            if hl == 'pivot':
                self.ax.text(bar.get_x() + bar.get_width()/2, bar.get_height()/2,
                            'MAX', ha='center', va='center', color='white', fontsize=8, fontweight='bold')
            elif hl == 'gap':
                self.ax.text(bar.get_x() + bar.get_width()/2, bar.get_height()/2,
                            'GAP', ha='center', va='center', color='black', fontsize=8, fontweight='bold')
            elif hl == 'swapping':
                self.ax.text(bar.get_x() + bar.get_width()/2, bar.get_height()/2,
                            '<>', ha='center', va='center', color='white', fontsize=10, fontweight='bold')
            elif hl == 'sorted':
                self.ax.text(bar.get_x() + bar.get_width()/2, bar.get_height()/2,
                            'OK', ha='center', va='center', color='white', fontsize=8, fontweight='bold')
        
        self.ax.set_xlim(-0.5, len(array) - 0.5)
        self.ax.set_ylim(0, max(array) + 8)
        self.ax.set_xticks(range(len(array)))
        self.ax.set_xticklabels([str(i) for i in range(len(array))], color='#666', fontsize=9)
        self.ax.set_yticks([])
        self.ax.set_title("Array View", color='#888', fontsize=10, pad=5)
        for spine in self.ax.spines.values():
            spine.set_visible(False)
        
        # Draw tree for Heap Sort
        if self.ax_tree is not None:
            self._draw_heap_tree(array, highlights)
        
        self.canvas.draw()
    
    def _draw_heap_tree(self, array, highlights):
        """Draw binary heap as a tree structure."""
        self.ax_tree.clear()
        self.ax_tree.set_facecolor(self.COLORS['bg'])
        self.ax_tree.set_title("Heap Tree View (Parent > Children)", color='#3fb950', fontsize=11, fontweight='bold', pad=8)
        
        n = len(array)
        if n == 0:
            return
        
        # Calculate positions
        depth = int(np.log2(n)) + 1
        positions = {}
        
        # Calculate x,y for each node
        for i in range(n):
            level = int(np.log2(i + 1))
            nodes_at_level = 2 ** level
            pos_in_level = i - (2 ** level - 1)
            
            # X position: spread across width at each level
            x_spacing = 1.0 / (nodes_at_level + 1)
            x = x_spacing * (pos_in_level + 1)
            
            # Y position: top to bottom
            y = 1 - (level + 0.5) / (depth + 0.5)
            
            positions[i] = (x, y)
        
        # Draw edges first (lines between parent and children)
        for i in range(n):
            left = 2 * i + 1
            right = 2 * i + 2
            
            if left < n:
                self.ax_tree.plot([positions[i][0], positions[left][0]], 
                                 [positions[i][1], positions[left][1]], 
                                 color='#444', linewidth=2, zorder=1)
            if right < n:
                self.ax_tree.plot([positions[i][0], positions[right][0]], 
                                 [positions[i][1], positions[right][1]], 
                                 color='#444', linewidth=2, zorder=1)
        
        # Draw nodes
        for i in range(n):
            x, y = positions[i]
            hl = highlights.get(i, 'normal')
            
            # Node color based on highlight
            if hl == 'pivot':
                color = self.COLORS['bar_pivot']
            elif hl == 'comparing':
                color = self.COLORS['bar_comparing']
            elif hl == 'swapping':
                color = self.COLORS['bar_swapping']
            elif hl == 'sorted':
                color = self.COLORS['bar_sorted']
            else:
                color = self.COLORS['bar_normal']
            
            # Draw circle node
            circle = plt.Circle((x, y), 0.04, color=color, ec='white', linewidth=2, zorder=2)
            self.ax_tree.add_patch(circle)
            
            # Node value
            self.ax_tree.text(x, y, str(array[i]), ha='center', va='center',
                            color='white', fontsize=10, fontweight='bold', zorder=3)
            
            # Index below node
            self.ax_tree.text(x, y - 0.08, f'[{i}]', ha='center', va='top',
                            color='#666', fontsize=7, zorder=3)
        
        self.ax_tree.set_xlim(0, 1)
        self.ax_tree.set_ylim(0, 1)
        self.ax_tree.set_xticks([])
        self.ax_tree.set_yticks([])
        for spine in self.ax_tree.spines.values():
            spine.set_visible(False)
    
    def _generate_steps(self):
        arr = self.array.copy()
        self.steps = []
        
        if self.algorithm_name == "Quick Sort":
            self._gen_quicksort(arr, 0, len(arr)-1, set())
        elif self.algorithm_name == "Heap Sort":
            self._gen_heapsort(arr)
        elif self.algorithm_name == "Shell Sort":
            self._gen_shellsort(arr)
        elif self.algorithm_name == "Merge Sort":
            self._gen_mergesort(arr, 0, len(arr), set())
        else:
            self._gen_radixsort(arr)
        
        self.steps.append((arr.copy(), {i: 'sorted' for i in range(len(arr))}, "Sorting Complete!"))
    
    def _gen_quicksort(self, arr, lo, hi, sorted_set):
        if lo < hi:
            pivot_idx = hi
            pivot_val = arr[pivot_idx]
            hl = {pivot_idx: 'pivot'}
            hl.update({i: 'sorted' for i in sorted_set})
            self.steps.append((arr.copy(), hl, f"PIVOT selected: {pivot_val}"))
            
            i = lo - 1
            for j in range(lo, hi):
                hl = {pivot_idx: 'pivot', j: 'comparing'}
                hl.update({k: 'sorted' for k in sorted_set})
                self.steps.append((arr.copy(), hl, f"Compare {arr[j]} with PIVOT {pivot_val}"))
                
                if arr[j] <= pivot_val:
                    i += 1
                    if i != j:
                        arr[i], arr[j] = arr[j], arr[i]
                        hl = {pivot_idx: 'pivot', i: 'swapping', j: 'swapping'}
                        hl.update({k: 'sorted' for k in sorted_set})
                        self.steps.append((arr.copy(), hl, f"Swap {arr[j]} and {arr[i]}"))
            
            arr[i+1], arr[hi] = arr[hi], arr[i+1]
            sorted_set.add(i+1)
            hl = {i+1: 'sorted'}
            hl.update({k: 'sorted' for k in sorted_set})
            self.steps.append((arr.copy(), hl, f"PIVOT placed at position {i+1}"))
            
            self._gen_quicksort(arr, lo, i, sorted_set)
            self._gen_quicksort(arr, i+2, hi, sorted_set)
    
    def _gen_heapsort(self, arr):
        n = len(arr)
        sorted_set = set()
        
        self.steps.append((arr.copy(), {0: 'pivot'}, "Building MAX HEAP (parent > children)"))
        
        for i in range(n//2 - 1, -1, -1):
            self._heapify(arr, n, i, sorted_set)
        
        self.steps.append((arr.copy(), {0: 'pivot'}, f"MAX HEAP ready! Root = {arr[0]} (largest)"))
        
        for i in range(n-1, 0, -1):
            hl = {0: 'pivot', i: 'comparing'}
            hl.update({k: 'sorted' for k in sorted_set})
            self.steps.append((arr.copy(), hl, f"Extract MAX {arr[0]} → move to position {i}"))
            
            arr[0], arr[i] = arr[i], arr[0]
            sorted_set.add(i)
            
            hl = {0: 'swapping', i: 'sorted'}
            hl.update({k: 'sorted' for k in sorted_set})
            self.steps.append((arr.copy(), hl, f"Swapped! Now heapify root..."))
            
            self._heapify(arr, i, 0, sorted_set)
    
    def _heapify(self, arr, n, i, sorted_set):
        largest = i
        l, r = 2*i+1, 2*i+2
        
        # Show comparison
        hl = {i: 'pivot'}
        if l < n: hl[l] = 'comparing'
        if r < n: hl[r] = 'comparing'
        hl.update({k: 'sorted' for k in sorted_set})
        self.steps.append((arr.copy(), hl, f"Heapify: check node {i} with children"))
        
        if l < n and arr[l] > arr[largest]: largest = l
        if r < n and arr[r] > arr[largest]: largest = r
        
        if largest != i:
            arr[i], arr[largest] = arr[largest], arr[i]
            hl = {i: 'swapping', largest: 'swapping'}
            hl.update({k: 'sorted' for k in sorted_set})
            self.steps.append((arr.copy(), hl, f"Swap {arr[i]} ↔ {arr[largest]}"))
            self._heapify(arr, n, largest, sorted_set)
    
    def _gen_shellsort(self, arr):
        n = len(arr)
        gap = 1
        while gap < n//3: gap = gap * 3 + 1
        
        while gap > 0:
            self.steps.append((arr.copy(), {}, f"GAP = {gap} (compare elements {gap} apart)"))
            
            for i in range(gap, n):
                temp = arr[i]
                j = i
                
                if j >= gap:
                    hl = {i: 'gap', j-gap: 'comparing'}
                    self.steps.append((arr.copy(), hl, f"Compare [{j}]={arr[j]} with [{j-gap}]={arr[j-gap]}"))
                
                while j >= gap and arr[j-gap] > temp:
                    hl = {j: 'swapping', j-gap: 'swapping'}
                    self.steps.append((arr.copy(), hl, f"Shift: {arr[j-gap]} moves right"))
                    arr[j] = arr[j-gap]
                    j -= gap
                
                arr[j] = temp
            gap //= 3
    
    def _gen_mergesort(self, arr, start, end, sorted_set):
        if end - start > 1:
            mid = (start + end) // 2
            
            hl = {i: 'comparing' for i in range(start, mid)}
            hl.update({i: 'gap' for i in range(mid, end)})
            self.steps.append((arr.copy(), hl, f"Split: Left[{start}:{mid}] Right[{mid}:{end}]"))
            
            self._gen_mergesort(arr, start, mid, sorted_set)
            self._gen_mergesort(arr, mid, end, sorted_set)
            
            left = arr[start:mid]
            right = arr[mid:end]
            i = j = 0
            k = start
            
            self.steps.append((arr.copy(), {}, f"Merge: {left} + {right}"))
            
            while i < len(left) and j < len(right):
                if left[i] <= right[j]:
                    arr[k] = left[i]; i += 1
                else:
                    arr[k] = right[j]; j += 1
                hl = {k: 'merging'}
                self.steps.append((arr.copy(), hl, f"Place {arr[k]}"))
                k += 1
            
            while i < len(left): arr[k] = left[i]; i += 1; k += 1
            while j < len(right): arr[k] = right[j]; j += 1; k += 1
    
    def _gen_radixsort(self, arr):
        if not arr or max(arr) == 0:
            return
        
        max_val = max(arr)
        exp = 1
        digit_pos = 1
        
        while max_val // exp > 0:
            self.steps.append((arr.copy(), {}, f"Sorting by DIGIT {digit_pos}"))
            
            output = sorted(arr, key=lambda x: (x // exp) % 10)
            
            for i in range(len(arr)):
                if arr[i] != output[i]:
                    arr[i] = output[i]
                    hl = {i: 'swapping'}
                    self.steps.append((arr.copy(), hl, f"Place {arr[i]}"))
            
            exp *= 10
            digit_pos += 1
    
    def _step_forward(self):
        if self.current_step >= len(self.steps):
            return
        
        arr, highlights, desc = self.steps[self.current_step]
        self._draw_bars(arr, highlights)
        self.step_label.configure(text=f"Step: {self.current_step + 1} / {len(self.steps)}")
        self.action_label.configure(text=desc)
        
        self.current_step += 1
        
        if self.current_step >= len(self.steps):
            self.step_btn.configure(state="disabled", text="DONE")
            self.play_btn.configure(state="disabled")
            self.is_running = False
    
    def _toggle_auto(self):
        if self.current_step >= len(self.steps):
            return
        
        self.is_running = not self.is_running
        
        if self.is_running:
            self.play_btn.configure(text="STOP", fg_color="#d29922")
            self.step_btn.configure(state="disabled")
            self._auto_play()
        else:
            self.play_btn.configure(text="AUTO", fg_color="#58a6ff")
            self.step_btn.configure(state="normal")
    
    def _auto_play(self):
        if not self.is_running or self.current_step >= len(self.steps):
            self.is_running = False
            self.play_btn.configure(text="AUTO", fg_color="#58a6ff")
            self.step_btn.configure(state="normal" if self.current_step < len(self.steps) else "disabled")
            return
        
        self._step_forward()
        
        if self.current_step < len(self.steps):
            self.after(int(self.animation_speed * 1000), self._auto_play)
    
    def _restart(self):
        self.is_running = False
        self.current_step = 0
        self.array = self.original_array.copy()
        self.steps = []
        self._generate_steps()
        self._draw_bars(self.array, {})
        
        self.step_btn.configure(state="normal", text="STEP")
        self.play_btn.configure(text="AUTO", fg_color="#58a6ff", state="normal")
        self.step_label.configure(text=f"Step: 0 / {len(self.steps)}")
        self.action_label.configure(text="Press STEP or AUTO to begin")
    
    def _change_speed(self, delta):
        self.animation_speed = max(0.1, min(1.5, self.animation_speed + delta))
    
    def _apply_custom(self):
        try:
            text = self.input_entry.get().strip()
            if text:
                numbers = [int(x.strip()) for x in text.split(',') if x.strip()]
                max_n = 10 if self.algorithm_name == "Heap Sort" else 15
                if 3 <= len(numbers) <= max_n:
                    self.array = numbers
                    self.original_array = numbers.copy()
                    self._restart()
        except ValueError:
            pass
    
    def _randomize(self):
        n = random.randint(7, 10) if self.algorithm_name == "Heap Sort" else random.randint(8, 12)
        self.array = [random.randint(5, 50) for _ in range(n)]
        self.original_array = self.array.copy()
        self._restart()


# Need to import plt for Circle
import matplotlib.pyplot as plt
