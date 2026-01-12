"""Core bot logic for real-time note detection and key automation"""

import mss
import numpy as np
import cv2
import time
from pynput.keyboard import Controller

from config import *


def run_bot(hit_zone, lower_color, upper_color):
    lane_width = hit_zone["width"] // 4
    key_pressed = [False] * 4
    note_press_time = [0] * 4
    is_holder = [False] * 4
    last_color_seen_time = [0] * 4
    holder_tail_bottom = [0] * 4
    
    keyboard = Controller()
    
    print(f"\nACTIVE BOT MODE (Tap + Holder Support)")
    print(f"HOLDER_THRESHOLD={HOLDER_THRESHOLD}ms, HOLDER_TAIL_GONE_TIME={HOLDER_TAIL_GONE_TIME}ms")
    print("Press Ctrl+C to stop.")
    
    with mss.mss() as sct:
        try:
            while True:
                current_time = time.time() * 1000
                img = np.array(sct.grab(hit_zone))
                hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
                color_mask = cv2.inRange(hsv, lower_color, upper_color)
                
                for i in range(4):
                    x_start = i * lane_width
                    x_end = (i + 1) * lane_width
                    
                    lane_mask = color_mask[:, x_start:x_end]
                    hit_zone_start = max(0, hit_zone["height"] - HIT_ZONE_SIZE)
                    hit_zone_mask = lane_mask[hit_zone_start:, :]
                    
                    note_detected = np.any(hit_zone_mask)
                    
                    if note_detected:
                        last_color_seen_time[i] = current_time
                        
                        colored_rows = np.where(np.any(hit_zone_mask, axis=1))[0]
                        if len(colored_rows) > 0:
                            holder_tail_bottom[i] = hit_zone_start + colored_rows[-1]
                        
                        if not key_pressed[i]:
                            keyboard.press(KEYS[i])
                            key_pressed[i] = True
                            note_press_time[i] = current_time
                            is_holder[i] = False
                        else:
                            time_held = current_time - note_press_time[i]
                            if time_held > HOLDER_THRESHOLD:
                                is_holder[i] = True
                    else:
                        if key_pressed[i]:
                            time_since_last_color = current_time - last_color_seen_time[i]
                            
                            if is_holder[i]:
                                if time_since_last_color > HOLDER_TAIL_GONE_TIME:
                                    keyboard.release(KEYS[i])
                                    key_pressed[i] = False
                                    is_holder[i] = False
                            else:
                                if time_since_last_color > KEY_HOLD_TIME:
                                    keyboard.release(KEYS[i])
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
            for i in range(4):
                keyboard.release(KEYS[i])
