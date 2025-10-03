"""
=============================================================================
MLFQ (Multi-Level Feedback Queue) CPU Scheduler - Graphical User Interface
=============================================================================

This file creates a complete GUI application for simulating CPU scheduling using
the Multi-Level Feedback Queue algorithm. The interface allows users to configure
scheduling parameters, add processes, and visualize the scheduling results.

Author: MLQ_Bautista_DelaCruz_Respecio Team

GUI Framework: tkinter (Python's built-in GUI library)
References:
- W3Schools. (2024). Python tkinter tutorial. https://www.w3schools.com/python/python_tkinter.asp
- W3Schools. (2024). Python GUI programming. https://www.w3schools.com/python/python_gui.asp

=============================================================================
IMPORTS AND DEPENDENCIES
=============================================================================
"""

# Import tkinter for GUI components (W3Schools, 2024, https://www.w3schools.com/python/python_tkinter.asp)
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Import our custom classes for process management and scheduling
from process import DEFAULT_PROCESSES, DEFAULT_QUANTUM, DEFAULT_DEMOTE_THRESHOLD, DEFAULT_AGING_THRESHOLD, load_defaults
from scheduler import SimpleMLFQScheduler
from drawing.queue_canvas import draw_queue_canvas
from drawing.schedule_canvas import draw_schedule_timeline
from drawing.timeline_grid import draw_timeline_grid
from gui_tabs.config_tab import (
    setup_configuration_tab,
    toggle_custom_processes, load_custom_processes, upload_process_file,
    parse_process_file, clear_uploaded_file,
    _next_expected_name, _ensure_custom_row_count,
    _on_tree_double_click, _cancel_cell_edit, _commit_cell_edit,
    on_num_processes_changed, update_settings_display
)
from gui_tabs.simulation_tab import (
    setup_simulation_tab,
    repaint_animation_frame,
    run_simulation, _run_simulation_background
)
from gui_tabs.results_tab import (
    setup_results_tab,
    populate_results_tab,
    _display_results, _show_error
)


"""
MAIN GUI CLASS
"""

