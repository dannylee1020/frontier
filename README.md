# Frontier

A portable agent skill for tracking recent frontier-AI research and technical activity, identifying the advances that matter, and explaining how the AI landscape is changing.

Frontier is designed for founders, engineers, investors, researchers, and technical leaders who need to keep their mental models current—not merely collect AI headlines.

## Why

> **Track advances, not headlines.**

AI is advancing rapidly, making it increasingly difficult to keep pace with frontier developments.

Frontier is research-led technical intelligence. It starts with new scholarly research, techniques, evaluations, and findings, then adds official frontier-lab activity to show what is being engineered, released, deployed, and prioritized.

Its output is organized around:

- **Frontier shifts** — material changes relative to a prior baseline
- **New techniques and findings** — novel research and technical results
- **Lab and deployment moves** — substantive first-party engineering, capability, infrastructure, evaluation, and strategic signals
- **Landscape direction** — convergence, divergence, and emerging priorities
- **Implications** — what engineers, founders, and investors should reconsider

## Supported agents

- Claude Code: `/frontier`
- Codex: `$frontier`
- OpenCode: native skill activation
- Pi: native skill activation


## Install

```bash
curl -fsSL https://raw.githubusercontent.com/dannylee1020/frontier/main/scripts/install.sh | sh
```

The installer requires `curl`, `tar`, and Python 3.12 or newer. Re-running it replaces existing Frontier installations with the downloaded version. Use `--agent pi` for Pi; Pi, Codex, and OpenCode share the Agent Skills destination.

## Evidence model

Frontier combines three evidence classes without collapsing their meaning:

- Scholarly research from OpenAlex and arXiv drives technical understanding. Semantic Scholar can supplement discovery when authenticated access is configured.
- Official frontier-lab publications reveal first-party research, engineering practice, capability releases, infrastructure investment, evaluations, and organizational direction.
- Hugging Face Papers provides a paper-attention overlay only; rank and upvotes are momentum context, not scientific validation.

A company publication establishes what an organization claimed or did. It does not independently validate performance or establish an industry-wide trend by itself. Frontier records source failures, evidence levels, limitations, and uncertainty.

## Search behavior

For each topic, Frontier generates two or three semantic-breadth discovery branches, searches the configured scholarly providers with provider-aware concurrency, and filters one shared Hugging Face Papers feed. OpenAlex and arXiv are enabled by default; Semantic Scholar joins the search only when `SEMANTIC_SCHOLAR_API_KEY` is set. In parallel, Frontier batches one OR-combined search for each approved frontier lab. It then:

- Filters papers by the requested publication date range
- Deduplicates paper records by DOI, arXiv ID, Semantic Scholar ID, and conservative title matching
- Uses the best rank from each scholarly provider without treating repeated query matches as corroboration
- Runs focused depth searches only when a shortlisted claim lacks baseline, validation, contradiction, or limitation evidence
- Establishes a prior baseline before claiming novelty when possible
- Synthesizes related evidence into frontier shifts without merging research and first-party authority
- Separates momentum from publication date and evidence quality
- Produces a concise report focused on what changed, why it matters, and what to watch

## Search utility

The bundled utility performs deterministic scholarly and Hugging Face Papers discovery:

```bash
python3.12 <skill-directory>/scripts/search.py \
  --query "long-horizon agents" \
  --query "memory-augmented agents" \
  --query "context compression" \
  --output /tmp/frontier-results.json
```

Use `--help` for additional search and output options.

The utility searches scholarly and momentum sources only. Official company publication discovery remains host-native because those sites have heterogeneous search and page structures.

Progress stays on `stderr`: interactive terminals receive one in-place status line, while captured output receives one compact completion and source-health line. Detailed provider failures remain in the JSON artifact.

Optional environment variables:

- `SEMANTIC_SCHOLAR_API_KEY` — enable optional Semantic Scholar discovery
- `OPENALEX_EMAIL` — use the OpenAlex polite pool
- `FRONTIER_USER_AGENT` — customize the request user agent
