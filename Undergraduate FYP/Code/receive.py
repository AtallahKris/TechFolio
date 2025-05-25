#!/usr/bin/env python3
import os
import zlib
import concurrent.futures
import pickle
import re
import sqlite3
import gc
import time
import hashlib
import struct
from pathlib import Path

from common import (
    CHUNK_SIZE, prepare_output_directory, string_to_key, xor_crypt_chunk,
    calculate_checksum, sanitize_path, get_optimal_buffer_size,
    get_optimal_thread_count, parse_chunk_header
)

def setup_optimized_sqlite_connection():
    try:
        db_conn = sqlite3.connect('file:memdb1?mode=memory&cache=shared', uri=True)
    except sqlite3.OperationalError:
        db_conn = sqlite3.connect(':memory:')
    
    db_conn.execute("PRAGMA journal_mode = OFF")
    db_conn.execute("PRAGMA synchronous = OFF")
    db_conn.execute("PRAGMA cache_size = 200000")
    db_conn.execute("PRAGMA temp_store = MEMORY")
    db_conn.execute("PRAGMA page_size = 32768")
    
    if ':memory:' not in str(db_conn):
        try:
            db_conn.execute("PRAGMA journal_mode = WAL")
        except sqlite3.OperationalError:
            pass
    
    try:
        db_conn.execute("PRAGMA mmap_size = 536870912")
    except sqlite3.OperationalError:
        pass
    
    return db_conn

def process_chunk_file(chunk_file, encrypt=True, key_string="", status_callback=None):
    try:
        if not os.path.exists(chunk_file):
            raise FileNotFoundError(f"Chunk file not found: {chunk_file}")
        
        file_size = os.path.getsize(chunk_file)
        
        key = string_to_key(key_string) if encrypt else None
        
        if file_size > 65536:
            with open(chunk_file, 'rb') as f:
                header_data = f.read(26)
                
                header_info = parse_chunk_header(header_data)
                
                payload = f.read(file_size - 26)
        else:
            with open(chunk_file, 'rb') as f:
                data = f.read()
                
            header_data = data[:26]
            header_info = parse_chunk_header(header_data)
            payload = data[26:]
            data = None
        
        is_metadata = header_info['is_metadata']
        sequence_number = header_info['sequence_number']
        total_count = header_info['total_count']
        is_encrypted = header_info['is_encrypted']
        chunk_checksum = header_info['checksum']
        
        if is_encrypted and encrypt:
            if not key:
                raise ValueError("Decryption key cannot be empty")
            data = xor_crypt_chunk(payload, key, offset=sequence_number * len(payload))
        else:
            data = payload
        
        if not header_info['is_metadata'] and not data and status_callback:
            status_callback(
                f"DIAGNOSTIC: Chunk {os.path.basename(chunk_file)} (seq={header_info['sequence_number']}) " +
                f"is a DATA chunk but has an EMPTY payload after potential decryption. " +
                f"Header checksum from chunk: {header_info['checksum'].hex()}. " +
                f"This chunk might contribute to a 0-byte file if its checksum validates an empty payload."
            )

        calculated_checksum = calculate_checksum(data).encode('utf-8')[:8]
        if calculated_checksum != header_info['checksum']:
            error_message = (
                f"Checksum verification FAILED for chunk {os.path.basename(chunk_file)}. " +
                f"Expected (from header): {header_info['checksum'].hex()}, " +
                f"Calculated (from payload): {calculated_checksum.hex()}. " +
                f"Payload length: {len(data)}. Sequence: {header_info['sequence_number']}."
            )
            if status_callback:
                status_callback(error_message)
            raise ValueError(error_message)
        
        return {
            'sequenceNumber': sequence_number, 
            'totalCount': total_count,
            'isMetadata': is_metadata
        }, data
            
    except Exception as e:
        if status_callback:
            status_callback(f"Error processing chunk {os.path.basename(chunk_file)}: {str(e)}")
        raise

def process_chunks_batch(chunk_files, encrypt, key_string, status_callback=None):
    results = []
    errors = []
    
    for chunk_path in chunk_files:
        try:
            metadata, data = process_chunk_file(chunk_path, encrypt, key_string)
            results.append((chunk_path, metadata, data))
        except Exception as e:
            errors.append((chunk_path, str(e)))
            if status_callback:
                status_callback(f"Error processing chunk {os.path.basename(chunk_path)}: {str(e)}")
    
    return results, errors

