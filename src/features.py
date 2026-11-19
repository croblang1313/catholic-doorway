"""Data-driven sections for the prayer, devotion and reference pages.

build.py calls render(body, lang) on every page; each {{PLACEHOLDER}} found
in a page body is replaced with HTML built from src/data/*.json.
"""
from pathlib import Path
import html
import json

DATA = Path(__file__).resolve().parent / "data"
e = html.escape


def _load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


EXAMEN_TABS = {"en": [("kids", "Kids"), ("teens", "Teens"), ("adults", "Adults")],
               "es": [("kids", "Niños"), ("teens", "Adolescentes"), ("adults", "Adultos")],
               "pt": [("kids", "Crianças"), ("teens", "Adolescentes"), ("adults", "Adultos")],
               "tl": [("kids", "Mga bata"), ("teens", "Kabataan"), ("adults", "Nakatatanda")]}


def examen_html(lang):
    data = _load("examen.json")[lang]
    tabs = "".join(
        f'<button type="button" class="chip" data-exam="{k}" aria-pressed="{"true" if k == "adults" else "false"}">{e(l)}</button>'
        for k, l in EXAMEN_TABS[lang])
    panels = []
    for key, _ in EXAMEN_TABS[lang]:
        groups = []
        n = 0
        for g in data[key]:
            items = []
            for it in g["items"]:
                n += 1
                items.append(f'<li><label><input type="checkbox" value="{e(it)}"><span>{e(it)}</span></label></li>')
            groups.append(f'<fieldset class="exam-group"><legend>{e(g["head"])}</legend><ul>{"".join(items)}</ul></fieldset>')
        hidden = "" if key == "adults" else " hidden"
        panels.append(f'<div class="exam-panel" data-panel="{key}"{hidden}>{"".join(groups)}</div>')
    return (f'<div class="filters exam-tabs" role="group">{tabs}</div>\n' + "\n".join(panels))


def _say(rows, all_words):
    if not rows:
        return ""
    out = "".join(f'<div class="say-row{" all" if who in all_words else ""}"><dt>{e(who)}</dt><dd>{e(line)}</dd></div>' for who, line in rows)
    return f'<dl class="say">{out}</dl>'


ALL_WORD = {"en": ("All",), "es": ("Todos",), "pt": ("Todos",), "tl": ("Lahat",)}


def _step(i, part, title, what, say="", tip="", sub=""):
    sub = f'<p class="step-sub muted small">{sub}</p>' if sub else ""
    tip = f'<p class="mass-tip">{tip}</p>' if tip else ""
    return (f'    <section class="mass-step" id="step-{i}" data-part="{e(part)}" data-step="{i}">'
            f'<div class="mass-head"><h3><span class="mass-no">{i}.</span> {e(title)}</h3></div>{sub}'
            f'<p>{what}</p>{say}{tip}</section>')


def _usccb(ref):
    """English reference like "Isaiah 52:14; 53:2-3" -> USCCB Bible link path."""
    import re
    m = re.match(r"(\d?\s?[A-Za-z]+)\s(\d+)(?::(\d+))?", ref)
    book = m.group(1).lower().replace(" ", "")
    book = {"psalm": "psalms"}.get(book, book)
    verse = "" if book == "psalms" or not m.group(3) else "?" + m.group(3)
    return f"https://bible.usccb.org/bible/{book}/{m.group(2)}{verse}"


