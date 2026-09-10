#!/usr/bin/env python3
"""
HM Portfolio — source-folder normalizer and generated-image cleanup.

Purpose
-------
Keep ONE authoritative source location for each gallery image while preserving
older HM Portfolio folders safely.

Authoritative source folders after migration:
  images/selected-work/
  images/practice/engineering/
  images/practice/painting/
  images/practice/photography/
  images/practice/graphic-design/
  images/practice/animation/
  images/practice/training/
  images/knowledge/engineering/
  images/knowledge/painting/
  images/knowledge/photography/
  images/knowledge/graphic-design/
  images/knowledge/animation/
  images/knowledge/training/

Generated folders (never manage manually):
  images/thumbs/
  images/previews/

The migration is deliberately conservative:
- identical duplicates are removed from legacy locations;
- unique legacy files are moved, never overwritten;
- filename collisions with different contents are preserved with a
  '--recovered-N' suffix;
- legacy HTML category IDs are changed to canonical names;
- gallery-data paths are rewritten before update_portfolio.py runs so titles
  can be preserved;
- cleanup mode removes only unreferenced generated gallery thumbs/previews.

Usage:
  python sync_portfolio_folders.py --migrate
  python sync_portfolio_folders.py --cleanup
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path
from typing import Dict, Iterable, Optional, Set

ROOT = Path(__file__).resolve().parent
IMAGES = ROOT / "images"
DATA_FILE = ROOT / "js" / "gallery-data.js"
INDEX_FILE = ROOT / "index.html"

CATEGORIES = (
    "engineering",
    "painting",
    "photography",
    "graphic-design",
    "animation",
    "training",
)

ALIASES = {
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


class Stats:
    moved = 0
    duplicates = 0
    collisions = 0
    derivatives_removed = 0
    html_changes = 0
    data_changes = 0
    warnings = 0


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def is_image(path: Path) -> bool:
    return path.is_file() and path.suffix.casefold() in IMAGE_EXTS


def canonical_category(value: str) -> Optional[str]:
    key = value.strip().casefold().replace("\\", "/").strip("/")
    if key in CATEGORIES:
        return key
    key2 = key.replace(" ", "-")
    return ALIASES.get(key) or ALIASES.get(key2)


def infer_category(text: str, fallback: str = "engineering") -> str:
    s = text.casefold().replace("\\", "/")
    tokens = [t for t in re.split(r"[/_.\-\s]+", s) if t]
    for token in tokens:
        cat = canonical_category(token)
        if cat:
            return cat

    groups = (
        ("photography", ("photo", "camera", "hdr", "lighting", "lightroom", "portrait")),
        ("painting", ("paint", "painting", "canvas", "sketch", "drawing", "watercolor")),
        ("animation", ("animation", "motion", "animate", "video", "toon", "character")),
        ("training", ("training", "teaching", "trainer", "course", "workshop", "class")),
        ("graphic-design", ("graphic", "poster", "logo", "typography", "illustrator", "indesign", "branding")),
        ("engineering", ("engineer", "architecture", "architect", "civil", "building", "construction")),
    )
    for cat, words in groups:
        if any(word in s for word in words):
            return cat
    return fallback


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def same_file(a: Path, b: Path) -> bool:
    try:
        if a.stat().st_size != b.stat().st_size:
            return False
        return sha256(a) == sha256(b)
    except OSError:
        return False


def unique_destination(dst: Path) -> Path:
    if not dst.exists():
        return dst
    counter = 2
    while True:
        candidate = dst.with_name(f"{dst.stem}--recovered-{counter}{dst.suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def old_derivative_paths(source: Path) -> Iterable[Path]:
    """Generated paths that mirrored an old non-original source location."""
    try:
        inside_images = source.resolve().relative_to(IMAGES.resolve())
    except ValueError:
        return []

    if not inside_images.parts or inside_images.parts[0] == "originals":
        return []

    rel_webp = inside_images.with_suffix(".webp")
    return (
        IMAGES / "thumbs" / rel_webp,
        IMAGES / "previews" / rel_webp,
    )


def remove_old_derivatives(source: Path) -> None:
    for derivative in old_derivative_paths(source):
        try:
            if derivative.exists() and derivative.is_file():
                derivative.unlink()
                Stats.derivatives_removed += 1
                print(f"  removed old generated file: {rel(derivative)}")
        except OSError as exc:
            Stats.warnings += 1
            print(f"WARNING: Could not remove {derivative}: {exc}")


def move_one(source: Path, destination: Path, path_map: Dict[str, str]) -> None:
    if not source.exists() or not source.is_file():
        return

    old_rel = rel(source)
    destination.parent.mkdir(parents=True, exist_ok=True)

    if destination.exists():
        if same_file(source, destination):
            source.unlink()
            path_map[old_rel] = rel(destination)
            Stats.duplicates += 1
            remove_old_derivatives(source)
            print(f"  duplicate removed: {old_rel}")
            return

        destination = unique_destination(destination)
        Stats.collisions += 1
        print(f"  filename collision preserved as: {rel(destination)}")

    remove_old_derivatives(source)
    shutil.move(str(source), str(destination))
    path_map[old_rel] = rel(destination)
    Stats.moved += 1
    print(f"  moved: {old_rel} -> {rel(destination)}")


def move_tree(source_dir: Path, destination_dir: Path, path_map: Dict[str, str]) -> None:
    if not source_dir.exists() or not source_dir.is_dir():
        return

    files = [p for p in source_dir.rglob("*") if p.is_file()]
    for source in sorted(files, key=lambda p: p.as_posix().casefold()):
        relative = source.relative_to(source_dir)
        move_one(source, destination_dir / relative, path_map)


def remove_empty_dirs(root: Path) -> None:
    if not root.exists() or not root.is_dir():
        return
    for folder in sorted(
        (p for p in root.rglob("*") if p.is_dir()),
        key=lambda p: len(p.parts),
        reverse=True,
    ):
        try:
            folder.rmdir()
        except OSError:
            pass
    try:
        root.rmdir()
    except OSError:
        pass


def load_gallery_data() -> dict:
    if not DATA_FILE.exists():
        return {}
    try:
        text = DATA_FILE.read_text(encoding="utf-8-sig")
        match = re.search(r"window\.HM_GALLERY_DATA\s*=\s*(\{.*\})\s*;\s*$", text, flags=re.S)
        if not match:
            return {}
        value = json.loads(match.group(1))
        return value if isinstance(value, dict) else {}
    except Exception as exc:
        Stats.warnings += 1
        print(f"WARNING: Could not read js/gallery-data.js: {exc}")
        return {}


def knowledge_category_maps(data: dict):
    exact: Dict[str, str] = {}
    by_name: Dict[str, Set[str]] = {}
    knowledge = data.get("knowledge", {})
    if not isinstance(knowledge, dict):
        return exact, by_name

    for raw_cat, items in knowledge.items():
        cat = canonical_category(str(raw_cat))
        if not cat or not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            original = item.get("original")
            if not isinstance(original, str):
                continue
            exact[original.replace("\\", "/")] = cat
            name = Path(original.replace("\\", "/")).name.casefold()
            by_name.setdefault(name, set()).add(cat)
    return exact, by_name


def category_for_knowledge(source: Path, data: dict) -> str:
    exact, by_name = knowledge_category_maps(data)
    source_rel = rel(source)

    candidates = [source_rel]
    marker = "images/originals/knowledge/"
    if source_rel.startswith(marker):
        candidates.append("images/knowledge/" + source_rel[len(marker):])

    for candidate in candidates:
        if candidate in exact:
            return exact[candidate]

    cats = by_name.get(source.name.casefold(), set())
    if len(cats) == 1:
        return next(iter(cats))

    return infer_category(source_rel)


def rewrite_gallery_data_paths(data: dict, path_map: Dict[str, str]) -> None:
    if not data or not path_map:
        return

    changed = 0

    def visit(value):
        nonlocal changed
        if isinstance(value, dict):
            original = value.get("original")
            if isinstance(original, str):
                normalized = original.replace("\\", "/")
                if normalized in path_map:
                    new_original = path_map[normalized]
                    value["original"] = new_original
                    new_source = ROOT.joinpath(*Path(new_original).parts)
                    if new_source.suffix.casefold() in {".gif", ".svg", ".webp"}:
                        value["thumb"] = new_original
                        value["preview"] = new_original
                    else:
                        inside_images = new_source.resolve().relative_to(IMAGES.resolve())
                        webp_rel = inside_images.with_suffix(".webp")
                        value["thumb"] = (Path("images") / "thumbs" / webp_rel).as_posix()
                        value["preview"] = (Path("images") / "previews" / webp_rel).as_posix()
                    changed += 1
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(data)
    if not changed:
        return

    payload = json.dumps(data, ensure_ascii=False, indent=2)
    DATA_FILE.write_text(
        "/* AUTO-GENERATED by UPDATE_PORTFOLIO.bat — do not edit manually. */\n"
        "window.HM_GALLERY_DATA = " + payload + ";\n",
        encoding="utf-8",
        newline="\n",
    )
    Stats.data_changes = changed
    print(f"Updated {changed} existing gallery-data path(s) before regeneration.")


def normalize_index_ids() -> None:
    if not INDEX_FILE.exists():
        return
    text = INDEX_FILE.read_text(encoding="utf-8-sig")
    replacements = {
        'data-gallery-category="architecture"': 'data-gallery-category="engineering"',
        'data-gallery-category="graphic"': 'data-gallery-category="graphic-design"',
        'data-gallery-category="education"': 'data-gallery-category="training"',
        'data-knowledge-filter="graphic"': 'data-knowledge-filter="graphic-design"',
    }
    changed = 0
    for old, new in replacements.items():
        count = text.count(old)
        if count:
            text = text.replace(old, new)
            changed += count
    if changed:
        INDEX_FILE.write_text(text, encoding="utf-8", newline="\n")
        Stats.html_changes = changed
        print(f"Updated {changed} legacy category ID(s) in index.html.")


def ensure_canonical_dirs() -> None:
    (IMAGES / "selected-work").mkdir(parents=True, exist_ok=True)
    for cat in CATEGORIES:
        (IMAGES / "practice" / cat).mkdir(parents=True, exist_ok=True)
        (IMAGES / "knowledge" / cat).mkdir(parents=True, exist_ok=True)


def migrate_current_legacy_practice(path_map: Dict[str, str]) -> None:
    mappings = {
        "architecture": "engineering",
        "graphic": "graphic-design",
    }
    for old, new in mappings.items():
        move_tree(IMAGES / "practice" / old, IMAGES / "practice" / new, path_map)

    move_tree(IMAGES / "education", IMAGES / "practice" / "training", path_map)


def migrate_flat_and_alias_knowledge(data: dict, path_map: Dict[str, str]) -> None:
    root = IMAGES / "knowledge"
    if not root.exists():
        return

    # First normalize category directory names such as graphic -> graphic-design.
    for child in list(root.iterdir()):
        if not child.is_dir():
            continue
        cat = canonical_category(child.name)
        if cat and child.name != cat:
            move_tree(child, root / cat, path_map)

    # Then move flat Knowledge images into their category directory.
    for source in sorted((p for p in root.iterdir() if is_image(p)), key=lambda p: p.name.casefold()):
        cat = category_for_knowledge(source, data)
        move_one(source, root / cat / source.name, path_map)


def migrate_originals(data: dict, path_map: Dict[str, str]) -> None:
    originals = IMAGES / "originals"
    if not originals.exists():
        return

    # Special/non-gallery assets: originals/about becomes images/about.
    move_tree(originals / "about", IMAGES / "about", path_map)
    move_tree(originals / "branding", IMAGES / "branding", path_map)
    move_tree(originals / "selected-work", IMAGES / "selected-work", path_map)

    # Old education is now Practice / Training.
    move_tree(originals / "education", IMAGES / "practice" / "training", path_map)

    # Old Practice categories, including legacy names.
    old_practice = originals / "practice"
    if old_practice.exists():
        for child in list(old_practice.iterdir()):
            if child.is_dir():
                cat = canonical_category(child.name)
                if cat:
                    move_tree(child, IMAGES / "practice" / cat, path_map)
                else:
                    Stats.warnings += 1
                    print(f"WARNING: Unrecognized originals/practice folder left untouched: {rel(child)}")
            elif is_image(child):
                cat = infer_category(child.name)
                move_one(child, IMAGES / "practice" / cat / child.name, path_map)

    # Old Knowledge may be flat or already categorized.
    old_knowledge = originals / "knowledge"
    if old_knowledge.exists():
        for source in sorted((p for p in old_knowledge.rglob("*") if is_image(p)), key=lambda p: p.as_posix().casefold()):
            relative = source.relative_to(old_knowledge)
            first = canonical_category(relative.parts[0]) if len(relative.parts) > 1 else None
            if first:
                rest = Path(*relative.parts[1:])
                destination = IMAGES / "knowledge" / first / rest
            else:
                cat = category_for_knowledge(source, data)
                destination = IMAGES / "knowledge" / cat / relative
            move_one(source, destination, path_map)

    # Root-level old originals (hero/signature etc.) belong directly in images/.
    for source in sorted((p for p in originals.iterdir() if p.is_file()), key=lambda p: p.name.casefold()):
        move_one(source, IMAGES / source.name, path_map)

    remove_empty_dirs(originals)


def migrate() -> int:
    print()
    print("=" * 66)
    print(" HM PORTFOLIO — NORMALIZE IMAGE SOURCE FOLDERS")
    print("=" * 66)
    print()

    if not IMAGES.exists():
        print("ERROR: images/ folder not found.")
        return 1

    ensure_canonical_dirs()
    data = load_gallery_data()
    path_map: Dict[str, str] = {}

    migrate_current_legacy_practice(path_map)
    migrate_flat_and_alias_knowledge(data, path_map)
    migrate_originals(data, path_map)

    # Some empty legacy roots can remain after duplicates were removed.
    for folder in (
        IMAGES / "education",
        IMAGES / "practice" / "architecture",
        IMAGES / "practice" / "graphic",
        IMAGES / "originals",
    ):
        remove_empty_dirs(folder)

    rewrite_gallery_data_paths(data, path_map)
    normalize_index_ids()

    print()
    print("Source-folder normalization complete.")
    print(f"  moved unique files       : {Stats.moved}")
    print(f"  removed duplicate files  : {Stats.duplicates}")
    print(f"  preserved collisions     : {Stats.collisions}")
    print(f"  old generated files gone : {Stats.derivatives_removed}")
    print(f"  warnings                 : {Stats.warnings}")
    print()
    print("AUTHORITATIVE SOURCE LOCATIONS:")
    print("  images/selected-work/")
    print("  images/practice/<category>/")
    print("  images/knowledge/<category>/")
    print()
    print("Do NOT manually manage images/thumbs/ or images/previews/.")
    print()
    return 0


def referenced_generated_paths(data: dict) -> Set[str]:
    allowed: Set[str] = set()

    def visit(value):
        if isinstance(value, dict):
            for key in ("thumb", "preview"):
                path = value.get(key)
                if isinstance(path, str):
                    normalized = path.replace("\\", "/")
                    if normalized.startswith("images/thumbs/") or normalized.startswith("images/previews/"):
                        allowed.add(normalized)
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(data)
    return allowed


def cleanup_generated() -> int:
    print()
    print("Cleaning unused generated gallery images...")
    data = load_gallery_data()
    if not data:
        print("WARNING: gallery-data.js could not be read; generated cleanup skipped.")
        return 0

    allowed = referenced_generated_paths(data)
    removed = 0

    # Only gallery-generated areas are cleaned. About/timeline derivatives are protected.
    scopes = (
        IMAGES / "thumbs" / "selected-work",
        IMAGES / "thumbs" / "practice",
        IMAGES / "thumbs" / "knowledge",
        IMAGES / "thumbs" / "education",
        IMAGES / "previews" / "selected-work",
        IMAGES / "previews" / "practice",
        IMAGES / "previews" / "knowledge",
        IMAGES / "previews" / "education",
    )

    for scope in scopes:
        if not scope.exists():
            continue
        for file in [p for p in scope.rglob("*") if p.is_file()]:
            if rel(file) not in allowed:
                try:
                    file.unlink()
                    removed += 1
                    print(f"  removed unused: {rel(file)}")
                except OSError as exc:
                    print(f"WARNING: Could not remove {rel(file)}: {exc}")
        remove_empty_dirs(scope)

    print(f"Generated cleanup complete: {removed} unused file(s) removed.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--migrate", action="store_true")
    group.add_argument("--cleanup", action="store_true")
    args = parser.parse_args()

    if args.migrate:
        return migrate()
    return cleanup_generated()


if __name__ == "__main__":
    raise SystemExit(main())
