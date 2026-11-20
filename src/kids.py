"""The Kids and Families section: hub, coloring pages, first prayers, Mass for kids,
saint stories and the family corner, in English, Spanish, Portuguese and Filipino.

build.py calls render(body, lang, url) on every page. A page body that is just
{{KIDS:<part>}} is replaced with the whole page built here from kids_text.TX.
url(en_slug) gives the address of another page in the same language.
"""
from pathlib import Path
import html
import json
import re

import kids_art
from kids_text import TX

e = html.escape
SRC = Path(__file__).resolve().parent
PARTS = ("kids", "coloring-pages", "first-prayers", "mass-for-kids", "saint-stories", "family-corner")
PRAYER_PAGE = {"en": "prayers.html", "es": "es/oraciones.html", "pt": "pt/oracoes.html", "tl": "tl/mga-dasal.html"}
PART_ICON = {"coloring-pages": "glory", "first-prayers": "pray", "mass-for-kids": "host", "saint-stories": "cross", "family-corner": "sent"}


def _prayer_from_page(lang, pid):
    """(title, text) of a prayer card on the main prayers page, so the wording always matches."""
    src = (SRC / "pages" / PRAYER_PAGE[lang]).read_text(encoding="utf-8")
    m = re.search(r'id="%s">\s*<h3>(.*?)</h3>\s*<p class="text">(.*?)</p>' % re.escape(pid), src, re.S)
    title = html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip()
    text = html.unescape(re.sub(r"<[^>]+>", "", m.group(2))).strip()
    return title, text


def _head(lang, url, part, h1=None, lede=None):
    t = TX[lang]
    kick = "" if part == "kids" else f'<p class="kicker"><a href="{url("kids")}">{t["name"]["kids"]}</a> &rsaquo; {t["name"][part]}</p>'
    if part == "kids":
        kick = f'<p class="kicker">{t["kicker"]}</p>'
    return f'''<div class="page-head kids-head">
  <div class="wrap">
    {kick}
    <h1>{h1 or t["h1"][part]}</h1>
    <p class="lede">{lede or t["lede"][part]}</p>
  </div>
</div>
'''


def _more(lang, url, skip):
    t = TX[lang]
    cards = "".join(
        f'<a class="card tile kid-tile" href="{url(p)}">{kids_art.ICONS[PART_ICON[p]]}<div><h3>{t["name"][p]}</h3><p>{t["blurb"][p]}</p></div></a>'
        for p in PARTS[1:] if p != skip)
    return f'<section class="section"><h2>{t["more"]}</h2><div class="grid kid-grid">{cards}</div></section>'


def _print_btn(lang, target, blank=False, label=None):
    t = TX[lang]
    b = ' data-blank="1"' if blank else ""
    return f'<button type="button" class="btn small secondary" data-print="{target}"{b}>{label or t["print"]}</button>'


# ---------------------------------------------------------------- hub

def hub(lang, url):
    t = TX[lang]
    h = t["hub"]
    thumbs = {"coloring-pages": "noah", "first-prayers": None, "mass-for-kids": "altar", "saint-stories": "francis", "family-corner": "advent-wreath"}
    cards = []
    for p in PARTS[1:]:
        art = (f'<div class="kid-thumb">{kids_art.coloring_svg(thumbs[p], "")}</div>' if thumbs[p]
               else f'<div class="kid-thumb kid-thumb-icon">{kids_art.ICONS["pray"]}</div>')
        cards.append(f'<a class="card tile kid-card" href="{url(p)}">{art}<h3>{t["name"][p]}</h3><p>{t["blurb"][p]}</p>'
                     f'<span class="go">{t["go"][p]} &rarr;</span></a>')
    tips = "".join(f"<li><strong>{a}</strong> {b}</li>" for a, b in h["tips"])
    return _head(lang, url, "kids") + f'''<div class="wrap">
  <section class="section">
    <div class="grid kid-hub">{"".join(cards)}</div>
  </section>
  <section class="section">
    <div class="grid two">
      <div class="card tile saint-today" data-sod>
        <p class="label">{h["sod"]}</p>
        <h3 class="sod-name">{h["sod_wait"]}</h3>
        <p class="sod-sub small muted">&nbsp;</p>
        <a class="go" href="{url("saint-stories")}">{h["sod_go"]} &rarr;</a>
      </div>
      <div class="card">
        <h3>{h["free_h"]}</h3>
        <p>{h["free"]}</p>
      </div>
    </div>
  </section>
  <section class="section prose">
    <h2>{h["tips_h"]}</h2>
    <ul class="kid-tips">{tips}</ul>
    <p>{h["sacr"].format(fc=url("first-communion"), conf=url("confirmation"), exam=url("examination-of-conscience"), fam=url("family-corner"))}</p>
  </section>
</div>'''


