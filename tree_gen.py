import os

# Treat these folders as files
treat_as_file = {"__pycache__", "c0mrade", ".vscode", ".git", "venv", "env", ".idea"}

def print_tree(path, prefix=""):
    entries = sorted(os.listdir(path))
    for i, entry in enumerate(entries):
        full_path = os.path.join(path, entry)
        branch = "├── " if i < len(entries) - 1 else "└── "
        print(prefix + branch + entry)

        # Only recurse if it's a directory and not in treat_as_file
        if os.path.isdir(full_path) and entry not in treat_as_file:
            extension = "│   " if i < len(entries) - 1 else "    "
            print_tree(full_path, prefix + extension)

if __name__ == "__main__":
    project_path = "/home/frank/Desktop/c0mrade-shop"  # change if needed
    print(project_path)
    print_tree(project_path)
