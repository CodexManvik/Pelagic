from functools import lru_cache
from pathlib import Path

PROMPTS_DIR = Path(__file__).resolve().parents[1] / "prompts"


@lru_cache(maxsize=32)
def load_prompt(name: str) -> str:
    prompt_path = PROMPTS_DIR / name
    return prompt_path.read_text(encoding="utf-8")
