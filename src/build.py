#!/usr/bin/env python3
"""Builds the static CatholicDoorway.com site.

Each page body lives in src/pages/<slug>.html. This script wraps it in the
shared header, navigation and footer and writes it to site/<slug>.html.
Run:  python3 src/build.py
"""
from pathlib import Path
import datetime
import hashlib
import html
import json

ROOT = Path(__file__).resolve().parent.parent
PAGES_DIR = ROOT / "src" / "pages"
OUT = ROOT / "site"
DOMAIN = "https://catholicdoorway.com"

# slug, nav label, <title>, meta description
PAGES = [
    ("index", "Home", "CatholicDoorway: a free guide to the Catholic faith",
     "A free, simple guide to the Catholic faith: prayers, daily readings, how to become Catholic (OCIA), a church finder, saints, beliefs and a glossary."),
    ("start-here", "Start Here", "Start Here: Becoming Catholic (OCIA) | CatholicDoorway",
     "New to the Catholic Church? How OCIA works, the four stages, how long it takes, who to contact, and what to expect at your first Mass."),
    ("find-a-church", "Find a Church", "Find a Catholic Church Near You | CatholicDoorway",
     "Find Catholic churches near you on a free map built from OpenStreetMap, with address, phone, website and directions."),
    ("prayers", "Prayers", "Catholic Prayers and How to Pray the Rosary | CatholicDoorway",
     "Traditional Catholic prayers, from the Our Father and Hail Mary to the Memorare, plus a step-by-step guide to the Rosary."),
    ("bible", "Bible & Readings", "The Bible and Today's Mass Readings | CatholicDoorway",
     "Today's Catholic Mass readings, how the Catholic Bible is arranged, and where to read it free online."),
    ("beliefs", "Beliefs", "What Catholics Believe | CatholicDoorway",
     "A plain-language overview of Catholic belief and practice: the Creed, the seven sacraments, Scripture and Tradition, Mary and the saints, and the moral life."),
    ("structure", "Church Structure", "How the Catholic Church Is Organized | CatholicDoorway",
     "How the Catholic Church is organized: the Pope, bishops, dioceses, parishes, priests and deacons, explained simply."),
    ("dioceses", "Dioceses", "U.S. Catholic Dioceses Directory | CatholicDoorway",
     "Find your Catholic diocese: the U.S. archdioceses and how to look up any diocese in the United States."),
    ("saints", "Saints", "Catholic Saints, Blesseds and Venerables | CatholicDoorway",
     "Meet the saints, and learn the path to sainthood: Servant of God, Venerable, Blessed and Saint."),
    ("glossary", "Glossary", "Catholic Glossary: Terms Explained Simply | CatholicDoorway",
     "Plain-English definitions of Catholic words, from Advent to Vespers."),
    ("about", "About", "About CatholicDoorway",
     "About CatholicDoorway.com: a free, ad-free guide to the Catholic faith. Sources, data and corrections."),
    ("404", "Not found", "Page not found | CatholicDoorway", "This page could not be found."),
]
NAV_EXCLUDE = {"about", "404"}

DOOR_SVG = '''<svg viewBox="0 0 34 40" aria-hidden="true" focusable="false"><path d="M3 39V17C3 8.7 9.3 2 17 2s14 6.7 14 15v22" fill="none" stroke="currentColor" stroke-width="2.4"/><path d="M8 39V18.5C8 13 12 8.5 17 8.5S26 13 26 18.5V39" fill="currentColor" opacity=".16"/><path d="M8 39V18.5C8 13 12 8.5 17 8.5S26 13 26 18.5V39" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M17 12v9M13.6 15.2h6.8" stroke="#a8802f" stroke-width="2" stroke-linecap="round"/><circle cx="22" cy="28" r="1.4" fill="#a8802f"/><path d="M1 39h32" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/></svg>'''

MENU_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 6h18M3 12h18M3 18h18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>'
THEME_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>'

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="CatholicDoorway">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{domain}/assets/img/og.png">
<meta name="theme-color" content="#1d2b4f">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Source+Sans+3:wght@400;500;600;700&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&display=swap">
<link rel="stylesheet" href="/assets/css/style.css">
<script>try{{var t=localStorage.getItem('cd-theme');if(t)document.documentElement.setAttribute('data-theme',t);}}catch(e){{}}</script>
{extra_head}
</head>
<body data-page="{slug}">
<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap header-row">
    <a class="brand" href="/" aria-label="CatholicDoorway home">{door}<span class="brand-name">Catholic<span>Doorway</span></span></a>
    <div class="header-tools">
      <button class="theme-btn" type="button" data-theme-toggle aria-label="Switch light or dark mode">{theme}</button>
      <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav">{menu}Menu</button>
    </div>
    <nav class="site-nav" id="site-nav" aria-label="Main">
      <ul>
{nav}
      </ul>
    </nav>
  </div>
