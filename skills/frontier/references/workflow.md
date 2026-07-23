# Workflow reference

1. Clarify the technical topic, date window, and desired depth.
2. Generate at most three query variants.
3. Run paper and artifact search concurrently with the bundled utility.
4. In parallel, search the approved company technical domains with host-native site-restricted search.
5. Apply the date boundary to papers, models, and repositories.
6. Normalize source-specific records while retaining provenance and authority.
7. Deduplicate papers, models, repositories, and related source records.
8. Rank candidates using reciprocal-rank fusion, relevance, recency, and authority as separate signals.
9. Select a diverse analysis set.
10. Analyze papers, model cards, repositories, and company posts in parallel when native subagents exist.
11. Group related records into technical advancements.
12. Consolidate one structured report in the parent agent.
13. Audit claims, citations, evidence levels, source health, and uncertainty.
14. Return the report with a reproducibility log.

The bundled utility is deterministic in parsing, date filtering, artifact deduplication, and ranking. Network response order is normalized before JSON output is emitted.
