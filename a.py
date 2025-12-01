import os

EXCLUDE = {"node_modules", ".git", ".venv", "venv", "__pycache__"}  # folders to skip
EXCLUDE_FILES = {".DS_Store", "Thumbs.db"}  # file names to skip
EXCLUDE_FILE_EXTENSIONS = {".pyc", ".log", ".tmp", ".txt", ".jpg"}  # file extensions to skip (include the dot)

def print_tree(root, prefix=""):
    try:
        entries = sorted(os.listdir(root))
    except PermissionError:
        return  # skip folders we can't access

    dirs = [e for e in entries if os.path.isdir(os.path.join(root, e)) and e not in EXCLUDE]
    files = []
    for e in entries:
        full = os.path.join(root, e)
        if not os.path.isfile(full):
            continue
        name = e
        _, ext = os.path.splitext(name)
        if name in EXCLUDE_FILES:
            continue
        if ext.lower() in EXCLUDE_FILE_EXTENSIONS:
            continue
        files.append(e)

    combined = dirs + files

    for i, entry in enumerate(combined):
        path = os.path.join(root, entry)
        is_last = (i == len(combined) - 1)

        connector = "└── " if is_last else "├── "
        print(prefix + connector + entry)

        if os.path.isdir(path) and entry not in EXCLUDE:
            new_prefix = prefix + ("    " if is_last else "│   ")
            print_tree(path, new_prefix)


if __name__ == "__main__":
    start_path = "./implantdetect-training"  # change to any start directory
    print(os.path.abspath(start_path))
    print_tree(start_path)
