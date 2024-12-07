from flask import Flask, render_template, Response, jsonify
import cv2
import threading
import time

app = Flask(__name__)

# Default coordinates for the initial location
DEFAULT_LATITUDE = 16.454231
DEFAULT_LONGITUDE = 80.604233

# Global variables for telemetry
current_lat = DEFAULT_LATITUDE
current_lon = DEFAULT_LONGITUDE

# OpenCV Video Capture
NORMAL_CAMERA_INDEX = 0
camera = cv2.VideoCapture(NORMAL_CAMERA_INDEX)  # Adjust index for your camera


def generate_video_feed():
    """Video stream generator for MJPEG."""
    while True:
        ret, frame = camera.read()
        if not ret:
            continue
        # Encode the frame as JPEG
        _, jpeg = cv2.imencode('.jpg', frame)
        frame_data = jpeg.tobytes()
        # Yield the frame in MJPEG format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Route for video feed."""
    return Response(generate_video_feed(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html', lat=current_lat, lon=current_lon)


@app.route('/update_telemetry', methods=['GET'])
def update_telemetry():
    """API to get the current telemetry."""
    return jsonify({'lat': current_lat, 'lon': current_lon})


@app.route('/set_location/<float:lat>/<float:lon>', methods=['POST'])
def set_location(lat, lon):
    """API to update the map location."""
    global current_lat, current_lon
    current_lat, current_lon = lat, lon
    return jsonify({'status': 'success', 'lat': current_lat, 'lon': current_lon})


def video_stream_thread():
    """Thread for capturing video with OpenCV."""
    while True:
        _, frame = camera.read()
        time.sleep(0.03)


if __name__ == '__main__':
    # Start the video stream in a separate thread
    threading.Thread(target=video_stream_thread, daemon=True).start()

    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
