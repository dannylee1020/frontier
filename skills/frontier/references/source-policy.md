# Frontier source policy

Frontier uses four evidence classes:

1. **Scholarly research** — papers and preprints that drive technical understanding.
2. **Official lab activity** — first-party research, engineering, releases, infrastructure, evaluations, and strategic technical signals.
3. **Momentum overlay** — attention context for papers, currently supplied by Hugging Face Papers.
4. **X social momentum** — broad topic retrieval from official X Recent Search, used to identify attention, discussion, and terminology rather than to validate technical claims.

A `frontier_move` is a synthesis layer, not a source class. It may connect evidence from multiple classes while preserving their different authority and validation semantics.

## Scholarly research

Default scholarly providers:

- **OpenAlex:** broad scholarly discovery and publication metadata.
- **arXiv:** recent preprints, especially in computer science, mathematics, physics, and AI.

Optional scholarly provider:

- **Semantic Scholar:** authenticated discovery, abstracts, related metadata, open-access links, and citation signals. Enable it only by setting `SEMANTIC_SCHOLAR_API_KEY`; omit it from collection and coverage when unconfigured.

Hugging Face Papers is a momentum overlay for papers. Its rank, upvotes, and feed submission date do not establish technical quality, novelty, or scholarly corroboration. Preserve the paper's publication date separately from `momentum_observed_at`.

## Configuration and credential boundary

The CLI loads supported provider variables internally from `~/.frontier/.env` or `$FRONTIER_HOME/.env`; it does not source the file in the invoking shell. Existing process environment variables take precedence. The agent must not read, print, or source this file. Missing optional credentials omit their providers. When `X_BEARER_TOKEN` is configured, X is enabled by default unless `FRONTIER_X_ENABLED=false`.

## X social momentum

X is a configuration-driven lane using the official X API v2 Recent Search endpoint. It searches each discovery branch broadly, excludes native retweets, and does not restrict results to frontier-lab accounts. Recent Search covers at most seven days; record the exact effective timestamps and the global fetched-post cap. The cap bounds fetched posts, while author expansions can have separate resource billing; monitor the X Developer Console. X is omitted when no token is configured or `FRONTIER_X_ENABLED=false`.

Normalize posts by post ID and edit-history IDs, preserve author identity as known or unknown, retain linked URLs and public metrics, and cluster related posts before synthesis. Views, likes, reposts, replies, bookmarks, impressions, recency, and follower counts measure attention or reach—not credibility, expertise, truth, consensus, adoption, or independent validation. A single high-reach origin is a viral post, not a trend. Multiple posts from one conversation or quoted chain are not independent corroboration.

The optional [x-sources.json](x-sources.json) registry annotates known official, author, practitioner, or commentator accounts. It never restricts retrieval and never upgrades a claim state. Canonical artifacts linked from X must be inspected separately before a trend can be described as technically supported.

## Official lab activity

The host agent searches approved official technical domains in [company-sources.md](company-sources.md) in parallel with the bundled paper utility. Include a publication when it materially reports or reveals:

- Research advance or empirical finding
- Engineering advance in training, inference, serving, evaluation, or operations
- Capability or model release
- Infrastructure or developer-platform move
- Evaluation, safety, or deployment finding
- Repeated technical priority or strategic signal

A company publication is primary evidence that the organization made a claim or took an action. It is not independent validation of performance or general truth, and it does not establish an industry shift by itself.

## Separate evidence semantics

- **Research record:** grounded in a scholarly paper; may be labeled published, preprint, abstract-level, full-text, or momentum-discovered.
- **X trend record:** grounded in normalized and clustered X posts; label momentum, trend type, author diversity, linked artifacts, truncation, and the unresolved evidence state separately.
- **Company record:** grounded in an official technical publication; label the organization, publication type, authority, and claim state.
- **Frontier move:** a synthesis that states its baseline, delta, evidence, landscape effect, readiness, and confidence.
- **External validation:** an independent evaluation or reproduction; do not infer it from an official source.
- **Adoption:** evidence that people or organizations use the capability; do not infer it from availability.

## Inclusion and exclusion

Include technical material that changes understanding of capability, method, evaluation, engineering practice, deployment, infrastructure, or lab direction.

Exclude funding, hiring, generic partnerships, generic thought leadership, promotional claims without technical detail, and routine availability notices unless they contain a material capability or infrastructure change.

## Source status

The report must distinguish `ok`, `partial`, `rate-limited`, `unavailable`, and `error` for each enabled provider or evidence lane. An unconfigured optional provider is omitted rather than marked unavailable. Paper status must distinguish `published`, `preprint`, `submitted`, `corrected`, `retracted`, and `unknown` whenever records support it. X is omitted when disabled; when enabled, report its status, exact effective window, fetched-post cap, truncation, and any partial or unavailable branch.

## Partial results

A provider timeout, rate limit, malformed response, unavailable host search, or missing company page is nonfatal. The search artifact and final report must record the failure. A failed source must never be represented as having no results. X attention must never be represented as technical evidence merely because a post is popular.
