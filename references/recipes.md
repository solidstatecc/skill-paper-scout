# Paper Scout — recipes

Copy-paste cookbook. Every command is keyless. `{baseDir}` is the skill folder.

## Prove it answers
```bash
python3 {baseDir}/scripts/scout.py selftest
```

## Find the paper
```bash
# named paper — one shot
python3 {baseDir}/scripts/scout.py search "Qwen3 technical report" --k 5

# by method — find the best hit, then keep its neighbours
python3 {baseDir}/scripts/scout.py search "training-free n-gram detection of AI text" --k 8
python3 {baseDir}/scripts/scout.py similar arxiv:2305.17359 --intent "training-free LLM text detection" --mode similar --k 12
```

## Map a field (related work)
```bash
python3 {baseDir}/scripts/scout.py search "<field or method>" --k 10
# expand the two strongest anchors, re-seed from new strong hits
python3 {baseDir}/scripts/scout.py similar <seed-id> --intent "<what you actually want>" --mode similar --k 15
```

## Ground a claim (anti-hallucination)
```bash
# before asserting a number or method, read it from the paper
python3 {baseDir}/scripts/scout.py read <paper-id> "what is the reported score on <benchmark>" --k 4
```
Check the score on each passage. Low score + off-topic text = unconfirmed. Don't cite it.

## Find prior art (GitHub)
```bash
python3 {baseDir}/scripts/scout.py github "<symptom, API, or design choice>" --k 10
```

## Scan what's new
```bash
python3 {baseDir}/scripts/scout.py search "<topic>" --from 2026-01-01 --k 20
# run on a schedule for a field tracker
```

## Build a reading list
```bash
python3 {baseDir}/scripts/scout.py similar <seed-id> --mode references --k 15   # prerequisites
python3 {baseDir}/scripts/scout.py similar <seed-id> --mode citers --k 15       # the frontier
```

## Compare-against / what does X build on
```bash
python3 {baseDir}/scripts/scout.py read <paper-id> "what methods does it benchmark against" --k 4
python3 {baseDir}/scripts/scout.py similar <paper-id> --mode references --k 15
```

## Verify an org / author claim
```bash
python3 {baseDir}/scripts/scout.py inspect <paper-id>
python3 {baseDir}/scripts/scout.py read <paper-id> "which institutions are the authors affiliated with" --k 3
```

## Superlative / leaderboard
The ranking lives on the web, not in an abstract. Find it with a keyless web search
(Firecrawl `firecrawl_search`, also no key), then map each top entry back with `search`.

## Flags
- `--k N` — how many results (default varies by move)
- `--from` / `--to` YYYY-MM-DD — date window (search)
- `--authors`, `--categories cs.LG` — filter (search)
- `--intent` — natural-language ranking target (similar)
- `--mode similar|citers|references` (similar)
- `--json` — machine-readable, for piping
- `--no-fallback` — fail instead of degrading to arXiv (search)

## Higher limits (optional, free)
```bash
export FIRECRAWL_API_KEY="fc-..."   # free signup, no card; the script adds it automatically
```
