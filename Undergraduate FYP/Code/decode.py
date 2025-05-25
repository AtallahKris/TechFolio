#!/usr/bin/env python3
import os
import numpy as np
import cv2
import struct
from reedsolo import RSCodec, ReedSolomonError
import argparse
import logging
import math
from collections import Counter

VERSION = 8
COLOR = 8
ERROR = 10
MODULES = 100
N_SYMBOLS = 3635
K_SYMBOLS = 2895
QZ = 4
FP_SIZE = 7
RS_OFFSET = 0

num_blocks_decode = 15
k_per_block_decode = 193
n_per_block_decode = 241

K_SYMBOLS_EFFECTIVE_DECODE = num_blocks_decode * k_per_block_decode
N_SYMBOLS_EFFECTIVE_DECODE = num_blocks_decode * n_per_block_decode

RS_BLOCK_CONFIGS = [{'n': n_per_block_decode, 'k': k_per_block_decode, 'data_len': k_per_block_decode}] * num_blocks_decode

if sum(b['k'] for b in RS_BLOCK_CONFIGS) != K_SYMBOLS_EFFECTIVE_DECODE:
    raise ValueError(f"Custom RS_BLOCK_CONFIGS k sum {sum(b['k'] for b in RS_BLOCK_CONFIGS)} != K_SYMBOLS_EFFECTIVE_DECODE {K_SYMBOLS_EFFECTIVE_DECODE}")
if sum(b['n'] for b in RS_BLOCK_CONFIGS) != N_SYMBOLS_EFFECTIVE_DECODE:
    raise ValueError(f"Custom RS_BLOCK_CONFIGS n sum {sum(b['n'] for b in RS_BLOCK_CONFIGS)} != N_SYMBOLS_EFFECTIVE_DECODE {N_SYMBOLS_EFFECTIVE_DECODE}")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UnsupportedFormatError(Exception):
    pass

def decode_c_COLOR_payload_from_image(image_path: str) -> bytes | None:
    if not os.path.exists(image_path):
        logger.error(f"Image file not found: {image_path}")
        raise FileNotFoundError(f"Image file not found: {image_path}")

    try:
        image = cv2.imread(image_path)
        if image is None:
            logger.error(f"Could not read image: {image_path}")
            raise ValueError(f"Could not read image: {image_path}")

        aligned_image = locate_and_align_patterns(image)
        if aligned_image is None:
            logger.error(f"Failed to align image: {image_path}")
            return None

        _, version, color, error, num_bytes_from_bch = extract_bch_metadata(aligned_image)

        if version != VERSION or color != COLOR or error != ERROR:
            logger.error(
                f"Unsupported c_COLOR format for {image_path}. "
                f"Expected V{VERSION}C{COLOR}E{ERROR}%, Got V{version}C{color}E{error}%"
            )
            raise UnsupportedFormatError(
                f"Unsupported c_COLOR format. Expected V{VERSION}C{COLOR}E{ERROR}%, Got V{version}C{color}E{error}%"
            )

        rs_data_from_image = extract_rs_data(aligned_image)
        if rs_data_from_image is None:
            logger.error(f"Failed to extract RS data from image: {image_path}")
            return None

        if len(rs_data_from_image) != N_SYMBOLS_EFFECTIVE_DECODE:
            logger.warning(f"Extracted RS data length {len(rs_data_from_image)} bytes, but reed_solomon_decode expects {N_SYMBOLS_EFFECTIVE_DECODE} (N_eff). This might be handled internally by reed_solomon_decode or indicate an issue.")

        chunk_payload = reed_solomon_decode(rs_data_from_image, num_bytes_from_bch)

        logger.info(f"Successfully decoded payload from {image_path}, size: {len(chunk_payload)} bytes (BCH indicated {num_bytes_from_bch}).")
        return chunk_payload

    except FileNotFoundError:
        raise
    except UnsupportedFormatError:
        raise
    except ReedSolomonError as rse:
        logger.error(f"Reed-Solomon decoding failed for {image_path}: {rse}")
        raise
    except ValueError as ve:
        logger.error(f"ValueError during decoding of {image_path}: {ve}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred while decoding {image_path}: {e}", exc_info=True)
        raise

