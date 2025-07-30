[⬇️ Download Latest Release](https://github.com/spahnrl/DupeDoctor/releases/latest)

> ⚠️ **Use with caution:** DupeDoctor moves files to a `_quarantine_*` folder based on your selections. Review contents before deleting. Use Undo when in doubt.

Here are your three final project files, ready to drop into `prj_dup_file_check/` before uploading to GitHub:

---

### ✅ `README.md`

````markdown
# 🧹 DupeDoctor – Duplicate File Cleaner

**DupeDoctor** is a powerful yet simple GUI tool built with Python and `customtkinter` to help identify and move duplicate files from any selected folder into a quarantine folder for review. It's designed to clean up redundant backup files (like "Copy", "Copy - Copy") while preserving the original version.

---

## 🚀 Features

- ✅ Detects duplicate files by name, size, extension, creation date, and modified date
- 📁 Automatically moves duplicates to a `_quarantine_<folder>` for safe review
- 🛑 Includes Stop and Undo buttons
- 🔍 Exclude specific file extensions from the scan
- 📝 Automatically generates a move log (`dupe_log.csv`)
- 🪟 Clean, scrollable GUI using `customtkinter`

---

## 🖥️ How to Run

1. **Clone or download the repo**
2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
````

3. Run the app:

   ```bash
   python dupe_doctor_gui.py
   ```

---

## 🔁 Undo Feature

If you move files to quarantine, you can easily restore them:

* Click **Undo Last Move**
* Select the quarantine folder (e.g. `_quarantine_MyDocuments`)
* All files will be moved back using `robocopy` (preserves timestamps)

---

## ⚙️ Requirements

* Python 3.8+
* Windows OS (robocopy dependency)
* `customtkinter` (included in requirements.txt)

---

## 📂 Folder Structure

```
prj_dup_file_check/
├── dupe_doctor_gui.py
├── requirements.txt
├── README.md
├── .gitignore
├── .venv/           # Ignored
└── .idea/           # Ignored
```

---

## 👨‍💻 Author

**Rick Spahn**
Built as part of `CV_Pipeline` and `prj_DupeDoctor_App_DuplicateFile_Mover`
Connect: [LinkedIn](https://www.linkedin.com/in/rick-spahn-14ba761/)
