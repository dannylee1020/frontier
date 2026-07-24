# Frontier workflow

1. Clarify the technical topic, date window, and output mode; default to `brief`.
2. Generate at most three query variants.
3. Run OpenAlex, arXiv, and Semantic Scholar concurrently for scholarly discovery.
4. Run Hugging Face Papers as a separate momentum overlay for the same queries.
5. In parallel, search the approved company technical domains with host-native site-restricted search.
6. Apply the publication-date boundary to paper records; keep Hugging Face observation dates separately.
7. Normalize and deduplicate scholarly and momentum paper records by identifiers and conservative title matching.
8. Rank Research Frontier papers by scholarly evidence and use Hugging Face momentum only as a late signal.
9. Rank Company Frontier publications independently by technical substance, relevance, and first-party provenance.
10. Select a diverse analysis set for each lane.
11. Analyze papers and company publications under their separate evidence contracts.
12. Link related paper and company findings thematically without merging their evidence.
13. Preserve the detailed evidence record internally.
14. Select no more than three principal items per lane for the default brief.
15. Write a plain-language synthesis focused on what changed and why it matters.
16. Audit claims, citations, evidence levels, source health, uncertainty, and momentum labeling.

The bundled utility is deterministic in parsing, date filtering, paper deduplication, and scholarly ranking. Hugging Face Papers is a global feed and is locally topic-filtered; its ranking and upvotes are context, not proof. Network response order is normalized before JSON output is emitted. Company publication search remains host-native because official sites are heterogeneous.