class MLFQGUI:
    """
    Main GUI class for the MLFQ CPU Scheduler application.
    
    This class creates and manages the entire graphical user interface, including:
    - Configuration panels for scheduler settings
    - Process input and management
    - Simulation controls and visualization
    - Results display and analysis
    
    The GUI uses tkinter widgets to create an interactive interface that allows
    users to experiment with different scheduling parameters and see real-time
    results of the MLFQ algorithm.
    
    References:
    - W3Schools. (2024). Python classes and objects. https://www.w3schools.com/python/python_classes.asp
    - W3Schools. (2024). Python tkinter widgets. https://www.w3schools.com/python/python_tkinter_widgets.asp
    """
    
    def __init__(self):
        """
        Initialize the MLFQ GUI application.
        
        This constructor method sets up the main window, creates all GUI components,
        and initializes the application state. It's called automatically when you
        create a new MLFQGUI object.
        
        References:
        - W3Schools. (2024). Python __init__ method. https://www.w3schools.com/python/python_classes.asp
        - W3Schools. (2024). tkinter window configuration. https://www.w3schools.com/python/python_tkinter.asp
        """
        # =====================================================================
        # MAIN WINDOW SETUP
        # =====================================================================
        
        # Create the main window (W3Schools, 2024, https://www.w3schools.com/python/python_tkinter.asp)
        self.root = tk.Tk()
        
        # Set window title that appears in the title bar
        self.root.title("MLFQ CPU Scheduler")
        
        # Set initial window size (width x height in pixels)
        self.root.geometry("1000x700")
        
        # Set minimum window size to prevent it from becoming too small
        self.root.minsize(1000, 700)
        
        # Set background color using hexadecimal color code (#f0f0f0 = light gray)
        # (W3Schools, 2024, https://www.w3schools.com/colors/colors_hexadecimal.asp)
        self.root.configure(bg='#f0f0f0')
        
        # Try to maximize the window on startup for better user experience
        # Different operating systems use different methods, so we try both
        try:
            self.root.state('zoomed')  # Works on Windows
        except tk.TclError:
            self.root.attributes('-zoomed', True)  # Alternative method
        
        # =====================================================================
        # GUI VARIABLES AND STATE MANAGEMENT
        # =====================================================================
        # These variables store the current settings and are linked to GUI widgets
        # (W3Schools, 2024, https://www.w3schools.com/python/python_variables.asp)
        # Scheduler Configuration Variables
        # IntVar and BooleanVar are special tkinter variables that automatically
        # update GUI widgets when their values change
        # (W3Schools, 2024, https://www.w3schools.com/python/python_tkinter_variables.asp)
        
        self.num_processes = tk.IntVar(value=len(DEFAULT_PROCESSES))  # Number of processes to simulate
        self.quantum_q0 = tk.IntVar(value=3)  # Time slice for Queue 0 (highest priority)
        self.quantum_q1 = tk.IntVar(value=3)  # Time slice for Queue 1 (medium priority)
        self.quantum_q2 = tk.IntVar(value=3)  # Time slice for Queue 2 (lowest priority)
        self.demote_threshold = tk.IntVar(value=DEFAULT_DEMOTE_THRESHOLD)  # Time before moving to lower priority
        self.aging_threshold = tk.IntVar(value=DEFAULT_AGING_THRESHOLD)    # Time before moving to higher priority
        self.preempt = tk.BooleanVar(value=True)  # Whether higher priority processes can interrupt lower ones
        self.use_default_processes = tk.BooleanVar(value=True)  # Use predefined processes vs custom ones

        # =====================================================================
        # ANIMATION AND VISUALIZATION STATE
        # =====================================================================
        
        # Animation Control Variables
        self.frames = []          # List to store animation frames for step-by-step visualization
        self.frame_i = 0          # Current frame index during animation playback
        self._animating = False   # Flag to track if animation is currently playing
        self.anim_delay_ms = 300  # Animation speed in milliseconds (default corresponds to slider value 5)
        self._anim_after_id = None # ID for scheduled animation updates (used to cancel animations)

        # Color Management for Process Visualization
        # Each process gets a unique color for easy identification in charts and timelines
        # (W3Schools, 2024, https://www.w3schools.com/colors/colors_hexadecimal.asp)
        self.colors = ["#8B0000", "#DC143C", "#FF0000", "#FF4500", "#FF8C00", 
                      "#228B22", "#32CD32", "#0000FF", "#4169E1", "#1E90FF"]
        self.color_map = {}  # Dictionary mapping process names to their assigned colors
        
        # =====================================================================
        # PROCESS DATA STORAGE
        # =====================================================================
        
        # Process Management Lists
        # These lists store different sets of processes that can be used in simulation
        self.custom_processes = []       # User-defined processes from the GUI table
        self.loaded_file_path = None         # Path to the currently loaded process file
        self.loaded_file_processes = []     # Processes loaded from external files
        
        # =====================================================================
        # GUI CREATION AND INITIALIZATION
        # =====================================================================
        
        # Create all the GUI widgets and layout
        # This method builds the entire interface structure
        self.setup_gui()
    
    """
    =============================================================================
    HELPER METHODS FOR GUI CREATION
    =============================================================================
    These methods create commonly used GUI components with consistent styling.
    They help reduce code repetition and maintain a uniform appearance.
    """
    
    def create_label_frame(self, parent, text, **kwargs):
        """
        Create a labeled frame with consistent styling.
        
        A LabelFrame is a container widget that groups related controls together
        with a visible border and title label.
        
        References:
        - W3Schools. (2024). Python tkinter frame. https://www.w3schools.com/python/python_tkinter_frame.asp
        """
        return tk.LabelFrame(parent, text=text, font=("Arial", 10, "bold"), **kwargs)
    
    def create_spinbox(self, parent, var, from_=1, to=20, width=8, **kwargs):
        """
        Create a spinbox with consistent styling.
        
        A Spinbox allows users to select from a range of values by typing or
        using up/down arrows. Perfect for numeric input with defined limits.
        
        References:
        - W3Schools. (2024). Python tkinter widgets. https://www.w3schools.com/python/python_tkinter_widgets.asp
        """
        return tk.Spinbox(parent, from_=from_, to=to, textvariable=var, width=width, **kwargs)
    
    def create_button(self, parent, text, command, **kwargs):
        """
        Create a button with consistent styling.
        
        Buttons are interactive widgets that users can click to trigger actions.
        This method ensures all buttons in the application have the same appearance.
        
        References:
        - W3Schools. (2024). Python tkinter button. https://www.w3schools.com/python/python_tkinter_button.asp
        """
        default_style = {"font": ("Arial", 9), "height": 1}
        default_style.update(kwargs)
        return tk.Button(parent, text=text, command=command, **default_style)
    
    def create_canvas(self, parent, height=180, **kwargs):
        """
        Create a canvas with consistent styling.
        
        A Canvas is a drawing widget used for creating graphics, charts, and
        custom visualizations. We use it for timeline and scheduling displays.
        
        References:
        - W3Schools. (2024). Python tkinter canvas. https://www.w3schools.com/python/python_tkinter_canvas.asp
        """
        return tk.Canvas(parent, height=height, bg="white", **kwargs)
    
    def _bind_mousewheel_to_canvas(self, canvas):
        """Bind mouse wheel scrolling to a canvas for both vertical and horizontal scrolling"""
        def _on_mousewheel(event):
            # Vertical scrolling (default mouse wheel)
            if event.state == 0:  # No modifier keys
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            # Horizontal scrolling (Shift + mouse wheel)
            elif event.state == 1:  # Shift key pressed
                canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")
        
        def _on_mousewheel_linux(event):
            # Linux mouse wheel support
            if event.state == 0:  # No modifier keys - vertical scroll
                if event.num == 4:
                    canvas.yview_scroll(-1, "units")
                elif event.num == 5:
                    canvas.yview_scroll(1, "units")
            elif event.state == 1:  # Shift key - horizontal scroll
                if event.num == 4:
                    canvas.xview_scroll(-1, "units")
                elif event.num == 5:
                    canvas.xview_scroll(1, "units")
        
        # Bind mouse wheel events for different platforms
        canvas.bind("<MouseWheel>", _on_mousewheel)  # Windows/Mac
        canvas.bind("<Button-4>", _on_mousewheel_linux)  # Linux
        canvas.bind("<Button-5>", _on_mousewheel_linux)  # Linux
        
        # Make canvas focusable so it can receive mouse wheel events
        canvas.bind("<Button-1>", lambda e: canvas.focus_set())
    
    def setup_settings_section(self, parent):
        """Setup all settings sections in a concise way"""
        settings = [
            ("Time Quantum per Queue", [
                ("Q0 (Highest):", self.quantum_q0),
                ("Q1 (Medium):", self.quantum_q1),
                ("Q2 (Lowest):", self.quantum_q2)
            ]),
            ("Demotion Threshold", [("Threshold:", self.demote_threshold)]),
            ("Aging Threshold", [("Threshold:", self.aging_threshold)])
        ]
        
        for title, items in settings:
            frame = self.create_label_frame(parent, title)
            frame.pack(fill='x', padx=5, pady=5)
            
            for label_text, var in items:
                item_frame = tk.Frame(frame)
                item_frame.pack(fill='x', padx=5, pady=2)
                tk.Label(item_frame, text=label_text, font=("Arial", 9, "bold")).pack(side='left')
                self.create_spinbox(item_frame, var).pack(side='left', padx=(5, 0))
        
        # Preemption setting
        preempt_frame = self.create_label_frame(parent, "Preemption")
        preempt_frame.pack(fill='x', padx=5, pady=5)
        
        tk.Radiobutton(preempt_frame, text="Yes (Recommended)", variable=self.preempt, value=True).pack(anchor='w', padx=5, pady=2)

        # For No Preemption
        tk.Radiobutton(preempt_frame, text="No", variable=self.preempt, value=False).pack(anchor='w', padx=5, pady=2)
    
    """
    =============================================================================
    MAIN GUI SETUP METHOD
    =============================================================================
    """
    
    def setup_gui(self):
        """
        Create and organize all GUI components.
        
        This method builds the complete user interface by creating tabs, frames,
        widgets, and organizing them into a logical layout. It's called once
        during initialization to set up the entire application interface.
        
        The GUI is organized into tabs:
        1. Configuration - Set scheduler parameters and processes
        2. Simulation - Run and control the scheduling simulation
        3. Results - View detailed results and analysis
        
        References:
        - W3Schools. (2024). Python tkinter layout. https://www.w3schools.com/python/python_tkinter_layout.asp
        - W3Schools. (2024). Python tkinter notebook. https://www.w3schools.com/python/python_tkinter_notebook.asp
        """
        
        # =====================================================================
        # APPLICATION TITLE
        # =====================================================================
        
        # Create main title label at the top of the window
        # Uses pack() geometry manager to position at top with padding
        # (W3Schools, 2024, https://www.w3schools.com/python/python_tkinter_pack.asp)
        tk.Label(self.root, text="MLFQ CPU Scheduler Simulator", 
                font=("Arial", 16, "bold"), bg='#f0f0f0', fg='#2c3e50').pack(pady=10)
        
        # =====================================================================
        # TAB CONTAINER SETUP
        # =====================================================================
        
        # Create notebook widget for organizing content into tabs
        # Notebook allows multiple pages of content in the same space
        # (W3Schools, 2024, https://www.w3schools.com/python/python_tkinter_notebook.asp)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create tabs
        self.setup_configuration_tab()
        self.setup_simulation_tab()
        self.setup_results_tab()
    
    """
    =============================================================================
    TAB SETUP METHODS
    =============================================================================
    These methods create the content for each tab in the application.
    """
    
    def setup_configuration_tab(self):
        return setup_configuration_tab(self)
    
    def setup_simulation_tab(self):
        return setup_simulation_tab(self)

    def setup_results_tab(self):
        return setup_results_tab(self)
    
    def _repaint_animation_frame(self):
        return repaint_animation_frame(self)

    def _draw_queue_canvas(self, canvas, processes):
        return draw_queue_canvas(self, canvas, processes)

    def _draw_schedule_timeline(self, frame):
        return draw_schedule_timeline(self, frame)

    def _draw_timeline_grid(self):
        return draw_timeline_grid(self)

    def _populate_results_tab(self):
        return populate_results_tab(self)
    
    # --- Config functions ---
    def toggle_custom_processes(self):        return toggle_custom_processes(self)
    def load_custom_processes(self):          return load_custom_processes(self)
    def upload_process_file(self):            return upload_process_file(self)
    def parse_process_file(self, file_path):  return parse_process_file(self, file_path)
    def clear_uploaded_file(self):            return clear_uploaded_file(self)

    def _next_expected_name(self):            return _next_expected_name(self)
    def _ensure_custom_row_count(self, n):    return _ensure_custom_row_count(self, n)
    def _on_tree_double_click(self, e):       return _on_tree_double_click(self, e)
    def _cancel_cell_edit(self):              return _cancel_cell_edit(self)
    def _commit_cell_edit(self, row, col):    return _commit_cell_edit(self, row, col)
    def on_num_processes_changed(self):       return on_num_processes_changed(self)
    def update_settings_display(self):        return update_settings_display(self)

    # --- Simulation functions ---
    def repaint_animation_frame(self):        return repaint_animation_frame(self)
    def run_simulation(self):                 return run_simulation(self)
    def _run_simulation_background(self):     return _run_simulation_background(self)

    # --- Results functions ---
    def _display_results(self, t, r, f):      return _display_results(self, t, r, f)
    def _show_error(self, msg):               return _show_error(self, msg)

    
    """
    =============================================================================
    APPLICATION LIFECYCLE METHODS
    =============================================================================
    """
    
    def run(self):
        """
        Start the GUI application and enter the main event loop.
        
        This method starts the tkinter main event loop, which:
        - Displays the GUI window
        - Handles user interactions (clicks, typing, etc.)
        - Keeps the application running until the user closes it
        - Processes all GUI events and updates
        
        References:
        - W3Schools. (2024). Python tkinter mainloop. https://www.w3schools.com/python/python_tkinter_mainloop.asp
        """
        self.root.mainloop()

    
    def _color_for(self, pid):
        """Simplified color mapping"""
        if not pid:
            return "#808080"  # Gray for idle
        
        if pid not in self.color_map:
            try:
                if pid.startswith('P') and pid[1:].isdigit():
                    process_num = int(pid[1:])
                    color_index = (process_num - 1) % len(self.colors)
                    self.color_map[pid] = self.colors[color_index]
                else:
                    self.color_map[pid] = "#808080"  # Gray fallback
            except:
                self.color_map[pid] = "#808080"  # Gray fallback
        
        return self.color_map[pid]

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
        if getattr(self, '_anim_after_id', None):
            self.root.after_cancel(self._anim_after_id)
            self._anim_after_id = None
        self.play_btn.config(state='normal')
        self.pause_btn.config(state='disabled')

        # Manual control buttons
        self.prev_tick_btn.config(state=('normal' if self.frame_i > 0 else 'disabled'))
        self.next_tick_btn.config(state=('normal' if self.frame_i < self.anim_total - 1 else 'disabled'))

    def reset_animation(self):
        # Reset animation to the beginning.
        self._clear_previous_run_outputs()
        self._animating = False
        if self._anim_after_id is not None:
            self.root.after_cancel(self._anim_after_id)
            self._anim_after_id = None
        
        self.frame_i = 0
        
        # Clear and redraw all canvases
        for canvas in self.queue_canvases:
            canvas.delete('all')
        self.schedule_canvas.delete('all')
        
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
        if self._animating:
            self._anim_after_id = self.root.after(self.anim_delay_ms, self._animate_step)


    def _animate_step(self):
        if not self._animating:
            return

        if self.frame_i >= self.anim_total - 1:
            self._repaint_animation_frame()
            self._animating = False
            
            if self._anim_after_id is not None:
                self.root.after_cancel(self._anim_after_id)
                self._anim_after_id = None
            self._on_animation_finished()
            return
        self._repaint_animation_frame()
        self.frame_i += 1
        self._schedule_next_tick()

    def _fill_queue_listboxes(self, fr):
        # This method is no longer needed with the new canvas-based approach
        # The _repaint_animation_frame method handles all the drawing
        pass

    def _on_animation_finished(self):
        # Called once the last frame is drawn.
        self.status_label.config(text="Animation finished.")
        # now populate and reveal the Results tab
        self._populate_results_tab()
        self.notebook.select(self.results_tab)
        self.play_btn.config(state='normal')

    def _clear_previous_run_outputs(self):
        # stop any in-flight animation
        self._animating = False
        if getattr(self, "_anim_after_id", None):
            self.root.after_cancel(self._anim_after_id)
            self._anim_after_id = None

        # forget old data
        self.frames = []
        self.timeline = []
        self.results = []
        self.frame_i = 0
        self.anim_total = 0
        self.color_map.clear()  # optional: new colors each run

        # clear canvases
        for c in getattr(self, "queue_canvases", []):
            c.delete("all")
        if hasattr(self, "schedule_canvas"):
            self.schedule_canvas.delete("all")
        if hasattr(self, "timeline_grid_canvas"):
            self.timeline_grid_canvas.delete("all")

        # clear text widgets/tables
        if hasattr(self, "timeline_text"):
            self.timeline_text.delete("1.0", "end")
        if hasattr(self, "summary_text"):
            self.summary_text.delete("1.0", "end")
        if hasattr(self, "results_tree"):
            for iid in self.results_tree.get_children():
                self.results_tree.delete(iid)

        # reset status labels
        if hasattr(self, "timer_label"):
            self.timer_label.config(text="Timer: 0")
        if hasattr(self, "current_process_label"):
            self.current_process_label.config(text="Running: None")
        if hasattr(self, "execution_time_label"):
            self.execution_time_label.config(text="Execution Time: 0")
        if hasattr(self, "tick_label"):
            self.tick_label.config(text="Tick: 0/0")

        # reset buttons
        if hasattr(self, "play_btn"):
            self.play_btn.config(state="normal")
        if hasattr(self, "pause_btn"):
            self.pause_btn.config(state="disabled")
        if hasattr(self, "reset_btn"):
            self.reset_btn.config(state="disabled")
        if hasattr(self, "prev_tick_btn"):
            self.prev_tick_btn.config(state="disabled")
        if hasattr(self, "next_tick_btn"):
            self.next_tick_btn.config(state="disabled")

        if hasattr(self, "status_label"):
            self.status_label.config(text="Ready to run simulation")




"""
=============================================================================
APPLICATION ENTRY POINT
=============================================================================
"""

def main():
    """
    Main function to start the MLFQ GUI application.
    
    This function creates an instance of the MLFQGUI class and starts the
    application. It includes error handling to gracefully manage any startup
    issues and display helpful error messages to the user.
    
    References:
    - W3Schools. (2024). Python try except. https://www.w3schools.com/python/python_try_except.asp
    """
    try:
        # Create and run the GUI application
        app = MLFQGUI()
        app.run()
    except Exception as e:
        # If there's an error during startup, show an error message
        # (W3Schools, 2024, https://www.w3schools.com/python/python_tkinter_messagebox.asp)
        root = tk.Tk()
        root.withdraw()  # Hide the empty window
        messagebox.showerror("Startup Error", f"Failed to start the application: {e}")
        root.destroy()

# This block runs only when the script is executed directly (not imported)
# (W3Schools, 2024, https://www.w3schools.com/python/python_modules.asp)
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # Graceful exit if Ctrl+C is pressed in the console
        pass
