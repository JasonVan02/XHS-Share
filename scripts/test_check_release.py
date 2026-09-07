#!/usr/bin/env python3
"""Regression tests for the mechanical validator, using synthetic review records.

The records deliberately do not claim to transcribe the sample images. These
tests check acceptance/rejection logic, not visual quality or factual accuracy.
"""

import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

from check_release import digest, expected_header, validate


class ReleaseChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "images").mkdir()
        (self.root / "prompts").mkdir()
        assets = Path(__file__).resolve().parent.parent / "assets"
        for name, source in [("01-cover", "style-cover.png"), ("02-method", "style-content.png")]:
            shutil.copy2(assets / source, self.root / "images" / f"{name}.png")
            (self.root / "prompts" / f"{name}.md").write_text("Synthetic fixture prompt", encoding="utf-8")
        (self.root / "caption.txt").write_text("Synthetic fixture caption", encoding="utf-8")
        self.manifest = {
            "schema_version": 1,
            "title": "Fixture title",
            "total_images": 2,
            "caption_file": "caption.txt",
            "support_files": [],
            "cards": [
                {"id": "cover", "order": 1, "kind": "cover", "file": "images/01-cover.png", "prompt": "prompts/01-cover.md", "section_label": "AI WORKFLOW", "text_blocks": ["让 Codex 理解目标"]},
                {"id": "method", "order": 2, "kind": "content", "file": "images/02-method.png", "prompt": "prompts/02-method.md", "section_label": "先说清楚", "text_blocks": ["Codex却越做越像 B。", "执行 → 自检"]},
            ],
        }
        self.manifest_path = self.root / "manifest.json"
        self.review_path = self.root / "review.json"
        self.write_manifest()
        self.review = {
            "schema_version": 1,
            "manifest_sha256": digest(self.manifest_path),
            "editorial": {"title_body_aligned": True, "claims_checked": True, "story_order_checked": True, "caption_consistent": True, "issues": []},
            "cards": [],
        }
        for card in self.manifest["cards"]:
            self.review["cards"].append({
                "id": card["id"],
                "image_sha256": digest(self.root / card["file"]),
                "reviewed_at": "2026-09-07T10:00:00+08:00",
                "method": "visual",
                "top_left_text": expected_header(card),
                "bottom_right_page_marker": None,
                "other_page_markers": [],
                "text_blocks": copy.deepcopy(card["text_blocks"]),
                "checks": {"legibility": True, "layout": True, "style_consistency": True, "content_numbers_and_arrows": True},
                "issues": [],
            })

    def write_manifest(self):
        self.manifest_path.write_text(json.dumps(self.manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    def run_check(self, stage="release"):
        self.review_path.write_text(json.dumps(self.review, ensure_ascii=False), encoding="utf-8")
        return validate(self.manifest_path, self.review_path, stage)[0]

    def assert_rejected(self, expected_message):
        result = self.run_check()
        self.assertFalse(result["passed"])
        self.assertTrue(any(expected_message in e for e in result["errors"]), result["errors"])

    def test_valid_records_and_cover_excluded(self):
        result = self.run_check()
        self.assertTrue(result["passed"], result["errors"])
        self.assertEqual(result["images"][1]["expected_top_left"], "01 先说清楚")

    def test_plan_does_not_require_generated_images(self):
        shutil.rmtree(self.root / "images")
        self.assertTrue(self.run_check("plan")["passed"])

    def test_rejects_upload_order_error(self):
        self.manifest["cards"].reverse()
        self.write_manifest()
        self.assert_rejected("upload order")

    def test_rejects_manual_page_number_in_label(self):
        self.manifest["cards"][1]["section_label"] = "02 先说清楚"
        self.write_manifest()
        self.assert_rejected("manual page number")

    def test_allows_numbers_that_are_content_in_a_label(self):
        self.manifest["cards"][0]["section_label"] = "2026 AI WORKFLOW"
        self.manifest["cards"][1]["section_label"] = "3个使用场景"
        self.write_manifest()
        self.assertTrue(self.run_check("plan")["passed"])

    def test_rejects_cover_counted_in_top_left(self):
        self.review["cards"][1]["top_left_text"] = "02 先说清楚"
        self.assert_rejected("top-left header/page number mismatch")

    def test_rejects_residual_bottom_page_number(self):
        self.review["cards"][1]["bottom_right_page_marker"] = "02 / 06"
        self.assert_rejected("bottom-right page marker")

    def test_rejects_old_pronoun_copy(self):
        self.review["cards"][1]["text_blocks"][0] = "它却越做越像 B。"
        self.assert_rejected("visible copy differs")

    def test_rejects_stale_manifest_review(self):
        self.manifest["title"] = "New topic"
        self.write_manifest()
        self.assert_rejected("manifest changed after review")

    def test_rejects_image_replaced_after_review(self):
        assets = Path(__file__).resolve().parent.parent / "assets"
        shutil.copy2(assets / "style-benefit.png", self.root / "images/02-method.png")
        self.assert_rejected("image changed or was not reviewed")

    def test_rejects_missing_page(self):
        (self.root / "images/02-method.png").unlink()
        self.assertFalse(self.run_check()["passed"])

    def test_rejects_duplicate_picture(self):
        shutil.copy2(self.root / "images/01-cover.png", self.root / "images/02-method.png")
        self.assert_rejected("duplicate image content")

    def test_rejects_unchecked_visual_quality(self):
        self.review["cards"][1]["checks"]["legibility"] = False
        self.assert_rejected("visual check not passed: legibility")

    def test_rejects_unresolved_editorial_issue(self):
        self.review["editorial"]["issues"] = ["Unverified quota claim"]
        self.assert_rejected("editorial issues")

    def test_rejects_path_outside_release(self):
        self.manifest["cards"][1]["file"] = "../private.png"
        self.write_manifest()
        self.assert_rejected("inside release directory")

    def test_package_is_ordered_and_excludes_unlisted_files(self):
        self.run_check()
        (self.root / "old-draft.txt").write_text("Do not ship", encoding="utf-8")
        output = self.root / "final.zip"
        script = Path(__file__).with_name("check_release.py")
        args = [sys.executable, str(script), str(self.manifest_path), "--review", str(self.review_path), "--package", str(output)]
        result = subprocess.run(args, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        with zipfile.ZipFile(output) as archive:
            self.assertEqual(archive.namelist()[:2], ["images/01-cover.png", "images/02-method.png"])
            self.assertNotIn("old-draft.txt", archive.namelist())
            self.assertIsNone(archive.testzip())
        again = subprocess.run(args, capture_output=True, text=True)
        self.assertNotEqual(again.returncode, 0)
        self.assertIn("already exists", again.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
