# Simple GUI for MLFQ Scheduler - Beginner Version
# This creates a user-friendly graphical interface using tkinter

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from simple_process import Process, DEFAULT_PROCESSES, DEFAULT_QUANTUM, DEFAULT_DEMOTE_THRESHOLD, DEFAULT_AGING_THRESHOLD
from simple_scheduler import SimpleMLFQScheduler

class MLFQGUI:
    """
    A simple graphical user interface for the MLFQ scheduler.
    This makes it easy for beginners to use without typing commands.
    """
    
    def __init__(self):
        # Uses tkinter.Tk() to create the main window (W3Schools: Python GUI with Tkinter)
        # This is the main window that holds all the GUI elements
        self.root = tk.Tk()
        self.root.title("MLFQ CPU Scheduler - Beginner Version")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Uses variables to store user input (GeeksforGeeks: Python Tkinter Variables)
        # These automatically update the GUI when changed
        self.num_processes = tk.IntVar(value=len(DEFAULT_PROCESSES))
        self.quantum = tk.IntVar(value=DEFAULT_QUANTUM)
        self.demote_threshold = tk.IntVar(value=DEFAULT_DEMOTE_THRESHOLD)
        self.aging_threshold = tk.IntVar(value=DEFAULT_AGING_THRESHOLD)
        self.preempt = tk.BooleanVar(value=True)
        self.use_default_processes = tk.BooleanVar(value=True)
        
        # Uses list to store custom processes created by user
        self.custom_processes = []
        
        self.setup_gui()
    
    def setup_gui(self):
        """Create and arrange all the GUI elements."""
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
        self.setup_processes_tab()
        self.setup_settings_tab()
        self.setup_simulation_tab()
        self.setup_results_tab()
    
    def setup_processes_tab(self):
        """Create the processes configuration tab."""
        # Uses tkinter.Frame to create a tab for process setup
        processes_frame = ttk.Frame(self.notebook)
        self.notebook.add(processes_frame, text="Processes")
        
        # Process count section
        count_frame = tk.LabelFrame(processes_frame, text="Number of Processes", font=("Arial", 10, "bold"))
        count_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(count_frame, text="How many processes?").pack(side='left', padx=5)
        # Uses tkinter.Spinbox for number input (W3Schools: Python Tkinter Spinbox)
        count_spinbox = tk.Spinbox(count_frame, from_=1, to=20, textvariable=self.num_processes, width=10)
        count_spinbox.pack(side='left', padx=5)
        
        # Default processes option
        default_frame = tk.LabelFrame(processes_frame, text="Process Options", font=("Arial", 10, "bold"))
        default_frame.pack(fill='x', padx=10, pady=5)
        
        # Uses tkinter.Checkbutton for yes/no options (W3Schools: Python Tkinter Checkbutton)
        default_check = tk.Checkbutton(
            default_frame, 
            text="Use default processes (recommended for beginners)",
            variable=self.use_default_processes,
            command=self.toggle_custom_processes
        )
        default_check.pack(anchor='w', padx=5, pady=2)
        
        # Custom processes section
        self.custom_frame = tk.LabelFrame(processes_frame, text="Custom Processes", font=("Arial", 10, "bold"))
        self.custom_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
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
        
        # Uses tkinter.Scrollbar for scrolling (W3Schools: Python Tkinter Scrollbar)
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.process_tree.yview)
        self.process_tree.configure(yscrollcommand=scrollbar.set)
        
        self.process_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Add process form
        form_frame = tk.Frame(self.custom_frame)
        form_frame.pack(fill='x', padx=5, pady=5)
        
        tk.Label(form_frame, text="Name:").grid(row=0, column=0, sticky='e', padx=5)
        self.name_entry = tk.Entry(form_frame, width=10)
        self.name_entry.grid(row=0, column=1, padx=5)
        
        tk.Label(form_frame, text="Arrival:").grid(row=0, column=2, sticky='e', padx=5)
        self.arrival_entry = tk.Entry(form_frame, width=10)
        self.arrival_entry.grid(row=0, column=3, padx=5)
        
        tk.Label(form_frame, text="Burst:").grid(row=0, column=4, sticky='e', padx=5)
        self.burst_entry = tk.Entry(form_frame, width=10)
        self.burst_entry.grid(row=0, column=5, padx=5)
        
        tk.Label(form_frame, text="Priority:").grid(row=0, column=6, sticky='e', padx=5)
        self.priority_entry = tk.Entry(form_frame, width=10)
        self.priority_entry.grid(row=0, column=7, padx=5)
        
        # Uses tkinter.Button for actions (W3Schools: Python Tkinter Button)
        add_button = tk.Button(form_frame, text="Add Process", command=self.add_process)
        add_button.grid(row=0, column=8, padx=5)
        
        clear_button = tk.Button(form_frame, text="Clear All", command=self.clear_processes)
        clear_button.grid(row=0, column=9, padx=5)
        
        # Load default processes
        self.load_default_processes()
        
        # Initially hide custom frame
        self.toggle_custom_processes()
    
    def setup_settings_tab(self):
        """Create the scheduler settings tab."""
        # Uses tkinter.Frame to create a tab for scheduler settings
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="Settings")
        
        # Quantum setting
        quantum_frame = tk.LabelFrame(settings_frame, text="Time Quantum", font=("Arial", 10, "bold"))
        quantum_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(quantum_frame, text="How much time should each process get before switching?").pack(anchor='w', padx=5, pady=2)
        tk.Label(quantum_frame, text="(Like giving each person 5 minutes to speak)").pack(anchor='w', padx=20, pady=2)
        
        quantum_spinbox = tk.Spinbox(quantum_frame, from_=1, to=20, textvariable=self.quantum, width=10)
        quantum_spinbox.pack(anchor='w', padx=5, pady=2)
        
        # Demotion threshold
        demote_frame = tk.LabelFrame(settings_frame, text="Demotion Threshold", font=("Arial", 10, "bold"))
        demote_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(demote_frame, text="How long should a process run before moving to lower priority?").pack(anchor='w', padx=5, pady=2)
        tk.Label(demote_frame, text="(If a process runs too long, it gets moved to a less important queue)").pack(anchor='w', padx=20, pady=2)
        
        demote_spinbox = tk.Spinbox(demote_frame, from_=1, to=50, textvariable=self.demote_threshold, width=10)
        demote_spinbox.pack(anchor='w', padx=5, pady=2)
        
        # Aging threshold
        aging_frame = tk.LabelFrame(settings_frame, text="Aging Threshold", font=("Arial", 10, "bold"))
        aging_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(aging_frame, text="How long should a process wait before moving to higher priority?").pack(anchor='w', padx=5, pady=2)
        tk.Label(aging_frame, text="(If a process waits too long, it gets moved to a more important queue)").pack(anchor='w', padx=20, pady=2)
        
        aging_spinbox = tk.Spinbox(aging_frame, from_=0, to=50, textvariable=self.aging_threshold, width=10)
        aging_spinbox.pack(anchor='w', padx=5, pady=2)
        
        # Preemption setting
        preempt_frame = tk.LabelFrame(settings_frame, text="Preemption", font=("Arial", 10, "bold"))
        preempt_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(preempt_frame, text="Should running processes be interrupted when higher priority ones arrive?").pack(anchor='w', padx=5, pady=2)
        tk.Label(preempt_frame, text="(Like stopping a low-priority customer when a VIP arrives)").pack(anchor='w', padx=20, pady=2)
        
        # Uses tkinter.Radiobutton for single choice options (W3Schools: Python Tkinter Radiobutton)
        preempt_yes = tk.Radiobutton(preempt_frame, text="Yes (Recommended)", variable=self.preempt, value=True)
        preempt_yes.pack(anchor='w', padx=5, pady=2)
        
        preempt_no = tk.Radiobutton(preempt_frame, text="No", variable=self.preempt, value=False)
        preempt_no.pack(anchor='w', padx=5, pady=2)
        
        # Help section
        help_frame = tk.LabelFrame(settings_frame, text="Help", font=("Arial", 10, "bold"))
        help_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
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
        """Create the simulation control tab."""
        # Uses tkinter.Frame to create a tab for running simulations
        sim_frame = ttk.Frame(self.notebook)
        self.notebook.add(sim_frame, text="Simulation")
        
        # Run simulation section
        run_frame = tk.LabelFrame(sim_frame, text="Run Simulation", font=("Arial", 12, "bold"))
        run_frame.pack(fill='x', padx=10, pady=10)
        
        # Uses tkinter.Button for starting the simulation
        self.run_button = tk.Button(
            run_frame, 
            text="🚀 Start Simulation", 
            command=self.run_simulation,
            font=("Arial", 12, "bold"),
            bg='#27ae60',
            fg='white',
            height=2
        )
        self.run_button.pack(pady=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(run_frame, mode='indeterminate')
        self.progress.pack(fill='x', padx=20, pady=5)
        
        # Status label
        self.status_label = tk.Label(run_frame, text="Ready to run simulation", font=("Arial", 10))
        self.status_label.pack(pady=5)
        
        # Current settings display
        settings_display = tk.LabelFrame(sim_frame, text="Current Settings", font=("Arial", 10, "bold"))
        settings_display.pack(fill='x', padx=10, pady=5)
        
        self.settings_text = tk.Text(settings_display, height=6, wrap='word', bg='#f8f9fa')
        self.settings_text.pack(fill='x', padx=5, pady=5)
        
        # Update settings display
        self.update_settings_display()
    
    def setup_results_tab(self):
        """Create the results display tab."""
        # Uses tkinter.Frame to create a tab for showing results
        results_frame = ttk.Frame(self.notebook)
        self.notebook.add(results_frame, text="Results")
        
        # Timeline section
        timeline_frame = tk.LabelFrame(results_frame, text="Execution Timeline", font=("Arial", 10, "bold"))
        timeline_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Uses tkinter.ScrolledText for displaying timeline (GeeksforGeeks: Python Tkinter ScrolledText)
        self.timeline_text = scrolledtext.ScrolledText(timeline_frame, height=8, wrap='word', font=("Courier", 9))
        self.timeline_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Results table section
        results_table_frame = tk.LabelFrame(results_frame, text="Process Results", font=("Arial", 10, "bold"))
        results_table_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
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
        """Show or hide the custom processes section based on checkbox."""
        # Uses tkinter widget methods to show/hide sections (GeeksforGeeks: Python Tkinter Widget Methods)
        if self.use_default_processes.get():
            self.custom_frame.pack_forget()  # Hide custom frame
        else:
            self.custom_frame.pack(fill='both', expand=True, padx=10, pady=5)  # Show custom frame
    
    def load_default_processes(self):
        """Load the default processes into the custom processes list."""
        # Uses list operations to clear and populate the process list (W3Schools: Python List Methods)
        self.custom_processes.clear()
        for item in self.process_tree.get_children():
            self.process_tree.delete(item)
        
        for name, arrival, burst, priority in DEFAULT_PROCESSES:
            self.custom_processes.append((name, arrival, burst, priority))
            self.process_tree.insert('', 'end', values=(name, arrival, burst, priority))
    
    def add_process(self):
        """Add a new process to the custom processes list."""
        try:
            # Uses tkinter Entry widgets to get user input (W3Schools: Python Tkinter Entry)
            name = self.name_entry.get().strip()
            arrival = int(self.arrival_entry.get())
            burst = int(self.burst_entry.get())
            priority = int(self.priority_entry.get())
            
            # Validate input
            if not name:
                # Uses tkinter.messagebox for error messages (W3Schools: Python Tkinter Messagebox)
                messagebox.showerror("Error", "Process name cannot be empty!")
                return
            
            if arrival < 0:
                messagebox.showerror("Error", "Arrival time cannot be negative!")
                return
            
            if burst < 1:
                messagebox.showerror("Error", "Burst time must be at least 1!")
                return
            
            if priority < 1 or priority > 3:
                messagebox.showerror("Error", "Priority must be between 1 and 3!")
                return
            
            # Add to list
            self.custom_processes.append((name, arrival, burst, priority))
            self.process_tree.insert('', 'end', values=(name, arrival, burst, priority))
            
            # Clear form
            self.name_entry.delete(0, 'end')
            self.arrival_entry.delete(0, 'end')
            self.burst_entry.delete(0, 'end')
            self.priority_entry.delete(0, 'end')
            
            messagebox.showinfo("Success", f"Process {name} added successfully!")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for arrival, burst, and priority!")
    
    def clear_processes(self):
        """Clear all custom processes."""
        # Uses tkinter.messagebox.askyesno for confirmation (W3Schools: Python Tkinter Messagebox)
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all processes?"):
            self.custom_processes.clear()
            for item in self.process_tree.get_children():
                self.process_tree.delete(item)
            messagebox.showinfo("Success", "All processes cleared!")
    
    def update_settings_display(self):
        """Update the settings display in the simulation tab."""
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
        """Run the MLFQ simulation in a separate thread."""
        # Uses threading to prevent GUI freezing (GeeksforGeeks: Python Threading)
        self.run_button.config(state='disabled')
        self.progress.start()
        self.status_label.config(text="Running simulation...")
        
        # Uses threading.Thread to run simulation in background (W3Schools: Python Threading)
        simulation_thread = threading.Thread(target=self._run_simulation_background)
        simulation_thread.daemon = True
        simulation_thread.start()
    
    def _run_simulation_background(self):
        """Run the actual simulation in the background thread."""
        try:
            # Get processes to use
            if self.use_default_processes.get():
                # Uses slicing to get the right number of default processes (GeeksforGeeks: Python List Slicing)
                processes = DEFAULT_PROCESSES[:self.num_processes.get()]
            else:
                processes = self.custom_processes[:self.num_processes.get()]
            
            # Create scheduler
            scheduler = SimpleMLFQScheduler(
                quantum=self.quantum.get(),
                demote_threshold=self.demote_threshold.get(),
                aging_threshold=self.aging_threshold.get(),
                preempt=self.preempt.get()
            )
            
            # Run simulation
            timeline, results = scheduler.simulate(processes)
            
            # Update GUI in main thread
            # Uses tkinter.after to update GUI from background thread (GeeksforGeeks: Python Tkinter Threading)
            self.root.after(0, self._display_results, timeline, results)
            
        except Exception as e:
            # Uses tkinter.after to show error in main thread
            self.root.after(0, self._show_error, str(e))
    
    def _display_results(self, timeline, results):
        """Display the simulation results in the GUI."""
        # Update status
        self.status_label.config(text="Simulation completed successfully!")
        self.progress.stop()
        self.run_button.config(state='normal')
        
        # Switch to results tab
        self.notebook.select(3)  # Results tab is index 3
        
        # Display timeline
        self.timeline_text.delete('1.0', 'end')
        timeline_text = "Execution Timeline:\n"
        timeline_text += "This shows when each process ran and in which queue:\n\n"
        
        if timeline:
            timeline_str = " | ".join([f"{start}-{end}:{name}@Q{queue}" 
                                      for start, end, name, queue in timeline])
            timeline_text += timeline_str
        else:
            timeline_text += "No processes were executed."
        
        self.timeline_text.insert('1.0', timeline_text)
        
        # Clear and populate results table
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        for result in results:
            self.results_tree.insert('', 'end', values=(
                result['name'],
                result['arrival'],
                result['burst'],
                result['priority'],
                result['first_start'] if result['first_start'] is not None else "N/A",
                result['completion'] if result['completion'] is not None else "N/A",
                result['turnaround'] if result['turnaround'] is not None else "N/A",
                result['waiting'],
                result['response'] if result['response'] is not None else "N/A"
            ))
        
        # Display summary
        self.summary_text.delete('1.0', 'end')
        
        # Calculate summary statistics
        completed_processes = [r for r in results if r['completion'] is not None]
        
        if completed_processes:
            avg_waiting = sum(r['waiting'] for r in completed_processes) / len(completed_processes)
            avg_turnaround = sum(r['turnaround'] for r in completed_processes) / len(completed_processes)
            avg_response = sum(r['response'] for r in completed_processes if r['response'] is not None) / len(completed_processes)
            
            total_burst_time = sum(r['burst'] for r in completed_processes)
            makespan = max(r['completion'] for r in completed_processes) - min(r['arrival'] for r in completed_processes)
            cpu_utilization = (total_burst_time / makespan) * 100 if makespan > 0 else 100.0
            
            summary_text = f"""
            Summary Statistics:
            • Average Waiting Time: {avg_waiting:.2f}
            • Average Turnaround Time: {avg_turnaround:.2f}
            • Average Response Time: {avg_response:.2f}
            • CPU Utilization: {cpu_utilization:.2f}%
            • Total Processes: {len(completed_processes)}
            • Total Simulation Time: {makespan}
            """
        else:
            summary_text = "No processes completed."
        
        self.summary_text.insert('1.0', summary_text)
        
        # Update settings display
        self.update_settings_display()
    
    def _show_error(self, error_message):
        """Show an error message to the user."""
        self.progress.stop()
        self.run_button.config(state='normal')
        self.status_label.config(text="Simulation failed!")
        messagebox.showerror("Simulation Error", f"An error occurred: {error_message}")
    
    def run(self):
        """Start the GUI application."""
        # Uses tkinter.mainloop to start the GUI (W3Schools: Python Tkinter Mainloop)
        # This makes the window appear and handles user interactions
        self.root.mainloop()

def main():
    """Main function to start the GUI application."""
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
    main()
