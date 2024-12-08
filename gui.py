import tkinter as tk
from tkinter import ttk
from detector import start_detection, reset_test, save_positions


class CircuitCheckerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Circuit Checker with Draggable Circles")
        self.root.geometry("1280x720")

        # Main frame
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left panel for controls
        control_frame = tk.Frame(main_frame, width=200, bg="lightgrey")
        control_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Description
        description_label = tk.Label(
            control_frame,
            text="This application allows you to detect lights in a circuit layout.\n"
                 "You can reposition the detection circles in real-time.\n"
                 "Use the buttons below to start, reset, or save positions.",
            wraplength=180,
            justify="left",
            bg="lightgrey",
        )
        description_label.pack(pady=10)

        # Dropdown for circuit layout
        layout_label = tk.Label(control_frame, text="Select Circuit Layout:", bg="lightgrey")
        layout_label.pack(pady=10)

        # Added CICON to the dropdown options
        self.layout_selector = ttk.Combobox(control_frame, values=["CILOW", "CICON"])
        self.layout_selector.set("CILOW")
        self.layout_selector.pack(pady=5)

        # Buttons
        start_button = tk.Button(control_frame, text="Start Detection", command=self.start_detection)
        start_button.pack(pady=10)

        reset_button = tk.Button(control_frame, text="Reset Test", command=self.reset_test)
        reset_button.pack(pady=10)

        save_button = tk.Button(control_frame, text="Save Positions", command=self.save_positions)
        save_button.pack(pady=10)

        # Canvas for camera feed
        self.canvas = tk.Canvas(main_frame, bg="black")
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    def start_detection(self):
        """Start detection for the selected layout."""
        selected_layout = self.layout_selector.get()
        start_detection(selected_layout, self.canvas)

    def reset_test(self):
        """Reset test for the selected layout."""
        selected_layout = self.layout_selector.get()
        reset_test(selected_layout)

    def save_positions(self):
        """Save positions for the selected layout."""
        selected_layout = self.layout_selector.get()
        save_positions(selected_layout)


if __name__ == "__main__":
    root = tk.Tk()
    app = CircuitCheckerGUI(root)
    root.mainloop()
