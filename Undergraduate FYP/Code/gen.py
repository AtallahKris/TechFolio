import os
import random
import string

INPUT_DIR = '/mnt/HDD/Documents/University/Balamand/ELCP392 - Senior Design II/Code/input'

def random_name(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def random_file_size(min_size=102, max_size=1024):
    return random.randint(min_size, max_size)

def create_random_file(folder):
    file_name = random_name() + '.bin'
    file_path = os.path.join(folder, file_name)
    size = random_file_size()
    with open(file_path, 'wb') as f:
        f.write(os.urandom(size))
    print(f"Created file: {file_path} ({size} bytes)")

def pick_or_create_folder(base_dir):
    folders = []
    for root, dirs, _ in os.walk(base_dir):
        for d in dirs:
            folders.append(os.path.join(root, d))
    if folders and random.choice([True, False]):
        parent = random.choice(folders)
    else:
        parent = base_dir
    new_folder = random_name()
    full_path = os.path.join(parent, new_folder)
    os.makedirs(full_path, exist_ok=True)
    return full_path

if __name__ == '__main__':
    folder = pick_or_create_folder(INPUT_DIR)
    create_random_file(folder)