# Simple Process Class for MLFQ Scheduler
# This file defines what a process looks like in our simulation


# Uses import to bring in the os module for file operations
# Learn more: https://www.w3schools.com/python/python_modules.asp
import os

def load_defaults(path="default_processes.txt"):
    """
    Load scheduler settings + processes from file.
    Priority: file values first, fallback = hardcoded.
    Returns ((q0,q1,q2), demote, aging, process_list).
    """
    # Uses multiple assignment to set default values
    # Learn more: https://www.w3schools.com/python/python_variables.asp
    q0, q1, q2 = 3, 3, 3
    demote, aging = 6, 5
    # Uses list() to create a copy of DEFAULT_PROCESSES
    # Learn more: https://www.w3schools.com/python/python_lists.asp
    processes = list(DEFAULT_PROCESSES)

    # Uses os.path.exists() to check if the file exists
    # Learn more: https://www.geeksforgeeks.org/python-os-path-exists-method/
    if not os.path.exists(path):
        return (q0, q1, q2), demote, aging, processes

    # Uses empty list to store processes we read from file
    # Learn more: https://www.w3schools.com/python/python_lists.asp
    read_procs = []
    # Uses with statement to safely open and read files
    # Learn more: https://www.w3schools.com/python/python_file_handling.asp
    with open(path, "r") as f:
        # Uses enumerate() to get both line number and line content
        # Learn more: https://www.geeksforgeeks.org/enumerate-in-python/
        for line_num, line in enumerate(f, 1):
            # Uses strip() to remove spaces and newlines from the line
            # Learn more: https://www.w3schools.com/python/python_strings.asp
            s = line.strip()
            # Uses if statement with or to check multiple conditions
            # Learn more: https://www.w3schools.com/python/python_conditions.asp
            # Uses startswith() to check if line begins with # (comment)
            # Learn more: https://www.geeksforgeeks.org/python-string-startswith-method/
            if not s or s.startswith("#"): 
                continue
            # Uses split() to break the line into separate words
            # Learn more: https://www.w3schools.com/python/python_strings.asp
            parts = s.split()
            # Settings
            # Uses len() to check how many parts we have
            # Learn more: https://www.w3schools.com/python/python_ref_functions.asp
            if len(parts) == 2:
                # Uses indexing to get the first and second parts
                # Learn more: https://www.w3schools.com/python/python_lists_access.asp
                # Uses upper() to make the key uppercase for consistency
                # Learn more: https://www.geeksforgeeks.org/python-string-upper-method/
                key, val = parts[0].upper(), parts[1]
                # Uses try-except to handle conversion errors
                # Learn more: https://www.w3schools.com/python/python_try_except.asp
                try:
                    # Uses int() to convert text to a number
                    # Learn more: https://www.w3schools.com/python/python_casting.asp
                    ival = int(val)
                except ValueError:
                    continue
                # Uses if-elif chain to check different setting names
                # Learn more: https://www.w3schools.com/python/python_conditions.asp
                if key == "Q0": q0 = ival
                elif key == "Q1": q1 = ival
                elif key == "Q2": q2 = ival
                elif key == "DEMOTE": demote = ival
                elif key == "AGING": aging = ival
            # Processes
            # Uses elif to check if we have exactly 4 parts
            # Learn more: https://www.w3schools.com/python/python_conditions.asp
            elif len(parts) == 4:
                # Uses indexing to get the process name
                # Learn more: https://www.w3schools.com/python/python_lists_access.asp
                name = parts[0]
                # Uses try-except to handle conversion errors
                # Learn more: https://www.w3schools.com/python/python_try_except.asp
                try:
                    # Uses int() to convert arrival time to number
                    # Learn more: https://www.w3schools.com/python/python_casting.asp
                    arrival = int(parts[1])
                    # Uses int() to convert burst time to number
                    # Learn more: https://www.w3schools.com/python/python_casting.asp
                    burst = int(parts[2])
                    # Uses int() to convert priority to number
                    # Learn more: https://www.w3schools.com/python/python_casting.asp
                    prio = int(parts[3])
                except ValueError:
                    # Uses f-string to create error message with line number
                    # Learn more: https://www.w3schools.com/python/python_string_formatting.asp
                    # Uses raise to stop the program and show the error
                    # Learn more: https://www.geeksforgeeks.org/python-exception-handling/
                    raise ValueError(f"Line {line_num}: invalid process values")
                # Uses append() to add the process to our list
                # Learn more: https://www.w3schools.com/python/python_lists_add.asp
                # Uses tuple to group the process data together
                # Learn more: https://www.w3schools.com/python/python_tuples.asp
                read_procs.append((name, arrival, burst, prio))

    # Uses if statement to check if we read any processes
    # Learn more: https://www.w3schools.com/python/python_conditions.asp
    if read_procs:
        processes = read_procs
    # Uses return to send back all the values we calculated
    # Learn more: https://www.w3schools.com/python/python_functions.asp
    # Uses tuple to group the return values together
    # Learn more: https://www.w3schools.com/python/python_tuples.asp
    return (q0, q1, q2), demote, aging, processes


