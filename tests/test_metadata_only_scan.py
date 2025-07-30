import os
import time


def scan_folder_metadata_only(folder_path, limit=50):
    result = []
    file_count = 0

    for root, _, _ in os.walk(folder_path):
        try:
            with os.scandir(root) as entries:
                for entry in entries:
                    if not entry.is_file(follow_symlinks=False):
                        continue

                    info = {
                        "Path": entry.path,
                        "Name": entry.name,
                        "Extension": os.path.splitext(entry.name)[1].lower()
                    }

                    try:
                        stat = entry.stat(follow_symlinks=False)
                        info["Size"] = stat.st_size
                        info["Created"] = time.ctime(stat.st_ctime)
                        info["Modified"] = time.ctime(stat.st_mtime)
                        info["Stat Success"] = True
                    except Exception as e:
                        info["Size"] = "Unavailable"
                        info["Created"] = "Unavailable"
                        info["Modified"] = "Unavailable"
                        info["Stat Success"] = False
                        info["Error"] = str(e)

                    result.append(info)
                    file_count += 1

                    if file_count >= limit:
                        return result

        except Exception as e:
            print(f"Failed to access {root}: {e}")

    return result


# Run the test
if __name__ == "__main__":
    test_folder = r"C:\Users\Rick_DellXPS\OneDrive\Recordings"  # Adjust if needed
    metadata = scan_folder_metadata_only(test_folder)

    print(f"\n📋 Metadata Scan Report (first {len(metadata)} files):\n")
    for item in metadata:
        print(f"{item['Path']}")
        print(f"  Extension: {item['Extension']}")
        print(f"  Size: {item['Size']}")
        print(f"  Created: {item['Created']}")
        print(f"  Modified: {item['Modified']}")
        print(f"  Stat OK?: {item['Stat Success']}")
        if not item['Stat Success']:
            print(f"  Error: {item['Error']}")
        print("-" * 50)