</header>
<main id="main">
"""

FOOT = """</main>
<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <p class="footer-verse">&ldquo;I am the door; if any one enters by me, he will be saved.&rdquo;</p>
        <p class="small">John 10:9 (RSV-CE)</p>
      </div>
      <div>
        <h4>Explore</h4>
        <ul>
          <li><a href="/start-here">Becoming Catholic (OCIA)</a></li>
          <li><a href="/find-a-church">Find a Church</a></li>
          <li><a href="/prayers">Prayers &amp; the Rosary</a></li>
          <li><a href="/bible">Today&rsquo;s Readings</a></li>
        </ul>
      </div>
      <div>
        <h4>Learn</h4>
        <ul>
          <li><a href="/beliefs">What Catholics Believe</a></li>
          <li><a href="/structure">How the Church Is Organized</a></li>
          <li><a href="/saints">Saints</a></li>
          <li><a href="/glossary">Glossary</a></li>
        </ul>
      </div>
      <div>
        <h4>About</h4>
        <ul>
          <li><a href="/about">About this site</a></li>
          <li><a href="/dioceses">Diocese directory</a></li>
          <li><a href="/about#corrections">Send a correction</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-base">
      CatholicDoorway is a free, independent guide with no ads. It is not an official site of the Catholic Church or any diocese. For the Church&rsquo;s official teaching, see the <a href="https://www.vatican.va/archive/ENG0015/_INDEX.HTM">Catechism of the Catholic Church</a>. Scripture quotations are from the Revised Standard Version of the Bible, Second Catholic Edition &copy; 2006 National Council of the Churches of Christ in the USA. Used by permission. All rights reserved.
    </div>
  </div>
</footer>
<script src="/assets/js/main.js" defer></script>
{extra_foot}
</body>
</html>
"""

EXTRA = {
    "find-a-church": (
        '<link rel="stylesheet" href="/assets/vendor/leaflet/leaflet.css">',
        '<script src="/assets/vendor/leaflet/leaflet.js"></script>\n<script src="/assets/js/map.js" defer></script>',
    ),
}


STATUS_LABEL = {"saint": "Saint", "blessed": "Blessed", "venerable": "Venerable", "servant": "Servant of God"}


def saints_html():
    data = json.loads((ROOT / "src" / "data" / "saints.json").read_text(encoding="utf-8"))
    out = []
    for p in data:
        e = html.escape
        feast = f" &middot; Feast: {e(p['feast'])}" if p.get("feast") else ""
        out.append(
            f'      <article class="card saint" data-status="{p["status"]}">'
            f'<span class="status s-{p["status"]}">{STATUS_LABEL[p["status"]]}</span>'
            f'<h3>{e(p["name"])}</h3><span class="meta">{e(p["years"])}{feast}</span>'
            f'<p>{e(p["bio"])}</p><span class="meta" style="margin-top:.4rem">{e(p["tags"][0].upper() + p["tags"][1:])}</span></article>')
    return "\n".join(out)


def glossary_html():
    data = json.loads((ROOT / "src" / "data" / "glossary.json").read_text(encoding="utf-8"))
    data.sort(key=lambda t: t[1].lower())
    out, letters, cur = [], [], None
    for slug, term, definition in data:
        L = term[0].upper()
        if L != cur:
            cur = L
            letters.append(L)
            out.append(f'    <div class="letter-head" id="letter-{L}">{L}</div>')
        out.append(f'    <dt id="{slug}">{html.escape(term)}</dt>\n    <dd>{html.escape(definition)}</dd>')
    alpha = "\n".join(f'    <a href="#letter-{L}">{L}</a>' for L in letters)
    return "\n".join(out), alpha


def version(rel):
    """Short content hash so browsers fetch new CSS/JS as soon as it changes."""
    return hashlib.sha1((OUT / rel.lstrip("/")).read_bytes()).hexdigest()[:10]


def bust(page):
    for rel in ("/assets/css/style.css", "/assets/js/main.js", "/assets/js/map.js"):
        page = page.replace(f'"{rel}"', f'"{rel}?v={version(rel)}"')
    return page


def nav_html(current):
    items = []
    for slug, label, *_ in PAGES:
        if slug in NAV_EXCLUDE:
            continue
        href = "/" if slug == "index" else f"/{slug}"
        cur = ' aria-current="page"' if slug == current else ""
        items.append(f'        <li><a href="{href}"{cur}>{label}</a></li>')
    return "\n".join(items)


def main():
    for slug, label, title, desc in PAGES:
        body = (PAGES_DIR / f"{slug}.html").read_text(encoding="utf-8")
        canonical = DOMAIN + ("/" if slug == "index" else f"/{slug}")
        eh, ef = EXTRA.get(slug, ("", ""))
        page = HEAD.format(title=title, desc=desc, canonical=canonical, domain=DOMAIN,
                           slug=slug, door=DOOR_SVG, menu=MENU_SVG, theme=THEME_SVG,
                           nav=nav_html(slug), extra_head=eh)
        body = body.replace("{{DOOR}}", DOOR_SVG)
        if "{{SAINTS}}" in body:
            body = body.replace("{{SAINTS}}", saints_html())
        if "{{GLOSSARY}}" in body:
            g, a = glossary_html()
            body = body.replace("{{GLOSSARY}}", g).replace("{{ALPHA}}", a)
        page += body
        page += FOOT.format(extra_foot=ef)
        (OUT / f"{slug}.html").write_text(bust(page), encoding="utf-8")
        print("built", slug)

    today = datetime.date.today().isoformat()
    urls = "\n".join(
        f"  <url><loc>{DOMAIN}{'/' if s == 'index' else '/' + s}</loc><lastmod>{today}</lastmod></url>"
        for s, *_ in PAGES if s != "404")
    (OUT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n',
        encoding="utf-8")


if __name__ == "__main__":
    main()
