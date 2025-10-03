import tkinter as tk
from tkinter import ttk

def setup_simulation_tab(self):
        """
        Create the Simulation tab interface.
        
        This tab provides:
        - Run simulation button and controls
        - Real-time visualization of the scheduling process
        - Interactive timeline showing process execution
        - Animation controls for step-by-step viewing
        
        References:
        - W3Schools. (2024). Python tkinter canvas. https://www.w3schools.com/python/python_tkinter_canvas.asp
        """
        self.simulation_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.simulation_tab, text="Simulation")
        
        # Status header
        status_header = tk.Frame(self.simulation_tab, bg='#2c3e50', height=60)
        status_header.pack(fill='x', padx=10, pady=(10, 5))
        status_header.pack_propagate(False)
        
        # Timer info
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

        # Controls
        controls_frame = tk.Frame(status_header, bg='#2c3e50')
        controls_frame.pack(side='right', fill='y', padx=10, pady=5)
        
        self.play_btn = self.create_button(controls_frame, "▶ Play", self.on_play_clicked, 
                                         bg="#27ae60", fg="white", width=8)
        self.pause_btn = self.create_button(controls_frame, "⏸ Pause", self.pause_animation, 
                                          state='disabled', width=8)
        self.reset_btn = self.create_button(controls_frame, "⟲ Reset", self.reset_animation, 
                                           state='disabled', width=8)
        
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

        # Main content area
        main_content = tk.Frame(self.simulation_tab)
        main_content.pack(fill='both', expand=True, padx=10, pady=5)

        # Left side - Queues
        left_panel = tk.Frame(main_content)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 5))

        # Create queue canvases
        queue_titles = ["Q0", "Q1", "Q2"]
        self.queue_canvases = []
        for i, title in enumerate(queue_titles):
            q_frame = tk.LabelFrame(left_panel, text=title, font=("Arial", 12, "bold"))
            q_frame.pack(fill='both', expand=True, pady=(0, 5))
            
            canvas = self.create_canvas(q_frame)
            canvas.pack(fill='both', expand=True, padx=5, pady=5)
            self.queue_canvases.append(canvas)

        # Right side - Schedule
        right_panel = tk.Frame(main_content)
        right_panel.pack(side='right', fill='both', expand=True, padx=(5, 0))

        schedule_frame = tk.LabelFrame(right_panel, text="Running Processes / Schedule", 
                                      font=("Arial", 12, "bold"))
        schedule_frame.pack(fill='both', expand=True, pady=(0, 5))

        schedule_container = tk.Frame(schedule_frame)
        schedule_container.pack(fill='both', expand=True, padx=5, pady=5)

        self.schedule_canvas = self.create_canvas(schedule_container, height=250)
        
        schedule_scrollbar = ttk.Scrollbar(schedule_container, orient='horizontal', 
                                         command=self.schedule_canvas.xview)
        self.schedule_canvas.configure(xscrollcommand=schedule_scrollbar.set)
        
        self.schedule_canvas.pack(side='top', fill='both', expand=True)
        schedule_scrollbar.pack(side='bottom', fill='x')
        
        # Add mouse wheel scrolling support for schedule canvas
        self._bind_mousewheel_to_canvas(self.schedule_canvas)

        # Tick controls
        tick_controls = tk.Frame(right_panel)
        tick_controls.pack(fill='x', pady=5)
        
        self.prev_tick_btn = self.create_button(tick_controls, "⏮ Prev", self.previous_tick, 
                                              state='disabled', width=6)
        self.next_tick_btn = self.create_button(tick_controls, "Next ⏭", self.next_tick, 
                                              state='disabled', width=6)
        
        self.prev_tick_btn.pack(side='left', padx=2)
        self.next_tick_btn.pack(side='left', padx=2)
        
        self.tick_label = tk.Label(tick_controls, text="Tick: 0/0", font=("Arial", 10, "bold"), 
                                 fg="#2c3e50")
        self.tick_label.pack(side='right', padx=5)

        # Status label
        self.status_label = tk.Label(right_panel, text="Ready to run simulation", 
                                   font=("Arial", 10), fg="#666666")
        self.status_label.pack(fill='x', pady=5)

        # Current settings
        settings = tk.LabelFrame(self.simulation_tab, text="Current Settings", font=("Arial", 10, "bold"))
        settings.pack(fill='x', padx=10, pady=5)

        self.settings_text = tk.Text(settings, height=4, wrap='word', bg='#f8f9fa')
        self.settings_text.pack(fill='x', padx=5, pady=5)

        self.update_settings_display()
        self.toggle_custom_processes()

def repaint_animation_frame(self):
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
        for i, canvas in enumerate(self.queue_canvases):
            self._draw_queue_canvas(canvas, fr['queues'][i])

        # Update schedule timeline
        self._draw_schedule_timeline(fr)

        self.tick_label.config(text=f"Tick: {self.frame_i+1}/{self.anim_total}")

