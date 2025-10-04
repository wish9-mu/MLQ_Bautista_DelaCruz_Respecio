# Simple Process Class for MLFQ Scheduler
# This file defines what a process looks like in our simulation

import os

def load_defaults(path="default_processes.txt"):
    """
    Load scheduler settings + processes from file.
    Priority: file values first, fallback = hardcoded.
    Returns ((q0,q1,q2,q3), demote, aging, process_list).
    """
    # Fallbacks
    q0, q1, q2, q3 = 3, 3, 3, 3
    demote, aging = 6, 5
    processes = list(DEFAULT_PROCESSES)

    if not os.path.exists(path):
        return (q0, q1, q2, q3), demote, aging, processes

    read_procs = []
    with open(path, "r") as f:
        for line_num, line in enumerate(f, 1):
            s = line.strip()
            if not s or s.startswith("#"): 
                continue
            parts = s.split()
            # Settings
            if len(parts) == 2:
                key, val = parts[0].upper(), parts[1]
                try:
                    ival = int(val)
                except ValueError:
                    continue
                if key == "Q0": q0 = ival
                elif key == "Q1": q1 = ival
                elif key == "Q2": q2 = ival
                elif key == "Q3": q3 = ival
                elif key == "DEMOTE": demote = ival
                elif key == "AGING": aging = ival
            # Processes
            elif len(parts) == 4:
                name = parts[0]
                try:
                    arrival = int(parts[1])
                    burst = int(parts[2])
                    prio = int(parts[3])
                except ValueError:
                    raise ValueError(f"Line {line_num}: invalid process values")
                read_procs.append((name, arrival, burst, prio))

    if read_procs:
        processes = read_procs
    return (q0, q1, q2, q3), demote, aging, processes


class Process:
    
    def __init__(self, name, arrival_time, burst_time, priority):
        self.name = name
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.priority = priority
        self.remaining_time = burst_time  # How much work is left
        
        # Uses max() and min() to convert priority to queue level (W3Schools: Python Built-in Functions)
        # Priority 1 becomes queue 0 (highest), priority 2 becomes queue 1, priority 3 becomes queue 2, priority 4 becomes queue 3
        self.queue_level = max(0, min(3, priority - 1))  # Which queue it starts in (0, 1, 2, or 3)
        self.first_start_time = None  # When it first got CPU time
        self.completion_time = None   # When it finished completely
        self.waiting_time = 0         # Total time spent waiting
        self.process_time = 0         # Demotion counter
        self.time_in_current_queue = 0  # Aging counter
        self.enqueued_at = 0            # When the process was enqueued
        
    def is_finished(self):
        """Check if the process is completely done."""
        # Uses <= comparison to check if no time is left (GeeksforGeeks: Python Operators)
        # Returns True if remaining_time is 0 or negative, False otherwise
        return self.remaining_time <= 0
    
    def get_turnaround_time(self):
        """Calculate how long from arrival to completion."""
        # Uses if statement to check if process completed (W3Schools: Python If Statement)
        # If not completed, return None; if completed, calculate the difference
        if self.completion_time is None:
            return None
        # Uses subtraction to calculate total time from arrival to completion (GeeksforGeeks: Python Operators)
        # This is the total time the process spent in the system
        return self.completion_time - self.arrival_time
    
    def get_response_time(self):
        """Calculate how long from arrival to first CPU time."""
        # Uses if statement to check if process ever started (W3Schools: Python If Statement)
        # If never started, return None; if started, calculate the difference
        if self.first_start_time is None:
            return None
        # Uses subtraction to calculate time from arrival to first CPU use (GeeksforGeeks: Python Operators)
        # This measures how quickly the system responded to the process
        return self.first_start_time - self.arrival_time
    
    def __str__(self):
        """Make it easy to print process information."""
        # Uses f-string formatting to create a readable string (W3Schools: Python String Formatting)
        # When you print a Process object, it shows all the important information
        return f"Process {self.name}: arrival={self.arrival_time}, burst={self.burst_time}, priority={self.priority}"


# Some example processes for testing
DEFAULT_PROCESSES = [
    ("P1", 1, 20, 3),  # Process 1: arrives at time 1, needs 20 units, priority 3
    ("P2", 3, 10, 2),  # Process 2: arrives at time 3, needs 10 units, priority 2
    ("P3", 5, 2, 1),   # Process 3: arrives at time 5, needs 2 units, priority 1
    ("P4", 8, 7, 2),   # Process 4: arrives at time 8, needs 7 units, priority 2
    ("P5", 11, 15, 3), # Process 5: arrives at time 11, needs 15 units, priority 3
    ("P6", 15, 8, 2),  # Process 6: arrives at time 15, needs 8 units, priority 2
    ("P7", 20, 4, 1),  # Process 7: arrives at time 20, needs 4 units, priority 1
    ("P8", 25, 12, 4), # Process 8: arrives at time 25, needs 12 units, priority 4
]

# Default settings for the scheduler
DEFAULT_QUANTUM = 3        # How much time each process gets before switching
DEFAULT_DEMOTE_THRESHOLD = 6  # How long before moving to lower priority queue
DEFAULT_AGING_THRESHOLD = 5   # How long before moving to higher priority queue
