import cv2
import os
import time
import natsort

IMAGE_DIR = 'c_COLOR_images/' 
DISPLAY_DURATION = 3
SUPPORTED_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff')

def display_images():
    absolute_image_dir = os.path.abspath(IMAGE_DIR)

    if not os.path.isdir(absolute_image_dir):
        print(f"Error: Image directory '{absolute_image_dir}' not found or is not a directory.")
        return

    image_files = [f for f in os.listdir(absolute_image_dir) if f.lower().endswith(SUPPORTED_EXTENSIONS)]
    
    if not image_files:
        print(f"No images with supported extensions found in '{absolute_image_dir}'.")
        return

    sorted_image_files = natsort.natsorted(image_files)

    cv2.namedWindow("c_COLOR Transmission", cv2.WINDOW_NORMAL)

    for image_file in sorted_image_files:
        image_path = os.path.join(absolute_image_dir, image_file)
        try:
            img = cv2.imread(image_path)
            if img is None:
                continue

            cv2.imshow("c_COLOR Transmission", img)
            
            key = cv2.waitKey(DISPLAY_DURATION * 1000) 
            
            if key == ord('q'):
                break
        except Exception as e:
            break
            
    cv2.destroyAllWindows()

if __name__ == "__main__":
    time.sleep(2)
    display_images()
