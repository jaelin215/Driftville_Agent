# --------------------------------------
# Author: Jaelin Lee
# Date: Feb 9, 2026
# Description: To rename all files under `app/logs` folder. To replace ":" with "-" in the file names due to Windows I/O issue.
# --------------------------------------

from pathlib import Path

logs_dir = Path("app/logs")

for file in logs_dir.rglob("*:*"):  # Recursive find files with colons
    new_name = file.name.replace(":", "-")
    new_path = file.parent / new_name
    file.rename(new_path)
    print(f"Renamed: {file.name} → {new_name}")

print("✓ All files renamed successfully")
