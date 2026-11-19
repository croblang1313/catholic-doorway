"""Catholic Terms extras: theme filters, related terms, and the three visual guides
(Anatomy of a Catholic Church, What Priests & Deacons Wear, Inside the Mass).

features.render() calls render(body, lang); each {{PLACEHOLDER}} below is replaced
with HTML built from src/data/glossary*.json, glossary_meta.json and mass*.json.
All drawings are original inline SVG.
"""
from pathlib import Path
import hashlib
import html
import json
import unicodedata

DATA = Path(__file__).resolve().parent / "data"
SITE = Path(__file__).resolve().parent.parent / "site"
e = html.escape


def _load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def _fold(t):
    return unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()


def _script():
    try:
        v = hashlib.sha1((SITE / "assets/js/visual.js").read_bytes()).hexdigest()[:10]
    except FileNotFoundError:
        v = "0"
    return f'<script src="/assets/js/visual.js?v={v}" defer></script>'


# URLs of the Catholic Terms page and the three guides in each language
URL = {
    "terms": {"en": "/glossary", "es": "/es/glosario", "pt": "/pt/glossario", "tl": "/tl/glosaryo"},
    "anatomy": {"en": "/church-anatomy", "es": "/es/partes-de-la-iglesia", "pt": "/pt/partes-da-igreja", "tl": "/tl/mga-bahagi-ng-simbahan"},
    "vestments": {"en": "/vestments", "es": "/es/vestiduras", "pt": "/pt/vestes-liturgicas", "tl": "/tl/kasuotan-ng-pari"},
    "mass": {"en": "/inside-the-mass", "es": "/es/dentro-de-la-misa", "pt": "/pt/por-dentro-da-missa", "tl": "/tl/sa-loob-ng-misa"},
    "first-mass": {"en": "/first-mass", "es": "/es/primera-misa", "pt": "/pt/primeira-missa", "tl": "/tl/unang-misa"},
}

# Page names, used in menus (build.py), cards and links
NAME = {
    "anatomy": {"en": "Anatomy of a Catholic Church", "es": "Las partes de una iglesia", "pt": "As partes de uma igreja", "tl": "Mga bahagi ng simbahan"},
    "vestments": {"en": "What Priests & Deacons Wear", "es": "Lo que visten sacerdotes y diáconos", "pt": "O que padres e diáconos vestem", "tl": "Ang suot ng pari at diyakono"},
    "mass": {"en": "Inside the Mass", "es": "Dentro de la Misa", "pt": "Por dentro da Missa", "tl": "Sa loob ng Misa"},
}

BLURB = {
    "anatomy": {"en": "Tap your way around a church: nave, sanctuary, altar, tabernacle, ambo, votive candles and more.",
                "es": "Recorre una iglesia tocando cada parte: nave, presbiterio, altar, sagrario, ambón, velas votivas y más.",
                "pt": "Percorra uma igreja tocando cada parte: nave, presbitério, altar, sacrário, ambão, velas votivas e mais.",
                "tl": "Libutin ang simbahan sa pagpindot sa bawat bahagi: nave, santuwaryo, altar, tabernakulo, ambo, kandila at iba pa."},
    "vestments": {"en": "Alb, stole, chasuble, dalmatic and cassock, and why the colors change through the year.",
                  "es": "Alba, estola, casulla, dalmática y sotana, y por qué cambian los colores durante el año.",
                  "pt": "Alva, estola, casula, dalmática e batina, e por que as cores mudam ao longo do ano.",
                  "tl": "Alba, estola, kasulya, dalmatika at sotana, at kung bakit nagbabago ang mga kulay sa buong taon."},
    "mass": {"en": "Why Catholics stand, sit, kneel and respond when they do, part by part.",
             "es": "Por qué los católicos se ponen de pie, se sientan, se arrodillan y responden en cada momento.",
             "pt": "Por que os católicos ficam de pé, sentam, ajoelham e respondem em cada momento.",
             "tl": "Kung bakit tumatayo, umuupo, lumuluhod at sumasagot ang mga Katoliko sa bawat bahagi."},
}

W = {
    "all": {"en": "All Terms", "es": "Todos", "pt": "Todos", "tl": "Lahat"},
    "browse": {"en": "Browse by Theme", "es": "Explorar por tema", "pt": "Explorar por tema", "tl": "Tingnan ayon sa paksa"},
    "related": {"en": "Related Terms", "es": "Términos relacionados", "pt": "Termos relacionados", "tl": "Kaugnay na mga termino"},
    "guides": {"en": "Visual Guides", "es": "Guías visuales", "pt": "Guias visuais", "tl": "Mga gabay na may larawan"},
    "see_church": {"en": "See it on the church map", "es": "Verlo en el plano de la iglesia", "pt": "Ver no mapa da igreja", "tl": "Tingnan sa mapa ng simbahan"},
    "see_vest": {"en": "See it in the vestments guide", "es": "Verlo en la guía de vestiduras", "pt": "Ver no guia das vestes", "tl": "Tingnan sa gabay sa kasuotan"},
    "terms": {"en": "Catholic Terms", "es": "Términos católicos", "pt": "Termos católicos", "tl": "Mga terminong Katoliko"},
    "showing": {"en": "Showing", "es": "Mostrando", "pt": "Mostrando", "tl": "Ipinapakita"},
}


def guide_cards(lang, skip=None):
    cards = []
    for k in ("anatomy", "mass", "vestments"):
        if k == skip:
            continue
        cards.append(f'<a class="card guide-card" href="{URL[k][lang]}">{ICON[k]}<span><strong>{e(NAME[k][lang])}</strong>'
                     f'<span class="small muted">{e(BLURB[k][lang])}</span></span></a>')
    return '<div class="grid guide-cards">' + "".join(cards) + "</div>"


def _terms(lang):
    return _load("glossary.json" if lang == "en" else f"glossary_{lang}.json")


def term_index(lang):
    return {s: (t, d) for s, t, d in _terms(lang)}


# ---------------------------------------------------------------- Catholic Terms page
def terms_html(lang):
    meta = _load("glossary_meta.json")
    cats, tmeta = meta["cats"], meta["terms"]
    data = sorted(_terms(lang), key=lambda t: _fold(t[1]))
    names = {s: t for s, t, _ in data}
    on_map = set(ANATOMY_ORDER) | {"chalice", "paten", "ciborium", "monstrance"}
    on_vest = set(VEST_TERMS)
    out, letters, cur = [], [], None
    for slug, term, definition in data:
        L = _fold(term)[0].upper()
        if L != cur:
            cur = L
            letters.append(L)
            out.append(f'    <div class="letter-head" id="letter-{L}">{L}</div>')
        m = tmeta.get(slug, {"c": [], "r": []})
        rel = sorted(m["r"], key=lambda s: _fold(names[s]))
        extra = ""
        if rel:
            links = ", ".join(f'<a href="#{s}">{e(names[s])}</a>' for s in rel)
            extra += f'<p class="related"><span>{W["related"][lang]}:</span> {links}</p>'
        tags = "".join(f'<button type="button" class="tag" data-cat="{c}">{e(cats[c][lang])}</button>' for c in m["c"])
        see = ""
        if slug in on_map:
            see = f' <a class="see" href="{URL["anatomy"][lang]}#{slug}">{W["see_church"][lang]} &rarr;</a>'
        elif slug in on_vest:
            see = f' <a class="see" href="{URL["vestments"][lang]}#{slug}">{W["see_vest"][lang]} &rarr;</a>'
        out.append(f'    <dt id="{slug}" data-cats="{" ".join(m["c"])}">{e(term)}</dt>\n'
                   f'    <dd data-cats="{" ".join(m["c"])}"><p>{e(definition)}</p>{extra}<p class="tags">{tags}{see}</p></dd>')
    alpha = "\n".join(f'    <a href="#letter-{L}">{L}</a>' for L in letters)
    order = sorted(cats, key=lambda c: _fold(cats[c][lang]))
    chips = [f'<button type="button" class="chip" data-cat="" aria-pressed="true">{W["all"][lang]}</button>']
    for c in order:
        n = sum(1 for s in names if c in tmeta.get(s, {"c": []})["c"])
        chips.append(f'<button type="button" class="chip" data-cat="{c}" aria-pressed="false">{e(cats[c][lang])} <span class="n">{n}</span></button>')
    chip_html = (f'<div class="term-cats" role="group" aria-label="{W["browse"][lang]}">'
                 f'<p class="label">{W["browse"][lang]}</p>{"".join(chips)}</div>')
    return "\n".join(out), alpha, chip_html


def render_terms(body, lang):
    if "{{TERMS}}" not in body:
        return body
    g, a, c = terms_html(lang)
    return (body.replace("{{TERMS}}", g).replace("{{TERMS_ALPHA}}", a).replace("{{TERM_CATS}}", c)
            .replace("{{TERM_COUNT}}", str(len(_terms(lang)))).replace("{{GUIDE_CARDS}}", guide_cards(lang))
            .replace("{{VISUAL_JS}}", _script()))


