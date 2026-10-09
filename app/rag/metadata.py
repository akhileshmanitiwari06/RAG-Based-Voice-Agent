import json
from pathlib import Path


TEMPLATE_DIR = (
    Path(__file__).resolve().parents[2]
    / "knowledge"
    / "templates"
)


def load_templates():
    templates = []

    for file in TEMPLATE_DIR.rglob("*.json"):
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)

        templates.append(data)

    return templates