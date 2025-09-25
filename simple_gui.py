# Simple GUI for MLFQ Scheduler - Beginner Version
# This creates a user-friendly graphical interface using tkinter

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from simple_process import Process, DEFAULT_PROCESSES, DEFAULT_QUANTUM, DEFAULT_DEMOTE_THRESHOLD, DEFAULT_AGING_THRESHOLD
from simple_scheduler import SimpleMLFQScheduler

class MLFQGUI:
    
    #A simple graphical user interface for the MLFQ scheduler.
    #This makes it easy for beginners to use without typing commands.
    
    def __init__(self):
        # Uses tkinter.Tk() to create the main window (W3Schools: Python GUI with Tkinter)
        # This is the main window that holds all the GUI elements
        self.root = tk.Tk()
        self.root.title("MLFQ CPU Scheduler - Beginner Version")
        self.root.geometry("1000x700")
        self.root.minsize(1000, 700)
        self.root.configure(bg='#f0f0f0')

        # For maximizing the window in Windows and Linux
        try:
            self.root.state('zoomed')       
        except tk.TclError:
            self.root.attributes('-zoomed', True)  
        
        # Uses variables to store user input (GeeksforGeeks: Python Tkinter Variables)
        # These automatically update the GUI when changed
        self.num_processes = tk.IntVar(value=len(DEFAULT_PROCESSES))
        self.quantum = tk.IntVar(value=DEFAULT_QUANTUM)
        self.demote_threshold = tk.IntVar(value=DEFAULT_DEMOTE_THRESHOLD)
        self.aging_threshold = tk.IntVar(value=DEFAULT_AGING_THRESHOLD)
        self.preempt = tk.BooleanVar(value=True)
        self.use_default_processes = tk.BooleanVar(value=True)

        # Animation state defaults
        self.frames = []
        self.frame_i = 0
        self._g_idx = 0
        self._animating = False
        self.anim_delay_ms = 120
        self._anim_after_id = None 

        # Color 
        self.idle_color = "#B383B3"
        self.palette = [
            "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7",
            "#DDA0DD", "#98D8C8", "#F7DC6F", "#BB8FCE", "#85C1E9",
        ]
        self.color_map = {} 
        
        # Uses list to store custom processes created by user
        self.custom_processes = []
        
        self.setup_gui()
    
    def setup_gui(self):
        # Create and arrange all the GUI elements.
        # Uses tkinter widgets to create the interface (W3Schools: Python Tkinter Widgets)
        
        # Create main title
        title_label = tk.Label(
            self.root, 
            text="MLFQ CPU Scheduler Simulator",
            font=("Arial", 16, "bold"),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        title_label.pack(pady=10)
        
        # Uses tkinter.Frame to organize sections (GeeksforGeeks: Python Tkinter Frame)
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create tabs
        self.setup_configuration_tab()
        self.setup_simulation_tab()
        self.setup_results_tab()
    
    def setup_configuration_tab(self):
        # Create the combined configuration tab for processes and settings.
        # Uses tkinter.Frame to create a tab for process setup and scheduler settings
        config_frame = ttk.Frame(self.notebook)
        self.notebook.add(config_frame, text="Configuration")
        
        # Create a main container with two columns
        main_container = tk.Frame(config_frame)
        main_container.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Left column for processes
        left_column = tk.Frame(main_container)
        left_column.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        # Right column for settings
        right_column = tk.Frame(main_container)
        right_column.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        # Process count section
        count_frame = tk.LabelFrame(left_column, text="Number of Processes", font=("Arial", 10, "bold"))
        count_frame.pack(fill='x', padx=5, pady=5)
        
        tk.Label(count_frame, text="How many processes?").pack(side='left', padx=5)
        # Uses tkinter.Spinbox for number input (W3Schools: Python Tkinter Spinbox)
        count_spinbox = tk.Spinbox(count_frame, from_=1, to=20, textvariable=self.num_processes, width=10)
        count_spinbox.pack(side='left', padx=5)

        self.num_processes.trace_add('write', lambda *args: self.on_num_processes_changed())
        
        # Default processes option
        default_frame = tk.LabelFrame(left_column, text="Process Options", font=("Arial", 10, "bold"))
        default_frame.pack(fill='x', padx=5, pady=5)
        
        # Uses tkinter.Checkbutton for yes/no options (W3Schools: Python Tkinter Checkbutton)
        default_check = tk.Checkbutton(
            default_frame, 
            text="Use default processes (recommended for beginners)",
            variable=self.use_default_processes,
            command=self.toggle_custom_processes
        )
        default_check.pack(anchor='w', padx=5, pady=2)
        
        # Custom processes section
        self.custom_frame = tk.LabelFrame(left_column, text="Custom Processes", font=("Arial", 10, "bold"))
        self.custom_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Process list with scrollbar
        list_frame = tk.Frame(self.custom_frame)
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Uses tkinter.Treeview for displaying process list (GeeksforGeeks: Python Tkinter Treeview)
        columns = ('Name', 'Arrival', 'Burst', 'Priority')
        self.process_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        
        # Set column headings
        for col in columns:
            self.process_tree.heading(col, text=col)
            self.process_tree.column(col, width=100)

        self.process_tree.bind("<Double-1>", self._on_tree_double_click)
        
        # Uses tkinter.Scrollbar for scrolling (W3Schools: Python Tkinter Scrollbar)
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.process_tree.yview)
        self.process_tree.configure(yscrollcommand=scrollbar.set)
        
        self.process_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Quantum setting
        quantum_frame = tk.LabelFrame(right_column, text="Time Quantum", font=("Arial", 10, "bold"))
        quantum_frame.pack(fill='x', padx=5, pady=5)
        
        tk.Label(quantum_frame, text="How much time should each process get before switching?").pack(anchor='w', padx=5, pady=2)
        tk.Label(quantum_frame, text="(Like giving each person 5 minutes to speak)").pack(anchor='w', padx=20, pady=2)
        
        quantum_spinbox = tk.Spinbox(quantum_frame, from_=1, to=20, textvariable=self.quantum, width=10)
        quantum_spinbox.pack(anchor='w', padx=5, pady=2)
        
        # Demotion threshold
        demote_frame = tk.LabelFrame(right_column, text="Demotion Threshold", font=("Arial", 10, "bold"))
        demote_frame.pack(fill='x', padx=5, pady=5)
        
        tk.Label(demote_frame, text="How long should a process run before moving to lower priority?").pack(anchor='w', padx=5, pady=2)
        tk.Label(demote_frame, text="(If a process runs too long, it gets moved to a less important queue)").pack(anchor='w', padx=20, pady=2)
        
        demote_spinbox = tk.Spinbox(demote_frame, from_=1, to=50, textvariable=self.demote_threshold, width=10)
        demote_spinbox.pack(anchor='w', padx=5, pady=2)
        
        # Aging threshold
        aging_frame = tk.LabelFrame(right_column, text="Aging Threshold", font=("Arial", 10, "bold"))
        aging_frame.pack(fill='x', padx=5, pady=5)
        
        tk.Label(aging_frame, text="How long should a process wait before moving to higher priority?").pack(anchor='w', padx=5, pady=2)
        tk.Label(aging_frame, text="(If a process waits too long, it gets moved to a more important queue)").pack(anchor='w', padx=20, pady=2)
        
        aging_spinbox = tk.Spinbox(aging_frame, from_=0, to=50, textvariable=self.aging_threshold, width=10)
        aging_spinbox.pack(anchor='w', padx=5, pady=2)
        
        # Preemption setting
        preempt_frame = tk.LabelFrame(right_column, text="Preemption", font=("Arial", 10, "bold"))
        preempt_frame.pack(fill='x', padx=5, pady=5)
        
        tk.Label(preempt_frame, text="Should running processes be interrupted when higher priority ones arrive?").pack(anchor='w', padx=5, pady=2)
        tk.Label(preempt_frame, text="(Like stopping a low-priority customer when a VIP arrives)").pack(anchor='w', padx=20, pady=2)
        
        # Uses tkinter.Radiobutton for single choice options (W3Schools: Python Tkinter Radiobutton)
        preempt_yes = tk.Radiobutton(preempt_frame, text="Yes (Recommended)", variable=self.preempt, value=True)
        preempt_yes.pack(anchor='w', padx=5, pady=2)
        
        preempt_no = tk.Radiobutton(preempt_frame, text="No", variable=self.preempt, value=False)
        preempt_no.pack(anchor='w', padx=5, pady=2)
        
        # Help section
        help_frame = tk.LabelFrame(right_column, text="Help", font=("Arial", 10, "bold"))
        help_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        help_text = """
        MLFQ (Multi-Level Feedback Queue) Settings Explained:
        
        • Time Quantum: How long each process can run before switching to another
        • Demotion Threshold: How long a process can run before moving to lower priority
        • Aging Threshold: How long a process waits before moving to higher priority
        • Preemption: Whether to interrupt running processes for higher priority ones
        
        Tip: Use the default values for your first simulation!
        """
        
        # Uses tkinter.Text widget for displaying help text (W3Schools: Python Tkinter Text)
        help_text_widget = tk.Text(help_frame, height=8, wrap='word', bg='#f8f9fa')
        help_text_widget.pack(fill='both', expand=True, padx=5, pady=5)
        help_text_widget.insert('1.0', help_text)
        help_text_widget.config(state='disabled')

        
    
    def setup_simulation_tab(self):
        # Simulation tab
        self.simulation_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.simulation_tab, text="Simulation")
        sim = self.simulation_tab

        # ---------- Controls (replaces the old "Run Simulation" box) ----------
        controls = tk.LabelFrame(sim, text="Controls", font=("Arial", 12, "bold"))
        controls.pack(fill='x', padx=10, pady=10)

        btn_style = {"font": ("Arial", 12, "bold"), "height": 2, "width": 12}
        small_btn_style = {"font": ("Arial", 10, "bold"), "height": 1, "width": 8}

        # Main control buttons
        self.play_btn  = tk.Button(controls, text="▶ Play", bg="#27ae60", fg="white",
                                   state='normal', command=self.on_play_clicked, **btn_style)
        self.pause_btn = tk.Button(controls, text="⏸ Pause", state='disabled', command=self.pause_animation, **btn_style)
        self.reset_btn = tk.Button(controls, text="⟲ Reset", state='disabled', command=self.reset_animation, **btn_style)

        # Tick-by-tick controls
        self.prev_tick_btn = tk.Button(controls, text="⏮ Prev", state='disabled', command=self.previous_tick, **small_btn_style)
        self.next_tick_btn = tk.Button(controls, text="Next ⏭", state='disabled', command=self.next_tick, **small_btn_style)

        # Speed control
        speed_frame = tk.Frame(controls)
        speed_frame.pack(fill='x', pady=5)
        
        tk.Label(speed_frame, text="Speed:", font=("Arial", 10)).pack(side='left', padx=5)
        self.speed_var = tk.IntVar(value=5)
        self.speed_slider = tk.Scale(speed_frame, from_=1, to=10, orient='horizontal', 
                                   variable=self.speed_var, command=self.update_speed, 
                                   length=200, font=("Arial", 9))
        self.speed_slider.pack(side='left', padx=5)

        # Main control row
        main_controls = tk.Frame(controls)
        main_controls.pack(fill='x', pady=5)
        
        self.play_btn.pack(side='left', expand=True, padx=5, pady=5)
        self.pause_btn.pack(side='left', expand=True, padx=5, pady=5)
        self.reset_btn.pack(side='left', expand=True, padx=5, pady=5)

        # Tick controls row
        tick_controls = tk.Frame(controls)
        tick_controls.pack(fill='x', pady=5)
        
        self.prev_tick_btn.pack(side='left', padx=5, pady=5)
        self.next_tick_btn.pack(side='left', padx=5, pady=5)

        # Status and tick display
        status_frame = tk.Frame(controls)
        status_frame.pack(fill='x', pady=5)
        
        self.status_label = tk.Label(status_frame, text="Ready to run simulation", font=("Arial", 10))
        self.status_label.pack(side='left', padx=5)
        
        self.tick_label = tk.Label(status_frame, text="Tick: 0/0", font=("Arial", 10, "bold"), fg="#2c3e50")
        self.tick_label.pack(side='right', padx=5)

        # ---------- Queue/CPU list displays (below the controls) ----------
        lists = tk.Frame(sim)
        lists.pack(fill='x', padx=10, pady=(0, 10))

        def _mk_listbox(parent, title):
            f = tk.Frame(parent)
            tk.Label(f, text=title, font=("Arial", 10, "bold")).pack(anchor='center')
            lb = tk.Listbox(f, height=3)
            lb.pack(fill='both', expand=True)
            return f, lb

        f0, self.lb_q0  = _mk_listbox(lists, "Q0 (Highest)")
        f1, self.lb_q1  = _mk_listbox(lists, "Q1")
        f2, self.lb_q2  = _mk_listbox(lists, "Q2")
        f3, self.lb_cpu = _mk_listbox(lists, "CPU (Running)")

        for i, f in enumerate([f0, f1, f2, f3]):
            f.grid(row=0, column=i, sticky='nsew', padx=5)
            lists.grid_columnconfigure(i, weight=1)

        # ---------- Timeline area ----------
        anim = tk.LabelFrame(sim, text="Animation", font=("Arial", 10, "bold"))
        anim.pack(fill='both', expand=True, padx=10, pady=5)

        tk.Label(anim, text="Simulation Timeline", font=("Arial", 10, "bold")).pack(
            anchor='w', padx=5, pady=(5, 0)
        )

        # Create a frame for timeline with scrollbar
        timeline_container = tk.Frame(anim)
        timeline_container.pack(fill='both', expand=True, padx=5, pady=8)

        self.timeline_canvas = tk.Canvas(timeline_container, height=140, bg="white")
        
        # Add horizontal scrollbar for long timelines
        timeline_scrollbar = ttk.Scrollbar(timeline_container, orient='horizontal', command=self.timeline_canvas.xview)
        self.timeline_canvas.configure(xscrollcommand=timeline_scrollbar.set)
        
        self.timeline_canvas.pack(side='top', fill='both', expand=True)
        timeline_scrollbar.pack(side='bottom', fill='x')

        # ---------- Current settings ----------
        settings = tk.LabelFrame(sim, text="Current Settings", font=("Arial", 10, "bold"))
        settings.pack(fill='x', padx=10, pady=5)

        self.settings_text = tk.Text(settings, height=6, wrap='word', bg='#f8f9fa')
        self.settings_text.pack(fill='x', padx=5, pady=5)

        self.update_settings_display()

        self.toggle_custom_processes()

    
    def setup_results_tab(self):
        # Create the results display tab.
        # Uses tkinter.Frame to create a tab for showing results
        self.results_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.results_tab, text="Results")
        results_frame = self.results_tab
        
        # Create main container with two sections
        main_container = tk.Frame(results_frame)
        main_container.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Timeline section (larger portion)
        timeline_frame = tk.LabelFrame(main_container, text="Execution Timeline", font=("Arial", 12, "bold"))
        timeline_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Uses tkinter.ScrolledText for displaying enhanced timeline (GeeksforGeeks: Python Tkinter ScrolledText)
        self.timeline_text = scrolledtext.ScrolledText(timeline_frame, height=15, wrap='word', font=("Courier", 10))
        self.timeline_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Results table section (smaller portion)
        results_table_frame = tk.LabelFrame(main_container, text="Process Results Summary", font=("Arial", 10, "bold"))
        results_table_frame.pack(fill='x', padx=5, pady=5)
        
        # Create results table
        columns = ('Process', 'Arrival', 'Burst', 'Priority', 'First Start', 'Completion', 'Turnaround', 'Waiting', 'Response')
        self.results_tree = ttk.Treeview(results_table_frame, columns=columns, show='headings', height=6)
        
        # Set column headings and widths
        column_widths = {'Process': 60, 'Arrival': 60, 'Burst': 60, 'Priority': 60, 'First Start': 80, 'Completion': 80, 'Turnaround': 80, 'Waiting': 70, 'Response': 70}
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=column_widths.get(col, 60))
        
        # Add scrollbar for results table
        results_scrollbar = ttk.Scrollbar(results_table_frame, orient='vertical', command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=results_scrollbar.set)
        
        self.results_tree.pack(side='left', fill='both', expand=True)
        results_scrollbar.pack(side='right', fill='y')
        
        # Summary section
        summary_frame = tk.LabelFrame(results_frame, text="Summary Statistics", font=("Arial", 10, "bold"))
        summary_frame.pack(fill='x', padx=10, pady=5)
        
        self.summary_text = tk.Text(summary_frame, height=4, wrap='word', bg='#f8f9fa', font=("Arial", 10))
        self.summary_text.pack(fill='x', padx=5, pady=5)
    
    def toggle_custom_processes(self):
        # Show or hide the custom processes section based on checkbox.
        # Uses tkinter widget methods to show/hide sections (GeeksforGeeks: Python Tkinter Widget Methods)
        use_defaults = self.use_default_processes.get()
        self.custom_frame.pack(fill='both', expand=True, padx=10, pady=5)

        n = max(1, int(self.num_processes.get()))

        # If we're switching FROM defaults TO custom, seed custom_processes
        # with whatever is currently visible (the default rows).
        if not use_defaults:
            visible_rows = [self.process_tree.item(i, 'values') for i in self.process_tree.get_children()]
            if visible_rows:
                self.custom_processes = [(str(nm), int(a), int(b), int(p)) for (nm, a, b, p) in visible_rows]
            # If nothing visible yet (e.g., first time), fall back to defaults[:n]
            if not self.custom_processes:
                self.custom_processes = list(DEFAULT_PROCESSES[:n])

        # Clear table before repopulating
        for item in self.process_tree.get_children():
            self.process_tree.delete(item)

        if use_defaults:
            # Exactly N defaults
            for name, arrival, burst, priority in DEFAULT_PROCESSES[:n]:
                self.process_tree.insert('', 'end', values=(name, arrival, burst, priority))
        else:
            # Use the seeded custom rows, then ensure we have exactly N
            for name, arrival, burst, priority in self.custom_processes:
                self.process_tree.insert('', 'end', values=(name, arrival, burst, priority))
            self._ensure_custom_row_count(n)

        self.update_settings_display()
    
    
    def _next_expected_name(self):
        names = [self.process_tree.item(i, 'values')[0] for i in self.process_tree.get_children()]
        nums = []
        for nm in names:
            if isinstance(nm, str) and nm.startswith('P') and nm[1:].isdigit():
                nums.append(int(nm[1:]))
        nxt = (max(nums) + 1) if nums else 1
        return f"P{nxt}"

    def _ensure_custom_row_count(self, target_n):
        # Make table have exactly target_n rows; auto-add P# rows or trim from bottom.
        current_iids = list(self.process_tree.get_children())
        cur_n = len(current_iids)

        # Add rows if fewer
        while cur_n < target_n:
            next_name = self._next_expected_name()     # e.g., 'P8'
            try:
                idx = int(next_name[1:]) - 1          # 0-based index into DEFAULT_PROCESSES
            except ValueError:
                idx = None

            if idx is not None and 0 <= idx < len(DEFAULT_PROCESSES):
                name, arrival, burst, priority = DEFAULT_PROCESSES[idx]
                # Ensure the name matches the sequence we're enforcing
                name = next_name
            else:
                # Fallback if we ran out of built-ins
                name, arrival, burst, priority = next_name, 0, 1, 1

            self.process_tree.insert('', 'end', values=(name, arrival, burst, priority))
            if not self.use_default_processes.get():
                self.custom_processes.append((name, arrival, burst, priority))
            cur_n += 1
        
        # Trim rows if more (remove from bottom)
        while cur_n > target_n:
            iid = self.process_tree.get_children()[-1]
            vals = self.process_tree.item(iid, 'values')
            self.process_tree.delete(iid)
            if not self.use_default_processes.get():
                try:
                    self.custom_processes.remove((vals[0], int(vals[1]), int(vals[2]), int(vals[3])))
                except ValueError:
                    pass
            cur_n -= 1

    def _on_tree_double_click(self, event):
        # For process customizations
        # Name column is locked to keep it incremental.
        
        # Block edits in defaults mode
        if self.use_default_processes.get():
            return

        region = self.process_tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        row_id = self.process_tree.identify_row(event.y)
        col_id = self.process_tree.identify_column(event.x)  # '#1'..'#4'
        if not row_id or not col_id:
            return

        # Column mapping: #1=Name (locked), #2=Arrival, #3=Burst, #4=Priority
        if col_id == "#1":
            messagebox.showinfo("Name locked", "Process IDs are locked (P1…PN). Edit Arrival, Burst, or Priority instead.")
            return

        bbox = self.process_tree.bbox(row_id, col_id)
        if not bbox:
            return
        x, y, w, h = bbox

        # Current value
        cur_vals = list(self.process_tree.item(row_id, "values"))
        cur_text = cur_vals[int(col_id[1:]) - 1]

        # Create an Entry overlayed on the cell
        self._cell_editor = tk.Entry(self.process_tree)
        self._cell_editor.insert(0, str(cur_text))
        self._cell_editor.select_range(0, 'end')
        self._cell_editor.focus_set()
        self._cell_editor.place(x=x, y=y, width=w, height=h)

        # Commit/cancel
        self._cell_editor.bind("<Return>",      lambda e: self._commit_cell_edit(row_id, col_id))
        self._cell_editor.bind("<KP_Enter>",    lambda e: self._commit_cell_edit(row_id, col_id))
        self._cell_editor.bind("<Escape>",      lambda e: self._cancel_cell_edit())
        self._cell_editor.bind("<FocusOut>",    lambda e: self._commit_cell_edit(row_id, col_id))

    def _cancel_cell_edit(self):
        if hasattr(self, "_cell_editor") and self._cell_editor:
            self._cell_editor.destroy()
            self._cell_editor = None

    def _commit_cell_edit(self, row_id, col_id):
        # Validate input, write back to Treeview, and sync self.custom_processes.
        if not hasattr(self, "_cell_editor") or not self._cell_editor:
            return
        new_text = self._cell_editor.get().strip()
        self._cell_editor.destroy()
        self._cell_editor = None

        # Only numeric columns can be edited
        idx = int(col_id[1:]) - 1  # 1-based to 0-based
        try:
            val = int(new_text)
        except ValueError:
            messagebox.showerror("Invalid input", "Please enter an integer value.")
            return

        # Validate per-column
        if idx == 1:        # Arrival
            if val < 0:
                messagebox.showerror("Invalid Arrival", "Arrival must be ≥ 0.")
                return
        elif idx == 2:      # Burst
            if val < 1:
                messagebox.showerror("Invalid Burst", "Burst must be ≥ 1.")
                return
        elif idx == 3:      # Priority
            if val < 1 or val > 3:
                messagebox.showerror("Invalid Priority", "Priority must be between 1 and 3.")
                return

        # Write back to Treeview
        values = list(self.process_tree.item(row_id, "values"))
        values[idx] = str(val)
        self.process_tree.item(row_id, values=values)

        # Sync custom_processes (custom mode only)
        if not self.use_default_processes.get():
            rows = [self.process_tree.item(i, 'values') for i in self.process_tree.get_children()]
            self.custom_processes = [(str(n), int(a), int(b), int(p)) for (n, a, b, p) in rows]

    def on_num_processes_changed(self):
        # Keep the table in sync with the requested count in both modes.
        n = max(1, int(self.num_processes.get()))
        if self.use_default_processes.get():
            # repopulate exactly N defaults
            for item in self.process_tree.get_children():
                self.process_tree.delete(item)
            for name, arrival, burst, priority in DEFAULT_PROCESSES[:n]:
                self.process_tree.insert('', 'end', values=(name, arrival, burst, priority))
        else:
            # If custom list is empty (first-time custom), seed from defaults[:n]
            if not self.custom_processes:
                self.custom_processes = list(DEFAULT_PROCESSES[:n])
                # also reflect in the table immediately
                for item in self.process_tree.get_children():
                    self.process_tree.delete(item)
                for name, arrival, burst, priority in self.custom_processes:
                    self.process_tree.insert('', 'end', values=(name, arrival, burst, priority))
            # then enforce exact N in custom mode (adds beyond using remaining defaults if available)
            self._ensure_custom_row_count(n)

        self.update_settings_display()

    
    def update_settings_display(self):
        # Update the settings display in the simulation tab.
        # Uses tkinter Text widget methods to update display (W3Schools: Python Tkinter Text)
        self.settings_text.config(state='normal')
        self.settings_text.delete('1.0', 'end')
        
        settings_info = f"""
        Current Settings:
        • Number of Processes: {self.num_processes.get()}
        • Time Quantum: {self.quantum.get()}
        • Demotion Threshold: {self.demote_threshold.get()}
        • Aging Threshold: {self.aging_threshold.get()}
        • Preemption: {'Yes' if self.preempt.get() else 'No'}
        • Using Default Processes: {'Yes' if self.use_default_processes.get() else 'No'}
        """
        
        self.settings_text.insert('1.0', settings_info)
        self.settings_text.config(state='disabled')
    
    def run_simulation(self):
        # Run the MLFQ simulation in a separate thread.
        # Uses threading to prevent GUI freezing (GeeksforGeeks: Python Threading)
        self.play_btn.config(state='disabled')
        self.status_label.config(text="Running simulation...")
        
        # Uses threading.Thread to run simulation in background (W3Schools: Python Threading)
        simulation_thread = threading.Thread(target=self._run_simulation_background)
        simulation_thread.daemon = True
        simulation_thread.start()
    
    def _run_simulation_background(self):
        # Run the actual simulation in the background thread.
        try:
            # Get processes to use
            if self.use_default_processes.get():
                # Uses slicing to get the right number of default processes (GeeksforGeeks: Python List Slicing)
                processes = DEFAULT_PROCESSES[:self.num_processes.get()]
            else:
                 # Read rows directly from the table to use the visible configuration
                items = self.process_tree.get_children()
                rows  = [self.process_tree.item(i, 'values') for i in items]
                processes = [
                    (str(name), int(arrival), int(burst), int(priority))
                    for (name, arrival, burst, priority) in rows
                ][:self.num_processes.get()]
            
            # Create scheduler
            scheduler = SimpleMLFQScheduler(
                quantum=self.quantum.get(),
                demote_threshold=self.demote_threshold.get(),
                aging_threshold=self.aging_threshold.get(),
                preempt=self.preempt.get()
            )
            
            # Run simulation
            timeline, results, frames = scheduler.simulate_with_frames(processes)
            
            # Update GUI in main thread
            # Uses tkinter.after to update GUI from background thread (GeeksforGeeks: Python Tkinter Threading)
            self.root.after(0, self._display_results, timeline, results, frames)
            
        except Exception as e:
            # Uses tkinter.after to show error in main thread
            self.root.after(0, self._show_error, str(e))
    
    def _display_results(self, timeline, results, frames):
        self.notebook.select(self.simulation_tab)

        # store data for later
        self.timeline = timeline
        self.results  = results
        self.frames   = frames or []

        # UI status
        self.status_label.config(text="Simulation completed. Playing animation…")

        # reset animation surfaces and color mapping
        self.frame_i = 0
        self._g_idx  = 0
        self.color_map = {}

        if hasattr(self, 'gantt_canvas'):
            self.gantt_canvas.delete('all')
        for lb in (getattr(self, 'lb_q0', None),
                   getattr(self, 'lb_q1', None),
                   getattr(self, 'lb_q2', None),
                   getattr(self, 'lb_cpu', None)):
            if lb: lb.delete(0, 'end')

        # prepare multi-row timeline
        self._init_timeline_canvas()
        self.timeline_canvas.update_idletasks()
        self._cell_w = None
        self.anim_total = len(self.frames)

        # auto-play using the normal play() path so buttons are consistent
        self.play_animation()
        self.reset_btn.config(state='normal')

    
    def _show_error(self, error_message):
        self.play_btn.config(state='normal')
        self.pause_btn.config(state='disabled')
        self.reset_btn.config(state='disabled')
        self.status_label.config(text="Simulation failed!")
        messagebox.showerror("Simulation Error", f"An error occurred: {error_message}")
    
    def run(self):
        # Start the GUI application.
        # Uses tkinter.mainloop to start the GUI (W3Schools: Python Tkinter Mainloop)
        # This makes the window appear and handles user interactions
        self.root.mainloop()

    def _repaint_animation_frame(self):
        if not self.frames:
            return
        fr = self.frames[self.frame_i]

        def fill(lb, items):
            if not lb: return
            lb.delete(0, 'end')
            for it in items: lb.insert('end', it)

        fill(getattr(self, 'lb_q0', None), fr['queues'][0])
        fill(getattr(self, 'lb_q1', None), fr['queues'][1])
        fill(getattr(self, 'lb_q2', None), fr['queues'][2])
        fill(getattr(self, 'lb_cpu', None), [fr['running']] if fr['running'] else [])

        self._append_multirow_cells(fr)

    def _append_gantt_cell(self, pid):
        if not hasattr(self, 'gantt_canvas'): return
        w = self.gantt_canvas.winfo_width() or 600
        total = max(1, len(self.frames))
        unit = max(1, int(w / total))
        idx = getattr(self, '_g_idx', 0)
        color = self._color_for(pid)
        self.gantt_canvas.create_rectangle(idx*unit, 0, (idx+1)*unit, 30,
                                        fill=color, outline='black')
        if pid:
            self.gantt_canvas.create_text(idx*unit + unit/2, 15, text=pid, fill="white", font=("Arial", 8))
        self._g_idx = idx + 1

    def _color_for(self, pid):
        if not pid:    # Idle color
            return self.idle_color
        
        # Use consistent color mapping based on process name
        if pid not in self.color_map:
            # Assign colors from predefined palette
            color_index = len(self.color_map) % len(self.palette)
            self.color_map[pid] = self.palette[color_index]
        
        return self.color_map[pid]

    def _append_multirow_cells(self, fr):
        # Draw one time-slice for Q0, Q1, Q2, and CPU.
        if not hasattr(self, 'timeline_canvas'):
            return
        c = self.timeline_canvas
        row_h  = getattr(self, '_row_h', 30)
        left_w = getattr(self, '_left_w', 70)

        # Calculate responsive cell width
        if getattr(self, '_cell_w', None) is None:
            width = max(600, c.winfo_width())
            total_frames = max(1, len(self.frames))
            
            # Calculate minimum width needed for text readability
            min_text_width = 50  # Minimum width for process names
            available_width = width - left_w
            
            # Calculate optimal cell width
            optimal_width = max(min_text_width, available_width // total_frames)
            
            # If we have too many frames, use minimum width and enable scrolling
            if optimal_width < min_text_width:
                optimal_width = min_text_width
                # Store the total width needed for scrolling
                self._total_timeline_width = left_w + (total_frames * optimal_width)
            
            self._cell_w = optimal_width

        unit = self._cell_w
        idx = getattr(self, '_g_idx', 0)

        # What to show per row at this tick:
        q0_head = fr['queues'][0][0] if fr['queues'][0] else None
        q1_head = fr['queues'][1][0] if fr['queues'][1] else None
        q2_head = fr['queues'][2][0] if fr['queues'][2] else None
        cpu_pid = fr['running'] if fr['running'] else None

        rows = [q0_head, q1_head, q2_head, cpu_pid]

        x0 = left_w + idx * unit
        x1 = left_w + (idx + 1) * unit

        # Calculate responsive font size based on cell width
        font_size = self._calculate_font_size(unit)

        for r, pid in enumerate(rows):
            y0 = r * row_h
            y1 = y0 + row_h - 1
            col = self._color_for(pid)
            c.create_rectangle(x0, y0, x1, y1, fill=col, outline='black')
            
            # Use responsive font size and ensure text fits
            text = pid if pid else "Idle"
            c.create_text((x0 + x1)/2, y0 + row_h/2,
                        text=text,
                        font=("Arial", font_size))
        
        # time tick label at the bottom row with responsive font
        tick_font_size = max(6, min(8, font_size - 1))
        c.create_text(x0 + 5, 4*row_h + 8, text=str(idx), anchor='w', font=("Arial", tick_font_size))

        self._g_idx = idx + 1

    def _calculate_font_size(self, cell_width):
        # Calculate appropriate font size based on cell width to prevent text overlap.
        # Base font size calculation
        if cell_width >= 80:
            return 10
        elif cell_width >= 60:
            return 9
        elif cell_width >= 40:
            return 8
        elif cell_width >= 30:
            return 7
        else:
            return 6


    def play_animation(self):
        # Start automated animation playback.
        if not self.frames:
            return
        self._animating = True
        self.play_btn.config(state='disabled')
        self.pause_btn.config(state='normal')
        self.prev_tick_btn.config(state='disabled')
        self.next_tick_btn.config(state='disabled')
        self._schedule_next_tick()

    def pause_animation(self):
        # Pause the automated animation.
        self._animating = False
        if self._anim_after_id is not None:
            self.root.after_cancel(self._anim_after_id)
            self._anim_after_id = None
        self.play_btn.config(state='normal')
        self.pause_btn.config(state='disabled')
        self.prev_tick_btn.config(state='normal')
        self.next_tick_btn.config(state='normal')
        self.update_tick_display()

    def reset_animation(self):
        # Reset animation to the beginning.
        self._animating = False
        if self._anim_after_id is not None:
            self.root.after_cancel(self._anim_after_id)
            self._anim_after_id = None
        
        self.frame_i = 0
        self._g_idx = 0
        
        # Clear and redraw timeline
        if hasattr(self, 'timeline_canvas'):
            self._init_timeline_canvas()
            if self.frames:
                self._append_multirow_cells(self.frames[0])
        
        # Update controls
        self.play_btn.config(state='normal')
        self.pause_btn.config(state='disabled')
        self.prev_tick_btn.config(state='disabled')
        self.next_tick_btn.config(state='normal' if len(self.frames) > 1 else 'disabled')
        self.update_tick_display()

    def next_tick(self):
        # Move to the next tick manually.
        if not self.frames or self.frame_i >= len(self.frames) - 1:
            return
        
        self.frame_i += 1
        self._repaint_animation_frame()
        self.update_tick_display()
        
        # Update button states
        self.prev_tick_btn.config(state='normal')
        if self.frame_i >= len(self.frames) - 1:
            self.next_tick_btn.config(state='disabled')

    def previous_tick(self):
        # Move to the previous tick manually.
        if not self.frames or self.frame_i <= 0:
            return
        
        self.frame_i -= 1
        self._repaint_animation_frame()
        self.update_tick_display()
        
        # Update button states
        self.next_tick_btn.config(state='normal')
        if self.frame_i <= 0:
            self.prev_tick_btn.config(state='disabled')

    def update_speed(self, value):
        # Update animation speed based on slider value.
        # Convert slider value (1-10) to delay in milliseconds
        # 1 = fastest (50ms), 10 = slowest (500ms)
        try:
            v = max(1, min(10, int(value)))
        except Exception:
            v = 5
        self.anim_delay_ms = 50 * (11 - v)   # 1→500ms, 10→50ms

        # If we're currently animating, apply the new delay immediately
        if self._animating:
            if self._anim_after_id is not None:
                self.root.after_cancel(self._anim_after_id)
                self._anim_after_id = None
            self._schedule_next_tick()

    def update_tick_display(self):
        # Update the tick display label.
        if not self.frames:
            self.tick_label.config(text="Tick: 0/0")
            return
        
        total_ticks = len(self.frames)
        current_tick = self.frame_i + 1
        self.tick_label.config(text=f"Tick: {current_tick}/{total_ticks}")

    def on_play_clicked(self):
        if not self.frames or self.frame_i >= len(self.frames):
            # Fresh run
            self.status_label.config(text="Running simulation...")
            self.play_btn.config(state='disabled')
            self.run_simulation()
        else:
            # Resume from pause
            self.play_animation()

    def _start_animation(self):
        # Begin auto-playing the animation once frames are ready.
        self.frame_i = 0
        self.anim_total = len(self.frames) if self.frames else 0
        self._init_timeline_canvas()
        self.timeline_canvas.update_idletasks()  # make sure width is available
        self._cell_w = None
        self._schedule_next_tick()

    def _schedule_next_tick(self):
        if self._anim_after_id is not None:
            self.root.after_cancel(self._anim_after_id)
            self._anim_after_id = None
        self._anim_after_id = self.root.after(self.anim_delay_ms, self._animate_step)

    def _animate_step(self):
        if not self.frames or self.frame_i >= self.anim_total:
            self._anim_after_id = None
            self._on_animation_finished()
            return

        fr = self.frames[self.frame_i]

        # Update listboxes
        self._fill_queue_listboxes(fr)

        # Draw one column for Q0, Q1, Q2, CPU
        self._append_multirow_cells(fr)        

        self.frame_i += 1
        self.update_tick_display()
        
        # Update button states
        if self.frame_i >= self.anim_total:
            self.next_tick_btn.config(state='disabled')
        else:
            self.next_tick_btn.config(state='normal')
        
        self.prev_tick_btn.config(state='normal')
        
        self._schedule_next_tick()

    def _fill_queue_listboxes(self, fr):
            def fill(lb, items):
                if not lb: return
                lb.delete(0, 'end')
                for it in items:
                    lb.insert('end', it)
            fill(getattr(self, 'lb_q0', None), fr['queues'][0])
            fill(getattr(self, 'lb_q1', None), fr['queues'][1])
            fill(getattr(self, 'lb_q2', None), fr['queues'][2])
            fill(getattr(self, 'lb_cpu', None), [fr['running']] if fr['running'] else [])


    def _populate_results_tab(self):
        # Fill the Results tab using self.timeline and self.results.
        # ---- Enhanced Timeline text ----
        self.timeline_text.delete('1.0', 'end')
        
        # Header section
        timeline_text = "=" * 80 + "\n"
        timeline_text += "MLFQ CPU SCHEDULER - EXECUTION TIMELINE\n"
        timeline_text += "=" * 80 + "\n\n"
        
        # Scheduling Rules Section
        timeline_text += "SCHEDULING RULES:\n"
        timeline_text += "-" * 40 + "\n"
        timeline_text += f"• Time Quantum: {self.quantum.get()} time units\n"
        timeline_text += f"• Demotion Threshold: {self.demote_threshold.get()} time units\n"
        timeline_text += f"• Aging Threshold: {self.aging_threshold.get()} time units\n"
        timeline_text += f"• Preemption: {'Enabled' if self.preempt.get() else 'Disabled'}\n\n"
        
        # Process Details Section
        timeline_text += "PROCESS DETAILS:\n"
        timeline_text += "-" * 40 + "\n"
        timeline_text += f"{'Process':<10} {'Priority':<8} {'Arrival':<7} {'Burst':<6} {'Completion':<10} {'Turnaround':<10} {'Waiting':<8}\n"
        timeline_text += "-" * 70 + "\n"
        
        for r in self.results:
            timeline_text += f"{r['name']:<10} {r['priority']:<8} {r['arrival']:<7} {r['burst']:<6} "
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
            self.results_tree.insert('', 'end', values=(
                r['name'], r['arrival'], r['burst'], r['priority'],
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
                f"• Average Waiting Time: {avg_wait:.2f}\n"
                f"• Average Turnaround Time: {avg_ta:.2f}\n"
                f"• Average Response Time: {avg_resp:.2f}\n"
                f"• CPU Utilization: {cpu_util:.2f}%\n"
                f"• Total Processes: {len(completed)}\n"
                f"• Total Simulation Time: {makespan}\n"
            )
        else:
            summary_text = "No processes completed."
        self.summary_text.insert('1.0', summary_text)


    def _on_animation_finished(self):
        # Called once the last frame is drawn.
        self.status_label.config(text="Animation finished.")
        # now populate and reveal the Results tab
        self._populate_results_tab()
        self.notebook.select(self.results_tab)
        self.play_btn.config(state='normal')

    def _init_timeline_canvas(self):
        if not hasattr(self, 'timeline_canvas'):
            return
        c = self.timeline_canvas
        c.delete('all')

        # layout constants used by _append_multirow_cells
        self._row_h  = 30        # per-row height
        self._left_w = 70        # left label gutter
        rows = ["Q0", "Q1", "Q2", "CPU"]

        # ensure canvas tall enough for 4 rows + small time-axis strip
        c.config(height=self._row_h * 4 + 18)

        # Calculate timeline width - use stored width if available, otherwise calculate
        if hasattr(self, '_total_timeline_width'):
            timeline_width = self._total_timeline_width
        else:
            # Estimate width based on frames
            total_frames = len(self.frames) if self.frames else 1
            min_cell_width = 50
            timeline_width = self._left_w + (total_frames * min_cell_width)
        
        # Set scroll region for horizontal scrolling
        c.configure(scrollregion=(0, 0, timeline_width, self._row_h * 4 + 18))

        # draw row labels + horizontal separators
        width = c.winfo_width() or 800
        for i, label in enumerate(rows):
            y0 = i * self._row_h
            y1 = y0 + self._row_h
            # label background
            c.create_rectangle(0, y0, self._left_w, y1, fill="#f7f7f7", outline="black")
            # label text
            c.create_text(self._left_w - 5, (y0 + y1) / 2, text=label,
                        anchor='e', font=("Arial", 9, "bold"))
            # row separator line across the timeline area
            c.create_line(self._left_w, y1, timeline_width, y1, fill="#cccccc")

        # small 't' mark for time axis below rows
        c.create_text(5, self._row_h * 4 + 8, text="t", anchor='w', font=("Arial", 8))

        # reset the column index used by _append_multirow_cells
        self._g_idx = 0

        # (optional) recompute column width on resize
        def _on_resize(_evt):
            # just clear guides and redraw them to match the new width
            self._init_timeline_canvas()
            # also redraw the already-drawn columns if we have any frames shown
            if self.frames and self.frame_i > 0:
                # replay the already drawn ticks quickly to rebuild the picture
                idx_backup = self._g_idx
                self._g_idx = 0
                for i in range(self.frame_i):
                    self._append_multirow_cells(self.frames[i])
                self._g_idx = idx_backup
        c.bind("<Configure>", lambda e: c.after_idle(_on_resize, e))


def main():
    # Main function to start the GUI application.
    # Uses try-except to handle any startup errors (W3Schools: Python Try Except)
    try:
        # Creates and runs the GUI application
        app = MLFQGUI()
        app.run()
    except Exception as e:
        # Uses tkinter.messagebox to show startup errors (W3Schools: Python Tkinter Messagebox)
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        messagebox.showerror("Startup Error", f"Failed to start the application: {e}")
        root.destroy()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # Graceful exit if Ctrl+C is pressed in the console
        pass
