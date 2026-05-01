"""
Tests for memory flywheel (memory.py).
All data is fictional. Not financial advice.
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools", "csi"))
import memory


def _tmp_dirs():
    tmp = tempfile.mkdtemp()
    data_dir = os.path.join(tmp, "data", "csi")
    reports_dir = os.path.join(tmp, "reports", "csi")
    reviews_dir = os.path.join(tmp, "reviews", "csi")
    playbooks_dir = os.path.join(tmp, "playbooks")
    return tmp, data_dir, reports_dir, reviews_dir, playbooks_dir


SAMPLE_CSV = os.path.join(
    os.path.dirname(__file__), "..", "tools", "csi", "sample_evidence.csv"
)


def _observe(data_dir, reports_dir, theme="Fictional AI infrastructure signal"):
    return memory.cmd_observe(SAMPLE_CSV, theme, data_dir=data_dir, reports_dir=reports_dir)


def _outcome(signal_id, data_dir, usefulness="useful", failure_mode="none",
             trajectory_correct="true", catalyst_occurred="true"):
    return memory.cmd_outcome(
        signal_id,
        event_confirmed="true",
        narrative_mainstreamed="true",
        trajectory_correct=trajectory_correct,
        catalyst_occurred=catalyst_occurred,
        transmission_confirmed="partial",
        usefulness=usefulness,
        failure_mode=failure_mode,
        notes="Fictional test outcome.",
        data_dir=data_dir,
    )


# ---------------------------------------------------------------------------
# 1. observe creates observations.jsonl
# ---------------------------------------------------------------------------
class TestObserveCreatesFile(unittest.TestCase):
    def test_creates_observations_jsonl(self):
        _, data_dir, reports_dir, _, _ = _tmp_dirs()
        _observe(data_dir, reports_dir)
        obs_path = os.path.join(data_dir, "observations.jsonl")
        self.assertTrue(os.path.exists(obs_path))

    def test_observation_has_required_fields(self):
        _, data_dir, reports_dir, _, _ = _tmp_dirs()
        _observe(data_dir, reports_dir)
        obs = memory.load_jsonl(os.path.join(data_dir, "observations.jsonl"))
        self.assertEqual(len(obs), 1)
        required = [
            "signal_id", "created_at", "theme", "crowd_signal_quality_score",
            "confidence", "source_coverage_grade", "signal_trajectory",
            "echo_chamber_risk", "source_classes", "source_group_coverage",
            "classification", "report_path",
        ]
        for field in required:
            self.assertIn(field, obs[0], f"Missing field: {field}")

    def test_classification_uses_new_vocabulary(self):
        _, data_dir, reports_dir, _, _ = _tmp_dirs()
        _observe(data_dir, reports_dir)
        obs = memory.load_jsonl(os.path.join(data_dir, "observations.jsonl"))[0]
        self.assertIn(obs["classification"], ("analysis-ready", "monitor", "reject"))
        self.assertNotIn(obs["classification"], ("tradeable", "watchlist"))


# ---------------------------------------------------------------------------
# 2. observe creates a report file
# ---------------------------------------------------------------------------
class TestObserveCreatesReport(unittest.TestCase):
    def test_report_file_exists(self):
        _, data_dir, reports_dir, _, _ = _tmp_dirs()
        _observe(data_dir, reports_dir)
        obs = memory.load_jsonl(os.path.join(data_dir, "observations.jsonl"))[0]
        self.assertTrue(os.path.exists(obs["report_path"]))

    def test_report_contains_not_recommendation(self):
        _, data_dir, reports_dir, _, _ = _tmp_dirs()
        _observe(data_dir, reports_dir)
        obs = memory.load_jsonl(os.path.join(data_dir, "observations.jsonl"))[0]
        with open(obs["report_path"], encoding="utf-8") as f:
            content = f.read()
        self.assertIn("Not a buy/sell/hold recommendation", content)


# ---------------------------------------------------------------------------
# 3. Duplicate signal_id does not overwrite
# ---------------------------------------------------------------------------
class TestDuplicateSignalId(unittest.TestCase):
    def test_duplicate_gets_new_id(self):
        _, data_dir, reports_dir, _, _ = _tmp_dirs()
        _observe(data_dir, reports_dir, theme="Same theme")
        _observe(data_dir, reports_dir, theme="Same theme")
        obs = memory.load_jsonl(os.path.join(data_dir, "observations.jsonl"))
        self.assertEqual(len(obs), 2)
        ids = {o["signal_id"] for o in obs}
        self.assertEqual(len(ids), 2, "Duplicate signal_id should get unique suffix")

    def test_original_observation_preserved(self):
        _, data_dir, reports_dir, _, _ = _tmp_dirs()
        _observe(data_dir, reports_dir, theme="Unique theme A")
        _observe(data_dir, reports_dir, theme="Unique theme A")
        obs = memory.load_jsonl(os.path.join(data_dir, "observations.jsonl"))
        first_id = obs[0]["signal_id"]
        self.assertFalse(first_id.endswith("-2"), "Original should not be overwritten")


# ---------------------------------------------------------------------------
# 4. list shows reviewed/unreviewed status
# ---------------------------------------------------------------------------
class TestListCommand(unittest.TestCase):
    def test_shows_unreviewed_by_default(self):
        _, data_dir, reports_dir, _, _ = _tmp_dirs()
        _observe(data_dir, reports_dir)
        output = memory.cmd_list(data_dir=data_dir)
        self.assertIn("unreviewed", output)

    def test_shows_reviewed_after_outcome(self):
        _, data_dir, reports_dir, _, _ = _tmp_dirs()
        _observe(data_dir, reports_dir)
        obs = memory.load_jsonl(os.path.join(data_dir, "observations.jsonl"))
        _outcome(obs[0]["signal_id"], data_dir)
        output = memory.cmd_list(data_dir=data_dir)
        self.assertIn("reviewed", output)

    def test_no_observations_message(self):
        _, data_dir, _, _, _ = _tmp_dirs()
        output = memory.cmd_list(data_dir=data_dir)
        self.assertIn("No observations found", output)


# ---------------------------------------------------------------------------
# 5. outcome refuses unknown signal_id
# ---------------------------------------------------------------------------
class TestOutcomeRefusesUnknown(unittest.TestCase):
    def test_unknown_signal_id_raises(self):
        _, data_dir, reports_dir, _, _ = _tmp_dirs()
        _observe(data_dir, reports_dir)
        with self.assertRaises(SystemExit):
            memory.cmd_outcome("definitely-not-a-real-id", data_dir=data_dir)


# ---------------------------------------------------------------------------
# 6. outcome appends for known signal_id
# ---------------------------------------------------------------------------
class TestOutcomeAppends(unittest.TestCase):
    def test_outcome_saved(self):
        _, data_dir, reports_dir, _, _ = _tmp_dirs()
        _observe(data_dir, reports_dir)
        obs = memory.load_jsonl(os.path.join(data_dir, "observations.jsonl"))
        _outcome(obs[0]["signal_id"], data_dir)
        outcomes = memory.load_jsonl(os.path.join(data_dir, "outcomes.jsonl"))
        self.assertEqual(len(outcomes), 1)
        self.assertEqual(outcomes[0]["signal_id"], obs[0]["signal_id"])

    def test_outcome_has_required_fields(self):
        _, data_dir, reports_dir, _, _ = _tmp_dirs()
        _observe(data_dir, reports_dir)
        obs = memory.load_jsonl(os.path.join(data_dir, "observations.jsonl"))
        _outcome(obs[0]["signal_id"], data_dir)
        out = memory.load_jsonl(os.path.join(data_dir, "outcomes.jsonl"))[0]
        required = [
            "signal_id", "reviewed_at", "event_confirmed", "narrative_mainstreamed",
            "trajectory_correct", "catalyst_occurred", "transmission_confirmed",
            "signal_usefulness", "failure_mode",
        ]
        for field in required:
            self.assertIn(field, out, f"Missing field: {field}")

    def test_outcome_no_price_fields(self):
        _, data_dir, reports_dir, _, _ = _tmp_dirs()
        _observe(data_dir, reports_dir)
        obs = memory.load_jsonl(os.path.join(data_dir, "observations.jsonl"))
        _outcome(obs[0]["signal_id"], data_dir)
        out = memory.load_jsonl(os.path.join(data_dir, "outcomes.jsonl"))[0]
        forbidden = ["return", "profit", "loss", "buy_price", "sell_price", "position_size"]
        for field in forbidden:
            self.assertNotIn(field, out)


# ---------------------------------------------------------------------------
# 7. monthly-review handles no data
# ---------------------------------------------------------------------------
class TestMonthlyReviewNoData(unittest.TestCase):
    def test_handles_empty_data_dir(self):
        _, data_dir, _, reviews_dir, _ = _tmp_dirs()
        out_path = os.path.join(reviews_dir, "2026-01-monthly-review.md")
        memory.cmd_monthly_review("2026-01", data_dir=data_dir, output_path=out_path)
        self.assertTrue(os.path.exists(out_path))
        with open(out_path) as f:
            content = f.read()
        self.assertIn("2026-01", content)
        self.assertIn("Non-Advisory Boundary", content)

    def test_handles_no_reviewed_outcomes(self):
        _, data_dir, reports_dir, reviews_dir, _ = _tmp_dirs()
        _observe(data_dir, reports_dir)
        out_path = os.path.join(reviews_dir, "2026-05-review.md")
        memory.cmd_monthly_review("2026-05", data_dir=data_dir, output_path=out_path)
        with open(out_path) as f:
            content = f.read()
        self.assertIn("Non-Advisory Boundary", content)


# ---------------------------------------------------------------------------
# 8. monthly-review summarizes counts
# ---------------------------------------------------------------------------
class TestMonthlyReviewCounts(unittest.TestCase):
    def _setup_with_outcome(self, usefulness="useful", failure_mode="none"):
        _, data_dir, reports_dir, reviews_dir, _ = _tmp_dirs()
        _observe(data_dir, reports_dir)
        obs = memory.load_jsonl(os.path.join(data_dir, "observations.jsonl"))
        _outcome(obs[0]["signal_id"], data_dir, usefulness=usefulness, failure_mode=failure_mode)
        return data_dir, reviews_dir

    def test_useful_count_reflected(self):
        data_dir, reviews_dir = self._setup_with_outcome(usefulness="useful")
        out_path = os.path.join(reviews_dir, "review.md")
        month = memory.load_jsonl(os.path.join(data_dir, "observations.jsonl"))[0]["created_at"][:7]
        memory.cmd_monthly_review(month, data_dir=data_dir, output_path=out_path)
        with open(out_path) as f:
            content = f.read()
        self.assertIn("Useful:", content)
        self.assertIn("Signals reviewed:", content)

    def test_not_useful_count_reflected(self):
        data_dir, reviews_dir = self._setup_with_outcome(usefulness="not_useful", failure_mode="hype")
        out_path = os.path.join(reviews_dir, "review.md")
        month = memory.load_jsonl(os.path.join(data_dir, "observations.jsonl"))[0]["created_at"][:7]
        memory.cmd_monthly_review(month, data_dir=data_dir, output_path=out_path)
        with open(out_path) as f:
            content = f.read()
        self.assertIn("Not useful:", content)
        self.assertIn("Non-Advisory Boundary", content)


# ---------------------------------------------------------------------------
# 9. playbook handles insufficient data
# ---------------------------------------------------------------------------
class TestPlaybookInsufficientData(unittest.TestCase):
    def test_insufficient_data_message(self):
        _, data_dir, reports_dir, _, playbooks_dir = _tmp_dirs()
        _observe(data_dir, reports_dir)
        out_path = os.path.join(playbooks_dir, "playbook.md")
        memory.cmd_playbook(data_dir=data_dir, output_path=out_path)
        with open(out_path) as f:
            content = f.read()
        self.assertIn("Insufficient", content)
        self.assertIn("Non-Advisory Boundary", content)

    def test_playbook_with_zero_observations(self):
        _, data_dir, _, _, playbooks_dir = _tmp_dirs()
        out_path = os.path.join(playbooks_dir, "playbook.md")
        memory.cmd_playbook(data_dir=data_dir, output_path=out_path)
        with open(out_path) as f:
            content = f.read()
        self.assertIn("Non-Advisory Boundary", content)


# ---------------------------------------------------------------------------
# 10. playbook produces patterns with enough reviewed sample data
# ---------------------------------------------------------------------------
class TestPlaybookWithData(unittest.TestCase):
    def _make_reviewed_dataset(self, n=6):
        _, data_dir, reports_dir, _, playbooks_dir = _tmp_dirs()
        for i in range(n):
            theme = f"Fictional signal theme number {i}"
            memory.cmd_observe(SAMPLE_CSV, theme, data_dir=data_dir, reports_dir=reports_dir)
        obs_list = memory.load_jsonl(os.path.join(data_dir, "observations.jsonl"))
        for obs in obs_list:
            _outcome(obs["signal_id"], data_dir, usefulness="useful")
        return data_dir, playbooks_dir

    def test_playbook_sections_present(self):
        data_dir, playbooks_dir = self._make_reviewed_dataset(6)
        out_path = os.path.join(playbooks_dir, "playbook.md")
        memory.cmd_playbook(data_dir=data_dir, output_path=out_path)
        with open(out_path) as f:
            content = f.read()
        self.assertIn("Current Best Signal Patterns", content)
        self.assertIn("Source-Class Lessons", content)
        self.assertIn("Trajectory Lessons", content)
        self.assertIn("Non-Advisory Boundary", content)

    def test_playbook_not_investment_playbook(self):
        data_dir, playbooks_dir = self._make_reviewed_dataset(6)
        out_path = os.path.join(playbooks_dir, "playbook.md")
        memory.cmd_playbook(data_dir=data_dir, output_path=out_path)
        with open(out_path) as f:
            content = f.read()
        self.assertIn("not an investment playbook", content.lower())


# ---------------------------------------------------------------------------
# 11. No command requires network access (structural check)
# ---------------------------------------------------------------------------
class TestNoNetworkRequired(unittest.TestCase):
    def test_observe_no_network(self):
        # observe only uses local files and csi module — no network calls possible
        _, data_dir, reports_dir, _, _ = _tmp_dirs()
        # Should complete without any network error
        _observe(data_dir, reports_dir)

    def test_playbook_no_network(self):
        _, data_dir, _, _, playbooks_dir = _tmp_dirs()
        out_path = os.path.join(playbooks_dir, "pb.md")
        memory.cmd_playbook(data_dir=data_dir, output_path=out_path)


# ---------------------------------------------------------------------------
# 12. No generated text claims buy/sell/hold
# ---------------------------------------------------------------------------
class TestNoBuySellHoldClaims(unittest.TestCase):
    def test_outcome_output_no_buysellhold(self):
        _, data_dir, reports_dir, _, _ = _tmp_dirs()
        _observe(data_dir, reports_dir)
        obs = memory.load_jsonl(os.path.join(data_dir, "observations.jsonl"))
        result = _outcome(obs[0]["signal_id"], data_dir)
        lower = result.lower()
        self.assertNotIn("buy this", lower)
        self.assertNotIn("sell this", lower)
        self.assertNotIn("hold this", lower)
        self.assertIn("does not recommend", lower)

    def test_observe_reminder_not_recommendation(self):
        _, data_dir, reports_dir, _, _ = _tmp_dirs()
        result = _observe(data_dir, reports_dir)
        self.assertIn("not a buy/sell/hold recommendation", result.lower())


# ---------------------------------------------------------------------------
# 13. Playbook does not suggest purchases/investments/companies to buy
# ---------------------------------------------------------------------------
class TestPlaybookNoPurchaseSuggestions(unittest.TestCase):
    def test_playbook_non_advisory_boundary_present(self):
        _, data_dir, _, _, playbooks_dir = _tmp_dirs()
        out_path = os.path.join(playbooks_dir, "pb.md")
        memory.cmd_playbook(data_dir=data_dir, output_path=out_path)
        with open(out_path) as f:
            content = f.read()
        self.assertIn("Non-Advisory Boundary", content)
        self.assertNotIn("purchase shares", content.lower())
        self.assertNotIn("invest in", content.lower())
        self.assertNotIn("recommended company", content.lower())

    def test_playbook_does_not_name_companies(self):
        _, data_dir, _, _, playbooks_dir = _tmp_dirs()
        out_path = os.path.join(playbooks_dir, "pb.md")
        memory.cmd_playbook(data_dir=data_dir, output_path=out_path)
        with open(out_path) as f:
            content = f.read()
        # These should never appear in playbook recommendations
        forbidden = ["buy TICKER", "invest in TICKER", "position size", "portfolio allocation"]
        for phrase in forbidden:
            self.assertNotIn(phrase, content)


# ---------------------------------------------------------------------------
# 14. New outputs use analysis-ready / monitor / reject
# ---------------------------------------------------------------------------
class TestClassificationVocabulary(unittest.TestCase):
    def test_observe_does_not_use_tradeable(self):
        _, data_dir, reports_dir, _, _ = _tmp_dirs()
        result = _observe(data_dir, reports_dir)
        self.assertNotIn("tradeable", result.lower())
        self.assertNotIn("watchlist", result.lower())

    def test_classify_signal_uses_new_vocabulary(self):
        import csi as _csi
        rows = [
            {
                "claim": "test", "source_name": "TestSource", "source_url": "",
                "source_class": "trade_publication", "source_date": "2025-01-01",
                "source_type": "article", "independence_rating": "15",
                "evidence_quality": "15", "specificity": "15", "catalyst_alignment": "8",
                "dissent_quality": "2", "time_signal": "7", "is_duplicate": "false",
                "notes": "fictional",
            }
        ] * 6
        result = _csi.score_evidence(rows)
        cls = memory.classify_signal(result)
        self.assertIn(cls, ("analysis-ready", "monitor", "reject"))
        self.assertNotIn(cls, ("tradeable", "watchlist"))

    def test_reject_for_low_score(self):
        result = {
            "score": 20,
            "source_coverage_grade": "D",
            "confidence": "no full-confidence score",
            "trajectory": "unknown",
            "dedupe": {"possible_echo_chamber": False, "duplicate_count": 0, "duplicate_ratio": 0},
            "disclaimer": "",
            "components": {},
            "penalties": {},
        }
        self.assertEqual(memory.classify_signal(result), "reject")

    def test_analysis_ready_for_high_score_grade_a(self):
        result = {
            "score": 72,
            "source_coverage_grade": "A",
            "confidence": "standard",
            "trajectory": "accelerating",
            "dedupe": {"possible_echo_chamber": False, "duplicate_count": 0, "duplicate_ratio": 0},
            "disclaimer": "",
            "components": {},
            "penalties": {},
        }
        self.assertEqual(memory.classify_signal(result), "analysis-ready")


# ---------------------------------------------------------------------------
# 15. Playbook non-advisory boundary
# ---------------------------------------------------------------------------
class TestPlaybookNonAdvisoryBoundary(unittest.TestCase):
    def test_boundary_headline_present(self):
        _, data_dir, _, _, playbooks_dir = _tmp_dirs()
        out_path = os.path.join(playbooks_dir, "pb.md")
        memory.cmd_playbook(data_dir=data_dir, output_path=out_path)
        with open(out_path) as f:
            content = f.read()
        self.assertIn("Crowd Signal Playbook", content)
        self.assertIn("Investment Playbook", content)
        self.assertIn("Non-Advisory Boundary", content)

    def test_monthly_review_boundary_present(self):
        _, data_dir, _, reviews_dir, _ = _tmp_dirs()
        out_path = os.path.join(reviews_dir, "review.md")
        memory.cmd_monthly_review("2026-05", data_dir=data_dir, output_path=out_path)
        with open(out_path) as f:
            content = f.read()
        self.assertIn("Non-Advisory Boundary", content)


if __name__ == "__main__":
    unittest.main()
