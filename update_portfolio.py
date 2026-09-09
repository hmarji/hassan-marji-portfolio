#!/usr/bin/env python3
"""
HM Portfolio — folder-driven gallery updater.

Put this file in the website root beside index.html, then run UPDATE_PORTFOLIO.bat.

What it does:
- Scans Selected Work, Practice, and Knowledge image folders.
- Preserves legacy Practice folders used by older versions of the site.
- Migrates the old hard-coded Selected Work into images/selected-work/ on first run.
- Preserves categories for old flat Knowledge images when possible.
- Creates lightweight WebP thumbnails and previews when Pillow is available.
- Regenerates js/gallery-data.js for gallery-manager.js.
"""

from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent
IMAGES = ROOT / "images"
JS_DIR = ROOT / "js"
DATA_FILE = JS_DIR / "gallery-data.js"
INDEX_FILE = ROOT / "index.html"

CATEGORIES = (
    "engineering",
    "painting",
    "photography",
    "graphic-design",
    "animation",
    "training",
)

# New preferred folders + legacy folders already used by HM Portfolio.
PRACTICE_SOURCES = {
    "engineering": (
        "images/practice/engineering",
        "images/practice/architecture",
    ),
    "painting": (
        "images/practice/painting",
    ),
    "photography": (
        "images/practice/photography",
    ),
    "graphic-design": (
        "images/practice/graphic-design",
        "images/practice/graphic",
    ),
    "animation": (
        "images/practice/animation",
    ),
    "training": (
        "images/practice/training",
        "images/education",
    ),
}

CATEGORY_ALIASES = {
    "engineering": "engineering",
    "architecture": "engineering",
    "architect": "engineering",
    "civil": "engineering",
    "painting": "painting",
    "paint": "painting",
    "art": "painting",
    "drawing": "painting",
    "photography": "photography",
    "photo": "photography",
    "camera": "photography",
    "graphic-design": "graphic-design",
    "graphic_design": "graphic-design",
    "graphic": "graphic-design",
    "design": "graphic-design",
    "animation": "animation",
    "motion": "animation",
    "video": "animation",
    "training": "training",
    "education": "training",
    "teaching": "training",
    "course": "training",
    "courses": "training",
    "workshop": "training",
    "workshops": "training",
}

IMAGE_EXTS = {
    ".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg",
    ".bmp", ".tif", ".tiff", ".avif",
}
KEEP_ORIGINAL_EXTS = {".gif", ".svg", ".webp"}

THUMB_MAX = 560
PREVIEW_MAX = 1800
THUMB_QUALITY = 78
PREVIEW_QUALITY = 84

try:
    from PIL import Image, ImageOps
    PILLOW_AVAILABLE = True
except Exception:
    Image = None
    ImageOps = None
    PILLOW_AVAILABLE = False


def posix(path: Path) -> str:
    """Path relative to the website root, always with forward slashes."""
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def natural_key(value: str):
    return [
        int(part) if part.isdigit() else part.casefold()
        for part in re.split(r"(\d+)", value)
    ]


def is_image(path: Path) -> bool:
    return path.is_file() and path.suffix.casefold() in IMAGE_EXTS


def image_files(folder: Path, recursive: bool = False) -> List[Path]:
    if not folder.exists():
        return []
    iterator = folder.rglob("*") if recursive else folder.iterdir()
    return sorted(
        (p for p in iterator if is_image(p)),
        key=lambda p: natural_key(p.relative_to(folder).as_posix()),
    )


def title_from_filename(path: Path) -> str:
    stem = path.stem
    # Numeric prefixes control order but should not normally appear in captions.
    stem = re.sub(r"^\s*\d+\s*[-_. ]*", "", stem)
    stem = stem.replace("_", " ").replace("-", " ")
    stem = re.sub(r"\s+", " ", stem).strip()
    return stem or path.stem


def load_existing_data() -> dict:
    if not DATA_FILE.exists():
        return {}
    try:
        text = DATA_FILE.read_text(encoding="utf-8-sig")
        match = re.search(
            r"window\.HM_GALLERY_DATA\s*=\s*(\{.*\})\s*;\s*$",
            text,
            flags=re.S,
        )
        if not match:
            return {}
        data = json.loads(match.group(1))
        return data if isinstance(data, dict) else {}
    except Exception as exc:
        print(f"WARNING: Could not read existing js/gallery-data.js: {exc}")
        return {}


