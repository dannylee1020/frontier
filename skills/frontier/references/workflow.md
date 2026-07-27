# Frontier workflow

1. Clarify the technical topic, date window, audience, and output mode; default to `brief`.
2. Generate two or three semantic-breadth discovery branches: a precision anchor, a lexical or ontology expansion, and an adjacent mechanism or application only when it adds distinct coverage.
3. Record each branch and its purpose; do not use simple paraphrases or fixed baseline/evaluation/limitations buckets.
4. Run OpenAlex and arXiv concurrently for each branch. When `SEMANTIC_SCHOLAR_API_KEY` is configured, also run Semantic Scholar and serialize its branches to avoid request bursts.
5. Fetch Hugging Face Papers once and locally filter the shared feed against each discovery branch as a separate momentum overlay.
6. In parallel, issue one OR-combined site-restricted query per approved frontier lab and batch organization queries where the host supports it.
7. Include substantive research, engineering, capability, infrastructure, evaluation, and strategic signals; exclude routine corporate news and marketing.
8. Apply the publication-date boundary to paper records; keep Hugging Face observation dates separately.
9. Normalize and deduplicate scholarly and momentum paper records by identifiers and conservative title matching.
10. Rank each paper using the best rank from each distinct scholarly provider; use cross-branch coverage only as a late relevance tie-breaker.
11. Rank company records independently by technical substance, directionality, specificity, and first-party provenance.
12. Select candidate advances, findings, lab moves, and possible landscape shifts.
13. Run at most three candidate-specific depth queries only when a shortlisted claim lacks baseline, validation, contradiction, or limitation evidence.
14. Attach depth findings to the relevant internal evidence record without treating repeated same-provider matches as corroboration.
15. Analyze papers and company publications under their separate evidence contracts.
16. Synthesize related records into `frontier_move` records without merging their evidence authority.
17. Apply the inference ladder: isolated signal, organizational direction, emerging direction, then converged frontier shift.
18. Select no more than three principal shifts, five techniques/findings, and three lab/deployment moves for the default brief.
19. Write a plain-language synthesis focused on what changed, why it matters, and what the audience should update.
20. Audit citations, evidence levels, claim states, source health, uncertainty, baseline support, and momentum labeling.

The bundled utility is deterministic in parsing, date filtering, paper deduplication, and scholarly ranking. Hugging Face Papers is a global feed and is locally topic-filtered; its ranking and upvotes are context, not proof. Company publication search remains host-native because official sites are heterogeneous. The first-party company lane supplies evidence of organizational claims and actions, not automatic independent validation or market-wide significance.
