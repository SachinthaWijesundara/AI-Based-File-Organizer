import shutil
import OrganizerLogic.ExtentionMapper as ex
from pathlib import Path

def move_file(file: Path, main_folder: Path):
    destination = ex.get_destination(file, main_folder)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination = ex.resolveDuplicate(destination)
    shutil.move(str(file), str(destination))


def move_file_ai(file: Path, main_folder: Path, category: str):
    destination = main_folder / "Organized" / category / file.name
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination = ex.resolveDuplicate(destination)
    shutil.move(str(file), str(destination))