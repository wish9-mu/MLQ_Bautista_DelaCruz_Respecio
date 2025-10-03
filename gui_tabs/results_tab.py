import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

def setup_results_tab(self):
        """
        Create the Results tab interface.
        
        This tab displays:
        - Detailed timeline grid showing process execution
        - Process results summary table
        - Performance statistics and metrics
        - Analysis of scheduling efficiency
        
        References:
        - W3Schools. (2024). Python tkinter grid. https://www.w3schools.com/python/python_tkinter_grid.asp
        """
        self.results_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.results_tab, text="Simulation Results")
        
        main_container = tk.Frame(self.results_tab)
        main_container.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Timeline grid
        timeline_grid_frame = self.create_label_frame(main_container, "Animation - Simulation Timeline")
        timeline_grid_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        timeline_container = tk.Frame(timeline_grid_frame)
        timeline_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.timeline_grid_canvas = self.create_canvas(timeline_container, height=250)
        
        timeline_v_scrollbar = ttk.Scrollbar(timeline_container, orient='vertical', command=self.timeline_grid_canvas.yview)
        timeline_h_scrollbar = ttk.Scrollbar(timeline_container, orient='horizontal', command=self.timeline_grid_canvas.xview)
        self.timeline_grid_canvas.configure(yscrollcommand=timeline_v_scrollbar.set, xscrollcommand=timeline_h_scrollbar.set)
        
        # Vvbox for scroll bars
        self.timeline_grid_canvas.grid(row=0, column=0, sticky='nsew')
        timeline_v_scrollbar.grid(row=0, column=1, sticky='ns')
        timeline_h_scrollbar.grid(row=1, column=0, columnspan=2, sticky='ew')
        
        # Configure grid weights so canvas expands
        timeline_container.grid_rowconfigure(0, weight=1)
        timeline_container.grid_columnconfigure(0, weight=1)
        
        # Add mouse wheel scrolling support for timeline grid canvas
        self._bind_mousewheel_to_canvas(self.timeline_grid_canvas)
        
        # Timeline text
        timeline_text_frame = self.create_label_frame(main_container, "Detailed Timeline")
        timeline_text_frame.pack(fill='x', padx=5, pady=5)
        
        self.timeline_text = scrolledtext.ScrolledText(timeline_text_frame, height=8, wrap='word', font=("Courier", 9))
        self.timeline_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Results table
        results_table_frame = self.create_label_frame(main_container, "Process Results Summary")
        results_table_frame.pack(fill='x', padx=5, pady=5)
        
        # Create container for results table with scrollbars
        results_container = tk.Frame(results_table_frame)
        results_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        columns = ('Process', 'Arrival', 'BT_Now', 'PT_Now', 'PT_Used', 'First Start', 'Completion', 'Turnaround', 'WT_Now', 'Response')
        self.results_tree = ttk.Treeview(results_container, columns=columns, show='headings', height=6)
        
        column_widths = {'Process': 60, 'Arrival': 60, 'BT_Now': 60, 'PT_Now': 60, 'PT_Used': 60, 'First Start': 80, 'Completion': 80, 'Turnaround': 80, 'WT_Now': 70, 'Response': 70}
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=column_widths.get(col, 60))
        
        # Vertical scrollbar
        results_v_scrollbar = ttk.Scrollbar(results_container, orient='vertical', command=self.results_tree.yview)
        # Horizontal scrollbar
        results_h_scrollbar = ttk.Scrollbar(results_container, orient='horizontal', command=self.results_tree.xview)
        
        # Configure both scrollbars
        self.results_tree.configure(yscrollcommand=results_v_scrollbar.set, xscrollcommand=results_h_scrollbar.set)
        
        # Pack the table and scrollbars
        self.results_tree.pack(side='left', fill='both', expand=True)
        results_v_scrollbar.pack(side='right', fill='y')
        results_h_scrollbar.pack(side='bottom', fill='x')
        
        # Summary
        summary_frame = self.create_label_frame(self.results_tab, "Summary Statistics")
        summary_frame.pack(fill='x', padx=10, pady=5)
        
        self.summary_text = tk.Text(summary_frame, height=4, wrap='word', bg='#f8f9fa', font=("Arial", 10))
        self.summary_text.pack(fill='x', padx=5, pady=5)

