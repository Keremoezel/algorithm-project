"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║     SORTING ALGORITHMS PERFORMANCE ANALYSIS SYSTEM - ULTIMATE EDITION         ║
║                      University Term Project 2025                              ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Main GUI Application - Uses separate modules for better organization:
  - algorithms.py: Sorting algorithm implementations
  - data_generator.py: Test data generation
  - gui.py: Visualization components
"""

import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import random
import time
import tracemalloc
import sys
import threading
import numpy as np
from dataclasses import dataclass

# Import from project modules
from algorithms import SortAlgorithms, ALGORITHM_MAP
from data_generator import DataGenerator, DATASET_TYPES
from gui import SortingVisualization

sys.setrecursionlimit(100000)
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")


# ═══════════════════════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════
@dataclass
class AlgorithmInfo:
    name: str
    description: str
    time_best: str
    time_avg: str
    time_worst: str
    space: str
    stable: bool
    in_place: bool
    how_it_works: str

@dataclass  
class PerformanceResult:
    algorithm: str
    time_ms: float
    memory_kb: float
    data_size: int
    data_type: str


ALGORITHM_INFO = {
    "Quick Sort": AlgorithmInfo(
        "Quick Sort", "Divide-and-conquer with pivot", "O(n log n)", "O(n log n)", "O(n²)", "O(log n)", False, True,
        "1. Pick a 'pivot' element\n2. Partition: smaller left, larger right\n3. Recursively sort partitions\n4. Combine results"
    ),
    "Heap Sort": AlgorithmInfo(
        "Heap Sort", "Binary heap based sorting", "O(n log n)", "O(n log n)", "O(n log n)", "O(1)", False, True,
        "1. Build a max-heap from array\n2. Extract max element to end\n3. Reduce heap size and heapify\n4. Repeat until sorted"
    ),
    "Shell Sort": AlgorithmInfo(
        "Shell Sort", "Gap-based insertion sort", "O(n log n)", "O(n^1.25)", "O(n²)", "O(1)", False, True,
        "1. Start with large gap\n2. Sort elements at gap distance\n3. Reduce gap size\n4. Repeat until gap is 1"
    ),
    "Merge Sort": AlgorithmInfo(
        "Merge Sort", "Stable divide-and-conquer", "O(n log n)", "O(n log n)", "O(n log n)", "O(n)", True, False,
        "1. Split array into two halves\n2. Recursively sort each half\n3. Merge sorted halves together\n4. Compare and place in order"
    ),
    "Radix Sort": AlgorithmInfo(
        "Radix Sort", "Non-comparison digit sort", "O(nk)", "O(nk)", "O(nk)", "O(n+k)", True, False,
        "1. Sort by least significant digit\n2. Use counting sort for each digit\n3. Move to next digit\n4. Repeat for all digits"
    ),
}


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════════════════════
class UltimateSortingAnalyzer(ctk.CTk):
    
    COLORS = {
        'bg_dark': '#ffffff', 'bg_card': '#ffffff',
        'accent_blue': '#0969da', 'accent_green': '#2da44e',
        'accent_purple': '#8250df', 'accent_orange': '#bf8700',
        'accent_red': '#cf222e', 'accent_cyan': '#0550ae',
        'text_primary': '#24292f', 'text_secondary': '#57606a',
        'border': '#cfd7df',
    }
    
    CHART_COLORS = ['#0969da', '#2da44e', '#8250df', '#bf8700', '#cf222e']
    
    ALGO_COLORS = {
        'Quick Sort': '#0969da', 'Heap Sort': '#2da44e',
        'Shell Sort': '#8250df', 'Merge Sort': '#bf8700', 'Radix Sort': '#cf222e',
    }
    
    def __init__(self):
        super().__init__()
        
        self.title("SORTING ALGORITHMS ANALYZER - Presentation Mode")
        self.geometry("1450x920")
        self.minsize(1200, 750)
        
        self.dataset_type = ctk.StringVar(value="Random")
        self.data_size = ctk.IntVar(value=10000)
        self.is_running = False
        self.results = []
        
        self._create_header()
        self._create_main()
        self._create_footer()
        
        self.after(100, self._startup_animation)
    
    def _startup_animation(self):
        self.status_indicator.configure(text="● Ready", text_color=self.COLORS['accent_green'])
    
    def _create_header(self):
        header = ctk.CTkFrame(self, height=90, corner_radius=0, fg_color=self.COLORS['bg_card'])
        header.pack(fill="x")
        header.pack_propagate(False)
        
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", padx=30, pady=15)
        
        ctk.CTkLabel(title_frame, text="SORTING ALGORITHMS ANALYZER",
                    font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
                    text_color=self.COLORS['accent_blue']).pack(anchor="w")
        ctk.CTkLabel(title_frame, text="Interactive Performance Analysis with Animated Visualizations",
                    font=ctk.CTkFont(size=12), text_color=self.COLORS['text_secondary']).pack(anchor="w")
        
        status_frame = ctk.CTkFrame(header, fg_color="transparent")
        status_frame.pack(side="right", padx=30)
        self.status_indicator = ctk.CTkLabel(status_frame, text="● Starting...",
                                             font=ctk.CTkFont(size=14, weight="bold"),
                                             text_color=self.COLORS['accent_orange'])
        self.status_indicator.pack()
    
    def _create_main(self):
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=10)
        main.grid_columnconfigure(1, weight=1)
        main.grid_rowconfigure(0, weight=1)
        
        self._create_sidebar(main)
        self._create_content(main)
    
    def _create_sidebar(self, parent):
        sidebar = ctk.CTkFrame(parent, width=300, corner_radius=15, fg_color=self.COLORS['bg_card'])
        sidebar.grid(row=0, column=0, sticky="ns", padx=(0, 15))
        sidebar.grid_propagate(False)
        
        ctk.CTkLabel(sidebar, text="CONTROL PANEL", font=ctk.CTkFont(size=16, weight="bold"),
                    text_color=self.COLORS['accent_cyan']).pack(pady=(25, 20))
        
        # Dataset Type
        self._section(sidebar, "DATASET TYPE")
        type_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        type_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        self.type_menu = ctk.CTkOptionMenu(type_frame, values=["Random", "Reverse Sorted", "Partially Sorted"],
                                           variable=self.dataset_type, width=240, height=35)
        self.type_menu.pack()
        
        # Size
        self._section(sidebar, "DATA SIZE")
        size_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        size_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        self.size_label = ctk.CTkLabel(size_frame, text="10,000 elements",
                                       font=ctk.CTkFont(size=22, weight="bold"))
        self.size_label.pack()
        
        self.size_slider = ctk.CTkSlider(size_frame, from_=1000, to=100000,
                                         number_of_steps=99, width=240, command=self._on_size_change)
        self.size_slider.set(10000)
        self.size_slider.pack(pady=10)
        
        preset_frame = ctk.CTkFrame(size_frame, fg_color="transparent")
        preset_frame.pack()
        for txt, val in [("1K", 1000), ("10K", 10000), ("50K", 50000), ("100K", 100000)]:
            ctk.CTkButton(preset_frame, text=txt, width=50, height=28,
                         fg_color=self.COLORS['border'], hover_color=self.COLORS['accent_blue'],
                         command=lambda v=val: self._set_size(v)).pack(side="left", padx=2)
        
        # Algorithms
        self._section(sidebar, "ALGORITHMS")
        algo_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        algo_frame.pack(fill="x", padx=20)
        
        self.algo_vars = {}
        for algo in ALGORITHM_MAP:
            var = ctk.BooleanVar(value=True)
            self.algo_vars[algo] = var
            ctk.CTkCheckBox(algo_frame, text=algo, variable=var,
                           checkbox_width=18, checkbox_height=18).pack(anchor="w", pady=2)
        
        # RUN BUTTON
        self.run_btn = ctk.CTkButton(sidebar, text="START ANALYSIS", height=55,
                                     font=ctk.CTkFont(size=18, weight="bold"),
                                     fg_color=self.COLORS['accent_green'], hover_color="#2ea043",
                                     command=self._start_analysis)
        self.run_btn.pack(pady=25, padx=20, fill="x")
        
        # Progress
        self.progress_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        self.progress_frame.pack(fill="x", padx=20)
        
        self.progress_text = ctk.CTkLabel(self.progress_frame, text="",
                                          font=ctk.CTkFont(size=11), text_color=self.COLORS['text_secondary'])
        self.progress_text.pack(anchor="w")
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, width=240, height=8)
        self.progress_bar.set(0)
        
        # Guide
        self._section(sidebar, "CHART GUIDE")
        self.guide_box = ctk.CTkTextbox(sidebar, height=100, corner_radius=10, font=ctk.CTkFont(size=10))
        self.guide_box.pack(fill="x", padx=20, pady=(0, 10))
        self._update_guide("Click START to analyze.\n\nTip: Click algorithm cards\nto see animated demos!")
    
    def _section(self, parent, text):
        ctk.CTkLabel(parent, text=text, font=ctk.CTkFont(size=11, weight="bold"),
                    text_color=self.COLORS['text_secondary']).pack(padx=20, pady=(15, 5), anchor="w")
    
    def _create_content(self, parent):
        content = ctk.CTkFrame(parent, corner_radius=15, fg_color=self.COLORS['bg_card'])
        content.grid(row=0, column=1, sticky="nsew")
        
        self.tabview = ctk.CTkTabview(content, corner_radius=10, fg_color="transparent",
                                      segmented_button_fg_color=self.COLORS['border'],
                                      segmented_button_selected_color=self.COLORS['accent_blue'])
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab_charts = self.tabview.add("Performance Charts")
        self.tab_info = self.tabview.add("Algorithm Info (Click for Demo!)")
        self.tab_report = self.tabview.add("Detailed Report")
        
        self._create_charts_tab()
        self._create_info_tab()
        self._create_report_tab()
    
    def _create_charts_tab(self):
        plt.style.use('default')
        
        self.fig = Figure(figsize=(12, 7), facecolor=self.COLORS['bg_dark'])
        self.fig.subplots_adjust(left=0.07, right=0.93, top=0.90, bottom=0.12, wspace=0.35, hspace=0.45)
        
        self.ax1 = self.fig.add_subplot(221)
        self.ax2 = self.fig.add_subplot(222)
        self.ax3 = self.fig.add_subplot(223)
        self.ax4 = self.fig.add_subplot(224)
        
        # Create twin axis for combined chart once
        self.ax3b = self.ax3.twinx()
        
        for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
            ax.set_facecolor(self.COLORS['bg_dark'])
        
        self._style_empty_charts()
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.tab_charts)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
    
    def _style_empty_charts(self):
        titles = ["EXECUTION TIME\n(Lower = Faster)", "MEMORY USAGE\n(Lower = Better)",
                  "COMBINED COMPARISON", "ALGORITHM RACE\n(Time to Finish)"]
        for ax, title in zip([self.ax1, self.ax2, self.ax3, self.ax4], titles):
            ax.set_title(title, color='black', fontsize=10, fontweight='bold', pad=10)
            ax.text(0.5, 0.5, "Click START ANALYSIS", ha='center', va='center',
                   color=self.COLORS['text_secondary'], fontsize=11, transform=ax.transAxes)
            ax.set_xticks([])
            ax.set_yticks([])
    
    def _create_info_tab(self):
        scroll = ctk.CTkScrollableFrame(self.tab_info, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(scroll, text="Click on any algorithm card below to see an animated demo!",
                    font=ctk.CTkFont(size=14, weight="bold"), text_color=self.COLORS['accent_cyan']).pack(pady=(5, 15))
        
        for i, (name, info) in enumerate(ALGORITHM_INFO.items()):
            card = ctk.CTkFrame(scroll, corner_radius=10, fg_color=self.COLORS['border'])
            card.pack(fill="x", pady=8, padx=5)
            
            card.bind("<Button-1>", lambda e, n=name: self._show_visualization(n))
            card.bind("<Enter>", lambda e, c=card: c.configure(fg_color="#3d444d"))
            card.bind("<Leave>", lambda e, c=card: c.configure(fg_color=self.COLORS['border']))
            
            header = ctk.CTkFrame(card, fg_color="transparent")
            header.pack(fill="x", padx=15, pady=(12, 8))
            header.bind("<Button-1>", lambda e, n=name: self._show_visualization(n))
            
            name_lbl = ctk.CTkLabel(header, text=f"▶ {info.name}", font=ctk.CTkFont(size=16, weight="bold"),
                                    text_color=self.CHART_COLORS[i], cursor="hand2")
            name_lbl.pack(side="left")
            name_lbl.bind("<Button-1>", lambda e, n=name: self._show_visualization(n))
            
            ctk.CTkLabel(header, text="Click to see demo", font=ctk.CTkFont(size=10),
                        text_color=self.COLORS['accent_green']).pack(side="right")
            
            desc_lbl = ctk.CTkLabel(card, text=info.how_it_works, font=ctk.CTkFont(size=11),
                                   text_color=self.COLORS['text_secondary'], justify="left", wraplength=700)
            desc_lbl.pack(padx=15, pady=(0, 5), anchor="w")
            desc_lbl.bind("<Button-1>", lambda e, n=name: self._show_visualization(n))
            
            comp = ctk.CTkFrame(card, fg_color=self.COLORS['bg_dark'], corner_radius=8)
            comp.pack(fill="x", padx=15, pady=(0, 12))
            
            for label, value, color in [("Best", info.time_best, self.COLORS['accent_green']),
                                        ("Avg", info.time_avg, self.COLORS['accent_blue']),
                                        ("Worst", info.time_worst, self.COLORS['accent_red']),
                                        ("Space", info.space, self.COLORS['accent_purple'])]:
                item = ctk.CTkFrame(comp, fg_color="transparent")
                item.pack(side="left", expand=True, pady=8)
                ctk.CTkLabel(item, text=label, font=ctk.CTkFont(size=9),
                            text_color=self.COLORS['text_secondary']).pack()
                ctk.CTkLabel(item, text=value, font=ctk.CTkFont(size=12, weight="bold"),
                            text_color=color).pack()
    
    def _show_visualization(self, algorithm_name):
        """Open animated visualization window."""
        info = ALGORITHM_INFO.get(algorithm_name)
        algo_info = {'how_it_works': info.how_it_works} if info else {}
        viz = SortingVisualization(self, algorithm_name, algo_info)
        viz.grab_set()
    
    def _create_report_tab(self):
        self.report_text = ctk.CTkTextbox(self.tab_report, font=("Consolas", 12),
                                          corner_radius=10, fg_color=self.COLORS['bg_dark'])
        self.report_text.pack(fill="both", expand=True, padx=10, pady=10)
        self.report_text.insert("1.0", "Click START ANALYSIS to generate report...")
    
    def _create_footer(self):
        footer = ctk.CTkFrame(self, height=35, corner_radius=0, fg_color=self.COLORS['bg_card'])
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)
        ctk.CTkLabel(footer, text="University Algorithms Project 2025",
                    font=ctk.CTkFont(size=11), text_color=self.COLORS['text_secondary']).pack(side="left", padx=20, pady=5)
        ctk.CTkLabel(footer, text="Quick • Heap • Shell • Merge • Radix Sort",
                    font=ctk.CTkFont(size=11), text_color=self.COLORS['text_secondary']).pack(side="right", padx=20, pady=5)
    
    def _on_size_change(self, val):
        self.data_size.set(int(val))
        self.size_label.configure(text=f"{int(val):,} elements")
    
    def _set_size(self, val):
        self.size_slider.set(val)
        self._on_size_change(val)
    
    def _update_guide(self, text):
        self.guide_box.configure(state="normal")
        self.guide_box.delete("1.0", "end")
        self.guide_box.insert("1.0", text)
        self.guide_box.configure(state="disabled")
    
    def _start_analysis(self):
        if self.is_running:
            return
        
        selected = [n for n, v in self.algo_vars.items() if v.get()]
        if not selected:
            return
        
        self.is_running = True
        self.run_btn.configure(state="disabled", text="ANALYZING...", fg_color=self.COLORS['accent_orange'])
        self.status_indicator.configure(text="● Running...", text_color=self.COLORS['accent_orange'])
        
        self.progress_text.pack(anchor="w")
        self.progress_bar.pack(pady=(5, 0))
        self.progress_bar.set(0)
        
        threading.Thread(target=self._run_analysis, daemon=True).start()
    
    def _run_analysis(self):
        try:
            size = self.data_size.get()
            dtype = self.dataset_type.get()
            selected = [n for n, v in self.algo_vars.items() if v.get()]
            
            self._update_prog("Generating data...", 0.05)
            time.sleep(0.2)
            
            if dtype == "Random":
                data = DataGenerator.random(size)
            elif dtype == "Reverse Sorted":
                data = DataGenerator.reverse(size)
            else:
                data = DataGenerator.partial(size)
            
            results = []
            total = len(selected)
            
            for i, algo in enumerate(selected):
                self._update_prog(f"Testing {algo}...", (i + 0.5) / total * 0.85 + 0.1)
                time.sleep(0.1)
                
                arr = data.copy()
                tracemalloc.start()
                start = time.perf_counter()
                ALGORITHM_MAP[algo](arr)
                end = time.perf_counter()
                _, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                
                results.append(PerformanceResult(algo, (end-start)*1000, peak/1024, size, dtype))
            
            self.results = results
            self._update_prog("Creating charts...", 0.95)
            time.sleep(0.2)
            
            self.after(0, lambda: self._display_results(results, dtype, size))
            
        except Exception as e:
            self.after(0, lambda: self.status_indicator.configure(text=f"Error", text_color=self.COLORS['accent_red']))
        finally:
            self.after(0, self._finish_analysis)
    
    def _update_prog(self, text, val):
        self.after(0, lambda: self.progress_text.configure(text=text))
        self.after(0, lambda: self.progress_bar.set(val))
    
    def _finish_analysis(self):
        self.is_running = False
        self.run_btn.configure(state="normal", text="START ANALYSIS", fg_color=self.COLORS['accent_green'])
        self.status_indicator.configure(text="● Complete!", text_color=self.COLORS['accent_green'])
        self.progress_bar.pack_forget()
        self.progress_text.pack_forget()
        
        if self.results:
            best_time = min(self.results, key=lambda r: r.time_ms)
            best_mem = min(self.results, key=lambda r: r.memory_kb)
            self._update_guide(f"Done!\n\nFastest: {best_time.algorithm}\nMost Efficient: {best_mem.algorithm}")
    
    def _display_results(self, results, dtype, size):
        self._update_charts(results, dtype, size)
        self._update_report(results, dtype, size)
        self.tabview.set("Performance Charts")
    
    def _update_charts(self, results, dtype, size):
        # Clear all axes including twin axis
        for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
            ax.clear()
        self.ax3b.clear()
        
        names = [r.algorithm.replace(" Sort", "") for r in results]
        full_names = [r.algorithm for r in results]
        times = [r.time_ms for r in results]
        mems = [r.memory_kb for r in results]
        x = np.arange(len(names))
        colors = [self.ALGO_COLORS.get(fn, '#58a6ff') for fn in full_names]
        
        # Time chart
        for i, (xi, ti, c, name) in enumerate(zip(x, times, colors, names)):
            self.ax1.plot([xi], [ti], 'o', color=c, markersize=14, markerfacecolor=c,
                         markeredgecolor='white', markeredgewidth=2, zorder=5, label=name)
            self.ax1.annotate(f'{ti:.1f}ms', (xi, ti), textcoords="offset points", xytext=(0, 18),
                             ha='center', fontsize=9, fontweight='bold', color='white',
                             bbox=dict(boxstyle='round,pad=0.3', facecolor=c, alpha=0.9))
        self.ax1.plot(x, times, '-', color='#888888', linewidth=2, alpha=0.5, zorder=1)
        min_idx = times.index(min(times))
        self.ax1.scatter([min_idx], [times[min_idx]], s=300, c='#00ff00', marker='*', zorder=10)
        self.ax1.set_title("EXECUTION TIME\n(Lower = Faster)", color='black', fontsize=11, fontweight='bold', pad=10)
        self.ax1.set_xticks(x)
        self.ax1.set_xticklabels(names, rotation=15, ha='right', fontsize=9, color='black')
        self.ax1.tick_params(colors='black')
        self.ax1.grid(True, linestyle='--', alpha=0.3)
        self.ax1.legend(loc='upper right', facecolor='#f0f0f0', labelcolor='black', fontsize=8)
        
        # Memory chart
        for i, (xi, mi, c, name) in enumerate(zip(x, mems, colors, names)):
            self.ax2.plot([xi], [mi], 's', color=c, markersize=14, markerfacecolor=c,
                         markeredgecolor='white', markeredgewidth=2, zorder=5)
            self.ax2.annotate(f'{mi:.0f}KB', (xi, mi), textcoords="offset points", xytext=(0, 18),
                             ha='center', fontsize=9, fontweight='bold', color='white',
                             bbox=dict(boxstyle='round,pad=0.3', facecolor=c, alpha=0.9))
        self.ax2.plot(x, mems, '-', color='#888888', linewidth=2, alpha=0.5, zorder=1)
        min_mem_idx = mems.index(min(mems))
        self.ax2.scatter([min_mem_idx], [mems[min_mem_idx]], s=300, c='#00ff00', marker='*', zorder=10)
        self.ax2.set_title("MEMORY USAGE\n(Lower = Better)", color='black', fontsize=11, fontweight='bold', pad=10)
        self.ax2.set_xticks(x)
        self.ax2.set_xticklabels(names, rotation=15, ha='right', fontsize=9, color='black')
        self.ax2.tick_params(colors='black')
        self.ax2.grid(True, linestyle='--', alpha=0.3)
        
        # Combined chart
        line1 = self.ax3.plot(x, times, 'o-', color=self.COLORS['accent_blue'], linewidth=3, markersize=10, label='Time (ms)')
        self.ax3.fill_between(x, times, alpha=0.2, color=self.COLORS['accent_blue'])
        self.ax3.set_ylabel("Time (ms)", color=self.COLORS['accent_blue'])
        self.ax3.tick_params(axis='y', colors=self.COLORS['accent_blue'])
        
        line2 = self.ax3b.plot(x, mems, 's-', color=self.COLORS['accent_orange'], linewidth=3, markersize=10, label='Memory (KB)')
        self.ax3b.fill_between(x, mems, alpha=0.2, color=self.COLORS['accent_orange'])
        self.ax3b.set_ylabel("Memory (KB)", color=self.COLORS['accent_orange'])
        self.ax3b.tick_params(axis='y', colors=self.COLORS['accent_orange'])
        
        self.ax3.set_title("COMBINED COMPARISON", color='black', fontsize=11, fontweight='bold', pad=10)
        self.ax3.set_xticks(x)
        self.ax3.set_xticklabels(names, rotation=15, ha='right', fontsize=9, color='black')
        self.ax3.tick_params(axis='x', colors='black')
        self.ax3.grid(True, linestyle='--', alpha=0.3)
        self.ax3.legend(line1+line2, ['Time', 'Memory'], loc='upper center', facecolor='#f0f0f0', labelcolor='black', ncol=2)
        
        # Race Chart (Ranking by Speed - Items/sec)
        # Calculate speed (Items per second) prevents div/0
        speeds = [size / (t / 1000 + 0.00001) for t in times]
        
        # Sort by speed ascending (Slowest at bottom, Fastest at top)
        sorted_idx = np.argsort(speeds)
        sorted_names = [names[i] for i in sorted_idx]
        sorted_speeds = [speeds[i] for i in sorted_idx]
        sorted_colors = [colors[i] for i in sorted_idx]
        sorted_times = [times[i] for i in sorted_idx]
        
        bars = self.ax4.barh(sorted_names, sorted_speeds, color=sorted_colors, edgecolor='white', height=0.6)
        
        max_speed = max(speeds)
        for i, (bar, speed, time_val) in enumerate(zip(bars, sorted_speeds, sorted_times)):
            # Label with Speed AND Time
            label_text = f"{speed:,.0f} ops/s ({time_val:.1f}ms)"
            self.ax4.text(speed + (max_speed * 0.02), bar.get_y() + bar.get_height()/2, label_text,
                         va='center', color='black', fontsize=9, fontweight='bold')
            
            # Winner badge for the top one
            if i == len(bars) - 1:
                self.ax4.text(speed / 2, bar.get_y() + bar.get_height()/2, '🏆 WINNER',
                             ha='center', va='center', color='white', fontsize=10, fontweight='bold',
                             bbox=dict(facecolor='black', alpha=0.3, edgecolor='none', boxstyle='round,pad=0.2'))
        
        self.ax4.set_title("ALGORITHM RACE\n(Processing Speed)", color='black', fontsize=11, fontweight='bold', pad=10)
        self.ax4.set_xlim(0, max(speeds) * 1.45) # Extra space
        self.ax4.tick_params(colors='black')
        self.ax4.grid(True, axis='x', linestyle='--', alpha=0.3)
        
        for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
            ax.set_facecolor(self.COLORS['bg_dark'])
            for spine in ax.spines.values():
                spine.set_color(self.COLORS['border'])
        
        self.fig.suptitle(f"Analysis: {dtype} Data | {size:,} Elements", color='black', fontsize=13, fontweight='bold', y=0.97)
        self.fig.tight_layout(rect=[0, 0, 1, 0.95])
        self.canvas.draw()
    
    def _update_report(self, results, dtype, size):
        best_time = min(results, key=lambda r: r.time_ms)
        best_mem = min(results, key=lambda r: r.memory_kb)
        
        report = f"""
PERFORMANCE ANALYSIS REPORT
===========================

Configuration: {dtype} | {size:,} elements

RESULTS (by speed):
"""
        for r in sorted(results, key=lambda x: x.time_ms):
            report += f"\n  {r.algorithm}: {r.time_ms:.2f} ms | {r.memory_kb:.0f} KB"
        
        report += f"""

WINNERS:
  Fastest: {best_time.algorithm} ({best_time.time_ms:.2f} ms)
  Most Efficient: {best_mem.algorithm} ({best_mem.memory_kb:.0f} KB)
"""
        self.report_text.delete("1.0", "end")
        self.report_text.insert("1.0", report)


if __name__ == "__main__":
    app = UltimateSortingAnalyzer()
    app.mainloop()