# ---------------------------------------------------------------- small icons
ICON = {
    "anatomy": '<svg class="gicon" viewBox="0 0 48 48" aria-hidden="true"><path d="M14 44V22a10 10 0 0 1 20 0v22" fill="none" stroke="currentColor" stroke-width="2.5"/><path d="M8 44h32" stroke="currentColor" stroke-width="2.5"/><path d="M24 4v10M20 8h8" stroke="currentColor" stroke-width="2.5"/><rect x="20" y="30" width="8" height="14" fill="none" stroke="currentColor" stroke-width="2"/></svg>',
    "vestments": '<svg class="gicon" viewBox="0 0 48 48" aria-hidden="true"><circle cx="24" cy="8" r="5" fill="none" stroke="currentColor" stroke-width="2.5"/><path d="M14 18q10-6 20 0l6 22H8z" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round"/><path d="M24 15v25M18 30h12" stroke="currentColor" stroke-width="2.5"/></svg>',
    "mass": '<svg class="gicon" viewBox="0 0 48 48" aria-hidden="true"><path d="M15 10h18l-3 14a6 6 0 0 1-12 0z" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round"/><path d="M24 30v10M17 42h14" stroke="currentColor" stroke-width="2.5"/><circle cx="24" cy="5" r="3" fill="currentColor"/></svg>',
}

# Posture figures (used on Inside the Mass)
POSE_SVG = {
    "stand": '<svg class="pfig" viewBox="0 0 40 56" aria-hidden="true"><circle cx="20" cy="7" r="5"/><path d="M20 13v20M20 33l-6 20M20 33l6 20M20 17l-8 13M20 17l8 13"/></svg>',
    "sit": '<svg class="pfig" viewBox="0 0 40 56" aria-hidden="true"><circle cx="15" cy="9" r="5"/><path d="M15 15v19h14v18M15 19l9 9"/><path class="seat" d="M6 36h28M8 36v16M32 36v16"/></svg>',
    "kneel": '<svg class="pfig" viewBox="0 0 40 56" aria-hidden="true"><circle cx="18" cy="7" r="5"/><path d="M18 13v20l2 17h14M18 17l7 7 4-6"/><path class="seat" d="M10 50h28"/></svg>',
    "any": '<svg class="pfig" viewBox="0 0 40 56" aria-hidden="true"><circle cx="20" cy="9" r="5"/><path d="M20 15v18M20 33l-6 19M20 33l6 19M20 19l-7 11M20 19l7 11"/><path class="seat" d="M4 8h6M30 8h6" stroke-dasharray="2 3"/></svg>',
}

# ---------------------------------------------------------------- Anatomy of a Catholic Church
# Walking order from the front doors to the tabernacle, with marker position on the plan
ANATOMY_ORDER = ["narthex", "holy-water", "baptismal-font", "nave", "pew", "kneeler", "stations-of-the-cross",
                 "votive-candles", "confessional", "sanctuary", "ambo", "altar", "crucifix", "presider-chair",
                 "tabernacle", "sanctuary-lamp"]
MARK = {"narthex": (300, 800), "holy-water": (214, 758), "baptismal-font": (300, 716), "nave": (300, 470),
        "pew": (440, 610), "kneeler": (155, 649), "stations-of-the-cross": (112, 395), "votive-candles": (55, 455),
        "confessional": (545, 676), "sanctuary": (450, 236), "ambo": (176, 196), "altar": (300, 196),
        "crucifix": (256, 142), "presider-chair": (412, 176), "tabernacle": (300, 74), "sanctuary-lamp": (350, 74)}

AT = {
    "kicker": {"en": "Visual Guide", "es": "Guía visual", "pt": "Guia visual", "tl": "Gabay na may larawan"},
    "lede": {"en": "What will you see when you walk into a Catholic church? Tap a number on the plan, or walk through the list from the front doors to the tabernacle.",
             "es": "¿Qué verás al entrar en una iglesia católica? Toca un número en el plano o recorre la lista desde la puerta hasta el sagrario.",
             "pt": "O que você vai ver ao entrar numa igreja católica? Toque num número do mapa ou percorra a lista da porta até o sacrário.",
             "tl": "Ano ang makikita mo pagpasok sa isang simbahang Katoliko? Pindutin ang isang numero sa mapa, o sundan ang listahan mula sa pintuan hanggang sa tabernakulo."},
    "plan": {"en": "Floor plan of a typical Catholic church, seen from above", "es": "Plano de una iglesia católica típica, visto desde arriba",
             "pt": "Planta de uma igreja católica típica, vista de cima", "tl": "Mapa ng karaniwang simbahang Katoliko, tanaw mula sa itaas"},
    "doors": {"en": "Main doors", "es": "Puerta principal", "pt": "Porta principal", "tl": "Pangunahing pintuan"},
    "front": {"en": "Front", "es": "Frente", "pt": "Frente", "tl": "Harapan"},
    "tap": {"en": "Tap a number to learn what it is.", "es": "Toca un número para saber qué es.", "pt": "Toque num número para saber o que é.", "tl": "Pindutin ang isang numero para malaman kung ano ito."},
    "walk": {"en": "Walking In, Step by Step", "es": "Al entrar, paso a paso", "pt": "Entrando, passo a passo", "tl": "Pagpasok, hakbang-hakbang"},
    "vessels": {"en": "On the Altar", "es": "Sobre el altar", "pt": "Sobre o altar", "tl": "Sa ibabaw ng altar"},
    "vessels_lede": {"en": "During Mass you will also see these sacred vessels.", "es": "Durante la Misa verás también estos vasos sagrados.",
                     "pt": "Durante a Missa você verá também estes vasos sagrados.", "tl": "Sa Misa, makikita mo rin ang mga banal na sisidlang ito."},
    "tips": {"en": "Good to Know as a Visitor", "es": "Bueno saberlo si vienes de visita", "pt": "Bom saber se você está de visita", "tl": "Mabuting malaman bilang bisita"},
    "tip_list": {"en": ["Catholics dip their fingers in holy water and make the Sign of the Cross as they come in, recalling their Baptism. You are welcome to skip it.",
                        "Before entering a pew, Catholics genuflect (bend the right knee) toward the tabernacle. A bow works too, and visitors may simply sit.",
                        "If the red sanctuary lamp is lit, Christ is present in the tabernacle, so people keep their voices low.",
                        "Every church differs: some have the tabernacle in a side chapel, some have the font in its own room. The pieces are the same."],
                 "es": ["Al entrar, los católicos mojan los dedos en agua bendita y hacen la señal de la cruz, recordando su Bautismo. Puedes omitirlo.",
                        "Antes de entrar en la banca, los católicos hacen una genuflexión (doblan la rodilla derecha) hacia el sagrario. Una inclinación también vale, y los visitantes pueden simplemente sentarse.",
                        "Si la lámpara roja está encendida, Cristo está presente en el sagrario, por eso se habla en voz baja.",
                        "Cada iglesia es distinta: en algunas el sagrario está en una capilla lateral y en otras la pila bautismal tiene su propio espacio. Las partes son las mismas."],
                 "pt": ["Ao entrar, os católicos molham os dedos na água benta e fazem o sinal da cruz, lembrando o seu Batismo. Você pode deixar de fazer.",
                        "Antes de entrar no banco, os católicos fazem genuflexão (dobram o joelho direito) em direção ao sacrário. Uma inclinação também serve, e os visitantes podem simplesmente sentar.",
                        "Se a lâmpada vermelha estiver acesa, Cristo está presente no sacrário, por isso se fala baixo.",
                        "Cada igreja é diferente: em algumas o sacrário fica numa capela lateral, em outras a pia batismal tem seu próprio espaço. As partes são as mesmas."],
                 "tl": ["Pagpasok, isinasawsaw ng mga Katoliko ang daliri sa agua bendita at nagtatanda ng krus, bilang pag-alala sa kanilang Binyag. Maaari mo itong laktawan.",
                        "Bago pumasok sa upuan, lumuluhod nang isang tuhod ang mga Katoliko (genuflect) paharap sa tabernakulo. Puwede rin ang pagyuko, at maaaring umupo na lang ang mga bisita.",
                        "Kapag nakasindi ang pulang ilawan, naroon si Kristo sa tabernakulo, kaya mahina ang boses ng mga tao.",
                        "Magkakaiba ang bawat simbahan: sa ilan, nasa gilid na kapilya ang tabernakulo, sa iba may sariling silid ang binyagan. Pareho pa rin ang mga bahagi."]},
    "more": {"en": "Look up more words in", "es": "Busca más palabras en", "pt": "Procure mais palavras em", "tl": "Maghanap ng iba pang salita sa"},
}


