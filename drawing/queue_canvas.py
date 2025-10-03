def draw_queue_canvas(self, canvas, processes):
        """Enhanced queue drawing with larger, more informative process boxes"""
        canvas.delete('all')
        
        if not processes:
            w, h = canvas.winfo_width() or 200, canvas.winfo_height() or 120
            canvas.create_text(w//2, h//2, text="Empty", font=("Arial", 12, "bold"), fill="#999")
            return
        
        w = canvas.winfo_width() or 260
        box_w, box_h, pad = min(280, w - 20), 48, 6

        for i, p in enumerate(processes[:3]):  # show top 3 to keep it clean
            y = 8 + i * (box_h + pad)
            color = self._color_for(p['name'])
            canvas.create_rectangle(10, y, 10+box_w, y+box_h, fill=color, outline='black', width=2)
            canvas.create_text(16, y+12, text=p['name'], font=("Arial", 11, "bold"), anchor='w', fill="white")

            row1 = f"BT:{p['burst']}  PT:{p['processing_time']}  REM:{p['remaining']}"
            row2 = f"WT:{p['waiting']}  AT:{p['arrival']}"
            canvas.create_text(16, y+28, text=row1, font=("Arial", 9), anchor='w', fill="white")
            canvas.create_text(16, y+40, text=row2, font=("Arial", 9), anchor='w', fill="white")