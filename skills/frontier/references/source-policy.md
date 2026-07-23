# Frontier source policy

Frontier searches four technical lanes for a topic:

## Papers

- **OpenAlex:** broad scholarly discovery and publication metadata.
- **arXiv:** recent preprints, especially in computer science, mathematics, physics, and AI.
- **Semantic Scholar:** discovery, abstracts, related metadata, open-access links, and citation signals.

## Artifacts

- **Hugging Face:** newly created relevant models and model-card records.
- **GitHub:** newly created relevant repositories containing models, tools, harnesses, benchmarks, or implementations.

These are discovery sources, not popularity feeds. Stars, downloads, and likes do not establish technical quality or novelty.

## Company technical publications

The host agent searches the approved official research/engineering domains in `company-sources.md` in parallel with the bundled utility. Only substantive research findings, methods, models, evaluations, harnesses, and technical tools qualify.

A company publication is primary evidence that the organization made a claim. It is not independent validation of that claim.

## Advancement grouping

Papers, company publications, model cards, repositories, and evaluation links describing the same work are grouped into one advancement while retaining every source URL and evidence type.

## Source status

The report must distinguish `ok`, `partial`, `rate-limited`, `unavailable`, and `error` for each lane. Paper status must distinguish `published`, `preprint`, `submitted`, `corrected`, `retracted`, and `unknown` whenever records support it.

## Partial results

A provider timeout, rate limit, malformed response, unavailable host search, or missing company page is nonfatal. The search artifact and final report must record the failure. A failed source must never be represented as having no results.
