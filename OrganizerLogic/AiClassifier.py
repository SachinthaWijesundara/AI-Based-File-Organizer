
import os
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

APIClient = Groq(api_key=os.environ.get("GROQ_API_KEY"))

CATEGORIES = ["University", "Business", "Personal", "Entertainment", "Finance", "Other"]

def classify_file(file: Path) -> str:
    prompt = (
        f"Classify this filename into exactly one category: {', '.join(CATEGORIES)}. "
        f"Filename: {file.name}. "
        f"Reply with only the category name, nothing else."
    )

    response = APIClient.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}],
    )

    category = response.choices[0].message.content.strip()
    return category if category in CATEGORIES else "Other"