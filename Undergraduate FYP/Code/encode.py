import os
import numpy as np
import cv2
import struct
from reedsolo import RSCodec
import argparse
import logging

VERSION = 8
COLOR = 8
ERROR = 10
MODULES = 100
N_SYMBOLS = 3635
K_SYMBOLS = 2895

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

QZ = ((MODULES + 8) - MODULES) // 2
RS_OFFSET = 0

NUM_RS_BLOCKS = 15
n_sym_per_block = 241
k_sym_per_block = 193
N_SYMBOLS_EFFECTIVE = NUM_RS_BLOCKS * n_sym_per_block
K_SYMBOLS_EFFECTIVE = NUM_RS_BLOCKS * k_sym_per_block


def is_valid_for_data(r_0idx, c_0idx, image_width_modules, image_height_modules):
    if not (0 <= r_0idx < image_height_modules and 0 <= c_0idx < image_width_modules):
        return False

    fp_size = 7
    m = MODULES

    tl_fp_r_start, tl_fp_c_start = 4, 4
    if (tl_fp_r_start <= r_0idx < tl_fp_r_start + fp_size) and \
       (tl_fp_c_start <= c_0idx < tl_fp_c_start + fp_size):
        return False

    tr_fp_r_start, tr_fp_c_start = 4, m - 3
    if (tr_fp_r_start <= r_0idx < tr_fp_r_start + fp_size) and \
       (tr_fp_c_start <= c_0idx < tr_fp_c_start + fp_size):
        return False

    bl_fp_r_start, bl_fp_c_start = m - 3, 4
    if (bl_fp_r_start <= r_0idx < bl_fp_r_start + fp_size) and \
       (bl_fp_c_start <= c_0idx < bl_fp_c_start + fp_size):
        return False

    br_fp_r_start, br_fp_c_start = m - 3, m - 3
    if (br_fp_r_start <= r_0idx < br_fp_r_start + fp_size) and \
       (br_fp_c_start <= c_0idx < br_fp_c_start + fp_size):
        return False

    return True


def encode_chunk_to_c_COLOR(chunk_data, output_path, scale_factor=10):
    if len(chunk_data) > K_SYMBOLS:
        raise ValueError(f"Chunk size {len(chunk_data)} exceeds maximum of {K_SYMBOLS} bytes (Adjusted Capacity K_eff)")

    num_bytes = len(chunk_data)
    bch_data = encode_bch_metadata(num_bytes)

    rs_data = reed_solomon_encode(chunk_data)

    c_COLOR_image = create_c_COLOR_pattern(rs_data, bch_data)

    if scale_factor > 1:
        enlarged_image = cv2.resize(c_COLOR_image, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_NEAREST)
    else:
        enlarged_image = c_COLOR_image

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    cv2.imwrite(output_path, enlarged_image, [cv2.IMWRITE_PNG_COMPRESSION, 0])

    return output_path


def encode_bch_metadata(num_bytes):
    num_bytes_bin_str = format(num_bytes, '012b')

    if not (1 <= VERSION <= 8):
        logger.error(f"VERSION {VERSION} is out of range 1-8. Defaulting version_code to 7 (for VERSION 8).")
        version_code = 7
    else:
        version_code = VERSION - 1
    version_bin_str = format(version_code, '03b')

    if not (1 <= COLOR <= 8):
        logger.error(f"COLOR {COLOR} is out of range 1-8. Defaulting color_code to 7 (for COLOR 8).")
        color_code = 7
    else:
        color_code = COLOR - 1
    color_code_bin_str = format(color_code, '03b')
    metadata_18_bits_str = num_bytes_bin_str + version_bin_str + color_code_bin_str

    logger.info(f"[encode_bch_metadata] Encoding num_bytes: {num_bytes} -> num_bytes_bin_str: '{num_bytes_bin_str}'")
    logger.info(f"[encode_bch_metadata] Encoding version_code: {version_code} -> version_bin_str: '{version_bin_str}' (for VERSION {VERSION})")
    logger.info(f"[encode_bch_metadata] Encoding color_code: {color_code} -> color_code_bin_str: '{color_code_bin_str}' (for COLOR {COLOR})")
    logger.info(f"[encode_bch_metadata] Full 18-bit metadata string being generated: '{metadata_18_bits_str}'")

    metadata_18_bits_list = [int(bit) for bit in metadata_18_bits_str]

    if len(metadata_18_bits_list) != 18:
        logger.error(f"Generated metadata string is not 18 bits: {len(metadata_18_bits_list)}. This is a bug.")
        metadata_18_bits_list = ([0] * 12) + ([1] * 3) + ([1]*3)

    logger.warning("Actual BCH (63,18) encoding is NOT performed. Using raw 18 metadata bits, zero-padded to 63, then one final zero for 64 bits.")
    bch_encoded_bits_63 = metadata_18_bits_list + ([0] * (63 - 18))

    final_bch_bits_64 = bch_encoded_bits_63 + [0]

    return final_bch_bits_64


