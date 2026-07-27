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
STYLE = (ROOT / "skills" / "frontier" / "references" / "writing-style.md").read_text()


class SkillContractTests(unittest.TestCase):
    def test_default_report_is_a_one_page_technical_note(self) -> None:
        expected_sections = (
            "## The short version",
            "## What changed",
            "## Also worth knowing",
            "## What to watch",
            "## Sources and limits",
        )
        for section in expected_sections:
            self.assertIn(section, TEMPLATE)
            self.assertIn(section, REPORT)

        old_sections = (
            "## Bottom Line",
            "## Frontier Shifts",
            "## New Techniques and Findings",
            "## Lab and Deployment Moves",
            "## Landscape Direction",
            "## Implications",
            "## Watchlist and Caveats",
        )
        default_report = REPORT.split("## Deep report", maxsplit=1)[0]
        for section in old_sections:
            self.assertNotIn(section, TEMPLATE)
            self.assertNotIn(section, default_report)

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

    def test_provider_coverage_is_part_of_the_default_report(self) -> None:
        self.assertIn("**Coverage:**", TEMPLATE)
        self.assertIn("**Limits:**", TEMPLATE)
        self.assertIn("source coverage", SKILL.lower())
        self.assertIn("Omit unconfigured optional providers", REPORT)
        self.assertIn(
            "Use Semantic Scholar only when `SEMANTIC_SCHOLAR_API_KEY` is configured",
            SKILL,
        )
        self.assertIn("An unconfigured optional provider is omitted", SKILL)

    def test_default_writing_contract_is_plain_and_bounded(self) -> None:
        self.assertIn("writing-style.md", SKILL)
        self.assertIn("writing-style.md", REPORT)
        self.assertIn("Start with the finding", STYLE)
        self.assertIn("one claim in each paragraph", STYLE)
        self.assertIn("Do not force", STYLE)
        self.assertIn("no more than three supported changes", TEMPLATE)
        self.assertIn("no more than five items", TEMPLATE)
        self.assertIn("no more than three items", TEMPLATE)
        for audience in ("**Engineers:**", "**Founders:**", "**Investors:**"):
            self.assertNotIn(audience, TEMPLATE)

    def test_evidence_safeguards_remain_explicit(self) -> None:
        self.assertIn("prior baseline", SKILL.lower())
        self.assertIn("not established", SKILL)
        self.assertIn("momentum context", SKILL.lower())
        self.assertIn("source failures", SKILL.lower())
        self.assertIn("independently corroborated", ANALYSIS)

    def test_query_fanout_prioritizes_semantic_breadth_then_depth(self) -> None:
        for branch in (
            "Precision anchor",
            "Lexical or ontology expansion",
            "Adjacent mechanism or application",
        ):
            self.assertIn(branch, SKILL)
        self.assertIn("Do not pad the portfolio with paraphrases", SKILL)
        self.assertIn("no more than three targeted", SKILL)
        self.assertIn("are not independent", SKILL)


if __name__ == "__main__":
    unittest.main()
