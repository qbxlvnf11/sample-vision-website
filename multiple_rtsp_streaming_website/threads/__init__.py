import threading

# --- Configuration ---
# Dictionary to store the latest frame from each camera (in JPEG byte format)
latest_frames = {}
# Locks for thread-safe frame access
locks = {}
# Event object to signal threads to stop
stop_event = threading.Event()
# ----------------