def reed_solomon_encode(data_bytes):
    num_blocks = NUM_RS_BLOCKS
    k_per_block = k_sym_per_block
    n_per_block = n_sym_per_block

    logger.info(f"RS Encoding: Effective K_SYMBOLS_EFFECTIVE: {K_SYMBOLS_EFFECTIVE}")
    logger.info(f"RS Encoding: Effective N_SYMBOLS_EFFECTIVE: {N_SYMBOLS_EFFECTIVE}")
    logger.info(f"RS Encoding: Global N_SYMBOLS for pixel path: {N_SYMBOLS}")

    k_block_defs = [k_per_block] * num_blocks
    n_block_defs = [n_per_block] * num_blocks

    if sum(k_block_defs) != K_SYMBOLS_EFFECTIVE:
        raise ValueError(f"Custom k_block_defs sum {sum(k_block_defs)} != K_SYMBOLS_EFFECTIVE {K_SYMBOLS_EFFECTIVE}")
    if sum(n_block_defs) != N_SYMBOLS_EFFECTIVE:
        raise ValueError(f"Custom n_block_defs sum {sum(n_block_defs)} != N_SYMBOLS_EFFECTIVE {N_SYMBOLS_EFFECTIVE}")

    nsym_block_defs = [n - k for n, k in zip(n_block_defs, k_block_defs)]

    padded_data = bytearray(data_bytes)
    if len(padded_data) < K_SYMBOLS_EFFECTIVE:
        num_padding_bytes = K_SYMBOLS_EFFECTIVE - len(padded_data)
        logger.info(f"Padding input data with {num_padding_bytes} random bytes to reach {K_SYMBOLS_EFFECTIVE} bytes for RS encoding.")
        padded_data.extend(os.urandom(num_padding_bytes))
    elif len(padded_data) > K_SYMBOLS_EFFECTIVE:
        logger.warning(f"Input data length {len(padded_data)} exceeds K_SYMBOLS_EFFECTIVE {K_SYMBOLS_EFFECTIVE}. Truncating.")
        padded_data = padded_data[:K_SYMBOLS_EFFECTIVE]

    all_encoded_data = bytearray()
    current_data_idx = 0

    for i in range(len(k_block_defs)):
        k_val = k_block_defs[i]
        n_val = n_block_defs[i]
        nsym_val = nsym_block_defs[i]

        rs_encoder = RSCodec(nsym=nsym_val, nsize=n_val)

        data_segment = padded_data[current_data_idx: current_data_idx + k_val]
        current_data_idx += k_val

        if len(data_segment) < k_val:
            data_segment.extend([0] * (k_val - len(data_segment)))

        encoded_segment = rs_encoder.encode(bytes(data_segment))
        all_encoded_data.extend(encoded_segment)

    if len(all_encoded_data) != N_SYMBOLS_EFFECTIVE:
        logger.error(f"CRITICAL: Multi-block RS encoding produced {len(all_encoded_data)} bytes, expected {N_SYMBOLS_EFFECTIVE} bytes.")

    final_rs_data_for_placement = bytearray(all_encoded_data)
    if len(final_rs_data_for_placement) < N_SYMBOLS:
        padding_to_global_n = N_SYMBOLS - len(final_rs_data_for_placement)
        logger.info(f"Padding RS encoded data (len {len(final_rs_data_for_placement)}) with {padding_to_global_n} zero bytes to reach global N_SYMBOLS ({N_SYMBOLS}) for pixel placement.")
        final_rs_data_for_placement.extend(bytes(padding_to_global_n))
    elif len(final_rs_data_for_placement) > N_SYMBOLS:
        logger.warning(f"RS encoded data ({len(final_rs_data_for_placement)}) is longer than global N_SYMBOLS ({N_SYMBOLS}). Truncating for pixel placement.")
        final_rs_data_for_placement = final_rs_data_for_placement[:N_SYMBOLS]

    return bytes(final_rs_data_for_placement)


