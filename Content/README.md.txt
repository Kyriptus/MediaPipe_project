# AI Gesture Controller (MediaPipe + OpenCV)

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Vision-orange)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green)

A touch-free virtual mouse and gesture control system built with Python, OpenCV, and MediaPipe. This project allows you to control your mouse cursor, click, drag-and-drop, and perform system shortcuts (like Alt-Tab or Show Desktop) using only hand gestures captured by your webcam.

## ?? Features

* **Cursor Control:** Smooth cursor movement using the Index Finger.
* **Smart Clicking:** "Open Palm" gesture triggers a left click (debounced to prevent double-clicking).
* **Drag & Drop:** Pinch your thumb and index finger to grab and move files or windows.
* **Intelligent Scroll Lock:** Use two fingers to nudge the screen up or down, engaging a continuous auto-scroll mode until you reset.
* **Productivity Shortcuts:**
    * **Three Fingers:** Triggers `Win + Tab` (Task View).
    * **Four Fingers:** Triggers `Win + D` (Show Desktop).
* **Smoothing Algorithms:** Includes jitter reduction and coordinate interpolation for a smooth user experience.
* **Fail-Safe:** Built-in safety mechanisms to instantly kill the program if control is lost.

## ??? Prerequisites

* Python 3.7 or higher
* A working webcam

## ?? Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/yourusername/ai-gesture-controller.git](https://github.com/yourusername/ai-gesture-controller.git)
    cd ai-gesture-controller
    ```

2.  **Install dependencies:**
    ```bash
    pip install opencv-python mediapipe pyautogui numpy
    ```

3.  **Run the application:**
    ```bash
    python main.py
    ```

## ?? Gesture Guide

| Hand Shape | Action | Description |
| :--- | :--- | :--- |
| **Index Finger Up** | **Move Cursor** | Point to move the mouse. (Tip: Keep other fingers down). |
| **Pinch (Index+Thumb)** | **Drag / Hold** | Bring thumb and index together to click-and-hold. Release to drop. |
| **Open Palm (5 Fingers)**| **Left Click** | Quickly open your hand to click. |
| **Two Fingers Up** | **Scroll Lock** | Move hand Up/Down slightly to start auto-scrolling. |
| **Three Fingers Up** | **Task View** | Triggers `Win + Tab` to switch applications. |
| **Four Fingers Up** | **Show Desktop** | Triggers `Win + D` to minimize all windows. |
| **Fist / OK Sign** | **Stop / Idle** | Stops scrolling and resets the cursor tracking. |

## ?? Configuration

You can tweak the sensitivity variables at the top of `main.py` to fit your setup:

* `CURSOR_SENSITIVITY`: Increase this if you want the mouse to move faster with smaller hand movements.
* `SMOOTHING_FACTOR`: Adjust this to balance between cursor responsiveness and jitter reduction.
* `SCROLL_LOCK_SPEED`: Controls how fast the page scrolls when in "Scroll Lock" mode.

## ?? Safety Fail-Safe

If the mouse control behaves unexpectedly, you can immediately kill the program using one of two methods:
1.  **Corner Fail-Safe:** Slam the mouse cursor into the very **Top-Left** corner of your screen.
2.  **Keyboard:** Press **`q`** while the webcam window is focused.

## ?? License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