def stations_html(lang):
    """The Stations of the Cross: one card per station with an original illustration.
    Without JavaScript the cards read as a list; stations.js turns them into a walk-through."""
    import stations_art
    d = _load("stations.json")[lang]
    en = _load("stations.json")["en"]
    ui = d["ui"]
    resp = _say(d["open"][3], ALL_WORD[lang])
    prayers = "".join(f'<h4>{e(t)}</h4><p>{e(x).replace(chr(10), "<br>")}</p>' for t, x in d["prayers"])
    hl = "" if lang == "en" else ' hreflang="en"'

    def card(i, label, title, body):
        art = stations_art.svg(i, ui["art"].replace("{t}", title))
        return (f'  <section class="st-card" id="station-{i}" data-i="{i}" aria-labelledby="st-h-{i}">'
                f'<figure class="st-fig">{art}</figure><div class="st-body">'
                f'<p class="st-num">{label}</p><h2 id="st-h-{i}">{e(title)}</h2>{body}</div></section>')

    o = d["open"]
    cards = [card(0, e(o[0]), o[1], f'<p>{e(o[2])}</p>{resp}<p class="st-tip">{e(o[4])}</p>')]
    for i, (title, ref, text, prayer) in enumerate(d["stations"], 1):
        link = _usccb(en["stations"][i - 1][1])
        if lang == "en":
            q, qref = d["quotes"][i - 1]
            scripture = (f'<blockquote class="st-scripture"><p>{e(q)}</p><footer><a href="{link}" target="_blank" rel="noopener" '
                         f'title="{ui["read"]}">{e(qref)}</a></footer></blockquote>')
        else:
            scripture = f'<p class="st-read">{ui["read"]}: <a href="{link}" target="_blank" rel="noopener"{hl}>{e(ref)}</a></p>'
        body = (f'{resp}{scripture}<p class="st-reflect">{e(text)}</p><p class="st-prayer">{e(prayer)}</p>'
                f'<details class="st-prayers"><summary>{ui["pray"]}: {e(ui["prayers"])}</summary>{prayers}</details>')
        cards.append(card(i, ui["of"].replace("{n}", str(i)), title, body))
    c = d["close"]
    cards.append(card(15, e(c[0]), c[1], f'<p>{e(c[2])}</p><p class="st-tip">{e(c[4])}</p>'))

    dots = [f'<button type="button" data-go="0" aria-label="{e(o[0])}">&#10013;</button>']
    dots += [f'<button type="button" data-go="{i}" aria-label="{e(ui["of"].replace("{n}", str(i)))}">{i}</button>' for i in range(1, 15)]
    dots.append(f'<button type="button" data-go="15" aria-label="{e(c[0])}">&#10013;</button>')
    return f'''<div class="stations" id="stations-app">
  <nav class="st-dots" aria-label="{e(ui["nav"])}" hidden>{"".join(dots)}</nav>
{chr(10).join(cards)}
  <div class="st-nav" hidden>
    <button class="btn secondary" type="button" id="st-back">{ui["back"]}</button>
    <span id="st-count" class="rs-count"></span>
    <button class="btn" type="button" id="st-next" data-next="{e(ui["next"])}" data-again="{e(ui["again"])}">{ui["next"]}</button>
  </div>
  <p class="small muted st-hint" hidden>{e(ui["hint"])}</p>
</div>'''


def chaplet_html(lang):
    d = _load("chaplet.json")[lang]
    out, n = [], 0
    for part, title, what, tip in d["steps"]:
        n += 1
        out.append(_step(n, part, title, e(what), "", tip))
    for k in range(1, 6):
        n += 1
        body = (f'<dl class="say"><div class="say-row"><dt>{e(d["large"])}</dt><dd>{e(d["ef"])}</dd></div>'
                f'<div class="say-row all"><dt>{e(d["small"])}</dt><dd>{e(d["sake"])} <span class="times">({e(d["times10"])})</span></dd></div></dl>')
        out.append(_step(n, f'{d["decade"]} {k}', f'{d["decade"]} {k}', "", body).replace("<p></p>", ""))
    p0, t0, w0, _ = d["end"][0]
    n += 1
    out.append(_step(n, p0, t0, e(w0), f'<dl class="say"><div class="say-row all"><dt>{e(d["times3"])}</dt><dd>{e(d["holy"])}</dd></div></dl>'))
    p1, t1, w1, tip1 = d["end"][1]
    n += 1
    out.append(_step(n, p1, t1, e(w1), "", e(tip1)))
    return "\n".join(out)


NOVENA_WORDS = {"en": ("Prayer for each day", "Intentions for each day", "Day"),
                "es": ("Oración para cada día", "Intenciones de cada día", "Día"),
                "pt": ("Oração para cada dia", "Intenções de cada dia", "Dia"),
                "tl": ("Dasal sa bawat araw", "Intensiyon sa bawat araw", "Ika-")}


