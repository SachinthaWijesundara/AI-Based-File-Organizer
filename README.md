# AI File Organizer

A local desktop tool that organizes a messy folder for you. Point it at a folder through a browser-based UI, and it sorts every loose file into tidy category folders — either by file type, by AI-guessed content, or both at once. Your existing subfolders are never touched, and files are never overwritten.

## Table of Contents

- [How It Works](#how-it-works)
- [The Three Modes](#the-three-modes)
- [Project Structure](#project-structure)
- [Setup](#setup)
- [Running It](#running-it)
- [Getting a Groq API Key](#getting-a-groq-api-key)
- [What It Actually Does to Your Files](#what-it-actually-does-to-your-files)
- [Known Limitations](#known-limitations)
- [Tech Stack](#tech-stack)

## How It Works

This isn't a plain script — it's a small local web app. Running `main.py` starts a Flask server on your machine and opens a page in your browser. The page has three buttons; clicking one sends a request back to the Python server, which opens a native folder-picker dialog, scans the folder you choose, and moves files into a new `Organized/` folder inside it.

Nothing leaves your machine except the filenames themselves, and only when you use an AI-powered mode — those get sent to Groq's API for classification.

## The Three Modes

**Extension sort** — sorts files by file type alone, using a fixed lookup table (`.pdf` → Documents, `.jpg` → Images, etc.). Instant, free, works offline, 100% predictable. Anything with an unrecognized extension goes into `Other`.

**AI sort** — reads each filename and asks an AI model (via the Groq API) which category it belongs in: `University`, `Business`, `Personal`, `Entertainment`, `Finance`, or `Other`. Requires an internet connection and a free Groq API key.

**Extension, then AI** — a two-pass sort. Extension decides the outer folder, AI decides an inner subfolder within it, e.g. `Organized/Documents/University/thesis.pdf`.

## Project Structure

```
AI based File Organizer/
├── main.py                        # Flask server + routes, the entry point
├── requirements.txt                # Python dependencies
├── .env                            # your real Groq API key (never committed)
├── .env.example                    # template showing what .env should contain
├── templates/
│   └── index.html                  # the web UI
├── static/
│   ├── style.css                   # styling
│   └── script.js                   # button click handling, talks to the Flask routes
└── OrganizerLogic/
    ├── Scanner.py                  # lists loose files in the chosen folder (skips subfolders)
    ├── ExtentionMapper.py          # extension → category lookup, duplicate-name resolution
    ├── AiClassifier.py             # sends filenames to Groq, gets back a category
    └── Move.py                     # actually moves files into Organized/<category>/
```

## Setup

Requires Python 3.10 or newer.

```bash
# 1. Create a virtual environment (first time only)
python -m venv .venv

# 2. Activate it (every time you open a new terminal)
.venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your own Groq API key
#    Copy .env.example to a new file named .env, and paste in a real key
copy .env.example .env
```

Then open `.env` and replace the placeholder with your actual key:

```
GROQ_API_KEY=your_real_key_here
```

`.env` is listed in `.gitignore` and will never be committed — this is your personal, private key.

## Running It

```bash
.venv\Scripts\python.exe main.py
```

This opens your default browser to `http://127.0.0.1:5000` automatically. Leave the terminal window open — closing it, or pressing `Ctrl+C`, shuts the server down and the page stops working.

Click a mode, pick a folder in the dialog that pops up, and wait for the result.

## Getting a Groq API Key

Only needed for "AI sort" or "Extension, then AI" — the plain Extension sort works with no key at all.

1. Go to [console.groq.com](https://console.groq.com)
2. Sign up (free, no credit card required)
3. Generate an API key
4. Paste it into your `.env` file as shown above

Groq's free tier is generous for personal use, but is still rate-limited — organizing a very large number of files in one run could hit that limit.

## What It Actually Does to Your Files

- Only **loose files sitting directly inside** the folder you pick are touched. Existing subfolders and everything inside them are left completely alone.
- Sorted files are moved into a new `Organized/` folder created inside the folder you picked — nothing is copied, files are relocated.
- If two files would end up with the same name in the same destination, the second one is automatically renamed (`report.pdf` → `report (1).pdf`) instead of overwriting the first.
- There is currently **no undo feature.** Test on a folder you don't mind experimenting with before running it on something important.

## Known Limitations

- **AI classification is not always accurate.** It's a language model guessing from a filename alone — a poorly named file (`IMG_4821.jpg`, `final_final_v2.docx`) gives it very little to work with, and it can misclassify. Extension sort is deterministic and always correct by definition; AI sort is a best-effort guess.
- **AI modes require an internet connection.** Every file triggers a separate network call to Groq's servers — if you're offline, only Extension sort will work.
- **AI modes are noticeably slower than Extension sort**, since each file is classified with its own separate API call, one after another, not in parallel.
- **Filenames are sent to a third party (Groq)** when using an AI mode. Nothing else about the file — not its contents, not its location — is sent, but be aware the filename itself leaves your machine.
- **The category list is fixed** (`University`, `Business`, `Personal`, `Entertainment`, `Finance`, `Other`) — the AI can't invent new categories, it can only pick from this list.
- **No support for organizing files inside subfolders.** The tool intentionally only looks at the top level of the folder you choose.
- **Windows-oriented setup instructions** — the activation command (`.venv\Scripts\activate`) is Windows syntax; Mac/Linux users would use `source .venv/bin/activate` instead.

## Tech Stack

- **Python** — core logic
- **Flask** — local web server, routes the UI's button clicks to the organizing logic
- **tkinter** — native OS folder-picker dialog
- **Groq API** — free-tier cloud AI for content-based classification
- **HTML / CSS / JavaScript** — the frontend UI, no framework, no build step
