# This handles all the logic for the MLFQ scheduling algorithm.
# Simple MLFQ (Multi-Level Feedback Queue) Scheduler
# This is the heart of our CPU scheduler simulation

from process import Process

class SimpleMLFQScheduler:
    
    # Set in here are defaults
    def __init__(self, quantums=[3, 3, 3, 3], demote_threshold=6, aging_threshold=5, preempt=True):
        
        self.quantums = quantums
        self.demote_threshold = demote_threshold
        self.aging_threshold = aging_threshold
        self.preempt = preempt
        
        # Create 4 queues with each queue as a list of processes
        self.queues = [[], [], [], []]
        
        # Keep track of all processes, where in process_name -> Process object
        self.processes = {} 

        # Logical list of processes in the CPU
        # Process Name, End Time
        self.cpu = None
        self.cpu_proc_end = None
        
        # Keep track of what happened during simulation
        # List of (start_time, end_time, process_name, queue_level)
        self.timeline = []  
        
        # Current time in the simulation
        self.current_time = 0

        self.current_run_start = 0
        
    def add_process(self, process):
        # Adds a process to the scheduler.
        # Uses dictionary assignment to store the process (W3Schools: Python Dictionaries)
        # This lets us find the process later using its name as a key
        self.processes[process.name] = process
        # Uses _add_to_queue to put the process in the right queue (GeeksforGeeks: Python Functions)
        # This is a helper function that handles the queue placement logic
        self._add_to_queue(process, process.queue_level)
        
    def _add_to_queue(self, process, queue_level):
        # Add a process to a specific queue (priority level) and updates priority level.
        process.queue_level = queue_level
        process.priority = queue_level + 1

        # Uses assignment to record when the process became ready (W3Schools: Python Variables)
        # This is used later to calculate how long the process waited
        process.enqueued_at = self.current_time
        process.time_in_current_queue = 0
        # Uses list.append() to add the process to the queue (W3Schools: Python List Methods)
        # This puts the process at the end of the queue (FIFO - First In, First Out)
        self.queues[queue_level].append(process.name)
        
    def _get_next_process(self):
        # Get the next process to run (from the highest priority non-empty queue).
        
        # We check queue 0 first (highest priority), then 1, then 2 (lowest priority)
        for queue_level in range(4):  
            if self.queues[queue_level]:  
                # Uses list.pop(0) to take the first process from the queue (W3Schools: Python List Methods)
                # This removes it from the queue and returns the process name
                process_name = self.queues[queue_level].pop(0) 
                # Uses dictionary lookup to get the actual Process object (W3Schools: Python Dictionaries)
                # We stored the process using its name as the key
                return self.processes[process_name]
        # Returns None if no processes are ready to run (GeeksforGeeks: Python None)
        return None  
    
    def _update_time_in_queue(self):
        # Increases waiting time for each process and saves the total waiting time
        for queue_level in range(4):
            for process_name in (self.queues[queue_level]):
                process = self.processes[process_name]
                # Uses hasattr() to check if the process has a enqueued_at attribute (GeeksforGeeks: Python hasattr)
                # Uses is not None to check if the attribute has a value (W3Schools: Python If Statement)
                if hasattr(process, 'enqueued_at') and process.enqueued_at is not None:
                    
                    process.time_in_current_queue = self.current_time - process.enqueued_at
                    # Simply adds 1 here, just disregards waiting time increase for first increase
                    process.waiting_time += max(0, self.current_time - max(process.enqueued_at, self.current_time - 1))

    def _handle_aging(self):
        # Move processes to higher priority queues if they've waited too long.

        # Disables aging
        if self.aging_threshold <= 0:
            return  
            
        # Check q1, q2 & q3, no checks for q0 (highest)
        for queue_level in [1, 2, 3]:
            processes_to_move = []
            
            # Check each process in this queue
            for i, process_name in enumerate(self.queues[queue_level]):
                process = self.processes[process_name]

                # If it's waited long enough, move it up
                if process.time_in_current_queue >= self.aging_threshold and process.queue_level > 0:
                    processes_to_move.append(i)
            
            # Move the processes in reverse order
            for i in reversed(processes_to_move):
                process_name = self.queues[queue_level].pop(i)
                process = self.processes[process_name]
                new_queue = process.queue_level - 1

                # Reset waiting time (queue level)
                self._add_to_queue(process, new_queue)

    def _handle_demotion(self, exiting_process):
        # Move processes to lower priority queues if they've used too much CPU time.

        # Disables demotion
        if self.demote_threshold <= 0:
            return

        # Check q0, q1 & q2, no checks for q3 (lowest)
        if exiting_process.process_time >= self.demote_threshold and exiting_process.queue_level < 3:
            exiting_process.queue_level += 1
            exiting_process.process_time = 0

    def _arrive(self, sorted_processes):
        while sorted_processes and self.current_time >= sorted_processes[0][1]:
            name, at, bt, pr = sorted_processes[0]
            self.add_process(Process(name, at, bt, pr))
            sorted_processes.pop(0)

    def _preemption_check(self, sorted_processes, time_to_run, base_priority=None):

        current_process_end = self.current_time + time_to_run
        vips = []

        #if self.cpu is None:
        #    return current_process_end, None

        if base_priority is None:
            base_priority = self.cpu.priority if self.cpu is not None else None

        if base_priority is None:
            return current_process_end, None

        for process in sorted_processes:
            arrival = process[1]
            if arrival >= current_process_end:
                break
            priority = process[3]

            # Checks if a vip process is arriving earlier than the current process end
            if arrival < current_process_end and priority < base_priority:
                # Preempt the current process
                current_process_end = arrival
                vips.append(process)
        if not vips:
            return current_process_end, None

        # Checks earliest arrival time, then highest priority if tie in AT
        vip = min(vips, key=lambda p: (p[1], p[3]))
        current_process_end = vip[1]
        
        return current_process_end, vip

    def _move_to_CPU(self, next, run_end=None):
        if next is None:
            self.cpu = None
            self.cpu_proc_end = None
            return
        
        self.cpu = next

        # is set when a process is first added to the CPU
        if self.cpu.first_start_time is None:
            self.cpu.first_start_time = self.current_time # set the first start time
        
        # Mark slice start (for timeline)
        self.current_run_start = self.current_time
        self.cpu_proc_end = run_end

    def _move_out_CPU(self):
        if not self.cpu:
            return
        p = self.cpu
        self.cpu = None
        self.cpu_proc_end = None
        if p.remaining_time > 0:
            return p
            
    def _process_completed(self):
        return sum(1 for p in self.processes.values() if p.completion_time is not None)
    
    def _append_slice(self, start, end, name, qlvl):
        # If last entry is same process and end == start (back-to-back), extend it
        if self.timeline and self.timeline[-1][2] == name and self.timeline[-1][1] == start:
            s0, _, n0, q0 = self.timeline.pop()
            self.timeline.append((s0, end, n0, q0))
        else:   
            self.timeline.append((start, end, name, qlvl))

    def _snapshot(self, running_name):
        
        # Queues with attributes
        detailed_queues = []
        for queue_level in range(4):
            queue_info = []
            for process_name in self.queues[queue_level]:
                if process_name in self.processes:
                    p = self.processes[process_name]
                    queue_info.append({
                        'name': process_name,
                        'arrival': p.arrival_time,
                        'burst': p.burst_time,
                        'priority': p.priority,
                        'waiting': p.waiting_time,
                        'remaining': p.remaining_time,
                        'time_in_queue': p.time_in_current_queue,
                        'processing_time': p.process_time
                    })
            detailed_queues.append(queue_info)

        # Running process details (if any)
        running_info = None
        if running_name and running_name in self.processes:
            p = self.processes[running_name]
            running_info = {
                'name': running_name,
                'arrival': p.arrival_time,
                'queue_level': p.queue_level,
                'waiting': p.waiting_time,
                'remaining': p.remaining_time,
                'execution_time': p.burst_time - p.remaining_time,
                'time_in_queue': p.time_in_current_queue,
                'processing_time': p.process_time,
            }

        return {
            't': self.current_time,
            'queues': detailed_queues,
            'running': running_info
        }


    def simulate_with_frames(self, process_list):
        # For reset every simulation
        self.__init__(  # reset state using current config
            quantums=self.quantums,
            demote_threshold=self.demote_threshold,
            aging_threshold=self.aging_threshold,
            preempt=self.preempt
        )

        # == SNAPSHOT ==
        frames = []
        requeue_holder = None

        # Prepare for the main simulation loop
        sorted_processes = sorted(process_list, key=lambda x: x[1])

        # Extra handler if no processes
        if not sorted_processes:
            return
    
        # Handle initial process arrivals
        self._arrive(sorted_processes)

        # Wait process arrives
        while not self.processes:
            self.current_time += 1
            self._arrive(sorted_processes)

        # Main simulation loop
        while True:
            # == Increase waiting time ==
            self._update_time_in_queue()

            # == Aging ==
            self._handle_aging()

            # == Arrival ==
            self._arrive(sorted_processes)

            # If may requeue holder
            if requeue_holder:
                self._add_to_queue(requeue_holder, requeue_holder.queue_level)
                requeue_holder = None

            # == IN CPU ==

            # If wala nang processes
            if self.cpu is None: 
                next_proc = self._get_next_process()
                if next_proc is None:
                    # Check for arriving processes
                    if not sorted_processes:
                        # Optional: final snapshot(None) here
                        break
                    # If meron pa, snapshot for idle
                    frames.append(self._snapshot(None))
                else:
                    # Snapshot ! ++ Add end time ng process
                    q = self.quantums[next_proc.queue_level]

                    # Checks kung onti nalang remaining time kesa sa quantum
                    planned = min(q, next_proc.remaining_time) 
                    run_end = self.current_time + planned


                    # == Preemption ==
                    if self.preempt:
                        #preempt_end, vip = self._preemption_check(sorted_processes, planned)
                        preempt_end, vip = self._preemption_check(sorted_processes, planned, base_priority=next_proc.priority)  
                        if preempt_end is not None:
                            run_end = min(run_end, preempt_end)
                        if vip is not None:     
                            sorted_processes.remove(vip)
                            sorted_processes.insert(0, vip)

                    self._move_to_CPU(next_proc, run_end)
                    frames.append(self._snapshot(self.cpu.name))

            if self.cpu:
                self.cpu.remaining_time -= 1
                self.cpu.process_time += 1

            # Check for process completion
            if self.cpu_proc_end is not None and self.current_time + 1 == self.cpu_proc_end:
                # Store 
                ran_name  = self.cpu.name
                ran_level = self.cpu.queue_level

                # Record the slice 
                self._append_slice(self.current_run_start, self.cpu_proc_end, ran_name, ran_level)

                # Check for completion
                if self.cpu and self.cpu.remaining_time <= 0 and self.cpu.completion_time is None:
                    self.cpu.completion_time = self.current_time + 1

                # == Out CPU ==
                if self.cpu.remaining_time > 0:
                    self._handle_demotion(self.cpu)
                requeue_holder = self._move_out_CPU()


            sim_done = self._process_completed()
            # Check if all processes are completed
            if sim_done == len(self.processes):
                break

            # Time advances 
            self.current_time += 1

        # Result details
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
