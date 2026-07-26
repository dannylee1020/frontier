# Frontier source policy

Frontier uses three evidence classes:

1. **Scholarly research** — papers and preprints that drive technical understanding.
2. **Official lab activity** — first-party research, engineering, releases, infrastructure, evaluations, and strategic technical signals.
3. **Momentum overlay** — attention context for papers, currently supplied by Hugging Face Papers.

A `frontier_move` is a synthesis layer, not a source class. It may connect evidence from multiple classes while preserving their different authority and validation semantics.

## Scholarly research

Canonical scholarly providers:

- **OpenAlex:** broad scholarly discovery and publication metadata.
- **arXiv:** recent preprints, especially in computer science, mathematics, physics, and AI.
- **Semantic Scholar:** discovery, abstracts, related metadata, open-access links, and citation signals.

Hugging Face Papers is a momentum overlay for papers. Its rank, upvotes, and feed submission date do not establish technical quality, novelty, or scholarly corroboration. Preserve the paper's publication date separately from `momentum_observed_at`.

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
- **Company record:** grounded in an official technical publication; label the organization, publication type, authority, and claim state.
- **Frontier move:** a synthesis that states its baseline, delta, evidence, landscape effect, readiness, and confidence.
- **External validation:** an independent evaluation or reproduction; do not infer it from an official source.
- **Adoption:** evidence that people or organizations use the capability; do not infer it from availability.

## Inclusion and exclusion

Include technical material that changes understanding of capability, method, evaluation, engineering practice, deployment, infrastructure, or lab direction.

Exclude funding, hiring, generic partnerships, generic thought leadership, promotional claims without technical detail, and routine availability notices unless they contain a material capability or infrastructure change.

## Source status

The report must distinguish `ok`, `partial`, `rate-limited`, `unavailable`, and `error` for each provider or evidence lane. Paper status must distinguish `published`, `preprint`, `submitted`, `corrected`, `retracted`, and `unknown` whenever records support it.

## Partial results

A provider timeout, rate limit, malformed response, unavailable host search, or missing company page is nonfatal. The search artifact and final report must record the failure. A failed source must never be represented as having no results.