def church_svg(lang):
    s = []
    a = s.append
    a(f'<svg class="church-plan" viewBox="0 0 600 840" role="img" aria-labelledby="plan-t"><title id="plan-t">{e(AT["plan"][lang])}</title>')
    # walls and floor
    a('<path class="floor" d="M150 270V150A150 112 0 0 1 450 150V270H520V740H80V270Z"/>')
    a('<rect class="floor narthex" x="80" y="740" width="440" height="82"/>')
    a('<rect class="floor" x="32" y="400" width="48" height="110"/>')   # side shrine
    a('<rect class="floor" x="520" y="630" width="50" height="92"/>')   # confessional
    a('<path class="wall" d="M150 270V150A150 112 0 0 1 450 150V270H520V630M520 722V740H80V510M80 400V270H150M80 400H32V510H80M520 630H570V722H520M80 740V822H262M338 822H520V740M80 740H270M330 740H520"/>')
    # sanctuary floor and steps
    a('<path class="sanct" d="M150 262V150A150 112 0 0 1 450 150V262Z"/>')
    a('<path class="step" d="M150 262H450M140 270H460"/>')
    # aisle
    a('<rect class="aisle" x="280" y="280" width="40" height="460"/>')
    # pews with kneelers
    for i in range(12):
        y = 300 + i * 32
        a(f'<rect class="pew" x="104" y="{y}" width="168" height="10" rx="2"/><rect class="kneel" x="104" y="{y + 15}" width="168" height="3"/>')
        a(f'<rect class="pew" x="328" y="{y}" width="168" height="10" rx="2"/><rect class="kneel" x="328" y="{y + 15}" width="168" height="3"/>')
    # stations of the cross on side walls
    for i in range(7):
        y = 300 + i * 58
        if not (400 <= y <= 512):
            a(f'<path class="station" d="M88 {y}v12M83 {y + 4}h10"/>')
        if not (624 <= y <= 724):
            a(f'<path class="station" d="M512 {y}v12M507 {y + 4}h10"/>')
    # votive candles in the side shrine, with a statue
    a('<circle class="statue" cx="44" cy="420" r="7"/>')
    for r in range(3):
        for c in range(3):
            a(f'<circle class="votive" cx="{50 + c * 9}" cy="{438 + r * 9}" r="3"/>')
    # confessional: priest's side, screen, penitent's side
    a('<path class="screen" d="M545 632V720"/><rect class="chair" x="552" y="668" width="12" height="12" rx="2"/><rect class="kneel" x="528" y="650" width="12" height="4"/>')
    # baptismal font
    a('<path class="font" d="M291 700h18l7 7v18l-7 7h-18l-7-7v-18z"/><circle class="water" cx="300" cy="716" r="8"/>')
    # holy water fonts at the inner doors
    a('<circle class="water" cx="252" cy="752" r="6"/><circle class="water" cx="348" cy="752" r="6"/>')
    # sanctuary furnishings
    a('<rect class="altar" x="245" y="178" width="110" height="38" rx="3"/><path class="cloth" d="M245 186h110"/>')
    a('<rect class="ambo" x="190" y="206" width="26" height="20" rx="3"/>')
    a('<path class="chair" d="M398 150h28v22h-28z"/><path class="cross" d="M300 122v32M290 132h20"/>')
    a('<rect class="taber" x="286" y="84" width="28" height="24" rx="3"/><path class="taber-door" d="M300 88v16"/>')
    a('<circle class="lamp" cx="336" cy="96" r="6"/>')
    # labels
    a(f'<text class="plan-label" x="300" y="836" text-anchor="middle">{e(AT["doors"][lang])} &#8595;</text>')
    a(f'<text class="plan-label" x="300" y="30" text-anchor="middle">&#8593; {e(AT["front"][lang])}</text>')
    # numbered hotspots
    names = term_index(lang)
    for i, k in enumerate(ANATOMY_ORDER, 1):
        x, y = MARK[k]
        a(f'<g class="hot" data-k="{k}" tabindex="0" role="button" aria-label="{i}. {e(names[k][0])}">'
          f'<circle cx="{x}" cy="{y}" r="14"/><text x="{x}" y="{y + 5}" text-anchor="middle">{i}</text></g>')
    a('</svg>')
    return "".join(s)


VESSEL_SVG = {
    "chalice": '<svg viewBox="0 0 60 60" aria-hidden="true"><path d="M17 8h26q0 20-13 24Q17 28 17 8z"/><path d="M30 32v14M20 52h20l-4-6H24z"/></svg>',
    "paten": '<svg viewBox="0 0 60 60" aria-hidden="true"><ellipse cx="30" cy="36" rx="24" ry="8"/><ellipse cx="30" cy="32" rx="11" ry="4" class="host"/></svg>',
    "ciborium": '<svg viewBox="0 0 60 60" aria-hidden="true"><path d="M30 4v6M27 7h6M18 12h24q2 6-2 8H20q-4-2-2-8z"/><path d="M16 22h28q0 14-14 16Q16 36 16 22z"/><path d="M30 38v8M20 52h20l-4-6H24z"/></svg>',
    "monstrance": '<svg viewBox="0 0 60 60" aria-hidden="true"><circle cx="30" cy="22" r="7" class="host"/><path d="M30 4v6M30 34v4M12 22h6M42 22h6M17 9l4 4M43 9l-4 4M17 35l4-4M43 35l-4-4"/><circle cx="30" cy="22" r="11"/><path d="M30 38v8M20 54h20l-4-8H24z"/></svg>',
}


def anatomy_html(lang):
    names = term_index(lang)
    t = URL["terms"][lang]
    rows = []
    for i, k in enumerate(ANATOMY_ORDER, 1):
        n, d = names[k]
        rows.append(f'<li id="{k}" data-k="{k}"><button type="button" class="an-item"><span class="an-no">{i}</span>'
                    f'<span><strong>{e(n)}</strong><span class="an-def">{e(d)}</span></span></button>'
                    f'<a class="small" href="{t}#{k}">{W["terms"][lang]} &rarr;</a></li>')
    vessels = "".join(f'<div class="card vessel" id="{k}">{VESSEL_SVG[k]}<h3>{e(names[k][0])}</h3><p>{e(names[k][1])}</p></div>'
                      for k in ("chalice", "paten", "ciborium", "monstrance"))
    tips = "".join(f"<li>{e(x)}</li>" for x in AT["tip_list"][lang])
    return f'''<div class="page-head">
  <div class="wrap">
    <p class="kicker"><a href="{t}">{W["terms"][lang]}</a> &rsaquo; {AT["kicker"][lang]}</p>
    <h1>{e(NAME["anatomy"][lang])}</h1>
    <p class="lede">{AT["lede"][lang]}</p>
  </div>
</div>
<div class="wrap">
  <div class="anatomy">
    <figure class="plan-wrap">{church_svg(lang)}
      <figcaption class="plan-info" id="plan-info" aria-live="polite"><span class="muted">{AT["tap"][lang]}</span></figcaption>
    </figure>
    <section class="an-list">
      <h2>{AT["walk"][lang]}</h2>
      <ol class="an-steps">{"".join(rows)}</ol>
    </section>
  </div>
  <section class="section">
    <h2>{AT["vessels"][lang]}</h2>
    <p>{AT["vessels_lede"][lang]}</p>
    <div class="grid vessels">{vessels}</div>
  </section>
  <section class="section prose">
    <h2>{AT["tips"][lang]}</h2>
    <ul>{tips}</ul>
    <p>{AT["more"][lang]} <a href="{t}">{W["terms"][lang]}</a>.</p>
  </section>
  <section class="section">
    <h2>{W["guides"][lang]}</h2>
    {guide_cards(lang, skip="anatomy")}
  </section>
</div>
{_script()}'''


# ---------------------------------------------------------------- What Priests & Deacons Wear
VEST_TERMS = ["alb", "cincture", "stole", "chasuble", "dalmatic", "cassock", "surplice", "clerical-collar", "cope",
              "mitre", "crozier", "zucchetto", "liturgical-colors", "vestments"]

COLORS = [  # key, swatch
    ("violet", "#6a3f8a"), ("white", "#f4efe2"), ("red", "#a8322d"), ("green", "#3f7a4a"), ("rose", "#d48aa0"), ("black", "#2b2b30")]

