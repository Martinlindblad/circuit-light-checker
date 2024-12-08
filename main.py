import tkinter as tk
from gui import CircuitCheckerGUI

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Circuit Checker with Draggable Circles")
    root.geometry("1280x720")  # Set window size
    app = CircuitCheckerGUI(root)
    root.mainloop()
