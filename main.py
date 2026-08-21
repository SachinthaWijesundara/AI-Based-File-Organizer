from pathlib import Path
import tkinter as tk
from tkinter import filedialog
from flask import Flask, render_template, jsonify
import webbrowser
from groq import APIError, RateLimitError

from OrganizerLogic import Scanner
from OrganizerLogic import Move
from OrganizerLogic import AiClassifier
from OrganizerLogic import ExtentionMapper

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


@app.route("/info")
def info():
    return jsonify({
        "models": AiClassifier.MODELS,
        "categories": AiClassifier.CATEGORIES,
        "batch_size": AiClassifier.BATCH_SIZE,
    })


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
    source = pick_folder()
    if source is None:
        return jsonify({"status": "cancelled"})

    AiClassifier.reset_models()
    files = Scanner.scan_folder(source)
    sorted_count = 0
    try:
        for i in range(0, len(files), AiClassifier.BATCH_SIZE):
            batch = files[i:i + AiClassifier.BATCH_SIZE]
            categories = AiClassifier.classify_batch(batch)
            for item in batch:
                Move.move_file_ai(item, source, categories[item.name])
                sorted_count += 1
    except RateLimitError:
        return jsonify({"status": "ai_limit", "count": sorted_count, "folder": source.name})
    except APIError:
        return jsonify({"status": "ai_unavailable", "count": sorted_count, "folder": source.name})

    return jsonify({"status": "done", "count": sorted_count, "folder": source.name})


@app.route("/organize/both", methods=["POST"])
def organize_both():
    source = pick_folder()
    if source is None:
        return jsonify({"status": "cancelled"})
    
    AiClassifier.reset_models()
    files = Scanner.scan_folder(source)
    sorted_count = 0
    try:
        for i in range(0, len(files), AiClassifier.BATCH_SIZE):
            batch = files[i:i + AiClassifier.BATCH_SIZE]
            categories = AiClassifier.classify_batch(batch)
            for item in batch:
                extension_category = ExtentionMapper.findCategory(item)
                Move.move_file_both(item, source, extension_category, categories[item.name])
                sorted_count += 1
    except RateLimitError:
        return jsonify({"status": "ai_limit", "count": sorted_count, "folder": source.name})
    except APIError:
        return jsonify({"status": "ai_unavailable", "count": sorted_count, "folder": source.name})

    return jsonify({"status": "done", "count": sorted_count, "folder": source.name})


if __name__ == "__main__":
    webbrowser.open("http://127.0.0.1:5000")
    app.run(port=5000, threaded=False)