VT = {
    "kicker": AT["kicker"],
    "lede": {"en": "The clothes worn at Mass are called vestments. Each piece has a purpose and a long history, and their color tells you what the Church is celebrating today.",
             "es": "La ropa que se usa en la Misa se llama vestiduras. Cada pieza tiene un sentido y una larga historia, y su color te dice qué celebra hoy la Iglesia.",
             "pt": "As roupas usadas na Missa se chamam paramentos. Cada peça tem um sentido e uma longa história, e a cor mostra o que a Igreja celebra hoje.",
             "tl": "Ang mga kasuotan sa Misa ay tinatawag na kasuotang pang-liturhiya. Bawat piraso ay may layunin at mahabang kasaysayan, at sinasabi ng kulay nito kung ano ang ipinagdiriwang ng Simbahan ngayon."},
    "dress": {"en": "Dress a Priest for Mass", "es": "Viste a un sacerdote para la Misa", "pt": "Vista um padre para a Missa", "tl": "Bihisan ang pari para sa Misa"},
    "dress_lede": {"en": "A priest puts his vestments on in this order. Tap each layer, then try the colors of the year.",
                   "es": "El sacerdote se pone las vestiduras en este orden. Toca cada capa y luego prueba los colores del año.",
                   "pt": "O padre veste os paramentos nesta ordem. Toque em cada camada e depois experimente as cores do ano.",
                   "tl": "Sa ganitong pagkakasunod isinusuot ng pari ang kanyang kasuotan. Pindutin ang bawat patong, pagkatapos subukan ang mga kulay ng taon."},
    "layers": {"en": "Layers", "es": "Capas", "pt": "Camadas", "tl": "Mga patong"},
    "color": {"en": "Color", "es": "Color", "pt": "Cor", "tl": "Kulay"},
    "fig": {"en": "Drawing of a priest in Mass vestments", "es": "Dibujo de un sacerdote con las vestiduras de la Misa",
            "pt": "Desenho de um padre com os paramentos da Missa", "tl": "Larawan ng pari na nakasuot pang-Misa"},
    "who": {"en": "Who Wears What", "es": "Quién viste qué", "pt": "Quem veste o quê", "tl": "Sino ang nagsusuot ng ano"},
    "priest": {"en": "Priest at Mass", "es": "Sacerdote en la Misa", "pt": "Padre na Missa", "tl": "Pari sa Misa"},
    "deacon": {"en": "Deacon at Mass", "es": "Diácono en la Misa", "pt": "Diácono na Missa", "tl": "Diyakono sa Misa"},
    "bishop": {"en": "Bishop", "es": "Obispo", "pt": "Bispo", "tl": "Obispo"},
    "street": {"en": "Priest or Deacon, Every Day", "es": "Sacerdote o diácono, a diario", "pt": "Padre ou diácono, no dia a dia", "tl": "Pari o diyakono, araw-araw"},
    "priest_note": {"en": "The stole hangs straight down from both shoulders, under the chasuble.",
                    "es": "La estola cae recta desde los dos hombros, debajo de la casulla.",
                    "pt": "A estola cai reta dos dois ombros, por baixo da casula.",
                    "tl": "Nakalaylay nang tuwid mula sa dalawang balikat ang estola, sa ilalim ng kasulya."},
    "deacon_note": {"en": "The stole crosses from his left shoulder to his right side. Over it he may wear a dalmatic, with sleeves.",
                    "es": "La estola cruza desde su hombro izquierdo hasta el costado derecho. Encima puede llevar una dalmática, con mangas.",
                    "pt": "A estola cruza do ombro esquerdo até o lado direito. Por cima ele pode usar uma dalmática, com mangas.",
                    "tl": "Pahilis ang estola mula sa kaliwang balikat hanggang kanang tagiliran. Sa ibabaw nito, maaari siyang magsuot ng dalmatika na may manggas."},
    "bishop_note": {"en": "The same vestments as a priest, plus the mitre, the crozier and a small cap, the zucchetto.",
                    "es": "Las mismas vestiduras que un sacerdote, más la mitra, el báculo y un pequeño gorro, el solideo.",
                    "pt": "Os mesmos paramentos de um padre, mais a mitra, o báculo e um pequeno barrete, o solidéu.",
                    "tl": "Kapareho ng sa pari, dagdag ang mitra, ang baculo at isang maliit na takip sa ulo, ang solideo."},
    "street_note": {"en": "Outside of Mass, clergy usually wear black with a white clerical collar, or a cassock.",
                    "es": "Fuera de la Misa, el clero suele vestir de negro con alzacuellos blanco, o con sotana.",
                    "pt": "Fora da Missa, o clero costuma vestir preto com colarinho clerical branco, ou batina.",
                    "tl": "Sa labas ng Misa, kadalasang nakaitim ang klero na may puting kuwelyo, o nakasotana."},
    "year": {"en": "Why the Colors Change", "es": "Por qué cambian los colores", "pt": "Por que as cores mudam", "tl": "Kung bakit nagbabago ang mga kulay"},
    "year_lede": {"en": "The Church year is a cycle that walks through the life of Christ, beginning with Advent. The vestment color is a quick signal of which season or feast it is.",
                  "es": "El año litúrgico es un ciclo que recorre la vida de Cristo y empieza en Adviento. El color de las vestiduras indica de un vistazo qué tiempo o fiesta es.",
                  "pt": "O ano litúrgico é um ciclo que percorre a vida de Cristo, começando no Advento. A cor dos paramentos mostra num relance qual é o tempo ou a festa.",
                  "tl": "Ang taon ng Simbahan ay isang ikot na sumusunod sa buhay ni Kristo, simula sa Adbiyento. Ang kulay ng kasuotan ay mabilis na hudyat kung anong panahon o kapistahan ngayon."},
    "wheel": {"en": "The Church year as a circle, starting with Advent at the top", "es": "El año litúrgico como un círculo, con el Adviento arriba",
              "pt": "O ano litúrgico como um círculo, com o Advento no alto", "tl": "Ang taon ng Simbahan bilang bilog, Adbiyento sa itaas"},
    "when": {"en": "When", "es": "Cuándo", "pt": "Quando", "tl": "Kailan"},
    "means": {"en": "Meaning", "es": "Significado", "pt": "Significado", "tl": "Kahulugan"},
    "today": {"en": "Today's color", "es": "El color de hoy", "pt": "A cor de hoje", "tl": "Kulay ngayon"},
    "today_link": {"en": "See today's feasts on the Holy Days Calendar", "es": "Mira las fiestas de hoy en el calendario", "pt": "Veja as festas de hoje no calendário", "tl": "Tingnan ang mga kapistahan ngayon sa kalendaryo"},
    "list": {"en": "Vestment by Vestment", "es": "Una por una", "pt": "Peça por peça", "tl": "Isa-isa"},
}
VT_LAYERS = {"en": ["Alb", "Cincture", "Stole", "Chasuble"], "es": ["Alba", "Cíngulo", "Estola", "Casulla"],
             "pt": ["Alva", "Cíngulo", "Estola", "Casula"], "tl": ["Alba", "Singulo", "Estola", "Kasulya"]}
CAL_URL = {"en": "/calendar", "es": "/es/calendario", "pt": "/pt/calendario", "tl": "/tl/kalendaryo"}

COLOR_TEXT = {
    "violet": {"en": ("Violet", "Advent and Lent. It may also be worn at funerals.", "Waiting, repentance and preparation."),
               "es": ("Morado", "Adviento y Cuaresma. También puede usarse en funerales.", "Espera, penitencia y preparación."),
               "pt": ("Roxo", "Advento e Quaresma. Também pode ser usado em funerais.", "Espera, penitência e preparação."),
               "tl": ("Lila", "Adbiyento at Kuwaresma. Maaari ring gamitin sa libing.", "Paghihintay, pagsisisi at paghahanda.")},
    "white": {"en": ("White or Gold", "Christmas and Easter seasons, Holy Thursday, feasts of the Lord, Mary, the angels and saints who were not martyrs. Often at weddings and funerals.", "Joy, purity and the glory of the Resurrection."),
              "es": ("Blanco o dorado", "Navidad y Pascua, el Jueves Santo, las fiestas del Señor, de la Virgen, de los ángeles y de los santos no mártires. A menudo en bodas y funerales.", "Alegría, pureza y la gloria de la Resurrección."),
              "pt": ("Branco ou dourado", "Natal e Páscoa, Quinta-feira Santa, festas do Senhor, de Nossa Senhora, dos anjos e dos santos não mártires. Muitas vezes em casamentos e funerais.", "Alegria, pureza e a glória da Ressurreição."),
              "tl": ("Puti o ginto", "Panahon ng Pasko at Muling Pagkabuhay, Huwebes Santo, mga kapistahan ng Panginoon, ni Maria, ng mga anghel at ng mga santong hindi martir. Madalas sa kasal at libing.", "Kagalakan, kadalisayan at kaluwalhatian ng Muling Pagkabuhay.")},
    "red": {"en": ("Red", "Palm Sunday, Good Friday, Pentecost, Confirmation, and feasts of the Apostles, Evangelists and martyrs.", "The fire of the Holy Spirit and the blood of those who gave their lives for Christ."),
            "es": ("Rojo", "Domingo de Ramos, Viernes Santo, Pentecostés, la Confirmación y las fiestas de apóstoles, evangelistas y mártires.", "El fuego del Espíritu Santo y la sangre de quienes dieron la vida por Cristo."),
            "pt": ("Vermelho", "Domingo de Ramos, Sexta-feira Santa, Pentecostes, a Crisma e as festas de apóstolos, evangelistas e mártires.", "O fogo do Espírito Santo e o sangue dos que deram a vida por Cristo."),
            "tl": ("Pula", "Linggo ng Palaspas, Biyernes Santo, Pentekostes, Kumpil, at mga kapistahan ng mga apostol, ebanghelista at martir.", "Ang apoy ng Espiritu Santo at ang dugo ng mga nag-alay ng buhay para kay Kristo.")},
    "green": {"en": ("Green", "Ordinary Time, the longest part of the year, between Christmas and Lent and from Pentecost to Advent.", "Hope, life and steady growth in faith."),
              "es": ("Verde", "El Tiempo Ordinario, la parte más larga del año, entre Navidad y Cuaresma y de Pentecostés a Adviento.", "Esperanza, vida y crecimiento constante en la fe."),
              "pt": ("Verde", "O Tempo Comum, a parte mais longa do ano, entre o Natal e a Quaresma e de Pentecostes ao Advento.", "Esperança, vida e crescimento constante na fé."),
              "tl": ("Berde", "Karaniwang Panahon, ang pinakamahabang bahagi ng taon, sa pagitan ng Pasko at Kuwaresma at mula Pentekostes hanggang Adbiyento.", "Pag-asa, buhay at patuloy na paglago sa pananampalataya.")},
    "rose": {"en": ("Rose", "May be worn on two Sundays: the third Sunday of Advent (Gaudete) and the fourth Sunday of Lent (Laetare).", "Joy breaking through: the waiting is more than half over."),
             "es": ("Rosa", "Puede usarse dos domingos: el tercero de Adviento (Gaudete) y el cuarto de Cuaresma (Laetare).", "La alegría que se asoma: ya pasó más de la mitad de la espera."),
             "pt": ("Rosa", "Pode ser usado em dois domingos: o terceiro do Advento (Gaudete) e o quarto da Quaresma (Laetare).", "A alegria que desponta: mais da metade da espera já passou."),
             "tl": ("Rosas", "Maaaring gamitin sa dalawang Linggo: ikatlong Linggo ng Adbiyento (Gaudete) at ikaapat na Linggo ng Kuwaresma (Laetare).", "Sumisilip na kagalakan: lampas na sa kalahati ang paghihintay.")},
    "black": {"en": ("Black", "May be worn at funerals and on All Souls' Day (November 2).", "Mourning, and prayer for those who have died."),
              "es": ("Negro", "Puede usarse en funerales y el Día de los Fieles Difuntos (2 de noviembre).", "Luto y oración por los difuntos."),
              "pt": ("Preto", "Pode ser usado em funerais e no Dia de Finados (2 de novembro).", "Luto e oração pelos falecidos."),
              "tl": ("Itim", "Maaaring gamitin sa libing at sa Araw ng mga Kaluluwa (Nobyembre 2).", "Pagdadalamhati at panalangin para sa mga yumao.")},
}

