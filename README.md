# AI File Organizer

A local desktop tool that organizes a messy folder for you. Point it at a folder through a browser-based UI, and it sorts every loose file into tidy category folders — either by file type, by AI-guessed content, or both at once. Your existing subfolders are never touched, and files are never overwritten.

## Table of Contents

- [How It Works](#how-it-works)
- [The Three Modes](#the-three-modes)
- [How the AI Classification Works](#how-the-ai-classification-works)
- [Multi-Model Fallback](#multi-model-fallback)
- [Project Structure](#project-structure)
- [Setup](#setup)
- [Running It](#running-it)
- [Getting a Groq API Key](#getting-a-groq-api-key)
- [What It Actually Does to Your Files](#what-it-actually-does-to-your-files)
- [The Interface](#the-interface)
- [Error Handling](#error-handling)
- [Known Limitations](#known-limitations)
- [Tech Stack](#tech-stack)

## How It Works

This isn't a plain script — it's a small local web app. Running `main.py` starts a Flask server on your machine and opens a page in your browser. The page has three buttons; clicking one sends a request back to the Python server, which opens a native folder-picker dialog, scans the folder you choose, and moves files into a new `Organized/` folder inside it.

Nothing leaves your machine except filenames and short content excerpts, and only when you use an AI-powered mode — those get sent to Groq's API for classification.

## The Three Modes

**Extension sort** — sorts files by file type alone, using a fixed lookup table (`.pdf` → Documents, `.jpg` → Images, etc.). Instant, free, works offline, 100% predictable. Anything with an unrecognized extension goes into `Other`.

**AI sort** — classifies each file by what it actually *is*, into `University`, `Business`, `Personal`, `Entertainment`, `Finance`, or `Other`. Requires an internet connection and a free Groq API key.

**Extension, then AI** — a two-pass sort producing nested folders. Extension decides the outer folder, AI decides an inner subfolder within it:

```
Organized/
├── Documents/
│   ├── University/thesis_ch3.pdf
│   └── Business/invoice_4471.pdf
├── Images/
│   └── Personal/holiday.jpg
└── Videos/
    └── Entertainment/movie_s01e02.mkv
```

## How the AI Classification Works

### It reads inside your files, not just the names

A filename like `report_final_v2.pdf` tells the AI almost nothing. So before classifying, the app extracts a short excerpt from each file:

| File type | What's read |
|---|---|
| `.pdf` | Text from the **first page** |
| `.docx` | The **first three non-empty paragraphs** |
| `.txt`, `.md` | The **first 500 characters** |
| Images, videos, archives, executables, audio | **Nothing** — there's no readable text, so these are classified on filename alone |

Excerpts are capped at 300 characters before being sent. If a file is corrupt, encrypted, a scanned PDF with no text layer, or gets deleted mid-run, extraction fails silently and that file falls back to filename-only classification rather than crashing the run.

### Files are classified in batches, not one at a time

Rather than one API call per file, files are grouped into **batches of 5** and classified in a single request. The prompt sent looks like this:

```
Classify each file into exactly one category: University, Business, Personal, Entertainment, Finance, Other.

FILE: thesis_ch3.pdf
CONTENT: Chapter 3: Photosynthesis in Marine Algae. This dissertation examines...
---
FILE: holiday.jpg
CONTENT: (none - classify by filename only)
---

Reply with ONLY a JSON object mapping each exact filename to its category.
```

The reply comes back as JSON, keyed by filename:

```json
{"thesis_ch3.pdf": "University", "holiday.jpg": "Personal"}
```

This cuts API calls by roughly 5× compared to classifying files individually.

### Defending against bad AI responses

Language models don't always cooperate. Several safeguards run on every response:

- **JSON mode is enforced** (`response_format={"type": "json_object"}`) so the model can't wrap its answer in prose or markdown fences.
- **Results are matched by filename, never by position** — if the model reorders or skips an entry, categories can't get shifted onto the wrong files.
- **Filename matching is case-insensitive**, so a model that replies `Thesis_CH3.pdf` for a file named `thesis_ch3.pdf` still matches.
- **Invented categories are rejected.** If the model returns something not on the list (`Archives`, say), that file becomes `Other`.
- **Omitted files become `Other`** rather than raising an error.
- **Invented filenames are ignored** — only files you actually asked about appear in the result.

## Multi-Model Fallback

Groq applies rate limits **per model**, not per account. This app exploits that: rather than relying on one model, it chains three, falling through automatically when one runs out of quota.

| Order | Model |
|---|---|
| 1st | `openai/gpt-oss-20b` |
| 2nd | `openai/gpt-oss-120b` |
| 3rd | `qwen/qwen3.6-27b` |

**How the fallback behaves:**

- A batch is attempted on the first model. If it succeeds, the others are never touched.
- If that model returns a **rate-limit error**, the same batch is immediately retried on the next model — the user sees no interruption.
- The exhausted model is remembered, so every **later** batch skips it entirely without wasting a call. One rate-limited model costs exactly **one** wasted request for the whole run, not one per batch.
- Only when **all three** are exhausted does the run stop and report back.

Because the three quota pools are independent, this roughly **triples** your effective throughput before hitting a wall — around 24,000 tokens per minute combined instead of 8,000.

**Why not a second provider (Gemini, OpenAI)?** Staying inside Groq means one API key, one SDK, and one response format. A second provider would need all three duplicated for the same benefit.

## Project Structure

```
AI based File Organizer/
├── main.py                        # Flask server + routes, the entry point
├── run.bat                         # double-click to install deps and launch the app
├── requirements.txt                # Python dependencies
├── .env                            # your real Groq API key (never committed)
├── .env.example                    # template showing what .env should contain
├── templates/
│   └── index.html                  # the web UI
├── static/
│   ├── style.css                   # styling
│   └── script.js                   # button click handling, talks to the Flask routes
└── OrganizerLogic/
    ├── Scanner.py                  # lists loose files; extracts text from pdf/docx/txt
    ├── ExtentionMapper.py          # extension → category lookup, duplicate-name resolution
    ├── AiClassifier.py             # batching, prompt building, multi-model fallback
    └── Move.py                     # moves files into Organized/ (1-level or 2-level nesting)
```

## Setup

Requires Python 3.10 or newer.

> **Shortcut:** if you just want to skip straight to running the app, `run.bat` (double-click it) does steps 1–3 below automatically. The manual steps are here in case you want to understand or control each step yourself.

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

**Easiest way — double-click `run.bat`.** It installs any missing dependencies and starts the app in one step, no terminal required. A console window will pop up and stay open while the app runs — that's normal, leave it be.

**Manual way**, if you'd rather run it yourself:

```bash
.venv\Scripts\python.exe main.py
```

Either way, your default browser opens automatically to `http://127.0.0.1:5000`. Click a mode, pick a folder in the dialog that pops up, and wait for the result.

### Stopping the server

**Closing the browser tab does *not* stop the server.** The web page and the Python server behind it are two separate things — the server keeps running in the background even after the tab is closed, until you stop it directly.

To actually stop it, either:

- Press `Ctrl+C` in the console/terminal window, **or**
- Just close that console/terminal window entirely (clicking the X works fine — it shuts down the server along with it)

If the console window gets lost, minimized, or closed without noticing, look for `python.exe` in Task Manager and end it there as a last resort.

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

## The Interface

The page is plain HTML, CSS and JavaScript — no framework, no build step. Two things are worth knowing about how it behaves.

### Light and dark mode

There's a toggle in the top-right corner. On first visit the page follows **your operating system's** setting via the `prefers-color-scheme` media query, so it opens dark if your OS is dark. Once you click the toggle, your choice is saved to `localStorage` and overrides the OS setting from then on.

The theme is applied by a tiny inline script in the page `<head>` that runs *before* the body renders — without it you'd see a white flash on every load in dark mode.

### Responsive layout

The layout adapts to whatever screen it's on — phone, tablet, laptop, or a half-width desktop window. Two techniques do the work:

**Fluid grids.** The mode cards and the info panels below them use CSS Grid's `auto-fit`:

```css
grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
```

This fits as many columns as will hold their minimum width, so the column count adjusts continuously rather than snapping at a few hardcoded widths. In practice:

| Screen width | Cards shown as |
|---|---|
| Under ~560px (phones) | 1 column |
| ~560–900px (tablets, split windows) | 2 columns |
| Above ~900px (laptops, desktops) | 3 columns |

**Fluid typography and spacing.** Font sizes and padding use `clamp()` so they scale smoothly with the viewport instead of jumping:

| | Phone | Desktop |
|---|---|---|
| Heading | 29px | 60px |
| Subtitle | 14.5px | 17px |
| Page padding | 28px / 16px | 64px / 24px |

**Orientation and touch.** Because the rules key off *width* rather than device type, rotating a phone to landscape is handled automatically — the wider viewport simply moves it into the 2-column layout, with no separate orientation rule needed. There is no OS-specific styling and none is required; a Windows laptop in a narrow window and an Android phone in portrait get the same treatment because they have the same amount of space.

Two `@media` rules handle the things that can't scale smoothly:

- **Under 560px** — the "what gets read" rows stack vertically instead of squeezing a label and value onto one line, and the badge, status box and theme toggle all shrink.
- **`@media (hover: none)`** — disables the card lift-on-hover effect on touchscreens, where a tap would otherwise leave a card stuck in its hovered state.

## Error Handling

Every failure mode in the AI modes is handled explicitly. Nothing crashes, and **no file is ever left half-moved.**

### No internet connection

Detected as a connection error, which is deliberately **not** retried across the other models — if the network is down, all three would fail identically, so retrying would just make the user wait three times as long for the same answer. It fails on the first attempt and reports immediately.

- Before any file is sorted → *"No internet connection, could not reach the AI service."*
- Partway through → *"Connection dropped after sorting N files. The rest were left untouched."*

### All models rate-limited

Distinct from a connection failure, and reported differently so the message matches the real cause:

- Before any file is sorted → *"AI limit reached. Wait about a minute and try again."*
- Partway through → *"AI limit reached after sorting N files. Wait a minute and run again for the rest."*

Groq's limits reset roughly every 60 seconds. Because only loose files are scanned, simply running the same mode again picks up exactly where it left off — already-sorted files are inside `Organized/` and won't be re-processed.

### Malformed AI responses

If a model returns unparseable JSON or rejects the request, that model is skipped and the next one tries the same batch. If all three fail this way, the batch degrades to `Other` rather than aborting the run — files still get sorted, just not intelligently.

### Unreadable files

A corrupt PDF, an encrypted document, a scanned page with no text layer, or a file deleted mid-run all fail extraction silently and fall back to filename-only classification.

### Why files are never left half-moved

Each batch is **fully classified before any file in it is moved.** If classification fails, zero files from that batch move. So the folder is always in a clean state: files are either sorted into `Organized/`, or sitting untouched where they started — never in between.

Extension sort never contacts the internet at all, so none of this applies to it.

## Known Limitations

- **AI classification is not always accurate.** It's a language model making a judgement call. Content extraction helps a lot for documents, but a file with no readable text and a meaningless name (`IMG_4821.jpg`) gives it very little to work with. Extension sort is deterministic and always correct by definition; AI sort is a best-effort guess.
- **AI modes require an internet connection** to work at all — see [Error Handling](#error-handling) for exactly what happens when it isn't available.
- **AI modes are slower than Extension sort.** Batching helps, but each batch is still a network round-trip, sent one after another rather than in parallel. Expect roughly 45 files/minute on a single model, ~135/minute across all three before limits are hit.
- **Filenames *and content excerpts* are sent to a third party (Groq)** when using an AI mode. For PDFs, Word documents and text files, that includes up to 300 characters of the actual text inside them. Nothing else — not the full file, not its location on disk — leaves your machine, but be aware the excerpts do.
- **The category list is fixed** (`University`, `Business`, `Personal`, `Entertainment`, `Finance`, `Other`) — the AI can't invent new categories, it can only pick from this list.
- **No support for organizing files inside subfolders.** The tool intentionally only looks at the top level of the folder you choose.
- **Windows-oriented setup instructions** — the activation command (`.venv\Scripts\activate`) is Windows syntax; Mac/Linux users would use `source .venv/bin/activate` instead.
- **The UI is responsive, but the app is not usable from a phone.** The layout adapts down to small screens, but the server runs on your own machine and the folder picker is a native desktop dialog — so you're viewing it in a desktop browser regardless. The responsive layout matters for narrow or split-screen windows, not for actually running it from a phone.

## Tech Stack

- **Python** — core logic
- **Flask** — local web server, routes the UI's button clicks to the organizing logic
- **tkinter** — native OS folder-picker dialog
- **Groq API** — free-tier cloud AI, three models chained for fallback (`gpt-oss-20b`, `gpt-oss-120b`, `qwen3.6-27b`)
- **pypdf / python-docx** — extracting text from PDFs and Word documents
- **python-dotenv** — loading the API key from `.env`
- **HTML / CSS / JavaScript** — the frontend UI, no framework, no build step, with light/dark theme support