def decode_c_COLOR_to_chunk(image_path, output_path):
    try:
        chunk_payload_bytes = decode_c_COLOR_payload_from_image(image_path)

        if chunk_payload_bytes is None:
            logger.error(f"Failed to get payload from {image_path}, cannot write to chunk.")
            raise ValueError(f"Decoding payload from {image_path} returned None.")

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(chunk_payload_bytes)

        logger.info(f"Successfully decoded {image_path} and wrote payload to {output_path}")
        return output_path

    except FileNotFoundError:
        logger.error(f"decode_c_COLOR_to_chunk: Image file not found: {image_path}")
        raise
    except UnsupportedFormatError as e:
        logger.error(f"decode_c_COLOR_to_chunk: Unsupported format for {image_path}: {e}")
        raise
    except ReedSolomonError as rse:
        logger.error(f"decode_c_COLOR_to_chunk: Reed-Solomon error for {image_path}: {rse}. Chunk not written.")
        raise
    except ValueError as ve:
        logger.error(f"decode_c_COLOR_to_chunk: ValueError for {image_path}: {ve}. Chunk not written.")
        raise
    except Exception as e:
        logger.error(f"decode_c_COLOR_to_chunk: Unexpected error for {image_path}: {e}. Chunk not written.", exc_info=True)
        raise

