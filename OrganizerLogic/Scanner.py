from pathlib import Path

SKIP_FOLDERS = {"Organized"}

def scan_folder(source: Path) -> list[Path]:
    files = []

    for item in source.iterdir():
        if item.is_file():
            files.append(item)
        elif item.is_dir() and item.name in SKIP_FOLDERS:
            continue

    return files