def existing_item_maps(data: dict):
    """
    Return:
      item_by_original: original path -> old item
      knowledge_category_by_original: original path -> old category
    """
    item_by_original: Dict[str, dict] = {}
    knowledge_category: Dict[str, str] = {}

    def remember(items, category: Optional[str] = None):
        if not isinstance(items, list):
            return
        for item in items:
            if not isinstance(item, dict):
                continue
            original = item.get("original")
            if not isinstance(original, str):
                continue
            item_by_original[original] = item
            if category:
                knowledge_category[original] = category

    remember(data.get("selectedWork", []))

    practice = data.get("practice", {})
    if isinstance(practice, dict):
        for items in practice.values():
            remember(items)

    knowledge = data.get("knowledge", {})
    if isinstance(knowledge, dict):
        for cat, items in knowledge.items():
            canonical = canonical_category(cat)
            remember(items, canonical)

    return item_by_original, knowledge_category


def canonical_category(value: str) -> Optional[str]:
    key = value.strip().casefold().replace("\\", "/")
    key = key.strip("/")
    if key in CATEGORIES:
        return key
    key2 = key.replace(" ", "-")
    if key2 in CATEGORIES:
        return key2
    return CATEGORY_ALIASES.get(key) or CATEGORY_ALIASES.get(key2)


def infer_category(text: str, fallback: str = "engineering") -> str:
    s = text.casefold().replace("\\", "/")
    tokens = [t for t in re.split(r"[/_.\-\s]+", s) if t]

    # Prefer folder/category words before looser filename hints.
    for token in tokens:
        c = canonical_category(token)
        if c:
            return c

    keyword_groups = (
        ("photography", ("photo", "camera", "hdr", "lighting", "lightroom", "portrait")),
        ("painting", ("paint", "painting", "canvas", "sketch", "drawing", "watercolor")),
        ("animation", ("animation", "motion", "animate", "video", "toon", "character")),
        ("training", ("training", "teaching", "trainer", "course", "workshop", "class", "adobe session")),
        ("graphic-design", ("graphic", "poster", "logo", "typography", "illustrator", "indesign", "branding")),
        ("engineering", ("engineer", "architecture", "architect", "civil", "building", "construction")),
    )
    for cat, words in keyword_groups:
        if any(word in s for word in words):
            return cat
    return fallback


def derive_target(source: Path, kind: str) -> Path:
    """
    Mirror the path below images/:
      images/practice/painting/x.jpg
      -> images/thumbs/practice/painting/x.webp
    """
    rel = source.resolve().relative_to(IMAGES.resolve())
    return IMAGES / kind / rel.with_suffix(".webp")


def derivative_is_fresh(source: Path, target: Path) -> bool:
    try:
        return (
            target.exists()
            and target.stat().st_size > 0
            and target.stat().st_mtime >= source.stat().st_mtime
        )
    except OSError:
        return False


def create_webp(source: Path, target: Path, max_side: int, quality: int) -> bool:
    if not PILLOW_AVAILABLE:
        return False
    if derivative_is_fresh(source, target):
        return True

    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        with Image.open(source) as im:
            im = ImageOps.exif_transpose(im)

            # Use RGB/RGBA for reliable WebP output while preserving alpha.
            if "A" in im.getbands():
                if im.mode != "RGBA":
                    im = im.convert("RGBA")
            elif im.mode != "RGB":
                im = im.convert("RGB")

            resampling = getattr(Image, "Resampling", Image).LANCZOS
            im.thumbnail((max_side, max_side), resampling)

            im.save(
                target,
                "WEBP",
                quality=quality,
                method=6,
            )
        return True
    except Exception as exc:
        print(f"WARNING: Could not optimize {posix(source)}: {exc}")
        try:
            if target.exists():
                target.unlink()
        except OSError:
            pass
        return False


