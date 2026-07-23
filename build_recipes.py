#!/usr/bin/env python3
"""Parse reseptikirja.md → recipes.json for the static UI."""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MD_PATH = ROOT / "reseptikirja.md"
OUT_PATH = ROOT / "recipes.json"

SECTION_IDS = {
    "Pääruoat": "paaruuat",
    "Jälkiruoat": "jalkiruoat",
    "Kastikkeet ja soosit": "kastikkeet",
    "Perusravintoarvot (usein käytetyt)": "perusarvot",
}

KNOWN_LABELS = (
    "Ainekset",
    "Valmistus",
    "Makrot",
    "Vinkki",
    "Huom",
    "Soveltuu",
    "Pohja",
    "Kastike",
    "Täytteet (vakio)",
    "Kypsennys",
    "Säilyvyys",
    "Mustikkaversio",
    "Kevennetyt variaatiot",
    "Lisävinkki",
    "Variaatio",
    "Variaatio (kidneypavuilla, vähemmän kaloreita)",
    "Ultimate-versio",
    "Glaze",
    "Kasvatettu glaze (isompi versio, 5 ann)",
    "Lime-jogurttisoosi (muhennosversio)",
)


def slugify(name: str) -> str:
    if name in SECTION_IDS:
        return SECTION_IDS[name]
    nfkd = unicodedata.normalize("NFKD", name)
    ascii_ = "".join(c for c in nfkd if not unicodedata.combining(c))
    ascii_ = ascii_.lower()
    ascii_ = ascii_.replace("ä", "a").replace("ö", "o").replace("å", "a")
    ascii_ = re.sub(r"[^a-z0-9]+", "-", ascii_).strip("-")
    return ascii_ or "section"


def truncate(text: str, limit: int = 48) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def extract_macros(blocks: list[dict]) -> str | None:
    for block in blocks:
        if block.get("label") == "Makrot":
            parts = []
            if block.get("content"):
                parts.append(block["content"])
            if block.get("items"):
                parts.extend(block["items"])
            raw = " · ".join(parts)
            return truncate(raw, 56) if raw else None
    return None


def parse_table(lines: list[str]) -> dict | None:
    rows = []
    for line in lines:
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-{3,}:?", c.replace(" ", "")) for c in cells):
            continue
        rows.append(cells)
    if len(rows) < 2:
        return None
    return {"headers": rows[0], "rows": rows[1:]}


def flush_block(blocks: list[dict], label: str | None, content_lines: list[str], items: list[str], steps: list[str]):
    if not label and not content_lines and not items and not steps:
        return
    content = "\n".join(content_lines).strip()
    block: dict = {
        "type": "section" if label else "paragraph",
        "label": label or "",
        "content": content,
        "items": items[:],
    }
    if steps:
        block["steps"] = steps[:]
    blocks.append(block)


def parse_recipe_body(body: str) -> tuple[str | None, list[dict], bool, str | None]:
    lines = body.strip().splitlines()
    meta = None
    favorite = False
    badge = None
    blocks: list[dict] = []

    i = 0
    # Leading italic meta lines and favorite markers
    while i < len(lines):
        raw = lines[i].strip()
        if not raw:
            i += 1
            continue
        if raw.startswith("*") and raw.endswith("*") and not raw.startswith("**"):
            meta_text = raw.strip("*").strip()
            if "Mikin suosikki" in meta_text:
                favorite = True
                badge = "Mikin suosikki"
                # may also include portion info before/after
                other = re.sub(r"\s*[·|]\s*Mikin suosikki\s*", " ", meta_text, flags=re.I)
                other = re.sub(r"Mikin suosikki", "", other, flags=re.I).strip(" ·|-")
                if other and not meta:
                    meta = other
            elif not meta:
                meta = meta_text
            i += 1
            continue
        if raw.lower().startswith("mikin suosikki") or "**mikin suosikki**" in raw.lower():
            favorite = True
            badge = "Mikin suosikki"
            i += 1
            continue
        break

    label = None
    content_lines: list[str] = []
    items: list[str] = []
    steps: list[str] = []

    def start_label(new_label: str):
        nonlocal label, content_lines, items, steps
        flush_block(blocks, label, content_lines, items, steps)
        label = new_label
        content_lines = []
        items = []
        steps = []

    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()
        i += 1

        if stripped == "---":
            continue

        # Favorite badge inline in body
        if re.search(r"Mikin suosikki", stripped, re.I):
            favorite = True
            badge = "Mikin suosikki"
            # keep line if it has other content after removing badge markers
            cleaned = re.sub(r"\*?Mikin suosikki\*?", "", stripped, flags=re.I).strip(" ·|-")
            if not cleaned:
                continue
            stripped = cleaned

        bold = re.match(r"^\*\*(.+?):\*\*\s*(.*)$", stripped)
        if bold:
            lab, rest = bold.group(1).strip(), bold.group(2).strip()
            start_label(lab)
            if rest:
                content_lines.append(rest)
            continue

        # Numbered steps under Valmistus (or current label)
        step_m = re.match(r"^(\d+)\.\s+(.+)$", stripped)
        if step_m and (label == "Valmistus" or steps or (label and not items and not content_lines)):
            if label != "Valmistus" and not steps and not label:
                start_label("Valmistus")
            steps.append(step_m.group(2).strip())
            continue

        if stripped.startswith("- "):
            items.append(stripped[2:].strip())
            continue

        if not stripped:
            # blank line: keep paragraph breaks inside content
            if content_lines and content_lines[-1] != "":
                content_lines.append("")
            continue

        content_lines.append(stripped)

    flush_block(blocks, label, content_lines, items, steps)

    # Drop empty trailing paragraph blocks
    blocks = [
        b
        for b in blocks
        if b.get("content") or b.get("items") or b.get("steps") or b.get("label")
    ]

    return meta, blocks, favorite, badge


