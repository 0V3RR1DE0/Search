import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import platform

def get_all_drives():
    if platform.system() == "Windows":
        from string import ascii_uppercase
        return [f"{drive}:/" for drive in ascii_uppercase if os.path.exists(f"{drive}:/")]
    else:
        return ["/"]

def search_file(file_name, path):
    return [str(p) for p in Path(path).rglob(file_name)]

def search_text(text, path):
    found_files = {}
    text_lower = text.lower()
    for file_path in Path(path).rglob('*'):
        if file_path.is_file():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line_number, line in enumerate(f, 1):
                        if text_lower in line.lower():
                            if str(file_path) not in found_files:
                                found_files[str(file_path)] = []
                            found_files[str(file_path)].append((line_number, line.lower().index(text_lower) + 1))
            except Exception:
                pass
    return found_files

def search_folder(folder_name, path):
    return [str(p) for p in Path(path).rglob(folder_name) if p.is_dir()]

def print_clickable_link(path):
    if platform.system() == "Windows":
        print(f"\033]8;;file://{path}\a{path}\033]8;;\a")
    else:
        print(f"\033]8;;file://{path}\a{path}\033]8;;\a")

def main():
    if len(sys.argv) < 3:
        print_help()
        return

    option = sys.argv[1]
    keyword = sys.argv[2]
    search_paths = [sys.argv[3]] if len(sys.argv) > 3 else get_all_drives()

    if option in ('-h', '--help'):
        print_help()
        return

    search_function = {
        '-f': search_file,
        '-t': search_text,
        '-ft': search_folder
    }.get(option)

    if not search_function:
        print("Invalid option. Please use -f, -t, or -ft.")
        print_help()
        return

    results = []
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(search_function, keyword, path) for path in search_paths]
        for future in as_completed(futures):
            result = future.result()
            if result:
                results.append(result)

    if not results:
        print("The specified file, text, or folder was not found.")
    else:
        if option == '-t':
            for result_dict in results:
                for file_path, positions in result_dict.items():
                    print_clickable_link(file_path)
                    for line, column in positions:
                        print(f"    Line {line}, Column {column}")
        else:  # -f or -ft
            for sublist in results:
                for item in sublist:
                    print_clickable_link(item)

def print_help():
    help_text = """
Usage: search.py [OPTION] <file/folder/text string> [<optional path>]
Options:
  -f        Search for a file
  -t        Search for text inside files
  -ft       Search for a folder
  -h, --help  Display this help message
"""
    print(help_text)

if __name__ == "__main__":
    main()