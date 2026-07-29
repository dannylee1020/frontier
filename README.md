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

Install Frontier directly with curl:

```sh
curl -fsSL https://raw.githubusercontent.com/dannylee1020/frontier/main/scripts/install.sh | sh
```

Frontier requires Python 3.12 or newer.

## How the research works

Frontier starts with two or three genuinely different search angles. It uses the same angles across the paper sources, then searches each lab with one combined query. This widens the search without filling it with minor rewrites of the same phrase.

The default paper sources are OpenAlex and arXiv. Hugging Face Papers adds paper-attention context without counting as scholarly validation. Semantic Scholar is optional.

When enabled, X searches each topic angle through the official Recent Search API, covering at most seven days. X trends describe attention, not technical validation. See [Search Posts](https://docs.x.com/x-api/posts/search/introduction) and [pricing](https://docs.x.com/x-api/getting-started/pricing).

Frontier then:

- Keeps papers inside the requested date range
- Merges duplicates by DOI, arXiv ID, Semantic Scholar ID, and careful title matching
- Stops repeated matches from one source from counting as independent support
- Runs a focused follow-up only when a promising finding needs earlier context, outside validation, contradictory evidence, or known limits
- Keeps paper evidence separate from first-party lab claims
- Reports source failures and missing evidence instead of treating them as zero results

Official lab publications show what an organization reported, released, or did. They do not independently prove a performance claim or establish an industry-wide trend.


## Optional providers

### X

Private configuration (`~/.frontier/.env`):

```dotenv
X_BEARER_TOKEN=<token from the X Developer Console>
# Optional: FRONTIER_X_ENABLED=false
```

Once configured, X is included by default. To opt out for a search, use the Frontier-specific `FRONTIER_X_ENABLED=false` setting. X retrieval is pay-per-use and limited to seven days. Its metrics measure attention, not credibility.

### Semantic Scholar

```dotenv
SEMANTIC_SCHOLAR_API_KEY=<key>
```

Ask your agent to include Semantic Scholar when you want its additional scholarly metadata.

Frontier loads `.env` internally; do not paste credentials into chat or ask the agent to display the file. Existing environment variables take precedence. `FRONTIER_HOME` can override the default Frontier home.

