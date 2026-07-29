# Frontier workflow

1. Clarify the technical topic, date window, audience, and output mode; default to `brief`.
2. Generate two or three semantic-breadth discovery branches: a precision anchor, a lexical or ontology expansion, and an adjacent mechanism or application only when it adds distinct coverage.
3. Record each branch and its purpose; do not use simple paraphrases or fixed baseline/evaluation/limitations buckets.
4. Run OpenAlex and arXiv concurrently for each branch. When `SEMANTIC_SCHOLAR_API_KEY` is configured, also run Semantic Scholar and serialize its branches to avoid request bursts.
5. Fetch Hugging Face Papers once and locally filter the shared feed against each discovery branch as a separate momentum overlay.
6. In parallel, issue one OR-combined site-restricted query per approved frontier lab and batch organization queries where the host supports it.
7. When `X_BEARER_TOKEN` is configured and X is not opted out, run each discovery branch through official X Recent Search without `from:` restrictions; cap fetched posts globally and preserve branch provenance.
8. Include substantive research, engineering, capability, infrastructure, evaluation, and strategic signals; exclude routine corporate news and marketing.
9. Apply the publication-date boundary to paper records; keep Hugging Face observation dates separately and X's exact recent timestamps separately.
10. Normalize and deduplicate scholarly and momentum paper records by identifiers and conservative title matching.
11. Deduplicate X posts by post/edit-history ID and cluster related posts by canonical links, references, conversations, or conservative text similarity before ranking attention.
12. Rank each paper using the best rank from each distinct scholarly provider; use cross-branch coverage only as a late relevance tie-breaker.
13. Rank company records independently by technical substance, directionality, specificity, and first-party provenance.
14. Rank X clusters by topic relevance, artifact links, author diversity, persistence, and recency-adjusted attention. Do not use attention as credibility.
15. Select candidate advances, findings, lab moves, social discussions, and possible landscape shifts.
16. Run at most three candidate-specific depth queries only when a shortlisted claim lacks baseline, validation, contradiction, or limitation evidence.
17. Attach depth findings to the relevant internal evidence record without treating repeated same-provider matches as corroboration.
18. Analyze papers, company publications, and X trend clusters under their separate evidence contracts.
19. Synthesize related records into `frontier_move` records without merging their evidence authority.
20. Apply the inference ladder: isolated signal, organizational direction, emerging direction, then converged frontier shift.
21. Select no more than three principal shifts, five techniques/findings, three lab/deployment moves, and only material X trend clusters for the default brief.
22. Write a plain-language synthesis focused on what changed, why it matters, and what the audience should update.
23. Audit citations, evidence levels, claim states, source health, uncertainty, baseline support, attention labeling, and momentum labeling.

The bundled utility is deterministic in parsing, date filtering, paper deduplication, scholarly ranking, X post deduplication, and local X clustering. Hugging Face Papers is a global feed and is locally topic-filtered; its ranking and upvotes are context, not proof. X is a broad social-momentum sample, not exhaustive coverage; its engagement metrics are attention context, not proof. Company publication search remains host-native because official sites are heterogeneous. The first-party company lane supplies evidence of organizational claims and actions, not automatic independent validation or market-wide significance.
