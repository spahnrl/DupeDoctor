import os
import hashlib
import shutil
from datetime import datetime

# === CONFIG ===
TARGET_FOLDER = r"C:\Users\Rick_DellXPS"
QUARANTINE_FOLDER = r"C:\Users\Rick_DellXPS\Duplicate_Quarantine"
HASH_CHUNK_SIZE = 8192

def get_file_hash(path, chunk_size=HASH_CHUNK_SIZE):
    hasher = hashlib.sha256()
    try:
        with open(path, 'rb') as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
    except (PermissionError, OSError):
        return None
    return hasher.hexdigest()

def find_duplicates(folder):
    hash_map = {}
    for root, _, files in os.walk(folder):
        for file in files:
            full_path = os.path.join(root, file)
            file_hash = get_file_hash(full_path)
            if file_hash:
                hash_map.setdefault(file_hash, []).append(full_path)
    return [paths for paths in hash_map.values() if len(paths) > 1]

def move_files_to_quarantine(duplicates):
    os.makedirs(QUARANTINE_FOLDER, exist_ok=True)
    count = 0

    for group in duplicates:
        keep = group[0]  # First file kept
        for dup in group[1:]:
            rel_path = os.path.relpath(dup, TARGET_FOLDER)
            dest_path = os.path.join(QUARANTINE_FOLDER, rel_path)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            try:
                shutil.copy2(dup, dest_path)
                print(f"Copied: {dup} -> {dest_path}")
                count += 1
            except Exception as e:
                print(f"Failed to copy {dup}: {e}")

    print(f"\n✅ Finished. {count} duplicate file(s) copied to quarantine folder.")

def main():
    print(f"Scanning for duplicates in: {TARGET_FOLDER}...\n")
    duplicates = find_duplicates(TARGET_FOLDER)
    print(f"Found {len(duplicates)} duplicate group(s).\n")
    copy_to_quarantine(duplicates)

if __name__ == "__main__":
    main()
