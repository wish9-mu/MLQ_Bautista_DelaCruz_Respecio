# Simple GUI for MLFQ Scheduler - Beginner Version
# This creates a user-friendly graphical interface using tkinter

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import os
from simple_process import Process, DEFAULT_PROCESSES, DEFAULT_QUANTUM, DEFAULT_DEMOTE_THRESHOLD, DEFAULT_AGING_THRESHOLD, load_defaults
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
        # Separate quantums for each queue (Q0=highest priority, Q2=lowest priority)
        self.quantum_q0 = tk.IntVar(value=3)  # Highest priority - shortest quantum
        self.quantum_q1 = tk.IntVar(value=3)  # Medium priority - medium quantum  
        self.quantum_q2 = tk.IntVar(value=3)  # Lowest priority - longest quantum
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

        # Color - Custom palette based on process ranges
        self.idle_color = "#808080"  # Gray for idle
        
        # Process-specific color ranges
        self.red_shades = ["#8B0000", "#DC143C", "#FF0000"]      # P1-P3: Dark Red, Crimson, Red
        self.orange_shades = ["#FF4500", "#FF8C00"]               # P4-P5: Orange Red, Dark Orange
        self.green_shades = ["#228B22", "#32CD32"]                # P6-P7: Forest Green, Lime Green
        self.blue_violet_shades = [                               # P8+: Blue to Violet
            "#0000FF", "#4169E1", "#1E90FF", "#00BFFF",          # Blues
            "#8A2BE2", "#9932CC", "#9400D3", "#8B008B",           # Violets
            "#4B0082", "#6A5ACD", "#7B68EE", "#9370DB"            # More violets
        ]
        self.color_map = {} 
        
        # Uses list to store custom processes created by user
        self.custom_processes = []
        
        # Track loaded file
        self.loaded_file_path = None
        self.loaded_file_processes = []
        
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
        self.count_spinbox = tk.Spinbox(count_frame, from_=1, to=20, textvariable=self.num_processes, width=10)
        self.count_spinbox.pack(side='left', padx=5)

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
        
        # File upload section
        file_frame = tk.Frame(default_frame)
        file_frame.pack(fill='x', padx=5, pady=5)
        
        tk.Label(file_frame, text="Or upload a .txt file with custom processes:", font=("Arial", 9)).pack(anchor='w')
        
        file_btn_frame = tk.Frame(file_frame)
        file_btn_frame.pack(fill='x', pady=2)
        
        self.upload_btn = tk.Button(file_btn_frame, text="📁 Upload .txt File", 
                                   command=self.upload_process_file, 
                                   font=("Arial", 9), bg="#3498db", fg="white")
        self.upload_btn.pack(side='left', padx=(0, 5))
        
        self.file_label = tk.Label(file_btn_frame, text="No file loaded", 
                                  font=("Arial", 8), fg="#666666")
        self.file_label.pack(side='left')
        
        self.clear_file_btn = tk.Button(file_btn_frame, text="✖ Clear", 
                                        command=self.clear_uploaded_file, 
                                        font=("Arial", 8), state='disabled')
        self.clear_file_btn.pack(side='left', padx=(5, 0))
        
        # Custom processes section
        self.custom_frame = tk.LabelFrame(left_column, text="Custom Processes", font=("Arial", 10, "bold"))
        self.custom_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Help text for editing
        help_text_frame = tk.Frame(self.custom_frame)
        help_text_frame.pack(fill='x', padx=5, pady=(5, 0))
        
        self.help_label = tk.Label(help_text_frame, 
                                  text="💡 Double-click on Arrival, BT_Now, PT_Now, or PT_Used to edit values", 
                                  font=("Arial", 9), 
                                  fg="#666666",
                                  wraplength=300)
        self.help_label.pack(anchor='w')
        
        # Process list with scrollbar
        list_frame = tk.Frame(self.custom_frame)
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Uses tkinter.Treeview for displaying process list (GeeksforGeeks: Python Tkinter Treeview)
        columns = ('Name', 'Arrival', 'BT_Now', 'PT_Now', 'PT_Used')
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
        
        # Time Quantum settings for each queue
        quantum_frame = tk.LabelFrame(right_column, text="Time Quantum per Queue", font=("Arial", 10, "bold"))
        quantum_frame.pack(fill='x', padx=5, pady=5)
        
        tk.Label(quantum_frame, text="How much time should each process get in each queue?").pack(anchor='w', padx=5, pady=2)
        tk.Label(quantum_frame, text="(Higher priority queues get shorter time slices)").pack(anchor='w', padx=20, pady=2)
        
        # Q0 (Highest Priority) quantum
        q0_frame = tk.Frame(quantum_frame)
        q0_frame.pack(fill='x', padx=5, pady=2)
        tk.Label(q0_frame, text="Q0 (Highest Priority):", font=("Arial", 9, "bold")).pack(side='left')
        q0_spinbox = tk.Spinbox(q0_frame, from_=1, to=20, textvariable=self.quantum_q0, width=8)
        q0_spinbox.pack(side='left', padx=(5, 0))
        
        # Q1 (Medium Priority) quantum
        q1_frame = tk.Frame(quantum_frame)
        q1_frame.pack(fill='x', padx=5, pady=2)
        tk.Label(q1_frame, text="Q1 (Medium Priority):", font=("Arial", 9, "bold")).pack(side='left')
        q1_spinbox = tk.Spinbox(q1_frame, from_=1, to=20, textvariable=self.quantum_q1, width=8)
        q1_spinbox.pack(side='left', padx=(5, 0))
        
        # Q2 (Lowest Priority) quantum
        q2_frame = tk.Frame(quantum_frame)
        q2_frame.pack(fill='x', padx=5, pady=2)
        tk.Label(q2_frame, text="Q2 (Lowest Priority):", font=("Arial", 9, "bold")).pack(side='left')
        q2_spinbox = tk.Spinbox(q2_frame, from_=1, to=20, textvariable=self.quantum_q2, width=8)
        q2_spinbox.pack(side='left', padx=(5, 0))
        
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
        
        Process Attributes:
        • BT_Now: Burst Time (total CPU time needed)
        • PT_Now: Priority Level (1=highest, 3=lowest)
        • PT_Used: Processing Time Used (CPU time used so far)
        • WT_Now: Waiting Time (time spent waiting in queues)
        
        Queue Display Abbreviations:
        • BT: Burst Time, PT: Priority Level, WT: Waiting Time, AT: Arrival Time
        
        File Upload Format (.txt):
        ProcessName ArrivalTime BT_Now PT_Now PT_Used
        Example: P1 0 5 1 0
        
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

        # ---------- Simulation Status Header ----------
        status_header = tk.Frame(sim, bg='#2c3e50', height=60)
        status_header.pack(fill='x', padx=10, pady=(10, 5))
        status_header.pack_propagate(False)
        
        # Timer and current process info
        timer_frame = tk.Frame(status_header, bg='#2c3e50')
        timer_frame.pack(side='left', fill='y', padx=10, pady=5)
        
        self.timer_label = tk.Label(timer_frame, text="Timer: 0", font=("Arial", 14, "bold"), 
                                   bg='#2c3e50', fg='white')
        self.timer_label.pack(anchor='w')
        
        self.current_process_label = tk.Label(timer_frame, text="Running: None", font=("Arial", 12), 
                                            bg='#2c3e50', fg='#ecf0f1')
        self.current_process_label.pack(anchor='w')
        
        self.execution_time_label = tk.Label(timer_frame, text="Execution Time: 0", font=("Arial", 10), 
                                           bg='#2c3e50', fg='#bdc3c7')
        self.execution_time_label.pack(anchor='w')

        # Controls on the right side of header
        controls_frame = tk.Frame(status_header, bg='#2c3e50')
        controls_frame.pack(side='right', fill='y', padx=10, pady=5)
        
        btn_style = {"font": ("Arial", 10, "bold"), "height": 1, "width": 8}
        
        self.play_btn = tk.Button(controls_frame, text="▶ Play", bg="#27ae60", fg="white",
                                 state='normal', command=self.on_play_clicked, **btn_style)
        self.pause_btn = tk.Button(controls_frame, text="⏸ Pause", state='disabled', 
                                  command=self.pause_animation, **btn_style)
        self.reset_btn = tk.Button(controls_frame, text="⟲ Reset", state='disabled', 
                                  command=self.reset_animation, **btn_style)
        
        self.play_btn.pack(side='left', padx=2)
        self.pause_btn.pack(side='left', padx=2)
        self.reset_btn.pack(side='left', padx=2)

        # Speed control
        speed_frame = tk.Frame(controls_frame, bg='#2c3e50')
        speed_frame.pack(side='left', padx=(10, 0))
        
        tk.Label(speed_frame, text="Speed:", font=("Arial", 9), bg='#2c3e50', fg='white').pack(side='left')
        self.speed_var = tk.IntVar(value=5)
        self.speed_slider = tk.Scale(speed_frame, from_=1, to=10, orient='horizontal', 
                                   variable=self.speed_var, command=self.update_speed, 
                                   length=100, font=("Arial", 8), bg='#2c3e50', fg='white')
        self.speed_slider.pack(side='left', padx=2)

        # ---------- Main Content Area ----------
        main_content = tk.Frame(sim)
        main_content.pack(fill='both', expand=True, padx=10, pady=5)

        # Left side - Queues
        left_panel = tk.Frame(main_content)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 5))

        # Queue 0 (High Priority)
        q0_frame = tk.LabelFrame(left_panel, text="Q0", font=("Arial", 12, "bold"))
        q0_frame.pack(fill='both', expand=True, pady=(0, 5))
        
        self.q0_canvas = tk.Canvas(q0_frame, height=120, bg="white")
        self.q0_canvas.pack(fill='both', expand=True, padx=5, pady=5)

        # Queue 1 (Medium Priority)
        q1_frame = tk.LabelFrame(left_panel, text="Q1", font=("Arial", 12, "bold"))
        q1_frame.pack(fill='both', expand=True, pady=(0, 5))
        
        self.q1_canvas = tk.Canvas(q1_frame, height=120, bg="white")
        self.q1_canvas.pack(fill='both', expand=True, padx=5, pady=5)

        # Queue 2 (Low Priority)
        q2_frame = tk.LabelFrame(left_panel, text="Q2", font=("Arial", 12, "bold"))
        q2_frame.pack(fill='both', expand=True, pady=(0, 5))
        
        self.q2_canvas = tk.Canvas(q2_frame, height=120, bg="white")
        self.q2_canvas.pack(fill='both', expand=True, padx=5, pady=5)

        # Right side - Running Processes/Schedule
        right_panel = tk.Frame(main_content)
        right_panel.pack(side='right', fill='both', expand=True, padx=(5, 0))

        # Running Processes/Schedule
        schedule_frame = tk.LabelFrame(right_panel, text="Running Processes / Schedule", 
                                      font=("Arial", 12, "bold"))
        schedule_frame.pack(fill='both', expand=True, pady=(0, 5))

        # Create a frame for schedule with scrollbar
        schedule_container = tk.Frame(schedule_frame)
        schedule_container.pack(fill='both', expand=True, padx=5, pady=5)

        self.schedule_canvas = tk.Canvas(schedule_container, height=200, bg="white")
        
        # Add horizontal scrollbar for long schedules
        schedule_scrollbar = ttk.Scrollbar(schedule_container, orient='horizontal', 
                                         command=self.schedule_canvas.xview)
        self.schedule_canvas.configure(xscrollcommand=schedule_scrollbar.set)
        
        self.schedule_canvas.pack(side='top', fill='both', expand=True)
        schedule_scrollbar.pack(side='bottom', fill='x')

        # Tick controls
        tick_controls = tk.Frame(right_panel)
        tick_controls.pack(fill='x', pady=5)
        
        small_btn_style = {"font": ("Arial", 9, "bold"), "height": 1, "width": 6}
        
        self.prev_tick_btn = tk.Button(tick_controls, text="⏮ Prev", state='disabled', 
                                     command=self.previous_tick, **small_btn_style)
        self.next_tick_btn = tk.Button(tick_controls, text="Next ⏭", state='disabled', 
                                     command=self.next_tick, **small_btn_style)
        
        self.prev_tick_btn.pack(side='left', padx=2)
        self.next_tick_btn.pack(side='left', padx=2)
        
        self.tick_label = tk.Label(tick_controls, text="Tick: 0/0", font=("Arial", 10, "bold"), 
                                 fg="#2c3e50")
        self.tick_label.pack(side='right', padx=5)

        # Status label
        self.status_label = tk.Label(right_panel, text="Ready to run simulation", 
                                   font=("Arial", 10), fg="#666666")
        self.status_label.pack(fill='x', pady=5)

        # ---------- Current settings ----------
        settings = tk.LabelFrame(sim, text="Current Settings", font=("Arial", 10, "bold"))
        settings.pack(fill='x', padx=10, pady=5)

        self.settings_text = tk.Text(settings, height=4, wrap='word', bg='#f8f9fa')
        self.settings_text.pack(fill='x', padx=5, pady=5)

        self.update_settings_display()
        self.toggle_custom_processes()

    
    def setup_results_tab(self):
        # Create the results display tab.
        # Uses tkinter.Frame to create a tab for showing results
        self.results_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.results_tab, text="Simulation Results")
        results_frame = self.results_tab
        
        # Create main container with two sections
        main_container = tk.Frame(results_frame)
        main_container.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Timeline Grid section (new grid-based visualization)
        timeline_grid_frame = tk.LabelFrame(main_container, text="Animation - Simulation Timeline", font=("Arial", 12, "bold"))
        timeline_grid_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create canvas for the timeline grid with scrollbars
        timeline_container = tk.Frame(timeline_grid_frame)
        timeline_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Timeline grid canvas
        self.timeline_grid_canvas = tk.Canvas(timeline_container, bg="white", height=200)
        
        # Add scrollbars for the timeline grid
        timeline_v_scrollbar = ttk.Scrollbar(timeline_container, orient='vertical', command=self.timeline_grid_canvas.yview)
        timeline_h_scrollbar = ttk.Scrollbar(timeline_container, orient='horizontal', command=self.timeline_grid_canvas.xview)
        self.timeline_grid_canvas.configure(yscrollcommand=timeline_v_scrollbar.set, xscrollcommand=timeline_h_scrollbar.set)
        
        # Pack canvas and scrollbars
        self.timeline_grid_canvas.pack(side='left', fill='both', expand=True)
        timeline_v_scrollbar.pack(side='right', fill='y')
        timeline_h_scrollbar.pack(side='bottom', fill='x')
        
        # Timeline text section (smaller portion)
        timeline_text_frame = tk.LabelFrame(main_container, text="Detailed Timeline", font=("Arial", 10, "bold"))
        timeline_text_frame.pack(fill='x', padx=5, pady=5)
        
        # Uses tkinter.ScrolledText for displaying enhanced timeline (GeeksforGeeks: Python Tkinter ScrolledText)
        self.timeline_text = scrolledtext.ScrolledText(timeline_text_frame, height=8, wrap='word', font=("Courier", 9))
        self.timeline_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Results table section (smaller portion)
        results_table_frame = tk.LabelFrame(main_container, text="Process Results Summary", font=("Arial", 10, "bold"))
        results_table_frame.pack(fill='x', padx=5, pady=5)
        
        # Create results table
        columns = ('Process', 'Arrival', 'BT_Now', 'PT_Now', 'PT_Used', 'First Start', 'Completion', 'Turnaround', 'WT_Now', 'Response')
        self.results_tree = ttk.Treeview(results_table_frame, columns=columns, show='headings', height=6)
        
        # Set column headings and widths
        column_widths = {'Process': 60, 'Arrival': 60, 'BT_Now': 60, 'PT_Now': 60, 'PT_Used': 60, 'First Start': 80, 'Completion': 80, 'Turnaround': 80, 'WT_Now': 70, 'Response': 70}
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

        # Enable/disable the number of processes spinbox
        if use_defaults:
            self.count_spinbox.config(state='disabled')
            self.help_label.config(text="Using default processes - editing disabled")

            (q0, q1, q2), demote, aging, file_procs = load_defaults("default_processes.txt")

            self.quantum_q0.set(q0)
            self.quantum_q1.set(q1)
            self.quantum_q2.set(q2)
            self.demote_threshold.set(demote)
            self.aging_threshold.set(aging)

            src = file_procs
            for name, arrival, burst, priority in src[:n]:
                self.process_tree.insert('', 'end', values=(name, arrival, burst, priority, 0))  # PT_Used starts at 0
        else:
            self.count_spinbox.config(state='normal')
            self.help_label.config(text="💡 Double-click on Arrival, BT_Now, PT_Now, or PT_Used to edit values")

        # If we're switching FROM defaults TO custom, seed custom_processes
        # with whatever is currently visible (the default rows).
        if not use_defaults:
            # If we have a loaded file, use those processes
            if self.loaded_file_processes:
                self.custom_processes = list(self.loaded_file_processes)
            else:
                # Otherwise, use currently visible rows
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
                self.process_tree.insert('', 'end', values=(name, arrival, burst, priority, 0))  # PT_Used starts at 0
        else:
            # Use the seeded custom rows, then ensure we have exactly N
            for name, arrival, burst, priority in self.custom_processes:
                self.process_tree.insert('', 'end', values=(name, arrival, burst, priority, 0))  # PT_Used starts at 0
            self._ensure_custom_row_count(n)

        self.update_settings_display()
    
    def upload_process_file(self):
        """Upload and parse a .txt file containing process definitions."""
        # Open file dialog
        file_path = filedialog.askopenfilename(
            title="Select Process File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            # Parse the file
            processes = self.parse_process_file(file_path)
            
            if not processes:
                messagebox.showerror("Invalid File", "No valid processes found in the file.")
                return
            
            # Store the loaded file info
            self.loaded_file_path = file_path
            self.loaded_file_processes = processes
            self._try_read_settings_from_file(file_path)
            
            # Update UI
            filename = os.path.basename(file_path)
            self.file_label.config(text=f"Loaded: {filename} ({len(processes)} processes)")
            self.clear_file_btn.config(state='normal')
            
            # Update the process count to match loaded file
            self.num_processes.set(len(processes))
            
            # Switch to custom mode and populate with loaded processes
            self.use_default_processes.set(False)
            self.toggle_custom_processes()
            
            messagebox.showinfo("File Loaded", f"Successfully loaded {len(processes)} processes from {filename}")
            
        except Exception as e:
            messagebox.showerror("File Error", f"Error loading file: {str(e)}")
    
    def parse_process_file(self, file_path):
        processes = []
        found = {}
        
        with open(file_path, 'r') as file:
            for line_num, line in enumerate(file, 1):
                s = line.strip()
                if not s or s.startswith('#'):
                    continue

                parts = s.split()

                # --- SETTINGS PAIRS (optional) ---
                if len(parts) == 2:
                    key = parts[0].upper()
                    if key in ("Q0", "Q1", "Q2", "DEMOTE", "AGING"):
                        try:
                            found[key] = int(parts[1])
                        except ValueError:
                            raise ValueError(f"Line {line_num}: {key} must be an integer")
                        continue  # don't treat as a process line

                # --- PROCESS ROWS (required format) ---
                if len(parts) == 4:
                    name = parts[0]
                    try:
                        arrival = int(parts[1])
                        burst   = int(parts[2])
                        prio    = int(parts[3])
                    except ValueError:
                        raise ValueError(f"Line {line_num}: invalid process numbers")

                    if arrival < 0:
                        raise ValueError(f"Line {line_num}: Arrival time must be >= 0")
                    if burst < 1:
                        raise ValueError(f"Line {line_num}: Burst time must be >= 1")
                    if prio not in (1, 2, 3):
                        raise ValueError(f"Line {line_num}: Priority must be between 1 and 3")

                    processes.append((name, arrival, burst, prio))
                    continue

                # Anything else is neither a valid setting nor a process
                raise ValueError(
                    f"Line {line_num}: Expected a setting "
                    f"(Q0/Q1/Q2/DEMOTE/AGING <int>) or 4 values (name, arrival, burst, priority)"
                )

        # Apply any optional settings we found (file-first; if missing, keep current GUI values)
        if "Q0" in found:     self.quantum_q0.set(found["Q0"])
        if "Q1" in found:     self.quantum_q1.set(found["Q1"])
        if "Q2" in found:     self.quantum_q2.set(found["Q2"])
        if "DEMOTE" in found: self.demote_threshold.set(found["DEMOTE"])
        if "AGING" in found:  self.aging_threshold.set(found["AGING"])

        # If no process lines were provided, keep current behavior (you can choose to allow empty)
        if not processes:
            raise ValueError("No process rows found in file")

        return processes
    
    def _try_read_settings_from_file(self, path):
        """
        OPTIONAL settings reader: If the file contains lines like
        Q0/Q1/Q2/DEMOTE/AGING, apply them to the GUI.
        If none are present, do nothing (no error).
        """
        if not os.path.exists(path):
            return
        found_any = False
        q0 = q1 = q2 = None
        demote = aging = None

        with open(path, "r") as f:
            for line in f:
                s = line.strip()
                if not s or s.startswith("#"):
                    continue
                parts = s.split()
                if len(parts) != 2:
                    continue
                key, val = parts[0].upper(), parts[1]
                try:
                    ival = int(val)
                except ValueError:
                    continue

                if key == "Q0":      q0 = ival;    found_any = True
                elif key == "Q1":    q1 = ival;    found_any = True
                elif key == "Q2":    q2 = ival;    found_any = True
                elif key == "DEMOTE": demote = ival; found_any = True
                elif key == "AGING":  aging  = ival; found_any = True

        if not found_any:
            return  # optional: nothing to apply

        if q0 is not None:      self.quantum_q0.set(q0)
        if q1 is not None:      self.quantum_q1.set(q1)
        if q2 is not None:      self.quantum_q2.set(q2)
        if demote is not None:  self.demote_threshold.set(demote)
        if aging is not None:   self.aging_threshold.set(aging)

        # also refresh the right-side “Current Settings” text
        self.update_settings_display()
    
    def clear_uploaded_file(self):
        """Clear the uploaded file and return to default processes."""
        self.loaded_file_path = None
        self.loaded_file_processes = []
        
        # Update UI
        self.file_label.config(text="No file loaded")
        self.clear_file_btn.config(state='disabled')
        
        # Return to default processes
        self.use_default_processes.set(True)
        self.toggle_custom_processes()
        
        messagebox.showinfo("File Cleared", "Uploaded file cleared. Using default processes.")
    
    
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

            self.process_tree.insert('', 'end', values=(name, arrival, burst, priority, 0))  # PT_Used starts at 0
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
            messagebox.showinfo("Editing Disabled", "Process editing is disabled when using default processes.\nUncheck 'Use default processes' to enable editing.")
            return

        region = self.process_tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        row_id = self.process_tree.identify_row(event.y)
        col_id = self.process_tree.identify_column(event.x)  # '#1'..'#4'
        if not row_id or not col_id:
            return

        # Column mapping: #1=Name (locked), #2=Arrival, #3=BT_Now, #4=PT_Now, #5=PT_Used
        if col_id == "#1":
            messagebox.showinfo("Name Locked", "Process names are automatically generated (P1, P2, P3...).\nDouble-click on Arrival, BT_Now, PT_Now, or PT_Used columns to edit those values.")
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
        elif idx == 2:      # BT_Now
            if val < 1:
                messagebox.showerror("Invalid BT_Now", "BT_Now must be ≥ 1.")
                return
        elif idx == 3:      # PT_Now
            if val < 1 or val > 3:
                messagebox.showerror("Invalid PT_Now", "PT_Now must be between 1 and 3.")
                return
        elif idx == 4:      # PT_Used
            if val < 0:
                messagebox.showerror("Invalid PT_Used", "PT_Used must be ≥ 0.")
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
                self.process_tree.insert('', 'end', values=(name, arrival, burst, priority, 0))  # PT_Used starts at 0
        else:
            # If custom list is empty (first-time custom), seed from defaults[:n]
            if not self.custom_processes:
                self.custom_processes = list(DEFAULT_PROCESSES[:n])
                # also reflect in the table immediately
                for item in self.process_tree.get_children():
                    self.process_tree.delete(item)
                for name, arrival, burst, priority in self.custom_processes:
                    self.process_tree.insert('', 'end', values=(name, arrival, burst, priority, 0))  # PT_Used starts at 0
            # then enforce exact N in custom mode (adds beyond using remaining defaults if available)
            self._ensure_custom_row_count(n)

        self.update_settings_display()

    
    def update_settings_display(self):
        # Update the settings display in the simulation tab.
        # Uses tkinter Text widget methods to update display (W3Schools: Python Tkinter Text)
        self.settings_text.config(state='normal')
        self.settings_text.delete('1.0', 'end')
        
        # Determine process source
        if self.loaded_file_path:
            filename = os.path.basename(self.loaded_file_path)
            process_source = f"Loaded from file: {filename}"
        elif self.use_default_processes.get():
            process_source = "Using default processes"
        else:
            process_source = "Using custom processes"
        
        settings_info = f"""
        Current Settings:
        • Number of Processes: {self.num_processes.get()}
        • Process Source: {process_source}
        • Time Quantum Q0 (Highest): {self.quantum_q0.get()}
        • Time Quantum Q1 (Medium): {self.quantum_q1.get()}
        • Time Quantum Q2 (Lowest): {self.quantum_q2.get()}
        • Demotion Threshold: {self.demote_threshold.get()}
        • Aging Threshold: {self.aging_threshold.get()}
        • Preemption: {'Yes' if self.preempt.get() else 'No'}
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
            
            # Create scheduler with separate quantums for each queue
            scheduler = SimpleMLFQScheduler(
                quantums=[self.quantum_q0.get(), self.quantum_q1.get(), self.quantum_q2.get()],
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

        # Clear all canvases
        for canvas_name in ['q0_canvas', 'q1_canvas', 'q2_canvas', 'schedule_canvas']:
            if hasattr(self, canvas_name):
                getattr(self, canvas_name).delete('all')

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

        # Update status header
        self.timer_label.config(text=f"Timer: {fr['t']}")
        
        if fr['running']:
            self.current_process_label.config(text=f"Running: {fr['running']['name']}")
            self.execution_time_label.config(text=f"Execution Time: {fr['running']['execution_time']}")
        else:
            self.current_process_label.config(text="Running: None")
            self.execution_time_label.config(text="Execution Time: 0")

        # Update queue displays
        self._draw_queue_canvas(self.q0_canvas, fr['queues'][0], "Q0")
        self._draw_queue_canvas(self.q1_canvas, fr['queues'][1], "Q1")
        self._draw_queue_canvas(self.q2_canvas, fr['queues'][2], "Q2")

        # Update schedule timeline
        self._draw_schedule_timeline(fr)

    def _draw_queue_canvas(self, canvas, processes, queue_title):
        """Draw processes in a queue canvas with their attributes horizontally beside the process name."""
        canvas.delete('all')
        
        if not processes:
            # Draw empty queue message
            canvas.create_text(canvas.winfo_width()//2, canvas.winfo_height()//2, 
                             text="Empty", font=("Arial", 14, "bold"), fill="#999999")
            return
        
        # Calculate layout
        canvas_width = canvas.winfo_width() or 200
        canvas_height = canvas.winfo_height() or 120
        
        # Process box dimensions
        box_width = min(180, canvas_width - 20)
        box_height = 25
        box_spacing = 5
        
        # Draw each process
        for i, process in enumerate(processes[:3]):  # Show max 3 processes
            y_pos = 10 + i * (box_height + box_spacing)
            
            # Process box background
            color = self._color_for(process['name'])
            canvas.create_rectangle(10, y_pos, 10 + box_width, y_pos + box_height, 
                                 fill=color, outline='black', width=1)
            
            # Process name and attributes on the same line
            attr_text = f"{process['name']} BT:{process['burst']} PT:{process['priority']} WT:{process['waiting']} AT:{process['arrival']}"
            canvas.create_text(15, y_pos + box_height//2, text=attr_text, 
                             font=("Arial", 8), anchor='w', fill="white")
        
        # If there are more than 3 processes, show "..."
        if len(processes) > 3:
            canvas.create_text(canvas_width//2, canvas_height - 10, text="...", 
                             font=("Arial", 12), fill="#666666")

    def _draw_schedule_timeline(self, frame):
        """Draw the horizontal timeline of process execution."""
        if not hasattr(self, 'schedule_canvas'):
            return
            
        canvas = self.schedule_canvas
        canvas.delete('all')
        
        # Calculate layout
        canvas_width = canvas.winfo_width() or 400
        canvas_height = canvas.winfo_height() or 200
        
        # Process block dimensions
        block_width = 60
        block_height = 40
        block_spacing = 5
        
        # Draw process blocks horizontally
        x_pos = 10
        y_pos = canvas_height // 2 - block_height // 2
        
        # Get the current running process
        if frame['running']:
            process = frame['running']
            
            # Current running process (highlighted)
            color = self._color_for(process['name'])
            canvas.create_rectangle(x_pos, y_pos, x_pos + block_width, y_pos + block_height,
                                 fill=color, outline='red', width=2)
            
            # Process name
            canvas.create_text(x_pos + block_width//2, y_pos + 10, text=process['name'],
                             font=("Arial", 10, "bold"), fill="white")
            
            # Process attributes
            attr_text = f"BT:{process['burst']} PT:{process['priority']}"
            canvas.create_text(x_pos + block_width//2, y_pos + 25, text=attr_text,
                             font=("Arial", 8), fill="white")
            
            x_pos += block_width + block_spacing
        
        # Draw completed processes from timeline
        if hasattr(self, 'timeline') and self.timeline:
            for start, end, process_name, queue_level in self.timeline:
                if process_name != (frame['running']['name'] if frame['running'] else None):
                    # Completed process block
                    color = self._color_for(process_name)
                    canvas.create_rectangle(x_pos, y_pos, x_pos + block_width, y_pos + block_height,
                                         fill=color, outline='black', width=1)
                    
                    # Process name
                    canvas.create_text(x_pos + block_width//2, y_pos + 10, text=process_name,
                                     font=("Arial", 9), fill="white")
                    
                    # Queue level
                    canvas.create_text(x_pos + block_width//2, y_pos + 25, text=f"Q{queue_level}",
                                     font=("Arial", 8), fill="white")
                    
                    x_pos += block_width + block_spacing
                    
                    # Stop if we run out of space
                    if x_pos + block_width > canvas_width - 10:
                        break
        
        # Update scroll region
        total_width = max(canvas_width, x_pos + 10)
        canvas.configure(scrollregion=(0, 0, total_width, canvas_height))

    def _color_for(self, pid):
        if not pid:    # Idle color
            return self.idle_color
        
        # Use consistent color mapping based on process name
        if pid not in self.color_map:
            try:
                if pid.startswith('P') and pid[1:].isdigit():
                    process_num = int(pid[1:])
                    
                    # Assign colors based on process number ranges
                    if 1 <= process_num <= 3:
                        # P1-P3: Red shades
                        color_index = (process_num - 1) % len(self.red_shades)
                        self.color_map[pid] = self.red_shades[color_index]
                    elif 4 <= process_num <= 5:
                        # P4-P5: Orange shades
                        color_index = (process_num - 4) % len(self.orange_shades)
                        self.color_map[pid] = self.orange_shades[color_index]
                    elif 6 <= process_num <= 7:
                        # P6-P7: Green shades
                        color_index = (process_num - 6) % len(self.green_shades)
                        self.color_map[pid] = self.green_shades[color_index]
                    else:
                        # P8+: Blue to Violet shades
                        color_index = (process_num - 8) % len(self.blue_violet_shades)
                        self.color_map[pid] = self.blue_violet_shades[color_index]
                else:
                    # Fallback for non-standard process names
                    self.color_map[pid] = "#808080"  # Gray
            except:
                # Fallback for any errors
                self.color_map[pid] = "#808080"  # Gray
        
        return self.color_map[pid]

    def _draw_timeline_grid(self):
        """Draw the grid-based timeline visualization showing Q0, Q1, Q2, and CPU rows."""
        if not hasattr(self, 'timeline_grid_canvas') or not self.timeline:
            return
            
        canvas = self.timeline_grid_canvas
        canvas.delete('all')
        
        # Calculate layout
        canvas_width = canvas.winfo_width() or 800
        canvas_height = canvas.winfo_height() or 200
        
        # Grid dimensions
        cell_width = 30
        cell_height = 35
        header_height = 25
        
        # Find the maximum time from timeline
        max_time = max(end for _, end, _, _ in self.timeline) if self.timeline else 0
        
        # Calculate total grid dimensions
        total_width = max(canvas_width, (max_time + 1) * cell_width + 100)
        total_height = header_height + 4 * cell_height + 20  # 4 rows: Q0, Q1, Q2, CPU
        
        # Set scroll region
        canvas.configure(scrollregion=(0, 0, total_width, total_height))
        
        # Draw headers
        headers = ['Q0 (Highest)', 'Q1', 'Q2', 'CPU (Running)']
        for i, header in enumerate(headers):
            y_pos = header_height + i * cell_height
            canvas.create_text(10, y_pos + cell_height//2, text=header, 
                             font=("Arial", 10, "bold"), anchor='w')
        
        # Draw time axis
        for t in range(max_time + 1):
            x_pos = 100 + t * cell_width
            canvas.create_text(x_pos + cell_width//2, header_height//2, text=str(t), 
                             font=("Arial", 9), anchor='center')
        
        # Create a grid to track what's in each cell
        grid_data = {}
        for queue_level in range(3):  # Q0, Q1, Q2
            grid_data[queue_level] = {}
            for t in range(max_time + 1):
                grid_data[queue_level][t] = None
        
        # CPU row
        grid_data['cpu'] = {}
        for t in range(max_time + 1):
            grid_data['cpu'][t] = None
        
        # Fill the grid with timeline data
        for start, end, process_name, queue_level in self.timeline:
            for t in range(start, end):
                if t <= max_time:
                    if queue_level < 3:  # Process in queue
                        grid_data[queue_level][t] = process_name
                    # Also mark CPU execution
                    grid_data['cpu'][t] = process_name
        
        # Draw the grid cells
        for queue_level in range(3):  # Q0, Q1, Q2
            for t in range(max_time + 1):
                x_pos = 100 + t * cell_width
                y_pos = header_height + queue_level * cell_height
                
                process_name = grid_data[queue_level][t]
                if process_name:
                    # Process is in this queue at this time
                    color = self._color_for(process_name)
                    canvas.create_rectangle(x_pos, y_pos, x_pos + cell_width, y_pos + cell_height,
                                         fill=color, outline='black', width=1)
                    canvas.create_text(x_pos + cell_width//2, y_pos + cell_height//2, 
                                     text=process_name, font=("Arial", 9, "bold"), 
                                     fill="white", anchor='center')
                else:
                    # Empty cell
                    canvas.create_rectangle(x_pos, y_pos, x_pos + cell_width, y_pos + cell_height,
                                         fill="#f0f0f0", outline='black', width=1)
                    canvas.create_text(x_pos + cell_width//2, y_pos + cell_height//2, 
                                     text="Idle", font=("Arial", 8), 
                                     fill="#999999", anchor='center')
        
        # Draw CPU row
        for t in range(max_time + 1):
            x_pos = 100 + t * cell_width
            y_pos = header_height + 3 * cell_height  # CPU is the 4th row
            
            process_name = grid_data['cpu'][t]
            if process_name:
                # Process is running on CPU
                color = self._color_for(process_name)
                canvas.create_rectangle(x_pos, y_pos, x_pos + cell_width, y_pos + cell_height,
                                     fill=color, outline='red', width=2)  # Red border for CPU
                canvas.create_text(x_pos + cell_width//2, y_pos + cell_height//2, 
                                 text=process_name, font=("Arial", 9, "bold"), 
                                 fill="white", anchor='center')
            else:
                # CPU is idle
                canvas.create_rectangle(x_pos, y_pos, x_pos + cell_width, y_pos + cell_height,
                                     fill="#f0f0f0", outline='red', width=2)
                canvas.create_text(x_pos + cell_width//2, y_pos + cell_height//2, 
                                 text="Idle", font=("Arial", 8), 
                                 fill="#999999", anchor='center')

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
        
        # Clear and redraw all canvases
        for canvas_name in ['q0_canvas', 'q1_canvas', 'q2_canvas', 'schedule_canvas']:
            if hasattr(self, canvas_name):
                getattr(self, canvas_name).delete('all')
        
        # Draw initial frame if available
        if self.frames:
            self._repaint_animation_frame()
        
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
        
        # Clear and redraw all canvases
        for canvas_name in ['q0_canvas', 'q1_canvas', 'q2_canvas', 'schedule_canvas']:
            if hasattr(self, canvas_name):
                getattr(self, canvas_name).delete('all')
        
        # Draw current frame
        if self.frames:
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

        # Update all displays
        self._repaint_animation_frame()

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
        # This method is no longer needed with the new canvas-based approach
        # The _repaint_animation_frame method handles all the drawing
        pass


    def _populate_results_tab(self):
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


    def _on_animation_finished(self):
        # Called once the last frame is drawn.
        self.status_label.config(text="Animation finished.")
        # now populate and reveal the Results tab
        self._populate_results_tab()
        self.notebook.select(self.results_tab)
        self.play_btn.config(state='normal')



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
