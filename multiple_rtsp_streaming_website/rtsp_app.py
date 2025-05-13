import argparse
import yaml

import os
# Set environment variable before loading OpenCV (force TCP transport)
os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'rtsp_transport;tcp'

import cv2
import time
import threading
from flask import Flask, render_template, Response

from threads import latest_frames, locks, stop_event
from threads.capture_threads import capture_thread_func
from utils import load_config
from threads.utils import generate_frames

# Initialize Flask app
app = Flask(__name__)

def get_args():
    
    parser = argparse.ArgumentParser()
    # parser.add_argument('--server_port', type=int, default=8877)
    parser.add_argument('--config', type=str, required=True)

    return parser.parse_args()

# Route for main page
@app.route('/')
def index():
    """Render main page that displays CCTV feeds."""
    num_cameras = len(camera_urls)
    # Pass camera count to template
    return render_template('index.html', camera_urls=camera_urls, num_cameras=num_cameras)

# Route to serve MJPEG stream for each camera
@app.route('/video_feed/<int:camera_id>')
def video_feed(camera_id):
    """Return MJPEG stream as a Flask Response."""
    if camera_id < 0 or camera_id >= len(camera_urls):
        return "Invalid camera ID", 404  # Handle invalid camera ID

    # Return streaming response using the frame generator
    return Response(generate_frames(camera_id),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# Run the application
if __name__ == '__main__':
    
    args = get_args()

    configs = load_config(args.config)
    print(configs)

    global camera_urls
    camera_urls = configs['cameras']

    # Initialize frame storage and locks for each camera
    for i in range(len(camera_urls)):
        latest_frames[i] = None
        locks[i] = threading.Lock()

    # Create and start capture threads for each camera
    threads = []
    for i, url in enumerate(camera_urls):
        thread = threading.Thread(target=capture_thread_func, args=(i, url), daemon=True)
        threads.append(thread)
        thread.start()

    print("Starting Flask web server...")
    try:
        # Run Flask app (host='0.0.0.0' allows external access, threaded=True enables multithreading)
        # debug=True helps with development but should be False in production
        app.run(host=configs['app']['host'], port=configs['app']['port'], debug=configs['app']['debug'], threaded=True)
    except KeyboardInterrupt:
        print("Shutdown requested by user...")
    finally:
        # Signal threads to stop on shutdown
        print("Signaling capture threads to stop...")
        stop_event.set()
        # (Optional) Wait for all threads to finish
        # print("Waiting for threads to finish...")
        # for t in threads:
        #     t.join()
        print("Shutdown complete.")
