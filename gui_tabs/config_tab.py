import tkinter as tk
from tkinter import ttk
from tkinter import ttk, messagebox, filedialog
from process import DEFAULT_PROCESSES, load_defaults
# Import os for file operations (W3Schools, 2024, https://www.w3schools.com/python/python_file_handling.asp)
import os

def setup_configuration_tab(self):
    """
    Create the Configuration tab interface.
    
    This tab allows users to:
    - Set scheduler parameters (quantum times, thresholds)
    - Choose between default or custom processes
    - Edit process details in a table format
    - Load processes from external files
    
    References:
    - W3Schools. (2024). Python tkinter treeview. https://www.w3schools.com/python/python_tkinter_treeview.asp
    """
    config_frame = ttk.Frame(self.notebook)
    self.notebook.add(config_frame, text="Configuration")
    
    # Two-column layout
    main_container = tk.Frame(config_frame)
    main_container.pack(fill='both', expand=True, padx=10, pady=5)
    
    left_column = tk.Frame(main_container)
    left_column.pack(side='left', fill='both', expand=True, padx=(0, 5))
    
    right_column = tk.Frame(main_container)
    right_column.pack(side='right', fill='both', expand=True, padx=(5, 0))
    
    # Process count section
    count_frame = self.create_label_frame(left_column, "Number of Processes")
    count_frame.pack(fill='x', padx=5, pady=5)
    
    tk.Label(count_frame, text="How many processes?").pack(side='left', padx=5)
    self.count_spinbox = self.create_spinbox(count_frame, self.num_processes, width=10)
    self.count_spinbox.pack(side='left', padx=5)
    self.num_processes.trace_add('write', lambda *args: self.on_num_processes_changed())
    
    # Process options
    default_frame = self.create_label_frame(left_column, "Process Options")
    default_frame.pack(fill='x', padx=5, pady=5)
    
    tk.Checkbutton(default_frame, text="Use default processes", 
                    variable=self.use_default_processes, command=self.toggle_custom_processes).pack(anchor='w', padx=5, pady=2)
    
    # File upload
    file_frame = tk.Frame(default_frame)
    file_frame.pack(fill='x', padx=5, pady=5)
    tk.Label(file_frame, text="Or upload .txt file:", font=("Arial", 9)).pack(anchor='w')
    
    file_btn_frame = tk.Frame(file_frame)
    file_btn_frame.pack(fill='x', pady=2)
    
    self.upload_btn = self.create_button(file_btn_frame, "📁 Upload", self.upload_process_file, bg="#3498db", fg="white")
    self.upload_btn.pack(side='left', padx=(0, 5))
    
    self.file_label = tk.Label(file_btn_frame, text="No file loaded", font=("Arial", 8), fg="#666666")
    self.file_label.pack(side='left')
    
    self.clear_file_btn = self.create_button(file_btn_frame, "✖ Clear", self.clear_uploaded_file, state='disabled')
    self.clear_file_btn.pack(side='left', padx=(5, 0))
    
    # Custom processes section
    self.custom_frame = self.create_label_frame(left_column, "Custom Processes")
    self.custom_frame.pack(fill='both', expand=True, padx=5, pady=5)
    
    self.help_label = tk.Label(self.custom_frame, text="💡 Double-click to edit values", 
                                font=("Arial", 9), fg="#666666")
    self.help_label.pack(anchor='w', padx=5, pady=(5, 0))
    
    # Process tree
    list_frame = tk.Frame(self.custom_frame)
    list_frame.pack(fill='both', expand=True, padx=5, pady=5)
    
    columns = ('Name', 'Arrival', 'Burst', 'Priority')
    self.process_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
    
    for col in columns:
        self.process_tree.heading(col, text=col)
        self.process_tree.column(col, width=100)

    self.process_tree.bind("<Double-1>", self._on_tree_double_click)
    
    scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.process_tree.yview)
    self.process_tree.configure(yscrollcommand=scrollbar.set)
    
    self.process_tree.pack(side='left', fill='both', expand=True)
    scrollbar.pack(side='right', fill='y')
    
    # Load custom processes button
    button_frame = tk.Frame(self.custom_frame)
    button_frame.pack(fill='x', padx=5, pady=5)
    
    self.load_custom_btn = self.create_button(button_frame, "Load Custom Processes", 
                                            self.load_custom_processes, 
                                            bg="#27ae60", fg="white", width=20)
    self.load_custom_btn.pack(side='left', padx=5)
    
    self.custom_status_label = tk.Label(button_frame, text="", font=("Arial", 9), fg="#666666")
    self.custom_status_label.pack(side='left', padx=10)
    
    # Settings sections
    self.setup_settings_section(right_column)

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
        self.load_custom_btn.config(state='disabled')
        self.custom_status_label.config(text="")

        (q0, q1, q2, q3), demote, aging, file_procs = load_defaults("default_processes.txt")

        self.quantum_q0.set(q0)
        self.quantum_q1.set(q1)
        self.quantum_q2.set(q2)
        self.quantum_q3.set(q3)
        self.demote_threshold.set(demote)
        self.aging_threshold.set(aging)

        src = file_procs
        for name, arrival, burst, priority in src[:n]:
            self.process_tree.insert('', 'end', values=(name, arrival, burst, priority, 0))  # PT_Used starts at 0
    else:
        self.count_spinbox.config(state='normal')
        self.help_label.config(text="💡 Double-click on Arrival, Burst, or Priority to edit values.")
        self.load_custom_btn.config(state='normal')
        self.custom_status_label.config(text="Ready to load custom processes", fg="#666666")

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
                self.custom_processes = [(str(nm), int(a), int(b), int(p)) for (nm, a, b, p, pt_used) in visible_rows]
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