def novenas_html(lang):
    w = NOVENA_WORDS[lang]
    out = []
    for nv in _load("novenas.json"):
        title, about, prayer = nv[lang]
        days = ""
        if nv.get("days"):
            lis = "".join(f"<li><strong>{w[2]}{'' if w[2].endswith('-') else ' '}{i}{' na araw' if w[2].endswith('-') else ''}.</strong> {e(x)}</li>" for i, x in enumerate(nv["days"][lang], 1))
            days = f'<h4>{w[1]}</h4><ol class="novena-days">{lis}</ol>'
        out.append(
            f'      <article class="card novena prayer" id="{nv["id"]}" data-start="{nv["start"]}">'
            f'<p class="label novena-when" aria-live="polite"></p><h3>{e(title)}</h3><p>{about}</p>{days}'
            f'<h4>{w[0]}</h4><p class="text">{e(prayer)}</p></article>')
    return "\n".join(out)


COMP_WORDS = {"en": ("Prayer companion", "Close", "&larr; Back", "Next &rarr;"),
              "es": ("Guía de oración", "Cerrar", "&larr; Atrás", "Siguiente &rarr;"),
              "pt": ("Guia de oração", "Fechar", "&larr; Voltar", "Próximo &rarr;"),
              "tl": ("Gabay sa pagdarasal", "Isara", "&larr; Bumalik", "Susunod &rarr;")}


def companion_html(lang):
    label, close, back, nxt = COMP_WORDS[lang]
    return f'''<div class="companion" id="companion" hidden role="dialog" aria-modal="true" aria-label="{label}">
  <div class="companion-bar">
    <span class="companion-part" id="comp-part"></span>
    <button class="companion-close" type="button" id="comp-close" aria-label="{close}">&times;</button>
  </div>
  <div class="companion-progress"><span id="comp-progress"></span></div>
  <div class="companion-body" id="comp-body" aria-live="polite"></div>
  <div class="companion-nav">
    <button class="btn secondary" type="button" id="comp-back">{back}</button>
    <span class="companion-count" id="comp-count"></span>
    <button class="btn" type="button" id="comp-next">{nxt}</button>
  </div>
</div>'''


