---
name: paper-scout
version: 0.1.0
description: >-
  Find and verify real research papers through a keyless research index — no login or API key from a normal IP. Use for any literature task: find a paper by name or by method, map a field's related work through its citation graph, pull the in-body passages that prove a specific claim, or search GitHub issues/PRs/READMEs for engineering prior art. Triggers include "find the paper that", "papers on X", "related work for", "what does X cite or compare against", "has anyone published on", "verify this citation", "is this claim real", "prior art for", "build a reading list on", "catch me up on <field>". Grounds every answer in papers the index actually returns — never invents titles or arXiv IDs. Not for general web search, news, or writing the paper for you; this finds, expands, and verifies the literature.
homepage: https://solidstate.cc/skills/paper-scout
metadata:
  openclaw:
    emoji: "🔭"
    requires:
      bins: ["python3"]
      env: []
    optionalEnv: ["FIRECRAWL_API_KEY"]
    install:
      - id: python-brew
        kind: brew
        formula: python
        bins: ["python3"]
        label: "Install Python (brew)"
---

# Paper Scout

Agents hallucinate citations. This one reads the papers first.

Paper Scout finds the work that answers a research question, then proves it.

It searches a keyless index of millions of arXiv papers, plus GitHub artifacts.

No login. The index answers raw HTTP for free. A clean IP needs no key — a datacenter or agent IP may.

Cite the literature. Not the vibe.

## What you get

One script, `scripts/scout.py`. Stdlib Python. Five moves over the same keyless index.

```bash
python3 {baseDir}/scripts/scout.py selftest
```

That makes one keyless call and prints the paper it found. If it answers, you're done setting up. There is nothing to log into.

A free key lifts the limits — and clears the block if your IP is flagged. See Notes.

## The five moves, and what each is for

**search** — semantic search over abstracts. The first move for almost any query.

```bash
python3 {baseDir}/scripts/scout.py search "training-free detection of AI-generated text" --k 10
```

Thin or all-alike results mean re-frame, not give up. Try the rival method, the dataset name, the sibling field. Filters: `--from`/`--to` (YYYY-MM-DD), `--authors`, `--categories cs.LG`.

**similar** — turn one good hit into the rest of its family. The move semantic search can't make.

```bash
python3 {baseDir}/scripts/scout.py similar arxiv:1706.03762 --intent "efficient attention" --mode similar --k 15
```

`--mode similar` → niche siblings. `citers` → who builds on it. `references` → what it builds on or compares against.

**inspect** — canonical metadata for one paper. Title, authors, categories, dates, ids.

```bash
python3 {baseDir}/scripts/scout.py inspect arxiv:1706.03762
```

Use it to confirm what an id resolves to before you cite it.

**read** — the in-body passages that answer one question. This is how you verify.

```bash
python3 {baseDir}/scripts/scout.py read arxiv:2305.17359 "what datasets is the method evaluated on" --k 4
```

Settle a single load-bearing doubt: a score actually reported, a method actually used, an affiliation. Not on everything — on the fact a claim rests on.

**github** — issues, PRs, and READMEs. Engineering prior art, not papers.

```bash
python3 {baseDir}/scripts/scout.py github "flash attention int8 kv cache" --k 10
```

Where the bug was hit, the design was argued, the trick was shipped. Before you build, check who already did.

Every move takes `--json` for piping into the next step.

## Match the move to the job

There is no fixed recipe. Read the question, pick the path.

- **Named paper** ("the Qwen3 report") → one `search`. Done. The only case that wants exactly one paper.
- **Paper by method** ("the one that introduced X") → `search` for the best hit, then `similar` to keep its neighbours. Don't narrow to the single match.
- **A family** ("alternatives to Adam", "benchmarks for Y") → the answer is a set. `similar --mode similar` off several strong anchors, re-seed from new hits.
- **Papers that use property P** → start at P's defining paper, expand by `citers`/`references`, then `read` a candidate to confirm it actually uses P.
- **Best on a benchmark / largest / most used** → the ranking lives on the web, not in an abstract. Find the leaderboard first, then `search` each top entry back into a paper.
- **From an org / by an author** → topical match isn't enough. `inspect` or `read` to verify the affiliation before you keep it.
- **What does X compare against** → it's inside X. `read X "what does it benchmark against"` or `similar X --mode references`.

## Use it for

The same index does more than find one paper.

- **Map a field.** Seed → `similar --mode similar` → a ranked reading set. The related-work section, the lit review, the "catch me up on <field>" — built from real papers, not memory.
- **Ground a claim.** Before a draft asserts "method X beats Y," `read` the paper for the number. Verified or it doesn't ship. This is the anti-hallucination move for any writing agent.
- **Find prior art.** `github` before you build. Someone hit your bug in an issue, or argued your design in a PR. Borrow the answer.
- **Scan what's new.** `search "<topic>" --from 2026-01-01` to see only recent work. Run it weekly and you have a field tracker.
- **Build a reading list.** `similar --mode references` is the prerequisites. `--mode citers` is the frontier. One seed, a whole path.
- **Red-team a draft.** Take each claim, `search` for what contradicts it and what it should cite. Find the hole before a reviewer does.

## Principles

- **When in doubt, include.** For a topic, method, or comparison, return the family — most relevant first. The neighbours are part of the answer. Dropping them leaves half an answer.
- **Verify to exclude, not to gatekeep.** `read` to rule a paper *out* when a hard constraint clearly fails. When it's plausibly relevant, keep it.
- **Read the score.** Passages come back scored. A low score means a weak match — the body index sometimes returns the wrong passage. If the top score is low and the text doesn't address the question, the body didn't confirm it. Don't launder a 0.03 into a citation.
- **Never fabricate.** Return only ids, titles, and numbers the index actually returned. No invented arXiv ids. Ever.
- **Degrade out loud.** If the index can't answer, the script falls back to the public arXiv API. It banners the fallback on stderr. Lower recall, still real. Tell the reader you're on the fallback.

## When the index can't answer

Two honest failure modes, both handled.

- **Index unreachable.** `search` drops to the arXiv API automatically and banners `[fallback: arXiv API …]`. Other moves print the error instead of guessing. Pass `--no-fallback` to fail hard. On the fallback the `--from`/`--to`/`--authors`/`--categories` filters don't apply — expect broader, lower-precision results.
- **Question lives on the web.** Leaderboards, "most popular," rankings — those aren't in any abstract. Use a keyless web search (Firecrawl's `firecrawl_search`, also no key) to find the ranking. Then `search` each entry back into a paper.

## Notes

- **Keyless from a normal IP.** Capped per IP per day — plenty for interactive work. From a datacenter or agent IP the index may 403 and ask for a key.
- **Free key.** Set `FIRECRAWL_API_KEY` (free signup, no card) and the script adds it automatically — it lifts the per-IP ceiling and clears the 403 on a flagged IP.
- **`read` runs longer.** The body endpoint is slower, so `read` waits up to 90s. Raise `PAPER_SCOUT_TIMEOUT` to change every call's limit.
- **Backend-agnostic on purpose.** The script talks to the index over plain HTTP. So it doesn't depend on any vendor's MCP tools shipping. If `firecrawl_research_*` MCP tools appear in a session, prefer them; the method is identical.
- **Provenance.** Data: Firecrawl's keyless research index. Skill, method, engine, and voice: Solid State. Credit upstream, improve downstream.
- **License.** MIT. Copy it. Fork it. Ship it.

---

*Solid State — solidstate.cc*
