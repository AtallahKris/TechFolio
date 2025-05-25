import shutil
import os
import random
import string
import hashlib
import logging

logger = logging.getLogger(__name__)

def delete_all_in_directory(directory):
    if not os.path.isdir(directory):
        logger.warning(f"Directory {directory} does not exist. Skipping deletion.")
        return
    logger.info(f"Deleting all files and subdirectories in {directory}...")
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            logger.error(f"Failed to delete {file_path}. Reason: {e}", exc_info=True)
    logger.info(f"Deletion completed for {directory}")

def create_random_file_in_random_subdir(root_dir):
    subdirs = [root_dir]
    for dirpath, dirnames, _ in os.walk(root_dir):
        for dirname in dirnames:
            subdirs.append(os.path.join(dirpath, dirname))
    if random.choice([True, False]) or not subdirs:
        rand_name = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        new_dir = os.path.join(root_dir, rand_name)
        os.makedirs(new_dir, exist_ok=True)
        target_dir = new_dir
    else:
        target_dir = random.choice(subdirs)
    rand_file_name = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    file_path = os.path.join(target_dir, rand_file_name)
    size = random.randint(1, 40960)
    with open(file_path, "wb") as f:
        f.write(os.urandom(size))

def calculate_file_hash(file_path):
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        buf = f.read(65536)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(65536)
    return hasher.hexdigest()

def get_files_with_hashes(directory):
    files_with_hashes = {}
    for root, _, files in os.walk(directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            rel_path = os.path.relpath(file_path, directory)
            files_with_hashes[rel_path] = calculate_file_hash(file_path)
    return files_with_hashes

def compare_directories(input_dir, output_dir):
    logger.info(f"Comparing directories: {input_dir} and {output_dir}")
    
    input_files = get_files_with_hashes(input_dir)
    output_files = get_files_with_hashes(output_dir)
    
    matching_files = []
    input_only_files = []
    output_only_files = []
    different_hash_files = []
    
    for rel_path, input_hash in input_files.items():
        if rel_path in output_files:
            if input_hash == output_files[rel_path]:
                matching_files.append(rel_path)
            else:
                different_hash_files.append((rel_path, input_hash, output_files[rel_path]))
        else:
            input_only_files.append(rel_path)
    
    for rel_path in output_files:
        if rel_path not in input_files:
            output_only_files.append(rel_path)
    
    logger.info(f"Matching files: {len(matching_files)}")
    logger.info(f"Files only in input: {len(input_only_files)}")
    logger.info(f"Files only in output: {len(output_only_files)}")
    logger.info(f"Files with different content: {len(different_hash_files)}")
    
    if different_hash_files:
        logger.info("Files with different content:")
        for rel_path, input_hash, output_hash in different_hash_files:
            logger.info(f"  {rel_path}: Input hash: {input_hash[:8]}..., Output hash: {output_hash[:8]}...")
    
    return {
        'matching': matching_files,
        'input_only': input_only_files,
        'output_only': output_only_files,
        'different': different_hash_files
    }

def main_clean_script_action():
    script_base_dir = os.path.dirname(os.path.abspath(__file__))
    
    input_dir_clean = os.path.join(script_base_dir, 'input')
    output_dir_clean = os.path.join(script_base_dir, 'output')
    chunks_dir_clean = os.path.join(script_base_dir, 'chunks')
    c_COLOR_images_dir = os.path.join(script_base_dir, 'c_COLOR_images')
    captured_c_COLOR_images_dir = os.path.join(script_base_dir, 'captured_c_COLOR_images')

    os.makedirs(input_dir_clean, exist_ok=True)
    os.makedirs(output_dir_clean, exist_ok=True)
    os.makedirs(chunks_dir_clean, exist_ok=True)
    os.makedirs(captured_c_COLOR_images_dir, exist_ok=True)

    logger.info("Running direct script actions from clean.py")
    
    comparison_results = compare_directories(input_dir_clean, output_dir_clean)
    logger.info(f"Comparison results: {comparison_results}")

    delete_all_in_directory(output_dir_clean)
    delete_all_in_directory(chunks_dir_clean)
    delete_all_in_directory(input_dir_clean) 
    delete_all_in_directory(c_COLOR_images_dir)
    delete_all_in_directory(captured_c_COLOR_images_dir)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    main_clean_script_action()