"""
TkInter application for visualizing generator output.

This application allows users to:
1. Write Python code directly in the editor to define a generator
2. Load a Python script with a get_generator() method
3. Execute the generator and visualize its output on a canvas

The generator should yield numeric values (float or int) which are then plotted.

Example code to paste:
    from generator_builder import Constant, RepeaterFor
    
    def get_generator():
        return RepeaterFor(3, Constant(0.5))()

Or load a script with a get_generator() function that returns a generator.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import math
from pathlib import Path
from typing import Generator, Optional, Callable


class GeneratorVisualizer:
    """TkInter application for visualizing generator output."""
    
    def __init__(self, root: tk.Tk):
        """Initialize the visualizer application.
        
        Args:
            root: The Tkinter root window.
        """
        self.root = root
        self.root.title("Generator Visualizer")
        self.root.geometry("1600x700")
        
        self.generator: Optional[Generator] = None
        self.running = False
        self.current_values: list = []
        self.max_points = 500
        self.every_nth = 10
        self.filepath = None
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Set up the user interface layout."""
        # Create main paned window
        paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel: Code editor
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        
        # Editor label and buttons
        editor_top = ttk.Frame(left_frame)
        editor_top.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(editor_top, text="Python Code:").pack(side=tk.LEFT, padx=5)
        ttk.Button(editor_top, text="Load Script", command=self._load_script).pack(side=tk.LEFT, padx=2)
        ttk.Button(editor_top, text="Reload Script", command=self._reload_script).pack(side=tk.LEFT, padx=2)
        ttk.Button(editor_top, text="Save File", command=self._save_script).pack(side=tk.LEFT, padx=2)
        ttk.Button(editor_top, text="Clear", command=self._clear_editor).pack(side=tk.LEFT, padx=2)
        # File status label
        self.file_status_label = ttk.Label(editor_top, text="", foreground="blue")
        self.file_status_label.pack(side=tk.LEFT, padx=20)
        # Text editor with scrollbar
        editor_frame = ttk.Frame(left_frame)
        editor_frame.pack(fill=tk.BOTH, expand=True)
        
        self.code_editor = scrolledtext.ScrolledText(
            editor_frame, 
            wrap=tk.WORD, 
            font=("Courier", 10),
            height=25
        )
        self.code_editor.pack(fill=tk.BOTH, expand=True)
        
        # Insert example code
        self._insert_example_code()
        
        # Right panel: Visualization
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=15)
        
        # Controls
        controls_frame = ttk.Frame(right_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(controls_frame, text="Run", command=self._run_generator).pack(side=tk.LEFT, padx=2)
        ttk.Button(controls_frame, text="Stop", command=self._stop_generator).pack(side=tk.LEFT, padx=2)
        ttk.Button(controls_frame, text="Clear Graph", command=self._clear_graph).pack(side=tk.LEFT, padx=2)
        
        # Max points control
        ttk.Label(controls_frame, text="Max Points:").pack(side=tk.LEFT, padx=(20, 5))
        self.max_points_var = tk.IntVar(value=self.max_points)
        max_points_spinbox = ttk.Spinbox(
            controls_frame, 
            from_=10, 
            to=1000, 
            textvariable=self.max_points_var,
            width=8,
            command=self._update_max_points
        )
        max_points_spinbox.pack(side=tk.LEFT, padx=2)

        # Every Nth control
        ttk.Label(controls_frame, text="Every Nth:").pack(side=tk.LEFT, padx=(20, 5))
        self.every_nth_var = tk.IntVar(value=self.every_nth)
        every_nth_spinbox = ttk.Spinbox(
            controls_frame, 
            from_=1, 
            to=100, 
            textvariable=self.every_nth_var,
            width=8,
            command=lambda: setattr(self, 'every_nth', self.every_nth_var.get())
        )
        every_nth_spinbox.pack(side=tk.LEFT, padx=2)
        
        # Status label
        self.status_label = ttk.Label(controls_frame, text="Ready", foreground="blue")
        self.status_label.pack(side=tk.LEFT, padx=20)
        
        # Canvas for visualization
        canvas_frame = ttk.LabelFrame(right_frame, text="Output Visualization")
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, bg="white", height=400)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", self._on_canvas_resize)
        
        # Info label
        self.info_label = ttk.Label(right_frame, text="Points: 0 | Min: — | Max: —")
        self.info_label.pack(fill=tk.X, pady=(5, 0))
    
    def _insert_example_code(self) -> None:
        """Insert example code into the editor."""
        example = """# Example

# The "inner" sine factory picks a random step in [100,400] and runs that twice (2 cycles)
# The wrapping Repeater then repeats that a random number of times in [50,100]
# Try setting Max Points to 4000 and Every Nth to 20 and press Run several times.

from waveforms import sine_wave_factory

def get_generator():
    gen_factory = sine_wave_factory(steps = (100,400), runs=2, repeater_arg=(50,100))
    return gen_factory()
"""
        self.code_editor.insert("1.0", example)
    
    def _load_script(self) -> None:
        """Load a Python script and extract its get_generator function."""
        filepath = filedialog.askopenfilename(
            filetypes=[("Python files", "*.py"), ("All files", "*.*")],
            initialdir=str(Path.cwd())
        )
        
        if filepath:
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                self.filepath = filepath
                self.code_editor.delete("1.0", tk.END)
                self.code_editor.insert("1.0", content)
                self._update_file_status(f"Loaded: {Path(filepath).name}", "green")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load script: {e}")
    
    def _reload_script(self) -> None:
        """Reload the currently loaded script."""
        if self.filepath:
            try:
                with open(self.filepath, 'r') as f:
                    content = f.read()
                self.code_editor.delete("1.0", tk.END)
                self.code_editor.insert("1.0", content)
                self._update_file_status(f"Reloaded: {Path(self.filepath).name}", "green")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reload script: {e}")
        else:
            messagebox.showinfo("Info", "No script loaded to reload")

    def _save_script(self) -> None:
        """Save the current editor content to a Python file."""
        filepath = filedialog.asksaveasfilename(
            filetypes=[("Python files", "*.py"), ("All files", "*.*")],
            initialdir=str(Path.cwd()),
            defaultextension=".py"
        )
        
        if filepath:
            try:
                content = self.code_editor.get("1.0", tk.END)
                with open(filepath, 'w') as f:
                    f.write(content)
                self._update_file_status(f"Saved: {Path(filepath).name}", "green")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save script: {e}")
    
    def _clear_editor(self) -> None:
        """Clear the code editor."""
        self.code_editor.delete("1.0", tk.END)
    
    def _clear_graph(self) -> None:
        """Clear the visualization canvas."""
        self.current_values.clear()
        self.canvas.delete("all")
        self.info_label.config(text="Points: 0 | Min: — | Max: —")
        self._update_status("Graph cleared", "blue")
    
    def _update_max_points(self) -> None:
        """Update the max_points value from the spinbox."""
        try:
            new_max = self.max_points_var.get()
            if new_max >= 10:
                self.max_points = new_max
                self._update_status(f"Max points set to {new_max}", "blue")
        except tk.TclError:
            pass
    
    def _run_generator(self) -> None:
        """Run the generator from the code editor in a separate thread."""
        if self.running:
            messagebox.showwarning("Warning", "A generator is already running")
            return
        
        code = self.code_editor.get("1.0", tk.END)
        
        if not code.strip():
            messagebox.showerror("Error", "Please enter Python code")
            return
        
        self._execute_generator(code)
    
    def _execute_generator(self, code: str) -> None:
        """Execute the generator code and visualize output.
        
        Args:
            code: The Python code containing a get_generator() function.
        """
        try:
            self.running = True
            self._update_status("Running...", "orange")
            self.current_values.clear()
            
            # Create namespace for execution
            namespace: dict = {}
            
            # Execute user code
            exec(code, namespace)
            
            # Get the generator
            if "get_generator" not in namespace:
                self.root.after(0, lambda: messagebox.showerror(
                    "Error", 
                    "Code must define a get_generator() function that returns a generator"
                ))
                self.running = False
                self._update_status("Error: No get_generator() function", "red")
                return
            
            get_generator: Callable = namespace["get_generator"]
            gen = get_generator()
            
            # Consume generator values
            for index, value in enumerate(gen):
                if not self.running:
                    break
                
                # Convert value to float
                try:
                    float_value = float(value)
                except (ValueError, TypeError):
                    continue
                
                if index % self.every_nth == 0:
                    self.current_values.append(float_value)
                
                # Update canvas periodically
                #if len(self.current_values) % 10 == 0:
                #    self.root.after(0, self._redraw_canvas)
                
                # Stop when max_points is reached
                if len(self.current_values) >= self.max_points:
                    break
                
            
            # Final redraw
            self.root.after(0, self._redraw_canvas)
            
            if self.running:
                self._update_status(f"Complete: {len(self.current_values)} points", "green")
            else:
                self._update_status("Stopped", "red")
            
            self.running = False
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: messagebox.showerror(
                "Execution Error",
                f"Error running generator:\n\n{error_msg}"
            ))
            self._update_status(f"Error: {error_msg[:50]}", "red")
            self.running = False
    
    def _redraw_canvas(self) -> None:
        """Redraw the visualization canvas with current values."""
        if not self.current_values:
            return
        
        self.canvas.delete("all")
        
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width <= 1 or height <= 1:
            return
        
        # Calculate bounds
        min_val = min(self.current_values)
        max_val = max(self.current_values)
        value_range = max_val - min_val if max_val != min_val else 1
        
        # Padding
        padding = 40
        plot_width = width - 2 * padding
        plot_height = height - 2 * padding
        
        # Draw axes
        self.canvas.create_line(padding, height - padding, width - padding, height - padding, fill="black", width=2)
        self.canvas.create_line(padding, padding, padding, height - padding, fill="black", width=2)
        
        # Draw labels
        self.canvas.create_text(padding - 20, padding, text=f"{max_val:.2f}", font=("Arial", 8))
        self.canvas.create_text(padding - 20, height - padding, text=f"{min_val:.2f}", font=("Arial", 8))
        self.canvas.create_text(width - padding, height - padding + 15, text="Index", font=("Arial", 8))
        
        # Draw grid
        grid_lines = 5
        for i in range(grid_lines + 1):
            y = height - padding - (i / grid_lines) * plot_height
            self.canvas.create_line(padding, y, width - padding, y, fill="lightgray", dash=(2, 2))
        
        # Draw data points and lines
        points = []
        for i, value in enumerate(self.current_values):
            x = padding + (i / max(len(self.current_values) - 1, 1)) * plot_width
            y = height - padding - ((value - min_val) / value_range) * plot_height
            points.append((x, y))
        
        if len(points) > 1:
            self.canvas.create_line(*[coord for point in points for coord in point], fill="blue", width=1)
        
        # Draw points
        point_size = 2
        for x, y in points:
            self.canvas.create_oval(x - point_size, y - point_size, 
                                   x + point_size, y + point_size, 
                                   fill="darkblue")
        
        # Update info
        self._update_info()
    
    def _update_info(self) -> None:
        """Update the info label with statistics."""
        if self.current_values:
            min_val = min(self.current_values)
            max_val = max(self.current_values)
            avg_val = sum(self.current_values) / len(self.current_values)
            info_text = f"Points: {len(self.current_values)} | Min: {min_val:.4f} | Max: {max_val:.4f} | Avg: {avg_val:.4f}"
        else:
            info_text = "Points: 0 | Min: — | Max: —"
        
        self.info_label.config(text=info_text)
    
    def _stop_generator(self) -> None:
        """Stop the running generator."""
        if self.running:
            self.running = False
            self._update_status("Stopped", "red")
        else:
            messagebox.showinfo("Info", "No generator is running")
    
    def _update_status(self, message: str, color: str = "blue") -> None:
        """Update the status label.
        
        Args:
            message: Status message to display.
            color: Text color for the message.
        """
        self.status_label.config(text=message, foreground=color)
    
    def _update_file_status(self, message: str, color: str = "blue") -> None:
        """Update the file status label.
        
        Args:
            message: Status message to display.
            color: Text color for the message.
        """
        self.file_status_label.config(text=message, foreground=color)   

    def _on_canvas_resize(self, event) -> None:
        """Handle canvas resize event."""
        if self.current_values:
            self._redraw_canvas()


def main():
    """Launch the Generator Visualizer application."""
    root = tk.Tk()
    app = GeneratorVisualizer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
