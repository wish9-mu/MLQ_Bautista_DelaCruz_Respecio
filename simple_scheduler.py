# This handles all the logic for the MLFQ scheduling algorithm.
# Simple MLFQ (Multi-Level Feedback Queue) Scheduler
# This is the heart of our CPU scheduler simulation

from simple_process import Process
from copy import deepcopy

class SimpleMLFQScheduler:
    
    def __init__(self, quantums=[3, 3, 3], demote_threshold=6, aging_threshold=5, preempt=True):
        # Support both old single quantum and new separate quantums for backward compatibility
        if isinstance(quantums, int):
            # Old format: single quantum for all queues
            self.quantums = [quantums, quantums, quantums]
        else:
            # New format: separate quantums for each queue
            self.quantums = quantums[:3]  # Ensure we only take first 3 values
        
        self.demote_threshold = demote_threshold
        self.aging_threshold = aging_threshold
        self.preempt = preempt
        
        # Create 3 queues (0 = highest priority, 2 = lowest priority)
        self.queues = [[], [], []]  # Each queue is a list of process names
        
        # Keep track of all processes
        self.processes = {}  # Dictionary: process_name -> Process object
        
        # Keep track of what happened during simulation
        self.timeline = []  # List of (start_time, end_time, process_name, queue_level)
        
        # Current time in the simulation
        self.current_time = 0
        
    def add_process(self, process):
        """Add a process to the scheduler."""
        # Uses dictionary assignment to store the process (W3Schools: Python Dictionaries)
        # This lets us find the process later using its name as a key
        self.processes[process.name] = process
        # Uses _add_to_queue to put the process in the right queue (GeeksforGeeks: Python Functions)
        # This is a helper function that handles the queue placement logic
        self._add_to_queue(process, process.queue_level)
        
    def _add_to_queue(self, process, queue_level):
        """Add a process to a specific queue."""
        # Uses assignment to update the process's queue level (W3Schools: Python Variables)
        # This keeps track of which queue the process is currently in
        process.queue_level = queue_level
        # Uses assignment to record when the process became ready (W3Schools: Python Variables)
        # This is used later to calculate how long the process waited
        process.last_ready_time = self.current_time
        # Uses list.append() to add the process to the queue (W3Schools: Python List Methods)
        # This puts the process at the end of the queue (FIFO - First In, First Out)
        self.queues[queue_level].append(process.name)
        
    def _get_next_process(self):
        """Get the next process to run (from the highest priority non-empty queue)."""
        # Uses for loop with range(3) to check all three queues (W3Schools: Python For Loops)
        # We check queue 0 first (highest priority), then 1, then 2 (lowest priority)
        for queue_level in range(3):  # Check queues 0, 1, 2
            # Uses if statement to check if queue has processes (W3Schools: Python If Statement)
            # Empty lists are False, non-empty lists are True
            if self.queues[queue_level]:  # If this queue has processes
                # Uses list.pop(0) to take the first process from the queue (W3Schools: Python List Methods)
                # This removes it from the queue and returns the process name
                process_name = self.queues[queue_level].pop(0)  # Take the first one
                # Uses dictionary lookup to get the actual Process object (W3Schools: Python Dictionaries)
                # We stored the process using its name as the key
                return self.processes[process_name]
        # Returns None if no processes are ready to run (GeeksforGeeks: Python None)
        # None is Python's way of saying "nothing" or "no value"
        return None  # No processes ready
    
    def _update_waiting_times(self, process):
        """Update how long this process has been waiting."""
        # Uses hasattr() to check if the process has a last_ready_time attribute (GeeksforGeeks: Python hasattr)
        # Uses is not None to check if the attribute has a value (W3Schools: Python If Statement)
        if hasattr(process, 'last_ready_time') and process.last_ready_time is not None:
            # Uses += to add the waiting time to the total (GeeksforGeeks: Python Operators)
            # Uses subtraction to calculate how long the process waited (GeeksforGeeks: Python Operators)
            process.waiting_time += self.current_time - process.last_ready_time
            # Uses assignment to reset the ready time (W3Schools: Python Variables)
            # This prevents counting the same waiting time multiple times
            process.last_ready_time = None
    
    def _handle_aging(self):
        """Move processes to higher priority queues if they've waited too long."""
        if self.aging_threshold <= 0:
            return  # Aging is disabled
            
        # Check queues 1 and 2 (not queue 0, since it's already highest priority)
        for queue_level in [1, 2]:
            processes_to_move = []
            
            # Check each process in this queue
            for i, process_name in enumerate(self.queues[queue_level]):
                process = self.processes[process_name]
                
                # Calculate how long this process has been waiting
                waiting_time = 0
                if hasattr(process, 'last_ready_time') and process.last_ready_time is not None:
                    waiting_time = self.current_time - process.last_ready_time
                
                # If it's waited long enough, move it up
                if waiting_time >= self.aging_threshold and process.queue_level > 0:
                    processes_to_move.append(i)
            
            # Move the processes (in reverse order to maintain indices)
            for i in reversed(processes_to_move):
                process_name = self.queues[queue_level].pop(i)
                process = self.processes[process_name]
                new_queue = process.queue_level - 1
                self._add_to_queue(process, new_queue)
                process.time_in_current_queue = 0
    
    def _check_for_new_arrivals(self, new_processes):
        """Check if any new processes have arrived and add them to queues."""
        for process_data in new_processes:
            name, arrival_time, burst_time, priority = process_data
            if arrival_time <= self.current_time and name not in self.processes:
                new_process = Process(name, arrival_time, burst_time, priority)
                self.add_process(new_process)
    
    def simulate(self, process_list):
        """
        Run the simulation with the given processes.
        
        Parameters:
        - process_list: List of tuples (name, arrival_time, burst_time, priority)
        
        Returns:
        - timeline: List of (start_time, end_time, process_name, queue_level)
        - results: List of dictionaries with process statistics
        """
        # Sort processes by arrival time
        # Uses sorted() to arrange processes by when they arrive (W3Schools: Python List Methods)
        # Uses lambda function to tell sorted() to use the second element (arrival time) (GeeksforGeeks: Python Lambda)
        sorted_processes = sorted(process_list, key=lambda x: x[1])
        arrival_index = 0
        
        # Keep running until all processes are done
        # Uses while True to create an infinite loop (W3Schools: Python While Loops)
        # We'll break out of this loop when all processes are finished
        while True:
            # Check if any new processes have arrived
            # Uses while loop to check for new arrivals (W3Schools: Python While Loops)
            # Uses len() to get the total number of processes (W3Schools: Python Built-in Functions)
            while arrival_index < len(sorted_processes):
                next_arrival = sorted_processes[arrival_index]
                if next_arrival[1] <= self.current_time:
                    name, arrival_time, burst_time, priority = next_arrival
                    if name not in self.processes:
                        new_process = Process(name, arrival_time, burst_time, priority)
                        self.add_process(new_process)
                    arrival_index += 1
                else:
                    break
            
            # If no processes are ready and no more are coming, we're done
            # Uses _get_next_process() to find a process to run (GeeksforGeeks: Python Functions)
            # This returns None if no processes are ready, or a Process object if one is ready
            next_process = self._get_next_process()
            if next_process is None:
                if arrival_index >= len(sorted_processes):
                    break  # No more processes coming
                else:
                    # Jump to when the next process arrives
                    self.current_time = sorted_processes[arrival_index][1]
                    continue
            
            # Handle aging before we run a process
            # Uses _handle_aging() to move long-waiting processes to higher priority (GeeksforGeeks: Python Functions)
            # This prevents processes from waiting forever in low-priority queues
            self._handle_aging()
            
            # Update waiting time for the process we're about to run
            # Uses _update_waiting_times() to calculate how long this process waited (GeeksforGeeks: Python Functions)
            # This adds the waiting time to the process's total waiting time
            self._update_waiting_times(next_process)
            
            # Record when this process first starts
            if next_process.first_start_time is None:
                next_process.first_start_time = self.current_time
            
            # Run the process
            # Uses assignment to remember when we started running this process (W3Schools: Python Variables)
            run_start_time = self.current_time
            # Uses min() to decide how long to run the process (W3Schools: Python Built-in Functions)
            # We can't run longer than the quantum for this queue or longer than the process needs
            queue_quantum = self.quantums[next_process.queue_level]
            time_to_run = min(queue_quantum, next_process.remaining_time)
            
            # Check if we should preempt (interrupt) this process
            # because a higher priority one arrived
            if self.preempt and arrival_index < len(sorted_processes):
                next_arrival_time = sorted_processes[arrival_index][1]
                if next_arrival_time < self.current_time + time_to_run:
                    time_to_run = next_arrival_time - self.current_time
            
            # Actually run the process
            # Uses += to advance the simulation time (GeeksforGeeks: Python Operators)
            self.current_time += time_to_run
            # Uses -= to reduce the remaining work for this process (GeeksforGeeks: Python Operators)
            next_process.remaining_time -= time_to_run
            # Uses += to track how long this process has run in its current queue (GeeksforGeeks: Python Operators)
            next_process.time_in_current_queue += time_to_run
            
            # Record this execution in the timeline
            # Uses list.append() to add this execution to the timeline (W3Schools: Python List Methods)
            # Uses tuple to store start time, end time, process name, and queue level (W3Schools: Python Tuples)
            self.timeline.append((run_start_time, self.current_time, 
                                next_process.name, next_process.queue_level))
            
            # Check what to do with the process now
            # Uses is_finished() to check if the process is completely done (GeeksforGeeks: Python Methods)
            # This method returns True if remaining_time is 0 or less
            if next_process.is_finished():
                # Process is completely done
                next_process.completion_time = self.current_time
                next_process.time_in_current_queue = 0
            else:
                # Process still has work to do
                # Check if it should move to a lower priority queue
                if (self.demote_threshold > 0 and 
                    next_process.time_in_current_queue >= self.demote_threshold and 
                    next_process.queue_level < 2):
                    # Move to lower priority queue
                    next_process.time_in_current_queue = 0
                    self._add_to_queue(next_process, next_process.queue_level + 1)
                else:
                    # Put it back in the same queue
                    self._add_to_queue(next_process, next_process.queue_level)
        
        # Calculate final results
        # Uses list() to create an empty list for storing results (W3Schools: Python Lists)
        results = []
        # Uses sorted() to arrange process names in order (W3Schools: Python List Methods)
        # Uses dictionary.keys() to get all process names (W3Schools: Python Dictionary Methods)
        for process_name in sorted(self.processes.keys()):
            process = self.processes[process_name]
            results.append({
                'name': process.name,
                'arrival': process.arrival_time,
                'burst': process.burst_time,
                'priority': process.priority,
                'first_start': process.first_start_time,
                'completion': process.completion_time,
                # Uses get_turnaround_time() to calculate total time in system (GeeksforGeeks: Python Methods)
                'turnaround': process.get_turnaround_time(),
                # Uses direct access to waiting_time (no function needed) (W3Schools: Python Object Properties)
                'waiting': process.waiting_time,
                # Uses get_response_time() to calculate time to first CPU use (GeeksforGeeks: Python Methods)
                'response': process.get_response_time()
            })
        
        return self.timeline, results
    
    def simulate_with_frames(self, process_list, step=1):
        """
        Like simulate(), but also returns 'frames' for animation.
        Each frame: {'t': int, 'queues': [list[str], list[str], list[str]], 'running': str|None}
        """
        self.__init__(  # reset state using current config
            quantums=self.quantums,
            demote_threshold=self.demote_threshold,
            aging_threshold=self.aging_threshold,
            preempt=self.preempt
        )

        # Run essentially the same loop as simulate(), but:
        # - advance time in chunks, and
        # - before/after each run slice, push a snapshot
        frames = []

        def snapshot(running_name):
            frames.append({
                't': self.current_time,
                'queues': [list(q) for q in self.queues],  # copy queue names
                'running': running_name
            })

        # ----- (copy the simulate() body,
        # inserting snapshot(running_name) before and after each run) -----
        sorted_processes = sorted(process_list, key=lambda x: x[1])
        arrival_index = 0

        while True:
            while arrival_index < len(sorted_processes):
                next_arrival = sorted_processes[arrival_index]
                if next_arrival[1] <= self.current_time:
                    name, at, bt, pr = next_arrival
                    if name not in self.processes:
                        self.add_process(Process(name, at, bt, pr))
                    arrival_index += 1
                else:
                    break

            nxt = self._get_next_process()
            if nxt is None:
                if arrival_index >= len(sorted_processes):
                    # final idle snapshot
                    snapshot(None)
                    break
                else:
                    self.current_time = sorted_processes[arrival_index][1]
                    snapshot(None)
                    continue

            self._handle_aging()
            self._update_waiting_times(nxt)
            if nxt.first_start_time is None:
                nxt.first_start_time = self.current_time

            run_start = self.current_time
            queue_quantum = self.quantums[nxt.queue_level]
            time_to_run = min(queue_quantum, nxt.remaining_time)

            if self.preempt and arrival_index < len(sorted_processes):
                next_arrival_time = sorted_processes[arrival_index][1]
                if next_arrival_time < self.current_time + time_to_run:
                    time_to_run = next_arrival_time - self.current_time

            # snapshot BEFORE running this slice
            snapshot(nxt.name)

            self.current_time += time_to_run
            nxt.remaining_time -= time_to_run
            nxt.time_in_current_queue += time_to_run

            self.timeline.append((run_start, self.current_time, nxt.name, nxt.queue_level))

            if nxt.is_finished():
                nxt.completion_time = self.current_time
                nxt.time_in_current_queue = 0
                # snapshot immediately after finishing
                snapshot(None)
            else:
                if (self.demote_threshold > 0 and 
                    nxt.time_in_current_queue >= self.demote_threshold and 
                    nxt.queue_level < 2):
                    nxt.time_in_current_queue = 0
                    self._add_to_queue(nxt, nxt.queue_level + 1)
                else:
                    self._add_to_queue(nxt, nxt.queue_level)

                # snapshot after re-queue
                snapshot(None)

        # Build results exactly like simulate()
        results = []
        for pname in sorted(self.processes.keys()):
            p = self.processes[pname]
            results.append({
                'name': p.name,
                'arrival': p.arrival_time,
                'burst': p.burst_time,
                'priority': p.priority,
                'first_start': p.first_start_time,
                'completion': p.completion_time,
                'turnaround': p.get_turnaround_time(),
                'waiting': p.waiting_time,
                'response': p.get_response_time()
            })
        return self.timeline, results, frames
