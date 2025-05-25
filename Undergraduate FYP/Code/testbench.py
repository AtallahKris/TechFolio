import os
import shutil
import time
import logging
import sys

try:
    import send
    import encode
    import decode
    import receive
    import clean
    import common
except ImportError as e:
    logging.error(f"Failed to import a required module: {e}. Ensure all script files (send.py, encode.py, decode.py, receive.py, clean.py) are in the same directory as testbench.py or in PYTHONPATH.")
    exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[])

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INPUT_DIR = os.path.join(BASE_DIR, "input")
CHUNKS_DIR = os.path.join(BASE_DIR, "chunks")
c_COLOR_IMAGES_DIR = os.path.join(BASE_DIR, "c_COLOR_images")
DECODED_CHUNKS_DIR = os.path.join(BASE_DIR, "decoded_chunks")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
ENCRYPTION_KEY = "your-secure-test-key123"

def setup_directories():
    logging.info("Setting up directories...")
    if not os.path.exists(INPUT_DIR):
        logging.warning(f"Input directory {INPUT_DIR} does not exist. Creating it. Please populate it with test files.")
        os.makedirs(INPUT_DIR, exist_ok=True)
    elif not os.listdir(INPUT_DIR):
        logging.warning(f"Input directory {INPUT_DIR} is empty. The test may not produce meaningful results.")

    for dir_path in [CHUNKS_DIR, c_COLOR_IMAGES_DIR, DECODED_CHUNKS_DIR, OUTPUT_DIR]:
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
    logging.info("Directory setup complete.")

def run_send_process():
    logging.info(f"Running send process: {INPUT_DIR} -> {CHUNKS_DIR}")
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
                output_dir=CHUNKS_DIR,
                encrypt=True,
                key_string=ENCRYPTION_KEY,
                status_callback=logging.info,
                force=True,
                explicit_base_for_rel_paths=INPUT_DIR
            )
        else:
            logging.error("Could not find a suitable main function in send.py (e.g., process_files). Skipping send process.")
            return False
    except Exception as e:
        logging.error(f"Error during send process: {e}", exc_info=True)
        return False

    if os.path.exists(CHUNKS_DIR):
        actual_chunk_files = [f for f in os.listdir(CHUNKS_DIR) if os.path.isfile(os.path.join(CHUNKS_DIR, f)) and f.endswith('.bin')]
        logging.info(f"Verification: Found {len(actual_chunk_files)} actual .bin chunk files in {CHUNKS_DIR} after send process.")
    else:
        logging.warning(f"Verification: CHUNKS_DIR {CHUNKS_DIR} does not exist after send process.")

    logging.info("Send process complete.")
    return True

def run_encode_process():
    logging.info(f"Running encode process: {CHUNKS_DIR} -> {c_COLOR_IMAGES_DIR}")
    if not os.path.exists(CHUNKS_DIR) or not os.listdir(CHUNKS_DIR):
        logging.warning("Chunks directory is empty or does not exist. Skipping encode process.")
        return True

    success = True
    chunk_files_raw = os.listdir(CHUNKS_DIR)
    logging.info(f"run_encode_process: Files found in {CHUNKS_DIR} (unsorted): {chunk_files_raw}")
    chunk_files = sorted(chunk_files_raw)
    logging.info(f"run_encode_process: Files to process (sorted): {chunk_files}")

    logging.info(f"Found {len(chunk_files)} chunk(s) to encode.")
    total_chunks_to_encode = len(chunk_files)
    encoded_count = 0
    logging.info(f"Starting encoding of {total_chunks_to_encode} chunks...")
    for chunk_filename_with_ext in chunk_files:
        logging.info(f"run_encode_process: Attempting to process entry: {chunk_filename_with_ext}")
        
        if os.path.isfile(os.path.join(CHUNKS_DIR, chunk_filename_with_ext)):
            chunk_file_path = os.path.join(CHUNKS_DIR, chunk_filename_with_ext)
            image_filename = os.path.splitext(chunk_filename_with_ext)[0] + ".png"
            c_COLOR_image_path = os.path.join(c_COLOR_IMAGES_DIR, image_filename)
            
            logging.info(f"Encoding {chunk_file_path} to {c_COLOR_image_path}...")
            try:
                if hasattr(encode, 'encode_chunk_to_c_COLOR'):
                    with open(chunk_file_path, 'rb') as f_chunk:
                        full_chunk_data = f_chunk.read()
                    
                    header_len = 26

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
        encoded_count += 1
        if encoded_count % 10 == 0 or encoded_count == total_chunks_to_encode:
            print(f"Encoding progress: {encoded_count}/{total_chunks_to_encode} chunks encoded.", end='\r', flush=True)
    print()
    logging.info("Encode process complete.")
    return success

