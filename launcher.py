# MLFQ Scheduler Launcher - Choose Your Interface
# This lets beginners choose between command-line and GUI versions

import sys
import tkinter as tk
from tkinter import messagebox

def show_launcher():
    """Show a simple launcher window to choose the interface."""
    # Uses tkinter to create a simple launcher window (W3Schools: Python GUI with Tkinter)
    root = tk.Tk()
    root.title("MLFQ Scheduler - Choose Interface")
    root.geometry("400x300")
    root.configure(bg='#f0f0f0')
    
    # Title
    title_label = tk.Label(
        root, 
        text="MLFQ CPU Scheduler",
        font=("Arial", 16, "bold"),
        bg='#f0f0f0',
        fg='#2c3e50'
    )
    title_label.pack(pady=20)
    
    # Description
    desc_label = tk.Label(
        root, 
        text="Choose how you want to run the scheduler:",
        font=("Arial", 12),
        bg='#f0f0f0'
    )
    desc_label.pack(pady=10)
    
    # GUI Button
    gui_button = tk.Button(
        root, 
        text="🖥️  GUI Version (Recommended for Beginners)",
        command=lambda: start_gui(root),
        font=("Arial", 12, "bold"),
        bg='#3498db',
        fg='white',
        height=2,
        width=40
    )
    gui_button.pack(pady=10)
    
    # Command Line Button
    cli_button = tk.Button(
        root, 
        text="💻  Command Line Version",
        command=lambda: start_cli(root),
        font=("Arial", 12, "bold"),
        bg='#95a5a6',
        fg='white',
        height=2,
        width=40
    )
    cli_button.pack(pady=10)
    
    # Help text
    help_text = """
    GUI Version: Easy-to-use graphical interface with buttons and forms
    Command Line: Text-based interface that runs in the terminal
    """
    
    help_label = tk.Label(
        root, 
        text=help_text,
        font=("Arial", 9),
        bg='#f0f0f0',
        justify='center'
    )
    help_label.pack(pady=20)
    
    # Uses tkinter.mainloop to show the launcher window (W3Schools: Python Tkinter Mainloop)
    root.mainloop()

def start_gui(parent):
    """Start the GUI version of the MLFQ scheduler."""
    # Uses tkinter.destroy to close the launcher (GeeksforGeeks: Python Tkinter Widget Methods)
    parent.destroy()
    
    try:
        # Uses import to load the GUI module (W3Schools: Python Import)
        from simple_gui import main as gui_main
        gui_main()
    except ImportError as e:
        # Uses tkinter.messagebox to show import errors (W3Schools: Python Tkinter Messagebox)
        messagebox.showerror("Error", f"Could not load GUI version: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"GUI version failed to start: {e}")

def start_cli(parent):
    """Start the command-line version of the MLFQ scheduler."""
    # Uses tkinter.destroy to close the launcher (GeeksforGeeks: Python Tkinter Widget Methods)
    parent.destroy()
    
    try:
        # Uses import to load the CLI module (W3Schools: Python Import)
        from simple_main import main as cli_main
        cli_main()
    except ImportError as e:
        # Uses tkinter.messagebox to show import errors (W3Schools: Python Tkinter Messagebox)
        messagebox.showerror("Error", f"Could not load CLI version: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"CLI version failed to start: {e}")

if __name__ == "__main__":
    # Uses try-except to handle any startup errors (W3Schools: Python Try Except)
    try:
        show_launcher()
    except Exception as e:
        print(f"Failed to start launcher: {e}")
        print("Try running the individual versions directly:")
        print("  python simple_gui.py     (for GUI version)")
        print("  python simple_main.py    (for command-line version)")
