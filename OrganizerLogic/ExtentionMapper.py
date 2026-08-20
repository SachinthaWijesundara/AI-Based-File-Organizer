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
extentionWithCategory = {ext:category for category, extention in EXTENSION_MAP.items() for ext in extention}\

def findCategory(file: Path) -> str:
    return extentionWithCategory.get(file.suffix.lower(), "Other")



