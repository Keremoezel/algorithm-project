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
                         text_color="black", command=lambda v=val: self._set_size(v)).pack(side="left", padx=2)
        
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
        self.tab_info = self.tabview.add("Algorithm Visualization")
        self.tab_report = self.tabview.add("Detailed Report")
        
        self._create_charts_tab()
        self._create_info_tab()
        self._create_report_tab()
    
    def _create_charts_tab(self):
        plt.style.use('default')
        
        self.fig = Figure(figsize=(12, 8), facecolor=self.COLORS['bg_dark'])
        self.fig.subplots_adjust(left=0.07, right=0.93, top=0.92, bottom=0.08, wspace=0.35, hspace=0.35)
        
        # Top row: Line charts
        self.ax1 = self.fig.add_subplot(221)
        self.ax2 = self.fig.add_subplot(222)
        # Bottom row: Bar charts
        self.ax3 = self.fig.add_subplot(223)
        self.ax4 = self.fig.add_subplot(224)
        
        for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
            ax.set_facecolor(self.COLORS['bg_dark'])
        
        self._style_empty_charts()
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.tab_charts)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
    
    def _style_empty_charts(self):
        titles = ["EXECUTION TIME", "MEMORY USAGE", "TIME COMPARISON", "MEMORY COMPARISON"]
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
            max_size = self.data_size.get()
            dtype = self.dataset_type.get()
            selected = [n for n, v in self.algo_vars.items() if v.get()]
            
            # Create test points from small to max_size (5 points)
            if max_size <= 5000:
                test_sizes = [max_size // 5 * i for i in range(1, 6)]
            else:
                test_sizes = [max_size // 5 * i for i in range(1, 6)]
            test_sizes = [max(100, s) for s in test_sizes]  # Minimum 100
            
            # Results dictionary: {algo_name: {size: PerformanceResult}}
            multi_results = {algo: {} for algo in selected}
            
            total_tests = len(selected) * len(test_sizes)
            current_test = 0
            
            for size in test_sizes:
                self._update_prog(f"Generating {size:,} elements...", current_test / total_tests * 0.9 + 0.05)
                
                if dtype == "Random":
                    data = DataGenerator.random(size)
                elif dtype == "Reverse Sorted":
                    data = DataGenerator.reverse(size)
                else:
                    data = DataGenerator.partial(size)
                
                for algo in selected:
                    self._update_prog(f"Testing {algo} ({size:,})...", current_test / total_tests * 0.9 + 0.05)
                    
                    arr = data.copy()
                    tracemalloc.start()
                    start = time.perf_counter()
                    ALGORITHM_MAP[algo](arr)
                    end = time.perf_counter()
                    _, peak = tracemalloc.get_traced_memory()
                    tracemalloc.stop()
                    
                    multi_results[algo][size] = PerformanceResult(algo, (end-start)*1000, peak/1024, size, dtype)
                    current_test += 1
            
            self.multi_results = multi_results
            self.test_sizes = test_sizes
            self._update_prog("Creating charts...", 0.95)
            time.sleep(0.1)
            
            self.after(0, lambda: self._display_multi_results(multi_results, test_sizes, dtype, max_size))
            
        except Exception as e:
            import traceback
            traceback.print_exc()
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
        
        if hasattr(self, 'multi_results') and self.multi_results:
            # Find fastest at max size
            max_size = max(self.test_sizes)
            final_results = [self.multi_results[algo][max_size] for algo in self.multi_results]
            best_time = min(final_results, key=lambda r: r.time_ms)
            best_mem = min(final_results, key=lambda r: r.memory_kb)
            self._update_guide(f"Done!\n\nFastest: {best_time.algorithm}\nMost Efficient: {best_mem.algorithm}")
    
    def _display_multi_results(self, multi_results, test_sizes, dtype, max_size):
        self._update_multi_charts(multi_results, test_sizes, dtype, max_size)
        # Pass all data for comprehensive report
        self._update_multi_report(multi_results, test_sizes, dtype, max_size)
        self.tabview.set("Performance Charts")
    
    def _update_multi_charts(self, multi_results, test_sizes, dtype, max_size):
        # Clear all axes
        for ax in [self.ax1, self.ax2]:
            ax.clear()
        
        # X axis: data sizes
        x = test_sizes
        x_labels = [f"{s//1000}K" if s >= 1000 else str(s) for s in test_sizes]
        
        # Store lines for interactive legend
        self.lines1 = []  # Time chart lines
        self.lines2 = []  # Memory chart lines
        
        # Plot each algorithm as a line
        for algo_name, size_results in multi_results.items():
            color = self.ALGO_COLORS.get(algo_name, '#58a6ff')
            display_name = algo_name.replace(" Sort", "")
            
            # Collect time and memory data for each size
            times = [size_results[s].time_ms for s in test_sizes]
            mems = [size_results[s].memory_kb for s in test_sizes]
            
            # Time chart - line with markers
            line1, = self.ax1.plot(x, times, 'o-', color=color, linewidth=2.5, markersize=8,
                         markerfacecolor=color, markeredgecolor='white', markeredgewidth=1.5,
                         label=algo_name, zorder=5, picker=5)
            self.lines1.append(line1)
            
            # Memory chart - line with markers
            line2, = self.ax2.plot(x, mems, 'o-', color=color, linewidth=2.5, markersize=8,
                         markerfacecolor=color, markeredgecolor='white', markeredgewidth=1.5,
                         label=algo_name, zorder=5, picker=5)
            self.lines2.append(line2)
        
        # Style Time chart
        self.ax1.set_title(f"Time - {dtype}", color='black', fontsize=12, fontweight='bold', pad=10)
        self.ax1.set_xlabel("Data Size (n)", color='black', fontsize=10)
        self.ax1.set_ylabel("Time (ms)", color='black', fontsize=10)
        self.ax1.set_xticks(x)
        self.ax1.set_xticklabels(x_labels, fontsize=9, color='black')
        self.ax1.tick_params(colors='black')
        self.ax1.grid(True, linestyle='-', alpha=0.3)
        leg1 = self.ax1.legend(loc='upper left', facecolor='white', labelcolor='black', fontsize=8,
                       edgecolor='#ccc', framealpha=0.95)
        
        # Style Memory chart  
        self.ax2.set_title(f"Memory - {dtype}", color='black', fontsize=12, fontweight='bold', pad=10)
        self.ax2.set_xlabel("Data Size (n)", color='black', fontsize=10)
        self.ax2.set_ylabel("Memory (KB)", color='black', fontsize=10)
        self.ax2.set_xticks(x)
        self.ax2.set_xticklabels(x_labels, fontsize=9, color='black')
        self.ax2.tick_params(colors='black')
        self.ax2.grid(True, linestyle='-', alpha=0.3)
        leg2 = self.ax2.legend(loc='upper left', facecolor='white', labelcolor='black', fontsize=8,
                       edgecolor='#ccc', framealpha=0.95)
        
        # Make legend items clickable - separate mapping for each chart
        self.legend_line_map = {}
        
        # Chart 1 legend -> Chart 1 lines only
        for leg_line, orig_line in zip(leg1.get_lines(), self.lines1):
            leg_line.set_picker(5)
            self.legend_line_map[leg_line] = orig_line
        
        # Chart 2 legend -> Chart 2 lines only
        for leg_line, orig_line in zip(leg2.get_lines(), self.lines2):
            leg_line.set_picker(5)
            self.legend_line_map[leg_line] = orig_line
        
        # Connect pick event
        if hasattr(self, '_pick_cid'):
            self.fig.canvas.mpl_disconnect(self._pick_cid)
        self._pick_cid = self.fig.canvas.mpl_connect('pick_event', self._on_legend_click)
        
        # Store data for hover tooltip
        self.hover_data = {
            'test_sizes': test_sizes,
            'multi_results': multi_results,
            'x_labels': x_labels
        }
        
        # Create annotation for hover tooltip
        self.annot1 = self.ax1.annotate("", xy=(0,0), xytext=(10,10),
                                        textcoords="offset points",
                                        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.9),
                                        fontsize=9, color='black', zorder=100)
        self.annot1.set_visible(False)
        
        self.annot2 = self.ax2.annotate("", xy=(0,0), xytext=(10,10),
                                        textcoords="offset points",
                                        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.9),
                                        fontsize=9, color='black', zorder=100)
        self.annot2.set_visible(False)
        
        # Connect hover event
        if hasattr(self, '_hover_cid'):
            self.fig.canvas.mpl_disconnect(self._hover_cid)
        self._hover_cid = self.fig.canvas.mpl_connect('motion_notify_event', self._on_hover)
        
        # === BAR CHARTS (Bottom Row) ===
        self.ax3.clear()
        self.ax4.clear()
        
        # Get data for max size
        algo_names = list(multi_results.keys())
        max_times = [multi_results[algo][max_size].time_ms for algo in algo_names]
        max_mems = [multi_results[algo][max_size].memory_kb for algo in algo_names]
        bar_colors = [self.ALGO_COLORS.get(algo, '#58a6ff') for algo in algo_names]
        short_names = [algo.replace(" Sort", "") for algo in algo_names]
        
        # Sort by time for time chart
        time_sorted = sorted(zip(short_names, max_times, bar_colors), key=lambda x: x[1])
        t_names, t_vals, t_colors = zip(*time_sorted)
        
        # Time bar chart
        bars1 = self.ax3.bar(t_names, t_vals, color=t_colors, edgecolor='white', linewidth=1.5)
        for bar, val in zip(bars1, t_vals):
            self.ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(t_vals)*0.02,
                         f'{val:.1f}ms', ha='center', va='bottom', fontsize=9, fontweight='bold', color='black')
        self.ax3.set_title(f"TIME COMPARISON AT MAX SIZE ({max_size:,} elements)", color='black', fontsize=10, fontweight='bold', pad=10)
        self.ax3.set_ylabel("Time (ms)", color='black', fontsize=9)
        self.ax3.tick_params(colors='black')
        self.ax3.grid(True, axis='y', linestyle='-', alpha=0.3)
        
        # Sort by memory for memory chart
        mem_sorted = sorted(zip(short_names, max_mems, bar_colors), key=lambda x: x[1])
        m_names, m_vals, m_colors = zip(*mem_sorted)
        
        # Memory bar chart
        bars2 = self.ax4.bar(m_names, m_vals, color=m_colors, edgecolor='white', linewidth=1.5)
        for bar, val in zip(bars2, m_vals):
            self.ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(m_vals)*0.02,
                         f'{val:.0f}KB', ha='center', va='bottom', fontsize=9, fontweight='bold', color='black')
        self.ax4.set_title(f"MEMORY COMPARISON AT MAX SIZE ({max_size:,} elements)", color='black', fontsize=10, fontweight='bold', pad=10)
        self.ax4.set_ylabel("Memory (KB)", color='black', fontsize=9)
        self.ax4.tick_params(colors='black')
        self.ax4.grid(True, axis='y', linestyle='-', alpha=0.3)
        
        # White background for all charts
        for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
            ax.set_facecolor('#ffffff')
            for spine in ax.spines.values():
                spine.set_color('#ccc')
        
        self.fig.set_facecolor('#ffffff')
        self.fig.suptitle(f"Algorithm Performance Analysis | Max: {max_size:,} Elements", 
                         color='black', fontsize=13, fontweight='bold', y=0.98)
        self.fig.tight_layout(rect=[0, 0.02, 1, 0.95])
        self.canvas.draw()
    
    def _on_hover(self, event):
        """Show tooltip when hovering over data points."""
        if event.inaxes not in [self.ax1, self.ax2]:
            self.annot1.set_visible(False)
            self.annot2.set_visible(False)
            self.canvas.draw_idle()
            return
        
        # Determine which chart and lines to check
        if event.inaxes == self.ax1:
            lines = self.lines1
            annot = self.annot1
            value_type = "ms"
        else:
            lines = self.lines2
            annot = self.annot2
            value_type = "KB"
        
        found = False
        for line in lines:
            if not line.get_visible():
                continue
            cont, ind = line.contains(event)
            if cont:
                x_data = line.get_xdata()
                y_data = line.get_ydata()
                idx = ind["ind"][0]
                x_val = x_data[idx]
                y_val = y_data[idx]
                
                # Get algorithm name from label
                algo_name = line.get_label()
                size_label = self.hover_data['x_labels'][idx] if idx < len(self.hover_data['x_labels']) else str(x_val)
                
                annot.xy = (x_val, y_val)
                annot.set_text(f"{algo_name}\n{size_label}: {y_val:.2f} {value_type}")
                annot.set_visible(True)
                found = True
                break
        
        if not found:
            annot.set_visible(False)
        
        self.canvas.draw_idle()
    
    def _on_legend_click(self, event):
        """Toggle line visibility when legend item is clicked - independent per chart."""
        leg_line = event.artist
        if leg_line in self.legend_line_map:
            orig_line = self.legend_line_map[leg_line]
            
            # Toggle visibility only for the clicked chart's line
            visible = not orig_line.get_visible()
            orig_line.set_visible(visible)
            
            # Change legend line alpha to show state
            leg_line.set_alpha(1.0 if visible else 0.2)
            
            self.canvas.draw()
    
    def _update_multi_report(self, multi_results, test_sizes, dtype, max_size):
        # Find winners at max size
        final_results = [multi_results[algo][max_size] for algo in multi_results]
        best_time = min(final_results, key=lambda r: r.time_ms)
        best_mem = min(final_results, key=lambda r: r.memory_kb)
        
        # Build comprehensive report
        report = f"""
╔══════════════════════════════════════════════════════════════════════════╗
║                    PERFORMANCE ANALYSIS REPORT                           ║
╚══════════════════════════════════════════════════════════════════════════╝

Configuration: {dtype} Data | Max Size: {max_size:,} elements
Test Points: {', '.join(f'{s:,}' for s in test_sizes)}

═══════════════════════════════════════════════════════════════════════════
                            TIME RESULTS (ms)
═══════════════════════════════════════════════════════════════════════════
"""
        # Header
        size_labels = [f"{s//1000}K" if s >= 1000 else str(s) for s in test_sizes]
        header = f"{'Algorithm':<15}" + "".join(f"{lbl:>10}" for lbl in size_labels)
        report += header + "\n"
        report += "-" * (15 + len(test_sizes) * 10) + "\n"
        
        # Time data for each algorithm
        for algo_name in multi_results:
            row = f"{algo_name:<15}"
            for size in test_sizes:
                time_val = multi_results[algo_name][size].time_ms
                row += f"{time_val:>10.2f}"
            report += row + "\n"
        
        report += f"""
═══════════════════════════════════════════════════════════════════════════
                          MEMORY RESULTS (KB)
═══════════════════════════════════════════════════════════════════════════
"""
        # Header again
        report += header + "\n"
        report += "-" * (15 + len(test_sizes) * 10) + "\n"
        
        # Memory data for each algorithm
        for algo_name in multi_results:
            row = f"{algo_name:<15}"
            for size in test_sizes:
                mem_val = multi_results[algo_name][size].memory_kb
                row += f"{mem_val:>10.0f}"
            report += row + "\n"
        
        report += f"""
═══════════════════════════════════════════════════════════════════════════
                              WINNERS
═══════════════════════════════════════════════════════════════════════════
  Fastest:        {best_time.algorithm} ({best_time.time_ms:.2f} ms at {max_size:,})
  Most Efficient: {best_mem.algorithm} ({best_mem.memory_kb:.0f} KB at {max_size:,})
"""
        self.report_text.delete("1.0", "end")
        self.report_text.insert("1.0", report)


if __name__ == "__main__":
    app = UltimateSortingAnalyzer()
    app.mainloop()
