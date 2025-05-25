#!/usr/bin/env python3
import os
import zlib
import struct
import string
import random
import concurrent.futures
import pickle
import gc
import time
import tempfile
import numpy as np
import hashlib
import secrets
import logging

from common import (
    CHUNK_SIZE, MAX_FILE_SIZE, prepare_output_directory, string_to_key,
    calculate_checksum, sanitize_path, get_optimal_buffer_size,
    get_optimal_thread_count, xor_crypt_chunk, create_chunk_header
)

READ_BUFFER_SIZE = 8192

def generate_random_key(length=12):
    chars = string.ascii_letters + string.digits + '!@#$%^&*()-_=+[]{}|;:,.<>?'
    return ''.join(secrets.choice(chars) for _ in range(length))

def get_optimal_compression_level(file_path, file_size=None, sample_data=None):
    _, ext = os.path.splitext(file_path.lower())
    
    if ext in ['.zip', '.rar', '.7z', '.gz', '.bz2', '.xz', '.jpg', '.jpeg', '.png', 
            '.mp3', '.mp4', '.avi', '.mkv', '.mov', '.pdf', '.docx', '.xlsx']:
        return 1
        
    if ext in ['.txt', '.csv', '.xml', '.json', '.html', '.md', '.log', '.sql', 
             '.c', '.cpp', '.h', '.py', '.js', '.java', '.cs', '.php', '.rb']:
        return 9
    
    if sample_data and len(sample_data) > 100:
        sample_compressed = zlib.compress(sample_data, 1)
        ratio = len(sample_compressed) / len(sample_data)
        
        if ratio < 0.3:
            return 9
        elif ratio < 0.6:
            return 6
        elif ratio < 0.8:
            return 3
        else:
            return 1
    
    return 6

def process_chunk(chunk_data, seq_number, total_chunks, output_dir, chunk_type="CH", encrypt=True, key=None, status_callback=None):
    is_metadata_flag = chunk_type == "MD"
    payload_checksum_bytes = calculate_checksum(chunk_data).encode('utf-8')[:8]
    payload_to_write = xor_crypt_chunk(chunk_data, key, offset=seq_number * len(chunk_data)) if encrypt and key else chunk_data
    header = create_chunk_header(
        is_metadata=is_metadata_flag,
        sequence_number=seq_number,
        total_chunks=total_chunks,
        is_encrypted=encrypt,
        payload_checksum_bytes=payload_checksum_bytes
    )
    final_chunk = header + payload_to_write
    prefix = "M" if is_metadata_flag else "C"
    total_chunks_for_filename = int(total_chunks) if total_chunks is not None else 0
    chunk_file_name = os.path.join(output_dir, f"{prefix}_{seq_number}_{total_chunks_for_filename}.bin")
    logging.info(f"process_chunk: Creating {chunk_file_name} (seq={seq_number}, total_chunks_in_name={total_chunks_for_filename}, type={prefix})")
    with open(chunk_file_name, 'wb', buffering=8192) as f: 
        f.write(final_chunk)
    return chunk_file_name

def estimate_compression_ratio(file_path):
    _, ext = os.path.splitext(file_path.lower())
    if ext in ['.zip', '.rar', '.7z', '.gz', '.bz2', '.xz', '.jpg', '.jpeg', '.png', 
              '.mp3', '.mp4', '.avi', '.mkv', '.mov', '.pdf', '.docx', '.xlsx']:
        return 0.95
    if ext in ['.txt', '.csv', '.xml', '.json', '.html', '.md', '.log', '.sql']:
        return 0.3
    if ext in ['.c', '.cpp', '.h', '.py', '.js', '.java', '.cs', '.php', '.rb']:
        return 0.4
    if ext in ['.exe', '.dll', '.so', '.bin', '.dat']:
        return 0.8
    return 0.7

