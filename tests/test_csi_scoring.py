"""
Tests for csi.py scoring logic.
All evidence is fictional. Not financial advice.
"""

import csv
import io
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools", "csi"))
import csi


def _make_rows(overrides: list[dict] = None) -> list[dict]:
    base = {
        "claim": "Fictional claim about TICKER_A",
        "source_name": "FictionalSource",
        "source_url": "https://example.com/1",
        "source_class": "trade_publication",
        "source_date": "2025-01-01",
        "source_type": "article",
        "independence_rating": "14",
        "evidence_quality": "14",
        "specificity": "14",
        "catalyst_alignment": "7",
        "dissent_quality": "3",
        "time_signal": "7",
        "is_duplicate": "false",
        "notes": "fictional example",
    }
    if overrides is None:
        return [base]
    return [{**base, **o} for o in overrides]


class TestScoreRange(unittest.TestCase):
    def test_score_always_0_to_100(self):
        rows = _make_rows()
        result = csi.score_evidence(rows)
        self.assertGreaterEqual(result["score"], 0)
        self.assertLessEqual(result["score"], 100)

    def test_score_with_max_values(self):
        rows = _make_rows([{
            "independence_rating": "20", "evidence_quality": "20",
            "specificity": "20", "catalyst_alignment": "10",
            "dissent_quality": "5", "time_signal": "10",
        }] * 8)
        result = csi.score_evidence(rows)
        self.assertLessEqual(result["score"], 100)
        self.assertGreaterEqual(result["score"], 0)

    def test_score_with_zero_values(self):
        rows = _make_rows([{
            "independence_rating": "0", "evidence_quality": "0",
            "specificity": "0", "catalyst_alignment": "0",
            "dissent_quality": "0", "time_signal": "0",
            "notes": "meme yolo moon guaranteed",
        }])
        result = csi.score_evidence(rows)
        self.assertEqual(result["score"], 0)


class TestEmptyEvidence(unittest.TestCase):
    def test_empty_returns_no_confidence(self):
        result = csi.score_evidence([])
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["source_coverage_grade"], "F")
        self.assertIn("no-evidence", result["confidence"])

    def test_empty_trajectory_unknown(self):
        result = csi.score_evidence([])
        self.assertEqual(result["trajectory"], "unknown")


class TestDuplicatePenalty(unittest.TestCase):
    def test_duplicates_reduce_score(self):
        clean_rows = _make_rows([{"source_name": f"Source{i}"} for i in range(5)])
        dup_rows = _make_rows([
            {"source_name": "Source1", "is_duplicate": "false"},
            {"source_name": "Source1", "is_duplicate": "true"},
            {"source_name": "Source1", "is_duplicate": "true"},
            {"source_name": "Source1", "is_duplicate": "true"},
        ])
        clean_result = csi.score_evidence(clean_rows)
        dup_result = csi.score_evidence(dup_rows)
        self.assertGreater(clean_result["score"], dup_result["score"])

    def test_echo_chamber_flagged(self):
        rows = _make_rows([{"is_duplicate": "true"}] * 6 + [{"is_duplicate": "false"}])
        dedupe = csi.dedupe_check(rows)
        self.assertTrue(dedupe["possible_echo_chamber"])


class TestUnknownSourcePenalty(unittest.TestCase):
    def test_unknown_sources_reduce_score(self):
        known_rows = _make_rows([{"source_class": "trade_publication"} for _ in range(4)])
        unknown_rows = _make_rows([{"source_class": "unknown"} for _ in range(4)])
        known_result = csi.score_evidence(known_rows)
        unknown_result = csi.score_evidence(unknown_rows)
        self.assertGreater(known_result["score"], unknown_result["score"])


class TestSourceCoverageGrade(unittest.TestCase):
    def test_multiple_groups_improve_grade(self):
        single_class = _make_rows([{"source_class": "social_media"}])
        multi_class = _make_rows([
            {"source_class": "primary_filing", "dissent_quality": "0"},
            {"source_class": "social_media", "dissent_quality": "0"},
            {"source_class": "major_news", "dissent_quality": "0"},
        ])
        single_result = csi.score_evidence(single_class)
        multi_result = csi.score_evidence(multi_class)
        grade_order = ["F", "D", "C", "B", "A"]
        self.assertGreater(
            grade_order.index(multi_result["source_coverage_grade"]),
            grade_order.index(single_result["source_coverage_grade"]),
        )

    def test_grade_a_requires_dissent(self):
        rows = _make_rows([
            {"source_class": "primary_filing", "dissent_quality": "4"},
            {"source_class": "social_media", "dissent_quality": "0"},
            {"source_class": "prediction_market", "dissent_quality": "0"},
        ])
        result = csi.score_evidence(rows)
        self.assertEqual(result["source_coverage_grade"], "A")

    def test_no_evidence_is_grade_f(self):
        result = csi.score_evidence([])
        self.assertEqual(result["source_coverage_grade"], "F")


class TestDisclaimerPresent(unittest.TestCase):
    def test_disclaimer_in_score_result(self):
        rows = _make_rows()
        result = csi.score_evidence(rows)
        disclaimer = result["disclaimer"].lower()
        self.assertIn("not a buy", disclaimer)
        self.assertIn("sell", disclaimer)
        self.assertIn("hold", disclaimer)

    def test_report_contains_not_recommendation(self):
        rows = _make_rows()
        result = csi.score_evidence(rows)
        report = csi._build_report_markdown("Test Theme", rows, result)
        self.assertIn("Not a buy/sell/hold recommendation", report)

    def test_score_label_not_buy_score(self):
        rows = _make_rows()
        result = csi.score_evidence(rows)
        self.assertIn("NOT a buy/sell/hold score", result["disclaimer"])


class TestSampleEvidenceReport(unittest.TestCase):
    def test_sample_evidence_produces_report_without_crash(self):
        sample_path = os.path.join(
            os.path.dirname(__file__), "..", "tools", "csi", "sample_evidence.csv"
        )
        rows = csi.load_evidence(sample_path)
        result = csi.score_evidence(rows)
        report = csi._build_report_markdown("Sample Theme", rows, result)
        self.assertIn("Crowd Signal Report", report)
        self.assertIn("Score Breakdown", report)
        self.assertGreaterEqual(result["score"], 0)
        self.assertLessEqual(result["score"], 100)

    def test_demo_runs_without_crash(self):
        output = csi.cmd_demo()
        self.assertIn("Crowd Signal Report", output)
        self.assertNotIn("Arron", output)
        self.assertNotIn("Carter", output)
        self.assertNotIn("PCS", output)


class TestQueryGenerator(unittest.TestCase):
    def test_queries_generated_for_theme(self):
        output = csi.cmd_queries("AI data center power scarcity")
        self.assertIn("Reuters", output)
        self.assertIn("Reddit", output)
        self.assertIn("Polymarket", output)
        self.assertIn("13F", output)

    def test_queries_do_not_execute_searches(self):
        # The function is purely string generation — no network calls
        output = csi.cmd_queries("fictional theme XYZ")
        self.assertIn("fictional theme XYZ", output)
        self.assertIn("Cost: $0", output)


class TestTemplateCommand(unittest.TestCase):
    def test_template_creates_csv_with_correct_columns(self):
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            tmp_path = f.name
        try:
            csi.cmd_template(tmp_path)
            with open(tmp_path, newline="") as f:
                reader = csv.DictReader(f)
                self.assertEqual(reader.fieldnames, csi.EVIDENCE_COLUMNS)
        finally:
            os.unlink(tmp_path)


if __name__ == "__main__":
    unittest.main()