# Church year wheel: (label key, weeks, color)
SEASONS = [("advent", 4, "violet"), ("christmas", 2.5, "white"), ("ot1", 7, "green"), ("lent", 5.5, "violet"),
           ("holyweek", 1, "red"), ("easter", 7, "white"), ("pentecost", .6, "red"), ("ot2", 24.4, "green")]
SEASON_NAME = {
    "advent": {"en": "Advent", "es": "Adviento", "pt": "Advento", "tl": "Adbiyento"},
    "christmas": {"en": "Christmas", "es": "Navidad", "pt": "Natal", "tl": "Pasko"},
    "ot1": {"en": "Ordinary Time", "es": "Tiempo Ordinario", "pt": "Tempo Comum", "tl": "Karaniwang Panahon"},
    "lent": {"en": "Lent", "es": "Cuaresma", "pt": "Quaresma", "tl": "Kuwaresma"},
    "holyweek": {"en": "Holy Week", "es": "Semana Santa", "pt": "Semana Santa", "tl": "Semana Santa"},
    "easter": {"en": "Easter", "es": "Pascua", "pt": "Páscoa", "tl": "Muling Pagkabuhay"},
    "pentecost": {"en": "Pentecost", "es": "Pentecostés", "pt": "Pentecostes", "tl": "Pentekostes"},
    "ot2": {"en": "Ordinary Time", "es": "Tiempo Ordinario", "pt": "Tempo Comum", "tl": "Karaniwang Panahon"},
}


def _figure(kind, label=""):
    """kind: layered | priest | deacon | bishop | street."""
    p = []
    a = p.append
    a(f'<svg class="vest-fig fig-{kind}" viewBox="0 0 200 400" role="img" aria-label="{e(label)}">')
    a('<ellipse class="shadow" cx="100" cy="388" rx="70" ry="8"/>')
    if kind == "street":
        a('<path class="cassock" d="M64 92Q100 80 136 92L148 382H52Z"/><path class="cassock" d="M64 92L40 232H58L74 130ZM136 92L160 232H142L126 130Z"/>')
        a('<g class="buttons">' + "".join(f'<circle cx="100" cy="{y}" r="1.8"/>' for y in range(96, 380, 12)) + '</g>')
        a('<rect class="collar" x="94" y="80" width="12" height="7" rx="1"/>')
    else:
        a('<g class="layer l-alb"><path class="alb" d="M64 92Q100 80 136 92L148 382H52Z"/>'
          '<path class="alb" d="M64 92L40 232H58L74 130ZM136 92L160 232H142L126 130Z"/><path class="fold" d="M84 140L78 380M116 140L122 380M100 110V382"/></g>')
        a('<g class="layer l-cinc"><path class="cinc" d="M70 198Q100 208 130 198"/><path class="cinc" d="M84 204L80 286M88 205L90 280"/></g>')
        if kind == "deacon":
            a('<g class="layer l-stole"><path class="lit" d="M118 84L134 94L86 246L74 236Z"/><path class="trim" d="M120 90L80 240"/></g>')
        else:
            a('<g class="layer l-stole"><path class="lit" d="M90 82L82 304H96L101 90Z"/><path class="lit" d="M110 82L118 304H104L99 90Z"/>'
              '<path class="trim" d="M89 290h6M92 286v8M111 290h6M114 286v8"/></g>')
        if kind in ("layered", "priest", "bishop"):
            a('<g class="layer l-chas"><path class="lit" d="M100 80Q60 84 34 122L24 334Q100 354 176 334L166 122Q140 84 100 80Z"/>'
              '<path class="orph" d="M92 84V346H108V84Z"/><path class="orph" d="M60 112Q100 150 140 112L136 104Q100 134 64 104Z"/>'
              '<path class="trim" d="M24 334Q100 354 176 334"/></g>')
    # head, hands
    a('<rect class="skin" x="92" y="68" width="16" height="16"/><circle class="skin" cx="100" cy="52" r="22"/>'
      '<path class="hair" d="M78 50Q80 26 100 28Q120 26 122 50Q116 36 100 38Q84 36 78 50Z"/>')
    a('<circle class="skin" cx="49" cy="238" r="9"/><circle class="skin" cx="151" cy="238" r="9"/>')
    if kind == "bishop":
        a('<path class="mitre" d="M80 42L83 4L100 16L117 4L120 42Q100 36 80 42Z"/><path class="orph" d="M97 13V40H103V13Z"/>'
          '<path class="crozier" d="M172 392V64M172 64Q172 30 150 32Q134 36 142 52Q150 60 158 50"/>')
    a('</svg>')
    return "".join(p)


def _wheel(lang):
    import math
    cx = cy = 160
    R, r = 132, 78
    total = sum(w for _, w, _ in SEASONS)
    sw = dict(COLORS)
    out = [f'<svg class="year-wheel" viewBox="0 0 320 320" role="img" aria-labelledby="wheel-t"><title id="wheel-t">{e(VT["wheel"][lang])}</title>']
    ang = -math.pi / 2
    for key, w, col in SEASONS:
        a2 = ang + 2 * math.pi * w / total
        large = 1 if a2 - ang > math.pi else 0
        p = lambda A, rad: (cx + rad * math.cos(A), cy + rad * math.sin(A))
        x1, y1 = p(ang, R); x2, y2 = p(a2, R); x3, y3 = p(a2, r); x4, y4 = p(ang, r)
        out.append(f'<path class="seg c-{col}" fill="{sw[col]}" data-c="{col}" d="M{x1:.1f} {y1:.1f}A{R} {R} 0 {large} 1 {x2:.1f} {y2:.1f}'
                   f'L{x3:.1f} {y3:.1f}A{r} {r} 0 {large} 0 {x4:.1f} {y4:.1f}Z"><title>{e(SEASON_NAME[key][lang])}</title></path>')
        if w >= 4:
            mid = (ang + a2) / 2
            tx, ty = p(mid, (R + r) / 2)
            out.append(f'<text class="seg-label{" dark" if col == "white" else ""}" x="{tx:.1f}" y="{ty + 4:.1f}" text-anchor="middle">{e(SEASON_NAME[key][lang])}</text>')
        ang = a2
    # rose Sundays (3rd of Advent, 4th of Lent) as small marks
    for weeks in (2.5, 4 + 2.5 + 7 + 3.5):
        A = -math.pi / 2 + 2 * math.pi * weeks / total
        out.append(f'<circle cx="{cx + (R + 10) * math.cos(A):.1f}" cy="{cy + (R + 10) * math.sin(A):.1f}" r="6" fill="{sw["rose"]}" stroke="var(--surface)" stroke-width="2"/>')
    out.append(f'<text class="wheel-mid" x="{cx}" y="{cy + 6}" text-anchor="middle">&#10013;</text></svg>')
    return "".join(out)


def vestments_html(lang):
    names = term_index(lang)
    t = URL["terms"][lang]
    lk = lambda k: f'<a href="{t}#{k}">{e(names[k][0])}</a>'
    layer_btn = "".join(f'<button type="button" class="chip" data-layer="{i}" aria-pressed="{"true" if i == 4 else "false"}">{i}. {e(n)}</button>'
                        for i, n in enumerate(VT_LAYERS[lang], 1))
    color_btn = "".join(f'<button type="button" class="swatch" data-color="{k}" style="--sw:{c}" aria-pressed="{"true" if k == "green" else "false"}">'
                        f'<span></span>{e(COLOR_TEXT[k][lang][0])}</button>' for k, c in COLORS)
    layer_text = "".join(f'<p class="layer-text" data-layer="{i}"{"" if i == 4 else " hidden"}><strong>{e(names[k][0])}.</strong> {e(names[k][1])}</p>'
                         for i, k in enumerate(["alb", "cincture", "stole", "chasuble"], 1))
    who = []
    for kind, terms in (("priest", ["alb", "stole", "chasuble"]), ("deacon", ["alb", "stole", "dalmatic"]),
                        ("bishop", ["mitre", "crozier", "zucchetto"]), ("street", ["cassock", "clerical-collar"])):
        who.append(f'<figure class="card who">{_figure(kind, VT[kind][lang])}<figcaption><h3>{e(VT[kind][lang])}</h3>'
                   f'<p class="small">{e(VT[kind + "_note"][lang])}</p><p class="small">{" · ".join(lk(k) for k in terms)}</p></figcaption></figure>')
    cards = "".join(f'<div class="card color-card" style="--sw:{c}"><span class="sw"></span><h3>{e(COLOR_TEXT[k][lang][0])}</h3>'
                    f'<p><strong>{VT["when"][lang]}:</strong> {e(COLOR_TEXT[k][lang][1])}</p><p><strong>{VT["means"][lang]}:</strong> {e(COLOR_TEXT[k][lang][2])}</p></div>'
                    for k, c in COLORS)
    vlist = "".join(f'<dt id="{k}">{e(names[k][0])}</dt><dd>{e(names[k][1])}</dd>' for k in VEST_TERMS)
    return f'''<div class="page-head">
  <div class="wrap">
    <p class="kicker"><a href="{t}">{W["terms"][lang]}</a> &rsaquo; {VT["kicker"][lang]}</p>
    <h1>{e(NAME["vestments"][lang])}</h1>
    <p class="lede">{VT["lede"][lang]}</p>
  </div>
</div>
<div class="wrap">
  <section class="section dress" id="dress">
    <div class="dress-fig" data-color="green" data-layer="4">{_figure("layered", VT["fig"][lang])}</div>
    <div>
      <h2>{VT["dress"][lang]}</h2>
      <p>{VT["dress_lede"][lang]}</p>
      <p class="label">{VT["layers"][lang]}</p>
      <div class="filters" role="group" aria-label="{VT["layers"][lang]}">{layer_btn}</div>
      <div aria-live="polite">{layer_text}</div>
      <p class="label">{VT["color"][lang]}</p>
      <div class="swatches" role="group" aria-label="{VT["color"][lang]}">{color_btn}</div>
    </div>
  </section>
  <section class="section">
    <h2>{VT["who"][lang]}</h2>
    <div class="grid who-grid">{"".join(who)}</div>
  </section>
  <section class="section" id="colors">
    <h2>{VT["year"][lang]}</h2>
    <p class="prose">{VT["year_lede"][lang]}</p>
    <div class="year">
      <div class="wheel-wrap">{_wheel(lang)}</div>
      <div class="grid color-cards">{cards}</div>
    </div>
    <p><a href="{CAL_URL[lang]}">{VT["today_link"][lang]} &rarr;</a></p>
  </section>
  <section class="section">
    <h2>{VT["list"][lang]}</h2>
    <dl class="glossary vest-list">{vlist}</dl>
  </section>
  <section class="section">
    <h2>{W["guides"][lang]}</h2>
    {guide_cards(lang, skip="vestments")}
  </section>
</div>
{_script()}'''


