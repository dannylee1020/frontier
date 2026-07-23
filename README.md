# Frontier

`frontier` is a portable agent skill for finding and synthesizing recent frontier-AI technological advancements.

For a topic, it searches four technical lanes:

- **Research papers:** OpenAlex, arXiv, and Semantic Scholar
- **Hugging Face:** relevant newly created models and their model-card records
- **GitHub:** relevant newly created repositories
- **Official technical publications:** research and engineering posts from the approved company registry

The host agent consolidates related records into one advancement report. It does not track general AI news, social trends, or every package/repository release.

## Requirements

- Python 3.12 or newer
- No third-party Python packages

## Supported runtimes

- Claude Code: `/frontier`
- Codex: `$frontier`
- OpenCode: native skill activation or implicit matching

## Install

Directly from GitHub with curl:

```bash
curl -fsSL https://raw.githubusercontent.com/dannylee1020/frontier/main/scripts/install.sh | sh
```

Pass installer options after `--`:

```bash
curl -fsSL https://raw.githubusercontent.com/dannylee1020/frontier/main/scripts/install.sh \
  | sh -s -- --agent codex --force
```

The bootstrap requires `curl`, `tar`, and `python3.12`. It downloads a temporary GitHub archive, runs the standard installer, and removes the temporary files.

Override the repository or ref when testing a fork or tag:

```bash
curl -fsSL https://raw.githubusercontent.com/dannylee1020/frontier/main/scripts/install.sh \
  | FRONTIER_REPOSITORY=owner/repository FRONTIER_REF=main sh
```

From a local checkout:

```bash
python3.12 scripts/install.py --agent all
```

Preview installation:

```bash
python3.12 scripts/install.py --agent all --dry-run
```

Replace an existing copy explicitly:

```bash
python3.12 scripts/install.py --agent all --force
```

## Search utility

The bundled utility searches papers, Hugging Face models, and GitHub repositories concurrently:

```bash
python3.12 skills/frontier/scripts/search.py \
  --query "long-horizon LLM agents" \
  --query "agent memory and tool use" \
  --since 2025-12-01 \
  --until 2026-03-01 \
  --candidate-limit 30 \
  --artifact-limit 20 \
  --output /tmp/frontier-results.json
```

Optional environment variables:

- `SEMANTIC_SCHOLAR_API_KEY` for higher Semantic Scholar reliability
- `OPENALEX_EMAIL` for the OpenAlex polite pool
- `GITHUB_TOKEN` for higher GitHub API reliability
- `FRONTIER_USER_AGENT` to identify the client

No credentials are required for the default workflow.

Official company publications are searched by the host agent with site-restricted web search. See [`company-sources.md`](skills/frontier/references/company-sources.md).

## Search behavior

1. Query variants are sent to all configured paper and artifact adapters concurrently.
2. Results outside the requested date window are removed.
3. Paper and artifact records are normalized separately.
4. Paper duplicates merge by DOI, arXiv ID, Semantic Scholar ID, or conservative title/author/year matching.
5. Model duplicates merge by Hugging Face model identifier; repository duplicates merge by GitHub full name.
6. Papers and artifacts are ranked with provider-independent reciprocal-rank fusion.
7. Authority is preserved separately from relevance. Stars, downloads, and likes are context only.
8. The host agent searches approved company technical domains in parallel and groups related papers, posts, models, and repositories into unified advancements.
9. The parent agent performs the final claim, citation, and evidence audit.

The default paper evidence boundary is abstract-level. Model cards, repository READMEs, and company pages must be inspected before making detailed technical claims.

## Official organizations

Anthropic, OpenAI, Google DeepMind, Meta, Microsoft, NVIDIA, Kimi/Moonshot AI, Qwen, GLM/Z.ai, and DeepSeek.

## Development checks

```bash
python3.12 -m compileall skills/frontier/scripts scripts
python3.12 -m unittest discover -s tests -v
python3.12 skills/frontier/scripts/search.py --help
```

## Scope

Included: OpenAlex, arXiv, Semantic Scholar, Hugging Face model discovery, GitHub repository discovery, approved company technical publications, standard-library Python, structured JSON, portable `SKILL.md`, and installer.

Deferred: general news, social sources, package-release monitoring, Crossref, PDF extraction, persistent caching, database storage, hosted services, and direct LLM API integration.
