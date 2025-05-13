import cv2
import time
import threading

from threads import latest_frames, locks, stop_event

# Background thread function to capture stream from each camera
def capture_thread_func(camera_id, rtsp_url):
    global latest_frames
    cap = None
    print(f"[{camera_id}] Capture thread started for {rtsp_url}")

    while not stop_event.is_set():
        try:
            # Attempt to reconnect if not connected or disconnected
            if cap is None or not cap.isOpened():
                print(f"[{camera_id}] Connecting to {rtsp_url}...")
                # Explicitly use CAP_FFMPEG and enforce TCP (already set via env variable)
                cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
                if not cap.isOpened():
                    print(f"[{camera_id}] Error: Could not open stream. Retrying in 5 seconds...")
                    # Wait a bit before retrying on failure
                    time.sleep(5)
                    cap = None  # Set to None to trigger retry in next loop
                    continue
                else:
                    print(f"[{camera_id}] Stream connected successfully.")

            # Read a frame
            ret, frame = cap.read()

            # If frame read fails
            if not ret:
                print(f"[{camera_id}] Error: Failed to read frame. Reconnecting...")
                cap.release()
                cap = None  # Release and retry in next loop
                time.sleep(1)
                continue

            # Encode frame to JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                # Encoding failed; try next frame
                continue

            frame_bytes = buffer.tobytes()

            # Update latest frame (thread-safe)
            with locks[camera_id]:
                latest_frames[camera_id] = frame_bytes

        except Exception as e:
            print(f"[{camera_id}] Exception in capture thread: {e}")
            if cap:
                cap.release()
            cap = None
            # Wait before retrying after exception
            time.sleep(5)

        # Optional short delay to reduce CPU usage
        # time.sleep(0.01) # 10ms delay

    # Release resources when thread stops
    if cap:
        cap.release()
    print(f"[{camera_id}] Capture thread stopped.")
