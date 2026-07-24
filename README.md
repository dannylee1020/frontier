# Frontier

A portable agent skill for discovering and understanding recent frontier-AI research.

Frontier reports two complementary views:

- Research papers from OpenAlex, arXiv, and Semantic Scholar
- Official technical publications from frontier companies


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

For each topic, Frontier searches the three scholarly providers and the Hugging Face Papers attention feed in parallel with host-native searches of approved company technical domains. It then:

- Filters papers by the requested publication date range
- Deduplicates paper records by DOI, arXiv ID, Semantic Scholar ID, and conservative title matching
- Keeps scholarly evidence and company first-party claims in separate insight lanes
- Preserves Hugging Face momentum separately from publication date and evidence quality
- Produces a concise report with Research Frontier, Company Frontier, connections, sources, and uncertainties

Popularity signals such as Hugging Face feed rank and upvotes are contextual only.

## Search utility

The bundled utility performs deterministic scholarly and Hugging Face Papers discovery:

```bash
python3.12 <skill-directory>/scripts/search.py \
  --query "long-horizon LLM agents" \
  --output /tmp/frontier-results.json
```

Use `--help` for additional search and output options.

Optional environment variables:

- `SEMANTIC_SCHOLAR_API_KEY` — improve Semantic Scholar access
- `OPENALEX_EMAIL` — use the OpenAlex polite pool
- `FRONTIER_USER_AGENT` — customize the request user agent
