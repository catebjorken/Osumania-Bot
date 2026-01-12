"""Configuration settings for osu!mania auto-bot"""

# Key Input Configuration
KEYS = ['z', 'x', '.', '/']  # Keys mapped to lanes (left to right)

# Timing Configuration
KEY_HOLD_TIME = 0.2  # Milliseconds to hold regular tap notes before releasing
HOLDER_THRESHOLD = 100  # Milliseconds of continuous color detection to classify as holder note
HOLDER_TAIL_GONE_TIME = 1  # Milliseconds after color disappears to release holder notes

# Detection Configuration
HIT_ZONE_SIZE = 60  # Pixel height from hit line where notes are detected and pressed
TOLERANCE_H = 5  # HSV Hue tolerance range (+/-) for color matching
TOLERANCE_S = 30  # HSV Saturation tolerance range (+/-) for color matching
TOLERANCE_V = 30  # HSV Value/Brightness tolerance range (+/-) for color matching

# Debug Configuration
SHOW_DEBUG = False  # Display real-time vision window (impacts performance)
