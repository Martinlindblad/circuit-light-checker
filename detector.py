import cv2
from layouts import CIRCUIT_LAYOUTS, COLOR_RANGES
import numpy as np
from PIL import Image, ImageTk
import tkinter as tk
import threading
import json

from utils import play_fail_sound, play_success_sound

light_status = {}
current_layout = "CILOW"
circles = {}


def update_circles(layout, canvas=None):
    """Update the `circles` dictionary based on the selected layout and initialize draggable circles."""
    global circles
    circles.clear()
    for label, data in CIRCUIT_LAYOUTS[layout].items():
        circles[label] = {"x": data["pos"][0], "y": data["pos"][1], "id": None}

    if canvas:
        canvas.delete("all")
        for label, data in circles.items():
            r = 10
            data["id"] = canvas.create_oval(
                data["x"] - r, data["y"] - r, data["x"] + r, data["y"] + r,
                fill="blue", outline="black", tags=label
            )


def save_positions(layout):
    """Save current circle positions for the given layout."""
    try:
        with open("positions.json", "r") as file:
            all_positions = json.load(file)
    except FileNotFoundError:
        all_positions = {}

    all_positions[layout] = {label: {"x": data["x"], "y": data["y"]} for label, data in circles.items()}

    with open("positions.json", "w") as file:
        json.dump(all_positions, file, indent=4)
    print(f"Positions saved for layout: {layout}")


def load_positions(layout):
    """Load positions for the given layout if available."""
    global circles
    try:
        with open("positions.json", "r") as file:
            all_positions = json.load(file)
            if layout in all_positions:
                for label, pos in all_positions[layout].items():
                    if label in circles:
                        circles[label]["x"], circles[label]["y"] = pos["x"], pos["y"]
                print(f"Positions loaded for layout: {layout}")
            else:
                print(f"No saved positions found for layout: {layout}. Using default positions.")
    except FileNotFoundError:
        print("No saved positions file found. Using default positions.")


def reset_test(layout):
    """Reset the test state."""
    global light_status
    light_status = {label: {"checked": False, "wrong": False, "success": False} for label in CIRCUIT_LAYOUTS[layout].keys()}
    print(f"Test reset for layout: {layout}")


def draw_frame(frame):
    """Draw a frame for the circuit layout."""
    frame_height, frame_width = frame.shape[:2]
    frame_width_layout = 600
    frame_height_layout = 300

    frame_x_start = int((frame_width - frame_width_layout) / 2)
    frame_y_start = int((frame_height - frame_height_layout) / 2)
    frame_x_end = frame_x_start + frame_width_layout
    frame_y_end = frame_y_start + frame_height_layout

    cv2.rectangle(frame, (frame_x_start, frame_y_start), (frame_x_end, frame_y_end), (255, 255, 255), 2)
    return frame

import time

def show_success_message(canvas):
    """Display a success message on the canvas."""
    success_text = canvas.create_text(
        640, 360,  # Center of the canvas
        text="Success! Test will reset in 3 seconds...",
        fill="green",
        font=("Arial", 24, "bold")
    )

    # Remove the message after 3 seconds
    canvas.after(3000, lambda: canvas.delete(success_text))



def detect_lights(frame, layout, canvas):
    """Detect lights and update their status."""
    global light_status
    lights = CIRCUIT_LAYOUTS[layout]

    # Initialize light status if not already set
    for label in lights.keys():
        if label not in light_status:
            light_status[label] = {"checked": False, "wrong": False, "success": False}

    all_correct = True  # Track if all lights are correctly detected

    for label, data in lights.items():
        if light_status[label]["success"]:
            continue  # Skip lights already marked as successful

        x = circles[label]["x"]
        y = circles[label]["y"]
        expected_color = data["color"]

        # Define region of interest (ROI)
        roi_size = 10
        if 0 <= y - roi_size < frame.shape[0] and 0 <= x - roi_size < frame.shape[1]:
            roi = frame[y - roi_size:y + roi_size, x - roi_size:x + roi_size]
            hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            brightness = np.mean(hsv_roi[:, :, 2])

            # Check brightness
            if brightness < 100:
                all_correct = False
                continue

            # Check color
            correct = False
            for color_name, (lower, upper) in COLOR_RANGES.items():
                mask = cv2.inRange(hsv_roi, np.array(lower), np.array(upper))
                if np.count_nonzero(mask) > 0:
                    if color_name == expected_color:
                        light_status[label]["checked"] = True
                        light_status[label]["success"] = True
                        correct = True
                    else:
                        light_status[label]["wrong"] = True
                    break

            if not correct:
                all_correct = False

    # If all lights are correct and checked, play success sound, show message, and reset
    if all_correct and all(status["checked"] for status in light_status.values()):
        play_success_sound()
        show_success_message(canvas)
        time.sleep(3)  # 3-second delay
        reset_test(layout)

def overlay_status(frame, layout):
    """Overlay the status on the frame."""
    text_x, text_y = 10, 30
    text_spacing = 25

    for label, data in CIRCUIT_LAYOUTS[layout].items():
        if light_status[label]["success"]:
            status_icon = "Success"
            text_color = (0, 255, 0)
            circle_color = (0, 255, 0)
        elif light_status[label]["wrong"]:
            status_icon = "Failed"
            text_color = (0, 0, 255)
            circle_color = (0, 0, 255)
        else:
            status_icon = "--"
            text_color = (255, 255, 255)
            circle_color = (255, 0, 0)

        text = f"{label}: {status_icon}"
        cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1)
        text_y += text_spacing

        x, y = circles[label]["x"], circles[label]["y"]
        cv2.circle(frame, (x, y), 10, circle_color, 2)


def make_circles_draggable(canvas):
    """Make the circles draggable on the canvas."""
    def on_click(event):
        for label, data in circles.items():
            x, y = data["x"], data["y"]
            if abs(event.x - x) <= 10 and abs(event.y - y) <= 10:
                canvas.current_circle = label
                break

    def on_drag(event):
        if hasattr(canvas, "current_circle") and canvas.current_circle:
            label = canvas.current_circle
            circles[label]["x"], circles[label]["y"] = event.x, event.y
            canvas.coords(
                circles[label]["id"],
                event.x - 10, event.y - 10, event.x + 10, event.y + 10
            )

    def on_release(event):
        if hasattr(canvas, "current_circle"):
            canvas.current_circle = None

    canvas.bind("<Button-1>", on_click)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)

def start_detection(layout, canvas):
    """Start the detection loop."""
    update_circles(layout, canvas)
    reset_test(layout)
    load_positions(layout)
    make_circles_draggable(canvas)

    def detection_loop():
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.resize(frame, (1280, 720))
            frame = draw_frame(frame)
            detect_lights(frame, layout, canvas)  # Pass canvas here
            overlay_status(frame, layout)

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            tk_image = ImageTk.PhotoImage(image=img)

            canvas.create_image(0, 0, anchor=tk.NW, image=tk_image)
            canvas.tk_image = tk_image

        cap.release()

    threading.Thread(target=detection_loop, daemon=True).start()
