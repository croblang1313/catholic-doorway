"""Site search: builds one small JSON index per language from the finished pages in site/.

Each entry is [title, url, snippet, page title]. Pages give one entry each, and inside a page
every section, card, prayer, question or term with an id and a heading gives its own entry,
so a search for "Memorare" lands on that prayer rather than the top of the Prayers page.
"""
from html.parser import HTMLParser
import html
import json
import re

SKIP_IDS = re.compile(r"^(main|site-nav|letter-|.*-(search|count|grid|list|msg|empty|toggle|form|input|status|results|title|text)$)")
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
ANCHOR_TAGS = {"section", "article", "details", "dt", "h2", "h3", "div", "li"}
BLOCK = {"p", "li", "dd", "div", "br", "ul", "ol", "tr", "td", "h2", "h3", "h4", "blockquote"}
HEAD_TAGS = {"h2", "h3", "h4", "summary", "dt"}


class Extract(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_main = False
        self.skip = 0          # inside script/style/svg/nav/buttons
        self.stack = []        # open tags inside main: [tag, entry, skipped, capturing]
        self.entries = []      # dicts: id, title, text
        self.open = []         # entries collecting text
        self.cap = []          # entries taking the current heading as their title
        self.last_dt = None
        self.dd_target = None

    def handle_starttag(self, tag, attrs):
        if tag == "main":
            self.in_main = True
            return
        if not self.in_main:
            return
        if tag in BLOCK:
            for e in self.open:
                e["text"].append(" ")
        if tag in VOID:
            return
        if tag in ("script", "style", "svg", "noscript", "select", "button", "nav", "template"):
            self.skip += 1
            self.stack.append([tag, None, True, None])
            return
        i = dict(attrs).get("id")
        entry = None
        if i and tag in ANCHOR_TAGS and not SKIP_IDS.match(i) and not self.skip:
            entry = {"id": i, "title": "", "text": []}
            self.entries.append(entry)
            self.open.append(entry)
        capturing = None
        if tag in HEAD_TAGS and not self.cap:
            capturing = [e for e in self.open if not e["title"]]
            self.cap = capturing
        if tag == "dd" and self.last_dt is not None:
            self.dd_target = self.last_dt
        self.stack.append([tag, entry, False, capturing])

    def handle_endtag(self, tag):
        if tag == "main":
            self.in_main = False
            return
        if not self.in_main:
            return
        for k in range(len(self.stack) - 1, -1, -1):
            if self.stack[k][0] == tag:
                break
        else:
            return
        while len(self.stack) > k:
            t, entry, sk, capturing = self.stack.pop()
            if sk:
                self.skip -= 1
            if capturing is not None:
                self.cap = []
            if entry is not None and entry in self.open:
                self.open.remove(entry)
                if t == "dt":
                    self.last_dt = entry
            if t == "dd":
                self.dd_target = None
                self.last_dt = None

    def handle_data(self, data):
        if not self.in_main or self.skip:
            return
        d = re.sub(r"\s+", " ", data)
        if not d.strip():
            return
        if self.cap:
            for e in self.cap:
                e["title"] += d
            return
        for e in self.open:
            e["text"].append(d)
        if self.dd_target is not None:
            self.dd_target["text"].append(d)


def clip(s, n=220):
    s = re.sub(r"\s+", " ", s).strip()
    if len(s) <= n:
        return s
    cut = s[:n].rsplit(" ", 1)[0]
    return cut.rstrip(",;:.") + "…"


def page_entries(text, url):
    title = html.unescape(re.search(r"<title>(.*?)</title>", text, re.S).group(1))
    title = re.sub(r"\s*\|\s*CatholicDoorway\s*$", "", title).strip()
    desc = re.search(r'<meta name="description" content="([^"]*)"', text)
    desc = html.unescape(desc.group(1)) if desc else ""
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", text, re.S)
    h1 = html.unescape(re.sub(r"<[^>]+>", "", h1.group(1))).strip() if h1 else title
    p = Extract()
    p.feed(text)
    out = [[h1 or title, url, clip(desc), ""]]
    seen = set()
    for e in p.entries:
        t = clip(e["title"], 90)
        if not t or e["id"] in seen or len(t) < 2:
            continue
        seen.add(e["id"])
        out.append([t, f"{url}#{e['id']}", clip("".join(e["text"])), h1 or title])
    return out


def write(out_dir, lang_pages):
    """lang_pages: {lang: [(url, html_text), ...]} -> site/data/search-<lang>.json"""
    for lang, pages in lang_pages.items():
        rows = []
        for url, text in pages:
            rows += page_entries(text, url)
        (out_dir / "data" / f"search-{lang}.json").write_text(
            json.dumps(rows, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        print(f"search index {lang}: {len(rows)} entries")