REGINA = {
    "en": ("Regina Caeli", "Queen of Heaven", [("V", "Queen of Heaven, rejoice, alleluia."), ("R", "For he whom you did merit to bear, alleluia."),
           ("V", "Has risen, as he said, alleluia."), ("R", "Pray for us to God, alleluia."),
           ("V", "Rejoice and be glad, O Virgin Mary, alleluia."), ("R", "For the Lord has truly risen, alleluia.")],
           "Let us pray. O God, who gave joy to the world through the resurrection of thy Son, our Lord Jesus Christ,\ngrant, we beseech thee, that through the intercession of the Virgin Mary, his Mother,\nwe may obtain the joys of everlasting life.\nThrough the same Christ our Lord. Amen.",
           "Prayed instead of the Angelus from Easter Sunday through Pentecost."),
    "es": ("Regina Caeli", "Reina del cielo", [("V", "Reina del cielo, alégrate; aleluya."), ("R", "Porque el que mereciste llevar en tu seno; aleluya."),
           ("V", "Ha resucitado, según predijo; aleluya."), ("R", "Ruega por nosotros a Dios; aleluya."),
           ("V", "Gózate y alégrate, Virgen María; aleluya."), ("R", "Porque en verdad ha resucitado el Señor; aleluya.")],
           "Oremos. Oh Dios, que por la resurrección de tu Hijo, nuestro Señor Jesucristo, te has dignado dar la alegría al mundo,\nconcédenos, por intercesión de su Madre, la Virgen María,\nalcanzar los gozos de la vida eterna.\nPor el mismo Cristo nuestro Señor. Amén.",
           "Se reza en lugar del Ángelus desde el Domingo de Pascua hasta Pentecostés."),
    "pt": ("Rainha do Céu", "Regina Caeli", [("V", "Rainha do Céu, alegrai-vos, aleluia."), ("R", "Porque quem merecestes trazer em vosso seio, aleluia."),
           ("V", "Ressuscitou como disse, aleluia."), ("R", "Rogai a Deus por nós, aleluia."),
           ("V", "Exultai e alegrai-vos, ó Virgem Maria, aleluia."), ("R", "Porque o Senhor ressuscitou verdadeiramente, aleluia.")],
           "Oremos. Ó Deus, que vos dignastes alegrar o mundo com a ressurreição do vosso Filho, Nosso Senhor Jesus Cristo,\nconcedei-nos, vos suplicamos, que por sua Mãe, a Virgem Maria,\nalcancemos as alegrias da vida eterna.\nPor Cristo, nosso Senhor. Amém.",
           "Rezada no lugar do Angelus desde o Domingo de Páscoa até Pentecostes."),
}
REGINA["tl"] = ("Regina Caeli", "Reyna ng Langit", [("N", "Reyna ng langit, magalak ka, aleluya."), ("B", "Sapagkat ang iyong pinagindapat na dalhin sa iyong sinapupunan, aleluya,"),
           ("N", "Ay nabuhay na mag-uli ayon sa kanyang sinabi, aleluya."), ("B", "Ipanalangin mo kami sa Diyos, aleluya."),
           ("N", "Magalak ka at matuwa, O Birheng Maria, aleluya."), ("B", "Sapagkat tunay na nabuhay na mag-uli ang Panginoon, aleluya.")],
           "Manalangin tayo. Ama naming makapangyarihan, sa muling pagkabuhay ng iyong Anak, ang aming Panginoong Hesukristo, ay ipinagkaloob mo ang galak sa sanlibutan;\nipagkaloob mo, hinihiling namin, na sa pamamagitan ng Birheng Maria, ang kanyang Ina,\nay makamtan namin ang mga kagalakan ng buhay na walang hanggan.\nSa pamamagitan din ni Kristong aming Panginoon. Amen.",
           "Dinarasal kapalit ng Orasyon mula Linggo ng Pagkabuhay hanggang Pentekostes.")
PRAYERS_PAGE = {"en": "prayers.html", "es": "es/oraciones.html", "pt": "pt/oracoes.html", "tl": "tl/mga-dasal.html"}


def angelus_html(lang):
    import re
    src = (DATA.parent / "pages" / PRAYERS_PAGE[lang]).read_text(encoding="utf-8")
    ang = re.search(r'<article class="card prayer" id="angelus">.*?</article>', src, re.S).group(0)
    title, sub, lines, prayer, note = REGINA[lang]
    body = "\n".join(f"<em>{v}.</em> {e(x)}" for v, x in lines) + "\n" + e(prayer)
    rc = (f'<article class="card prayer" id="regina-caeli"><h3>{e(title)} <span class="muted small">({e(sub)})</span></h3>'
          f'<p class="text">{body}</p><p class="small muted">{e(note)}</p></article>')
    return ang + "\n      " + rc


BY = {"jp2": ("St. John Paul II", "San Juan Pablo II", "São João Paulo II", "San Juan Pablo II"), "b16": ("Benedict XVI", "Benedicto XVI", "Bento XVI", "Benedicto XVI"),
      "fr": ("Francis", "Francisco", "Francisco", "Francisco"), "leo14": ("Leo XIV", "León XIV", "Leão XIV", "Leo XIV"), "leo13": ("Leo XIII", "León XIII", "Leão XIII", "Leo XIII"),
      "pius11": ("Pius XI", "Pío XI", "Pio XI", "Pio XI"), "pius12": ("Pius XII", "Pío XII", "Pio XII", "Pio XII"), "j23": ("St. John XXIII", "San Juan XXIII", "São João XXIII", "San Juan XXIII"),
      "p6": ("St. Paul VI", "San Pablo VI", "São Paulo VI", "San Pablo VI"), "v2": ("Second Vatican Council", "Concilio Vaticano II", "Concílio Vaticano II", "Ikalawang Konsilyo Vaticano"),
      "cdf": ("Dicastery for the Doctrine of the Faith", "Dicasterio para la Doctrina de la Fe", "Dicastério para a Doutrina da Fé", "Dikasteryo para sa Doktrina ng Pananampalataya")}