def locate_and_align_patterns(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    hierarchical_fps = []
    if hierarchy is not None and hierarchy.ndim == 3 and hierarchy.shape[0] == 1:
        for i, contour in enumerate(contours):
            c0_idx = i

            if hierarchy[0, c0_idx, 2] == -1: continue
            c1_idx = hierarchy[0, c0_idx, 2]
            if hierarchy[0, c1_idx, 3] != c0_idx: continue

            if hierarchy[0, c1_idx, 2] == -1: continue
            c2_idx = hierarchy[0, c1_idx, 2]
            if hierarchy[0, c2_idx, 3] != c1_idx: continue

            if hierarchy[0, c2_idx, 2] != -1: continue

            c0 = contours[c0_idx]
            c1 = contours[c1_idx]
            c2 = contours[c2_idx]

            valid_shape_count = 0
            for cnt_test in [c0, c1, c2]:
                peri = cv2.arcLength(cnt_test, True)
                approx_test = cv2.approxPolyDP(cnt_test, 0.04 * peri, True)
                if len(approx_test) == 4 and cv2.isContourConvex(approx_test):
                    _, _, w_test, h_test = cv2.boundingRect(approx_test)
                    if 0.7 < float(w_test)/(h_test + 1e-6) < 1.3:
                        valid_shape_count +=1
            if valid_shape_count != 3:
                continue

            m0 = cv2.moments(c0); m1 = cv2.moments(c1); m2 = cv2.moments(c2)
            if m0['m00'] == 0 or m1['m00'] == 0 or m2['m00'] == 0: continue

            c0_center = (m0['m10']/m0['m00'], m0['m01']/m0['m00'])
            c1_center = (m1['m10']/m1['m00'], m1['m01']/m1['m00'])
            c2_center = (m2['m10']/m2['m00'], m2['m01']/m2['m00'])

            dist_c0c1 = np.sqrt((c0_center[0]-c1_center[0])**2 + (c0_center[1]-c1_center[1])**2)
            dist_c1c2 = np.sqrt((c1_center[0]-c2_center[0])**2 + (c1_center[1]-c2_center[1])**2)

            if dist_c0c1 > 15 or dist_c1c2 > 15:
                continue

            area_c0 = cv2.contourArea(c0)
            area_c1 = cv2.contourArea(c1)
            area_c2 = cv2.contourArea(c2)

            if area_c2 < (15*15): continue
            if area_c1 < area_c2 or area_c0 < area_c1 : continue

            ratio1 = area_c2 / (area_c1 + 1e-6)
            ratio2 = area_c1 / (area_c0 + 1e-6)

            if not (0.2 < ratio1 < 0.7 and 0.3 < ratio2 < 0.8):
                continue

            hierarchical_fps.append({'contour': c0, 'center_x': c0_center[0], 'center_y': c0_center[1], 'area': area_c0})

    finder_patterns_final_contours = []
    if len(hierarchical_fps) >= 4:
        logger.info(f"Hierarchical detection found {len(hierarchical_fps)} candidates. Selecting 4.")

        hierarchical_fps.sort(key=lambda p: p['area'], reverse=True)
        selected_fps_meta = hierarchical_fps[:4]
        finder_patterns_final_contours = [fp['contour'] for fp in selected_fps_meta]
    else:
        logger.warning(f"Hierarchical FP detection found only {len(hierarchical_fps)} candidates. Falling back to simple quad detection.")

        simple_fps_candidates = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 200:
                perimeter = cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, 0.04 * perimeter, True)
                if len(approx) == 4 and cv2.isContourConvex(approx):
                    x, y, w, h = cv2.boundingRect(approx)
                    if 0.7 < float(w)/(h+1e-6) < 1.3:
                        M = cv2.moments(contour)
                        if M['m00'] == 0: continue
                        center_x, center_y = (M['m10']/M['m00'], M['m01']/M['m00'])
                        simple_fps_candidates.append({'contour': contour, 'center_x': center_x, 'center_y': center_y, 'area': area})

        logger.info(f"Simple quad detection found {len(simple_fps_candidates)} candidates.")
        if len(simple_fps_candidates) >= 4:
            simple_fps_candidates.sort(key=lambda p: p['area'], reverse=True)
            selected_fps_meta = simple_fps_candidates[:4]
            finder_patterns_final_contours = [fp['contour'] for fp in selected_fps_meta]
        else:
            logger.warning(f"Simple quad detection found {len(simple_fps_candidates)} candidates. Attempting KMeans corner fallback if contours exist.")
            if contours:
                pass

    if len(finder_patterns_final_contours) != 4:
        logger.warning(f"Primary and simple FP detection failed to yield 4 FPs (found {len(finder_patterns_final_contours)}). Trying Harris corner + KMeans fallback.")

        gray_harris = np.float32(gray)
        dst = cv2.cornerHarris(gray_harris, blockSize=2, ksize=3, k=0.04)
        dst = cv2.dilate(dst,None)
        ret, dst = cv2.threshold(dst,0.01*dst.max(),255,0)
        dst = np.uint8(dst)

        ret, labels, stats, centroids = cv2.connectedComponentsWithStats(dst)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)

        if len(centroids) >= 4 :
            try:
                compactness, labels_kmeans, centers_kmeans = cv2.kmeans(np.float32(centroids[1:]), 4, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

                logger.info(f"KMeans found {len(centers_kmeans)} centers. This path is not fully robust for contour extraction.")
                raise ValueError(f"KMeans fallback invoked but not fully implemented to return contours. Found {len(finder_patterns_final_contours)} FPs before KMeans.")

            except cv2.error as e:
                 raise ValueError(f"KMeans clustering failed: {e}. Could not locate 4 finder patterns.")
        else:
            raise ValueError(f"Not enough Harris corners ({len(centroids)}) for KMeans. Could not locate 4 finder patterns.")

    if len(finder_patterns_final_contours) != 4:
        raise ValueError(f"Could not robustly locate 4 finder patterns in the image. Found {len(finder_patterns_final_contours)}.")

    contour_centroids = []
    for contour in finder_patterns_final_contours:
        M = cv2.moments(contour)
        if M['m00'] == 0: raise ValueError("FP contour has zero area during centroid calculation.")
        contour_centroids.append((M['m10']/M['m00'], M['m01']/M['m00']))

    contour_centroids_with_contours = list(zip(contour_centroids, finder_patterns_final_contours))
    contour_centroids_with_contours.sort(key=lambda item: item[0][1])

    top_row = sorted(contour_centroids_with_contours[:2], key=lambda item: item[0][0])
    bottom_row = sorted(contour_centroids_with_contours[2:], key=lambda item: item[0][0])

    tl_contour = top_row[0][1]
    tr_contour = top_row[1][1]
    bl_contour = bottom_row[0][1]
    br_contour = bottom_row[1][1]

    rect_tl = cv2.boundingRect(tl_contour)
    rect_tr = cv2.boundingRect(tr_contour)
    rect_bl = cv2.boundingRect(bl_contour)
    rect_br = cv2.boundingRect(br_contour)

    src_pts = np.array([
        [rect_tl[0], rect_tl[1]],
        [rect_tr[0] + rect_tr[2] - 1, rect_tr[1]],
        [rect_bl[0], rect_bl[1] + rect_bl[3] - 1],
        [rect_br[0] + rect_br[2] - 1, rect_br[1] + rect_br[3] - 1]
    ], dtype=np.float32)

    size_of_output_image = MODULES + 2 * QZ

    dst_pts = np.array([
        [QZ, QZ],
        [QZ + MODULES - 1, QZ],
        [QZ, QZ + MODULES - 1],
        [QZ + MODULES - 1, QZ + MODULES - 1]
    ], dtype=np.float32)

    M = cv2.getPerspectiveTransform(src_pts, dst_pts)
    aligned_image = cv2.warpPerspective(image, M, (size_of_output_image, size_of_output_image), flags=cv2.INTER_NEAREST)

    logger.info(f"locate_and_align_patterns: src_pts used for warp: {src_pts.tolist()}")
    logger.info(f"locate_and_align_patterns: dst_pts used for warp: {dst_pts.tolist()}")

    return aligned_image

def extract_bch_metadata(image):
    bch_bits = []
    bch_row = QZ - 1
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
        logger.error(f"BCH extraction path has {len(full_bch_path)} pixels, expected 32. BCH will be incorrect.")

        return ([1]*64), VERSION, COLOR, -1, 0

    image_height, image_width = image.shape[:2]

    valid_bch_colors_map = {
        (0, 0, 255): [0, 0],
        (0, 255, 0): [0, 1],
        (255, 0, 0): [1, 0],
        (255, 255, 255): [1, 1]
    }
    valid_bch_color_tuples = list(valid_bch_colors_map.keys())

    for i, coord in enumerate(full_bch_path):
        r, c = coord['r'], coord['c']

        if not (0 <= r < image_height and 0 <= c < image_width):
            logger.error(f"BCH({i}) coord ({r},{c}) is OOB ({image_height}x{image_width}). Appending [0,0].")
            bch_bits.extend([0,0])
            continue

        pixel_color_bgr_numpy = image[r, c]
        pixel_color_bgr = tuple(pixel_color_bgr_numpy)

        extracted_pair = valid_bch_colors_map.get(pixel_color_bgr)
        source_of_bits = "exact_match"

        if extracted_pair is None:
            min_dist = float('inf')
            closest_color_bits = [0,0]
            distances_log = []

            px_b, px_g, px_r = int(pixel_color_bgr_numpy[0]), int(pixel_color_bgr_numpy[1]), int(pixel_color_bgr_numpy[2])

            for bch_color_tuple, bits_pair in valid_bch_colors_map.items():
                bch_b, bch_g, bch_r = bch_color_tuple
                dist = (px_b - bch_b)**2 + (px_g - bch_g)**2 + (px_r - bch_r)**2
                distances_log.append(f"to_{bch_color_tuple}_({bits_pair})={dist}")
                if dist < min_dist:
                    min_dist = dist
                    closest_color_bits = bits_pair

            logger.warning(f"BCH({i}) @({r},{c}): Read {list(pixel_color_bgr_numpy)}. No exact match. Distances: [{', '.join(distances_log)}]. Closest: {closest_color_bits} (dist={min_dist}).")
            extracted_pair = closest_color_bits
            source_of_bits = "closest_match"

            logger.info(f"BCH({i}) @({r},{c}): Read {list(pixel_color_bgr_numpy)}. Matched {extracted_pair} by {source_of_bits}.")

        bch_bits.extend(extracted_pair)

    if len(bch_bits) != 64:
        logger.error(f"Extracted {len(bch_bits)} BCH bits, expected 64. Padding with zeros.")
        bch_bits.extend([0] * (64 - len(bch_bits)))

    num_bytes_bits = bch_bits[0:12]
    version_code_bits = bch_bits[12:15]
    color_code_bits = bch_bits[15:18]
    error_code_bits = bch_bits[18:20]

    num_bytes = int("".join(map(str, num_bytes_bits)), 2)

    version_code = int("".join(map(str, version_code_bits)), 2)
    version = version_code + 1

    color_code = int("".join(map(str, color_code_bits)), 2)
    color = color_code + 1

    error_map_decode = {0: 10, 1: 20, 2: 30}
    error_code_val = int("".join(map(str, error_code_bits)), 2)
    error = error_map_decode.get(error_code_val, -1)

    logger.info(f"Extracted BCH: Version={version} (code={version_code}), Color={color} (code={color_code}), Error={error}% (code={error_code_val}), NumBytes={num_bytes}")
    logger.info(f"Raw BCH bits (first 20 for metadata): {bch_bits[:20]}")

    return bch_bits, version, color, error, num_bytes

def get_rs_pixel_path_coords():
    path_coords_final = []

    for c_idx in range((MODULES + 4) - 1, ((MODULES - 3) - 1) - 1, -1):
        for r_idx in range((MODULES - 5) - 1, (14 - 1) - 1, -1):
            path_coords_final.append((r_idx, c_idx))

    c_idx_p2 = (MODULES - 4) - 1
    for r_idx in range((MODULES - 5) - 1, (5 - 1) - 1, -1):
        path_coords_final.append((r_idx, c_idx_p2))

    for c_idx in range((MODULES - 5) - 1, (14 - 1) - 1, -1):
        for r_idx in range((MODULES + 4) - 1, (5 - 1) - 1, -1):
            path_coords_final.append((r_idx, c_idx))

    c_idx_p4 = (13 - 1)
    for r_idx in range((MODULES + 4) - 1, (13 - 1) - 1, -1):
        path_coords_final.append((r_idx, c_idx_p4))

    for c_idx in range((12 - 1), (5 - 1) - 1, -1):
        for r_idx in range((MODULES - 5) - 1, (14 - 1) - 1, -1):
            path_coords_final.append((r_idx, c_idx))

    return path_coords_final

def extract_rs_data(image):
    data_bits = []

    fp_regions = []
    fp_regions.append({'r_start': QZ, 'r_end': QZ + FP_SIZE, 'c_start': QZ, 'c_end': QZ + FP_SIZE})
    fp_regions.append({'r_start': QZ, 'r_end': QZ + FP_SIZE, 'c_start': QZ + MODULES - FP_SIZE, 'c_end': QZ + MODULES})
    fp_regions.append({'r_start': QZ + MODULES - FP_SIZE, 'r_end': QZ + MODULES, 'c_start': QZ, 'c_end': QZ + FP_SIZE})
    fp_regions.append({'r_start': QZ + MODULES - FP_SIZE, 'r_end': QZ + MODULES, 'c_start': QZ + MODULES - FP_SIZE, 'c_end': QZ + MODULES})

    def is_in_fp(r, c):
        for region in fp_regions:
            if region['r_start'] <= r < region['r_end'] and \
               region['c_start'] <= c < region['c_end']:
                return True
        return False

    bch_coords_set = set()
    coords_path1_bch = []
    for x_mat_1idx in range(MODULES + 4, (MODULES - 3) - 1, -1):
        coords_path1_bch.append((13 - 1, x_mat_1idx - 1))
    coords_path2_bch = []
    for y_mat_1idx in range(12, 5 - 1, -1):
        coords_path2_bch.append((y_mat_1idx - 1, 13 - 1))
    coords_path3_bch = []
    for x_mat_1idx in range(12, 5 - 1, -1):
        coords_path3_bch.append((13 - 1, x_mat_1idx - 1))
    coords_path4_bch = []
    row_path4_0idx = (MODULES - 4) - 1
    for x_mat_1idx in range(12, 5 - 1, -1):
        coords_path4_bch.append((row_path4_0idx, x_mat_1idx - 1))
    for p in coords_path1_bch + coords_path2_bch + coords_path3_bch + coords_path4_bch:
        bch_coords_set.add(p)

    rs_pixel_path = get_rs_pixel_path_coords()

    pixels_read = 0
    expected_total_bits = N_SYMBOLS * 8
    padding_bits_added_in_encode = (3 - (expected_total_bits % 3)) % 3
    total_bits_to_extract = expected_total_bits + padding_bits_added_in_encode

    for r_abs, c_abs in rs_pixel_path:
        if len(data_bits) >= total_bits_to_extract:
            break

        if not (0 <= r_abs < image.shape[0] and 0 <= c_abs < image.shape[1]):
            logger.warning(f"RS path coord ({r_abs},{c_abs}) is OOB. Skipping.")
            continue

        if is_in_fp(r_abs, c_abs):
            continue

        if (r_abs, c_abs) in bch_coords_set:
            continue

        pixel_color = image[r_abs, c_abs]
        bits = get_bits_from_color(pixel_color)
        if bits:
            data_bits.extend(bits)
            pixels_read += 1
        else:
            logger.warning(f"Could not map color {pixel_color} at RS data location ({r_abs},{c_abs}) to bits. Appending [0,0,0].")
            data_bits.extend([0,0,0])

    if len(data_bits) < total_bits_to_extract:
        logger.warning(f"Extracted {len(data_bits)} RS data bits (path yielded {pixels_read} pixels), but expected {total_bits_to_extract} (after padding). Data might be truncated or path is shorter than expected.")

    actual_rs_data_bits = data_bits[:expected_total_bits]

    if len(actual_rs_data_bits) != expected_total_bits:
         logger.error(f"After removing padding, extracted {len(actual_rs_data_bits)} RS data bits, expected {expected_total_bits} (for N_SYMBOLS={N_SYMBOLS}). This will likely cause decoding failure.")

    logger.info(f"extract_rs_data: Read {pixels_read} pixels. Extracted {len(data_bits)} raw bits. After removing padding: {len(actual_rs_data_bits)} bits for RS decoding (target N_SYMBOLS={N_SYMBOLS}).")

    rs_data_bytes_from_pixels = bits_to_bytes(actual_rs_data_bits)

    if len(rs_data_bytes_from_pixels) < N_SYMBOLS_EFFECTIVE_DECODE:
        logger.error(f"Extracted data ({len(rs_data_bytes_from_pixels)}) is less than N_SYMBOLS_EFFECTIVE_DECODE ({N_SYMBOLS_EFFECTIVE_DECODE}). Padding with zeros.")
        rs_data_for_decode = rs_data_bytes_from_pixels + bytes(N_SYMBOLS_EFFECTIVE_DECODE - len(rs_data_bytes_from_pixels))
    elif len(rs_data_bytes_from_pixels) > N_SYMBOLS_EFFECTIVE_DECODE:
        logger.info(f"Extracted data ({len(rs_data_bytes_from_pixels)}) is greater than N_SYMBOLS_EFFECTIVE_DECODE ({N_SYMBOLS_EFFECTIVE_DECODE}). Truncating for RS block processing.")
        rs_data_for_decode = rs_data_bytes_from_pixels[:N_SYMBOLS_EFFECTIVE_DECODE]
    else:
        rs_data_for_decode = rs_data_bytes_from_pixels

    return rs_data_for_decode

def get_bits_from_color(color):
    b, g, r = color
    b, g, r = int(b), int(g), int(r)

    color_map_rs = {
        (0, 0, 255): [0, 0, 0],
        (0, 255, 0): [0, 0, 1],
        (255, 0, 0): [0, 1, 0],
        (0, 255, 255): [0, 1, 1],
        (255, 0, 255): [1, 0, 0],
        (255, 255, 0): [1, 0, 1],
        (255, 255, 255): [1, 1, 0],
        (0, 0, 0): [1, 1, 1]
    }

    best_match = None
    min_distance = float('inf')

    for key_color, bits in color_map_rs.items():
        kb, kg, kr = int(key_color[0]), int(key_color[1]), int(key_color[2])
        distance = (b - kb)**2 + (g - kg)**2 + (r - kr)**2

        if distance < min_distance:
            min_distance = distance
            best_match = bits

    if min_distance > 8000:
        logger.warning(f"Poor color match for color {color}. Closest mapped color is {min_distance} away. This might indicate an issue.")

    return best_match

def bits_to_bytes(bits):
    padding = 8 - (len(bits) % 8) if len(bits) % 8 != 0 else 0
    if padding:
        bits = bits + [0] * padding

    byte_values = []
    for i in range(0, len(bits), 8):
        byte = 0
        for j in range(8):
            if i + j < len(bits):
                byte = (byte << 1) | bits[i + j]
        byte_values.append(byte)

    return bytes(byte_values)

def reed_solomon_decode(rs_data, original_size_from_bch):
    if len(rs_data) != N_SYMBOLS_EFFECTIVE_DECODE:
        logger.error(f"reed_solomon_decode: Expected {N_SYMBOLS_EFFECTIVE_DECODE} bytes of RS data (N_eff), got {len(rs_data)}. Adjusting.")
        if len(rs_data) < N_SYMBOLS_EFFECTIVE_DECODE:
            rs_data += bytes(N_SYMBOLS_EFFECTIVE_DECODE - len(rs_data))
        else:
            rs_data = rs_data[:N_SYMBOLS_EFFECTIVE_DECODE]

    decoded_payload_bytes = bytearray()
    current_rs_data_offset = 0

    for config in RS_BLOCK_CONFIGS:
        n = config['n']
        k = config['k']

        block_rs_data = rs_data[current_rs_data_offset : current_rs_data_offset + n]
        current_rs_data_offset += n

        if len(block_rs_data) != n:
            logger.error(f"Not enough data for RS block (n={n}). Expected {n}, got {len(block_rs_data)}. Skipping block.")
            continue

        rs_decoder = RSCodec(n - k, nsize=n)

        try:
            decoded_message_part, _, err_stat = rs_decoder.decode(bytes(block_rs_data))
            decoded_payload_bytes.extend(decoded_message_part)

        except ReedSolomonError as e:
            logger.error(f"Reed-Solomon decoding error for a block (n={n}, k={k}): {str(e)}. This chunk is corrupted.")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during Reed-Solomon decoding for a block (n={n}, k={k}): {str(e)}. Appending {k} zero bytes as a fallback (but this is not ideal).")
            decoded_payload_bytes.extend(bytes(k))

    if len(decoded_payload_bytes) != K_SYMBOLS_EFFECTIVE_DECODE:
        logger.warning(f"Multi-block RS decoding resulted in {len(decoded_payload_bytes)} total payload bytes, expected {K_SYMBOLS_EFFECTIVE_DECODE} (K_eff). Payload will be used as is.")

    max_payload_after_decode = K_SYMBOLS_EFFECTIVE_DECODE

    if original_size_from_bch > max_payload_after_decode:
        logger.warning(f"BCH original size ({original_size_from_bch}) is greater than K_eff_decode ({max_payload_after_decode}). Using {max_payload_after_decode}.")
        final_data = decoded_payload_bytes[:max_payload_after_decode]
    elif original_size_from_bch < 0:
        logger.error(f"BCH original size is negative ({original_size_from_bch}). Using full K_eff_decode payload ({max_payload_after_decode}).")
        final_data = decoded_payload_bytes[:max_payload_after_decode]
    else:
        size_to_take = min(original_size_from_bch, max_payload_after_decode)
        final_data = decoded_payload_bytes[:size_to_take]

        if len(final_data) != original_size_from_bch and original_size_from_bch <= max_payload_after_decode :
             logger.warning(f"Final data length {len(final_data)} does not match BCH original size {original_size_from_bch} (original_size was <= K_eff {max_payload_after_decode}).")
        elif original_size_from_bch > max_payload_after_decode:
             logger.warning(f"Final data truncated to {len(final_data)} because BCH original size {original_size_from_bch} exceeded K_eff {max_payload_after_decode}.")

    logger.info(f"RS decoding complete. Original size from BCH: {original_size_from_bch}. Decoded payload length (K_eff): {len(decoded_payload_bytes)}. Final data length: {len(final_data)}.")
    return bytes(final_data)

def process_image(image_path, output_dir):
    image_basename = os.path.basename(image_path)
    output_file = os.path.join(output_dir, f"{os.path.splitext(image_basename)[0]}.bin")

    try:
        return decode_c_COLOR_to_chunk(image_path, output_file)
    except UnsupportedFormatError as e:
        logger.error(str(e))
        raise
    except Exception as e:
        logger.error(f"Error decoding image {image_path}: {str(e)}")
        raise

def main():
    parser = argparse.ArgumentParser(description='Decode c_COLOR images to file chunks.')
    parser.add_argument('--input', '-i', required=True, help='Input c_COLOR image or directory')
    parser.add_argument('--output', '-o', required=True, help='Output directory for decoded chunks')
    parser.add_argument('--force', '-f', action='store_true', help='Force decoding even with errors')
    args = parser.parse_args()

    if os.path.isfile(args.input):
        try:
            output_path = process_image(args.input, args.output)
            logger.info(f"Successfully decoded image to {output_path}")
        except UnsupportedFormatError as e:
            logger.error(str(e))
            return 1
        except Exception as e:
            logger.error(f"Error decoding image {args.input}: {str(e)}")
            return 1
    elif os.path.isdir(args.input):
        success_count = 0
        fail_count = 0

        for filename in os.listdir(args.input):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                image_path = os.path.join(args.input, filename)
                try:
                    output_path = process_image(image_path, args.output)
                    logger.info(f"Successfully decoded image to {output_path}")
                    success_count += 1
                except UnsupportedFormatError as e:
                    logger.error(f"{filename}: {str(e)}")
                    fail_count += 1
                except Exception as e:
                    logger.error(f"Error decoding image {image_path}: {str(e)}")
                    fail_count += 1

        logger.info(f"Decoding complete: {success_count} images decoded, {fail_count} failed")
        if fail_count > 0 and not args.force:
            return 1
    else:
        logger.error(f"Input path {args.input} is not a file or directory")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())