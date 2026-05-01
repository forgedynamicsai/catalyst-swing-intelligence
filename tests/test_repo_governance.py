"""
Governance guardrail tests — verify required files exist and maintain safe boundaries.
Not financial advice. Not a buy/sell/hold system.
"""

import os
import unittest

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")


def _exists(rel_path: str) -> bool:
    return os.path.isfile(os.path.join(REPO_ROOT, rel_path))


def _read(rel_path: str) -> str:
    with open(os.path.join(REPO_ROOT, rel_path), encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# File existence
# ---------------------------------------------------------------------------

class TestGovernanceFilesExist(unittest.TestCase):

    def test_ci_workflow_exists(self):
        self.assertTrue(_exists(".github/workflows/tests.yml"))

    def test_codeowners_exists(self):
        self.assertTrue(_exists(".github/CODEOWNERS"))

    def test_pr_template_exists(self):
        self.assertTrue(_exists(".github/pull_request_template.md"))

    def test_bug_report_template_exists(self):
        self.assertTrue(_exists(".github/ISSUE_TEMPLATE/bug_report.md"))

    def test_feature_request_template_exists(self):
        self.assertTrue(_exists(".github/ISSUE_TEMPLATE/feature_request.md"))

    def test_scoring_question_template_exists(self):
        self.assertTrue(_exists(".github/ISSUE_TEMPLATE/scoring_question.md"))

    def test_source_request_template_exists(self):
        self.assertTrue(_exists(".github/ISSUE_TEMPLATE/source_request.md"))

    def test_maintainer_policy_exists(self):
        self.assertTrue(_exists("docs/maintainer-policy.md"))

    def test_security_md_exists(self):
        self.assertTrue(_exists("SECURITY.md"))


# ---------------------------------------------------------------------------
# README links
# ---------------------------------------------------------------------------

class TestReadmeLinks(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.readme = _read("README.md")

    def test_readme_links_to_maintainer_policy(self):
        self.assertIn("maintainer-policy.md", self.readme)

    def test_readme_has_contributing_safely_section(self):
        self.assertIn("Contributing Safely", self.readme)

    def test_readme_has_official_repo_vs_forks(self):
        self.assertIn("Official Repo vs Forks", self.readme)


# ---------------------------------------------------------------------------
# CONTRIBUTING.md links
# ---------------------------------------------------------------------------

class TestContributingLinks(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.contrib = _read("CONTRIBUTING.md")

    def test_contributing_links_to_maintainer_policy(self):
        self.assertIn("maintainer-policy.md", self.contrib)

    def test_contributing_has_before_opening_pr_section(self):
        self.assertIn("Before Opening a PR", self.contrib)

    def test_contributing_has_do_not_submit_section(self):
        self.assertIn("Do Not Submit", self.contrib)


# ---------------------------------------------------------------------------
# Maintainer policy content
# ---------------------------------------------------------------------------

class TestMaintainerPolicy(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.policy = _read("docs/maintainer-policy.md")

    def test_crowd_signal_quality_boundary(self):
        self.assertIn("Crowd Signal Quality ≠ Security Risk ≠ Trade Decision", self.policy)

    def test_playbook_boundary(self):
        self.assertIn("Crowd Signal Playbook ≠ Investment Playbook", self.policy)

    def test_merge_requirements_present(self):
        self.assertIn("Merge Requirements", self.policy)

    def test_maintainer_rights_present(self):
        self.assertIn("Maintainer Rights", self.policy)

    def test_classification_language_documented(self):
        self.assertIn("analysis-ready / monitor / reject", self.policy)

    def test_non_advisory_footer(self):
        lower = self.policy.lower()
        self.assertIn("does not recommend", lower)


# ---------------------------------------------------------------------------
# PR template content
# ---------------------------------------------------------------------------

class TestPRTemplate(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.template = _read(".github/pull_request_template.md")

    def test_non_advisory_boundary_checklist(self):
        self.assertIn("Non-Advisory Boundary", self.template)
        self.assertIn("buy/sell/hold", self.template)

    def test_privacy_boundary_checklist(self):
        self.assertIn("Privacy Boundary", self.template)
        self.assertIn("PERSONALIZATION.local.md", self.template)

    def test_source_evidence_boundary_checklist(self):
        self.assertIn("Source / Evidence Boundary", self.template)
        self.assertIn("paid API", self.template)

    def test_test_run_requirement(self):
        self.assertIn("python -m unittest discover", self.template)

    def test_preserves_core_boundaries(self):
        self.assertIn("Crowd Signal Quality ≠ Security Risk ≠ Trade Decision", self.template)
        self.assertIn("Crowd Signal Playbook ≠ Investment Playbook", self.template)


# ---------------------------------------------------------------------------
# No advisory language in governance files
# ---------------------------------------------------------------------------

class TestNoAdvisoryInGovernanceFiles(unittest.TestCase):

    GOVERNANCE_FILES = [
        ".github/pull_request_template.md",
        ".github/ISSUE_TEMPLATE/bug_report.md",
        ".github/ISSUE_TEMPLATE/feature_request.md",
        ".github/ISSUE_TEMPLATE/scoring_question.md",
        ".github/ISSUE_TEMPLATE/source_request.md",
        "docs/maintainer-policy.md",
        "SECURITY.md",
    ]

    FORBIDDEN_CLAIMS = [
        "buy this stock",
        "sell this stock",
        "recommended company",
        "portfolio allocation",
        "purchase shares",
        "this tool predicts",
        "guaranteed returns",
        "alpha generating",
    ]

    def test_governance_files_no_advisory_claims(self):
        for rel_path in self.GOVERNANCE_FILES:
            content = _read(rel_path).lower()
            for phrase in self.FORBIDDEN_CLAIMS:
                self.assertNotIn(
                    phrase, content,
                    f"Found advisory phrase '{phrase}' in {rel_path}"
                )

    def test_ci_workflow_only_runs_tests(self):
        ci = _read(".github/workflows/tests.yml")
        self.assertIn("python -m unittest discover", ci)
        # Should not call any paid API or external service
        self.assertNotIn("pip install", ci)

    def test_codeowners_uses_correct_account(self):
        codeowners = _read(".github/CODEOWNERS")
        self.assertIn("@forgedynamicsai", codeowners)
        # Should cover safety-critical files
        self.assertIn("skills/", codeowners)
        self.assertIn("DISCLAIMER.md", codeowners)


if __name__ == "__main__":
    unittest.main()