# ---------------------------------------------------------------- Inside the Mass
MT = {
    "kicker": AT["kicker"],
    "lede": {"en": "Catholics stand, sit, kneel and answer the priest at set moments. None of it is random: each posture and response says something with the body and voice. Here is the why behind each part.",
             "es": "Los católicos se ponen de pie, se sientan, se arrodillan y responden al sacerdote en momentos fijos. Nada es al azar: cada postura y cada respuesta dice algo con el cuerpo y la voz. Aquí está el porqué de cada parte.",
             "pt": "Os católicos ficam de pé, sentam, ajoelham e respondem ao padre em momentos certos. Nada é por acaso: cada postura e cada resposta diz algo com o corpo e a voz. Aqui está o porquê de cada parte.",
             "tl": "Tumatayo, umuupo, lumuluhod at sumasagot sa pari ang mga Katoliko sa takdang mga sandali. Walang basta-basta rito: bawat tindig at sagot ay may sinasabi sa katawan at tinig. Narito ang dahilan sa likod ng bawat bahagi."},
    "cta": {"en": "Going to Mass soon? Follow along step by step on your phone with", "es": "¿Vas a ir a Misa pronto? Síguela paso a paso en tu teléfono con",
            "pt": "Vai à Missa em breve? Acompanhe passo a passo no celular com", "tl": "Magsisimba ka ba? Sundan ito nang hakbang-hakbang sa iyong telepono gamit ang"},
    "first": {"en": "Your First Mass", "es": "Tu primera Misa", "pt": "Sua primeira Missa", "tl": "Ang iyong unang Misa"},
    "glance": {"en": "The Mass at a Glance", "es": "La Misa de un vistazo", "pt": "A Missa num relance", "tl": "Ang Misa sa isang sulyap"},
    "glance_lede": {"en": "Each dot is one moment of a Sunday Mass, colored by what the people do. Tap one to see it in the step-by-step guide.",
                    "es": "Cada punto es un momento de la Misa dominical, con el color de lo que hace la gente. Toca uno para verlo en la guía paso a paso.",
                    "pt": "Cada ponto é um momento da Missa de domingo, com a cor do que o povo faz. Toque num para vê-lo no guia passo a passo.",
                    "tl": "Bawat tuldok ay isang sandali ng Misa tuwing Linggo, kinulayan ayon sa ginagawa ng mga tao. Pindutin ang isa para makita ito sa gabay."},
    "postures": {"en": "Why We Stand, Sit and Kneel", "es": "Por qué nos ponemos de pie, nos sentamos y nos arrodillamos",
                 "pt": "Por que ficamos de pé, sentamos e ajoelhamos", "tl": "Kung bakit tayo tumatayo, umuupo at lumuluhod"},
    "gestures": {"en": "Gestures and What They Mean", "es": "Los gestos y lo que significan", "pt": "Os gestos e o que significam", "tl": "Mga kilos at ang kahulugan nito"},
    "responses": {"en": "Why We Respond", "es": "Por qué respondemos", "pt": "Por que respondemos", "tl": "Kung bakit tayo sumasagot"},
    "resp_lede": {"en": "The Mass is a conversation. The priest speaks for the Church to God and to the people, and the people answer. Most responses come straight from the Bible.",
                  "es": "La Misa es un diálogo. El sacerdote habla en nombre de la Iglesia a Dios y al pueblo, y el pueblo responde. Casi todas las respuestas vienen directamente de la Biblia.",
                  "pt": "A Missa é um diálogo. O padre fala em nome da Igreja a Deus e ao povo, e o povo responde. Quase todas as respostas vêm diretamente da Bíblia.",
                  "tl": "Ang Misa ay isang pag-uusap. Nagsasalita ang pari para sa Simbahan sa Diyos at sa mga tao, at sumasagot ang mga tao. Karamihan ng mga sagot ay mula mismo sa Bibliya."},
    "note": {"en": "Customs vary a little by country and parish. In the United States the bishops ask the faithful to kneel from after the Holy, Holy, Holy until after the Great Amen, and again after the Lamb of God. If kneeling is hard for you, sitting is always fine.",
             "es": "Las costumbres varían un poco según el país y la parroquia. En Estados Unidos, los obispos piden arrodillarse desde después del Santo hasta después del Gran Amén, y de nuevo después del Cordero de Dios. Si te cuesta arrodillarte, siempre puedes quedarte sentado.",
             "pt": "Os costumes variam um pouco conforme o país e a paróquia. Em alguns lugares se ajoelha só na consagração; nos Estados Unidos, do Santo até o Grande Amém e depois do Cordeiro de Deus. Se for difícil ajoelhar, pode ficar sentado.",
             "tl": "Bahagyang nagkakaiba ang kaugalian ayon sa bansa at parokya. Sa Estados Unidos, hinihiling ng mga obispo na lumuhod mula pagkatapos ng Santo, Santo, Santo hanggang pagkatapos ng Dakilang Amen, at muli pagkatapos ng Kordero ng Diyos. Kung mahirap lumuhod, laging puwedeng umupo."},
}

PART_WHY = {  # index of the part in mass*.json order
    "en": ["Quiet time to arrive and get ready. Many people kneel briefly to pray when they first reach their pew.",
           "The people gather as one, admit they need God's mercy and praise him, so that they are ready to listen.",
           "God speaks through Scripture: usually the Old Testament, a Psalm, a New Testament letter and the Gospel. The homily applies it to daily life.",
           "The gifts of bread and wine are offered, and in the Eucharistic Prayer they become the Body and Blood of Christ, his sacrifice made present.",
           "The people pray the Our Father, offer peace and receive Christ in Holy Communion.",
           "A blessing and a sending out: the word Mass comes from the Latin dismissal, Ite, missa est, \"Go, you are sent.\""],
    "es": ["Un rato en silencio para llegar y prepararse. Muchos se arrodillan un momento a rezar al llegar a la banca.",
           "El pueblo se reúne como uno solo, reconoce que necesita la misericordia de Dios y lo alaba, para estar listo para escuchar.",
           "Dios habla por la Escritura: normalmente el Antiguo Testamento, un salmo, una carta del Nuevo Testamento y el Evangelio. La homilía lo aplica a la vida diaria.",
           "Se ofrecen el pan y el vino, y en la Plegaria Eucarística se convierten en el Cuerpo y la Sangre de Cristo: su sacrificio se hace presente.",
           "El pueblo reza el Padrenuestro, se da la paz y recibe a Cristo en la Comunión.",
           "Una bendición y un envío: la palabra Misa viene de la despedida en latín, Ite, missa est, «Vayan, son enviados»."],
    "pt": ["Um tempo em silêncio para chegar e se preparar. Muitos se ajoelham um instante para rezar ao chegar ao banco.",
           "O povo se reúne como um só, reconhece que precisa da misericórdia de Deus e o louva, para estar pronto para ouvir.",
           "Deus fala pela Escritura: geralmente o Antigo Testamento, um salmo, uma carta do Novo Testamento e o Evangelho. A homilia aplica isso à vida diária.",
           "O pão e o vinho são oferecidos e, na Oração Eucarística, tornam-se o Corpo e o Sangue de Cristo: o seu sacrifício se torna presente.",
           "O povo reza o Pai-Nosso, dá a paz e recebe Cristo na Comunhão.",
           "Uma bênção e um envio: a palavra Missa vem da despedida em latim, Ite, missa est, «Ide, sois enviados»."],
    "tl": ["Tahimik na sandali para dumating at maghanda. Marami ang lumuluhod sandali para manalangin pagdating sa upuan.",
           "Nagtitipon ang mga tao bilang isa, inaamin na kailangan nila ang awa ng Diyos at pinupuri siya, upang handa silang makinig.",
           "Nagsasalita ang Diyos sa Kasulatan: kadalasan ang Lumang Tipan, isang Salmo, isang liham ng Bagong Tipan at ang Mabuting Balita. Iniuugnay ito ng homiliya sa araw-araw na buhay.",
           "Iniaalay ang tinapay at alak, at sa Panalanging Eukaristiko ay nagiging Katawan at Dugo ni Kristo: ginagawang kasalukuyan ang kanyang sakripisyo.",
           "Dinarasal ng lahat ang Ama Namin, nagbibigayan ng kapayapaan at tinatanggap si Kristo sa Komunyon.",
           "Isang pagbabasbas at pagsusugo: ang salitang Misa ay galing sa Latin na pamamaalam, Ite, missa est, \"Humayo kayo, kayo ay isinusugo.\""],
}

