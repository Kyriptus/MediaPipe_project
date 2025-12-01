import cv2
import numpy as np
import mediapipe as mp
import pyautogui
import sys
#import time
import math

screen_width, screen_height = pyautogui.size()
pyautogui.FAILSAFE = True

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
mp_draw = mp.solutions.drawing_utils

SMOOTHING_FACTOR = 0.7
CURSOR_SENSITIVITY = 1.5
PINCH_THRESHOLD = 0.07

SCROLL_NUDGE_THRESHOLD = 0.03
SCROLL_LOCK_SPEED = 30

smooth_x, smooth_y = 0.5 * screen_width, 0.5 * screen_height
last_gesture = None
last_pos = None
is_dragging = False
scroll_lock_direction = None

def get_hand_landmarks(frame, frame_rgb):
    try:
        results = hands.process(frame_rgb)
        
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            return hand_landmarks.landmark
            
    except Exception as e:
        print(f"Error in hand processing: {e}")
        return None
        
    return None

def classify_gesture(landmarks):
    tip_ids = [mp_hands.HandLandmark.INDEX_FINGER_TIP,
               mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
               mp_hands.HandLandmark.RING_FINGER_TIP,
               mp_hands.HandLandmark.PINKY_TIP]
    
    mcp_ids = [mp_hands.HandLandmark.INDEX_FINGER_MCP,
               mp_hands.HandLandmark.MIDDLE_FINGER_MCP,
               mp_hands.HandLandmark.RING_FINGER_MCP,
               mp_hands.HandLandmark.PINKY_MCP]
               
    thumb_tip_id = mp_hands.HandLandmark.THUMB_TIP
    thumb_mcp_id = mp_hands.HandLandmark.THUMB_MCP
    index_tip_id = mp_hands.HandLandmark.INDEX_FINGER_TIP

    
    fingers_up = []
    for i in range(len(tip_ids)):
        tip = landmarks[tip_ids[i]]
        mcp = landmarks[mcp_ids[i]]
        if tip.y < mcp.y:
            fingers_up.append(True)
        else:
            fingers_up.append(False)
    num_fingers_up = sum(fingers_up)

    is_thumb_out = landmarks[thumb_tip_id].x < landmarks[thumb_mcp_id].x
    
    pinch_distance = math.hypot(landmarks[thumb_tip_id].x - landmarks[index_tip_id].x, 
                                 landmarks[thumb_tip_id].y - landmarks[index_tip_id].y)
    is_pinching = pinch_distance < PINCH_THRESHOLD


    if (num_fingers_up == 3 and not fingers_up[0] and
        fingers_up[1] and fingers_up[2] and fingers_up[3] and
        is_pinching):
        return "OK_SIGN"

    if num_fingers_up == 4 and is_thumb_out:
        return "OPEN_PALM"

    if num_fingers_up == 4 and not is_thumb_out:
        return "FOUR_FINGERS"

    if num_fingers_up == 1 and fingers_up[0]:
        return "ONE_FINGER"
        
    if num_fingers_up == 2 and fingers_up[0] and fingers_up[1]:
        return "TWO_FINGERS"
        
    if num_fingers_up == 3 and fingers_up[0] and fingers_up[1] and fingers_up[2]:
        return "THREE_FINGERS"

    if num_fingers_up == 0:
        if is_pinching:
            return "PINCH_DRAG"
        else:
            return "FIST"

    return "IDLE"

