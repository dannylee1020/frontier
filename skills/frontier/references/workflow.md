# Frontier workflow

1. Clarify the technical topic, date window, audience, and output mode; default to `brief`.
2. Generate at most three query variants and record them for reproducibility.
3. Run OpenAlex, arXiv, and Semantic Scholar concurrently for scholarly discovery.
4. Run Hugging Face Papers as a separate momentum overlay for the same queries.
5. In parallel, search approved frontier-lab technical domains with host-native site-restricted search.
6. Include substantive research, engineering, capability, infrastructure, evaluation, and strategic signals; exclude routine corporate news and marketing.
7. Apply the publication-date boundary to paper records; keep Hugging Face observation dates separately.
8. Normalize and deduplicate scholarly and momentum paper records by identifiers and conservative title matching.
9. Rank research records by relevance, evidence, novelty potential, and recency; use Hugging Face momentum only as a late signal.
10. Rank company records independently by technical substance, directionality, specificity, and first-party provenance.
11. Select candidate advances, findings, lab moves, and possible landscape shifts.
12. For shortlisted novelty or shift claims, establish a prior baseline through cited prior work or focused historical lookup.
13. Analyze papers and company publications under their separate evidence contracts.
14. Synthesize related records into `frontier_move` records without merging their evidence authority.
15. Apply the inference ladder: isolated signal, organizational direction, emerging direction, then converged frontier shift.
16. Select no more than three principal shifts, five techniques/findings, and three lab/deployment moves for the default brief.
17. Write a plain-language synthesis focused on what changed, why it matters, and what the audience should update.
18. Audit citations, evidence levels, claim states, source health, uncertainty, baseline support, and momentum labeling.

The bundled utility is deterministic in parsing, date filtering, paper deduplication, and scholarly ranking. Hugging Face Papers is a global feed and is locally topic-filtered; its ranking and upvotes are context, not proof. Company publication search remains host-native because official sites are heterogeneous. The first-party company lane supplies evidence of organizational claims and actions, not automatic independent validation or market-wide significance.
