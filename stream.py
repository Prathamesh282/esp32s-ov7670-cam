import serial
import numpy as np
import cv2

# Set correct port (Check using `ls /dev/tty.*` on macOS)
SERIAL_PORT = "/dev/cu.usbserial-0001"  # Change this to your actual ESP32 port
BAUD_RATE = 115200
IMG_WIDTH, IMG_HEIGHT = 160, 120  # Adjust according to the camera resolution

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

# Skip BMP header (54 bytes)
BMP_HEADER_SIZE = 54

while True:
    frame_data = ser.read(BMP_HEADER_SIZE + IMG_WIDTH * IMG_HEIGHT * 2)
    if len(frame_data) < BMP_HEADER_SIZE:
        continue  # Skip if incomplete frame

    img_data = np.frombuffer(frame_data[BMP_HEADER_SIZE:], dtype=np.uint16)
    img_data = img_data.reshape((IMG_HEIGHT, IMG_WIDTH))

    # Convert 16-bit RGB565 to 8-bit grayscale
    img_gray = (img_data >> 8).astype(np.uint8)

    cv2.imshow("ESP32 Camera Stream", img_gray)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

ser.close()
cv2.destroyAllWindows()