def populate_results_tab(self):
        # Fill the Results tab using self.timeline and self.results.
        
        # Draw the timeline grid visualization
        self._draw_timeline_grid()
        
        # ---- Enhanced Timeline text ----
        self.timeline_text.delete('1.0', 'end')
        
        # Header section
        timeline_text = "=" * 80 + "\n"
        timeline_text += "MLFQ CPU SCHEDULER - EXECUTION TIMELINE\n"
        timeline_text += "=" * 80 + "\n\n"
        
        # Scheduling Rules Section
        timeline_text += "SCHEDULING RULES:\n"
        timeline_text += "-" * 40 + "\n"
        timeline_text += f"• Time Quantum Q0 (Highest): {self.quantum_q0.get()} time units\n"
        timeline_text += f"• Time Quantum Q1 (Medium): {self.quantum_q1.get()} time units\n"
        timeline_text += f"• Time Quantum Q2 (Lowest): {self.quantum_q2.get()} time units\n"
        timeline_text += f"• Demotion Threshold: {self.demote_threshold.get()} time units\n"
        timeline_text += f"• Aging Threshold: {self.aging_threshold.get()} time units\n"
        timeline_text += f"• Preemption: {'Enabled' if self.preempt.get() else 'Disabled'}\n\n"
        
        # Process Details Section
        timeline_text += "PROCESS DETAILS:\n"
        timeline_text += "-" * 40 + "\n"
        timeline_text += f"{'Process':<10} {'PT_Now':<8} {'Arrival':<7} {'BT_Now':<6} {'PT_Used':<7} {'Completion':<10} {'Turnaround':<10} {'WT_Now':<8}\n"
        timeline_text += "-" * 80 + "\n"
        
        for r in self.results:
            pt_used = r['burst'] - (r['burst'] - r.get('remaining', 0)) if 'remaining' in r else r['burst']
            timeline_text += f"{r['name']:<10} {r['priority']:<8} {r['arrival']:<7} {r['burst']:<6} {pt_used:<7} "
            timeline_text += f"{r['completion'] if r['completion'] is not None else 'N/A':<10} "
            timeline_text += f"{r['turnaround'] if r['turnaround'] is not None else 'N/A':<10} "
            timeline_text += f"{r['waiting']:<8}\n"
        
        timeline_text += "\n"
        
        # Execution Timeline Section
        timeline_text += "EXECUTION TIMELINE:\n"
        timeline_text += "-" * 40 + "\n"
        timeline_text += "Time | Process | Queue | Action\n"
        timeline_text += "-" * 40 + "\n"
        
        if self.timeline:
            for start, end, process, queue in self.timeline:
                action = f"Executing in Q{queue}" if queue < 3 else "Running on CPU"
                timeline_text += f"{start:4d} | {process:<7} | Q{queue:<4} | {action}\n"
        else:
            timeline_text += "No processes were executed.\n"
        
        timeline_text += "\n"
        
        # Time Axis Section
        timeline_text += "TIME AXIS:\n"
        timeline_text += "-" * 40 + "\n"
        if self.timeline:
            max_time = max(end for _, end, _, _ in self.timeline)
            time_axis = " ".join([f"{i:2d}" for i in range(max_time + 1)])
            timeline_text += f"Time: {time_axis}\n"
        else:
            timeline_text += "Time: No execution recorded\n"
        
        timeline_text += "\n" + "=" * 80 + "\n"
        
        self.timeline_text.insert('1.0', timeline_text)

        # ---- Results table ----
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)

        for r in self.results:
            pt_used = r['burst'] - (r['burst'] - r.get('remaining', 0)) if 'remaining' in r else r['burst']
            self.results_tree.insert('', 'end', values=(
                r['name'], r['arrival'], r['burst'], r['priority'], pt_used,
                r['first_start'] if r['first_start'] is not None else "N/A",
                r['completion']  if r['completion']  is not None else "N/A",
                r['turnaround']  if r['turnaround']  is not None else "N/A",
                r['waiting'],
                r['response']    if r['response']    is not None else "N/A"
            ))

        # ---- Summary ----
        self.summary_text.delete('1.0', 'end')
        completed = [r for r in self.results if r['completion'] is not None]
        if completed:
            avg_wait = sum(r['waiting'] for r in completed) / len(completed)
            avg_ta   = sum(r['turnaround'] for r in completed) / len(completed)
            avg_resp = sum(r['response'] for r in completed if r['response'] is not None) / len(completed)
            total_bt = sum(r['burst'] for r in completed)
            makespan = max(r['completion'] for r in completed) - min(r['arrival'] for r in completed)
            cpu_util = (total_bt / makespan) * 100 if makespan > 0 else 100.0
            summary_text = (
                f"Summary Statistics:\n"
                f"• Average WT_Now: {avg_wait:.2f}\n"
                f"• Average Turnaround Time: {avg_ta:.2f}\n"
                f"• Average Response Time: {avg_resp:.2f}\n"
                f"• CPU Utilization: {cpu_util:.2f}%\n"
                f"• Total Processes: {len(completed)}\n"
                f"• Total Simulation Time: {makespan}\n"
            )
        else:
            summary_text = "No processes completed."
        self.summary_text.insert('1.0', summary_text)

def _display_results(self, timeline, results, frames):
    self.notebook.select(self.simulation_tab)

    # store data for later
    self.timeline = timeline or []
    self.results  = results or []
    self.frames   = frames or []

    # UI status
    self.status_label.config(text="Simulation completed. Playing animation…")

    # reset animation state
    self.frame_i = 0
    self.anim_total = len(self.frames)
    self._animating = False
    self._anim_after_id = None
    self.status_label.config(text="Simulation ready. Use ▶, Next, or Prev.")

    # clear canvases before first paint
    for c in getattr(self, 'queue_canvases', []):
        c.delete('all')
    self.schedule_canvas.delete('all')

    # prime buttons
    self.play_btn.config(state=('normal' if self.anim_total > 0 else 'disabled'))
    self.pause_btn.config(state='disabled')
    self.reset_btn.config(state=('normal' if self.anim_total > 0 else 'disabled'))
    self.prev_tick_btn.config(state='disabled')
    self.next_tick_btn.config(state=('normal' if self.anim_total > 1 else 'disabled'))

    # paint tick 0 immediately
    if self.anim_total > 0:
        self._repaint_animation_frame()
        self.play_animation()


def _show_error(self, error_message):
    self.play_btn.config(state='normal')
    self.pause_btn.config(state='disabled')
    self.reset_btn.config(state='disabled')
    self.status_label.config(text="Simulation failed!")
    messagebox.showerror("Simulation Error", f"An error occurred: {error_message}")