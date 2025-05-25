import os
import shutil
import time
import logging
import sys

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, **kwargs):
        return iterable

try:
    import send
    import encode
    import clean
    import common
except ImportError as e:
    logging.error(f"Failed to import a required module: {e}. Ensure all script files (send.py, encode.py, clean.py, common.py) are in the same directory or in PYTHONPATH.")
    exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[])

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INPUT_DIR = os.path.join(BASE_DIR, "input") 
SENDER_CHUNKS_DIR = os.path.join(BASE_DIR, "chunks") 
SENDER_c_COLOR_IMAGES_DIR = os.path.join(BASE_DIR, "c_COLOR_images") 
ENCRYPTION_KEY = "your-secure-test-key123"

def setup_sender_directories():
    logging.info("Setting up sender directories (Device A)...")
    if not os.path.exists(INPUT_DIR):
        logging.warning(f"Input directory {INPUT_DIR} does not exist. Creating it. Please populate it with test files.")
        os.makedirs(INPUT_DIR, exist_ok=True)
    elif not os.listdir(INPUT_DIR):
        logging.warning(f"Input directory {INPUT_DIR} is empty. The test may not produce meaningful results.")

    for dir_path in [SENDER_CHUNKS_DIR, SENDER_c_COLOR_IMAGES_DIR]:
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
    logging.info("Sender directory setup complete.")

def run_send_process():
    logging.info(f"Running send process (Device A): {INPUT_DIR} -> {SENDER_CHUNKS_DIR}")
    try:
        if hasattr(send, 'process_files'):
            items_to_process = []
            for root, dirs, files_in_root in os.walk(INPUT_DIR):
                for file_name in files_in_root:
                    items_to_process.append(os.path.join(root, file_name))
            
            if not items_to_process:
                logging.warning(f"Input directory {INPUT_DIR} is empty. Send process will do nothing.")
                return True

            send.process_files(
                files=items_to_process,
                output_dir=SENDER_CHUNKS_DIR,
                encrypt=True,
                key_string=ENCRYPTION_KEY,
                status_callback=logging.info,
                force=True,
                explicit_base_for_rel_paths=INPUT_DIR
            )
        elif hasattr(send, 'process_files'):
            items_to_process = []
            for root, dirs, files_in_root in os.walk(INPUT_DIR):
                for file_name in files_in_root:
                    items_to_process.append(os.path.join(root, file_name))
            
            if not items_to_process:
                logging.warning(f"Input directory {INPUT_DIR} is empty. Send process will do nothing.")
                return True

            send.process_files(
                files=items_to_process,
                output_dir=SENDER_CHUNKS_DIR,
                encrypt=True,
                key_string=ENCRYPTION_KEY,
                status_callback=logging.info,
                force=True,
                explicit_base_for_rel_paths=INPUT_DIR
            )
        else:
            logging.error("Could not find a suitable main function in send.py. Skipping send process.")
            return False
    except Exception as e:
        logging.error(f"Error during send process: {e}", exc_info=True)
        return False

    if os.path.exists(SENDER_CHUNKS_DIR):
        actual_chunk_files = [f for f in os.listdir(SENDER_CHUNKS_DIR) if os.path.isfile(os.path.join(SENDER_CHUNKS_DIR, f)) and f.endswith('.bin')]
        logging.info(f"Verification: Found {len(actual_chunk_files)} actual .bin chunk files in {SENDER_CHUNKS_DIR} after send process.")
    else:
        logging.warning(f"Verification: SENDER_CHUNKS_DIR {SENDER_CHUNKS_DIR} does not exist after send process.")

    logging.info("Send process complete.")
    return True

