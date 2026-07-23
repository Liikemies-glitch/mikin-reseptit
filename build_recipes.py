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
IMAGES_DIR = ROOT / "images"
MANIFEST_PATH = IMAGES_DIR / "manifest.json"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

SECTION_IDS = {
    "Pääruoat": "paaruuat",
    "Aamupalat": "aamupalat",
    "Jälkiruoat": "jalkiruoat",
    "Kastikkeet ja soosit": "kastikkeet",
}

# Short / casual filenames → recipe title slug
FILENAME_ALIASES = {
    "pizza": "rahkapohja-pizza",
    "pizza2": "rahkapohja-pizza",
    "piz": "rahkapohja-pizza",
    "joku-piz": "rahkapohja-pizza",
    "joku-pizza": "rahkapohja-pizza",
    "rahkapohja": "rahkapohja-pizza",
    "kebab": "rullakebab",
    "kebabbia": "rullakebab",
    "rullakebab": "rullakebab",
    "moussaka": "kreikkalainen-moussaka",
    "munakoiso": "kreikkalainen-moussaka",
    "curry": "keltainen-curry",
    "tortilla": "kanatortillat",
    "kanatortilla": "kanatortillat",
    "kanatortillat": "kanatortillat",
    "taytteet": "kanatortillat",
    "jauhelihapata": "mausteinen-jauhelihapata",
    "keema": "intialainen-jauhelihakeema",
    "jauhelihakeema": "intialainen-jauhelihakeema",
    "makaroni": "gluteeniton-makaroonilaatikko-munaton",
    "makaroonilaatikko": "gluteeniton-makaroonilaatikko-munaton",
    "porkkana": "proteiini-porkkanakakku",
    "porkkanakakku": "proteiini-porkkanakakku",
    "appelsiinikana": "appelsiinikana",
    "mikin-maukas-matto": "intialainen-jauhelihakeema",
    "mikin-maukas-matto-2": "intialainen-jauhelihakeema",
    "mustikka": "brownie",
    "mustikkabrownie": "brownie",
}

# Filename hints that should sort after the main plated shot
IMAGE_SECONDARY_HINTS = (
    "ladonta",
    "taytteet",
    "tayte",
    "ilman",
    "frosting",
    "prep",
    "vaihe",
)

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
    "Kuvat",
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


def web_path(path: Path) -> str:
    """Repo-relative POSIX path for the static site."""
    rel = path.resolve().relative_to(ROOT)
    return rel.as_posix()


def parse_image_refs(text: str) -> list[str]:
    """Split a Kuvat line / list into image path stems or filenames."""
    parts = re.split(r"[,;\n]+", text)
    out = []
    for part in parts:
        name = part.strip().strip("`").strip()
        if not name:
            continue
        out.append(name)
    return out


def resolve_image_ref(ref: str) -> str | None:
    """Turn a markdown image ref into a site-relative path if the file exists."""
    candidates = []
    raw = Path(ref)
    if raw.is_absolute():
        return None
    if ref.startswith("images/"):
        candidates.append(ROOT / ref)
    else:
        candidates.append(IMAGES_DIR / ref)
        candidates.append(ROOT / ref)
    for cand in candidates:
        if cand.is_file() and cand.suffix.lower() in IMAGE_EXTS:
            return web_path(cand)
    return None


def extract_explicit_images(blocks: list[dict]) -> tuple[list[dict], list[str]]:
    """Pull **Kuvat:** block out of recipe body → image paths."""
    remaining: list[dict] = []
    images: list[str] = []
    for block in blocks:
        if (block.get("label") or "").strip().lower() != "kuvat":
            remaining.append(block)
            continue
        refs: list[str] = []
        if block.get("content"):
            refs.extend(parse_image_refs(block["content"]))
        for item in block.get("items") or []:
            refs.extend(parse_image_refs(item))
        for ref in refs:
            resolved = resolve_image_ref(ref)
            if resolved and resolved not in images:
                images.append(resolved)
    return remaining, images


def load_manifest() -> dict[str, list[str]]:
    if not MANIFEST_PATH.is_file():
        return {}
    try:
        data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    if not isinstance(data, dict):
        return {}
    out: dict[str, list[str]] = {}
    for key, value in data.items():
        slug = slugify(str(key))
        refs = value if isinstance(value, list) else [value]
        paths = []
        for ref in refs:
            resolved = resolve_image_ref(str(ref))
            if resolved and resolved not in paths:
                paths.append(resolved)
        if paths:
            out[slug] = paths
    return out


def stem_match_keys(stem: str) -> list[str]:
    """Possible recipe slugs a filename stem could belong to."""
    base = slugify(stem)
    trimmed = re.sub(r"[-_]?\d+$", "", base).strip("-")
    keys: list[str] = []

    def push(k: str):
        if k and k not in keys:
            keys.append(k)

    push(trimmed)
    push(base)
    if trimmed in FILENAME_ALIASES:
        push(FILENAME_ALIASES[trimmed])
    if base in FILENAME_ALIASES:
        push(FILENAME_ALIASES[base])

    parts = [p for p in trimmed.split("-") if p]
    for part in parts:
        push(part)
        if part in FILENAME_ALIASES:
            push(FILENAME_ALIASES[part])
        # soft contains (kebabbia → kebab)
        for alias, target in FILENAME_ALIASES.items():
            if len(alias) >= 4 and alias in part:
                push(alias)
                push(target)

    for i in range(len(parts)):
        piece = "-".join(parts[i:])
        push(piece)
        if piece in FILENAME_ALIASES:
            push(FILENAME_ALIASES[piece])
    return keys


