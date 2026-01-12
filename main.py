"""osumania Auto-Bot - Main entry point"""

import mss
import numpy as np
import cv2
import pygetwindow as gw
import time

from calibration import take_calibration_screenshot, pick_color, select_roi
from bot import run_bot
from config import TOLERANCE_H, TOLERANCE_S, TOLERANCE_V


def main():
    windows = gw.getWindowsWithTitle('osu!')
    if not windows:
        print("Can't find game, make sure it is running")
        return
    
    osu_win = windows[0]
    time.sleep(0.5)

    with mss.mss() as sct:
        # Step 1: Screenshot
        print("\n=== STEP 1: SCREENSHOT ===")
        calibration_img = take_calibration_screenshot(sct, osu_win)
        
        # Step 2: Color calibration
        print("\n=== STEP 2: COLOR CALIBRATION ===")
        picked = pick_color(calibration_img)
        h, s, v = picked["h"], picked["s"], picked["v"]
        print(f"Picked color: H={h}, S={s}, V={v}")
        
        lower_color = np.array([max(0, h - TOLERANCE_H), max(0, s - TOLERANCE_S), max(0, v - TOLERANCE_V)])
        upper_color = np.array([min(180, h + TOLERANCE_H), min(255, s + TOLERANCE_S), min(255, v + TOLERANCE_V)])
        
        print(f"Using HSV range: H({lower_color[0]}-{upper_color[0]}), S({lower_color[1]}-{upper_color[1]}), V({lower_color[2]}-{upper_color[2]})")
        
        # Step 3: Hit zone selection
        print("\n=== STEP 3: SELECT HIT ZONE ===")
        roi = select_roi(calibration_img)
        
        hit_zone = {
            "left": osu_win.left + roi["x1"],
            "top": osu_win.top + roi["y1"],
            "width": roi["width"],
            "height": roi["height"]
        }
        
        print(f"Hit zone selected: {hit_zone}")
        print("\n=== STEP 4: START BOT ===")
        print("Click back into osu and make sure game is PLAYING")
        print("Bot will start in 5 seconds...")
        
        for countdown in range(5, 0, -1):
            print(f"Starting in {countdown}...", end='\r', flush=True)
            time.sleep(1)
        print("STARTING BOT!        \n")
        
        # Step 4: Run bot
        run_bot(hit_zone, lower_color, upper_color)

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