KIND = {"catechism": ("Catechism", "Catecismo", "Catecismo", "Katesismo"), "law": ("Church law", "Derecho de la Iglesia", "Direito da Igreja", "Batas ng Simbahan"),
        "council": ("Vatican II", "Vaticano II", "Vaticano II", "Vaticano II"), "encyclical": ("Encyclical", "Encíclica", "Encíclica", "Ensiklika"),
        "exhortation": ("Apostolic exhortation", "Exhortación apostólica", "Exortação apostólica", "Pangaral apostoliko"),
        "letter": ("Apostolic letter", "Carta apostólica", "Carta apostólica", "Liham apostoliko"), "doctrine": ("Doctrinal document", "Documento doctrinal", "Documento doutrinal", "Dokumentong doktrinal")}
TOPIC = {"faith": ("Faith and God", "La fe y Dios", "A fé e Deus", "Ang pananampalataya at ang Diyos"), "church": ("The Church", "La Iglesia", "A Igreja", "Ang Simbahan"),
         "scripture": ("Scripture", "La Escritura", "A Escritura", "Ang Banal na Kasulatan"), "liturgy": ("Mass and liturgy", "La Misa y la liturgia", "A Missa e a liturgia", "Ang Misa at ang liturhiya"),
         "sacraments": ("Sacraments", "Sacramentos", "Sacramentos", "Mga sakramento"), "mary": ("Mary", "María", "Maria", "Si Maria"),
         "morality": ("Moral life", "La vida moral", "A vida moral", "Ang buhay moral"), "life": ("Human life", "La vida humana", "A vida humana", "Ang buhay ng tao"),
         "family": ("Marriage and family", "El matrimonio y la familia", "O matrimônio e a família", "Ang kasal at ang pamilya"),
         "social": ("Social teaching", "Doctrina social", "Doutrina social", "Panlipunang turo"), "mission": ("Mission and evangelization", "Misión y evangelización", "Missão e evangelização", "Misyon at ebanghelisasyon"),
         "prayer": ("Prayer and holiness", "Oración y santidad", "Oração e santidade", "Panalangin at kabanalan"), "ecumenism": ("Other Christians and religions", "Otros cristianos y religiones", "Outros cristãos e religiões", "Ibang Kristiyano at relihiyon")}
LI = {"en": 0, "es": 1, "pt": 2, "tl": 3}
ARCH = {"en": "en", "es": "sp", "pt": "po", "tl": "en"}


def doc_url(d, lang):
    if "url" in d:
        return d["url"].get(lang, d["url"]["en"])
    if "a" in d:
        return f'https://www.vatican.va/archive/hist_councils/ii_vatican_council/documents/vat-ii_{d["a"]}_{ARCH[lang]}.html'
    if "r" in d:
        return f'https://www.vatican.va/roman_curia/congregations/cfaith/documents/{d["r"]}_{ARCH[lang]}.html'
    return "https://www.vatican.va/content/" + d["c"].replace("{l}", "en" if lang == "tl" else lang)


