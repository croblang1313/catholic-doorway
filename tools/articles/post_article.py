#!/usr/bin/env python3
"""Leave a "This Week in the Church" article on catholicdoorway.com as a draft for approval.

Usage: python3 post_article.py article.json [more.json ...] [--dry-run]

Sends each file to POST https://catholicdoorway.com/api/articles with the Social Posts drafts token
($DRAFTS_TOKEN, or the file named by $DRAFTS_TOKEN_FILE). The token can only leave drafts. It prints
the private review link; opening it shows the article exactly as it will look, with a Publish button.
All drafts and published articles are also listed at https://catholicdoorway.com/this-week/review
(admin password).

Article JSON (see seed/ for full examples and README.md for the writing rules):
  {"slug": "what-is-advent", "title": "...", "description": "one or two sentences (meta description)",
   "kicker": "Season · Advent begins November 29, 2026", "date": "YYYY-MM-DD (the feast day)",
   "verse": {"t": "RSV-CE text", "r": "Psalm 25:1"},
   "body": "<p>...</p><h2>...</h2>... (p, h2, h3, ul, ol, li, blockquote class=scripture|ccc, cite, a, strong, em)",
   "related": [{"href": "/advent", "label": "...", "note": "..."}],
   "sources": [{"label": "Catechism of the Catholic Church 524", "href": "https://..."}],
   "social": "one-line idea for the matching social post"}
"""
import json, os, sys, urllib.error, urllib.request

SITE = os.environ.get("SITE_URL", "https://catholicdoorway.com")


def token():
    t = os.environ.get("DRAFTS_TOKEN", "").strip()
    if not t and os.environ.get("DRAFTS_TOKEN_FILE"):
        t = open(os.environ["DRAFTS_TOKEN_FILE"]).read().strip()
    if not t:
        sys.exit("No drafts token: set DRAFTS_TOKEN or DRAFTS_TOKEN_FILE.")
    return t


def check(a):
    """Catch the House Rules a script can check before anything is sent."""
    problems = []
    text = json.dumps(a, ensure_ascii=False)
    if "—" in text or "&mdash;" in text:
        problems.append("contains an em dash (House Rule 8)")
    for k in ("slug", "title", "description", "kicker", "date", "body"):
        if not a.get(k):
            problems.append(f"missing {k}")
    if len(a.get("title", "")) > 70:
        problems.append("title over 70 characters")
    if not 70 <= len(a.get("description", "")) <= 300:
        problems.append("description should be 70 to 300 characters")
    return problems


def send(path, dry=False, tok=None):
    a = json.load(open(path, encoding="utf-8"))
    problems = check(a)
    if problems:
        sys.exit(f"{path}: " + "; ".join(problems))
    if dry:
        print("ok (dry run)", a["slug"])
        return {"slug": a["slug"], "url": f"{SITE}/this-week/{a['slug']}", "review_url": None}
    req = urllib.request.Request(SITE + "/api/articles", data=json.dumps(a).encode(), method="POST",
                                 headers={"Authorization": "Bearer " + (tok or token()), "Content-Type": "application/json",
                                          "User-Agent": "CatholicDoorway drafts"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            out = json.load(r)
    except urllib.error.HTTPError as e:
        out = json.loads(e.read() or b"{}")
        if out.get("error") == "already_published":
            print("already published, left alone:", out.get("url"))
            return out
        sys.exit(f"{path}: {e.code} {out}")
    print("draft", out["url"], "\n  review:", out["review_url"])
    return out


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    for p in [x for x in sys.argv[1:] if not x.startswith("--")]:
        send(p, dry)
