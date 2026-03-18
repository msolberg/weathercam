import cv2
import boto3
import time
from datetime import datetime
import os

# --- Configuration ---
BUCKET_NAME = "your-unique-bucket-name"
INTERVAL = 10  # Seconds
SKIP_FRAMES = 20 # To allow auto-exposure to settle

# Initialize S3 client
s3 = boto3.client('s3')

def capture_and_upload():
    # 1. Initialize camera
    # 0 is usually the default USB cam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    try:
        # 2. Set resolution (optional, check NexiGo N60 supported modes)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

        # 3. Warm up the camera (The "Skip" logic)
        for _ in range(SKIP_FRAMES):
            cap.read()

        # 4. Capture the actual frame
        ret, frame = cap.read()
        
        if ret:
            # Create a unique filename
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            local_file = f"/tmp/image_{timestamp}.jpg"
            s3_key = f"captures/image_{timestamp}.jpg"

            # Save locally to RAM disk (/tmp)
            cv2.imwrite(local_file, frame)

            # 5. Upload to S3
            s3.upload_file(local_file, BUCKET_NAME, s3_key)
            print(f"Successfully uploaded {s3_key}")

            # Clean up local file
            os.remove(local_file)
        else:
            print("Error: Could not read frame.")

    finally:
        # Always release the camera so other processes can use it
        cap.release()

if __name__ == "__main__":
    print("Starting webcam monitor...")
    while True:
        capture_and_upload()
        time.sleep(INTERVAL)