def documents_html(lang):
    i = LI[lang]
    docs = _load("documents.json")
    kinds = []
    out = []
    for d in docs:
        if d["kind"] not in kinds:
            kinds.append(d["kind"])
        title, summary = d[lang]
        tags = " ".join(d["t"])
        latin = f'<span class="doc-latin">{e(d["latin"])}</span>' if d["latin"] != title else ""
        topics = ", ".join(TOPIC[x][i] for x in d["t"])
        out.append(
            f'      <li class="doc" data-kind="{d["kind"]}" data-topics="{tags}"><a href="{e(doc_url(d, lang))}" target="_blank" rel="noopener">'
            f'<span class="doc-kind">{KIND[d["kind"]][i]} &middot; {d["year"]}</span>{latin}<strong>{e(title)}</strong></a>'
            f'<p>{e(summary)}</p><p class="small muted">{BY[d["by"]][i]} &middot; {e(topics)}</p></li>')
    all_w = ("All", "Todos", "Todos", "Lahat")[i]
    chips = f'<button type="button" class="chip" data-dkind="all" aria-pressed="true">{all_w}</button>' + "".join(
        f'<button type="button" class="chip" data-dkind="{k}" aria-pressed="false">{KIND[k][i]}</button>' for k in kinds)
    opts = f'<option value="">{("Any topic", "Cualquier tema", "Qualquer tema", "Anumang paksa")[i]}</option>' + "".join(
        f'<option value="{k}">{v[i]}</option>' for k, v in TOPIC.items())
    return (f'<div class="filters" role="group">{chips}</div>\n<select id="doc-topic" class="doc-topic" aria-label="{("Topic", "Tema", "Tema", "Paksa")[i]}">{opts}</select>\n'
            f'<ul class="doc-list" id="doc-list">\n' + "\n".join(out) + "\n    </ul>")


CCC_TOPICS = [
    ("Scripture and Tradition", "La Escritura y la Tradición", "A Escritura e a Tradição", "Ang Banal na Kasulatan at Tradisyon", 74, 141),
    ("Faith", "La fe", "A fé", "Ang pananampalataya", 142, 184),
    ("The Trinity", "La Trinidad", "A Trindade", "Ang Banal na Santatlo", 232, 267),
    ("Creation and the angels", "La creación y los ángeles", "A criação e os anjos", "Ang paglikha at ang mga anghel", 279, 354),
    ("Original sin", "El pecado original", "O pecado original", "Ang kasalanang mana", 385, 421),
    ("Jesus, true God and true man", "Jesús, verdadero Dios y verdadero hombre", "Jesus, verdadeiro Deus e verdadeiro homem", "Si Hesus, tunay na Diyos at tunay na tao", 456, 483),
    ("Mary, Mother of God", "María, Madre de Dios", "Maria, Mãe de Deus", "Si Maria, Ina ng Diyos", 484, 511),
    ("Jesus’ death and resurrection", "La muerte y resurrección de Jesús", "A morte e ressurreição de Jesus", "Ang kamatayan at muling pagkabuhay ni Hesus", 571, 658),
    ("The Holy Spirit", "El Espíritu Santo", "O Espírito Santo", "Ang Espiritu Santo", 683, 747),
    ("The Church: one, holy, catholic and apostolic", "La Iglesia: una, santa, católica y apostólica", "A Igreja: una, santa, católica e apostólica", "Ang Simbahan: iisa, banal, katolika at apostolika", 811, 870),
    ("The Pope and the bishops", "El Papa y los obispos", "O Papa e os bispos", "Ang Papa at ang mga obispo", 880, 896),
    ("The communion of saints", "La comunión de los santos", "A comunhão dos santos", "Ang pakikipag-isa ng mga banal", 946, 962),
    ("Heaven, purgatory and hell", "El cielo, el purgatorio y el infierno", "O céu, o purgatório e o inferno", "Langit, purgatoryo at impiyerno", 1020, 1041),
    ("The liturgy", "La liturgia", "A liturgia", "Ang liturhiya", 1066, 1209),
    ("Baptism", "El Bautismo", "O Batismo", "Ang Binyag", 1213, 1284),
    ("Confirmation", "La Confirmación", "A Crisma", "Ang Kumpil", 1285, 1321),
    ("The Eucharist and the Mass", "La Eucaristía y la Misa", "A Eucaristia e a Missa", "Ang Eukaristiya at ang Misa", 1322, 1419),
    ("Confession", "La Confesión", "A Confissão", "Ang Kumpisal", 1422, 1498),
    ("Indulgences", "Las indulgencias", "As indulgências", "Ang mga indulhensiya", 1471, 1479),
    ("Anointing of the Sick", "La Unción de los enfermos", "A Unção dos Enfermos", "Ang Pagpapahid ng Langis sa Maysakit", 1499, 1532),
    ("Holy Orders", "El Orden sacerdotal", "A Ordem", "Ang Banal na Orden", 1536, 1600),
    ("Marriage", "El Matrimonio", "O Matrimônio", "Ang Kasal", 1601, 1666),
    ("Sacramentals and funerals", "Los sacramentales y los funerales", "Os sacramentais e os funerais", "Ang mga sakramental at ang libing", 1667, 1690),
    ("Conscience", "La conciencia", "A consciência", "Ang budhi", 1776, 1802),
    ("The virtues", "Las virtudes", "As virtudes", "Ang mga birtud", 1803, 1845),
    ("Sin, mortal and venial", "El pecado, mortal y venial", "O pecado, mortal e venial", "Ang kasalanan, mortal at benyal", 1846, 1876),
    ("Social justice", "La justicia social", "A justiça social", "Katarungang panlipunan", 1928, 1948),
    ("Grace", "La gracia", "A graça", "Ang grasya", 1987, 2029),
    ("The Ten Commandments", "Los Diez Mandamientos", "Os Dez Mandamentos", "Ang Sampung Utos", 2052, 2082),
    ("Sunday and holy days", "El domingo y las fiestas", "O domingo e as festas", "Ang Linggo at ang mga pista", 2168, 2195),
    ("Family and parents", "La familia y los padres", "A família e os pais", "Ang pamilya at ang mga magulang", 2197, 2257),
    ("Respect for life", "El respeto a la vida", "O respeito à vida", "Paggalang sa buhay", 2258, 2330),
    ("Chastity and sexuality", "La castidad y la sexualidad", "A castidade e a sexualidade", "Kalinisang-puri at sekswalidad", 2331, 2400),
    ("Property, work and the poor", "Los bienes, el trabajo y los pobres", "Os bens, o trabalho e os pobres", "Ari-arian, trabaho at ang mga dukha", 2401, 2463),
    ("Truthfulness", "La verdad", "A verdade", "Katapatan sa katotohanan", 2464, 2513),
    ("Prayer", "La oración", "A oração", "Ang panalangin", 2558, 2758),
    ("The Our Father", "El Padre Nuestro", "O Pai-Nosso", "Ang Ama Namin", 2759, 2865),
]


