# Simple MLFQ Scheduler - Main Program
# This is the main program that ties everything together

from simple_process import Process, DEFAULT_PROCESSES, DEFAULT_QUANTUM, DEFAULT_DEMOTE_THRESHOLD, DEFAULT_AGING_THRESHOLD
from simple_input import get_number, get_yes_or_no, print_separator, print_section_title
from simple_scheduler import SimpleMLFQScheduler



def get_processes_from_user():
    """Ask the user how many processes they want and get their details."""
    # Uses print_section_title to create a nice header (GeeksforGeeks: Python Functions)
    # This makes the output look organized and professional
    print_section_title("Setting Up Processes")
    
    # Ask how many processes
    # Uses get_number to safely get a number from the user (W3Schools: Python Input)
    # If they type something invalid, it uses the default value instead
    num_processes = get_number(
        f"How many processes would you like? (press Enter for default: {len(DEFAULT_PROCESSES)}) ",
        default_value=len(DEFAULT_PROCESSES),
        min_value=1,
        max_value=20
    )
    
    # If they want the default number, use default processes
    if num_processes == len(DEFAULT_PROCESSES):
        print("Using default processes:")
        for i, (name, arrival, burst, priority) in enumerate(DEFAULT_PROCESSES):
            print(f"  {name}: arrives at {arrival}, needs {burst} time units, priority {priority}")
        return DEFAULT_PROCESSES
    
    # Otherwise, let them create their own processes
    print(f"\nCreating {num_processes} processes...")
    print("For each process, enter the details or press Enter for suggested values.")
    
    processes = []
    for i in range(num_processes):
        name = f"P{i+1}"
        print(f"\nProcess {name}:")
        
        # Get arrival time
        # Uses get_number to get when this process arrives (W3Schools: Python Input)
        # The default spreads processes out (0, 2, 4, 6...) so they don't all come at once
        arrival = get_number(
            f"  When does {name} arrive? ",
            default_value=i * 2,  # Suggest spreading them out
            min_value=0
        )
        
        # Get burst time (how much work it needs)
        # Uses get_number to get how much work this process needs (W3Schools: Python Input)
        # Default of 10 is a reasonable amount - not too short, not too long
        burst = get_number(
            f"  How much CPU time does {name} need? ",
            default_value=10,  # Suggest 10 time units
            min_value=1
        )
        
        # Get priority
        # Uses get_number to get the priority (1-3) (W3Schools: Python Input)
        # Default of 2 is medium priority - not too high, not too low
        priority = get_number(
            f"  What priority should {name} have? (1=highest, 3=lowest) ",
            default_value=2,  # Suggest medium priority
            min_value=1,
            max_value=3
        )
        
        processes.append((name, arrival, burst, priority))
    
    return processes

def get_scheduler_settings():
    """Get the scheduler configuration from the user."""
    # Uses print_section_title to create another nice header (GeeksforGeeks: Python Functions)
    # This separates the process setup from the scheduler settings
    print_section_title("Scheduler Settings")
    
    # Get quantum (time slice)
    # Uses get_number to get how long each process runs before switching (W3Schools: Python Input)
    # This is like asking "how long does each person get to speak before we move to the next person?"
    quantum = get_number(
        f"How much time should each process get before switching? (press Enter for default: {DEFAULT_QUANTUM}) ",
        default_value=DEFAULT_QUANTUM,
        min_value=1
    )
    
    # Get demotion threshold
    # Uses get_number to get when processes move to lower priority (W3Schools: Python Input)
    # If a process runs too long, it gets moved to a less important queue
    demote_threshold = get_number(
        f"How long should a process run before moving to lower priority? (press Enter for default: {DEFAULT_DEMOTE_THRESHOLD}) ",
        default_value=DEFAULT_DEMOTE_THRESHOLD,
        min_value=1
    )
    
    # Get aging threshold
    # Uses get_number to get when processes move to higher priority (W3Schools: Python Input)
    # If a process waits too long, it gets moved to a more important queue (aging)
    aging_threshold = get_number(
        f"How long should a process wait before moving to higher priority? (press Enter for default: {DEFAULT_AGING_THRESHOLD}) ",
        default_value=DEFAULT_AGING_THRESHOLD,
        min_value=0
    )
    
    # Ask about preemption
    # Uses get_yes_or_no to ask if we should interrupt running processes (W3Schools: Python Input)
    # Preemption means stopping a low-priority process when a high-priority one arrives
    preempt = get_yes_or_no(
        "Should running processes be interrupted when higher priority ones arrive?",
        default_answer=True
    )
    
    return quantum, demote_threshold, aging_threshold, preempt

