#!/usr/bin/env python3
"""Validate an XHS release against an explicit manifest and real visual review.

Python standard library only. Does not render, OCR, edit images, or infer review
results. A passing result checks the supplied observations, not their truth.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import struct
import sys
import zipfile


VISUAL_CHECKS = (
    "legibility", "layout", "style_consistency", "content_numbers_and_arrows"
)
EDITORIAL_CHECKS = (
    "title_body_aligned", "claims_checked", "story_order_checked", "caption_consistent"
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize(value):
    return re.sub(r"\s+", "", value) if isinstance(value, str) else None


def load_object(path):
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.name}: JSON root must be an object")
    return value


def relative_file(root, value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("file paths must be nonempty relative strings")
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"path must stay inside release directory: {value}")
    resolved = (root / path).resolve()
    if not resolved.is_relative_to(root):
        raise ValueError(f"path resolves outside release directory: {value}")
    return resolved


def expected_header(card):
    if card["order"] == 1:
        return card["section_label"]
    return f"{card['order'] - 1:02d} {card['section_label']}"


def validate(manifest_path, review_path=None, stage="release"):
    manifest_path = Path(manifest_path).resolve()
    root = manifest_path.parent
    errors, image_records, package_files = [], [], []
    report = {
        "stage": stage,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "verification_scope": "Manifest, file integrity and supplied visual observations; no automatic visual or factual verification.",
        "errors": errors,
        "images": image_records,
    }

    def fail(message):
        errors.append(message)

    try:
        manifest = load_object(manifest_path)
    except (OSError, ValueError) as exc:
        fail(str(exc))
        report["passed"] = False
        return report, package_files
    report["manifest_sha256"] = digest(manifest_path)
    if manifest.get("schema_version") != 1:
        fail("manifest schema_version must be 1")
    if not isinstance(manifest.get("title"), str) or not manifest["title"].strip():
        fail("manifest title is missing")
    cards = manifest.get("cards")
    if not isinstance(cards, list) or not cards:
        fail("cards must be a nonempty array")
        report["passed"] = False
        return report, package_files
    if type(manifest.get("total_images")) is not int or manifest["total_images"] != len(cards):
        fail("total_images does not match cards")

    canvas = manifest.get("canvas", {})
    if not isinstance(canvas, dict):
        canvas = {}
        fail("canvas must be an object")
    ratio = canvas.get("aspect_ratio", [3, 4])
    if not (isinstance(ratio, list) and len(ratio) == 2 and all(type(n) is int and n > 0 for n in ratio)):
        fail("aspect_ratio must be two positive integers")
        ratio = [3, 4]
    min_width = canvas.get("min_width", 1080)
    if type(min_width) is not int or min_width < 1:
        fail("min_width must be a positive integer")
        min_width = 1080

    ids, image_paths, prompt_paths = set(), set(), set()
    resolved_cards = []
    for position, card in enumerate(cards, 1):
        prefix = f"card {position}"
        if not isinstance(card, dict):
            fail(f"{prefix}: must be an object")
            continue
        card_id = card.get("id")
        if not isinstance(card_id, str) or not card_id.strip() or card_id in ids:
            fail(f"{prefix}: missing or duplicate id")
        else:
            ids.add(card_id)
        if type(card.get("order")) is not int or card["order"] != position:
            fail(f"{prefix}: upload order must be consecutive from 1")
        if card.get("kind") != ("cover" if position == 1 else "content"):
            fail(f"{prefix}: only first image is the cover")
        if not isinstance(card.get("section_label"), str) or not card["section_label"].strip():
            fail(f"{prefix}: section_label is missing")
        elif re.match(r"^\d{2}(?:\s|$)", card["section_label"]):
            fail(f"{prefix}: section_label must not include a manual page number")
        blocks = card.get("text_blocks")
        if not isinstance(blocks, list) or not blocks or any(not isinstance(x, str) or not x.strip() for x in blocks):
            fail(f"{prefix}: text_blocks must contain all visible nonempty text blocks")
        try:
            image_path = relative_file(root, card.get("file"))
            prompt_path = relative_file(root, card.get("prompt"))
            if image_path in image_paths or prompt_path in prompt_paths:
                fail(f"{prefix}: duplicate image or prompt path")
            image_paths.add(image_path)
            prompt_paths.add(prompt_path)
            if not image_path.name.startswith(f"{position:02d}-") or image_path.suffix.lower() != ".png":
                fail(f"{prefix}: image filename must start with {position:02d}- and end in .png")
            if prompt_path.suffix.lower() != ".md":
                fail(f"{prefix}: prompt must be a Markdown file")
            resolved_cards.append((card, image_path, prompt_path))
        except ValueError as exc:
            fail(f"{prefix}: {exc}")

    support = manifest.get("support_files", [])
    if not isinstance(support, list):
        fail("support_files must be an array")
        support = []
    ancillary = []
    for value in [manifest.get("caption_file")] + support:
        try:
            path = relative_file(root, value)
            if path.suffix.lower() not in {".md", ".txt", ".json"}:
                fail(f"support/caption file must be text or JSON: {value}")
            ancillary.append(path)
        except ValueError as exc:
            fail(str(exc))
    if errors or stage == "plan":
        report["passed"] = not errors
        report["expected_headers"] = [expected_header(c) for c in cards] if not errors else []
        return report, package_files

    try:
        if review_path is None:
            raise ValueError("release stage requires --review after visually inspecting every image")
        review_path = Path(review_path).resolve()
        if not review_path.is_relative_to(root):
            raise ValueError("review file must be inside release directory")
        review = load_object(review_path)
    except (OSError, ValueError) as exc:
        fail(str(exc))
        report["passed"] = False
        return report, package_files
    if review.get("schema_version") != 1:
        fail("review schema_version must be 1")
    if review.get("manifest_sha256") != report["manifest_sha256"]:
        fail("manifest changed after review; review the changes before updating the record")
    editorial = review.get("editorial", {})
    if not isinstance(editorial, dict):
        editorial = {}
    for check in EDITORIAL_CHECKS:
        if editorial.get(check) is not True:
            fail(f"editorial check not passed: {check}")
    if editorial.get("issues") != []:
        fail("editorial issues are missing or unresolved")
    reviewed_cards = review.get("cards")
    if not isinstance(reviewed_cards, list):
        reviewed_cards = []
        fail("review cards must be an array")
    observations = {}
    for entry in reviewed_cards:
        if not isinstance(entry, dict) or not isinstance(entry.get("id"), str):
            fail("review entry has no id")
            continue
        if entry["id"] in observations:
            fail(f"duplicate review id: {entry['id']}")
        observations[entry["id"]] = entry
    if set(observations) != ids:
        fail("review must contain exactly one record for each manifest card")

    dimensions, hashes = set(), set()
    for card, image_path, prompt_path in resolved_cards:
        prefix = card["id"]
        try:
            data = image_path.read_bytes()
            if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
                raise ValueError("image does not have a valid PNG header")
            width, height = struct.unpack(">II", data[16:24])
            if height == 0 or width < min_width or abs(width / height - ratio[0] / ratio[1]) > 0.005:
                fail(f"{prefix}: wrong aspect ratio or insufficient width")
            dimensions.add((width, height))
            sha = hashlib.sha256(data).hexdigest()
            if sha in hashes:
                fail(f"{prefix}: duplicate image content")
            hashes.add(sha)
            image_records.append({"id": prefix, "file": card["file"], "order": card["order"], "expected_top_left": expected_header(card), "expected_bottom_right_page_marker": None, "width": width, "height": height, "sha256": sha})
        except (OSError, ValueError) as exc:
            fail(f"{prefix}: {exc}")
            continue
        observation = observations.get(prefix, {})
        if observation.get("image_sha256") != sha:
            fail(f"{prefix}: image changed or was not reviewed")
        if observation.get("method") not in {"visual", "visual+ocr"}:
            fail(f"{prefix}: real visual review is required")
        try:
            datetime.fromisoformat(observation.get("reviewed_at", "").replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            fail(f"{prefix}: reviewed_at must be an ISO timestamp")
        if normalize(observation.get("top_left_text")) != normalize(expected_header(card)):
            fail(f"{prefix}: top-left header/page number mismatch")
        if "bottom_right_page_marker" not in observation or observation["bottom_right_page_marker"] is not None:
            fail(f"{prefix}: bottom-right page marker must be absent")
        if observation.get("other_page_markers") != []:
            fail(f"{prefix}: extra page markers are present or unchecked")
        observed = observation.get("text_blocks")
        if not isinstance(observed, list) or [normalize(x) for x in observed] != [normalize(x) for x in card["text_blocks"]]:
            fail(f"{prefix}: visible copy differs from the manifest")
        checks = observation.get("checks", {})
        if not isinstance(checks, dict):
            checks = {}
        for check in VISUAL_CHECKS:
            if checks.get(check) is not True:
                fail(f"{prefix}: visual check not passed: {check}")
        if observation.get("issues") != []:
            fail(f"{prefix}: visual issues are missing or unresolved")
        if not prompt_path.is_file() or not prompt_path.read_text(encoding="utf-8").strip():
            fail(f"{prefix}: saved prompt missing or empty")
    if len(dimensions) > 1:
        fail("image dimensions are inconsistent across the series")
    for path in ancillary:
        if not path.is_file() or not path.read_text(encoding="utf-8").strip():
            fail(f"support/caption file missing or empty: {path.name}")
    package_files = [p for _, p, _ in resolved_cards]
    package_files += [manifest_path, review_path] + ancillary
    package_files += [p for _, _, p in resolved_cards]
    report["passed"] = not errors
    return report, list(dict.fromkeys(package_files))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--stage", choices=("plan", "release"), default="release")
    parser.add_argument("--review", type=Path)
    parser.add_argument("--package", type=Path, help="Create a new ZIP only after all checks pass")
    args = parser.parse_args()
    if args.package and args.stage != "release":
        parser.error("--package requires release stage")
    root = args.manifest.resolve().parent
    try:
        report, files = validate(args.manifest, args.review, args.stage)
        report_path = root / ("qa-plan.json" if args.stage == "plan" else "qa-report.json")
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if args.package and report["passed"]:
            output = args.package.resolve()
            if output.exists():
                raise ValueError("ZIP already exists; choose a new versioned filename")
            with zipfile.ZipFile(output, "x", compression=zipfile.ZIP_DEFLATED) as archive:
                for path in dict.fromkeys(files + [report_path]):
                    archive.write(path, path.relative_to(root))
            with zipfile.ZipFile(output) as archive:
                if archive.testzip() is not None:
                    raise ValueError("ZIP integrity check failed")
            report["package"] = str(output)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["passed"] else 1
    except (OSError, ValueError, TypeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
