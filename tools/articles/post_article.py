#!/usr/bin/env python3
"""Leave a "This Week in the Church" article on catholicdoorway.com as a draft for approval.

Usage: python3 post_article.py article.json [more.json ...] [--dry-run]
       python3 post_article.py --attach article.json [--image share.jpg]
           (re-make and send only the PDF and share picture; works on a published article too)

Sends each file to POST https://catholicdoorway.com/api/articles with the Social Posts drafts token
($DRAFTS_TOKEN, or the file named by $DRAFTS_TOKEN_FILE). The token can only leave drafts. It prints
the private review link. Christopher reads and publishes it in the Articles tab of Social Posts
(https://social.catholicdoorway.com/#articles).

Article JSON (see seed/ for full examples and README.md for the writing rules):
  {"slug": "what-is-advent", "title": "...", "description": "one or two sentences (meta description)",
   "kicker": "Season · Advent begins November 29, 2026", "date": "YYYY-MM-DD (the feast day)",
   "verse": {"t": "RSV-CE text", "r": "Psalm 25:1"},
   "body": "<p>...</p><h2>...</h2>... (p, h2, h3, ul, ol, li, blockquote class=scripture|ccc, cite, a, strong, em)",
   "related": [{"href": "/advent", "label": "...", "note": "..."}],
   "sources": [{"label": "Catechism of the Catholic Church 524", "href": "https://..."}],
   "social": "one-line idea for the matching social post",
   "share_image": {"kicker": "...", "title": "...", "body": "...", "ref": "...", "theme": "cream|navy"}}

Every draft also carries:
  - a PDF copy, made here with make_article_pdf.js, for the article's "Download PDF" button;
  - a 1200x630 share picture (what Facebook, X and WhatsApp show when the link is shared).
    send_drafts.py passes the matching post's picture design; on its own this script renders
    "share_image" (same fields as a post image), or uses "image": "file.jpg" next to the JSON.
    Its background color comes from week_theme(): a different color each week ("share_theme" overrides).
"""
import base64, json, os, subprocess, sys, tempfile, urllib.error, urllib.request

SITE = os.environ.get("SITE_URL", "https://catholicdoorway.com")
HERE = os.path.dirname(os.path.abspath(__file__))


def _tool(*names):
    for n in names:
        p = os.path.normpath(os.path.join(HERE, n))
        if os.path.exists(p):
            return p
    sys.exit("can't find " + names[0])


# Article share pictures change color every week so they don't look alike in a feed.
# Dark and light alternate; consecutive weeks never repeat. "share_theme" in the article overrides.
ARTICLE_ROTATION = ["navy", "rose", "forest", "sky", "burgundy", "sage", "purple", "cream", "teal"]


def week_theme(a):
    if a.get("share_theme"):
        return a["share_theme"]
    import datetime
    try:
        d = datetime.date.fromisoformat(str(a.get("date", ""))[:10])
    except ValueError:
        d = datetime.date.today()
    weeks = (d - datetime.date(1970, 1, 4)).days // 7  # weeks run Sunday to Saturday
    return ARTICLE_ROTATION[weeks % len(ARTICLE_ROTATION)]


def render_share_image(spec, out):
    """The post-picture design at 1200x630."""
    tool = _tool("../social-posts/make_post_image.js", "../tools/make_post_image.js")
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(spec, f)
    subprocess.run(["node", tool, f.name, out, "--wide"], check=True)
    os.unlink(f.name)
    return out


def render_pdf(article_path, out):
    subprocess.run(["node", os.path.join(HERE, "make_article_pdf.js"), article_path, out], check=True)
    return out


def files_for(path, a, image=None):
    """Make the PDF and find or make the share picture. Returns (pdf_path, image_path)."""
    base = os.path.splitext(os.path.abspath(path))[0]
    pdf = render_pdf(path, base + ".pdf")
    if not image and isinstance(a.get("image"), str) and not a["image"].startswith("data:"):
        image = os.path.join(os.path.dirname(os.path.abspath(path)), a["image"])
    if not image:
        spec = a.get("share_image") or {"kicker": "This Week in the Church", "title": a["title"], "ref": a.get("kicker", "")}
        image = render_share_image({**spec, "theme": week_theme(a)}, base + "-share.jpg")
    print("pdf", pdf, "\n  share picture", image)
    return pdf, image


def b64(path, mime):
    return f"data:{mime};base64," + base64.b64encode(open(path, "rb").read()).decode()


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
    if len(a.get("related") or []) != 3:
        problems.append("related should have exactly 3 pages (the Keep going cards)")
    if not 70 <= len(a.get("description", "")) <= 300:
        problems.append("description should be 70 to 300 characters")
    return problems


def send(path, dry=False, tok=None, image=None):
    a = json.load(open(path, encoding="utf-8"))
    problems = check(a)
    if problems:
        sys.exit(f"{path}: " + "; ".join(problems))
    pdf, image = files_for(path, a, image)
    a.pop("share_image", None)
    a["pdf"] = b64(pdf, "application/pdf")
    a["image"] = b64(image, "image/png" if image.lower().endswith(".png") else "image/jpeg")
    a.setdefault("image_alt", a["title"] + ": This Week in the Church at CatholicDoorway")
    if dry:
        print("ok (dry run)", a["slug"])
        return {"slug": a["slug"], "title": a["title"], "url": f"{SITE}/this-week/{a['slug']}", "review_url": None}
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
    out["title"] = a["title"]
    print("draft", out["url"], "\n  review:", out["review_url"])
    return out


def attach(path, tok=None, image=None):
    """Send only the PDF and share picture (for an article that is already published)."""
    a = json.load(open(path, encoding="utf-8"))
    pdf, image = files_for(path, a, image)
    body = {"slug": a["slug"], "pdf": b64(pdf, "application/pdf"),
            "image": b64(image, "image/png" if image.lower().endswith(".png") else "image/jpeg"),
            "image_alt": a.get("image_alt") or a["title"] + ": This Week in the Church at CatholicDoorway"}
    req = urllib.request.Request(SITE + "/api/articles/files", data=json.dumps(body).encode(), method="POST",
                                 headers={"Authorization": "Bearer " + (tok or token()), "Content-Type": "application/json",
                                          "User-Agent": "CatholicDoorway drafts"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            out = json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"{path}: {e.code} {e.read()[:300]}")
    print("attached", a["slug"], "\n  picture:", out.get("image_url"), "\n  pdf:", out.get("pdf_url"))
    return out


if __name__ == "__main__":
    args = sys.argv[1:]
    dry = "--dry-run" in args
    img = args[args.index("--image") + 1] if "--image" in args else None
    paths = [x for i, x in enumerate(args) if not x.startswith("--") and not (i and args[i - 1] == "--image")]
    for p in paths:
        if "--attach" in args:
            attach(p, image=img)
        else:
            send(p, dry, image=img)
