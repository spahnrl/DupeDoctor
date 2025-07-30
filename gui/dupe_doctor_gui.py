# dupe_doctor_gui.py
import os
import threading
import tkinter.filedialog as fd
import customtkinter as ctk
from tkinter import scrolledtext
from datetime import datetime
import shutil
import subprocess
from collections import defaultdict
import re

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("dark-blue")


def normalize_name(name):
    """Normalize filename by removing copy indicators like ' - Copy', ' (1)', etc."""
    name = re.sub(r" - Copy( \(\d+\))?$", "", name)
    name = re.sub(r" \(\d+\)$", "", name)
    return name.strip()


class DupeDoctorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("DupeDoctor – Duplicate File Cleaner")
        self.geometry("850x650")
        self.stop_move_requested = False
        self.selected_folder = ""
        self.setup_ui()

    def setup_ui(self):
        self.scrollable_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)
        ctk.CTkLabel(self.scrollable_frame, text="🧹 DupeDoctor – Duplicate File Cleaner",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(10, 20))

        # 📁 Folder Selection
        ctk.CTkLabel(self.scrollable_frame, text="📁 Select Folder to Scan", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        ctk.CTkButton(self.scrollable_frame, text="Browse Folder", command=self.select_folder).pack(pady=(5, 0))
        self.folder_label = ctk.CTkLabel(self.scrollable_frame, text="")
        self.folder_label.pack(anchor="w", padx=20)

        # 🔍 Match Criteria
        ctk.CTkLabel(self.scrollable_frame, text="🔍 Match Criteria", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 0))
        self.criteria = {}
        for label in ["Name", "Size", "Extension", "Created", "Modified"]:
            var = ctk.BooleanVar(value=(label in ["Name", "Size", "Extension"]))
            chk = ctk.CTkCheckBox(self.scrollable_frame, text=label, variable=var)
            chk.pack(anchor="w", padx=20)
            self.criteria[label] = var

        # 🚫 Exclude Extensions
        ctk.CTkLabel(self.scrollable_frame, text="🚫 Exclude File Extensions (comma-separated, e.g. py,pyc,ipynb)", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 0))
        self.exclude_entry = ctk.CTkEntry(self.scrollable_frame)
        self.exclude_entry.insert(0, "py,pyc,ipynb")
        self.exclude_entry.pack(fill="x", padx=5, pady=(0, 10))

        # 🚀 Start Scan
        ctk.CTkLabel(self.scrollable_frame, text="🚀 Start Scan", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(10, 0))
        self.scan_button = ctk.CTkButton(self.scrollable_frame, text="Start Scan", command=self.start_scan)
        self.scan_button.pack(pady=(5, 10))

        # 📦 Move Duplicates
        ctk.CTkLabel(self.scrollable_frame, text="📦 Move Duplicates", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        self.move_button = ctk.CTkButton(self.scrollable_frame, text="Move Duplicates", command=self.move_duplicates)
        self.move_button.pack(pady=(5, 10))

        self.stop_button = ctk.CTkButton(self.scrollable_frame, text="Stop Move", command=self.request_stop_move, fg_color="red")
        self.stop_button.pack(pady=(5, 0))
        self.stop_button.configure(state="disabled")

        self.undo_button = ctk.CTkButton(self.scrollable_frame, text="Undo Last Move", command=self.undo_last_move)
        self.undo_button.pack(pady=(10, 10))

        # 🪵 Log Output
        ctk.CTkLabel(self.scrollable_frame, text="🪵 Log Output", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        self.log_box = scrolledtext.ScrolledText(self.scrollable_frame, wrap="word", height=10, borderwidth=2, relief="solid")
        self.log_box.pack(fill="both", expand=True, padx=5, pady=10)

    def select_folder(self):
        folder = fd.askdirectory()
        if folder:
            self.selected_folder = folder
            self.folder_label.configure(text=folder)

    def log(self, message):
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")

    def start_scan(self):
        if not self.selected_folder:
            self.log("⚠️ Please select a folder to scan.")
            return

        self.log("🔍 Scan started with the following criteria:")
        criteria_mapping = {
            "Name": "name",
            "Size": "size",
            "Extension": "ext",
            "Created": "created",
            "Modified": "modified"
        }

        active_criteria = [criteria_mapping[key] for key, val in self.criteria.items() if val.get()]
        for crit in active_criteria:
            self.log(f"✅ {crit}")

        files_data = []
        exclude_exts = [e.strip().lower() for e in self.exclude_entry.get().split(",") if e.strip()]
        self.log(f"🚫 Skipping extensions: {', '.join(exclude_exts) or 'None'}")

        for root, _, files in os.walk(self.selected_folder):
            for f in files:
                ext = os.path.splitext(f)[1][1:].lower()
                if ext in exclude_exts:
                    continue
                full_path = os.path.join(root, f)
                try:
                    stat = os.stat(full_path)
                    base_name = os.path.splitext(f)[0]
                    files_data.append({
                        "path": full_path,
                        "name": normalize_name(base_name),
                        "ext": os.path.splitext(f)[1].lower(),
                        "size": stat.st_size,
                        "created": stat.st_ctime,
                        "modified": stat.st_mtime
                    })
                except Exception as e:
                    self.log(f"⚠️ Could not access {full_path}: {e}")

        self.log(f"🔍 Checking {len(files_data)} files...")

        groups = defaultdict(list)
        for f in files_data:
            try:
                key = tuple(f[k] for k in active_criteria)
                groups[key].append(f["path"])
            except KeyError as e:
                self.log(f"❌ Missing key: {e} in file {f['path']}")

        duplicates_found = 0
        for group, paths in groups.items():
            if len(paths) > 1:
                duplicates_found += 1
                self.log(f"\n🔗 Duplicate Group ({len(paths)} files):")
                for p in paths:
                    self.log(f"   - {p}")

        if duplicates_found == 0:
            self.log("\n✅ Scan complete. No duplicates found.")
        else:
            self.log(f"\n✅ Scan complete. {duplicates_found} duplicate group(s) found.")

    def move_duplicates(self):
        if not self.selected_folder:
            self.log("⚠️ Please select a folder first.")
            return

        self.stop_move_requested = False
        self.stop_button.configure(state="normal")
        self.move_button.configure(state="disabled")
        threading.Thread(target=self.handle_move_duplicates).start()

    def request_stop_move(self):
        self.log("🛑 Stop requested...")
        self.stop_move_requested = True

    def handle_move_duplicates(self):
        moved_files = []
        quarantine_dir = os.path.join(self.selected_folder, f"_quarantine_{os.path.basename(self.selected_folder)}")
        os.makedirs(quarantine_dir, exist_ok=True)

        files_by_base = defaultdict(list)
        exclude_exts = [e.strip().lower() for e in self.exclude_entry.get().split(",") if e.strip()]
        self.log(f"🚫 Skipping extensions: {', '.join(exclude_exts) or 'None'}")

        for root, _, files in os.walk(self.selected_folder):
            if quarantine_dir in root:
                continue
            for f in files:
                ext = os.path.splitext(f)[1][1:].lower()
                if ext in exclude_exts:
                    continue
                full_path = os.path.join(root, f)
                base_name = os.path.splitext(f)[0]
                normalized = normalize_name(base_name)
                files_by_base[normalized].append(full_path)

        for base, file_list in files_by_base.items():
            if len(file_list) <= 1:
                continue
            canonical = min(file_list, key=lambda p: (len(os.path.basename(p)), os.path.getctime(p)))
            for f in file_list:
                if f == canonical:
                    continue
                if self.stop_move_requested:
                    self.log("⛔ Move cancelled by user.")
                    break
                rel_path = os.path.relpath(f, self.selected_folder)
                dest_path = os.path.join(quarantine_dir, rel_path)
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                try:
                    shutil.move(f, dest_path)
                    moved_files.append((f, dest_path))
                    self.log(f"📦 Moved: {f} → {dest_path}")
                except Exception as e:
                    self.log(f"❌ Failed to move {f}: {str(e)}")

        if moved_files:
            log_path = os.path.join(quarantine_dir, "dupe_log.csv")
            with open(log_path, "w", encoding="utf-8") as f:
                for src, dst in moved_files:
                    f.write(f"{src},{dst}\n")
            self.log(f"📝 Log saved: {log_path}")
        else:
            self.log("📭 No duplicates moved or nothing matched criteria.")

        self.move_button.configure(state="normal")
        self.stop_button.configure(state="disabled")

    def undo_last_move(self):
        folder = fd.askdirectory(title="Select _quarantine_* folder to restore from")
        if not folder:
            self.log("⚠️ No folder selected.")
            return

        parent_dir = os.path.dirname(folder)
        command = ["robocopy", folder, parent_dir, "/E", "/XO"]
        self.log(f"🛠️ Running undo: {' '.join(command)}")

        try:
            subprocess.run(command, capture_output=True, text=True)
            self.log("✅ Undo completed using robocopy.")
        except Exception as e:
            self.log(f"❌ Undo failed: {str(e)}")


if __name__ == "__main__":
    app = DupeDoctorApp()
    app.mainloop()
