#!/usr/bin/env python3
"""
Validate topics.json and foods.json before pushing to the NutriLens content repo.

Usage:  python3 validate.py            # checks both files in the current folder
        python3 validate.py foods.json # check one file

Exit code 0 = OK, 1 = problems found (listed).
"""
import json
import re
import sys
from pathlib import Path

LANGS = ("ta", "hi")
problems: list[str] = []


def err(msg: str) -> None:
    problems.append(msg)


def load(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        err(f"{path}: file not found")
    except json.JSONDecodeError as e:
        err(f"{path}: invalid JSON — {e.msg} at line {e.lineno}, column {e.colno}")
    return None


def check_foods(path: Path) -> None:
    d = load(path)
    if d is None:
        return
    if d.get("schema_version") != 1:
        err(f"{path}: schema_version must be 1")
    cv = d.get("content_version")
    if not isinstance(cv, (int, float)) or isinstance(cv, bool):
        err(f"{path}: content_version must be a NUMBER (e.g. 2), got {cv!r}")
    cats = d.get("categories")
    if not isinstance(cats, dict) or not cats:
        err(f"{path}: 'categories' must be a non-empty object")
        cats = {}
    foods = d.get("foods")
    if not isinstance(foods, list) or not foods:
        err(f"{path}: 'foods' must be a non-empty list")
        return
    seen: set[str] = set()
    for i, f in enumerate(foods):
        tag = f"{path} foods[{i}] ({f.get('id', '?')} / {f.get('name', '?')})"
        for k in ("id", "name", "category", "serving"):
            if not isinstance(f.get(k), str) or not f[k].strip():
                err(f"{tag}: '{k}' must be a non-empty string")
        for k in ("cal", "protein", "carbs", "fat"):
            v = f.get(k)
            if not isinstance(v, (int, float)) or isinstance(v, bool) or v < 0:
                err(f"{tag}: '{k}' must be a number ≥ 0")
        if f.get("id") in seen:
            err(f"{tag}: duplicate id")
        seen.add(f.get("id"))
        if f.get("category") not in cats:
            err(f"{tag}: category '{f.get('category')}' is not in 'categories'")
    print(f"✓ {path}: {len(foods)} foods, {len(cats)} categories, content_version {cv}")


def check_topics(path: Path) -> None:
    d = load(path)
    if d is None:
        return
    if d.get("schema_version") != 1:
        err(f"{path}: schema_version must be 1")
    cv = d.get("content_version")
    if not isinstance(cv, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", cv):
        err(f"{path}: content_version must be a date string 'YYYY-MM-DD', got {cv!r}")
    topics = d.get("topics")
    if not isinstance(topics, list) or not topics:
        err(f"{path}: 'topics' must be a non-empty list")
        return
    keys: set[str] = set()
    card_ids: set[str] = set()
    total = 0
    for t in topics:
        ttag = f"{path} topic '{t.get('key', '?')}'"
        if t.get("key") in keys:
            err(f"{ttag}: duplicate key")
        keys.add(t.get("key"))
        for k in ("topic_id", "key", "title", "subtitle", "emoji", "icon_name", "description"):
            if not isinstance(t.get(k), str) or not t[k].strip():
                err(f"{ttag}: '{k}' must be a non-empty string")
        cards = t.get("cards")
        if not isinstance(cards, list) or not cards:
            err(f"{ttag}: 'cards' must be a non-empty list")
            continue
        if t.get("card_count") != len(cards):
            err(f"{ttag}: card_count is {t.get('card_count')} but there are {len(cards)} cards")
        m = re.match(r"(\d+) cards", t.get("description", ""))
        if m and int(m.group(1)) != len(cards):
            err(f"{ttag}: description says '{m.group(0)}' but there are {len(cards)} cards")
        tr = t.get("translations") or {}
        for lang in LANGS:
            if not isinstance(tr.get(lang), dict) or not tr[lang].get("title"):
                err(f"{ttag}: missing translations.{lang}.title")
        orders = sorted(c.get("order") for c in cards if isinstance(c.get("order"), int))
        if orders != list(range(1, len(cards) + 1)):
            err(f"{ttag}: card 'order' values must be exactly 1..{len(cards)} with no gaps/duplicates")
        for c in cards:
            ctag = f"{ttag} card '{c.get('card_id', '?')}'"
            if c.get("card_id") in card_ids:
                err(f"{ctag}: duplicate card_id")
            card_ids.add(c.get("card_id"))
            for k in ("card_id", "number", "label", "title"):
                if not isinstance(c.get(k), str) or not c[k].strip():
                    err(f"{ctag}: '{k}' must be a non-empty string")
            content = c.get("content")
            if not isinstance(content, dict) or not content.get("type"):
                err(f"{ctag}: 'content' must be an object with a 'type'")
            ctr = c.get("translations") or {}
            for lang in LANGS:
                if not isinstance(ctr.get(lang), dict) or not ctr[lang].get("title"):
                    err(f"{ctag}: missing translations.{lang}.title (card will show English)")
        total += len(cards)
    print(f"✓ {path}: {len(topics)} topics, {total} cards, content_version {cv}")


def main() -> int:
    targets = [Path(a) for a in sys.argv[1:]] or [Path("topics.json"), Path("foods.json")]
    for p in targets:
        if p.name.startswith("foods"):
            check_foods(p)
        elif p.name.startswith("topics"):
            check_topics(p)
        else:
            err(f"{p}: don't know how to validate this file (expected topics*.json or foods*.json)")
    if problems:
        print(f"\n✗ {len(problems)} problem(s):")
        for p in problems:
            print("  -", p)
        return 1
    print("\nAll good — safe to bump content_version and push.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
