# Workflow reference

1. Clarify the technical topic, date window, and output mode; default to `brief`.
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
12. Preserve the detailed evidence record internally.
13. Select no more than five principal advancements for the default brief.
14. Write a plain-language one-page synthesis focused on what changed and why it matters.
15. Audit claims, citations, evidence levels, source health, and uncertainty.
16. Return the brief, or switch to the deep report contract when explicitly requested.

The bundled utility is deterministic in parsing, date filtering, artifact deduplication, and ranking. Network response order is normalized before JSON output is emitted. Concision applies to presentation, not to evidence collection or claim auditing.
