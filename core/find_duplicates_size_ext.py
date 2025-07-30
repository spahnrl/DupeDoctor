import os
from collections import defaultdict

def find_duplicates_by_size_and_ext(folder):
    """
    Group files by (size, extension) tuple using os.lstat to avoid OneDrive downloads.
    Returns a list of lists of duplicate file paths.
    """
    grouped = defaultdict(list)
    for root, _, files in os.walk(folder):
        for file in files:
            full_path = os.path.join(root, file)
            try:
                stat = os.lstat(full_path)  # ✅ This avoids triggering cloud-only downloads
                size = stat.st_size
                ext = os.path.splitext(file)[1].lower()
                grouped[(size, ext)].append(full_path)
            except Exception:
                continue

    return [group for group in grouped.values() if len(group) > 1]
