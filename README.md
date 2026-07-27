# Frontier

Frontier is an agent skill for keeping up with recent AI research and technical work from leading frontier labs.

It searches papers and publications from universities, research team and frontier labs, checks what actually changed, and returns a short report with sources and caveats.

## What you get

The default report is kept to one page:

- **The short version** — the main finding and its strongest caveat
- **What changed** — up to three supported changes, with evidence
- **Also worth knowing** — useful research, deployment updates, and evidence that points the other way
- **What to watch** — results that could change the current conclusion
- **Sources and limits** — where Frontier looked and what it could not verify

## Supported agents

- Claude Code: `/frontier`
- Codex: `$frontier`
- OpenCode: native skill activation
- Pi: native skill activation

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/dannylee1020/frontier/main/scripts/install.sh | sh
```

You need `curl`, `tar`, and Python 3.12 or newer. Running the installer again replaces the existing Frontier installation.

Use `--agent pi` to install for Pi. Pi, Codex, and OpenCode use the same Agent Skills directory.

## How the research works

Frontier starts with two or three genuinely different search angles. It uses the same angles across the paper sources, then searches each lab with one combined query. This widens the search without filling it with minor rewrites of the same phrase.

The default paper sources are OpenAlex and arXiv. Set `SEMANTIC_SCHOLAR_API_KEY` to add Semantic Scholar. Frontier also checks Hugging Face Papers to see which papers are getting attention, but does not treat rank or upvotes as proof.

Frontier then:

- Keeps papers inside the requested date range
- Merges duplicates by DOI, arXiv ID, Semantic Scholar ID, and careful title matching
- Stops repeated matches from one source from counting as independent support
- Runs a focused follow-up only when a promising finding needs earlier context, outside validation, contradictory evidence, or known limits
- Keeps paper evidence separate from first-party lab claims
- Reports source failures and missing evidence instead of treating them as zero results

Official lab publications show what an organization reported, released, or did. They do not independently prove a performance claim or establish an industry-wide trend.

## Search utility

The bundled utility searches papers and the Hugging Face Papers feed:

```bash
python3.12 <skill-directory>/scripts/search.py \
  --query "long-horizon agents" \
  --query "memory-augmented agents" \
  --query "context compression" \
  --output /tmp/frontier-results.json
```

Use `--help` to see the available search and output options.

Lab-site search stays with the host agent because each site works differently.

Progress is written to `stderr`. Interactive terminals show one live status line, followed by a short receipt with matches by source, unique papers in the date window, the shortlist size, and any source failures. Full errors stay in the JSON output.

Optional environment variables:

- `SEMANTIC_SCHOLAR_API_KEY` — add Semantic Scholar
- `OPENALEX_EMAIL` — use the OpenAlex polite pool
- `FRONTIER_USER_AGENT` — set a custom request user agent
