"""
Tests that SKILL.md, examples, and tools docs contain the bridge from
evidence-harvest output to CSI CLI workflow.

These tests verify the user-experience contract — not code logic.
All content tested is public methodology. Not financial advice.
"""

import os
import unittest

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")


def _read(rel_path: str) -> str:
    with open(os.path.join(REPO_ROOT, rel_path), encoding="utf-8") as f:
        return f.read()


class TestSkillContainsBridge(unittest.TestCase):
    """SKILL.md must include the CLI bridge in its crowd-scan output contract."""

    @classmethod
    def setUpClass(cls):
        cls.skill = _read("skills/catalyst-swing-intelligence/SKILL.md")

    def test_convert_to_csi_section_present(self):
        self.assertIn("Convert to CSI Evidence CSV", self.skill)

    def test_template_command_present(self):
        self.assertIn("python tools/csi/csi.py template", self.skill)

    def test_observe_command_present(self):
        self.assertIn("python tools/csi/csi.py observe", self.skill)

    def test_score_command_present(self):
        self.assertIn("python tools/csi/csi.py score", self.skill)

    def test_report_command_present(self):
        self.assertIn("python tools/csi/csi.py report", self.skill)

    def test_not_buy_sell_hold_in_bridge(self):
        # The bridge section must preserve the non-advisory boundary
        idx = self.skill.find("Convert to CSI Evidence CSV")
        bridge_section = self.skill[idx:idx + 1500]
        self.assertIn("not a buy/sell/hold score", bridge_section.lower())


class TestCrowdScanExampleContainsMapping(unittest.TestCase):
    """crowd-scan-example.md must include a CSV mapping section."""

    @classmethod
    def setUpClass(cls):
        cls.example = _read("examples/crowd-scan-example.md")

    def test_convert_findings_section_present(self):
        self.assertIn("Convert Findings to CSI Evidence CSV", self.example)

    def test_csv_mapping_has_source_class(self):
        self.assertIn("source_class", self.example)

    def test_csv_mapping_has_evidence_quality(self):
        self.assertIn("evidence_quality", self.example)

    def test_command_sequence_present(self):
        self.assertIn("python tools/csi/csi.py template", self.example)
        self.assertIn("python tools/csi/csi.py observe", self.example)

    def test_fictional_label_present(self):
        self.assertIn("Fictional", self.example)

    def test_not_buy_sell_hold(self):
        lower = self.example.lower()
        self.assertNotIn("buy this", lower)
        self.assertNotIn("sell this", lower)
        self.assertNotIn("hold this", lower)


class TestToolsReadmeContainsWorkflow(unittest.TestCase):
    """tools/csi/README.md must include the full harvest-to-memory workflow."""

    @classmethod
    def setUpClass(cls):
        cls.readme = _read("tools/csi/README.md")

    def test_workflow_section_present(self):
        self.assertIn("From Evidence Harvest to Memory Flywheel", self.readme)

    def test_all_pipeline_commands_present(self):
        for cmd in ["template", "score", "report", "observe", "list", "outcome",
                    "monthly-review", "playbook"]:
            self.assertIn(f"csi.py {cmd}", self.readme, f"Missing command: {cmd}")

    def test_non_advisory_boundary(self):
        self.assertIn("not investment performance", self.readme.lower())


class TestNoAdvisoryLanguageInDocs(unittest.TestCase):
    """Public docs must not present the Crowd Signal Quality Score as buy/sell/hold advice."""

    DOCS = [
        "skills/catalyst-swing-intelligence/SKILL.md",
        "examples/crowd-scan-example.md",
        "tools/csi/README.md",
        "docs/crowd-signal-scoring.md",
        "docs/memory-flywheel.md",
    ]

    def test_score_not_presented_as_buy_score(self):
        for rel_path in self.DOCS:
            content = _read(rel_path)
            lower = content.lower()
            # These phrases must NOT appear as claims (they may appear in "not X" context)
            advisory_claims = [
                "this is a buy recommendation",
                "purchase shares",
                "recommended company",
                "portfolio allocation",
            ]
            for phrase in advisory_claims:
                self.assertNotIn(phrase, lower, f"Found '{phrase}' in {rel_path}")

    def test_crowd_signal_quality_not_equals_trade_decision(self):
        skill = _read("skills/catalyst-swing-intelligence/SKILL.md")
        self.assertIn("Crowd Signal Quality", skill)
        self.assertIn("Trade Decision", skill)


if __name__ == "__main__":
    unittest.main()
