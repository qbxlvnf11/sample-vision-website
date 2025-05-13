import cv2
import time
import threading

from threads import latest_frames, locks

# Generator function to stream frames for a specific camera
def generate_frames(camera_id):
    """Continuously yield frames in MJPEG format for a specific camera"""
    while True:
        frame_bytes = None
        # Get latest frame (thread-safe)
        with locks[camera_id]:
            if camera_id in latest_frames and latest_frames[camera_id]:
                 frame_bytes = latest_frames[camera_id]

        if frame_bytes:
            # Send frame in MJPEG format
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        else:
            # No frame available yet or an error occurred
            time.sleep(0.1)  # Wait a bit

        # Control streaming rate (prevent overloading browser/network)
        time.sleep(0.05)  # Target around 20 FPS; adjust as needed
