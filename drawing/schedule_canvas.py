def draw_schedule_timeline(self, frame):
        """Draw the horizontal timeline with current running process on top and past slices below."""
        c = self.schedule_canvas
        c.delete('all')

        W = c.winfo_width() or 520
        H = c.winfo_height() or 220
        bw, bh, gap = 100, 64, 8
        
        # Add labels for the two rows
        c.create_text(5, 25, text="Current:", font=("Arial", 10, "bold"), anchor='w', fill="black")
        c.create_text(5, 95, text="Queued:", font=("Arial", 10, "bold"), anchor='w', fill="black")

        # Row 1: Current running process (TOP ROW)
        current_x = 60  # Start after the label
        current_y = 10  # Top position
        
        if frame['running']:
            rp = frame['running']
            col = self._color_for(rp['name'])
            c.create_rectangle(current_x, current_y, current_x+bw, current_y+bh, fill=col, outline='red', width=3)
            c.create_text(current_x+bw//2, current_y+12, text=rp['name'], font=("Arial", 12, "bold"), fill="white")
            c.create_text(current_x+bw//2, current_y+30, text=f"Q{rp['queue_level']}  REM:{rp['remaining']}", font=("Arial", 9), fill="white")
            # Display BT, PT on first line and WT, AT on second line for CPU queue
            # Calculate burst time from execution_time + remaining
            burst_time = rp.get('execution_time', 0) + rp.get('remaining', 0)
            line1_text = f"BT:{burst_time} PT:{rp.get('processing_time', 'N/A')}"
            line2_text = f"WT:{rp.get('waiting', 'N/A')} AT:{rp.get('arrival', 'N/A')}"
            c.create_text(current_x+bw//2, current_y+42, text=line1_text, font=("Arial", 8), fill="white")
            c.create_text(current_x+bw//2, current_y+54, text=line2_text, font=("Arial", 8), fill="white")

        # Row 2: Incoming processes in queues (BOTTOM ROW)
        queue_x = 60  # Start after the label
        queue_y = 80  # Bottom position
        
        # Show processes from all queues (Q0, Q1, Q2) in priority order
        for queue_level in range(3):  # Q0 (highest) to Q2 (lowest)
            queue_processes = frame['queues'][queue_level]
            for process in queue_processes:
                # Skip the currently running process to avoid duplication
                if frame['running'] and process['name'] == frame['running']['name']:
                    continue
                    
                col = self._color_for(process['name'])
                # Use different border colors for different queue levels
                border_colors = ['#FFD700', '#C0C0C0', '#CD7F32']  # Gold, Silver, Bronze
                border_color = border_colors[queue_level]
                
                c.create_rectangle(queue_x, queue_y, queue_x+bw, queue_y+bh, fill=col, outline=border_color, width=2)
                c.create_text(queue_x+bw//2, queue_y+12, text=process['name'], font=("Arial", 11, "bold"), fill="white")
                c.create_text(queue_x+bw//2, queue_y+30, text=f"Q{queue_level}  REM:{process['remaining']}", font=("Arial", 9), fill="white")
                c.create_text(queue_x+bw//2, queue_y+48, text=f"WT:{process['waiting']}", font=("Arial", 9), fill="white")
                queue_x += bw + gap

        # Set scroll region to accommodate both rows
        max_x = max(current_x + bw + gap, queue_x + gap)
        c.configure(scrollregion=(0, 0, max(W, max_x), H))