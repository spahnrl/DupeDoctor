# find_duplicates_hash.py

import os
import hashlib
from datetime import datetime

# === CONFIG ===
TARGET_FOLDER = r"C:\Users\Rick_DellXPS\OneDrive\Pictures"
HASH_CHUNK_SIZE = 8192
LOG_FILE = r"C:\Users\Rick_DellXPS\Python\PythonProject\prj_dup_file_check\photo_duplicates_log.txt"

# File extensions to include
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.heic', '.raw'}

def get_file_hash(path, chunk_size=HASH_CHUNK_SIZE):
    hasher = hashlib.sha256()
    try:
        with open(path, 'rb') as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
    except (PermissionError, OSError):
        return None
    return hasher.hexdigest()

def is_image_file(file_path):
    return os.path.splitext(file_path)[1].lower() in IMAGE_EXTENSIONS

def find_duplicates_by_hash(folder):
    hash_map = {}
    for root, _, files in os.walk(folder):
        for file in files:
            full_path = os.path.join(root, file)
            if not is_image_file(full_path):
                continue
            file_hash = get_file_hash(full_path)
            print(f"Scanning: {full_path}")
            if file_hash:
                hash_map.setdefault(file_hash, []).append(full_path)
    return [paths for paths in hash_map.values() if len(paths) > 1]

def log_duplicates(duplicates):
    with open(LOG_FILE, "w", encoding="utf-8") as log:
        log.write(f"Photo Duplicate Report — {datetime.now()}\n")
        log.write("=" * 60 + "\n")
        for i, group in enumerate(duplicates, start=1):
            total_size = sum(os.path.getsize(p) for p in group)
            log.write(f"\nGroup {i} ({len(group)} files, {round(total_size/1_048_576, 2)} MB)\n")
            for path in group:
                log.write(f" - {path}\n")
            log.write("-" * 40 + "\n")
    print(f"\n📄 Log saved to: {LOG_FILE}")

def main():
    print(f"Scanning for duplicate images in: {TARGET_FOLDER}\n")
    duplicates = find_duplicates(TARGET_FOLDER)
    print(f"\nFound {len(duplicates)} duplicate group(s).")

    log_duplicates(duplicates)

    # Optional quick preview in console
    for i, group in enumerate(duplicates[:5], start=1):
        print(f"\nGroup {i} Preview ({len(group)} files):")
        for path in group:
            print(f" - {path}")
        print("-" * 40)

if __name__ == "__main__":
    main()