def run_encode_process():
    logging.info(f"Running encode process (Device A): {SENDER_CHUNKS_DIR} -> {SENDER_c_COLOR_IMAGES_DIR}")
    if not os.path.exists(SENDER_CHUNKS_DIR) or not os.listdir(SENDER_CHUNKS_DIR):
        logging.warning("Sender chunks directory is empty or does not exist. Skipping encode process.")
        return True

    success = True
    chunk_files_raw = os.listdir(SENDER_CHUNKS_DIR)
    logging.info(f"run_encode_process: Files found in {SENDER_CHUNKS_DIR} (unsorted): {chunk_files_raw}")
    chunk_files = sorted([f for f in chunk_files_raw if os.path.isfile(os.path.join(SENDER_CHUNKS_DIR, f))])
    logging.info(f"run_encode_process: Files to process (sorted): {chunk_files}")

    logging.info(f"Found {len(chunk_files)} chunk(s) to encode.")
    total_chunks_to_encode = len(chunk_files)
    logging.info(f"Starting encoding of {total_chunks_to_encode} chunks...")
    for chunk_filename_with_ext in tqdm(chunk_files, desc="Encoding Chunks ", unit="chunk", ncols=100, ascii=True, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]'):
        logging.info(f"run_encode_process: Attempting to process entry: {chunk_filename_with_ext}")
        
        chunk_file_path = os.path.join(SENDER_CHUNKS_DIR, chunk_filename_with_ext)
        image_filename = os.path.splitext(chunk_filename_with_ext)[0] + ".png"
        c_COLOR_image_path = os.path.join(SENDER_c_COLOR_IMAGES_DIR, image_filename)
        
        logging.info(f"Encoding {chunk_file_path} to {c_COLOR_image_path}...")
        try:
            if hasattr(encode, 'encode_chunk_to_c_COLOR'):
                with open(chunk_file_path, 'rb') as f_chunk:
                    full_chunk_data = f_chunk.read()
                
                header_len = getattr(common, '_CHUNK_FULL_HEADER_LEN', 26) 

                if len(full_chunk_data) < header_len:
                    logging.error(f"Chunk file {chunk_file_path} is too short ({len(full_chunk_data)} bytes) to contain a header of {header_len} bytes. Skipping.")
                    success = False
                    continue
                
                payload_data = full_chunk_data[header_len:]
                
                logging.info(f"For chunk file {chunk_filename_with_ext}: Full data length: {len(full_chunk_data)}, Header length: {header_len}, Payload length being passed to encode: {len(payload_data)}")
                if chunk_filename_with_ext.startswith("M_"): 
                    logging.info(f"METADATA CHUNK {chunk_filename_with_ext} - Payload size for encode: {len(payload_data)}")
                
                encode.encode_chunk_to_c_COLOR(
                    chunk_data=payload_data,
                    output_path=c_COLOR_image_path,
                    scale_factor=10 
                )
            else:
                logging.error(f"encode.py does not have the 'encode_chunk_to_c_COLOR' function. Skipping encode for {chunk_filename_with_ext}.")
                success = False 
                continue
        except Exception as e:
            logging.error(f"Error encoding chunk {chunk_file_path} to {c_COLOR_image_path}: {e}", exc_info=True)
            success = False
            continue 
    logging.info("Encode process complete.")
    return success

def main_sender():
    log_file_path = os.path.join(BASE_DIR, "log_sender.txt")
    file_handler = logging.FileHandler(log_file_path, mode='w')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    root_logger.addHandler(file_handler)
    root_logger.setLevel(logging.INFO)

    overall_start_time = time.time()
    logging.info("Starting c_COLOR File Transfer System Testbench - SENDER PART...")

    logging.info("Starting: Setup Sender Directories")
    setup_sender_directories()
    logging.info("Completed: Setup Sender Directories")

    logging.info("Starting: Send Process")
    if not run_send_process():
        logging.error("Send process failed. Aborting sender testbench.")
        print("Overall Test Result (Sender): FAILED")
        return
    logging.info("Completed: Send Process")

    logging.info("Starting: Encode Process")
    if not run_encode_process():
        logging.error("Encode process failed. Aborting sender testbench.")
        print("Overall Test Result (Sender): FAILED")
        return
    logging.info("Completed: Encode Process")
    
    overall_end_time = time.time()
    logging.info(f"Sender testbench finished in {overall_end_time - overall_start_time:.2f} seconds.")
    logging.info(f"Overall Test Result (Sender): COMPLETED (Images ready in {SENDER_c_COLOR_IMAGES_DIR}, Chunks in {SENDER_CHUNKS_DIR})")
    print(f"Overall Test Result (Sender): COMPLETED (Images ready in {SENDER_c_COLOR_IMAGES_DIR}, Chunks in {SENDER_CHUNKS_DIR})")

if __name__ == "__main__":
    main_sender()