def create_c_COLOR_pattern(rs_data, bch_data):
    image_size = MODULES + 8
    c_COLOR = np.ones((image_size, image_size, 3), dtype=np.uint8) * 255

    add_finder_patterns(c_COLOR)
    place_bch_data(c_COLOR, bch_data)
    place_rs_data(c_COLOR, rs_data)

    return c_COLOR


def add_finder_patterns(image):
    pattern_corrected = np.zeros((7, 7, 3), dtype=np.uint8)
    pattern_corrected[1:6, 1:6, :] = 255
    pattern_corrected[2:5, 2:5, :] = 0

    fp_size = 7

    tl_r, tl_c = 4, 4
    image[tl_r: tl_r + fp_size, tl_c: tl_c + fp_size] = pattern_corrected

    bl_r, bl_c = (MODULES - 3), 4
    image[bl_r: bl_r + fp_size, bl_c: bl_c + fp_size] = pattern_corrected

    tr_r, tr_c = 4, (MODULES - 3)
    image[tr_r: tr_r + fp_size, tr_c: tr_c + fp_size] = pattern_corrected

    br_r, br_c = (MODULES - 3), (MODULES - 3)
    image[br_r: br_r + fp_size, br_c: br_c + fp_size] = pattern_corrected


def place_bch_data(image, bch_data):
    if len(bch_data) != 64:
        logger.error(f"BCH data must be 64 bits long, got {len(bch_data)}. Skipping.")
        return

    def get_bch_color_for_2bits(bits_pair_tuple):
        bits_pair = list(bits_pair_tuple)
        if bits_pair == [0, 0]: return [0, 0, 255]
        if bits_pair == [0, 1]: return [0, 255, 0]
        if bits_pair == [1, 0]: return [255, 0, 0]
        if bits_pair == [1, 1]: return [255, 255, 255]
        logger.warning(f"Invalid 2-bit pair for BCH color: {bits_pair}")
        return [128, 128, 128]

    bit_idx = 0
    pixels_placed = 0

    coords_path1 = []
    for x_mat_1idx in range(MODULES + 4, (MODULES - 3) - 1, -1):
        coords_path1.append({'r': 13 - 1, 'c': x_mat_1idx - 1})

    coords_path2 = []
    for y_mat_1idx in range(12, 5 - 1, -1):
        coords_path2.append({'r': y_mat_1idx - 1, 'c': 13 - 1})

    coords_path3 = []
    for x_mat_1idx in range(12, 5 - 1, -1):
        coords_path3.append({'r': 13 - 1, 'c': x_mat_1idx - 1})

    coords_path4 = []
    row_path4_0idx = (MODULES - 4) - 1
    for x_mat_1idx in range(12, 5 - 1, -1):
        coords_path4.append({'r': row_path4_0idx, 'c': x_mat_1idx - 1})

    full_bch_path = coords_path1 + coords_path2 + coords_path3 + coords_path4

    if len(full_bch_path) != 32:
        logger.error(f"BCH placement path has {len(full_bch_path)} pixels, expected 32. BCH will be incorrect.")
        return

    image_height, image_width = image.shape[:2]
    for coord in full_bch_path:
        r, c = coord['r'], coord['c']
        if not is_valid_for_data(r, c, image_width, image_height):
            logger.error(f"BCH coord ({r},{c}) is invalid (FP or OOB). Skipping this BCH pixel.")
            continue

        if bit_idx <= len(bch_data) - 2:
            bits_pair_tuple = tuple(bch_data[bit_idx: bit_idx + 2])
            color = get_bch_color_for_2bits(bits_pair_tuple)
            image[r, c] = color
            pixels_placed += 1
            bit_idx += 2
        else:
            logger.warning("Ran out of BCH bits during placement.")
            break

    if pixels_placed != 32 or bit_idx != 64:
        logger.warning(f"BCH placement: {pixels_placed} pixels, {bit_idx} bits. Expected 32 pixels, 64 bits.")


