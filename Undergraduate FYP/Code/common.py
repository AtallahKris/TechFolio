import os
import re
import hashlib
import shutil
import struct
import numpy as np
import psutil

CHUNK_SIZE = 2895
MAX_FILE_SIZE = 50 * 1024 * 1024  

def get_script_dir():
    return os.path.dirname(os.path.abspath(__file__))

def prepare_output_directory(directory, allow_overwrite=False):
    if os.path.exists(directory):
        if not allow_overwrite:
            if os.listdir(directory):
                return False
        else:
            shutil.rmtree(directory)
            os.makedirs(directory)
    else:
        os.makedirs(directory)
    return True

def string_to_key(key_string): 
    return b'' if not key_string else key_string.encode('utf-8')

def xor_crypt_chunk(data, key, offset=0):
    if not key: 
        raise ValueError("Encryption/decryption key cannot be empty")
    
    key_length = len(key)
    data_length = len(data)
    
    data_view = memoryview(data)
    key_view = memoryview(key)
    
    if data_length <= 256:
        return bytes(data_view[i] ^ key_view[(i + offset) % key_length] for i in range(data_length))
    
    if data_length < 8192:
        result = bytearray(data_length)
        if key_length > 0 and (key_length & (key_length - 1)) == 0:
            key_mask = key_length - 1
            for i in range(data_length):
                result[i] = data_view[i] ^ key_view[(i + offset) & key_mask]
        else:
            if key_length <= 64:
                for i_data in range(data_length):
                    result[i_data] = data_view[i_data] ^ key_view[(i_data + offset) % key_length]
            else: 
                for i in range(data_length):
                    result[i] = data_view[i] ^ key_view[(i + offset) % key_length]
        return bytes(result)
    
    chunk_size = 4 * 1024 * 1024
    
    if data_length <= chunk_size:
        data_array = np.frombuffer(data, dtype=np.uint8)
        key_array = np.frombuffer(key, dtype=np.uint8)
        
        if key_length > 0 and (key_length & (key_length - 1)) == 0:
            indices = (np.arange(data_length, dtype=np.uint32) + offset) & (key_length - 1)
        else:
            indices = (np.arange(data_length, dtype=np.uint32) + offset) % key_length
        
        return np.bitwise_xor(data_array, key_array[indices]).tobytes()
    
    result = bytearray(data_length)
    result_view = memoryview(result)
    
    for chunk_start in range(0, data_length, chunk_size):
        chunk_end = min(chunk_start + chunk_size, data_length)
        chunk_size_actual = chunk_end - chunk_start
        
        chunk_data = data_view[chunk_start:chunk_end]
        chunk_array = np.frombuffer(chunk_data, dtype=np.uint8)
        
        chunk_offset = offset + chunk_start
        if key_length > 0 and (key_length & (key_length - 1)) == 0:
            indices = (np.arange(chunk_size_actual, dtype=np.uint32) + chunk_offset) & (key_length - 1)
        else:
            indices = (np.arange(chunk_size_actual, dtype=np.uint32) + chunk_offset) % key_length
        
        key_array = np.frombuffer(key, dtype=np.uint8)
        chunk_key = key_array[indices]
        
        chunk_result = np.bitwise_xor(chunk_array, chunk_key)
        
        result_view[chunk_start:chunk_end] = chunk_result.tobytes()
    
    return bytes(result)

def calculate_checksum(data):
    if isinstance(data, bytes):
        return hashlib.sha256(data).hexdigest()
    if isinstance(data, str): 
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    return hashlib.sha256(str(data).encode('utf-8')).hexdigest()

_SANITIZE_PATH_REGEX = re.compile(r'[<>:"/\\|?*]')

_CHUNK_FULL_HEADER_LEN = 26
_CHUNK_MAGIC_WORD = b'HEADER'
_CHUNK_HEADER_MAIN_STRUCT = struct.Struct('<IIB8s')
_ORD_M = ord(b'M') 
_ORD_C = ord(b'C')
_ORD_E = ord(b'E') 
_ORD_N = ord(b'N') 
_VERSION_V1 = b'V1'

def sanitize_path(path):
    return _SANITIZE_PATH_REGEX.sub('_', path)