def ccc_page(n, lang):
    m = _load("ccc_map.json")[lang]
    page = None
    for start, code in m["map"]:
        if start <= n:
            page = code
    return m["base"] + page + m["ext"]


def ccc_topics_html(lang):
    i = LI[lang]
    out = []
    for *names, a, b in CCC_TOPICS:
        out.append(f'      <li><a href="{ccc_page(a, lang)}" target="_blank" rel="noopener">{e(names[i])}</a> <span class="muted">{a}&ndash;{b}</span></li>')
    return "\n".join(out)


def ccc_map_json(lang):
    m = _load("ccc_map.json")[lang]
    return html.escape(json.dumps(m, separators=(",", ":")), quote=True)


PLACEHOLDERS = {"{{DOCUMENTS}}": documents_html, "{{CCC_TOPICS}}": ccc_topics_html, "{{CCC_MAP}}": ccc_map_json, "{{ANGELUS}}": angelus_html, "{{COMPANION}}": companion_html, "{{EXAMEN}}": examen_html, "{{STATIONS}}": stations_html, "{{CHAPLET}}": chaplet_html,
                "{{NOVENAS}}": novenas_html}


def render(body, lang="en"):
    import visual
    for ph, fn in PLACEHOLDERS.items():
        if ph in body:
            body = body.replace(ph, fn(lang))
    return visual.render(body, lang)


def write_worker_data(root):
    """The Worker builds prayer reminders from the same novena list as the website."""
    nv = _load("novenas.json")
    js = ("// Generated by src/build.py from src/data/novenas.json. Do not edit by hand.\n"
          "export default " + json.dumps(nv, ensure_ascii=False, indent=1) + ";\n")
    (root / "worker" / "novenas-data.js").write_text(js, encoding="utf-8")
