import cv2
import numpy as np
import requests
import pyttsx3
import time
from ultralytics import YOLO

# Initialize TTS engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Adjust speaking rate if needed

# Set your ESP32's IP address and endpoint for the camera stream.
esp_ip = "192.168.1.105"  # Replace with your ESP32's IP
camera_url = f"http://192.168.1.105/camera"

# Load your YOLOv11x model (ensure 'yolov11x.pt' exists at the given path)
model = YOLO('yolo11x.pt')

# Optionally load class labels (for example, from a coco.names file)
classes = []
with open("/Users/prathameshbandal/Downloads/coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]
    
# Dictionary to track the last time a label was spoken (to avoid repetition)
last_spoken = {}
SPEAK_COOLDOWN = 5  # seconds

def speak_label(label):
    """Speak the label if it hasn't been spoken recently."""
    current_time = time.time()
    if label in last_spoken:
        if current_time - last_spoken[label] < SPEAK_COOLDOWN:
            return  # Skip speaking if within cooldown period
    last_spoken[label] = current_time
    engine.say(label)
    engine.runAndWait()

def get_esp32_image(url):
    """
    Fetches the image from the ESP32 camera endpoint.
    Assumes that the ESP32 is streaming JPEG images.
    """
    try:
        response = requests.get(url, timeout=5)
        img_arr = np.frombuffer(response.content, dtype=np.uint8)
        img = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)
        return img
    except Exception as e:
        print("Error fetching image:", e)
        return None

while True:
    # Fetch the latest frame from the ESP32 stream
    frame = get_esp32_image(camera_url)
    if frame is None:
        continue

    # Run YOLOv11x inference on the frame
    results = model(frame)
    
    # Create a copy of the frame for annotations
    annotated_frame = frame.copy()

    # Process detections if any
    if results and results[0].boxes is not None:
        for box in results[0].boxes:
            # Extract bounding box coordinates (assumed to be in xyxy format)
            coords = box.xyxy[0].cpu().numpy().astype(int)
            x1, y1, x2, y2 = coords
            confidence = float(box.conf[0])
            class_id = int(box.cls[0])
            # If no classes provided, use class id as label; otherwise use the class name
            label = str(class_id) if classes is None else classes[class_id]
            text = f"{label}: {confidence:.2f}"
            
            # Draw bounding box (with thin line)
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), thickness=1)
            # Draw label with a smaller font for low resolution images
            cv2.putText(annotated_frame, text, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX,
                        0.3, (0, 255, 0), thickness=1, lineType=cv2.LINE_AA)
            
            # Speak the detected label
            speak_label(label)
    
    # Display the annotated frame
    cv2.imshow("ESP32 YOLOv11x Detection with TTS", annotated_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
