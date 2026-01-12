import mss
import numpy as np
import cv2
import pygetwindow as gw
import time
from pathlib import Path
from pynput.keyboard import Controller, Key

def take_calibration_screenshot(sct, osu_win):
    """Take a screenshot while game is playing for calibration"""
    print("\n=== TAKING SCREENSHOT ===")
    print("Make sure osu! is PLAYING with notes visible")
    print("Screenshot will be taken in 5 seconds...")
    
    for countdown in range(5, 0, -1):
        print(f"Taking screenshot in {countdown}...", end='\r', flush=True)
        time.sleep(1)
    
    window_area = {
        "top": osu_win.top,
        "left": osu_win.left,
        "width": osu_win.width,
        "height": osu_win.height
    }
    
    img = np.array(sct.grab(window_area))
    print("Screenshot captured!\n")
    
    return img

def pick_color(img):
    """Click on a red note in the screenshot to get its exact HSV color"""
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    display = img.copy()
    picked_color = {"h": None, "s": None, "v": None}
    
    def mouse_callback(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            h, s, v = hsv_img[y, x]
            picked_color["h"] = int(h)
            picked_color["s"] = int(s)
            picked_color["v"] = int(v)
            print(f"Picked color at ({x}, {y}): H={h}, S={s}, V={v}")
    
    cv2.namedWindow("Color Picker - Click on a RED NOTE in the screenshot")
    cv2.setMouseCallback("Color Picker - Click on a RED NOTE in the screenshot", mouse_callback)
    
    print("CLICK ON A RED NOTE in the screenshot to get its exact color")
    print("Press SPACE when done picking")
    
    while True:
        cv2.imshow("Color Picker - Click on a RED NOTE in the screenshot", display)
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord(' '):
            if picked_color["h"] is not None:
                cv2.destroyAllWindows()
                return picked_color
            else:
                print("No color picked yet!")

def select_roi(img):
    """Interactive ROI selection on screenshot"""
    display = img.copy()
    state = {"x1": None, "y1": None, "x2": None, "y2": None, "selecting": False}
    
    def mouse_callback(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            state["x1"] = x
            state["y1"] = y
            state["selecting"] = True
        elif event == cv2.EVENT_MOUSEMOVE and state["selecting"]:
            state["x2"] = x
            state["y2"] = y
        elif event == cv2.EVENT_LBUTTONUP:
            state["x2"] = x
            state["y2"] = y
            state["selecting"] = False
    
    cv2.namedWindow("Select Hit Zone - Click and drag to select")
    cv2.setMouseCallback("Select Hit Zone - Click and drag to select", mouse_callback)
    
    print("Click and drag to select the hit zone area (where notes pass through)")
    print("Press SPACE to confirm, or 'r' to reset")
    
    while True:
        display = img.copy()
        
        # Draw selection rectangle if active
        if state["x1"] is not None and state["x2"] is not None:
            x1, y1 = min(state["x1"], state["x2"]), min(state["y1"], state["y2"])
            x2, y2 = max(state["x1"], state["x2"]), max(state["y1"], state["y2"])
            cv2.rectangle(display, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(display, f"{x2-x1}x{y2-y1}", (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        cv2.imshow("Select Hit Zone - Click and drag to select", display)
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord(' '):  # SPACE to confirm
            if state["x1"] is not None and state["x2"] is not None:
                x1, y1 = min(state["x1"], state["x2"]), min(state["y1"], state["y2"])
                x2, y2 = max(state["x1"], state["x2"]), max(state["y1"], state["y2"])
                cv2.destroyAllWindows()
                return {
                    "x1": x1,
                    "y1": y1,
                    "width": x2 - x1,
                    "height": y2 - y1
                }
        elif key == ord('r'):  # R to reset
            state = {"x1": None, "y1": None, "x2": None, "y2": None, "selecting": False}

def start_bot():
    windows = gw.getWindowsWithTitle('osu!')
    if not windows:
        print("Close the game and re-open it, I can't find it!")
        return
    
    osu_win = windows[0]
    time.sleep(0.5)

    with mss.mss() as sct:
        # Step 1: Take screenshot while game is playing
        print("\n=== STEP 1: SCREENSHOT ===")
        calibration_img = take_calibration_screenshot(sct, osu_win)
        
        # Step 2: Pick color from screenshot
        print("\n=== STEP 2: COLOR CALIBRATION ===")
        picked = pick_color(calibration_img)
        h, s, v = picked["h"], picked["s"], picked["v"]
        print(f"Picked color: H={h}, S={s}, V={v}")
        
        # Create HSV range with tolerance (MUCH TIGHTER to reduce false positives)
        tolerance_h = 5
        tolerance_s = 30
        tolerance_v = 30
        
        lower_color = np.array([max(0, h - tolerance_h), max(0, s - tolerance_s), max(0, v - tolerance_v)])
        upper_color = np.array([min(180, h + tolerance_h), min(255, s + tolerance_s), min(255, v + tolerance_v)])
        
        print(f"Using HSV range: H({lower_color[0]}-{upper_color[0]}), S({lower_color[1]}-{upper_color[1]}), V({lower_color[2]}-{upper_color[2]})")
        
        # Step 3: Select hit zone from screenshot
        print("\n=== STEP 3: SELECT HIT ZONE ===")
        roi = select_roi(calibration_img)
        
        # Convert relative coordinates to absolute screen coordinates
        hit_zone = {
            "left": osu_win.left + roi["x1"],
            "top": osu_win.top + roi["y1"],
            "width": roi["width"],
            "height": roi["height"]
        }
        
        print(f"Hit zone selected: {hit_zone}")
        print("\n=== STEP 4: START BOT ===")
        print("Click back into osu! and make sure game is PLAYING")
        print("Bot will start in 5 seconds...")
        
        # Countdown before starting
        for countdown in range(5, 0, -1):
            print(f"Starting in {countdown}...", end='\r', flush=True)
            time.sleep(1)
        print("STARTING BOT!        \n")
        
        keys = ['z', 'x', '.', '/']
        lane_width = hit_zone["width"] // 4
        key_pressed = [False] * 4
        note_press_time = [0] * 4  # When we first pressed the key
        is_holder = [False] * 4  # Whether current note is a holder
        last_color_seen_time = [0] * 4  # Last time we saw color in hit zone
        holder_tail_bottom = [0] * 4  # Lowest Y position of holder tail
        
        # CONFIG: Tap/Holder detection
        KEY_HOLD_TIME = 0.2  # milliseconds to hold regular taps
        HOLDER_THRESHOLD = 100  # ms of continuous color = it's a holder
        HOLDER_TAIL_GONE_TIME = 1  # ms of no color at bottom = holder ended
        HIT_ZONE_SIZE = 60  # pixels from hit line where we detect and press
        SHOW_DEBUG = False  # Set to True to see vision window (slows down bot)
        
        # Use pynput for MUCH faster key input
        keyboard = Controller()
        key_map = {'z': 'z', 'x': 'x', '.': '.', '/': '/'}
        
        print(f"\nACTIVE BOT MODE (Tap + Holder Support)")
        print(f"HOLDER_THRESHOLD={HOLDER_THRESHOLD}ms, HOLDER_TAIL_GONE_TIME={HOLDER_TAIL_GONE_TIME}ms")
        print("Bot running at max speed. Press Ctrl+C to stop.")
        
        try:
            while True:
                current_time = time.time() * 1000
                img = np.array(sct.grab(hit_zone))
                hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
                color_mask = cv2.inRange(hsv, lower_color, upper_color)
                
                # For each lane, detect if color is present in hit zone
                for i in range(4):
                    x_start = i * lane_width
                    x_end = (i + 1) * lane_width
                    
                    lane_mask = color_mask[:, x_start:x_end]
                    hit_zone_start = max(0, hit_zone["height"] - HIT_ZONE_SIZE)
                    hit_zone_mask = lane_mask[hit_zone_start:, :]
                    
                    note_detected = np.any(hit_zone_mask)
                    
                    if note_detected:
                        last_color_seen_time[i] = current_time
                        
                        # Find the bottommost (lowest Y) colored pixel in hit zone
                        colored_rows = np.where(np.any(hit_zone_mask, axis=1))[0]
                        if len(colored_rows) > 0:
                            holder_tail_bottom[i] = hit_zone_start + colored_rows[-1]  # Last row = bottom
                        
                        if not key_pressed[i]:
                            # New note detected, press key
                            keyboard.press(keys[i])
                            key_pressed[i] = True
                            note_press_time[i] = current_time
                            is_holder[i] = False
                        else:
                            # Already holding, check if it's a holder
                            time_held = current_time - note_press_time[i]
                            if time_held > HOLDER_THRESHOLD:
                                is_holder[i] = True
                    else:
                        # No note detected
                        if key_pressed[i]:
                            time_since_last_color = current_time - last_color_seen_time[i]
                            
                            if is_holder[i]:
                                # For holders, release quickly after color disappears
                                if time_since_last_color > HOLDER_TAIL_GONE_TIME:
                                    keyboard.release(keys[i])
                                    key_pressed[i] = False
                                    is_holder[i] = False
                            else:
                                # For taps, release after KEY_HOLD_TIME
                                if time_since_last_color > KEY_HOLD_TIME:
                                    keyboard.release(keys[i])
                                    key_pressed[i] = False
                
                if SHOW_DEBUG:
                    display_view = img.copy()
                    cv2.line(display_view, (0, hit_zone["height"]-5), (hit_zone["width"], hit_zone["height"]-5), (0, 0, 255), 3)
                    for j in range(1, 4):
                        cv2.line(display_view, (j * lane_width, 0), (j * lane_width, hit_zone["height"]), (0, 255, 0), 2)
                    cv2.imshow('Bot Vision', display_view)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
        except KeyboardInterrupt:
            print("\nBot stopped.")
        finally:
            # Cleanup - release all keys
            for i in range(4):
                keyboard.release(keys[i])

cv2.destroyAllWindows()
start_bot()