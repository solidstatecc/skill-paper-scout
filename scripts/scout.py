#!/usr/bin/env python3
"""paper-scout — Solid State.

Find and verify real research papers through Firecrawl's keyless Research Index.

No login. No key. The index answers raw HTTP requests for free, capped per IP
per day. Set FIRECRAWL_API_KEY (free signup, no card) only to lift those caps.
If the index is ever unreachable, search degrades to the public arXiv API so the
agent never has to fabricate a result.

Stdlib only. One file. The engine is the moat, not the dependency tree.

Subcommands:
  search   <query>            semantic search over abstracts
  similar  <id>               expand one paper into its family (similar|citers|references)
  inspect  <id>               canonical metadata for one paper
  read     <id> <question>    in-body passages that answer a specific question
  github   <query>            issues / PRs / READMEs — engineering prior art
  selftest                    one keyless call to prove the index answers

IDs are source ids like  arxiv:1706.03762  (or a canonical paperId).
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = os.environ.get("PAPER_SCOUT_BASE", "https://api.firecrawl.dev/v2/search/research")
KEY = os.environ.get("FIRECRAWL_API_KEY")  # optional, free, only lifts per-IP caps
_TIMEOUT_ENV = os.environ.get("PAPER_SCOUT_TIMEOUT")  # explicit override applies to every call
TIMEOUT = int(_TIMEOUT_ENV) if _TIMEOUT_ENV else 30
READ_TIMEOUT = int(_TIMEOUT_ENV) if _TIMEOUT_ENV else 90  # body/read endpoint is slower than the rest

# similar's API requires a non-empty intent. Default it per mode so the documented
# intent-less calls (reading lists, field maps) work without forcing --intent.
_DEFAULT_INTENT = {
    "similar": "closely related papers",
    "citers": "important work that builds on this paper",
    "references": "key prior work this paper builds on",
}


def _get(path, params=None, timeout=None):
    url = BASE + path
    if params:
        clean = {k: v for k, v in params.items() if v not in (None, "")}
        url += "?" + urllib.parse.urlencode(clean)
    req = urllib.request.Request(url, headers={"User-Agent": "paper-scout/1.0 (Solid State)"})
    if KEY:
        req.add_header("Authorization", "Bearer " + KEY)
    try:
        with urllib.request.urlopen(req, timeout=timeout or TIMEOUT) as r:
            return json.loads(r.read().decode("utf-8")), None
    except urllib.error.HTTPError as e:
        return None, "HTTP %s: %s" % (e.code, e.read().decode("utf-8", "replace")[:300])
    except Exception as e:  # noqa: BLE001 — surface the reason, never crash silently
        return None, "%s: %s" % (type(e).__name__, e)


def _arxiv_id(item):
    ids = item.get("ids") or {}
    ax = ids.get("arxiv")
    if ax:
        return ax[0] if isinstance(ax, list) else ax
    pid = item.get("primaryId") or ""
    return pid.split("arxiv:")[-1] if pid.startswith("arxiv:") else ""


def _link(item):
    ax = _arxiv_id(item)
    return "https://arxiv.org/abs/" + ax if ax else (item.get("primaryId") or item.get("paperId") or "")


def _print_papers(results, kind="results"):
    if not results:
        print("(no %s)" % kind)
        return
    for i, p in enumerate(results, 1):
        score = p.get("score")
        head = "%2d. %s" % (i, (p.get("title") or "(untitled)").strip())
        if score is not None:
            head += "   [score %.3f]" % score
        print(head)
        meta = "    %s" % _link(p)
        pid = p.get("primaryId") or p.get("paperId")
        if pid:
            meta += "   id=%s" % pid
        print(meta)
        ab = (p.get("abstract") or "").strip().replace("\n", " ")
        if ab:
            print("    " + (ab[:240] + ("…" if len(ab) > 240 else "")))
        print()


# ---------------------------------------------------------------- commands
def cmd_search(a):
    params = {"query": a.query, "k": a.k, "from": a.from_, "to": a.to,
              "authors": a.authors, "categories": a.categories}
    data, err = _get("/papers", params)
    if err:
        if a.no_fallback:
            sys.exit("search failed: %s" % err)
        sys.stderr.write("[fallback: arXiv API — Research Index unreachable: %s]\n" % err)
        return _arxiv_fallback(a.query, a.k, a.json)
    results = data.get("results", data if isinstance(data, list) else [])
    if a.json:
        print(json.dumps(results, indent=2))
    else:
        _print_papers(results, "papers")


def cmd_similar(a):
    seed = a.id[0]
    intent = a.intent or _DEFAULT_INTENT.get(a.mode, "closely related papers")
    params = {"intent": intent, "mode": a.mode, "k": a.k}
    data, err = _get("/papers/%s/similar" % urllib.parse.quote(seed, safe=""), params)
    if err:
        sys.exit("similar failed: %s" % err)
    results = data.get("results", [])
    if a.json:
        print(json.dumps(results, indent=2))
    else:
        print("# %s of %s (intent: %s)\n" % (a.mode, seed, intent))
        _print_papers(results, "neighbours")


def cmd_inspect(a):
    data, err = _get("/papers/%s" % urllib.parse.quote(a.id[0], safe=""))
    if err:
        sys.exit("inspect failed: %s" % err)
    if a.json:
        print(json.dumps(data, indent=2))
        return
    p = data.get("paper", data)
    print(p.get("title", "(untitled)"))
    print(_link(p))
    au = p.get("authors") or []
    if isinstance(au, str):
        names = [s.strip() for s in au.split(",") if s.strip()]
    elif au:
        names = [x.get("name", x) if isinstance(x, dict) else x for x in au]
    else:
        names = []
    if names:
        print("authors: " + ", ".join(map(str, names[:12])) + (" …" if len(names) > 12 else ""))
    cats = p.get("categories") or []
    if cats:
        print("categories: " + ", ".join(map(str, cats)))
    for d in ("createdDate", "updateDate"):
        if p.get(d):
            print("%s: %s" % (d, p[d]))
    ab = (p.get("abstract") or "").strip()
    if ab:
        print("\n" + ab)


def cmd_read(a):
    data, err = _get("/papers/%s" % urllib.parse.quote(a.id[0], safe=""), {"query": a.question, "k": a.k}, timeout=READ_TIMEOUT)
    if err:
        sys.exit("read failed: %s" % err)
    passages = data.get("passages") or (data.get("paper", {}) or {}).get("passages") or []
    if a.json:
        print(json.dumps(passages, indent=2))
        return
    title = (data.get("paper", {}) or {}).get("title", a.id[0])
    print('# %s\n# Q: %s\n' % (title, a.question))
    if not passages:
        print("(no passages returned — the body may not be indexed for this paper)")
        return
    for i, ps in enumerate(passages, 1):
        sc = ps.get("score")
        print("[%d]%s" % (i, ("  score %.3f" % sc) if sc is not None else ""))
        print((ps.get("text") or "").strip())
        print()


def cmd_github(a):
    data, err = _get("/github", {"query": a.query, "k": a.k})
    if err:
        sys.exit("github failed: %s" % err)
    results = data.get("results", [])
    if a.json:
        print(json.dumps(results, indent=2))
        return
    if not results:
        print("(no github results)")
        return
    for i, g in enumerate(results, 1):
        bits = [g.get("repo", "?")]
        if g.get("pageType"):
            bits.append(g["pageType"])
        if g.get("number"):
            bits.append("#%s" % g["number"])
        print("%2d. %s" % (i, "  ".join(map(str, bits))))
        if g.get("url"):
            print("    " + g["url"])
        sn = (g.get("snippet") or "").strip().replace("\n", " ")
        if sn:
            print("    " + (sn[:240] + ("…" if len(sn) > 240 else "")))
        print()


def cmd_selftest(a):
    data, err = _get("/papers", {"query": "attention is all you need", "k": 1})
    if err:
        sys.exit("FAIL (keyless): %s" % err)
    r = (data.get("results") or [{}])[0]
    print("OK — keyless index answered. sample: %s (%s)%s"
          % (r.get("title", "?"), _link(r), "  [key in use]" if KEY else "  [no key]"))


def _arxiv_fallback(query, k, as_json):
    import xml.etree.ElementTree as ET
    q = urllib.parse.urlencode({"search_query": "all:" + query, "start": 0, "max_results": k})
    url = "https://export.arxiv.org/api/query?" + q
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT) as r:
            xml = r.read().decode("utf-8")
    except Exception as e:  # noqa: BLE001
        sys.exit("arXiv fallback failed too: %s" % e)
    ns = {"a": "http://www.w3.org/2005/Atom"}
    out = []
    for e in ET.fromstring(xml).findall("a:entry", ns):
        ax = (e.findtext("a:id", "", ns) or "").rsplit("/abs/", 1)[-1]
        out.append({"title": (e.findtext("a:title", "", ns) or "").strip(),
                    "primaryId": "arxiv:" + ax, "ids": {"arxiv": [ax]},
                    "abstract": (e.findtext("a:summary", "", ns) or "").strip()})
    if as_json:
        print(json.dumps(out, indent=2))
    else:
        _print_papers(out, "papers (arXiv fallback)")


def main():
    p = argparse.ArgumentParser(prog="scout", description="paper-scout — keyless research index, by Solid State")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search", help="semantic search over abstracts")
    s.add_argument("query")
    s.add_argument("--k", type=int, default=10)
    s.add_argument("--from", dest="from_", metavar="YYYY-MM-DD")
    s.add_argument("--to", metavar="YYYY-MM-DD")
    s.add_argument("--authors")
    s.add_argument("--categories", help="e.g. cs.LG")
    s.add_argument("--no-fallback", action="store_true", help="fail instead of degrading to arXiv")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_search)

    sm = sub.add_parser("similar", help="expand one paper into its family")
    sm.add_argument("id", nargs=1)
    sm.add_argument("--intent", help="rank neighbours against this intent (optional; a mode-appropriate default is used if omitted)")
    sm.add_argument("--mode", choices=["similar", "citers", "references"], default="similar")
    sm.add_argument("--k", type=int, default=15)
    sm.add_argument("--json", action="store_true")
    sm.set_defaults(func=cmd_similar)

    ins = sub.add_parser("inspect", help="canonical metadata for one paper")
    ins.add_argument("id", nargs=1)
    ins.add_argument("--json", action="store_true")
    ins.set_defaults(func=cmd_inspect)

    rd = sub.add_parser("read", help="in-body passages that answer a question")
    rd.add_argument("id", nargs=1)
    rd.add_argument("question")
    rd.add_argument("--k", type=int, default=4)
    rd.add_argument("--json", action="store_true")
    rd.set_defaults(func=cmd_read)

    gh = sub.add_parser("github", help="issues / PRs / READMEs — engineering prior art")
    gh.add_argument("query")
    gh.add_argument("--k", type=int, default=10)
    gh.add_argument("--json", action="store_true")
    gh.set_defaults(func=cmd_github)

    st = sub.add_parser("selftest", help="one keyless call to prove the index answers")
    st.set_defaults(func=cmd_selftest)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