class Process:
    """
    A simple class to represent a process in our CPU scheduler.
    Think of a process like a task that needs to be done.
    """
    
    def __init__(self, name, arrival_time, burst_time, priority):
        """
        Create a new process.
        
        Parameters:
        - name: A string like "P1", "P2", etc. (like giving a task a name)
        - arrival_time: When the process arrives at the CPU (like when you start a task)
        - burst_time: How much CPU time the process needs (like how long a task takes)
        - priority: How important the process is (1 = most important, 3 = least important)
        """
        # Uses self to store the process name
        # Learn more: https://www.w3schools.com/python/python_classes.asp
        self.name = name
        # Uses self to store when the process arrives
        # Learn more: https://www.w3schools.com/python/python_classes.asp
        self.arrival_time = arrival_time
        # Uses self to store how much work the process needs
        # Learn more: https://www.w3schools.com/python/python_classes.asp
        self.burst_time = burst_time
        # Uses self to store the process priority
        # Learn more: https://www.w3schools.com/python/python_classes.asp
        self.priority = priority
        
        # These will be set during simulation
        # Uses assignment to track remaining work
        # Learn more: https://www.w3schools.com/python/python_variables.asp
        self.remaining_time = burst_time  # How much work is left
        # Uses max() and min() to convert priority to queue level
        # Learn more: https://www.w3schools.com/python/python_ref_functions.asp
        # Uses arithmetic to convert priority 1,2,3 to queue levels 0,1,2
        # Learn more: https://www.geeksforgeeks.org/python-operators/
        self.queue_level = max(0, min(2, priority - 1))  # Which queue it starts in (0, 1, or 2)
        # Uses None to indicate "not set yet"
        # Learn more: https://www.geeksforgeeks.org/python-none-keyword/
        self.first_start_time = None  # When it first got CPU time
        # Uses None to indicate "not finished yet"
        # Learn more: https://www.geeksforgeeks.org/python-none-keyword/
        self.completion_time = None   # When it finished completely
        # Uses 0 to start counting waiting time
        # Learn more: https://www.w3schools.com/python/python_numbers.asp
        self.waiting_time = 0         # Total time spent waiting
        # Uses 0 to start counting time in current queue
        # Learn more: https://www.w3schools.com/python/python_numbers.asp
        self.time_in_current_queue = 0  # Time spent in current queue level
        
    def is_finished(self):
        """Check if the process is completely done."""
        # Uses <= comparison to check if no time is left
        # Learn more: https://www.geeksforgeeks.org/python-operators/
        return self.remaining_time <= 0
    
    def get_turnaround_time(self):
        """Calculate how long from arrival to completion."""
        # Uses if statement to check if process completed
        # Learn more: https://www.w3schools.com/python/python_conditions.asp
        # Uses is None to check if completion_time hasn't been set yet
        # Learn more: https://www.geeksforgeeks.org/python-none-keyword/
        if self.completion_time is None:
            return None
        # Uses subtraction to calculate total time from arrival to completion
        # Learn more: https://www.geeksforgeeks.org/python-operators/
        return self.completion_time - self.arrival_time
    
    def get_response_time(self):
        """Calculate how long from arrival to first CPU time."""
        # Uses if statement to check if process ever started
        # Learn more: https://www.w3schools.com/python/python_conditions.asp
        # Uses is None to check if first_start_time hasn't been set yet
        # Learn more: https://www.geeksforgeeks.org/python-none-keyword/
        if self.first_start_time is None:
            return None
        # Uses subtraction to calculate time from arrival to first CPU use
        # Learn more: https://www.geeksforgeeks.org/python-operators/
        return self.first_start_time - self.arrival_time
    
    def __str__(self):
        """Make it easy to print process information."""
        # Uses f-string formatting to create a readable string
        # Learn more: https://www.w3schools.com/python/python_string_formatting.asp
        # Uses self to access the process's own data
        # Learn more: https://www.w3schools.com/python/python_classes.asp
        return f"Process {self.name}: arrival={self.arrival_time}, burst={self.burst_time}, priority={self.priority}"


# Some example processes for testing
# Uses list of tuples to store process data
# Learn more: https://www.w3schools.com/python/python_lists.asp
DEFAULT_PROCESSES = [
    ("P1", 1, 20, 3),  # Process 1: arrives at time 1, needs 20 units, priority 3
    ("P2", 3, 10, 2),  # Process 2: arrives at time 3, needs 10 units, priority 2
    ("P3", 5, 2, 1),   # Process 3: arrives at time 5, needs 2 units, priority 1
    ("P4", 8, 7, 2),   # Process 4: arrives at time 8, needs 7 units, priority 2
    ("P5", 11, 15, 3), # Process 5: arrives at time 11, needs 15 units, priority 3
    ("P6", 15, 8, 2),  # Process 6: arrives at time 15, needs 8 units, priority 2
    ("P7", 20, 4, 1),  # Process 7: arrives at time 20, needs 4 units, priority 1
]

# Default settings for the scheduler
DEFAULT_QUANTUM = 3        # How much time each process gets before switching
DEFAULT_DEMOTE_THRESHOLD = 6  # How long before moving to lower priority queue
DEFAULT_AGING_THRESHOLD = 5   # How long before moving to higher priority queue
