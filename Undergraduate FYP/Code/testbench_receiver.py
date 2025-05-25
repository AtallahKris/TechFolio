import os
import shutil
import time
import logging
import sys
from tqdm import tqdm

try:
    import decode
    import receive
    import clean
    import common
except ImportError as e:
    logging.error(f"Failed to import a required module: {e}. Ensure all script files (decode.py, receive.py, clean.py, common.py) are in the same directory or in PYTHONPATH.")
    exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[])

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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

RECEIVER_CAPTURED_c_COLOR_IMAGES_DIR = os.path.join(BASE_DIR, "c_COLOR_images")
RECEIVER_DECODED_CHUNKS_DIR = os.path.join(BASE_DIR, "decoded_chunks") 
RECEIVER_OUTPUT_DIR = os.path.join(BASE_DIR, "output")
SENDER_CHUNKS_DIR_FOR_HEADERS = os.path.join(BASE_DIR, "chunks")
ENCRYPTION_KEY = "your-secure-test-key123"

def setup_receiver_directories():
    logging.info("Setting up receiver directories (Device B)...")
    for dir_path in [RECEIVER_DECODED_CHUNKS_DIR, RECEIVER_OUTPUT_DIR]:
        if os.path.exists(dir_path):
            logging.info(f"Cleaning directory: {dir_path}")
            if hasattr(clean, 'delete_all_in_directory'):
                clean.delete_all_in_directory(dir_path)
                os.makedirs(dir_path, exist_ok=True)
            else:
                shutil.rmtree(dir_path)
                os.makedirs(dir_path, exist_ok=True)
        else:
            os.makedirs(dir_path, exist_ok=True)
    
    if not os.path.exists(RECEIVER_CAPTURED_c_COLOR_IMAGES_DIR):
        logging.warning(f"Captured c_COLOR images directory {RECEIVER_CAPTURED_c_COLOR_IMAGES_DIR} (Device B input) does not exist. Create it and populate with images from sender.")
        os.makedirs(RECEIVER_CAPTURED_c_COLOR_IMAGES_DIR, exist_ok=True)
    elif not os.listdir(RECEIVER_CAPTURED_c_COLOR_IMAGES_DIR):
        logging.warning(f"Captured c_COLOR images directory {RECEIVER_CAPTURED_c_COLOR_IMAGES_DIR} (Device B input) is empty. Decode process may not run correctly.")

    if not os.path.exists(SENDER_CHUNKS_DIR_FOR_HEADERS):
        logging.warning(f"Original sender's chunks directory {SENDER_CHUNKS_DIR_FOR_HEADERS} (for headers) does not exist on Device B. Decode might fail if headers are needed from original sender's chunk files.")

    logging.info("Receiver directory setup complete.")

