from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / "skills" / "frontier" / "SKILL.md").read_text()
TEMPLATE = (ROOT / "skills" / "frontier" / "assets" / "report-template.md").read_text()
ANALYSIS = (ROOT / "skills" / "frontier" / "references" / "analysis-schema.md").read_text()
REPORT = (ROOT / "skills" / "frontier" / "references" / "report-schema.md").read_text()
SOURCES = (ROOT / "skills" / "frontier" / "references" / "company-sources.md").read_text()
SAFETY = (ROOT / "skills" / "frontier" / "references" / "safety.md").read_text()


class SkillContractTests(unittest.TestCase):
    def test_default_report_is_landscape_first(self) -> None:
        expected_sections = (
            "## Bottom Line",
            "## Frontier Shifts",
            "## New Techniques and Findings",
            "## Lab and Deployment Moves",
            "## Landscape Direction",
            "## Implications",
            "## Watchlist and Caveats",
        )
        for section in expected_sections:
            self.assertIn(section, TEMPLATE)
            self.assertIn(section, REPORT)

        self.assertNotIn("## Research Frontier", TEMPLATE)
        self.assertNotIn("## Company Frontier", TEMPLATE)

    def test_frontier_move_contract_has_required_fields_and_types(self) -> None:
        for field in (
            "Previous baseline",
            "What changed",
            "Novelty",
            "Supporting evidence",
            "Landscape effect",
            "Practical readiness",
            "Confidence",
        ):
            self.assertIn(field, ANALYSIS)
            self.assertIn(field.lower(), SKILL.lower())

        for move_type in (
            "research_advance",
            "engineering_advance",
            "evaluation_finding",
            "capability_release",
            "infrastructure_move",
            "strategic_signal",
        ):
            self.assertIn(move_type, ANALYSIS)
            self.assertIn(move_type, SKILL)

    def test_company_activity_is_broader_than_research_but_attributed(self) -> None:
        for publication_type in (
            "capability_release",
            "infrastructure",
            "evaluation",
            "strategic_signal",
        ):
            self.assertIn(publication_type, SOURCES)
            self.assertIn(publication_type, ANALYSIS)

        self.assertIn("first-party", ANALYSIS)
        self.assertIn("independent evaluation", SAFETY)
        self.assertIn("industry-wide direction", SAFETY)

    def test_evidence_safeguards_remain_explicit(self) -> None:
        self.assertIn("prior baseline", SKILL.lower())
        self.assertIn("not established", SKILL)
        self.assertIn("momentum context", SKILL.lower())
        self.assertIn("source failures", SKILL.lower())
        self.assertIn("independently corroborated", ANALYSIS)


if __name__ == "__main__":
    unittest.main()