# ---------------------------------------------------------------- coloring pages

PALETTE = ["#e53935", "#fb8c00", "#fdd835", "#8bc34a", "#2e7d32", "#4fc3f7", "#1e63c6", "#5e35b1",
           "#ec5fa4", "#f8c9a0", "#c68a54", "#7b4a26", "#9e9e9e", "#212121", "#e2b64a", "#ffffff"]


def coloring(lang, url):
    t = TX[lang]
    c = t["coloring"]
    groups = []
    for g in ("saints", "bible", "mass", "seasons"):
        cards = []
        for pid, _, grp in kids_art.PAGES:
            if grp != g:
                continue
            title = c["titles"][pid]
            cards.append(f'<figure class="card cpage-card" id="color-{pid}">{kids_art.coloring_svg(pid, title)}'
                         f'<figcaption><h3>{title}</h3><p class="small muted">{c["about"][pid]}</p>'
                         f'<button type="button" class="btn small" data-color="{pid}">{c["color_this"]}</button></figcaption></figure>')
        groups.append(f'<section class="section" id="group-{g}"><h2>{c["groups"][g]}</h2><div class="grid cpage-grid">{"".join(cards)}</div></section>')
    swatches = "".join(
        f'<button type="button" class="swatch" style="--c:{col}" data-c="{col}" aria-label="{c["color_word"]} {i + 1}" aria-pressed="{"true" if i == 0 else "false"}"></button>'
        for i, col in enumerate(PALETTE))
    jump = " &middot; ".join(f'<a href="#group-{g}">{c["groups"][g]}</a>' for g in ("saints", "bible", "mass", "seasons"))
    return _head(lang, url, "coloring-pages") + f'''<div class="wrap" id="coloring-app">
  <p class="kid-jump">{jump}</p>
  <section class="section studio" id="studio" hidden>
    <div class="studio-wrap">
      <div class="studio-art" id="studio-art"></div>
      <div class="studio-tools">
        <h2 id="studio-title">{c["studio"]}</h2>
        <p class="small muted">{c["how"]}</p>
        <div class="palette" role="group" aria-label="{c["colors"]}">{swatches}</div>
        <div class="studio-btns">
          <button type="button" class="btn small secondary" id="studio-undo">{c["undo"]}</button>
          <button type="button" class="btn small secondary" id="studio-clear">{c["clear"]}</button>
          <button type="button" class="btn small" id="studio-print">{c["print_mine"]}</button>
          <button type="button" class="btn small secondary" id="studio-blank">{c["print_blank"]}</button>
          <button type="button" class="btn small secondary" id="studio-close">{c["close"]}</button>
        </div>
        <p class="small muted">{c["saved"]}</p>
      </div>
    </div>
  </section>
  <noscript><p class="card">{c["noscript"]}</p></noscript>
  {"".join(groups)}
  <section class="section prose">
    <h2>{c["print_h"]}</h2>
    <p>{c["print_p"]}</p>
  </section>
  {_more(lang, url, "coloring-pages")}
</div>'''


# ---------------------------------------------------------------- first prayers