def main():
    global smooth_x, smooth_y, last_gesture, last_pos, is_dragging, scroll_lock_direction

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        sys.exit()

    print("--- MediaPipe Gesture Controller (Final v10 - Scroll Lock) ---")
    print("GESTURES:")
    print("  - 'ONE FINGER' (Point): Move the cursor.")
    print("  - 'PINCH_DRAG': Hold and drag a file.")
    print("  - 'OPEN_PALM': Click the mouse (fires once).")
    print("  - 'TWO_FINGERS': Nudge UP/DOWN to 'Lock' continuous scroll.")
    print("  - 'THREE_FINGERS': Switch Tab (Win+Tab) (fires once).")
    print("  - 'FOUR_FINGERS': Show Desktop (Win+D) (fires once).")
    print("  - 'FIST' / 'OK_SIGN': Idle (and stops scroll).")
    print("\n!!! SAFETY FAIL-SAFE ENABLED !!!")
    print("To quit, press 'q' OR slam your mouse to the TOP-LEFT corner.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        landmarks = get_hand_landmarks(frame, frame_rgb)
        
        gesture_text = "No Hand Detected"
        current_gesture = None

        if landmarks:
            current_gesture = classify_gesture(landmarks)
            gesture_text = current_gesture
            
            if current_gesture == "PINCH_DRAG":
                if not is_dragging:
                    pyautogui.mouseDown()
                    is_dragging = True
                    print("DRAG: Mouse Down")
            elif is_dragging:
                pyautogui.mouseUp()
                is_dragging = False
                print("DRAG: Mouse Up (Drop)")

            
            if current_gesture == "ONE_FINGER" or (current_gesture == "PINCH_DRAG" and is_dragging):
                scroll_lock_direction = None
                tip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                
                map_x = np.interp(tip.x, [0.0, 1.0], [0 - (screen_width * (CURSOR_SENSITIVITY - 1)), 
                                                     screen_width * CURSOR_SENSITIVITY])
                map_y = np.interp(tip.y, [0.0, 1.0], [0 - (screen_height * (CURSOR_SENSITIVITY - 1)), 
                                                     screen_height * CURSOR_SENSITIVITY])
                
                smooth_x = (smooth_x * SMOOTHING_FACTOR) + (map_x * (1 - SMOOTHING_FACTOR))
                smooth_y = (smooth_y * SMOOTHING_FACTOR) + (map_y * (1 - SMOOTHING_FACTOR))
                
                pyautogui.moveTo(smooth_x, smooth_y)
                last_pos = None

            elif current_gesture == "OPEN_PALM" and last_gesture != "OPEN_PALM":
                scroll_lock_direction = None
                pyautogui.click()
                print("CLICK!")
                last_pos = None 

            elif current_gesture == "TWO_FINGERS":
                current_y = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP].y
                
                if scroll_lock_direction is None:
                    if last_pos is None:
                        last_pos = (0, current_y)
                    
                    delta_y = current_y - last_pos[1]
                    
                    if abs(delta_y) > SCROLL_NUDGE_THRESHOLD: 
                        if delta_y > 0:
                            scroll_lock_direction = "DOWN"
                            print("SCROLL LOCK: ON (DOWN)")
                        else:
                            scroll_lock_direction = "UP"
                            print("SCROLL LOCK: ON (UP)")
                        last_pos = (0, current_y)
                
                if scroll_lock_direction == "UP":
                    pyautogui.scroll(SCROLL_LOCK_SPEED)
                elif scroll_lock_direction == "DOWN":
                    pyautogui.scroll(-SCROLL_LOCK_SPEED)

            
            elif current_gesture == "THREE_FINGERS" and last_gesture != "THREE_FINGERS":
                scroll_lock_direction = None
                pyautogui.hotkey('win', 'tab')
                print("ACTION: Win+Tab")
                last_pos = None 
            
            elif current_gesture == "FOUR_FINGERS" and last_gesture != "FOUR_FINGERS":
                scroll_lock_direction = None
                pyautogui.hotkey('win', 'd')
                print("ACTION: Show Desktop (Win+D)")
                last_pos = None

            elif current_gesture in ("FIST", "OK_SIGN", "IDLE"):
                scroll_lock_direction = None
                last_pos = None
            
        cv2.putText(frame, gesture_text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 
                    1, (0, 0, 255), 2, cv2.LINE_AA)
        cv2.imshow("MediaPipe Gesture Controller", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
        last_gesture = current_gesture

    print("Cleaning up and closing...")
    cap.release()
    cv2.destroyAllWindows()
    sys.exit()

if __name__ == "__main__":
    main()