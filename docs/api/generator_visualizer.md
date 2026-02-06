# Generator Visualizer

Interactive TkInter application for visualizing generator output.

## Overview

The Generator Visualizer provides a graphical user interface for testing and visualizing generators from the `generator_builder` and `waveform` modules. It allows users to write Python code directly or load scripts that define generators, then see their output plotted on a canvas.

## Features

- **Code Editor**: Write or load Python code with a `get_generator()` function
- **Visualization**: Plot generator output on a canvas
- **Interactive Controls**: Run, stop, and clear graphs with button controls
- **Configurable Max Points**: Adjust the maximum number of points before generator terminates (10-1000)
- **Configurable Every Nth point**: Plot only every Nth point (1-100). Along with Max Points this determines how far through the generator the visualizer gets.
- **Statistics Display**: View point count, minimum, maximum, and average values
- **File Loading**: Load and reload Python scripts with a `get_generator()` method

## Running the Visualizer

```bash
python3 generator_visualizer.py
```

This launches the interactive application with a two-panel layout:
- **Left Panel**: Code editor with example code
- **Right Panel**: Visualization canvas with controls

## Using the Visualizer

### Basic Usage

1. Write Python code in the editor that defines a `get_generator()` function:

```python
from generator_builder import Constant, RepeaterFor

def get_generator():
    return RepeaterFor(3, Constant(0.5))()
```

2. Click **Run** to execute the generator and visualize output
3. The result appears on the canvas with axes and gridlines
4. Statistics display shows point count, min/max/average values

### Managing Scripts

Click **Load Script** to browse and load a Python file that contains a `get_generator()` function. The file contents replace the editor code.

Click **Reload Script** to reload the currently opened script from disk. This allows the user to user their editor of choice - make changes, save, reload into visualizer.

Click **Save Script** to save the current script.

### Controls

- **Run**: Execute the generator code and visualize output
- **Stop**: Terminate a running generator
- **Clear Graph**: Clear the canvas and reset statistics
- **Max Points**: Spinbox to set the point limit (10-1000, default 500)


## Requirements

- Python 3.6+
- tkinter (included with most Python installations)
- generator_builder and waveform modules

## Class Reference

### GeneratorVisualizer

Main application class managing the UI and generator execution.

**Attributes:**

- `generator`: Currently loaded generator instance
- `running`: Boolean indicating if generator is executing
- `current_values`: List of plotted values
- `max_points`: Maximum points before generator terminates (default: 500)

**Methods:**

- `_run_generator()`: Execute generator from code editor
- `_stop_generator()`: Terminate running generator
- `_clear_graph()`: Clear visualization and statistics
- `_load_script()`: Load Python script from file
- `_reload_script()`: Reload Python script from the current file
- `_redraw_canvas()`: Update visualization with current data
- `_update_max_points()`: Update max_points from spinbox

## Graph Display

The visualization canvas includes:

- **Axes**: X-axis for index, Y-axis for values
- **Gridlines**: Horizontal lines at regular intervals for reference
- **Data Points**: Blue dots at each value
- **Connecting Lines**: Blue line connecting all points to show waveform
- **Labels**: Min/max value labels on Y-axis

The graph automatically scales to fit all data points and adjusts when the window is resized.

## Error Handling

- **Missing Function**: Returns error if code doesn't define `get_generator()`
- **Execution Errors**: Displays error message if generator raises an exception
- **Invalid Values**: Silently skips non-numeric values from generator
- **File Load Errors**: Shows dialog if script cannot be loaded

All errors are displayed as messagebox dialogs and logged to the status label.
