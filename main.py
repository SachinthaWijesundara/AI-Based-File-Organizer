from pathlib import Path
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

#Using Tkinter to open a Folder Selection window
root = tk.Tk()
root.withdraw()

source = filedialog.askdirectory(title="Select a Folder To ORganize")

if not source:
    messagebox.showerror("Error", "No file selected", parent=root)
else:
    source = Path(source)

root.destroy()
