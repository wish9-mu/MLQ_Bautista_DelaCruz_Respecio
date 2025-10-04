import tkinter as tk
from tkinter import ttk

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