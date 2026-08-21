import logging
from pathlib import Path
from pypdf import PdfReader
from docx import Document

logging.getLogger("pypdf").setLevel(logging.ERROR)

SKIP_FOLDERS = {"Organized"}

def scan_folder(source: Path) -> list[Path]:
    files = []

    for item in source.iterdir():
        if item.is_file():
            files.append(item)
        elif item.is_dir() and item.name in SKIP_FOLDERS:
            continue

    return files

def read_first_page_pdf(file: Path) -> str | None:
    try:
        reader = PdfReader(file)
        if not reader.pages:
            return None
        text = reader.pages[0].extract_text()
        return text.strip() or None
    except Exception:
        return None

def read_first_three_paragraph(file: Path) -> str | None:
    try:
        doc = Document(file)
        pragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        text = " ".join(pragraphs[:3])
        return text.strip() or None
    except Exception:
        return None

def extract_content(file: Path) -> str | None:
    if file.suffix.lower() == ".pdf":
        return read_first_page_pdf(file)      
    elif file.suffix.lower() == ".docx":
        return read_first_three_paragraph(file) 
    elif file.suffix.lower() in (".txt", ".md"):
        try:
            return file.read_text(errors="ignore")[:500].strip() or None
        except Exception:
            return None 
    else:
        return None   # images, zips, exe, mp3, mp4, etc — nothing to extract