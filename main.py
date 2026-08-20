from pathlib import Path
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

from OrganizerLogic import Scanner
from OrganizerLogic import Move


def main():

    #Using Tkinter to open a Folder Selection window
    root = tk.Tk()
    root.withdraw()

    source = filedialog.askdirectory(title="Select a Folder To ORganize")

    if not source:
        messagebox.showerror("Error", "No file selected", parent=root)
        return
    else:
        source = Path(source)

    root.destroy()

    pathList = Scanner.scan_folder(source)

    for item in pathList:
        Move.move_file(item, source)


if __name__ == "__main__":
    main()




