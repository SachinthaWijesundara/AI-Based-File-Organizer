from pathlib import Path

EXTENSION_MAP = {
    "Documents": {".pdf", ".docx", ".doc", ".txt", ".md"},
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".webp"},
    "Videos": {".mp4", ".mkv", ".avi", ".mov"},
    "Audio": {".mp3", ".wav", ".flac"},
    "Archives": {".zip", ".rar", ".7z"},
    "Programs": {".exe", ".msi"},
}

#Converts to all file extentions and their types
extentionWithCategory = {ext:category for category, extention in EXTENSION_MAP.items() for ext in extention}

def findCategory(file: Path) -> str:
    return extentionWithCategory.get(file.suffix.lower(), "Other")

def get_destination(file: Path, main_folder: Path) -> Path:
    category = findCategory(file)
    return main_folder / "Organized" / category / file.name

#Avoid Duplicates
def resolveDuplicate (file: Path) -> Path:
    if not file.exists():
        return file

    stemOfName = file.stem
    suffixOfName = file.suffix
    destFolder = file.parent
    count = 1

    while file.exists() :
        file = destFolder / f"{stemOfName} ({count}){suffixOfName}"
        count +=1

    return file


