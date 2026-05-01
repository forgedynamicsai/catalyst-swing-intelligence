"""
v0.5 operability tests: validate, import-md, wizard.
All data is fictional. Not financial advice.
"""

import csv
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools", "csi"))
import validation
import importer
import wizard

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
SAMPLE_CSV = os.path.join(REPO_ROOT, "tools", "csi", "sample_evidence.csv")
SAMPLE_MD = os.path.join(REPO_ROOT, "tools", "csi", "sample_evidence.md")


# ===========================================================================
# Validation tests (7 required)
# ===========================================================================

class TestValidationPass(unittest.TestCase):
    def test_valid_sample_passes(self):
        _, errors, warnings = validation.validate_file(SAMPLE_CSV)
        self.assertEqual(errors, [], f"Unexpected errors: {errors}")

    def test_cmd_validate_pass_exit_0(self):
        _, code = validation.cmd_validate(SAMPLE_CSV)
        self.assertEqual(code, 0)

    def test_pass_output_contains_next_commands(self):
        output, _ = validation.cmd_validate(SAMPLE_CSV)
        self.assertIn("python tools/csi/csi.py score", output)
        self.assertIn("python tools/csi/csi.py report", output)


class TestValidationErrors(unittest.TestCase):
    def _csv_with(self, rows: list[dict], fieldnames=None) -> str:
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        )
        cols = fieldnames or validation.REQUIRED_COLUMNS
        writer = csv.DictWriter(tmp, fieldnames=cols)
        writer.writeheader()
        writer.writerows(rows)
        tmp.close()
        return tmp.name

    def tearDown(self):
        pass  # temp files cleaned up per test

    def test_missing_required_column_fails(self):
        cols = [c for c in validation.REQUIRED_COLUMNS if c != "evidence_quality"]
        path = self._csv_with([{c: "x" if c not in validation.NUMERIC_RANGES else "5" for c in cols}],
                               fieldnames=cols)
        try:
            _, errors, _ = validation.validate_file(path)
            self.assertTrue(any("evidence_quality" in e for e in errors))
        finally:
            os.unlink(path)

    def test_out_of_range_numeric_fails(self):
        row = {c: "" for c in validation.REQUIRED_COLUMNS}
        row.update({"claim": "test", "source_name": "src", "source_class": "major_news",
                    "source_date": "2026-01-01", "source_type": "article",
                    "independence_rating": "99",  # out of range
                    "evidence_quality": "5", "specificity": "5",
                    "catalyst_alignment": "5", "dissent_quality": "3",
                    "time_signal": "5", "is_duplicate": "false"})
        path = self._csv_with([row])
        try:
            _, errors, _ = validation.validate_file(path)
            self.assertTrue(any("independence_rating" in e for e in errors),
                            f"Expected range error, got: {errors}")
        finally:
            os.unlink(path)

    def test_invalid_source_class_fails(self):
        row = {c: "" for c in validation.REQUIRED_COLUMNS}
        row.update({"claim": "test", "source_name": "src", "source_class": "twitter_hype",
                    "source_date": "2026-01-01", "source_type": "social",
                    "independence_rating": "5", "evidence_quality": "5",
                    "specificity": "5", "catalyst_alignment": "5",
                    "dissent_quality": "1", "time_signal": "5", "is_duplicate": "false"})
        path = self._csv_with([row])
        try:
            _, errors, _ = validation.validate_file(path)
            self.assertTrue(any("source_class" in e for e in errors))
        finally:
            os.unlink(path)

    def test_bad_boolean_fails(self):
        row = {c: "" for c in validation.REQUIRED_COLUMNS}
        row.update({"claim": "test", "source_name": "src", "source_class": "major_news",
                    "source_date": "2026-01-01", "source_type": "article",
                    "independence_rating": "5", "evidence_quality": "5",
                    "specificity": "5", "catalyst_alignment": "5",
                    "dissent_quality": "1", "time_signal": "5",
                    "is_duplicate": "maybe"})  # bad boolean
        path = self._csv_with([row])
        try:
            _, errors, _ = validation.validate_file(path)
            self.assertTrue(any("is_duplicate" in e for e in errors))
        finally:
            os.unlink(path)

    def test_empty_critical_field_produces_warning(self):
        row = {c: "" for c in validation.REQUIRED_COLUMNS}
        row.update({"claim": "",  # empty critical field
                    "source_name": "src", "source_class": "major_news",
                    "source_date": "2026-01-01", "source_type": "article",
                    "independence_rating": "5", "evidence_quality": "5",
                    "specificity": "5", "catalyst_alignment": "5",
                    "dissent_quality": "1", "time_signal": "5", "is_duplicate": "false"})
        path = self._csv_with([row])
        try:
            _, errors, warnings = validation.validate_file(path)
            self.assertEqual(errors, [])
            self.assertTrue(any("claim" in w for w in warnings))
        finally:
            os.unlink(path)

    def test_advisory_language_produces_warning(self):
        row = {c: "" for c in validation.REQUIRED_COLUMNS}
        row.update({"claim": "this is a buy now opportunity",  # advisory marker
                    "source_name": "src", "source_class": "major_news",
                    "source_date": "2026-01-01", "source_type": "article",
                    "independence_rating": "5", "evidence_quality": "5",
                    "specificity": "5", "catalyst_alignment": "5",
                    "dissent_quality": "1", "time_signal": "5", "is_duplicate": "false"})
        path = self._csv_with([row])
        try:
            _, errors, warnings = validation.validate_file(path)
            self.assertEqual(errors, [])
            self.assertTrue(any("buy now" in w.lower() for w in warnings))
        finally:
            os.unlink(path)

    def test_strict_mode_treats_warnings_as_errors(self):
        # Use sample CSV which passes normally — add a row with empty source_url
        row = {c: "" for c in validation.REQUIRED_COLUMNS}
        row.update({"claim": "test claim", "source_name": "src",
                    "source_class": "major_news", "source_date": "2026-01-01",
                    "source_type": "article", "independence_rating": "5",
                    "evidence_quality": "5", "specificity": "5",
                    "catalyst_alignment": "5", "dissent_quality": "1",
                    "time_signal": "5", "is_duplicate": "false",
                    "source_url": "", "notes": ""})  # missing source_url → warning
        path = self._csv_with([row])
        try:
            output, code = validation.cmd_validate(path, strict=True)
            self.assertEqual(code, 1)
        finally:
            os.unlink(path)