def resolve_stem_to_slug(stem: str, known_slugs: set[str]) -> str | None:
    candidates = stem_match_keys(stem)
    for key in candidates:
        if key in known_slugs:
            return key
    for key in candidates:
        target = FILENAME_ALIASES.get(key)
        if target and target in known_slugs:
            return target
    # token overlap with known recipe slugs (porkkanakakku → proteiini-porkkanakakku)
    tokens = [t for t in slugify(stem).split("-") if len(t) >= 5]
    for slug in known_slugs:
        for token in tokens:
            if token in slug or slug in token:
                return slug
    return candidates[0] if candidates else None


def image_rank(path: str) -> tuple[int, str]:
    """Prefer plated/finished shots before prep / component photos."""
    name = slugify(Path(path).stem)
    secondary = any(hint in name for hint in IMAGE_SECONDARY_HINTS)
    plated = any(h in name for h in ("ateria", "whole-meal", "wholemeal", "lautanen"))
    if secondary:
        return (2, path)
    if plated:
        return (1, path)
    return (0, path)


def discover_images_by_slug(known_slugs: set[str] | None = None) -> dict[str, list[str]]:
    """Map recipe title slug → image paths from images/ folder layout."""
    known = known_slugs or set()
    by_slug: dict[str, list[str]] = {}
    if not IMAGES_DIR.is_dir():
        return by_slug

    def add(slug: str, path: Path):
        if path.suffix.lower() not in IMAGE_EXTS:
            return
        if path.name.startswith("."):
            return
        web = web_path(path)
        by_slug.setdefault(slug, [])
        if web not in by_slug[slug]:
            by_slug[slug].append(web)

    for path in sorted(IMAGES_DIR.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in IMAGE_EXTS:
            continue
        if path.name.lower() == "manifest.json":
            continue
        rel = path.relative_to(IMAGES_DIR)
        # images/<slug>/file.jpg
        if len(rel.parts) >= 2:
            folder_slug = resolve_stem_to_slug(rel.parts[0], known) or slugify(rel.parts[0])
            folder_slug = FILENAME_ALIASES.get(folder_slug, folder_slug)
            add(folder_slug, path)
            continue
        chosen = resolve_stem_to_slug(path.stem, known)
        if chosen:
            add(chosen, path)

    for slug, paths in by_slug.items():
        by_slug[slug] = sorted(paths, key=image_rank)
    return by_slug


def attach_recipe_images(sections: list[dict]) -> None:
    known_slugs = {slugify(r["title"]) for s in sections for r in s["recipes"]}
    discovered = discover_images_by_slug(known_slugs)
    manifest = load_manifest()

    for section in sections:
        for recipe in section["recipes"]:
            blocks, explicit = extract_explicit_images(recipe.get("blocks") or [])
            recipe["blocks"] = blocks
            title_slug = slugify(recipe["title"])
            images: list[str] = []
            for src in (explicit, manifest.get(title_slug, []), discovered.get(title_slug, [])):
                for path in src:
                    if path not in images:
                        images.append(path)
            images.sort(key=image_rank)
            recipe["images"] = images
            recipe["image"] = images[0] if images else None


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


RATING_RE = re.compile(r"(?:^|\s|[·|])\s*(\d{1,2})\s*/\s*10\b", re.I)


def extract_rating(text: str | None) -> tuple[str | None, int | None]:
    """Pull N/10 out of meta text; return cleaned meta and rating 0–10."""
    if not text:
        return None, None
    match = RATING_RE.search(text)
    if not match:
        return text.strip() or None, None
    value = int(match.group(1))
    if value < 0 or value > 10:
        value = max(0, min(10, value))
    cleaned = (text[: match.start()] + text[match.end() :]).strip(" ·|-")
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
    return cleaned or None, value


def parse_recipe_body(body: str) -> tuple[str | None, list[dict], int | None]:
    lines = body.strip().splitlines()
    meta = None
    rating = None
    blocks: list[dict] = []

    i = 0
    # Leading italic meta lines (annos · N/10)
    while i < len(lines):
        raw = lines[i].strip()
        if not raw:
            i += 1
            continue
        if raw.startswith("*") and raw.endswith("*") and not raw.startswith("**"):
            meta_text = raw.strip("*").strip()
            cleaned, found = extract_rating(meta_text)
            if found is not None:
                rating = found
            if cleaned and not meta:
                meta = cleaned
            elif not meta and cleaned is None and found is None:
                meta = meta_text
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

        bold = re.match(r"^\*\*(.+?):\*\*\s*(.*)$", stripped)
        if bold:
            lab, rest = bold.group(1).strip(), bold.group(2).strip()
            if lab.lower() == "arvosana":
                try:
                    rating = int(re.search(r"\d{1,2}", rest).group(0))
                except Exception:
                    pass
                continue
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

    return meta, blocks, rating


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

    for part in parts[1:]:
        lines = part.splitlines()
        if not lines:
            continue
        name = lines[0].strip()
        body = "\n".join(lines[1:])

        if name.lower().startswith("sisällys"):
            continue

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
                meta, blocks, rating = parse_recipe_body(rbody)
                recipes.append(
                    {
                        "title": rtitle,
                        "meta": meta,
                        "blocks": blocks,
                        "rating": rating,
                    }
                )
        else:
            table = parse_table(body.splitlines())
            if not table:
                raw = [l for l in body.splitlines() if l.strip() and l.strip() != "---"]

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

    attach_recipe_images(sections)

    footers = re.findall(
        r"^\*((?:Kaikki reseptit|Kokoelma).+)\*\s*$", text, re.M
    )
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
                    "rating": recipe.get("rating"),
                    "image": recipe.get("image"),
                    "images": recipe.get("images") or [],
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