def make_item(source: Path, old_items: Dict[str, dict]) -> dict:
    original = posix(source)
    old = old_items.get(original, {})
    title = old.get("title") if isinstance(old, dict) else None
    if not isinstance(title, str) or not title.strip():
        title = title_from_filename(source)

    # README contract: GIF/SVG/WebP stay in their original format.
    if source.suffix.casefold() in KEEP_ORIGINAL_EXTS or not PILLOW_AVAILABLE:
        thumb = original
        preview = original
    else:
        thumb_path = derive_target(source, "thumbs")
        preview_path = derive_target(source, "previews")
        thumb_ok = create_webp(source, thumb_path, THUMB_MAX, THUMB_QUALITY)
        preview_ok = create_webp(source, preview_path, PREVIEW_MAX, PREVIEW_QUALITY)
        thumb = posix(thumb_path) if thumb_ok else original
        preview = posix(preview_path) if preview_ok else original

    return {
        "original": original,
        "thumb": thumb,
        "preview": preview,
        "title": title.strip(),
    }


def scan_practice(old_items: Dict[str, dict]) -> dict:
    result = {cat: [] for cat in CATEGORIES}
    for cat in CATEGORIES:
        seen = set()
        for rel_folder in PRACTICE_SOURCES[cat]:
            folder = ROOT / rel_folder
            for source in image_files(folder):
                original = posix(source)
                if original in seen:
                    continue
                seen.add(original)
                result[cat].append(make_item(source, old_items))
    return result


def selected_sources_from_index() -> List[Path]:
    """Fallback for first migration if gallery-data.js is missing."""
    if not INDEX_FILE.exists():
        return []
    try:
        text = INDEX_FILE.read_text(encoding="utf-8-sig", errors="ignore")
    except OSError:
        return []

    # Restrict parsing to the Selected Work section when possible.
    section_match = re.search(
        r'<section[^>]+class=["\'][^"\']*selected-work[^"\']*["\'][\s\S]*?</section>',
        text,
        flags=re.I,
    )
    section = section_match.group(0) if section_match else text

    values = re.findall(
        r'data-selected-src\s*=\s*["\']([^"\']+)["\']',
        section,
        flags=re.I,
    )
    sources = []
    for value in values:
        value = value.split("?", 1)[0].split("#", 1)[0]
        candidate = ROOT / Path(value.replace("/", str(Path("/"))))
        # The expression above is platform-safe after normalization below.
        candidate = ROOT.joinpath(*Path(value.replace("\\", "/")).parts)
        if candidate.exists() and is_image(candidate):
            sources.append(candidate)
    return sources


def migrate_selected_work(existing_data: dict) -> None:
    folder = IMAGES / "selected-work"
    folder.mkdir(parents=True, exist_ok=True)

    # Never duplicate/overwrite an already-established Selected Work gallery.
    if image_files(folder):
        return

    candidates: List[Path] = []
    old_selected = existing_data.get("selectedWork", [])
    if isinstance(old_selected, list):
        for item in old_selected:
            if not isinstance(item, dict):
                continue
            original = item.get("original")
            if not isinstance(original, str):
                continue
            source = ROOT.joinpath(*Path(original.replace("\\", "/")).parts)
            if source.exists() and is_image(source):
                candidates.append(source)

    if not candidates:
        candidates = selected_sources_from_index()

    # De-duplicate while preserving order.
    unique: List[Path] = []
    seen = set()
    for source in candidates:
        key = str(source.resolve()).casefold()
        if key not in seen:
            seen.add(key)
            unique.append(source)

    if not unique:
        return

    print("First-run Selected Work migration:")
    width = max(2, len(str(len(unique))))
    for index, source in enumerate(unique, 1):
        destination = folder / f"{index:0{width}d}_{source.name}"
        if destination.exists():
            continue
        shutil.copy2(source, destination)
        print(f"  copied {posix(source)} -> {posix(destination)}")


def scan_selected_work(old_items: Dict[str, dict]) -> List[dict]:
    return [
        make_item(source, old_items)
        for source in image_files(IMAGES / "selected-work")
    ]


def knowledge_existing_categories(existing_data: dict) -> Dict[str, str]:
    result: Dict[str, str] = {}
    knowledge = existing_data.get("knowledge", {})
    if not isinstance(knowledge, dict):
        return result
    for raw_cat, items in knowledge.items():
        cat = canonical_category(raw_cat)
        if not cat or not isinstance(items, list):
            continue
        for item in items:
            if isinstance(item, dict) and isinstance(item.get("original"), str):
                result[item["original"]] = cat
    return result


