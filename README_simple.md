# Simple MLFQ CPU Scheduler - Beginner Version

This is a simplified, beginner-friendly version of a Multi-Level Feedback Queue (MLFQ) CPU scheduler simulator. It's designed to be easy to understand for people learning Python and computer science concepts.

## What is MLFQ?

Multi-Level Feedback Queue (MLFQ) is a CPU scheduling algorithm used by operating systems to decide which process gets to use the CPU. Here's how it works:

1. **Multiple Priority Levels**: There are 3 queues (levels 0, 1, 2) where level 0 is highest priority
2. **Time Quantum**: Each process gets a certain amount of time to run before switching
3. **Feedback**: Processes can move between queues based on their behavior
4. **Aging**: Long-waiting processes can move to higher priority queues

## Files in this Project

### Core Files

- `launcher.py` - Simple launcher to choose between GUI and command-line versions
- `simple_gui.py` - Graphical user interface version (recommended for beginners)
- `simple_main.py` - Command-line version of the main program
- `simple_process.py` - Defines what a process looks like
- `simple_scheduler.py` - The MLFQ scheduling algorithm
- `simple_input.py` - Helper functions for getting user input

### How to Run

1. Make sure you have Python 3 installed
2. Choose your preferred interface:

   **Option 1: Launcher (Recommended)**
   ```bash
   python launcher.py
   ```
   This opens a simple window where you can choose between GUI and command-line versions.

   **Option 2: GUI Version (Easiest for Beginners)**
   ```bash
   python simple_gui.py
   ```
   This opens a graphical interface with buttons, forms, and visual results.

   **Option 3: Command-Line Version**
   ```bash
   python simple_main.py
   ```
   This runs in the terminal with text prompts and outputs.

## What Each File Does

### `simple_process.py`

- Defines the `Process` class that represents a task/process
- Contains default process examples for testing
- Has helper methods to calculate timing statistics

### `simple_input.py`

- Contains functions to get input from the user
- Handles errors gracefully (like invalid numbers)
- Provides nice formatting for prompts

### `simple_scheduler.py`

- Contains the `SimpleMLFQScheduler` class
- Implements the core MLFQ algorithm
- Handles process scheduling, aging, and preemption
- Returns detailed results about the simulation

### `simple_main.py`

- The command-line version of the main program
- Gets input from the user through text prompts
- Runs the simulation
- Displays results in a nice format

### `simple_gui.py`

- The graphical user interface version
- Uses tkinter to create a user-friendly interface
- Has tabs for different functions (Processes, Settings, Simulation, Results)
- Shows results in tables and formatted text
- Recommended for beginners who prefer visual interfaces

### `launcher.py`

- A simple launcher that lets you choose between GUI and command-line versions
- Opens a small window with two buttons
- Makes it easy to pick your preferred interface

## Key Concepts Explained

### Process

A process is like a task that needs to be done. It has:

- **Name**: Like "P1", "P2", etc.
- **Arrival Time**: When it shows up to be processed
- **Burst Time**: How much CPU time it needs
- **Priority**: How important it is (1=highest, 3=lowest)

### Queues

Think of queues like lines at different priority levels:

- **Queue 0**: VIP line (highest priority)
- **Queue 1**: Regular line (medium priority)
- **Queue 2**: Economy line (lowest priority)

### Time Quantum

This is how much time each process gets before we switch to another one. Like giving each person 5 minutes to speak before moving to the next person.

### Aging

If a process waits too long in a lower priority queue, it gets moved up to a higher priority queue. This prevents processes from waiting forever.

### Preemption

This means we can interrupt a running process if a higher priority one arrives. Like if a VIP customer shows up, we might interrupt the current customer.

## GUI Features

The GUI version (`simple_gui.py`) provides a beginner-friendly interface with:

### **Processes Tab**
- Choose number of processes with a spinner
- Toggle between default and custom processes
- Add custom processes with a form
- View all processes in a table
- Clear processes with one click

### **Settings Tab**
- Configure scheduler settings with spinners and radio buttons
- See helpful explanations for each setting
- Built-in help text explaining MLFQ concepts
- Real-time settings preview

### **Simulation Tab**
- One-click simulation start
- Progress bar showing simulation status
- Current settings display
- Easy access to run simulations

### **Results Tab**
- Visual timeline showing process execution
- Interactive results table with all process details
- Summary statistics in a formatted display
- Easy-to-read formatting and organization

## Example Output

**GUI Version:**
- Visual tabs for different functions
- Tables and formatted displays
- Progress indicators and status messages
- Interactive forms and buttons

**Command-Line Version:**
- Text-based prompts and responses
- Formatted console output
- Step-by-step configuration process
- Detailed text results and statistics

## Learning Objectives

By studying this code, you'll learn:

- Object-oriented programming concepts (classes, methods)
- How to structure a program into multiple files
- Input validation and error handling
- Algorithm implementation (MLFQ scheduling)
- Data structures (lists, dictionaries, queues)
- How to calculate and display statistics

## Tips for Beginners

1. **Start with `simple_main.py`** - This shows the overall flow
2. **Look at `simple_process.py`** - This shows basic class concepts
3. **Study `simple_input.py`** - This shows input handling patterns
4. **Examine `simple_scheduler.py`** - This shows algorithm implementation

## Comparing to the Original

The original code used advanced Python features like:

- `@dataclass` decorators
- Complex type hints
- Advanced list comprehensions
- Lambda functions

This beginner version uses:

- Simple classes with `__init__` methods
- Basic loops and if statements
- Clear variable names
- Extensive comments

Both versions do the same thing, but this one is much easier to understand and modify!