def run_decode_process():
    logging.info(f"Running decode process (Device B): {RECEIVER_CAPTURED_c_COLOR_IMAGES_DIR} -> {RECEIVER_DECODED_CHUNKS_DIR}")
    if not os.path.exists(RECEIVER_CAPTURED_c_COLOR_IMAGES_DIR) or not os.listdir(RECEIVER_CAPTURED_c_COLOR_IMAGES_DIR):
        logging.warning(f"Captured c_COLOR images directory '{RECEIVER_CAPTURED_c_COLOR_IMAGES_DIR}' (Device B input) is empty or does not exist. Skipping decode process.")
        return True

    success = True
    image_files = sorted([f for f in os.listdir(RECEIVER_CAPTURED_c_COLOR_IMAGES_DIR) if os.path.isfile(os.path.join(RECEIVER_CAPTURED_c_COLOR_IMAGES_DIR, f)) and f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))])
    if not image_files:
        logging.warning(f"No image files found in {RECEIVER_CAPTURED_c_COLOR_IMAGES_DIR}. Skipping decode process.")
        return True
        
    logging.info(f"Found {len(image_files)} image(s) to decode.")
    total_images_to_decode = len(image_files)
    decoded_count = 0
    logging.info(f"Starting decoding of {total_images_to_decode} images...")

    for image_filename in tqdm(image_files, desc="Decoding Images ", unit="image", ncols=100, ascii=True, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]'):
        c_COLOR_image_path = os.path.join(RECEIVER_CAPTURED_c_COLOR_IMAGES_DIR, image_filename)
        reconstructed_chunk_filename = os.path.splitext(image_filename)[0] + ".bin"
        reconstructed_chunk_path = os.path.join(RECEIVER_DECODED_CHUNKS_DIR, reconstructed_chunk_filename)

        logging.info(f"Processing image {c_COLOR_image_path} to reconstruct chunk {reconstructed_chunk_path}...")
        try:
            decoded_payload_bytes = None
            if hasattr(decode, 'decode_c_COLOR_payload_from_image'):
                logging.info(f"Attempting to decode {c_COLOR_image_path} directly to memory...")
                decoded_payload_bytes = decode.decode_c_COLOR_payload_from_image(c_COLOR_image_path)
                if decoded_payload_bytes is None:
                    logging.error(f"decode_c_COLOR_payload_from_image failed for {c_COLOR_image_path} (returned None).")
                    success = False
                    continue
            elif hasattr(decode, 'decode_c_COLOR_to_chunk'): 
                logging.error("Fallback decode_c_COLOR_to_chunk not fully implemented in this split script version without knowing its exact signature/behavior.")
                success = False
                continue
            else:
                logging.error("Suitable decode function (e.g., 'decode_c_COLOR_payload_from_image') not found in decode.py.")
                success = False
                break 

            if decoded_payload_bytes is None:
                logging.error(f"Failed to obtain decoded payload for {c_COLOR_image_path}.")
                success = False
                continue

            original_chunk_for_header_filename = os.path.splitext(image_filename)[0] + ".bin"
            original_chunk_path = os.path.join(SENDER_CHUNKS_DIR_FOR_HEADERS, original_chunk_for_header_filename)

            if not os.path.exists(original_chunk_path):
                logging.error(f"Original chunk {original_chunk_path} (needed for header) not found in {SENDER_CHUNKS_DIR_FOR_HEADERS} on Device B. Cannot prepend header. Ensure sender's 'chunks' dir is available for receiver.")
                success = False
                continue
            
            header_len = getattr(common, '_CHUNK_FULL_HEADER_LEN', 26)
            with open(original_chunk_path, 'rb') as f_orig_chunk:
                original_header = f_orig_chunk.read(header_len)
                if len(original_header) < header_len:
                    logging.error(f"Original chunk {original_chunk_path} is too short to read a header of {header_len} bytes.")
                    success = False
                    continue

                if original_chunk_for_header_filename.startswith("M_"):
                    original_payload_bytes_for_check = f_orig_chunk.read()
                    if original_payload_bytes_for_check == decoded_payload_bytes:
                        logging.info(f"SUCCESS: Metadata payload for {original_chunk_for_header_filename} MATCHES original after decoding.")
                    else:
                        logging.error(f"CRITICAL ERROR: METADATA PAYLOAD MISMATCH for {original_chunk_for_header_filename}!")
                        success = False
            
            logging.info(f"Size of decoded payload for {reconstructed_chunk_filename}: {len(decoded_payload_bytes)} bytes.")
            full_reconstructed_chunk_data = original_header + decoded_payload_bytes

            with open(reconstructed_chunk_path, 'wb') as f_final_chunk:
                f_final_chunk.write(full_reconstructed_chunk_data)
            logging.info(f"Re-prepended header. Reconstructed chunk saved to {reconstructed_chunk_path}. Final size: {len(full_reconstructed_chunk_data)} bytes.")

        except Exception as e:
            logging.error(f"Error processing image {image_filename} (decode/header prepend): {e}", exc_info=True)
            success = False
            
    logging.info("Decode process complete.")
    return success

def run_receive_process():
    logging.info(f"Running receive process (Device B): {RECEIVER_DECODED_CHUNKS_DIR} -> {RECEIVER_OUTPUT_DIR}")
    if not os.path.exists(RECEIVER_DECODED_CHUNKS_DIR) or not os.listdir(RECEIVER_DECODED_CHUNKS_DIR):
        logging.warning("Receiver's decoded chunks directory is empty or does not exist. Skipping receive process.")
        return False 

    try:
        if hasattr(receive, 'reassemble_files'):
            chunk_file_paths = [os.path.join(RECEIVER_DECODED_CHUNKS_DIR, fname) for fname in os.listdir(RECEIVER_DECODED_CHUNKS_DIR) if os.path.isfile(os.path.join(RECEIVER_DECODED_CHUNKS_DIR, fname))]
            if not chunk_file_paths:
                logging.warning(f"Receiver's decoded chunks directory {RECEIVER_DECODED_CHUNKS_DIR} contains no files. Receive process will do nothing.")
                return True

            receive.reassemble_files(
                chunk_files=chunk_file_paths,
                output_dir=RECEIVER_OUTPUT_DIR,
                encrypt=True,
                key_string=ENCRYPTION_KEY,
                status_callback=logging.info,
                force=True
            )
        elif hasattr(receive, 'main_receive_logic'):
            receive.main_receive_logic(
                chunks_dir=RECEIVER_DECODED_CHUNKS_DIR,
                output_dir=RECEIVER_OUTPUT_DIR,
                encrypt=True,
                key_string=ENCRYPTION_KEY,
                status_callback=logging.info
            )
        elif hasattr(receive, 'reassemble_files_from_chunks'):
             receive.reassemble_files_from_chunks(
                chunks_dir=RECEIVER_DECODED_CHUNKS_DIR,
                output_dir=RECEIVER_OUTPUT_DIR,
                encrypt=True,
                key_string=ENCRYPTION_KEY,
                status_callback=logging.info
            )
        else:
            logging.error("Could not find a suitable main function in receive.py. Skipping receive process.")
            return False
    except Exception as e:
        logging.error(f"Error during receive process: {e}", exc_info=True)
        return False
    logging.info("Receive process complete.")
    return True

