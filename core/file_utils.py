import os
import csv
from datetime import datetime

# === CONFIG ===
TARGET_FOLDER = r"C:\Users\Rick_DellXPS\OneDrive\Pictures"
OUTPUT_FILE = r"C:\Users\Rick_DellXPS\Python\PythonProject\prj_dup_file_check\file_metadata.csv"

def collect_metadata(folder):
    metadata = []
    for root, _, files in os.walk(folder):
        for file in files:
            full_path = os.path.join(root, file)
            try:
                stat = os.stat(full_path)
                metadata.append({
                    "Full Path": full_path,
                    "File Name": file,
                    "Size (Bytes)": stat.st_size,
                    "Date Created": datetime.fromtimestamp(stat.st_ctime),
                    "Date Modified": datetime.fromtimestamp(stat.st_mtime)
                })
            except Exception as e:
                print(f"Skipped (no access): {full_path} — {e}")
    return metadata

def write_csv(metadata):
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=metadata[0].keys())
        writer.writeheader()
        writer.writerows(metadata)
    print(f"\n✅ Metadata saved to: {OUTPUT_FILE}")

def main():
    print(f"Scanning folder: {TARGET_FOLDER}")
    data = collect_metadata(TARGET_FOLDER)
    print(f"Found {len(data)} files.")
    if data:
        write_csv(data)

if __name__ == "__main__":
    main()