def get_optimal_buffer_size(file_size=None):
    try:
        mem_available = psutil.virtual_memory().available
        default_buffer = 2 * 1024 * 1024
        
        if file_size:
            if file_size < 1024 * 1024:
                return min(file_size, 64 * 1024)
                
            if file_size < 10 * 1024 * 1024:
                return min(file_size // 4, 512 * 1024)
        
        return min(mem_available // 16, 8 * 1024 * 1024)
    except:
        pass
    
    return 2 * 1024 * 1024

def get_optimal_thread_count(task_type="io", total_items=None, file_size=None):
    cpu_count = os.cpu_count() or 4
    
    if total_items is not None and total_items < 100 or (file_size and file_size < 10 * 1024 * 1024):
        return max(2, cpu_count // 2)
    
    try:
        available_memory = psutil.virtual_memory().available
        mem_factor = max(1, min(4, available_memory // (2 * 1024 * 1024 * 1024)))
        
        if task_type == "io":
            return min(6, max(2, cpu_count * mem_factor // 3))
        elif task_type == "cpu_heavy":
            return min(4, max(1, cpu_count * mem_factor // 4))
        else:
            return min(4, max(2, cpu_count * mem_factor // 3))
    except:
        pass
    
    if task_type == "io":
        return min(4, cpu_count)
    elif task_type == "cpu_heavy":
        return min(2, cpu_count)
    else:
        return min(3, cpu_count)

def parse_chunk_header(header_data: bytes) -> dict:
    if len(header_data) < _CHUNK_FULL_HEADER_LEN:
        raise ValueError(f"Header data too short. Expected at least {_CHUNK_FULL_HEADER_LEN} bytes, got {len(header_data)}.")

    if header_data[0:6] != _CHUNK_MAGIC_WORD:
        raise ValueError("Invalid chunk header: Magic word 'HEADER' not found.")

    version_bytes = header_data[6:8]
    if version_bytes != _VERSION_V1:
        raise ValueError(f"Unsupported header version: {version_bytes.decode('ascii', 'ignore')}. Expected '{_VERSION_V1.decode('ascii')}'.")

    chunk_type_byte = header_data[8]
    is_metadata = False
    if chunk_type_byte == _ORD_M:
        is_metadata = True
    elif chunk_type_byte == _ORD_C:
        is_metadata = False
    else:
        raise ValueError(f"Invalid chunk type identifier: {chr(chunk_type_byte)}. Expected 'M' or 'C'.")

    if len(header_data) < 9 + _CHUNK_HEADER_MAIN_STRUCT.size:
        raise ValueError(f"Header data too short for main header struct. Expected {9 + _CHUNK_HEADER_MAIN_STRUCT.size} bytes, got {len(header_data)}.")

    try:
        seq_num, total_count, enc_flag_byte, checksum_bytes = _CHUNK_HEADER_MAIN_STRUCT.unpack_from(header_data, 9)
    except struct.error as e:
        raise ValueError(f"Failed to unpack main header fields (seq, total, enc_flag, checksum): {e}")

    is_encrypted = False
    if enc_flag_byte == _ORD_E:
        is_encrypted = True
    elif enc_flag_byte == _ORD_N:
        is_encrypted = False
    else:
        raise ValueError(f"Invalid encryption flag: {chr(enc_flag_byte)}. Expected 'E' or 'N'.")

    return {
        'is_metadata': is_metadata,
        'sequence_number': seq_num,
        'total_count': total_count,
        'is_encrypted': is_encrypted,
        'checksum': checksum_bytes, 
        'version': version_bytes
    }

def create_chunk_header(is_metadata: bool, sequence_number: int, total_chunks: int, is_encrypted: bool, payload_checksum_bytes: bytes, version: bytes = _VERSION_V1) -> bytes:

    if len(payload_checksum_bytes) != 8:
        raise ValueError("Payload checksum must be 8 bytes.")
    if version != _VERSION_V1:
        raise ValueError(f"Unsupported version for header creation: {version.decode('ascii', 'ignore')}")

    magic_word = _CHUNK_MAGIC_WORD
    version_bytes = version

    chunk_type_byte = _ORD_M if is_metadata else _ORD_C
    encryption_flag_byte = _ORD_E if is_encrypted else _ORD_N

    main_header_part = _CHUNK_HEADER_MAIN_STRUCT.pack(
        sequence_number,
        total_chunks,
        encryption_flag_byte,
        payload_checksum_bytes
    )

    return magic_word + version_bytes + bytes([chunk_type_byte]) + main_header_part