from pathlib import Path
import tkinter as tk
from tkinter import filedialog
from flask import Flask, render_template, jsonify
import webbrowser

from OrganizerLogic import Scanner
from OrganizerLogic import Move

app = Flask(__name__)


def pick_folder():
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    selected = filedialog.askdirectory(title="Select a Folder To Organize")
    root.destroy()
    return Path(selected) if selected else None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/organize/extension", methods=["POST"])
def organize_extension():
    source = pick_folder()
    if source is None:
        return jsonify({"status": "cancelled"})

    files = Scanner.scan_folder(source)
    for item in files:
        Move.move_file(item, source)

    return jsonify({"status": "done", "count": len(files), "folder": source.name})


@app.route("/organize/ai", methods=["POST"])
def organize_ai():
    return jsonify({"status": "unavailable"})


@app.route("/organize/both", methods=["POST"])
def organize_both():
    return jsonify({"status": "unavailable"})


if __name__ == "__main__":
    webbrowser.open("http://127.0.0.1:5000")
    app.run(port=5000, threaded=False)
