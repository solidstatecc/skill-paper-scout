## Description: <br>
Find and verify real research papers through a keyless research index — no login or API key from a normal IP. Find a paper by name or by method, map a field's related work through its citation graph, pull the in-body passages that prove a specific claim, or search GitHub issues/PRs/READMEs for engineering prior art. Grounds every answer in papers the index actually returned — never invents titles or arXiv IDs. Not for general web search, news, or writing the paper for you. <br>

**Status: NOT LISTED.** Council + provenance review pending before any marketplace listing. <br>

## Publisher: <br>
[Solid State](https://solidstate.cc) <br>

### License/Terms of Use: <br>
MIT (intended) — pending listing gate <br>

## Use Case: <br>
For builders, founders, and research-grounded writing agents who need answers backed by real papers, not hallucinated citations. It covers literature finding, related-work mapping, claim verification, engineering prior art, and field tracking. Zero setup from a normal IP; a datacenter or agent host needs the free key (no card). <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: Keyless access is rate-limited per IP per day. <br>
Mitigation: Plenty for interactive work; an optional free `FIRECRAWL_API_KEY` (no card) lifts the ceiling and the script adds it automatically when set. <br>

Risk: A datacenter or agent IP can be flagged as suspicious — the index returns a 403 and refuses keyless access. <br>
Mitigation: Set the free `FIRECRAWL_API_KEY` (no card); the script sends it automatically and the block clears. `search` also degrades to the public arXiv API. <br>
Risk: The body-passage index can return a low-relevance or mismatched passage. <br>
Mitigation: Passages are scored; the skill instructs the agent to treat low scores as unconfirmed and never assert a fact from a weak match. <br>
Risk: The research index could change or be unreachable. <br>
Mitigation: The engine talks plain HTTP (not a vendor MCP), and `search` degrades to the public arXiv API with a stderr banner rather than fabricating. <br>

## Reference(s): <br>
- [Solid State — paper-scout](https://solidstate.cc/skills/paper-scout) <br>
- Firecrawl Research Index (keyless REST: `api.firecrawl.dev/v2/search/research/*`) <br>
- arXiv API (`export.arxiv.org/api/query`) — fallback path <br>

## Skill Output: <br>
**Output Type(s):** [Ranked paper list, paper metadata, scored in-body passages, GitHub prior-art list, JSON] <br>
**Output Format:** [Readable lists with title + arXiv link + score, or `--json` for piping] <br>
**Output Parameters:** [query/id + flags: --k, --from/--to, --authors, --categories, --intent, --mode] <br>
**Other Properties Related to Output:** [Five moves — search, similar, inspect, read, github — over one keyless index.] <br>

## Skill Version(s): <br>
0.1.0 (draft) <br>

## Provenance: <br>
Original Solid State work. The data backend is Firecrawl's public research index, accessed over its documented keyless HTTP API; no Firecrawl code, prompt text, or branding is reproduced. All code, prose, the five-move method framing, the multi-use-case recipes, the backend-agnostic engine, the arXiv fallback, and the low-score verification discipline are written from scratch by Solid State. The upstream `firecrawl/skills` paper-finder inspired the problem, not the implementation. <br>

## Ethical Considerations: <br>
Returns only what the index actually returns; the method forbids inventing papers, titles, or IDs, and flags low-confidence passages as unconfirmed. Respect Firecrawl's and arXiv's terms and rate limits. The skill finds and verifies literature; it does not assess research quality for you. <br>