def print_timeline(timeline):
    """Print the execution timeline in a nice format."""
    # Uses print_section_title to create a header for the timeline (GeeksforGeeks: Python Functions)
    # This shows when each process ran and in which priority queue
    print_section_title("Execution Timeline")
    print("This shows when each process ran and in which queue:")
    
    if not timeline:
        print("No processes were executed.")
        return
    
    timeline_str = " | ".join([f"{start}-{end}:{name}@Q{queue}" 
                              for start, end, name, queue in timeline])
    print(timeline_str)

def print_results(results):
    """Print detailed results for each process."""
    # Uses print_section_title to create a header for the results (GeeksforGeeks: Python Functions)
    # This shows detailed statistics for each process (waiting time, turnaround time, etc.)
    print_section_title("Process Results")
    
    # Print header
    header = ["Process", "Arrival", "Burst", "Priority", "First Start", 
              "Completion", "Turnaround", "Waiting", "Response"]
    print(" | ".join(f"{h:>12}" for h in header))
    
    # Print each process's results
    for result in results:
        row = [
            result['name'],
            str(result['arrival']),
            str(result['burst']),
            str(result['priority']),
            str(result['first_start']) if result['first_start'] is not None else "N/A",
            str(result['completion']) if result['completion'] is not None else "N/A",
            str(result['turnaround']) if result['turnaround'] is not None else "N/A",
            str(result['waiting']),
            str(result['response']) if result['response'] is not None else "N/A"
        ]
        print(" | ".join(f"{cell:>12}" for cell in row))

def print_summary(results):
    """Print summary statistics."""
    # Uses print_section_title to create a header for the summary (GeeksforGeeks: Python Functions)
    # This shows overall averages and CPU utilization across all processes
    print_section_title("Summary Statistics")
    
    # Only include completed processes in averages
    completed_processes = [r for r in results if r['completion'] is not None]
    
    if not completed_processes:
        print("No processes completed.")
        return
    
    # Calculate averages
    avg_waiting = sum(r['waiting'] for r in completed_processes) / len(completed_processes)
    avg_turnaround = sum(r['turnaround'] for r in completed_processes) / len(completed_processes)
    avg_response = sum(r['response'] for r in completed_processes if r['response'] is not None) / len(completed_processes)
    
    # Calculate CPU utilization
    total_burst_time = sum(r['burst'] for r in completed_processes)
    makespan = max(r['completion'] for r in completed_processes) - min(r['arrival'] for r in completed_processes)
    cpu_utilization = (total_burst_time / makespan) * 100 if makespan > 0 else 100.0
    
    print(f"Average Waiting Time:    {avg_waiting:.2f}")
    print(f"Average Turnaround Time: {avg_turnaround:.2f}")
    print(f"Average Response Time:   {avg_response:.2f}")
    print(f"CPU Utilization:         {cpu_utilization:.2f}%")
    print(f"Total Processes:         {len(completed_processes)}")
    print(f"Total Simulation Time:   {makespan}")

def main():
    """The main function that runs everything."""
    
    
    # Get processes from user
    # Uses get_processes_from_user to ask user about processes (GeeksforGeeks: Python Functions)
    # This either uses default processes or lets the user create custom ones
    processes = get_processes_from_user()
    
    # Get scheduler settings
    # Uses get_scheduler_settings to get all the configuration (GeeksforGeeks: Python Functions)
    # This asks about quantum, demotion, aging, and preemption settings
    quantum, demote_threshold, aging_threshold, preempt = get_scheduler_settings()
    
    # Create and run the scheduler
    # Uses print_section_title to show we're starting the simulation (GeeksforGeeks: Python Functions)
    # This gives the user a clear indication that the actual work is beginning
    print_section_title("Running Simulation")
    print("Simulating CPU scheduling...")
    
    scheduler = SimpleMLFQScheduler(
        quantum=quantum,
        demote_threshold=demote_threshold,
        aging_threshold=aging_threshold,
        preempt=preempt
    )
    
    # Uses scheduler.simulate to run the actual MLFQ algorithm (GeeksforGeeks: Python Classes)
    # This does all the scheduling work and returns the timeline and results
    timeline, results = scheduler.simulate(processes)
    
    # Show results
    # Uses print_timeline to show when each process ran (GeeksforGeeks: Python Functions)
    # This shows the execution order and which queue each process used
    print_timeline(timeline)
    print()
    # Uses print_results to show detailed stats for each process (GeeksforGeeks: Python Functions)
    # This shows waiting time, turnaround time, response time for each process
    print_results(results)
    print()
    # Uses print_summary to show overall averages and CPU utilization (GeeksforGeeks: Python Functions)
    # This gives a high-level view of how well the scheduler performed
    print_summary(results)
    
    # Uses print_separator to create a nice ending line (GeeksforGeeks: Python Functions)
    # This gives a clean finish to the program output
    print_separator()
    print("Simulation complete! Thank you for using the MLFQ scheduler.")

if __name__ == "__main__":
    main()