def prayers(lang, url):
    t = TX[lang]
    p = t["prayers"]
    cards = []
    for key, src, tip in p["list"]:
        if isinstance(src, str):
            title, text = _prayer_from_page(lang, src)
            if key in p["titles"]:
                title = p["titles"][key]
        else:
            title, text = src
        if key == "sign":  # kids learn the short form first
            text = text.strip().split("\n")[-1]
        lines = "".join(f'<span class="kp-line">{e(x.strip())}</span>' for x in text.split("\n") if x.strip())
        cards.append(f'''<article class="card kid-prayer" id="kp-{key}">
      <h2>{title}</h2>
      <p class="kp-text" lang="{lang if lang != "tl" else "fil"}">{lines}</p>
      <div class="kp-tools"><button type="button" class="btn small kp-say" hidden>{p["read"]}</button></div>
      <p class="kp-tip">{tip}</p>
    </article>''')
    toc = "".join(f'<li><a href="#kp-{k}">{(p["titles"].get(k) or (_prayer_from_page(lang, s)[0] if isinstance(s, str) else s[0]))}</a></li>' for k, s, _ in p["list"])
    return _head(lang, url, "first-prayers") + f'''<div class="wrap" id="first-prayers">
  <section class="section">
    <ul class="toc kid-toc">{toc}</ul>
    <div class="kp-bar card" id="kp-bar" hidden>
      <span>{p["speed"]}</span>
      <button type="button" class="chip" data-rate="0.7" aria-pressed="true">{p["slow"]}</button>
      <button type="button" class="chip" data-rate="0.95" aria-pressed="false">{p["normal"]}</button>
      <span class="small muted" id="kp-novoice" hidden>{p["novoice"]}</span>
    </div>
    <div class="kid-prayers">{"".join(cards)}</div>
  </section>
  <section class="section prose">
    <h2>{p["teach_h"]}</h2>
    <ul class="kid-tips">{"".join(f"<li>{x}</li>" for x in p["teach"])}</ul>
    <p>{p["more_link"].format(prayers=url("prayers"), rosary=url("rosary"))}</p>
  </section>
  {_more(lang, url, "first-prayers")}
</div>'''


# ---------------------------------------------------------------- Mass for kids

def mass(lang, url):
    import visual
    t = TX[lang]
    m = t["mass"]
    steps = visual.mass_steps(lang)
    pose_word = visual.POSE_WORD[lang]
    cards = []
    for n, (idx, icon, text, keep) in enumerate(m["steps"], 1):
        s = steps[idx]
        say = ""
        if keep:
            rows = [(w, x) for w, x in s["say"] if w][:2]
            say = '<dl class="say">' + "".join(f'<div class="say-row"><dt>{e(w)}</dt><dd>{e(x)}</dd></div>' for w, x in rows) + "</dl>"
        cards.append(f'''<li class="card kid-step" id="kid-step-{n}">
      <div class="ks-top">{kids_art.ICONS[icon]}<div><p class="ks-n">{n}</p><h3>{e(s["title"])}</h3>
      <p class="ks-pose pose-bg-{s["pose"]}">{visual.POSE_SVG[s["pose"]]}<span>{pose_word[s["pose"]]}</span></p></div></div>
      <p>{text}</p>{say}
    </li>''')
    spy = "".join(f'<li><label><input type="checkbox"><span><strong>{a}</strong> {b}</span></label></li>' for a, b in m["spy"])
    tips = "".join(f"<li>{x}</li>" for x in m["tips"])
    return _head(lang, url, "mass-for-kids") + f'''<div class="wrap">
  <section class="section">
    <h2>{m["steps_h"]}</h2>
    <p class="prose">{m["steps_p"]}</p>
    <ol class="kid-steps">{"".join(cards)}</ol>
  </section>
  <section class="section" id="i-spy">
    <div class="sheet" id="spy-sheet">
      <h2>{m["spy_h"]}</h2>
      <p>{m["spy_p"]}</p>
      <ul class="spy-list">{spy}</ul>
    </div>
    <p class="btn-row-left">{_print_btn(lang, "#spy-sheet", blank=True)}</p>
  </section>
  <section class="section prose">
    <h2>{m["tips_h"]}</h2>
    <ul class="kid-tips">{tips}</ul>
    <p>{m["links"].format(inside=url("inside-the-mass"), first=url("first-mass"), color=url("coloring-pages"))}</p>
  </section>
  {_more(lang, url, "mass-for-kids")}
</div>'''


# ---------------------------------------------------------------- saint stories