POSTURE = {  # key: (title, why) per language
    "stand": {"en": ("Standing", "Standing is the posture of respect and readiness, like rising when someone important enters. Early Christians prayed standing as people of the Resurrection. We stand for the Gospel, because Christ himself speaks, and for the great prayers."),
              "es": ("De pie", "Estar de pie es la postura del respeto y la disponibilidad, como levantarse cuando entra alguien importante. Los primeros cristianos rezaban de pie como pueblo de la Resurrección. Nos ponemos de pie para el Evangelio, porque habla Cristo mismo, y para las grandes oraciones."),
              "pt": ("De pé", "Ficar de pé é a postura do respeito e da prontidão, como levantar-se quando chega alguém importante. Os primeiros cristãos rezavam de pé como povo da Ressurreição. Ficamos de pé para o Evangelho, porque o próprio Cristo fala, e para as grandes orações."),
              "tl": ("Nakatayo", "Ang pagtayo ay tindig ng paggalang at kahandaan, gaya ng pagtayo kapag dumarating ang isang mahalagang tao. Nananalangin nang nakatayo ang mga unang Kristiyano bilang bayan ng Muling Pagkabuhay. Tumatayo tayo sa Mabuting Balita, dahil si Kristo mismo ang nagsasalita, at sa mga dakilang panalangin.")},
    "sit": {"en": ("Sitting", "Sitting is the posture of listening and taking things in, like Mary of Bethany sitting at Jesus' feet (Luke 10:39). We sit for the first readings, the homily and while the gifts are prepared."),
            "es": ("Sentados", "Estar sentado es la postura de escuchar y acoger, como María de Betania sentada a los pies de Jesús (Lucas 10,39). Nos sentamos para las primeras lecturas, la homilía y mientras se preparan los dones."),
            "pt": ("Sentados", "Ficar sentado é a postura de quem escuta e acolhe, como Maria de Betânia sentada aos pés de Jesus (Lucas 10,39). Sentamos nas primeiras leituras, na homilia e enquanto se preparam as oferendas."),
            "tl": ("Nakaupo", "Ang pag-upo ay tindig ng pakikinig at pagtanggap, gaya ni Maria ng Betania na nakaupo sa paanan ni Hesus (Lucas 10:39). Umuupo tayo sa mga unang pagbasa, sa homiliya at habang inihahanda ang mga alay.")},
    "kneel": {"en": ("Kneeling", "Kneeling is the posture of adoration and humility. We kneel when the bread and wine become the Body and Blood of Christ and he is present on the altar, as people knelt before Jesus in the Gospels."),
              "es": ("De rodillas", "Arrodillarse es la postura de la adoración y la humildad. Nos arrodillamos cuando el pan y el vino se convierten en el Cuerpo y la Sangre de Cristo y él está presente sobre el altar, como la gente se arrodillaba ante Jesús en los Evangelios."),
              "pt": ("De joelhos", "Ajoelhar é a postura da adoração e da humildade. Ajoelhamos quando o pão e o vinho se tornam o Corpo e o Sangue de Cristo e ele está presente sobre o altar, como as pessoas se ajoelhavam diante de Jesus nos Evangelhos."),
              "tl": ("Nakaluhod", "Ang pagluhod ay tindig ng pagsamba at kababaang-loob. Lumuluhod tayo kapag ang tinapay at alak ay naging Katawan at Dugo ni Kristo at naroon siya sa altar, gaya ng pagluhod ng mga tao sa harap ni Hesus sa mga Ebanghelyo.")},
}

GESTURES = {
    "en": [("Sign of the Cross", "At the start and end of Mass and at the blessing.", "It sums up the faith: the Trinity, and the cross by which we are saved."),
           ("Three small crosses", "As the Gospel is announced, on forehead, lips and heart.", "A silent prayer: may God's word be in my mind, on my lips and in my heart."),
           ("Striking the breast", "At \"through my fault\" in the I Confess.", "A sign of sorrow, like the tax collector who beat his breast and prayed, \"God, be merciful to me, a sinner\" (Luke 18:13)."),
           ("A bow", "In the Creed at the words about Jesus becoming man, and before receiving Communion.", "Reverence for the mystery of God becoming one of us, and for Christ in the Eucharist."),
           ("Genuflecting", "Before entering the pew and when passing the tabernacle.", "Bending the knee to Christ present in the tabernacle (Philippians 2:10)."),
           ("Sign of peace", "Just before Communion.", "Jesus asks us to be reconciled before bringing our gift to the altar (Matthew 5:23–24).")],
    "es": [("La señal de la cruz", "Al comenzar y terminar la Misa y en la bendición.", "Resume la fe: la Trinidad y la cruz por la que somos salvados."),
           ("Tres pequeñas cruces", "Al anunciarse el Evangelio, en la frente, los labios y el pecho.", "Una oración en silencio: que la Palabra de Dios esté en mi mente, en mis labios y en mi corazón."),
           ("Golpearse el pecho", "En «por mi culpa» del Yo confieso.", "Un signo de arrepentimiento, como el publicano que se golpeaba el pecho y decía: «Oh Dios, ten compasión de mí, que soy pecador» (Lucas 18,13)."),
           ("Una inclinación", "En el Credo, en las palabras sobre la encarnación de Jesús, y antes de comulgar.", "Reverencia ante el misterio de Dios hecho uno de nosotros, y ante Cristo en la Eucaristía."),
           ("La genuflexión", "Antes de entrar en la banca y al pasar ante el sagrario.", "Doblar la rodilla ante Cristo presente en el sagrario (Filipenses 2,10)."),
           ("La paz", "Justo antes de la Comunión.", "Jesús nos pide reconciliarnos antes de llevar la ofrenda al altar (Mateo 5,23-24).")],
    "pt": [("O sinal da cruz", "No começo e no fim da Missa e na bênção.", "Resume a fé: a Trindade e a cruz pela qual somos salvos."),
           ("Três pequenas cruzes", "Quando se anuncia o Evangelho, na testa, nos lábios e no peito.", "Uma oração em silêncio: que a Palavra de Deus esteja na minha mente, nos meus lábios e no meu coração."),
           ("Bater no peito", "Em «por minha culpa» do Confesso a Deus.", "Um sinal de arrependimento, como o publicano que batia no peito e dizia: «Meu Deus, tem piedade de mim, pecador» (Lucas 18,13)."),
           ("Uma inclinação", "No Creio, nas palavras sobre a encarnação de Jesus, e antes de comungar.", "Reverência diante do mistério de Deus feito um de nós, e diante de Cristo na Eucaristia."),
           ("A genuflexão", "Antes de entrar no banco e ao passar diante do sacrário.", "Dobrar o joelho diante de Cristo presente no sacrário (Filipenses 2,10)."),
           ("O abraço da paz", "Pouco antes da Comunhão.", "Jesus pede que nos reconciliemos antes de levar a oferta ao altar (Mateus 5,23-24).")],
    "tl": [("Tanda ng Krus", "Sa simula at wakas ng Misa at sa pagbabasbas.", "Buod ito ng pananampalataya: ang Santisima Trinidad at ang krus na nagligtas sa atin."),
           ("Tatlong maliliit na krus", "Pagpapahayag ng Mabuting Balita, sa noo, labi at dibdib.", "Tahimik na dasal: nawa'y mapasa-isip ko, mapasa-labi ko at mapasa-puso ko ang Salita ng Diyos."),
           ("Pagdagok sa dibdib", "Sa \"kasalanan ko\" ng Inaamin ko.", "Tanda ng pagsisisi, gaya ng publikanong dumagok sa dibdib at nanalangin, \"O Diyos, mahabag ka sa akin na isang makasalanan\" (Lucas 18:13)."),
           ("Pagyuko", "Sa Kredo, sa mga salita tungkol sa pagkakatawang-tao ni Hesus, at bago tumanggap ng Komunyon.", "Paggalang sa misteryo ng Diyos na naging isa sa atin, at kay Kristo sa Eukaristiya."),
           ("Pagluhod nang isang tuhod", "Bago pumasok sa upuan at kapag dumaraan sa tabernakulo.", "Pagluhod kay Kristo na naroon sa tabernakulo (Filipos 2:10)."),
           ("Pagbibigayan ng kapayapaan", "Bago ang Komunyon.", "Hinihiling ni Hesus na makipagkasundo muna tayo bago maghandog sa altar (Mateo 5:23–24).")],
}

