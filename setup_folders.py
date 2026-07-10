"""
One-time setup: moves the demo files into the folder structure Flask needs.
Run this ONCE from your PythonProject2 folder, then delete it.

    python setup_folders.py
"""
import os
import shutil

# Where this script lives = project root
ROOT = os.path.dirname(os.path.abspath(__file__))

# folder -> files that belong in it
LAYOUT = {
    "templates":  ["index.html", "events.html"],
    "static/css": ["style.css"],
    "static/js":  ["main.js"],
}

print("Setting up Flask folders in:", ROOT, "\n")

for folder, files in LAYOUT.items():
    dest_dir = os.path.join(ROOT, *folder.split("/"))
    os.makedirs(dest_dir, exist_ok=True)

    for name in files:
        src = os.path.join(ROOT, name)
        dst = os.path.join(dest_dir, name)

        if os.path.exists(dst):
            print(f"  already in place: {folder}/{name}")
        elif os.path.exists(src):
            shutil.move(src, dst)
            print(f"  moved: {name}  ->  {folder}/{name}")
        else:
            print(f"  MISSING (not found in root): {name}")

print("\nDone. Folder structure:")
for folder in LAYOUT:
    print("  " + folder + "/")

print("\nNow run app.py. You can delete setup_folders.py.")