def load_custom_processes(self):
    """Load and validate the custom processes from the table."""
    if self.use_default_processes.get():
        messagebox.showinfo("Default Mode", "You are currently using default processes. Uncheck 'Use default processes' to load custom processes.")
        return
    
    try:
        # Read and validate all rows from the table
        rows = [self.process_tree.item(i, 'values') for i in self.process_tree.get_children()]
        validated_processes = []
        
        for i, (name, arrival, burst, priority, pt_used) in enumerate(rows):
            # Validate each field
            try:
                arrival_val = int(arrival)
                burst_val = int(burst)
                priority_val = int(priority)
                pt_used_val = int(pt_used)
                
                if arrival_val < 0:
                    raise ValueError(f"Process {name}: Arrival time must be ≥ 0")
                if burst_val < 1:
                    raise ValueError(f"Process {name}: Burst time must be ≥ 1")
                if priority_val not in (1, 2, 3, 4):
                    raise ValueError(f"Process {name}: Priority must be 1, 2, 3, or 4")
                if pt_used_val < 0:
                    raise ValueError(f"Process {name}: PT_Used must be ≥ 0")
                
                validated_processes.append((str(name), arrival_val, burst_val, priority_val))
                
            except ValueError as e:
                messagebox.showerror("Validation Error", str(e))
                return
        
        # Update the custom processes list
        self.custom_processes = validated_processes
        
        # Update status
        self.custom_status_label.config(text=f"✓ Loaded {len(validated_processes)} custom processes", fg="#27ae60")
        
        # Update settings display
        self.update_settings_display()
        
        messagebox.showinfo("Success", f"Successfully loaded {len(validated_processes)} custom processes!\nYou can now run the simulation.")
        
    except Exception as e:
        messagebox.showerror("Load Error", f"Error loading custom processes: {str(e)}")
        self.custom_status_label.config(text="✗ Load failed", fg="#e74c3c")

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
    """Simplified file parsing"""
    processes = []
    settings = {}
    
    with open(file_path, 'r') as file:
        for line_num, line in enumerate(file, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            parts = line.split()
            
            # Settings (Q0/Q1/Q2/DEMOTE/AGING value)
            if len(parts) == 2 and parts[0].upper() in ("Q0", "Q1", "Q2", "Q3", "DEMOTE", "AGING"):
                try:
                    settings[parts[0].upper()] = int(parts[1])
                except ValueError:
                    raise ValueError(f"Line {line_num}: {parts[0]} must be an integer")
                continue

            # Process (name arrival burst priority)
            if len(parts) == 4:
                try:
                    name, arrival, burst, priority = parts[0], int(parts[1]), int(parts[2]), int(parts[3])
                    if arrival < 0 or burst < 1 or priority not in (1, 2, 3, 4):
                        raise ValueError("Invalid process values")
                    processes.append((name, arrival, burst, priority))
                except ValueError:
                    raise ValueError(f"Line {line_num}: Invalid process format")
                continue

            raise ValueError(f"Line {line_num}: Invalid format")

    # Apply settings
    for key, value in settings.items():
        if key == "Q0": self.quantum_q0.set(value)
        elif key == "Q1": self.quantum_q1.set(value)
        elif key == "Q2": self.quantum_q2.set(value)
        elif key == "Q3": self.quantum_q3.set(value)
        elif key == "DEMOTE": self.demote_threshold.set(value)
        elif key == "AGING": self.aging_threshold.set(value)

    if not processes:
        raise ValueError("No processes found in file")
    
    return processes


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

    # Column mapping: #1=Name (locked), #2=Arrival, #3=BT_Now, #4=PT_Now, #5=PT_Used (locked)
    if col_id == "#1":
        messagebox.showinfo("Name Locked", "Process names are automatically generated (P1, P2, P3...).\nDouble-click on Arrival, BT_Now, or PT_Now columns to edit those values.")
        return
    elif col_id == "#5":  # PT_Used column
        messagebox.showinfo("PT_Used Locked", "PT_Used (Processing Time Used) is automatically calculated during simulation.\nThis value cannot be manually edited.")
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
        self.custom_processes = [(str(n), int(a), int(b), int(p)) for (n, a, b, p, pt_used) in rows]

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
    • Time Quantum Q3 (Lowest): {self.quantum_q3.get()}
    • Demotion Threshold: {self.demote_threshold.get()}
    • Aging Threshold: {self.aging_threshold.get()}
    • Preemption: {'Yes' if self.preempt.get() else 'No'}
    """
    
    self.settings_text.insert('1.0', settings_info)
    self.settings_text.config(state='disabled')