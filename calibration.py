"""Interactive calibration tools for osu!mania bot setup"""

import cv2
import numpy as np
import time


def take_calibration_screenshot(sct, osu_win):
    print("\n=== TAKING SCREENSHOT ===")
    print("Make sure osu is PLAYING with notes visible")
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
    
    cv2.namedWindow("Color Picker - Click on a note in the screenshot")
    cv2.setMouseCallback("Color Picker - Click on a note in the screenshot", mouse_callback)
    
    print("Click on a note in the screenshot to get its exact color")
    print("Press SPACE when done picking")
    
    while True:
        cv2.imshow("Color Picker - Click on a note in the screenshot", display)
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord(' '):
            if picked_color["h"] is not None:
                cv2.destroyAllWindows()
                return picked_color
            else:
                print("No color picked yet")


def select_roi(img):
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
        
        if state["x1"] is not None and state["x2"] is not None:
            x1, y1 = min(state["x1"], state["x2"]), min(state["y1"], state["y2"])
            x2, y2 = max(state["x1"], state["x2"]), max(state["y1"], state["y2"])
            cv2.rectangle(display, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(display, f"{x2-x1}x{y2-y1}", (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        cv2.imshow("Select Hit Zone - Click and drag to select", display)
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord(' '):
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
        elif key == ord('r'):
            state = {"x1": None, "y1": None, "x2": None, "y2": None, "selecting": False}
