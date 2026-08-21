
import os, json
from pathlib import Path
from groq import Groq, RateLimitError, BadRequestError
from dotenv import load_dotenv
from OrganizerLogic.Scanner import extract_content

load_dotenv()
APIClient = Groq(api_key=os.environ.get("GROQ_API_KEY"))

CATEGORIES = ["University", "Business", "Personal", "Entertainment", "Finance", "Other"]
MODELS = ["openai/gpt-oss-20b", "openai/gpt-oss-120b", "qwen/qwen3.6-27b"]
BATCH_SIZE = 5

_exhausted = set()


def reset_models():
    _exhausted.clear()


def _build_prompt(files: list[Path]) -> str:
    blocks = []
    for f in files:
        content = extract_content(f)
        line = f"CONTENT: {content[:300]}" if content else "CONTENT: (none - classify by filename only)"
        blocks.append(f"FILE: {f.name}\n{line}\n---")
    return (
        f"Classify each file into exactly one category: {', '.join(CATEGORIES)}.\n\n"
        + "\n".join(blocks)
        + "\n\nReply with ONLY a JSON object mapping each exact filename to its category."
    )

def classify_batch(files: list[Path]) -> dict[str, str]:
    if not files:
        return {}

    prompt = _build_prompt(files)
    last_error = None

    for model in MODELS:
        if model in _exhausted:
            continue
        try:
            response = APIClient.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
            )
            raw = json.loads(response.choices[0].message.content)
        except RateLimitError as error:
            _exhausted.add(model)
            last_error = error
            continue
        except (json.JSONDecodeError, BadRequestError, AttributeError, TypeError):
            continue

        lookup = {str(k).lower(): v for k, v in raw.items()}
        return {
            f.name: (lookup.get(f.name.lower()) if lookup.get(f.name.lower()) in CATEGORIES else "Other")
            for f in files
        }

    if last_error is not None:
        raise last_error

    return {f.name: "Other" for f in files}