def extract_metadata_from_files(metadata_files, encrypt, key_string, status_callback=None):
    if not metadata_files:
        raise ValueError("No metadata files provided")
        
    if status_callback:
        status_callback(f"Extracting metadata from {len(metadata_files)} metadata chunks")
    
    metadata_chunks = []
    errors = []
    
    def get_seq_from_header(file_path):
        try:
            with open(file_path, 'rb') as f:
                header = f.read(26)
            header_info = parse_chunk_header(header)
            return header_info['sequence_number']
        except Exception:
            return float('inf')
    
    metadata_files = sorted(metadata_files, key=get_seq_from_header)
    
    thread_count = min(get_optimal_thread_count(total_items=len(metadata_files)), len(metadata_files), 8)
    
    if len(metadata_files) > 3 and thread_count > 1:
        batch_size = max(1, len(metadata_files) // thread_count)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
            futures = []
            
            for i in range(0, len(metadata_files), batch_size):
                batch = metadata_files[i:min(i+batch_size, len(metadata_files))]
                future = executor.submit(process_chunks_batch, batch, encrypt, key_string, None)
                futures.append((future, i))
            
            for future, batch_idx in futures:
                try:
                    results, batch_errors = future.result()
                    
                    for chunk_path, chunk_metadata, chunk_data in results:
                        metadata_chunks.append((chunk_metadata, chunk_data))
                    
                    errors.extend(batch_errors)
                    
                    if status_callback and batch_errors:
                        status_callback(f"Warning: Failed to process {len(batch_errors)} metadata chunks in batch {batch_idx}")
                        
                except Exception as e:
                    if status_callback:
                        status_callback(f"Error processing metadata batch {batch_idx}: {str(e)}")
    else:
        for file_path in metadata_files:
            try:
                metadata, data = process_chunk_file(file_path, encrypt, key_string, status_callback)
                metadata_chunks.append((metadata, data))
            except Exception as e:
                errors.append((file_path, str(e)))
                if status_callback:
                    status_callback(f"Warning: Failed to process metadata chunk {os.path.basename(file_path)}: {str(e)}")
    
    if not metadata_chunks:
        error_msg = "No metadata could be processed"
        if errors:
            try:
                file_name = os.path.basename(errors[0][0]) if isinstance(errors[0][0], str) else "Unknown"
                error_msg += f". First error: {file_name}: {errors[0][1]}"
            except Exception:
                error_msg += f". Errors occurred but details could not be retrieved"
        raise ValueError(error_msg)
    
    metadata_chunks.sort(key=lambda x: x[0]['sequenceNumber'])
    
    try:
        decompressor = zlib.decompressobj()
        decompressed_data = bytearray()
        
        for _, chunk_data in metadata_chunks:
            decompressed_chunk = decompressor.decompress(chunk_data)
            decompressed_data.extend(decompressed_chunk)
        
        final_data = decompressor.flush()
        if final_data:
            decompressed_data.extend(final_data)
            
        metadata = pickle.loads(bytes(decompressed_data))
        
        if not isinstance(metadata, dict) or 'files' not in metadata:
            raise ValueError("Invalid metadata format: missing required fields")
        
        for file_info in metadata.get('files', []):
            if 'path' not in file_info or 'start_sequence' not in file_info or 'chunk_count' not in file_info:
                raise ValueError("Invalid file metadata: missing required fields")
        
        return metadata
    except zlib.error as e:
        if status_callback:
            status_callback(f"Error decompressing metadata: {str(e)}")
        raise ValueError(f"Failed to decompress metadata: {str(e)}")
    except pickle.UnpicklingError as e:
        if status_callback:
            status_callback(f"Error parsing metadata: {str(e)}")
        raise ValueError(f"Failed to parse metadata: {str(e)}")
    except Exception as e:
        if status_callback:
            status_callback(f"Error processing metadata: {str(e)}")
        raise ValueError(f"Failed to decompress or parse metadata: {str(e)}")

def process_chunks_streaming(chunk_files, output_path, encrypt, key_string, 
                           status_callback=None, cancel_check=None, 
                           progress_callback=None, progress_range=(0, 100)):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    buffer_size = get_optimal_buffer_size()
    
    key = string_to_key(key_string) if encrypt else None
    
    detailed_logging_active = True 

    try:
        total_chunks = len(chunk_files)
        if total_chunks == 0:
            return True
            
        estimated_total_size = total_chunks * CHUNK_SIZE
        
        if total_chunks <= 50:
            batch_size = total_chunks
        elif total_chunks <= 500:
            batch_size = 50
        elif total_chunks <= 5000:
            batch_size = 100
        else:
            batch_size = 200
    
        total_batches = (total_chunks + batch_size - 1) // batch_size
        
        if total_chunks <= 10:
            thread_count = 1
        elif total_chunks <= 100 or estimated_total_size < 5 * 1024 * 1024:
            thread_count = min(2, get_optimal_thread_count(total_items=total_chunks))
        else:
            thread_count = get_optimal_thread_count(total_items=total_chunks, file_size=estimated_total_size)
        
        start_progress, end_progress = progress_range
        
        def extract_seq_from_filename(filename):
            try:
                parts = os.path.basename(filename).split('_')
                if len(parts) >= 2:
                    return int(parts[1])
            except (ValueError, IndexError):
                pass
            return None
            
        def get_seq_num(chunk_path):
            seq = extract_seq_from_filename(chunk_path)
            if seq is not None:
                return seq
                
            try:
                with open(chunk_path, 'rb') as f:
                    header = f.read(26)
                header_info = parse_chunk_header(header)
                return header_info['sequence_number']
            except Exception:
                return float('inf')
        
        need_to_sort = True
        
        if len(chunk_files) > 5:
            sample_files = chunk_files[:min(10, len(chunk_files))]
            seq_nums = [extract_seq_from_filename(f) for f in sample_files]
            
            if all(s is not None for s in seq_nums):
                is_ordered = True
                for i in range(len(seq_nums) - 1):
                    if seq_nums[i] > seq_nums[i + 1]:
                        is_ordered = False
                        break
                if is_ordered:
                    need_to_sort = False

        if need_to_sort:
            if status_callback:
                status_callback("Sorting chunk files by sequence number...")
            chunk_files = sorted(chunk_files, key=get_seq_num)
        
        if cancel_check and cancel_check():
            if status_callback:
                status_callback("Operation cancelled")
            return False
        
        processed_chunks_count = 0
        last_progress_update_time = time.time()
        
        update_frequency = 0.5
        if estimated_total_size <= 10 * 1024 * 1024:
            update_frequency = 0.25
        elif estimated_total_size > 100 * 1024 * 1024:
            update_frequency = 1.0
        
        def update_progress(batch_idx, batch_processed_count=0, force=False):
            nonlocal last_progress_update_time
            current_time = time.time()
            
            if force or (current_time - last_progress_update_time >= update_frequency):
                last_progress_update_time = current_time
                
                total_processed = processed_chunks_count + batch_processed_count
                progress_pct = start_progress + ((total_processed / total_chunks) * (end_progress - start_progress))
                
                if progress_callback:
                    progress_callback(f"Processing chunks: {total_processed}/{total_chunks}", progress_pct)
        
        with open(output_path, 'wb', buffering=buffer_size) as output_file:
            decompressor = zlib.decompressobj()
            
            for batch_idx in range(total_batches):
                if cancel_check and cancel_check():
                    if status_callback:
                        status_callback("Operation cancelled")
                    return False
                
                start_idx = batch_idx * batch_size
                end_idx = min((batch_idx + 1) * batch_size, total_chunks)
                current_batch = chunk_files[start_idx:end_idx]
                
                if thread_count > 1 and len(current_batch) > 3:
                    chunk_results = []
                    sub_batch_size = max(1, len(current_batch) // thread_count)
                    
                    with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
                        futures = []
                        for sub_batch_start in range(0, len(current_batch), sub_batch_size):
                            sub_batch_end = min(sub_batch_start + sub_batch_size, len(current_batch))
                            sub_batch = current_batch[sub_batch_start:sub_batch_end]
                            
                            future = executor.submit(process_chunks_batch, sub_batch, encrypt, key_string, None)
                            futures.append((future, sub_batch_start))
                        
                        for future, sub_idx in futures:
                            try:
                                results, errors = future.result()
                                if errors and status_callback:
                                    status_callback(f"Batch {batch_idx}, sub-batch starting {sub_idx}: encountered {len(errors)} errors during chunk processing.")
                                
                                results.sort(key=lambda x: x[1]['sequenceNumber'])
                                
                                for chunk_path_processed, metadata, chunk_data in results:
                                    if status_callback and detailed_logging_active:
                                        status_callback(f"Decompressing chunk (batch {batch_idx}, sub {sub_idx}) seq: {metadata['sequenceNumber']}, input data length: {len(chunk_data)}, first 10 input bytes: {chunk_data[:10].hex() if chunk_data else 'EMPTY_INPUT'}")
                                    
                                    decompressed_data = decompressor.decompress(chunk_data)
                                    
                                    if status_callback and detailed_logging_active:
                                        status_callback(f"Decompressed chunk (batch {batch_idx}, sub {sub_idx}) seq: {metadata['sequenceNumber']}, output data length: {len(decompressed_data)}, first 10 output bytes: {decompressed_data[:10].hex() if decompressed_data else 'EMPTY_OUTPUT'}")

                                    bytes_written = output_file.write(decompressed_data)
                                    
                                    if status_callback and detailed_logging_active:
                                        status_callback(f"Wrote {bytes_written} decompressed bytes for seq {metadata['sequenceNumber']} to {output_path}. Decompressed size: {len(decompressed_data)}")
                                    
                                    chunk_data = None 
                                    decompressed_data = None
                                    processed_chunks_count +=1
                                    
                            except Exception as e:
                                if status_callback:
                                    status_callback(f"Error processing sub-batch {sub_idx} in batch {batch_idx}: {str(e)}")
                        update_progress(batch_idx, force=True)
                else:
                    for chunk_path in current_batch:
                        if cancel_check and cancel_check():
                            if status_callback: status_callback("Operation cancelled")
                            return False
                        try:
                            metadata, data = process_chunk_file(chunk_path, encrypt, key_string)
                            if status_callback and detailed_logging_active:
                                status_callback(f"Decompressing chunk (single-thread) seq: {metadata['sequenceNumber']}, input data length: {len(data)}, first 10 input bytes: {data[:10].hex() if data else 'EMPTY_INPUT'}")
                            
                            decompressed_data = decompressor.decompress(data)

                            if status_callback and detailed_logging_active:
                                status_callback(f"Decompressed chunk (single-thread) seq: {metadata['sequenceNumber']}, output data length: {len(decompressed_data)}, first 10 output bytes: {decompressed_data[:10].hex() if decompressed_data else 'EMPTY_OUTPUT'}")

                            bytes_written = output_file.write(decompressed_data)
                            if status_callback and detailed_logging_active:
                                status_callback(f"Wrote {bytes_written} decompressed bytes (single-thread) for seq {metadata['sequenceNumber']} to {output_path}. Decompressed size: {len(decompressed_data)}")

                            data = None 
                            decompressed_data = None
                            processed_chunks_count += 1
                            update_progress(batch_idx, batch_processed_count= (processed_chunks_count - start_idx * batch_size) )


                        except Exception as e:
                            if status_callback:
                                status_callback(f"Error processing chunk {os.path.basename(chunk_path)}: {str(e)}")
            
            final_decompressed_data = decompressor.flush()
            if status_callback:
                if final_decompressed_data:
                    status_callback(f"Decompressor flushed {len(final_decompressed_data)} bytes for {output_path}.")
                else:
                    status_callback(f"Decompressor flushed 0 bytes for {output_path}.")

            if final_decompressed_data:
                bytes_written = output_file.write(final_decompressed_data)
                if status_callback:
                    status_callback(f"Wrote {bytes_written} final flushed decompressed bytes to {output_path}.")
            
            output_file.flush()
            os.fsync(output_file.fileno())
            final_size = output_file.tell()
            if status_callback:
                status_callback(f"File {output_path} final position in stream: {final_size} bytes before closing.")

        if os.path.exists(output_path):
            actual_os_size = os.path.getsize(output_path)
            if status_callback:
                status_callback(f"File {output_path} size on disk after closing: {actual_os_size} bytes.")
        else:
            if status_callback:
                status_callback(f"File {output_path} does NOT exist on disk after processing (this is unexpected).")
        
        update_progress(total_batches, force=True)

        if total_chunks > 0 and os.path.exists(output_path) and os.path.getsize(output_path) == 0:
            if status_callback:
                status_callback(f"CRITICAL WARNING: File {output_path} is 0 bytes after processing {total_chunks} chunks.")

        return True
    except MemoryError:
        if status_callback:
            status_callback("Error: Insufficient memory to process chunks")
        return False
        
    except Exception as e:
        if status_callback:
            status_callback(f"Error processing chunks: {str(e)}")
        raise

def validate_and_get_type(file_path):
    try:
        if not os.path.exists(file_path):
            return None
            
        with open(file_path, 'rb') as f:
            header = f.read(26)
        
        if header[:6] != b'HEADER':
            return None
            
        header_info = parse_chunk_header(header)
        return 'MD' if header_info['is_metadata'] else 'CH'
    except Exception:
        return None

def analyze_chunks_in_db(chunk_files, db_conn, status_callback=None):
    db_cursor = db_conn.cursor()
    total_chunks = len(chunk_files)
    
    db_cursor.execute('''CREATE TABLE IF NOT EXISTS chunks (
        seq_num INTEGER PRIMARY KEY, 
        total_count INTEGER,
        chunk_type TEXT,
        file_path TEXT
    )''')
    
    batch_size = min(5000, max(1000, total_chunks // 10))
    
    db_conn.execute("BEGIN TRANSACTION")
    
    chunks_processed = 0
    current_batch = []
    
    try:
        for chunk_path in chunk_files:
            if not os.path.exists(chunk_path):
                continue
                
            try:
                with open(chunk_path, 'rb') as f:
                    header = f.read(26)
                    
                header_info = parse_chunk_header(header)
                chunk_type = 'MD' if header_info['is_metadata'] else 'CH'
                seq_num = header_info['sequence_number']
                total_count = header_info['total_count']
                
                current_batch.append((seq_num, total_count, chunk_type, chunk_path))
                chunks_processed += 1
                
                if len(current_batch) >= batch_size:
                    db_cursor.executemany("INSERT OR REPLACE INTO chunks VALUES (?, ?, ?, ?)", current_batch)
                    db_conn.commit()
                    current_batch = []
            except Exception as e:
                if status_callback:
                    status_callback(f"Error analyzing chunk {os.path.basename(chunk_path)}: {str(e)}")
        
        if current_batch:
            db_cursor.executemany("INSERT OR REPLACE INTO chunks VALUES (?, ?, ?, ?)", current_batch)
            db_conn.commit()
            
        db_cursor.execute("CREATE INDEX IF NOT EXISTS idx_type ON chunks(chunk_type)")
        db_conn.commit()
        
        return chunks_processed
        
    except Exception as e:
        db_conn.rollback()
        if status_callback:
            status_callback(f"Error during chunk analysis: {str(e)}")
        raise

def reassemble_files(chunk_files, output_dir, encrypt=True, key_string="", 
                    progress_callback=None, status_callback=None, cancel_check=None, force=False):
    try:
        if not prepare_output_directory(output_dir, allow_overwrite=force):
            if status_callback:
                status_callback(f"Output directory {output_dir} is not empty. Use --force to overwrite.")
            return False
            
        if status_callback:
            status_callback(f"Processing {len(chunk_files)} chunks")
        
        stages = [
            ("Analyzing chunks", 0, 30),
            ("Processing metadata", 30, 40),
            ("Reassembling files", 40, 100)
        ]
        
        if status_callback:
            status_callback(f"Stage 1: {stages[0][0]}")
        
        db_conn = setup_optimized_sqlite_connection()
        
        chunks_processed = analyze_chunks_in_db(chunk_files, db_conn, status_callback)
        
        if chunks_processed == 0:
            if status_callback:
                status_callback("Error: No chunks could be analyzed")
            db_conn.close()
            return False
            
        if cancel_check and cancel_check():
            if status_callback:
                status_callback("Operation cancelled")
            db_conn.close()
            return False
        
        if status_callback:
            status_callback(f"Analyzed {chunks_processed} chunks")
        
        if progress_callback:
            progress_callback("Chunk analysis complete", stages[1][1])
        
        if status_callback:
            status_callback(f"Stage 2: {stages[1][0]}")
        
        db_cursor = db_conn.cursor()
        db_cursor.execute("SELECT file_path FROM chunks WHERE chunk_type = 'MD' ORDER BY seq_num")
        metadata_files = [row[0] for row in db_cursor.fetchall()]
        
        if not metadata_files:
            if status_callback:
                status_callback("Error: No metadata chunks found")
            db_conn.close()
            return False
        
        metadata = extract_metadata_from_files(metadata_files, encrypt, key_string, status_callback)
        
        if status_callback:
            file_count = len(metadata.get('files', []))
            status_callback(f"Found {file_count} files in metadata")
        
        if metadata.get('encrypted', False) != encrypt:
            if status_callback:
                if metadata.get('encrypted', False):
                    status_callback("Error: Chunks are encrypted but decryption not enabled")
                else:
                    status_callback("Error: Decryption enabled but chunks are not encrypted")
            db_conn.close()
            return False
        
        if encrypt and metadata.get('key_verification'):
            if metadata.get('key_verification') != calculate_checksum(string_to_key(key_string)):
                if status_callback:
                    status_callback("Error: Invalid decryption key")
                db_conn.close()
                return False
        
        if progress_callback:
            progress_callback("Metadata processed", stages[2][1])
        
        if status_callback:
            status_callback(f"Stage 3: {stages[2][0]}")
        
        total_data_chunks = sum(file_info.get('chunk_count', 0) for file_info in metadata['files'])
        if status_callback:
            status_callback(f"Processing {total_data_chunks} data chunks across {len(metadata['files'])} files")
        
        file_thread_count = get_optimal_thread_count(total_items=len(metadata['files']))
        
        processed_target_paths = {}
        for file_info in metadata['files']:
            desired_rel_path = file_info.get('original_path', file_info['path'])

            if desired_rel_path in processed_target_paths:
                path_obj = Path(desired_rel_path)
                new_filename = f"{path_obj.stem}_{file_info['start_sequence']}{path_obj.suffix}"
                file_info['path'] = str(path_obj.parent / new_filename)
            else:
                file_info['path'] = desired_rel_path
            
            processed_target_paths[desired_rel_path] = True
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=file_thread_count) as thread_pool:
            file_futures = []
            
            for file_idx, file_info in enumerate(metadata['files']):
                if cancel_check and cancel_check():
                    if status_callback:
                        status_callback("Operation cancelled")
                    db_conn.close()
                    return False
                
                start_seq = file_info['start_sequence']
                chunk_count = file_info['chunk_count']
                
                db_cursor.execute(
                    "SELECT file_path FROM chunks WHERE chunk_type = 'CH' AND seq_num >= ? AND seq_num < ? ORDER BY seq_num",
                    (start_seq, start_seq + chunk_count)
                )
                file_chunks = [row[0] for row in db_cursor.fetchall()]
                
                current_file_path = file_info.get('path', '')
                if status_callback:
                    status_callback(f"DEBUG_REASSEMBLE: File {current_file_path}, StartSeq: {start_seq}, ChunkCount: {chunk_count}, Identified Chunks: {len(file_chunks)} chunks: {file_chunks[:5]}...")

                if len(file_chunks) != chunk_count:
                    if status_callback:
                        status_callback(f"Warning: Missing chunks for {file_info['path']} " +
                                      f"(found {len(file_chunks)}/{chunk_count})")
                    if len(file_chunks) == 0:
                        continue
                
                rel_path = file_info['path']
                output_path = os.path.join(output_dir, rel_path)
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                def process_file(file_chunks, output_path, file_info, file_idx):
                    try:
                        if cancel_check and cancel_check():
                            if status_callback:
                                status_callback(f"Skipping file {file_info['path']} - operation cancelled")
                            return False
                        
                        if total_data_chunks > 0:
                            progress_chunks = sum(f.get('chunk_count', 0) for f in metadata['files'][:file_idx])
                            start_pct = 40 + (progress_chunks / total_data_chunks * 60)
                            chunk_ratio = file_info['chunk_count'] / total_data_chunks
                            end_pct = start_pct + (chunk_ratio * 60)
                            file_progress_range = (start_pct, end_pct)
                        else:
                            file_progress_range = (40, 100)
                        
                        result = process_chunks_streaming(
                            file_chunks, output_path, encrypt, key_string, 
                            status_callback, cancel_check, 
                            progress_callback, file_progress_range
                        )
                        
                        if result is False:
                            if status_callback:
                                status_callback(f"File {file_info['path']} - processing failed or cancelled")
                            return False
                        
                        if os.path.exists(output_path):
                            actual_size = os.path.getsize(output_path)
                            expected_size = file_info.get('size', 0)
                            
                            expected_checksum = file_info.get('checksum')
                            file_verified = False
                            if expected_checksum:
                                try:
                                    with open(output_path, 'rb') as f_check:
                                        actual_checksum = calculate_checksum(f_check.read())
                                    if actual_checksum == expected_checksum:
                                        if status_callback:
                                            status_callback(f"Checksum VERIFIED for {file_info['path']}. Size: {actual_size} (Expected: {expected_size})")
                                        file_verified = True
                                    else:
                                        if status_callback:
                                            status_callback(f"CRITICAL: Checksum MISMATCH for {file_info['path']}. " +
                                                          f"Expected {expected_checksum}, got {actual_checksum}. " +
                                                          f"File size: {actual_size} (Expected: {expected_size}).")
                                except Exception as cs_ex:
                                    if status_callback:
                                        status_callback(f"Error calculating checksum for {file_info['path']}: {cs_ex}")

                            else:
                                if status_callback:
                                    status_callback(f"No checksum in metadata to verify for {file_info['path']}.")
                                file_verified = True

                            if expected_size > 0 and actual_size != expected_size:
                                if status_callback:
                                    status_callback(f"Warning: Size MISMATCH for {file_info['path']}. " +
                                                  f"Expected {expected_size} bytes, got {actual_size} bytes.")
                                if not file_verified:
                                     pass
                            elif actual_size == expected_size and not expected_checksum:
                                if status_callback:
                                     status_callback(f"Size MATCHED for {file_info['path']} (no checksum for full verification).")
                            elif expected_size == 0 and actual_size == 0:
                                if status_callback:
                                    status_callback(f"Correctly processed empty file: {file_info['path']}")
                                file_verified = True

                            if file_verified and actual_size == expected_size:
                                if status_callback:
                                    status_callback(f"Successfully reconstructed and verified: {file_info['path']}")
                            elif file_verified and expected_size == 0 and actual_size == 0:
                                if status_callback:
                                    status_callback(f"Successfully reconstructed (empty file verified): {file_info['path']}")
                            elif file_verified and actual_size != expected_size:
                                 if status_callback:
                                    status_callback(f"Notice: Checksum VERIFIED for {file_info['path']}, but size differs. Expected {expected_size}, got {actual_size}. Content is likely correct.")
                            else:
                                if status_callback:
                                    status_callback(f"Failed to fully verify {file_info['path']}. Verified: {file_verified}, Expected Size: {expected_size}, Actual Size: {actual_size}")
                                return False

                        else:
                            if file_info.get('size', 0) == 0:
                                if status_callback:
                                    status_callback(f"Successfully processed expected empty file (not created on disk): {file_info['path']}")
                            else:
                                if status_callback:
                                    status_callback(f"Error: Output file NOT CREATED for {file_info['path']} (and it was not expected to be empty).")
                                return False
                        
                        return True
                    except Exception as e:
                        if status_callback:
                            status_callback(f"Error processing {file_info['path']}: {str(e)}")
                        return False
                
                future = thread_pool.submit(
                    process_file, file_chunks, output_path, file_info, file_idx
                )
                file_futures.append(future)
                
                max_concurrent = min(3, file_thread_count)
                if len(file_futures) >= max_concurrent:
                    done, file_futures_set = concurrent.futures.wait(
                        file_futures, 
                        return_when=concurrent.futures.FIRST_COMPLETED
                    )
                    file_futures = list(file_futures_set)
                    
                    gc.collect()
            
            if file_futures:
                done, _ = concurrent.futures.wait(file_futures)
                failed_files = 0
                for future in done:
                    try:
                        if future.exception():
                            if status_callback:
                                status_callback(f"Error in file processing: {future.exception()}")
                            failed_files += 1
                        elif not future.result():
                            failed_files += 1
                    except concurrent.futures.CancelledError:
                        pass
                
                if failed_files > 0 and status_callback:
                    status_callback(f"Warning: {failed_files} files failed to process correctly")
        
        db_conn.close()
        
        if status_callback:
            status_callback("File reassembly completed")
        
        return True
    
    except MemoryError:
        if status_callback:
            status_callback("Error: Insufficient memory to process chunks")
        raise
    
    except Exception as e:
        if status_callback:
            status_callback(f"Error: {str(e)}")
        raise