def saints(lang, url):
    t = TX[lang]
    s = t["saints"]
    months = t["months"]
    cards = []
    for key, mmdd, name, story, try_, color in s["list"]:
        mo, d = int(mmdd[:2]), int(mmdd[3:])
        date = t["date_fmt"].format(d=d, m=months[mo - 1])
        col = (f'<a class="small" href="{url("coloring-pages")}#color-{color}">{s["color"].format(name=name)} &rarr;</a>' if color else "")
        cards.append(f'''<article class="card kid-saint" id="saint-{key}" data-feast="{mmdd}">
      <p class="label ks-date">{date}<span class="ks-flag" hidden></span></p>
      <h3>{name}</h3>
      <p>{story}</p>
      <p class="kp-tip"><strong>{s["try"]}</strong> {try_}</p>
      {col}
    </article>''')
    return _head(lang, url, "saint-stories") + f'''<div class="wrap" id="saint-stories">
  <section class="section">
    <div class="grid two">
      <div class="card" id="saint-feature">
        <p class="label" id="saint-feature-label">{s["next"]}</p>
        <h3 id="saint-feature-name">&nbsp;</h3>
        <p id="saint-feature-date" class="small muted">&nbsp;</p>
        <a id="saint-feature-link" href="#saint-stories-list">{s["read"]} &rarr;</a>
      </div>
      <a class="card tile saint-today" href="{url("saints-directory")}" data-sod>
        <p class="label">{s["sod"]}</p>
        <h3 class="sod-name">&nbsp;</h3>
        <p class="sod-sub small muted">&nbsp;</p>
        <span class="go">{s["sod_go"]} &rarr;</span>
      </a>
    </div>
    <script type="application/json" id="saint-ui">{json.dumps({"today": s["today"], "next": s["next"], "months": months, "fmt": t["date_fmt"]}, ensure_ascii=False)}</script>
  </section>
  <section class="section" id="saint-stories-list">
    <h2>{s["all_h"]}</h2>
    <p class="prose">{s["all_p"].format(saints=url("saints"))}</p>
    <div class="grid two kid-saints">{"".join(cards)}</div>
  </section>
  {_more(lang, url, "saint-stories")}
</div>'''


# ---------------------------------------------------------------- family corner

def family(lang, url):
    t = TX[lang]
    f = t["family"]
    secs = []
    for key, color, title, intro, ideas in f["seasons"]:
        cards = "".join(f'<div class="card fam-idea"><h3>{a}</h3><p>{b.format(**{k: url(k) for k in ("advent", "stations-of-the-cross", "rosary", "saints", "first-prayers", "coloring-pages", "baptism")})}</p></div>' for a, b in ideas)
        secs.append(f'''<section class="section fam-season" id="season-{key}" data-season="{key}">
    <h2><span class="season-dot" style="background:var(--lit-{color})"></span>{title} <span class="fam-now" hidden>{f["now"]}</span></h2>
    <p class="prose">{intro}</p>
    <div class="grid two">{cards}</div>
  </section>''')
    jump = " &middot; ".join(f'<a href="#season-{k}">{ti}</a>' for k, _, ti, _, _ in f["seasons"])

    def sheet(sid, sh, link):
        fields = "".join(f'<p class="fill"><span>{x}</span><span class="fill-line"></span></p>' for x in sh["fields"])
        lists = "".join(f'<h3>{h}</h3><ul class="spy-list">' + "".join(
            f'<li><label><input type="checkbox"><span>{x}</span></label></li>' for x in items) + "</ul>" for h, items in sh["lists"])
        draw = f'<div class="draw-box"><span>{sh["draw"]}</span></div>' if sh.get("draw") else ""
        return f'''<article class="card prep" id="prep-{sid}">
      <div class="sheet" id="sheet-{sid}">
        <h2>{sh["title"]}</h2>
        <p class="small muted">{sh["sub"]}</p>
        {fields}{lists}{draw}
      </div>
      <p class="btn-row-left">{_print_btn(lang, "#sheet-" + sid, blank=True, label=f["print_sheet"])} <a href="{link}">{sh["guide"]} &rarr;</a></p>
    </article>'''

    return _head(lang, url, "family-corner") + f'''<div class="wrap" id="family-corner">
  <p class="kid-jump">{jump} &middot; <a href="#prep">{f["prep_h"]}</a></p>
  <p class="card fam-season-now" id="fam-season-now" hidden></p>
  <script type="application/json" id="fam-ui">{json.dumps({"now": f["now_line"], "names": {k: ti for k, _, ti, _, _ in f["seasons"]}}, ensure_ascii=False)}</script>
  {"".join(secs)}
  <section class="section" id="prep">
    <h2>{f["prep_h"]}</h2>
    <p class="prose">{f["prep_p"]}</p>
    <div class="grid two prep-grid">
      {sheet("communion", f["communion"], url("first-communion"))}
      {sheet("confirmation", f["confirmation"], url("confirmation"))}
    </div>
  </section>
  {_more(lang, url, "family-corner")}
</div>'''


BUILDERS = {"kids": hub, "coloring-pages": coloring, "first-prayers": prayers, "mass-for-kids": mass,
            "saint-stories": saints, "family-corner": family}


def render(body, lang, url):
    m = re.search(r"\{\{KIDS:([a-z-]+)\}\}", body)
    if not m:
        return body
    return body.replace(m.group(0), BUILDERS[m.group(1)](lang, url))