def get_color_for_bits(bits_tuple):
    bits = list(bits_tuple)
    color_code = (bits[0] << 2) | (bits[1] << 1) | bits[2]
    colors = {
        0: [0, 0, 255],
        1: [0, 255, 0],
        2: [255, 0, 0],
        3: [0, 255, 255],
        4: [255, 0, 255],
        5: [255, 255, 0],
        6: [255, 255, 255],
        7: [0, 0, 0]
    }
    return colors.get(color_code, [128, 128, 128])


def place_rs_data(image, rs_data):
    image_height, image_width = image.shape[:2]

    data_bits = []
    for byte_val in rs_data:
        for i in range(7, -1, -1):
            data_bits.append((byte_val >> i) & 1)

    remainder = len(data_bits) % 3
    if remainder != 0:
        padding_needed = 3 - remainder
        data_bits.extend([0] * padding_needed)
        logger.info(f"Padded RS data with {padding_needed} zero bits. New len: {len(data_bits)}")

    bit_idx = 0
    pixels_colored = 0

    bch_coords_set = set()
    coords_path1 = []
    for x_mat_1idx in range(MODULES + 4, (MODULES - 3) - 1, -1):
        coords_path1.append((13 - 1, x_mat_1idx - 1))
    coords_path2 = []
    for y_mat_1idx in range(12, 5 - 1, -1):
        coords_path2.append((y_mat_1idx - 1, 13 - 1))
    coords_path3 = []
    for x_mat_1idx in range(12, 5 - 1, -1):
        coords_path3.append((13 - 1, x_mat_1idx - 1))
    coords_path4 = []
    for x_mat_1idx in range(12, 5 - 1, -1):
        coords_path4.append(((MODULES - 4) - 1, x_mat_1idx - 1))
    for p in coords_path1 + coords_path2 + coords_path3 + coords_path4:
        bch_coords_set.add(p)

    def encode_pixel_at(r_img_0idx, c_img_0idx):
        nonlocal bit_idx, pixels_colored

        if not is_valid_for_data(r_img_0idx, c_img_0idx, image_width, image_height):
            return True

        if (r_img_0idx, c_img_0idx) in bch_coords_set:
            return True

        if bit_idx <= len(data_bits) - 3:
            pixel_bits_tuple = tuple(data_bits[bit_idx: bit_idx + 3])
            color = get_color_for_bits(pixel_bits_tuple)
            image[r_img_0idx, c_img_0idx] = color
            bit_idx += 3
            pixels_colored += 1
            return True
        return False

    if bit_idx <= len(data_bits) - 3:
        for x_mat_1idx in range(MODULES + 4, (MODULES - 3) - 1, -1):
            c_img_0idx = x_mat_1idx - 1
            for y_mat_1idx in range(MODULES - 5, 14 - 1, -1):
                r_img_0idx = y_mat_1idx - 1
                if not encode_pixel_at(r_img_0idx, c_img_0idx): break
            if not (bit_idx <= len(data_bits) - 3): break

    if bit_idx <= len(data_bits) - 3:
        c_img_0idx = (MODULES - 4) - 1
        for y_mat_1idx in range(MODULES - 5, 5 - 1, -1):
            r_img_0idx = y_mat_1idx - 1
            if not encode_pixel_at(r_img_0idx, c_img_0idx): break

    if bit_idx <= len(data_bits) - 3:
        for x_mat_1idx in range(MODULES - 5, 14 - 1, -1):
            c_img_0idx = x_mat_1idx - 1
            for y_mat_1idx in range(MODULES + 4, 5 - 1, -1):
                r_img_0idx = y_mat_1idx - 1
                if not encode_pixel_at(r_img_0idx, c_img_0idx): break
            if not (bit_idx <= len(data_bits) - 3): break

    if bit_idx <= len(data_bits) - 3:
        c_img_0idx = 13 - 1
        for y_mat_1idx in range(MODULES + 4, 13 - 1, -1):
            r_img_0idx = y_mat_1idx - 1
            if not encode_pixel_at(r_img_0idx, c_img_0idx): break

    if bit_idx <= len(data_bits) - 3:
        for x_mat_1idx in range(12, 5 - 1, -1):
            c_img_0idx = x_mat_1idx - 1
            for y_mat_1idx in range(MODULES - 5, 14 - 1, -1):
                r_img_0idx = y_mat_1idx - 1
                if not encode_pixel_at(r_img_0idx, c_img_0idx): break
            if not (bit_idx <= len(data_bits) - 3): break

    if bit_idx < len(data_bits):
        logger.warning(f"RS data: {len(data_bits) - bit_idx} bits remaining after trying to place. Placed {pixels_colored} pixels.")
    else:
        logger.info(f"RS data: All bits placed. Placed {pixels_colored} pixels.")

    total_image_pixels = image_width * image_height
    finder_pattern_pixels = 4 * (7 * 7)
    bch_pixels = len(bch_coords_set)

    potential_rs_pixels = 0
    for r_idx in range(image_height):
        for c_idx in range(image_width):
            if is_valid_for_data(r_idx, c_idx, image_width, image_height) and (r_idx, c_idx) not in bch_coords_set:
                potential_rs_pixels += 1

    available_rs_bits = potential_rs_pixels * 3
    actual_rs_bits_placed = bit_idx

    logger.info(f"c_COLOR Encoding Stats:")
    logger.info(f"  - Total pixels in image grid: {total_image_pixels} ({image_width}x{image_height})")
    logger.info(f"  - Pixels for Finder Patterns: {finder_pattern_pixels}")
    logger.info(f"  - Pixels for BCH data: {bch_pixels}")
    logger.info(f"  - Calculated potential pixels for RS data: {potential_rs_pixels}")
    logger.info(f"  - Total available bit capacity for RS data: {available_rs_bits} bits")
    logger.info(f"  - Actual RS data bits written: {actual_rs_bits_placed} bits")
    if available_rs_bits > 0:
        usage_percentage = (actual_rs_bits_placed / available_rs_bits) * 100
        logger.info(f"  - RS data capacity usage: {usage_percentage:.2f}%")
    else:
        logger.info(f"  - RS data capacity usage: N/A (no available bits for RS data)")


