import requests
import numpy as np
import cv2
import pyttsx3
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image

# Initialize TTS engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)

# Load BLIP-2 model
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large").to("cuda" if torch.cuda.is_available() else "cpu")

# ESP32 camera stream URL
esp_ip = "192.168.1.105"  # Replace with your ESP32's IP
camera_url = f"http://192.168.1.105/camera"

def get_esp32_image(url):
    """Fetches an image from ESP32 camera."""
    try:
        response = requests.get(url, timeout=5)
        img_arr = np.frombuffer(response.content, dtype=np.uint8)
        img = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)
        return img
    except Exception as e:
        print("Error fetching image:", e)
        return None

def generate_caption(image):
    """Generate a caption using BLIP-2 model."""
    image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    inputs = processor(image_pil, return_tensors="pt").to("cuda" if torch.cuda.is_available() else "cpu")
    output = model.generate(**inputs)
    caption = processor.decode(output[0], skip_special_tokens=True)
    return caption

def speak(text):
    """Convert text to speech."""
    engine.say(text)
    engine.runAndWait()

while True:
    # Capture frame from ESP32
    frame = get_esp32_image(camera_url)
    if frame is None:
        continue

    # Generate a description
    description = generate_caption(frame)
    print("Description:", description)

    # Speak the description
    speak(description)

    # Display frame
    cv2.imshow("ESP32 Live Stream", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
