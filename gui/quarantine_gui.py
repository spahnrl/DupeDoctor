import os
import shutil
import csv
from datetime import datetime
from collections import defaultdict
import tkinter as tk
from tkinter import filedialog, messagebox
from quarantine.move_to_quarantine import move_files_to_quarantine

# === Folder Selection ===
def select_source_folder():
    root = tk.Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title="Select folder to scan for duplicates")
    if not folder:
        messagebox.showinfo("Cancelled", "No folder selected.")
        exit()
    return folder

# === Utility Functions ===
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

def find_medium_safe_duplicates(metadata):
    grouped = defaultdict(list)
    for entry in metadata:
        key = (
            entry["File Name"],
            entry["Extension"],
            entry["Size"]
        )
        grouped[key].append(entry)
    return [group for group in grouped.values() if len(group) > 1]

def move_to_quarantine(duplicates, source_folder, quarantine_folder):
    ensure_dir(quarantine_folder)
    log_entries = []

    for group in duplicates:
        for entry in group[1:]:  # Keep the first
            src = entry["Full Path"]
            rel_path = os.path.relpath(src, source_folder)
            dest = os.path.join(quarantine_folder, rel_path)

            try:
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.move(src, dest)
                log_entries.append({
                    "Original Path": src,
                    "Moved To": dest,
                    "Size": entry["Size"],
                    "Date Modified": datetime.fromtimestamp(entry["Date Modified"]),
                    "Date Created": datetime.fromtimestamp(entry["Date Created"])
                })
                print(f"Moved: {src} → {dest}")
            except Exception as e:
                print(f"❌ Failed to move {src}: {e}")
    return log_entries

def write_log(log_entries, log_path):
    ensure_dir(os.path.dirname(log_path))
    with open(log_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=log_entries[0].keys())
        writer.writeheader()
        writer.writerows(log_entries)
    print(f"\n📄 Move log saved to: {log_path}")

# === Main Entry Point ===
def main():
    source_folder = select_source_folder()
    folder_name = os.path.basename(source_folder.rstrip("\\/"))
    quarantine_folder = os.path.join(source_folder, f"_quarantine_{folder_name}")
    log_file = os.path.join(quarantine_folder, "moved_duplicates_log.csv")

    print(f"📦 Scanning for duplicates in: {source_folder}")
    metadata = collect_metadata(source_folder)
    print(f"📋 Collected metadata for {len(metadata)} files.")

    duplicates = find_medium_safe_duplicates(metadata)
    print(f"🔁 Found {len(duplicates)} duplicate group(s).\n")

    if duplicates:
        log_entries = move_to_quarantine(duplicates, source_folder, quarantine_folder)
        if log_entries:
            write_log(log_entries, log_file)
            messagebox.showinfo("Finished", f"{len(log_entries)} files moved to:\n{quarantine_folder}")
    else:
        print("✅ No duplicates found.")
        messagebox.showinfo("No Duplicates Found", "No medium-safe duplicates were detected.")

if __name__ == "__main__":
    main()