# ===========================================================================
# Import-md tests (6 required)
# ===========================================================================

class TestImportMd(unittest.TestCase):
    def _tmp_csv(self) -> str:
        f = tempfile.NamedTemporaryFile(suffix=".csv", delete=False)
        f.close()
        os.unlink(f.name)  # remove so importer can create it
        return f.name

    def test_standard_markdown_table_imports(self):
        out = self._tmp_csv()
        try:
            output, code = importer.import_md(SAMPLE_MD, out)
            self.assertEqual(code, 0, f"Import failed: {output}")
            self.assertTrue(Path(out).exists())
            with open(out, newline="") as f:
                rows = list(csv.DictReader(f))
            self.assertGreater(len(rows), 0)
        finally:
            if Path(out).exists():
                os.unlink(out)

    def test_header_aliases_normalized(self):
        md_text = (
            "| claim | source | url | class | date | type |\n"
            "|---|---|---|---|---|---|\n"
            "| Fictional claim A | Fictional Source | https://example.com | major_news | 2026-01-01 | article |\n"
        )
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False,
                                          encoding="utf-8") as f:
            f.write(md_text)
            md_path = f.name
        out = self._tmp_csv()
        try:
            output, code = importer.import_md(md_path, out)
            # Should succeed — aliases should be mapped
            with open(out, newline="") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["source_name"], "Fictional Source")
            self.assertEqual(rows[0]["source_url"], "https://example.com")
        finally:
            os.unlink(md_path)
            if Path(out).exists():
                os.unlink(out)

    def test_missing_optional_fields_use_defaults(self):
        # Minimal table — only claim and source_name
        md_text = (
            "| claim | source_name |\n"
            "|---|---|\n"
            "| Fictional claim B | Fictional Minimal Source |\n"
        )
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False,
                                          encoding="utf-8") as f:
            f.write(md_text)
            md_path = f.name
        out = self._tmp_csv()
        try:
            output, code = importer.import_md(md_path, out)
            self.assertIn("default", output.lower())
            with open(out, newline="") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(rows[0]["evidence_quality"], "0")
            self.assertIn("imported from markdown", rows[0]["notes"])
        finally:
            os.unlink(md_path)
            if Path(out).exists():
                os.unlink(out)

    def test_missing_required_unmappable_field_fails(self):
        # Table without claim column and no alias
        md_text = (
            "| source_name | evidence_quality |\n"
            "|---|---|\n"
            "| Source X | 10 |\n"
        )
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False,
                                          encoding="utf-8") as f:
            f.write(md_text)
            md_path = f.name
        out = self._tmp_csv()
        try:
            output, code = importer.import_md(md_path, out)
            self.assertEqual(code, 1)
            self.assertIn("claim", output.lower())
        finally:
            os.unlink(md_path)
            if Path(out).exists():
                os.unlink(out)

    def test_existing_output_not_overwritten(self):
        # Create a pre-existing output file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False,
                                          encoding="utf-8") as f:
            f.write("existing content\n")
            existing_path = f.name
        try:
            output, code = importer.import_md(SAMPLE_MD, existing_path)
            self.assertEqual(code, 1)
            self.assertIn("already exists", output)
        finally:
            os.unlink(existing_path)

    def test_imported_csv_validates(self):
        out = self._tmp_csv()
        try:
            _, import_code = importer.import_md(SAMPLE_MD, out)
            self.assertEqual(import_code, 0)
            _, errors, _ = validation.validate_file(out)
            self.assertEqual(errors, [], f"Imported CSV failed validation: {errors}")
        finally:
            if Path(out).exists():
                os.unlink(out)