def process_chunk(chunk_file, output_dir, scale_factor=10):
    with open(chunk_file, 'rb') as f:
        chunk_data = f.read()

    chunk_basename = os.path.basename(chunk_file)
    output_file = os.path.join(output_dir, f"{os.path.splitext(chunk_basename)[0]}.png")

    return encode_chunk_to_c_COLOR(chunk_data, output_file, scale_factor)


def main():
    parser = argparse.ArgumentParser(description='Encode file chunks to c_COLOR images.')
    parser.add_argument('--input', '-i', required=True, help='Input chunk file or directory')
    parser.add_argument('--output', '-o', required=True, help='Output directory for c_COLOR images')
    parser.add_argument('--scale', '-s', type=int, default=10, help='Scale factor for output images (default: 10)')
    args = parser.parse_args()

    if not os.path.exists(args.output):
        os.makedirs(args.output)

    if os.path.isfile(args.input):
        try:
            output_path = process_chunk(args.input, args.output, args.scale)
            logger.info(f"Successfully encoded chunk to {output_path}")
        except Exception as e:
            logger.error(f"Error encoding chunk {args.input}: {str(e)}", exc_info=True)
            return 1
    elif os.path.isdir(args.input):
        success_count = 0
        fail_count = 0

        for filename in os.listdir(args.input):
            if filename.endswith('.bin'):
                chunk_path = os.path.join(args.input, filename)
                try:
                    output_path = process_chunk(chunk_path, args.output, args.scale)
                    logger.info(f"Successfully encoded chunk to {output_path}")
                    success_count += 1
                except Exception as e:
                    logger.error(f"Error encoding chunk {chunk_path}: {str(e)}", exc_info=True)
                    fail_count += 1

        logger.info(f"Encoding complete: {success_count} chunks encoded, {fail_count} failed")
        if fail_count > 0:
            return 1
    else:
        logger.error(f"Input path {args.input} is not a file or directory")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())