def run_decode_process():
    logging.info(f"Running decode process: {c_COLOR_IMAGES_DIR} -> {DECODED_CHUNKS_DIR}")
    if not os.path.exists(c_COLOR_IMAGES_DIR) or not os.listdir(c_COLOR_IMAGES_DIR):
        logging.warning(f"c_COLOR images directory '{c_COLOR_IMAGES_DIR}' is empty or does not exist. Skipping decode process.")
        return True

    success = True
    image_files = [f for f in os.listdir(c_COLOR_IMAGES_DIR) if os.path.isfile(os.path.join(c_COLOR_IMAGES_DIR, f)) and f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
    if not image_files:
        logging.warning(f"No image files found in {c_COLOR_IMAGES_DIR}. Skipping decode process.")
        return True
        
    logging.info(f"Found {len(image_files)} image(s) to decode.")
    total_images_to_decode = len(image_files)
    decoded_count = 0
    logging.info(f"Starting decoding of {total_images_to_decode} images...")
    for image_filename in image_files:
        c_COLOR_image_path = os.path.join(c_COLOR_IMAGES_DIR, image_filename)
        
        reconstructed_chunk_filename = os.path.splitext(image_filename)[0] + ".bin"
        reconstructed_chunk_path = os.path.join(DECODED_CHUNKS_DIR, reconstructed_chunk_filename)

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
                temp_payload_filename = f"temp_payload_{reconstructed_chunk_filename}"
                temp_payload_path = os.path.join(DECODED_CHUNKS_DIR, temp_payload_filename)
                
                logging.info(f"Decoding {c_COLOR_image_path} to temporary payload file {temp_payload_path}...")
                decode.decode_c_COLOR_to_chunk(c_COLOR_image_path, temp_payload_path)

                if not os.path.exists(temp_payload_path):
                    logging.error(f"decode_c_COLOR_to_chunk failed to create temporary payload file {temp_payload_path} for image {c_COLOR_image_path}.")
                    success = False
                    continue
                
                with open(temp_payload_path, 'rb') as f_payload:
                    decoded_payload_bytes = f_payload.read()
                
                try:
                    os.remove(temp_payload_path)
                except OSError as e_rm:
                    logging.warning(f"Could not remove temporary payload file {temp_payload_path}: {e_rm}")
            else:
                logging.error("Suitable decode function (e.g., 'decode_c_COLOR_payload_from_image' or 'decode_c_COLOR_to_chunk') not found in decode.py.")
                success = False
                break

            if decoded_payload_bytes is None:
                logging.error(f"Failed to obtain decoded payload for {c_COLOR_image_path} after attempting all methods.")
                success = False
                continue

            original_chunk_for_header_filename = os.path.splitext(image_filename)[0] + ".bin"
            original_chunk_path = os.path.join(CHUNKS_DIR, original_chunk_for_header_filename)

            if not os.path.exists(original_chunk_path):
                logging.error(f"Original chunk {original_chunk_path} (needed for header) not found for image {image_filename}. Cannot prepend header.")
                success = False
                continue

            header_len = common._CHUNK_FULL_HEADER_LEN
            with open(original_chunk_path, 'rb') as f_orig_chunk:
                original_header = f_orig_chunk.read(header_len)

                if original_chunk_for_header_filename.startswith("M_"):
                    original_payload_bytes = f_orig_chunk.read()
                    if original_payload_bytes == decoded_payload_bytes:
                        logging.info(f"SUCCESS: Metadata payload for {original_chunk_for_header_filename} MATCHES original after decoding.")
                    else:
                        logging.error(f"CRITICAL ERROR: METADATA PAYLOAD MISMATCH for {original_chunk_for_header_filename}!")
                        logging.error(f"  Original payload length: {len(original_payload_bytes)}")
                        logging.error(f"  Decoded payload length: {len(decoded_payload_bytes)}")

            logging.info(f"Size of decoded payload for {reconstructed_chunk_filename}: {len(decoded_payload_bytes)} bytes.")

            full_reconstructed_chunk_data = original_header + decoded_payload_bytes

            with open(reconstructed_chunk_path, 'wb') as f_final_chunk:
                f_final_chunk.write(full_reconstructed_chunk_data)
            logging.info(f"Re-prepended header. Reconstructed chunk saved to {reconstructed_chunk_path}. Final size: {len(full_reconstructed_chunk_data)} bytes.")

        except Exception as e:
            logging.error(f"Error processing image {image_filename} (decode/header prepend): {e}", exc_info=True)
            success = False
            
        decoded_count += 1
        if decoded_count % 10 == 0 or decoded_count == total_images_to_decode:
            print(f"Decoding progress: {decoded_count}/{total_images_to_decode} images decoded.", end='\r', flush=True)
    print()
    logging.info("Decode process complete.")
    return success

def run_receive_process():
    logging.info(f"Running receive process: {DECODED_CHUNKS_DIR} -> {OUTPUT_DIR}")
    if not os.path.exists(DECODED_CHUNKS_DIR) or not os.listdir(DECODED_CHUNKS_DIR):
        logging.warning("Decoded chunks directory is empty or does not exist. Skipping receive process.")
        return False

    try:
        if hasattr(receive, 'reassemble_files'):
            chunk_file_paths = [os.path.join(DECODED_CHUNKS_DIR, fname) for fname in os.listdir(DECODED_CHUNKS_DIR) if os.path.isfile(os.path.join(DECODED_CHUNKS_DIR, fname))]
            if not chunk_file_paths:
                logging.warning(f"Decoded chunks directory {DECODED_CHUNKS_DIR} contains no files. Receive process will do nothing.")
                return True

            receive.reassemble_files(
                chunk_files=chunk_file_paths,
                output_dir=OUTPUT_DIR,
                encrypt=True,
                key_string=ENCRYPTION_KEY,
                status_callback=logging.info,
                force=True
            )
        else:
            logging.error("Could not find a suitable main function in receive.py (e.g., reassemble_files). Skipping receive process.")
            return False
    except Exception as e:
        logging.error(f"Error during receive process: {e}", exc_info=True)
        return False
    logging.info("Receive process complete.")
    return True

def verify_output():
    logging.info("Verifying output...")
    if not hasattr(clean, 'compare_directories'):
        logging.error("clean.compare_directories function not found. Cannot verify output.")
        return False

    comparison_results = clean.compare_directories(INPUT_DIR, OUTPUT_DIR)
    
    logging.info("Comparison Results:")
    logging.info(f"  Matching files: {len(comparison_results.get('matching', []))}")
    if comparison_results.get('matching'):
        for f in comparison_results['matching']: logging.info(f"    - {f}")
    
    logging.info(f"  Files only in input: {len(comparison_results.get('input_only', []))}")
    if comparison_results.get('input_only'):
        for f in comparison_results['input_only']: logging.info(f"    - {f}")

    logging.info(f"  Files only in output: {len(comparison_results.get('output_only', []))}")
    if comparison_results.get('output_only'):
        for f in comparison_results['output_only']: logging.info(f"    - {f}")

    logging.info(f"  Files with different content: {len(comparison_results.get('different', []))}")
    if comparison_results.get('different'):
        for diff_file_info in comparison_results['different']:
             logging.info(f"    - Path: {diff_file_info[0]}, Input Hash: {diff_file_info[1][:8]}..., Output Hash: {diff_file_info[2][:8]}...")

    if not comparison_results.get('input_only') and \
       not comparison_results.get('output_only') and \
       not comparison_results.get('different') and \
       len(comparison_results.get('matching', [])) > 0 and \
       os.listdir(INPUT_DIR):
        logging.info("SUCCESS: Output matches input!")
        return True
    elif not os.listdir(INPUT_DIR):
        logging.warning("Input directory was empty. Verification is trivial.")
        return False
    else:
        logging.error("FAILURE: Output does not match input or discrepancies found.")
        return False

def main():
    log_file_path = os.path.join(BASE_DIR, "log.txt")
    file_handler = logging.FileHandler(log_file_path, mode='w')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    root_logger.addHandler(file_handler)
    root_logger.setLevel(logging.INFO)

    overall_start_time = time.time()
    logging.info("Starting c_COLOR File Transfer System Testbench...")

    stages = [
        ("Setup Directories", setup_directories, 1),
        ("Send Process", run_send_process, 10),
        ("Encode Process", run_encode_process, 30),
        ("Decode Process", run_decode_process, 30),
        ("Receive Process", run_receive_process, 20),
        ("Verify Output", verify_output, 9)
    ]

    logging.info(f"Starting: {stages[0][0]}")
    stages[0][1]()
    logging.info(f"Completed: {stages[0][0]}")

    logging.info(f"Starting: {stages[1][0]}")
    if not stages[1][1]():
        logging.error("Send process failed. Aborting testbench.")
        return
    logging.info(f"Completed: {stages[1][0]}")

    logging.info(f"Starting: {stages[2][0]}")
    if not stages[2][1]():
        logging.error("Encode process failed. Aborting testbench.")
        return
    logging.info(f"Completed: {stages[2][0]}")

    logging.info(f"Starting: {stages[3][0]}")
    if not stages[3][1]():
        logging.error("Decode process failed. Aborting testbench.")
        return
    logging.info(f"Completed: {stages[3][0]}")

    logging.info(f"Starting: {stages[4][0]}")
    if not stages[4][1]():
        logging.error("Receive process failed. Aborting testbench.")
        return
    logging.info(f"Completed: {stages[4][0]}")

    logging.info(f"Starting: {stages[5][0]}")
    verification_passed = stages[5][1]()
    logging.info(f"Completed: {stages[5][0]}")

    overall_end_time = time.time()
    logging.info(f"Testbench finished in {overall_end_time - overall_start_time:.2f} seconds.")
    if verification_passed:
        logging.info("Overall Test Result: PASSED")
        print("Overall Test Result: PASSED")
    else:
        logging.error("Overall Test Result: FAILED")
        print("Overall Test Result: FAILED")

if __name__ == "__main__":
    main()
