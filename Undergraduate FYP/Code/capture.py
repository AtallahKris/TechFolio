import cv2
import os
import time
import threading
from datetime import datetime
from queue import Queue

OUTPUT_DIR = 'captured_c_COLOR_images/'
CAMERA_INDEX = 0
CAPTURE_DURATION = 180
RESOLUTION_WIDTH = 1280
RESOLUTION_HEIGHT = 720
TARGET_FPS = 5

def initialize_camera():
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print(f"Error: Could not open camera with index {CAMERA_INDEX}")
        return None

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, RESOLUTION_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, RESOLUTION_HEIGHT)
    
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    
    cap.set(cv2.CAP_PROP_FPS, TARGET_FPS)
    
    print(f"Camera initialized. Resolution: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
    print(f"Camera FPS: {cap.get(cv2.CAP_PROP_FPS)}")
    
    return cap

def save_image_worker(queue):
    while True:
        item = queue.get()
        if item is None:
            queue.task_done()
            break
            
        frame, filename = item
        try:
            cv2.imwrite(filename, frame)
            print(f"Saved: {filename}")
        except Exception as e:
            print(f"Error saving image {filename}: {e}")
        queue.task_done()

def capture_images(cap):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    print(f"Starting image capture. Press 'q' to stop early.")
    
    save_queue = Queue(maxsize=100)
    save_thread = threading.Thread(target=save_image_worker, args=(save_queue,))
    save_thread.daemon = True
    save_thread.start()
    
    capture_count = 0
    start_time = time.time()
    last_save_time = start_time
    save_interval = 1.0 / 5

    try:
        cv2.namedWindow("Camera Feed", cv2.WINDOW_NORMAL)
        
        while (time.time() - start_time) < CAPTURE_DURATION:
            ret, frame = cap.read()
            if not ret:
                continue
                
            cv2.imshow("Camera Feed", frame)
            
            current_time = time.time()
            if current_time - last_save_time >= save_interval:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                filename = os.path.join(OUTPUT_DIR, f"capture_{timestamp}.png")
                save_queue.put((frame.copy(), filename))
                capture_count += 1
                last_save_time = current_time

            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Capture stopped by user.")
                break
    finally:
        save_queue.put(None)
        save_thread.join()
        
        print(f"Capture finished. Total images requested: {capture_count}")
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    print("Initializing camera...")
    camera = initialize_camera()
    if camera:
        print("Starting capture...")
        capture_images(camera)
    else:
        print("Camera initialization failed.")
