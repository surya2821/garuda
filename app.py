from flask import Flask, Response, render_template, request, jsonify
import cv2

app = Flask(__name__)

# Video feed setup
camera = cv2.VideoCapture(0)  # Use 0 for the default camera

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/log_location', methods=['POST'])
def log_location():
    data = request.json
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    print(f"Live Location: Latitude {latitude}, Longitude {longitude}")
    return jsonify({"message": "Location logged successfully!"})

if __name__ == "__main__":
    app.run(debug=True)