def knowledge_category_for(
    source: Path,
    old_category: Dict[str, str],
) -> str:
    original = posix(source)
    if original in old_category:
        return old_category[original]

    knowledge_root = IMAGES / "knowledge"
    rel = source.relative_to(knowledge_root)

    # New preferred structure: images/knowledge/<category>/...
    if len(rel.parts) > 1:
        first = canonical_category(rel.parts[0])
        if first:
            return first

    # Legacy flat images are retained and categorized heuristically.
    return infer_category(rel.as_posix(), fallback="engineering")


def scan_knowledge(
    old_items: Dict[str, dict],
    existing_data: dict,
) -> dict:
    result = {cat: [] for cat in CATEGORIES}
    knowledge_root = IMAGES / "knowledge"
    if not knowledge_root.exists():
        return result

    old_category = knowledge_existing_categories(existing_data)

    for source in image_files(knowledge_root, recursive=True):
        cat = knowledge_category_for(source, old_category)
        result[cat].append(make_item(source, old_items))

    for cat in CATEGORIES:
        result[cat].sort(key=lambda item: natural_key(item["original"]))

    return result


def ensure_new_folders() -> None:
    (IMAGES / "selected-work").mkdir(parents=True, exist_ok=True)
    for cat in CATEGORIES:
        (IMAGES / "practice" / cat).mkdir(parents=True, exist_ok=True)
        (IMAGES / "knowledge" / cat).mkdir(parents=True, exist_ok=True)


def write_data(data: dict) -> None:
    JS_DIR.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, ensure_ascii=False, indent=2)
    content = (
        "/* AUTO-GENERATED by UPDATE_PORTFOLIO.bat — do not edit manually. */\n"
        "window.HM_GALLERY_DATA = "
        + payload
        + ";\n"
    )
    DATA_FILE.write_text(content, encoding="utf-8", newline="\n")


def counts(data: dict) -> Tuple[int, int, int]:
    selected = len(data.get("selectedWork", []))
    practice = sum(len(v) for v in data.get("practice", {}).values())
    knowledge = sum(len(v) for v in data.get("knowledge", {}).values())
    return selected, practice, knowledge


def validate_root() -> None:
    if not INDEX_FILE.exists():
        raise RuntimeError(
            "index.html was not found. Put update_portfolio.py and "
            "UPDATE_PORTFOLIO.bat in the main HM Portfolio folder."
        )
    if not IMAGES.exists():
        raise RuntimeError("The images folder was not found.")


def main() -> int:
    print()
    print("=" * 62)
    print(" HM PORTFOLIO — UPDATE GALLERIES")
    print("=" * 62)
    print(f"Website: {ROOT}")
    print()

    validate_root()
    ensure_new_folders()

    existing_data = load_existing_data()
    old_items, _ = existing_item_maps(existing_data)

    migrate_selected_work(existing_data)

    data = {
        "version": 1,
        "selectedWork": scan_selected_work(old_items),
        "practice": scan_practice(old_items),
        "knowledge": scan_knowledge(old_items, existing_data),
    }

    write_data(data)

    selected_count, practice_count, knowledge_count = counts(data)
    print()
    print("Updated js/gallery-data.js")
    print(f"  Selected Work : {selected_count}")
    print(f"  Practice      : {practice_count}")
    print(f"  Knowledge     : {knowledge_count}")
    print(f"  Total         : {selected_count + practice_count + knowledge_count}")
    print()

    if PILLOW_AVAILABLE:
        print(
            f"Optimized image mode: ON "
            f"(thumbs <= {THUMB_MAX}px, previews <= {PREVIEW_MAX}px)"
        )
    else:
        print("Optimized image mode: OFF")
        print("Pillow is not installed, so original files were used for display.")
        print("Install Pillow and run the updater again to create WebP derivatives.")

    print()
    print("Next: open index.html and check the site locally.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nCancelled.")
        raise SystemExit(130)
    except Exception as exc:
        print()
        print("ERROR:", exc)
        raise SystemExit(1)
