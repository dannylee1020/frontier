# Frontier

A portable agent skill for discovering and understanding recent frontier-AI advances.

Frontier searches:

- Research papers
- Official technical publications
- Hugging Face models and model cards
- Relevant GitHub repositories

It combines related findings into a structured, evidence-grounded report.

## Supported agents

- Claude Code: `/frontier`
- Codex: `$frontier`
- OpenCode: native skill activation

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/dannylee1020/frontier/main/scripts/install.sh | sh
```

The installer requires `curl`, `tar`, and Python 3.12 or newer.

## Search behavior

For each topic, Frontier searches papers, official technical publications, Hugging Face, and GitHub in parallel. It then:

- Filters results by the requested date range
- Removes duplicates and groups related findings
- Ranks results by relevance, evidence, and authority
- Produces one structured report with sources and uncertainties

Popularity signals such as stars, downloads, and likes are not treated as technical evidence.

## Search utility

The bundled utility performs deterministic paper, model, and repository discovery:

```bash
python3.12 <skill-directory>/scripts/search.py \
  --query "long-horizon LLM agents" \
  --output /tmp/frontier-results.json
```

Use `--help` for additional search and output options.

Optional environment variables:

- `SEMANTIC_SCHOLAR_API_KEY` — improve Semantic Scholar access
- `OPENALEX_EMAIL` — use the OpenAlex polite pool
- `GITHUB_TOKEN` — improve GitHub API rate limits
- `FRONTIER_USER_AGENT` — customize the request user agent