# ===========================================================================
# Wizard tests
# ===========================================================================

class TestWizardHelp(unittest.TestCase):
    def test_wizard_dry_run_runs_without_error(self):
        output = wizard.dry_run_plan(
            "Fictional AI infrastructure signal",
            "evidence.csv",
            "data/csi",
            "reports/csi",
        )
        self.assertIsInstance(output, str)
        self.assertGreater(len(output), 0)

    def test_wizard_banner_contains_non_advisory(self):
        self.assertIn("does NOT provide", wizard.WIZARD_BANNER)
        self.assertIn("buy/sell/hold", wizard.WIZARD_BANNER)
        self.assertIn("Crowd Signal Quality", wizard.WIZARD_BANNER)

    def test_dry_run_plan_references_key_commands(self):
        output = wizard.dry_run_plan(
            "Fictional theme", "evidence.csv", "data/csi", "reports/csi"
        )
        for cmd in ["template", "validate", "score", "report", "observe",
                    "outcome", "monthly-review", "playbook"]:
            self.assertIn(cmd, output, f"Missing command: {cmd}")

    def test_dry_run_plan_no_recommendations(self):
        output = wizard.dry_run_plan(
            "Fictional theme", "evidence.csv", "data/csi", "reports/csi"
        ).lower()
        self.assertNotIn("buy this", output)
        self.assertNotIn("sell this", output)
        self.assertNotIn("invest in", output)

    def test_dry_run_no_interactive_side_effects(self):
        # dry_run_plan is a pure function — should not touch filesystem
        output = wizard.dry_run_plan(
            "Fictional theme", "evidence.csv", "data/csi", "reports/csi"
        )
        self.assertIn("dry-run", output.lower())

    def test_next_steps_text_non_advisory(self):
        text = wizard._next_steps_text("fake-signal-id").lower()
        self.assertIn("does not provide", text)
        self.assertIn("outcome", text)
        self.assertIn("monthly-review", text)
        self.assertIn("playbook", text)

    def test_slugify_produces_url_safe_string(self):
        slug = wizard._slugify("AI Data Center / Power Scarcity (Fictional!)")
        self.assertNotIn(" ", slug)
        self.assertNotIn("/", slug)
        self.assertNotIn("(", slug)


if __name__ == "__main__":
    unittest.main()