RESPONSES = {  # (priest says, people answer, why)
    "en": [("The Lord be with you.", "And with your spirit.", "An ancient greeting found in St. Paul's letters (2 Timothy 4:22). The people pray for the priest and recognize the Holy Spirit he received at ordination."),
           ("The word of the Lord.", "Thanks be to God.", "Thanks for God speaking to us in the reading just heard."),
           ("The Gospel of the Lord.", "Praise to you, Lord Jesus Christ.", "Spoken to Christ himself, who is present in the Gospel."),
           ("Lift up your hearts.", "We lift them up to the Lord.", "An invitation used since the earliest centuries: set aside distractions for the great prayer of thanksgiving."),
           ("Holy, Holy, Holy Lord God of hosts…", "", "The song of the angels in Isaiah 6:3 and Revelation 4:8, joined to the crowd's \"Hosanna\" on Palm Sunday (Matthew 21:9). Heaven and earth sing together."),
           ("Behold the Lamb of God…", "Lord, I am not worthy that you should enter under my roof, but only say the word and my soul shall be healed.", "The words of the Roman centurion who trusted Jesus to heal his servant from afar (Matthew 8:8)."),
           ("The Body of Christ.", "Amen.", "\"Yes, I believe it.\" Each communicant makes a personal act of faith that this is truly Christ.")],
    "es": [("El Señor esté con ustedes.", "Y con tu espíritu.", "Un saludo antiguo que aparece en las cartas de san Pablo (2 Timoteo 4,22). El pueblo reza por el sacerdote y reconoce el Espíritu Santo que recibió en su ordenación."),
           ("Palabra de Dios.", "Te alabamos, Señor.", "Alabanza a Dios que nos acaba de hablar en la lectura."),
           ("Palabra del Señor.", "Gloria a ti, Señor Jesús.", "Dicho a Cristo mismo, que está presente en el Evangelio."),
           ("Levantemos el corazón.", "Lo tenemos levantado hacia el Señor.", "Una invitación usada desde los primeros siglos: dejar las distracciones para la gran oración de acción de gracias."),
           ("Santo, Santo, Santo es el Señor, Dios del universo…", "", "El canto de los ángeles en Isaías 6,3 y Apocalipsis 4,8, unido al «Hosanna» de la multitud el Domingo de Ramos (Mateo 21,9). Cielo y tierra cantan juntos."),
           ("Éste es el Cordero de Dios…", "Señor, no soy digno de que entres en mi casa, pero una palabra tuya bastará para sanarme.", "Las palabras del centurión romano que confió en que Jesús curaría a su siervo a distancia (Mateo 8,8)."),
           ("El Cuerpo de Cristo.", "Amén.", "«Sí, lo creo». Cada persona que comulga hace un acto de fe personal en que esto es verdaderamente Cristo.")],
    "pt": [("O Senhor esteja convosco.", "Ele está no meio de nós.", "Uma saudação antiga, presente nas cartas de São Paulo (2 Timóteo 4,22). No Brasil, o povo responde afirmando a presença de Cristo na assembleia reunida (Mateus 18,20)."),
           ("Palavra do Senhor.", "Graças a Deus.", "Agradecimento a Deus, que acabou de nos falar na leitura."),
           ("Palavra da Salvação.", "Glória a vós, Senhor.", "Dito ao próprio Cristo, presente no Evangelho."),
           ("Corações ao alto.", "O nosso coração está em Deus.", "Um convite usado desde os primeiros séculos: deixar as distrações para a grande oração de ação de graças."),
           ("Santo, Santo, Santo, Senhor Deus do universo…", "", "O canto dos anjos em Isaías 6,3 e Apocalipse 4,8, unido ao «Hosana» da multidão no Domingo de Ramos (Mateus 21,9). Céu e terra cantam juntos."),
           ("Eis o Cordeiro de Deus…", "Senhor, eu não sou digno de que entreis em minha morada, mas dizei uma palavra e serei salvo.", "As palavras do centurião romano que confiou que Jesus curaria o seu servo à distância (Mateus 8,8)."),
           ("O Corpo de Cristo.", "Amém.", "«Sim, eu creio». Cada pessoa que comunga faz um ato de fé pessoal de que isto é verdadeiramente Cristo.")],
    "tl": [("Sumainyo ang Panginoon.", "At sumaiyo rin.", "Isang sinaunang pagbati na makikita sa mga liham ni San Pablo (2 Timoteo 4:22). Ipinapanalangin din ng mga tao ang pari bilang tugon."),
           ("Ang Salita ng Diyos.", "Salamat sa Diyos.", "Pasasalamat sa Diyos na kakausap lamang sa atin sa pagbasa."),
           ("Ang Mabuting Balita ng Panginoon.", "Pinupuri ka namin, Panginoong Hesukristo.", "Sinasabi kay Kristo mismo, na naroon sa Mabuting Balita."),
           ("Itaas ninyo ang inyong puso.", "Itinaas na namin sa Panginoon.", "Isang paanyayang ginagamit na mula pa sa mga unang siglo: iwan ang mga abala para sa dakilang panalangin ng pasasalamat."),
           ("Santo, Santo, Santo, Panginoong Diyos ng mga hukbo…", "", "Ang awit ng mga anghel sa Isaias 6:3 at Pahayag 4:8, kasama ang \"Hosana\" ng mga tao noong Linggo ng Palaspas (Mateo 21:9). Sabay na umaawit ang langit at lupa."),
           ("Ito ang Kordero ng Diyos…", "Panginoon, hindi ako karapat-dapat na magpatuloy sa iyo, ngunit sa isang salita mo lamang ay gagaling na ako.", "Ang mga salita ng senturyong Romano na nagtiwalang pagagalingin ni Hesus ang kanyang alipin kahit malayo (Mateo 8:8)."),
           ("Katawan ni Kristo.", "Amen.", "\"Oo, naniniwala ako.\" Bawat tumatanggap ay nagpapahayag ng sariling pananampalataya na ito ay tunay na si Kristo.")],
}
RESP_WORD = {"en": ("Priest", "People"), "es": ("Sacerdote", "Pueblo"), "pt": ("Padre", "Povo"), "tl": ("Pari", "Bayan")}
POSE_WORD = {"en": {"stand": "Stand", "sit": "Sit", "kneel": "Kneel", "any": "As you wish"},
             "es": {"stand": "De pie", "sit": "Sentados", "kneel": "De rodillas", "any": "Como prefieras"},
             "pt": {"stand": "De pé", "sit": "Sentados", "kneel": "De joelhos", "any": "Como preferir"},
             "tl": {"stand": "Nakatayo", "sit": "Nakaupo", "kneel": "Nakaluhod", "any": "Ayon sa gusto mo"}}


def mass_steps(lang):
    return _load("mass.json" if lang == "en" else f"mass_{lang}.json")


def inside_mass_html(lang):
    steps = mass_steps(lang)
    fm = URL["first-mass"][lang]
    parts, order = {}, []
    for i, s in enumerate(steps, 1):
        if s["part"] not in parts:
            parts[s["part"]] = []
            order.append(s["part"])
        parts[s["part"]].append((i, s))
    tl = []
    for pi, part in enumerate(order):
        dots = "".join(f'<a class="mdot pose-bg-{s["pose"]}" href="{fm}#step-{i}" title="{e(s["title"])} ({POSE_WORD[lang][s["pose"]]})">'
                       f'<span class="mdot-n">{i}</span><span class="mdot-t">{e(s["title"])}</span></a>' for i, s in parts[part])
        tl.append(f'<li class="mpart"><h3>{e(part)}</h3><p>{e(PART_WHY[lang][pi])}</p><div class="mdots">{dots}</div></li>')
    key = "".join(f'<li><span class="mdot-key pose-bg-{k}"></span>{v}</li>' for k, v in POSE_WORD[lang].items())
    post = "".join(f'<div class="card posture">{POSE_SVG[k]}<h3>{e(POSTURE[k][lang][0])}</h3><p>{e(POSTURE[k][lang][1])}</p></div>'
                   for k in ("stand", "sit", "kneel"))
    gest = "".join(f'<div class="card"><h3>{e(n)}</h3><p class="small muted">{e(w)}</p><p>{e(y)}</p></div>' for n, w, y in GESTURES[lang])
    pw, aw = RESP_WORD[lang]
    resp = "".join(f'<div class="card resp"><dl class="say"><div class="say-row"><dt>{pw}</dt><dd>{e(p)}</dd></div>'
                   + (f'<div class="say-row all"><dt>{aw}</dt><dd>{e(a)}</dd></div>' if a else "")
                   + f'</dl><p>{e(y)}</p></div>' for p, a, y in RESPONSES[lang])
    t = URL["terms"][lang]
    return f'''<div class="page-head">
  <div class="wrap">
    <p class="kicker"><a href="{t}">{W["terms"][lang]}</a> &rsaquo; {MT["kicker"][lang]}</p>
    <h1>{e(NAME["mass"][lang])}</h1>
    <p class="lede">{MT["lede"][lang]}</p>
    <p>{MT["cta"][lang]} <a href="{fm}">{MT["first"][lang]}</a>.</p>
  </div>
</div>
<div class="wrap">
  <section class="section">
    <h2>{MT["glance"][lang]}</h2>
    <p>{MT["glance_lede"][lang]}</p>
    <ul class="mkey">{key}</ul>
    <ol class="mtimeline">{"".join(tl)}</ol>
  </section>
  <section class="section">
    <h2>{MT["postures"][lang]}</h2>
    <div class="grid postures">{post}</div>
    <p class="small muted">{MT["note"][lang]}</p>
  </section>
  <section class="section">
    <h2>{MT["gestures"][lang]}</h2>
    <div class="grid">{gest}</div>
  </section>
  <section class="section">
    <h2>{MT["responses"][lang]}</h2>
    <p class="prose">{MT["resp_lede"][lang]}</p>
    <div class="grid two">{resp}</div>
  </section>
  <section class="section">
    <h2>{W["guides"][lang]}</h2>
    {guide_cards(lang, skip="mass")}
  </section>
</div>'''


def render(body, lang="en"):
    body = render_terms(body, lang)
    for ph, fn in (("{{ANATOMY_PAGE}}", anatomy_html), ("{{VESTMENTS_PAGE}}", vestments_html), ("{{INSIDE_MASS_PAGE}}", inside_mass_html)):
        if ph in body:
            body = body.replace(ph, fn(lang))
    return body
