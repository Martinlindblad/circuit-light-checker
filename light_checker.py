import cv2
import tkinter as tk
from tkinter import ttk
import numpy as np
import winsound  # For sound notification (Windows-specific)

# Define light positions and required colors for CILOW
CILOW_LIGHTS = {
    "SERVICE OUT": {"pos": (120, 50), "color": "yellow"},
    "D3BUS CIDIS": {"pos": (180, 50), "color": "red"},
    "D3BUS SHAFT": {"pos": (240, 50), "color": "green"},
}

# Define light positions and required colors for CICON
CICON_LIGHTS = {
    "LIGHT 1": {"pos": (100, 50), "color": "green"},
    "LIGHT 2": {"pos": (200, 50), "color": "yellow"},
    "LIGHT 3": {"pos": (300, 50), "color": "red"},
}

# Circuit layout options
CIRCUIT_LAYOUTS = {
    "CILOW": CILOW_LIGHTS,
    "CICON": CICON_LIGHTS,
}

# HSV color ranges
COLOR_RANGES = {
    "yellow": [(20, 100, 100), (30, 255, 255)],
    "red": [(0, 120, 70), (10, 255, 255)],
    "green": [(40, 40, 40), (90, 255, 255)],
}

# Variables for tracking
current_layout = "CILOW"
light_status = {}  # Track status for each light


def play_success_sound():
    """Play a success sound."""
    winsound.Beep(1000, 200)  # Frequency 1000 Hz, duration 200 ms
    winsound.Beep(1500, 200)
    winsound.Beep(2000, 300)


def reset_test():
    """Reset the test state."""
    global light_status
    light_status = {label: {"checked": False, "wrong": False} for label in CIRCUIT_LAYOUTS[current_layout].keys()}
    print("Test reset.")


def update_layout(selection):
    """Update the circuit layout and reset the test."""
    global current_layout
    current_layout = selection
    reset_test()
    print(f"Selected Layout: {current_layout}")


def detect_lights(frame, layout):
    """Detect lights and update their status."""
    global light_status
    all_correct = True
    lights = CIRCUIT_LAYOUTS[layout]

    for label, data in lights.items():
        x, y = data["pos"]
        expected_color = data["color"]

        # Define a small ROI around the point
        roi_size = 10
        roi = frame[y - roi_size:y + roi_size, x - roi_size:x + roi_size]
        hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        # Check brightness
        brightness = np.mean(hsv_roi[:, :, 2])  # V channel
        if brightness < 100:  # Light is off
            light_status[label] = {"checked": False, "wrong": False}
            all_correct = False
            continue

        # Check color
        correct = False
        for color_name, (lower, upper) in COLOR_RANGES.items():
            mask = cv2.inRange(hsv_roi, np.array(lower), np.array(upper))
            if np.count_nonzero(mask) > 0:  # Detected color
                if color_name == expected_color:
                    correct = True
                    light_status[label] = {"checked": True, "wrong": False}
                else:
                    light_status[label] = {"checked": False, "wrong": True}
                break

        if not correct:
            all_correct = False

    # If all lights are correct, play success sound and reset
    if all_correct and all(status["checked"] for status in light_status.values()):
        play_success_sound()
        reset_test()


def overlay_status(frame):
    """Overlay the status on the frame."""
    lights = CIRCUIT_LAYOUTS[current_layout]
    text_x, text_y = 10, 30
    text_spacing = 30

    for label, data in lights.items():
        # Status icons
        if light_status.get(label, {}).get("checked", False):
            status = "✓"
            color = (0, 255, 0)  # Green for correct
        elif light_status.get(label, {}).get("wrong", False):
            status = "✗"
            color = (0, 0, 255)  # Red for wrong
        else:
            status = " "  # No status
            color = (255, 255, 255)  # White for default

        # Draw the status text
        cv2.putText(frame, f"{label}: {status}", (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        text_y += text_spacing


def start_detection():
    """Start the OpenCV window with the selected layout."""
    reset_test()  # Ensure the test is reset before starting
    cap = cv2.VideoCapture(0)  # Use webcam or replace with video file

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        frame = cv2.resize(frame, (640, 480))
        detect_lights(frame, current_layout)  # Detect lights
        overlay_status(frame)  # Overlay the status on the frame

        cv2.imshow("Circuit Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):  # Quit on 'q' key
            break

    cap.release()
    cv2.destroyAllWindows()


# Create GUI
root = tk.Tk()
root.title("Circuit Layout Selector")

# Dropdown menu for layout selection
layout_label = tk.Label(root, text="Select Circuit Layout:")
layout_label.pack(pady=5)

layout_selector = ttk.Combobox(root, values=list(CIRCUIT_LAYOUTS.keys()))
layout_selector.set(current_layout)
layout_selector.pack(pady=5)
layout_selector.bind("<<ComboboxSelected>>", lambda e: update_layout(layout_selector.get()))

# Start button
start_button = tk.Button(root, text="Start Detection", command=start_detection)
start_button.pack(pady=10)

# Reset button
reset_button = tk.Button(root, text="Reset Test", command=reset_test)
reset_button.pack(pady=10)

# Run the GUI
root.mainloop()
