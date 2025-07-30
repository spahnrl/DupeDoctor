import os
import csv
from datetime import datetime
from collections import defaultdict
from core.find_duplicates_hash import find_duplicates_by_hash
from core.file_utils import get_file_metadata  # only if used

# === CONFIG ===
SOURCE_FOLDER = r"C:\Users\Rick_DellXPS\OneDrive\Pictures"
LOG_FOLDER = r"C:\Users\Rick_DellXPS\Duplicate_Quarantine_MetadataStrict"
LOG_FILE = os.path.join(LOG_FOLDER, "dryrun_quarantine_log.csv")

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def collect_metadata(folder):
    metadata = []
    for root, _, files in os.walk(folder):
        for file in files:
            full_path = os.path.join(root, file)
            try:
                stat = os.stat(full_path)
                name, ext = os.path.splitext(file)
                metadata.append({
                    "Full Path": full_path,
                    "File Name": name.lower(),
                    "Extension": ext.lower(),
                    "Size": stat.st_size,
                    "Date Modified": stat.st_mtime,
                    "Date Created": stat.st_ctime
                })
            except Exception as e:
                print(f"Skipped (no access): {full_path} — {e}")
    return metadata

def find_strict_duplicates(metadata):
    grouped = defaultdict(list)
    for entry in metadata:
        key = (
            entry["File Name"],
            entry["Extension"],
            entry["Size"],
            # entry["Date Modified"],
            # entry["Date Created"]
        )
        grouped[key].append(entry)
    return [group for group in grouped.values() if len(group) > 1]

def dry_run_log(duplicates):
    ensure_dir(LOG_FOLDER)
    log_entries = []

    for group in duplicates:
        for entry in group[1:]:  # keep the first file in each group
            log_entries.append({
                "Original Path": entry["Full Path"],
                "Size": entry["Size"],
                "Date Modified": datetime.fromtimestamp(entry["Date Modified"]),
                "Date Created": datetime.fromtimestamp(entry["Date Created"]),
                "Action": "Would move to quarantine"
            })
            print(f"💡 Would move: {entry['Full Path']}")

    if log_entries:
        with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=log_entries[0].keys())
            writer.writeheader()
            writer.writerows(log_entries)
        print(f"\n📄 Dry run log saved to: {LOG_FILE}")
    else:
        print("✅ No duplicate files found in dry run.")

def main():
    print(f"🔍 Scanning for strict duplicates in: {SOURCE_FOLDER}")
    metadata = collect_metadata(SOURCE_FOLDER)
    print(f"📦 Collected metadata for {len(metadata)} files.")

    duplicates = find_strict_duplicates(metadata)
    print(f"📑 Found {len(duplicates)} duplicate group(s) using strict matching.\n")

    dry_run_log(duplicates)

if __name__ == "__main__":
    main()