def process_file_streaming(file_path, output_dir, start_seq, total_chunks, encrypt=True, key=None, 
                         chunk_size=CHUNK_SIZE, status_callback=None):
    temp_file_path = None
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            raise FileNotFoundError(f"File is empty: {file_path}")
        if file_size > MAX_FILE_SIZE:
            raise ValueError(f"File size exceeds maximum limit of {MAX_FILE_SIZE/(1024*1024):.1f} MB: {file_path}")
        buffer_size = get_optimal_buffer_size(file_size)
        if file_size < 1024 * 1024:
            comp_level = get_optimal_compression_level(file_path, file_size)
        else:
            sample_data = bytearray()
            with open(file_path, 'rb') as f:
                sample_data.extend(f.read(min(4096, file_size // 10)))
                if file_size > 8192:
                    f.seek(file_size // 2)
                    sample_data.extend(f.read(min(4096, file_size // 10)))
                if file_size > 16384:
                    f.seek(max(0, file_size - 4096))
                    sample_data.extend(f.read(4096))
            comp_level = get_optimal_compression_level(file_path, file_size, bytes(sample_data))
        use_temp_file = file_size > 100 * 1024 * 1024
        compressor = zlib.compressobj(comp_level)
        checksum_calculator = hashlib.sha256()
        compressed_size = 0
        temp_file = None
        compressed_chunks = [] if not use_temp_file else None
        if use_temp_file:
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            temp_file_path = temp_file.name
        with open(file_path, 'rb', buffering=buffer_size) as f:
            while True:
                buffer = f.read(buffer_size)
                if not buffer:
                    break
                checksum_calculator.update(buffer)
                compressed_chunk = compressor.compress(buffer)
                if compressed_chunk:
                    if use_temp_file:
                        temp_file.write(compressed_chunk)
                        compressed_size += len(compressed_chunk)
                    else:
                        compressed_chunks.append(compressed_chunk)
            final_data = compressor.flush()
            if final_data:
                if use_temp_file:
                    temp_file.write(final_data)
                    compressed_size += len(final_data)
                    temp_file.flush()
                else:
                    compressed_chunks.append(final_data)
        file_checksum = checksum_calculator.hexdigest()
        if use_temp_file:
            temp_file.close()
            chunk_count = (compressed_size + chunk_size - 1) // chunk_size
        else:
            compressed_data = b''.join(compressed_chunks)
            compressed_chunks = None
            chunk_count = (len(compressed_data) + chunk_size - 1) // chunk_size
        result_chunks = []
        batch_size = min(50, max(10, chunk_count // 4))
        thread_count = min(os.cpu_count() or 4, max(2, chunk_count // 10))
        with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
            for batch_start in range(0, chunk_count, batch_size):
                batch_end = min(batch_start + batch_size, chunk_count)
                batch_futures = []
                temp_file_handle = None
                if use_temp_file:
                    temp_file_handle = open(temp_file_path, 'rb')
                for i in range(batch_start, batch_end):
                    try:
                        if use_temp_file:
                            temp_file_handle.seek(i * chunk_size)
                            chunk_data = temp_file_handle.read(chunk_size)
                        else:
                            chunk_data = compressed_data[i*chunk_size:min((i+1)*chunk_size, len(compressed_data))]
                        future = executor.submit(process_chunk, chunk_data, start_seq + i, total_chunks, output_dir, "CH", encrypt, key)
                        batch_futures.append((future, i))
                    except Exception as e:
                        if status_callback:
                            status_callback(f"Error reading chunk {i} for {os.path.basename(file_path)}: {str(e)}")
                if temp_file_handle:
                    temp_file_handle.close()
                for future, idx in batch_futures:
                    try:
                        chunk_path = future.result()
                        result_chunks.append(chunk_path)
                    except Exception as e:
                        if status_callback:
                            status_callback(f"Error processing chunk {idx} for {os.path.basename(file_path)}: {str(e)}")
                if status_callback and (batch_end % max(10, chunk_count // 10) == 0 or batch_end == chunk_count):
                    status_callback(f"Processing file {os.path.basename(file_path)}: {batch_end}/{chunk_count} chunks")
                batch_futures = None
                if chunk_count > 100 and batch_end % (batch_size * 5) == 0:
                    gc.collect()
        return result_chunks, file_size, file_checksum
    except Exception as e:
        if status_callback: 
            status_callback(f"Error processing file {file_path} in streaming mode: {str(e)}")
        raise
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                if status_callback:
                    status_callback(f"Warning: Could not delete temporary file: {str(e)}")

def process_file_batch(file_batch, output_dir, metadata, current_seq, total_chunks, 
                      common_base, encrypt=True, key=None, status_callback=None):
    results = []
    errors = []
    for file_data in file_batch:
        file_path = file_data['path']
        try:
            rel_path = os.path.relpath(file_path, common_base)
            safe_rel_path = sanitize_path(rel_path)
            start_seq = current_seq
            chunk_files, file_size, file_checksum = process_file_streaming(
                file_path, output_dir, start_seq, total_chunks, 
                encrypt=encrypt, key=key, status_callback=status_callback
            )
            chunk_count = len(chunk_files)
            current_seq += chunk_count
            file_metadata = {
                "path": safe_rel_path, 
                "size": file_size,
                "start_sequence": start_seq, 
                "chunk_count": chunk_count,
                "checksum": file_checksum, 
                "original_path": rel_path,
                "total_chunks": total_chunks
            }
            results.append((file_path, chunk_files, file_metadata))
        except Exception as e:
            errors.append((file_path, str(e)))
            if status_callback:
                status_callback(f"Error processing {os.path.basename(file_path)}: {str(e)}")
    return results, errors, current_seq

def process_files(files, output_dir, encrypt=True, key_string="", 
                  progress_callback=None, status_callback=None, force=False,
                  explicit_base_for_rel_paths=None): 
    try:
        os.makedirs(output_dir, exist_ok=True)
        if not files:
            if status_callback: status_callback("No files selected")
            return False
        if encrypt and not key_string:
            if status_callback: status_callback("ERROR: Encryption key cannot be empty when encryption is enabled")
            raise ValueError("Encryption key cannot be empty when encryption is enabled")
        key = string_to_key(key_string) if encrypt else None
        missing_files = []
        for file_path in files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        if missing_files:
            error_msg = f"ERROR: {len(missing_files)} file(s) not found"
            if len(missing_files) <= 3:
                error_msg += f": {', '.join(os.path.basename(f) for f in missing_files)}"
            if status_callback: status_callback(error_msg)
            raise FileNotFoundError(error_msg)
        if not prepare_output_directory(output_dir, allow_overwrite=force):
            if status_callback: 
                status_callback(f"Output directory {output_dir} is not empty. Use --force to overwrite.")
            raise ValueError(f"Output directory {output_dir} is not empty. Use --force to overwrite.")
        actual_common_base_for_rel_paths = ""
        if explicit_base_for_rel_paths:
            actual_common_base_for_rel_paths = os.path.abspath(explicit_base_for_rel_paths)
            if not os.path.isdir(actual_common_base_for_rel_paths):
                if os.path.isfile(actual_common_base_for_rel_paths):
                     actual_common_base_for_rel_paths = os.path.dirname(actual_common_base_for_rel_paths)
                else:
                    raise ValueError(f"Explicit base for relative paths '{actual_common_base_for_rel_paths}' is not a valid directory.")
            for f_abs_path_str in files:
                f_abs_path = os.path.abspath(f_abs_path_str)
                if not f_abs_path.startswith(os.path.join(actual_common_base_for_rel_paths, '')) and f_abs_path != actual_common_base_for_rel_paths :
                    raise ValueError(f"File '{f_abs_path}' is not under the explicit base '{actual_common_base_for_rel_paths}'. Path starts with: {os.path.join(actual_common_base_for_rel_paths, '')}")
        elif not files:
            actual_common_base_for_rel_paths = os.path.abspath(os.getcwd()) 
        elif len(files) == 1:
            actual_common_base_for_rel_paths = os.path.abspath(os.path.dirname(files[0]))
        else: 
            actual_common_base_for_rel_paths = os.path.commonpath([os.path.abspath(f) for f in files])
        if status_callback:
            status_callback(f"Using common base for relative paths: {actual_common_base_for_rel_paths}")
        valid_files_data = [] 
        for file_path_str in files:
            abs_path = os.path.abspath(file_path_str)
            try:
                file_size = os.path.getsize(abs_path)
                if file_size == 0:
                    if status_callback: status_callback(f"Warning: File {os.path.basename(abs_path)} is empty. It will be processed as an empty file.")
                valid_files_data.append({'path': abs_path, 'size': file_size})
            except FileNotFoundError:
                if status_callback: status_callback(f"Error: File not found during size check: {abs_path}")
                pass
        if not valid_files_data:
            if status_callback: status_callback("No valid files found to process after initial checks.")
            return True 
        for f_info in valid_files_data:
            try:
                with open(f_info['path'], 'rb') as orig_f:
                    f_info['checksum'] = calculate_checksum(orig_f.read()) 
                if status_callback:
                    status_callback(f"Calculated original checksum for {os.path.basename(f_info['path'])}: {f_info['checksum'][:10]}...") 
            except Exception as e:
                f_info['checksum'] = "" 
                if status_callback:
                    status_callback(f"Warning: Could not calculate checksum for {os.path.basename(f_info['path'])}: {e}")
        if status_callback: status_callback(f"Analyzing {len(valid_files_data)} files...")
        analyzed_file_info = []
        total_estimated_file_chunks = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(os.cpu_count() or 4, len(valid_files_data))) as executor:
            analysis_futures = {}
            for i, file_data_item in enumerate(valid_files_data):
                file_path = file_data_item['path']
                file_size = file_data_item['size']
                use_streaming = file_size > READ_BUFFER_SIZE * 10 
                if use_streaming:
                    future = executor.submit(lambda p: (p, estimate_compression_ratio(p)), file_path)
                    analysis_futures[future] = {'path': file_path, 'size': file_size, 'streaming': True, 'index': i}
                else:
                    future = executor.submit(
                        lambda p, s: (p, zlib.compress(open(p, 'rb').read(), get_optimal_compression_level(p,s))),
                        file_path, file_size
                    )
                    analysis_futures[future] = {'path': file_path, 'size': file_size, 'streaming': False, 'index': i}
            for future in concurrent.futures.as_completed(analysis_futures):
                file_info = analysis_futures[future]
                original_path = file_info['path']
                original_size = file_info['size']
                try:
                    if file_info['streaming']:
                        _, ratio = future.result()
                        estimated_compressed_size = int(original_size * ratio)
                        chunk_count = (estimated_compressed_size + CHUNK_SIZE - 1) // CHUNK_SIZE
                        analyzed_file_info.append({
                            'path': original_path, 'actual_size': original_size, 'streaming': True,
                            'estimated_compressed_size': estimated_compressed_size, 'chunk_count': chunk_count
                        })
                    else:
                        _, compressed_data = future.result()
                        chunk_count = (len(compressed_data) + CHUNK_SIZE - 1) // CHUNK_SIZE
                        analyzed_file_info.append({
                            'path': original_path, 'actual_size': original_size, 'streaming': False,
                            'compressed_data': compressed_data, 
                            'chunk_count': chunk_count
                        })
                    total_estimated_file_chunks += chunk_count
                except Exception as e:
                    if status_callback:
                        status_callback(f"Warning: Error analyzing {os.path.basename(original_path)}: {e}. Estimating based on original size.")
                    chunk_count = (original_size + CHUNK_SIZE - 1) // CHUNK_SIZE
                    analyzed_file_info.append({
                        'path': original_path, 'actual_size': original_size, 'streaming': True, 
                        'estimated_compressed_size': original_size, 'chunk_count': chunk_count
                    })
                    total_estimated_file_chunks += chunk_count
                if progress_callback:
                    processed_analyses = len(analyzed_file_info)
                    progress_callback(f"Analyzing files: {processed_analyses}/{len(valid_files_data)}", 
                                     (processed_analyses / len(valid_files_data)) * 30)
        checksum_map = {item['path']: item.get('checksum', "") for item in valid_files_data}
        for af_info in analyzed_file_info:
            af_info['checksum'] = checksum_map.get(af_info['path'], "")
        if not analyzed_file_info:
            if status_callback: status_callback("No files to process after analysis.")
            return True
        if status_callback: status_callback("Preparing metadata...")
        metadata = {
            "files": [], 
            "total_files": len(valid_files_data), 
            "base_directory": actual_common_base_for_rel_paths, 
            "encrypted": encrypt,
            "created_time": time.time(),
            "format_version": "2.1" 
        }
        if encrypt: 
            metadata["key_verification"] = calculate_checksum(key)
        temp_metadata_files_list = []
        _seq_counter_for_meta_est = 0 
        for file_data in analyzed_file_info: 
            rel_path_for_meta_est = os.path.relpath(file_data['path'], actual_common_base_for_rel_paths)
            safe_rel_path_for_meta_est = sanitize_path(rel_path_for_meta_est)
            temp_metadata_files_list.append({
                "path": safe_rel_path_for_meta_est, 
                "size": file_data['actual_size'],
                "start_sequence": _seq_counter_for_meta_est, 
                "chunk_count": file_data['chunk_count'],     
                "original_path": rel_path_for_meta_est, 
                "total_chunks": 0 
            })
            _seq_counter_for_meta_est += file_data['chunk_count']
        _temp_meta = metadata.copy()
        _temp_meta["files"] = temp_metadata_files_list
        preliminary_metadata_bytes = pickle.dumps(_temp_meta)
        preliminary_compressed_metadata = zlib.compress(preliminary_metadata_bytes, 9)
        if status_callback: status_callback(f"Preliminary compressed metadata size: {len(preliminary_compressed_metadata)} bytes")
        metadata_chunks_count = (len(preliminary_compressed_metadata) + CHUNK_SIZE - 1) // CHUNK_SIZE
        actual_total_file_chunks = sum(f['chunk_count'] for f in analyzed_file_info)
        total_chunks = metadata_chunks_count + actual_total_file_chunks
        current_sequence_for_files = metadata_chunks_count 
        for file_data in analyzed_file_info:
            rel_path = os.path.relpath(file_data['path'], actual_common_base_for_rel_paths)
            safe_rel_path = sanitize_path(rel_path)
            file_data['start_sequence'] = current_sequence_for_files 
            file_data['total_chunks'] = total_chunks 
            metadata["files"].append({
                "path": safe_rel_path, 
                "size": file_data['actual_size'],
                "start_sequence": current_sequence_for_files, 
                "chunk_count": file_data['chunk_count'], 
                "checksum": file_data.get('checksum', ""), 
                "original_path": rel_path, 
                "total_chunks": total_chunks 
            })
            current_sequence_for_files += file_data['chunk_count']
        final_metadata_bytes = pickle.dumps(metadata)
        final_compressed_metadata = zlib.compress(final_metadata_bytes, 9)
        if status_callback: status_callback(f"Final compressed metadata size: {len(final_compressed_metadata)} bytes")
        current_calc_metadata_chunks = (len(final_compressed_metadata) + CHUNK_SIZE - 1) // CHUNK_SIZE
        if current_calc_metadata_chunks != metadata_chunks_count:
            if status_callback:
                status_callback(f"INFO: Metadata chunk count changed from {metadata_chunks_count} (based on preliminary) to {current_calc_metadata_chunks} (based on first final). Re-calculating...")
            metadata_chunks_count = current_calc_metadata_chunks 
            metadata["total_chunks"] = actual_total_file_chunks + metadata_chunks_count
            for file_info_item in metadata["files"]: 
                file_info_item["total_chunks"] = metadata["total_chunks"]
            final_metadata_bytes = pickle.dumps(metadata)
            final_compressed_metadata = zlib.compress(final_metadata_bytes, 9)
            if status_callback: status_callback(f"Re-finalized compressed metadata size after total_chunks update: {len(final_compressed_metadata)} bytes")
            new_metadata_chunks_count_final = (len(final_compressed_metadata) + CHUNK_SIZE - 1) // CHUNK_SIZE
            if new_metadata_chunks_count_final != metadata_chunks_count:
                if status_callback:
                    status_callback(f"WARNING: Metadata chunk count changed AGAIN to {new_metadata_chunks_count_final} after re-finalization. Previous was {metadata_chunks_count}. Updating total_chunks again.")
                metadata_chunks_count = new_metadata_chunks_count_final 
                metadata["total_chunks"] = actual_total_file_chunks + metadata_chunks_count
                for file_info_item in metadata["files"]:
                    file_info_item["total_chunks"] = metadata["total_chunks"]
                final_metadata_bytes = pickle.dumps(metadata) 
                final_compressed_metadata = zlib.compress(final_metadata_bytes, 9) 
                if status_callback: status_callback(f"Final re-compressed metadata size after second total_chunks update: {len(final_compressed_metadata)} bytes")
                metadata_chunks_count = (len(final_compressed_metadata) + CHUNK_SIZE - 1) // CHUNK_SIZE
        if status_callback: status_callback(f"Writing {metadata_chunks_count} metadata chunk(s)...")
        all_created_chunk_paths = []
        if status_callback: status_callback(f"Processing metadata into {metadata_chunks_count} chunks...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(4, metadata_chunks_count)) as executor:
            meta_futures = []
            for i in range(metadata_chunks_count):
                start_pos = i * CHUNK_SIZE
                end_pos = min((i + 1) * CHUNK_SIZE, len(final_compressed_metadata))
                chunk_data_content = final_compressed_metadata[start_pos:end_pos]
                future = executor.submit(process_chunk, chunk_data_content, i, total_chunks, output_dir, "MD", encrypt, key)
                meta_futures.append(future)
            for i, future in enumerate(concurrent.futures.as_completed(meta_futures)):
                try:
                    all_created_chunk_paths.append(future.result())
                    if progress_callback:
                        progress_callback(f"Processing metadata: {i+1}/{metadata_chunks_count}", 
                                         30 + ((i+1) / metadata_chunks_count * 10))
                except Exception as e:
                    if status_callback: status_callback(f"Error processing metadata chunk {i}: {e}")
            if len(all_created_chunk_paths) != metadata_chunks_count:
                raise RuntimeError(f"Failed to create all metadata chunks. Expected {metadata_chunks_count}, got {len(all_created_chunk_paths)}")
        if status_callback: status_callback(f"Processing {len(analyzed_file_info)} files...")
        file_processing_worker_count = get_optimal_thread_count(
            "cpu_heavy" if sum(f['actual_size'] for f in analyzed_file_info) > 50*1024*1024 else "io",
            len(analyzed_file_info),
            sum(f['actual_size'] for f in analyzed_file_info)
        )
        processed_files_count = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=file_processing_worker_count) as executor:
            file_proc_futures_map = {} 
            for file_data_item in analyzed_file_info: 
                is_streaming = file_data_item['streaming']
                path_to_process = file_data_item['path']
                if is_streaming:
                    future = executor.submit(process_file_streaming,
                                             path_to_process,
                                             output_dir,
                                             file_data_item['start_sequence'],
                                             file_data_item['total_chunks'],
                                             encrypt, key, CHUNK_SIZE, status_callback)
                else: 
                    future = executor.submit(process_precompressed_data,
                                             file_data_item['compressed_data'],
                                             output_dir,
                                             file_data_item['start_sequence'],
                                             file_data_item['total_chunks'],
                                             encrypt, key, CHUNK_SIZE,
                                             path_to_process) 
                file_proc_futures_map[future] = {'path': path_to_process, 'streaming': is_streaming, 'data': file_data_item}
            for future in concurrent.futures.as_completed(file_proc_futures_map):
                future_info = file_proc_futures_map[future]
                original_file_path = future_info['path']
                is_streaming_file = future_info['streaming']
                try:
                    if is_streaming_file: 
                        created_paths, file_size, file_checksum = future.result()
                        all_created_chunk_paths.extend(created_paths)
                        for m_file_entry in metadata["files"]:
                            if m_file_entry["original_path"] == os.path.relpath(original_file_path, actual_common_base_for_rel_paths):
                                m_file_entry["checksum"] = file_checksum
                                break
                    else: 
                        created_paths = future.result()
                        all_created_chunk_paths.extend(created_paths)
                    processed_files_count += 1
                    if progress_callback:
                        progress_callback(f"Processing files: {processed_files_count}/{len(analyzed_file_info)}",
                                         40 + (processed_files_count / len(analyzed_file_info) * 60))
                except Exception as e:
                    if status_callback:
                        status_callback(f"Error processing file {os.path.basename(original_file_path)}: {str(e)}")
        expected_total_chunks_from_metadata = metadata.get("total_chunks", 0)
        actual_chunk_files_count = len(all_created_chunk_paths)
        total_data_chunks = actual_total_file_chunks
        if status_callback:
            status_callback(f"Verification: Final metadata_chunks_count={metadata_chunks_count}, Final total_data_chunks={total_data_chunks}")
            status_callback(f"Verification: metadata dict total_chunks for 'Expected' value={expected_total_chunks_from_metadata}")
            status_callback(f"Verification: Created {actual_chunk_files_count} actual chunk files in {output_dir}.")
            if expected_total_chunks_from_metadata != actual_chunk_files_count and actual_chunk_files_count == (total_data_chunks + metadata_chunks_count):
                status_callback(f"Verification NOTE: 'Expected' ({expected_total_chunks_from_metadata}) differs from actual file count ({actual_chunk_files_count}), but actual matches sum of data+meta chunks ({total_data_chunks + metadata_chunks_count}). This suggests 'total_chunks' in pickled metadata might be stale.")
            elif expected_total_chunks_from_metadata != actual_chunk_files_count:
                status_callback(f"Verification WARNING: Mismatch between metadata dict total_chunks ({expected_total_chunks_from_metadata}) and actual files created ({actual_chunk_files_count}).")
        if status_callback:
            status_callback(f"Successfully processed {len(valid_files_data)} files into {len(all_created_chunk_paths)} chunks (including metadata).")
        return True
    except Exception as e:
        if status_callback: 
            status_callback(f"Critical error in send process: {e}")
        raise

def process_precompressed_data(compressed_data, output_dir, start_seq, total_chunks, 
                               encrypt, key, chunk_size, original_file_path_for_log=""):
    chunk_count_for_this_file = (len(compressed_data) + chunk_size - 1) // chunk_size
    created_chunk_paths = []
    for i in range(chunk_count_for_this_file):
        chunk_data_content = compressed_data[i*chunk_size : min((i+1)*chunk_size, len(compressed_data))]
        chunk_path = process_chunk(chunk_data_content, start_seq + i, total_chunks, output_dir, "CH", encrypt, key)
        created_chunk_paths.append(chunk_path)
    return created_chunk_paths
