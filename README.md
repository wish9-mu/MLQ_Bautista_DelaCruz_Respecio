# MLFQ (Multi-Level Feedback Queue) CPU Scheduler

A graphical user interface application for simulating CPU scheduling using the Multi-Level Feedback Queue algorithm. This program allows users to configure scheduling parameters, add processes, and visualize the scheduling results through an intuitive GUI.

## Features

- **Interactive GUI**: Complete graphical interface built with tkinter
- **Process Management**: Add, edit, and manage processes with custom arrival times and burst times
- **Configurable Parameters**: Adjust quantum times, demotion thresholds, and aging thresholds
- **Visual Simulation**: Real-time visualization of the scheduling process
- **Results Analysis**: Detailed statistics and performance metrics
- **File Import**: Load process configurations from text files

## Requirements

- **Python 3.x** (Python 3.6 or higher recommended)
- **tkinter** (included with most Python installations)
- No additional external dependencies required

## How to Run

### Quick Start

1. **Navigate to the project directory**:

   ```bash
   cd "MLQ_Bautista_DelaCruz_Respecio"
   ```

2. **Run the program**:
   ```bash
   python gui.py
   ```

That's it! The GUI application will launch automatically.

### Alternative Running Methods

You can also run the program using:

```bash
# Using Python 3 explicitly
python3 gui.py

# Or if Python is in your PATH
py gui.py
```

## Program Structure

The main application entry point is `gui.py`, which contains:

- **Main GUI Class**: `MLFQGUI` - The primary application window
- **Configuration Tab**: Set up scheduling parameters and process details
- **Simulation Tab**: Run and visualize the scheduling simulation
- **Results Tab**: View detailed performance metrics and statistics

## Usage Instructions

1. **Configuration**: Use the Configuration tab to set up your scheduling parameters and add processes
2. **Simulation**: Switch to the Simulation tab to run the MLFQ algorithm
3. **Results**: View the Results tab to analyze performance metrics and statistics

## File Structure

```
MLQ_Bautista_DelaCruz_Respecio/
├── gui.py                 # Main application entry point
├── process.py            # Process management classes
├── scheduler.py          # MLFQ scheduling algorithm
├── drawing/              # Visualization components
├── gui_tabs/             # GUI tab implementations
├── Processes/            # Sample process files
└── References_List/      # Documentation and references
```

## Sample Process Files

The `Processes/` directory contains example process configuration files:

- `default_processes.txt` - Default process set
- `sample_processes.txt` - Sample process configurations
- `simple_main.txt` - Simple test case

## Troubleshooting

### Common Issues

1. **"Module not found" errors**: Ensure you're running the command from the correct directory (`MLQ_Bautista_DelaCruz_Respecio/`)

2. **GUI doesn't appear**: Make sure you have tkinter installed (usually included with Python)

3. **Permission errors**: Run the command prompt as administrator if needed

### Getting Help

If you encounter any issues:

1. Ensure Python is properly installed and accessible from the command line
2. Verify you're in the correct directory
3. Check that all files are present in the project folder

## Author

MLQ_Bautista_DelaCruz_Respecio Team

---

**Note**: This program uses Python's built-in tkinter library for the GUI, so no additional package installation is required beyond having Python installed on your system.