def parse_markdown(text: str) -> dict:
    # Drop title + intro + TOC; split on ## sections
    parts = re.split(r"^## ", text, flags=re.M)
    header = parts[0]
    title_m = re.search(r"^#\s+(.+)$", header, re.M)
    title = title_m.group(1).strip() if title_m else "Mikin Reseptikirja"
    brand = "Mikin Reseptikirja"
    intro_lines = []
    for line in header.splitlines():
        if line.startswith("#") or line.startswith("---") or line.startswith("##"):
            continue
        if line.strip():
            intro_lines.append(line.strip())
    intro = " ".join(intro_lines[:2]) if intro_lines else ""

    sections = []
    footer = None

    for part in parts[1:]:
        lines = part.splitlines()
        if not lines:
            continue
        name = lines[0].strip()
        body = "\n".join(lines[1:])

        if name.lower().startswith("sisällys"):
            continue

        # Footer italic after last section handled separately
        section_id = slugify(name)
        recipes = []
        table = None
        raw = []

        # Split recipes on ### 
        if "### " in body or body.lstrip().startswith("### "):
            recipe_parts = re.split(r"^### ", body, flags=re.M)
            preamble = recipe_parts[0].strip()
            if preamble and not preamble.startswith("|"):
                raw = [l for l in preamble.splitlines() if l.strip()]
            for rp in recipe_parts[1:]:
                rlines = rp.splitlines()
                rtitle = rlines[0].strip()
                rbody = "\n".join(rlines[1:])
                meta, blocks, favorite, badge = parse_recipe_body(rbody)
                # Detect favorite in meta italic that includes it
                if meta and "Mikin suosikki" in meta:
                    favorite = True
                    badge = "Mikin suosikki"
                    meta = re.sub(r"\s*[·|]\s*Mikin suosikki", "", meta, flags=re.I).strip()
                    meta = re.sub(r"Mikin suosikki", "", meta, flags=re.I).strip(" ·|-") or None
                recipes.append(
                    {
                        "title": rtitle,
                        "meta": meta,
                        "blocks": blocks,
                        "favorite": favorite,
                        "badge": badge,
                    }
                )
        else:
            table = parse_table(body.splitlines())
            if not table:
                raw = [l for l in body.splitlines() if l.strip() and l.strip() != "---"]

        # Trailing footer note in last section? Check whole doc end
        sections.append(
            {
                "id": section_id,
                "name": name,
                "recipes": recipes,
                "table": table,
                "raw": raw,
            }
        )

    # Assign recipe ids
    for section in sections:
        for idx, recipe in enumerate(section["recipes"]):
            recipe["id"] = f"{section['id']}-{idx}"

    # Footer from trailing italic
    foot_m = re.search(r"^\*(.+)\*\s*$", text, re.M)
    # Prefer last italic line that looks like footer
    footers = re.findall(r"^\*(Kokoelma.+)\*\s*$", text, re.M)
    footer = footers[-1] if footers else None

    # Build index
    index = []
    for section in sections:
        if section["id"] == "perusarvot":
            continue
        for recipe in section["recipes"]:
            index.append(
                {
                    "kind": "recipe",
                    "id": recipe["id"],
                    "sectionId": section["id"],
                    "section": section["name"],
                    "title": recipe["title"],
                    "meta": recipe.get("meta"),
                    "macros": extract_macros(recipe.get("blocks") or []),
                    "favorite": bool(recipe.get("favorite")),
                    "badge": recipe.get("badge"),
                }
            )

    return {
        "title": title,
        "brand": brand,
        "intro": intro,
        "footer": footer,
        "sections": sections,
        "index": index,
    }


def main() -> None:
    data = parse_markdown(MD_PATH.read_text(encoding="utf-8"))
    OUT_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    n = len(data["index"])
    print(f"Wrote {OUT_PATH.name}: {len(data['sections'])} sections, {n} index rows")
    for s in data["sections"]:
        print(f"  - {s['id']}: {s['name']} ({len(s['recipes'])} recipes)")


if __name__ == "__main__":
    main()