def verify_output():
    logging.info("Verifying output state after receive process (Device B)...")

    if not os.path.exists(RECEIVER_OUTPUT_DIR):
        logging.error(f"Output directory {RECEIVER_OUTPUT_DIR} (Device B) was not created by the receive process.")
        return False

    decoded_chunks_were_processed = False
    if os.path.exists(RECEIVER_DECODED_CHUNKS_DIR) and os.listdir(RECEIVER_DECODED_CHUNKS_DIR):
        if any(os.path.isfile(os.path.join(RECEIVER_DECODED_CHUNKS_DIR, f)) for f in os.listdir(RECEIVER_DECODED_CHUNKS_DIR)):
            decoded_chunks_were_processed = True
    
    if decoded_chunks_were_processed:
        if not os.listdir(RECEIVER_OUTPUT_DIR):
            logging.error(f"Output directory {RECEIVER_OUTPUT_DIR} (Device B) is empty, but decoded chunks were processed. Expected output files/directories.")
            return False
        else:
            if any(os.path.isfile(os.path.join(RECEIVER_OUTPUT_DIR, f)) or os.path.isdir(os.path.join(RECEIVER_OUTPUT_DIR, f)) for f in os.listdir(RECEIVER_OUTPUT_DIR)):
                logging.info(f"Output directory {RECEIVER_OUTPUT_DIR} (Device B) contains content as expected after processing decoded chunks.")
            else:
                logging.error(f"Output directory {RECEIVER_OUTPUT_DIR} (Device B) is empty or contains no processable items, but decoded chunks were processed.")
                return False
    else:
        logging.info("No decoded chunks were processed on Device B. Output directory state is considered acceptable (may be empty).")

    logging.info("Output state verification successful on Device B (assuming receive process handled checksums internally).")
    return True

def main_receiver():
    log_file_path = os.path.join(BASE_DIR, "log_receiver.txt")
    file_handler = logging.FileHandler(log_file_path, mode='w')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    root_logger.addHandler(file_handler)
    root_logger.setLevel(logging.INFO)

    overall_start_time = time.time()
    logging.info("Starting c_COLOR File Transfer System Testbench - RECEIVER PART...")

    logging.info("Starting: Setup Receiver Directories")
    setup_receiver_directories()
    logging.info("Completed: Setup Receiver Directories")

    logging.info("Starting: Decode Process")
    if not run_decode_process():
        logging.error("Decode process failed. Aborting receiver testbench.")
        print("Overall Test Result (Receiver): FAILED")
        return
    logging.info("Completed: Decode Process")

    logging.info("Starting: Receive Process")
    if not run_receive_process():
        logging.error("Receive process failed. Aborting receiver testbench.")
        print("Overall Test Result (Receiver): FAILED")
        return
    logging.info("Completed: Receive Process")

    logging.info("Starting: Verify Output")
    verification_passed = verify_output()
    logging.info(f"Completed: Verify Output (Passed: {verification_passed})")

    overall_end_time = time.time()
    logging.info(f"Receiver testbench finished in {overall_end_time - overall_start_time:.2f} seconds.")
    if verification_passed:
        logging.info("Overall Test Result (Receiver): PASSED")
        print("Overall Test Result (Receiver): PASSED")
    else:
        logging.error("Overall Test Result (Receiver): FAILED")
        print("Overall Test Result (Receiver): FAILED")

if __name__ == "__main__":
    main_receiver()
