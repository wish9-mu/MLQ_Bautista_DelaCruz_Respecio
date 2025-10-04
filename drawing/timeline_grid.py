def draw_timeline_grid(self):
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
        total_height = header_height + 5 * cell_height + 20  # 5 rows: Q0, Q1, Q2, Q3, CPU
        
        # Set scroll region
        canvas.configure(scrollregion=(0, 0, total_width, total_height))
        
        # Draw headers
        headers = ['Q0 (Highest)', 'Q1 (High)', 'Q2 (Medium)', 'Q3 (Lowest)', 'CPU (Running)']
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
        for queue_level in range(4):  # Q0, Q1, Q2, Q3
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