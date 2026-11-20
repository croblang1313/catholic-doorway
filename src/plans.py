"""Reading plans: Bible in a Year, Catechism in a Year, the Gospels in 30 days and a 90-day OCIA plan.

Writes site/data/plans-<lang>.json, which the Reading Plans page (assets/js/plans.js) and the
Worker's reminder feed (worker/plans.js) both read. Each day is a list of readings:
  {"k": "b", "l": "Genesis 1–3", "r": "gen+1-3"}             Bible, opens /read-the-bible?ref=...
  {"k": "c", "l": "Catechism 1–8", "u": "https://...", "t": "Prologue"}   Catechism, opens vatican.va

Bible portions are balanced by length (the number of letters in the Douay-Rheims text), so no
day is much longer than another. Long stretches are split on chapter ends whenever one is close.
"""
import bisect
import json
from pathlib import Path

import features

ROOT = Path(__file__).resolve().parent.parent
BIBLE = ROOT / "site" / "data" / "bible" / "drb"
LANGS = ("en", "es", "pt", "tl")
LI = {"en": 0, "es": 1, "pt": 2, "tl": 3}

# Book names in Spanish, Portuguese and Filipino, in the order of books.json (Catholic canon, 73 books)
BOOK_ES = ["Génesis", "Éxodo", "Levítico", "Números", "Deuteronomio", "Josué", "Jueces", "Rut", "1 Samuel", "2 Samuel",
           "1 Reyes", "2 Reyes", "1 Crónicas", "2 Crónicas", "Esdras", "Nehemías", "Tobías", "Judit", "Ester", "Job",
           "Salmos", "Proverbios", "Eclesiastés", "Cantar de los Cantares", "Sabiduría", "Eclesiástico", "Isaías", "Jeremías",
           "Lamentaciones", "Baruc", "Ezequiel", "Daniel", "Oseas", "Joel", "Amós", "Abdías", "Jonás", "Miqueas", "Nahúm",
           "Habacuc", "Sofonías", "Ageo", "Zacarías", "Malaquías", "1 Macabeos", "2 Macabeos",
           "Mateo", "Marcos", "Lucas", "Juan", "Hechos", "Romanos", "1 Corintios", "2 Corintios", "Gálatas", "Efesios",
           "Filipenses", "Colosenses", "1 Tesalonicenses", "2 Tesalonicenses", "1 Timoteo", "2 Timoteo", "Tito", "Filemón",
           "Hebreos", "Santiago", "1 Pedro", "2 Pedro", "1 Juan", "2 Juan", "3 Juan", "Judas", "Apocalipsis"]
BOOK_PT = ["Gênesis", "Êxodo", "Levítico", "Números", "Deuteronômio", "Josué", "Juízes", "Rute", "1 Samuel", "2 Samuel",
           "1 Reis", "2 Reis", "1 Crônicas", "2 Crônicas", "Esdras", "Neemias", "Tobias", "Judite", "Ester", "Jó",
           "Salmos", "Provérbios", "Eclesiastes", "Cântico dos Cânticos", "Sabedoria", "Eclesiástico", "Isaías", "Jeremias",
           "Lamentações", "Baruc", "Ezequiel", "Daniel", "Oseias", "Joel", "Amós", "Abdias", "Jonas", "Miqueias", "Naum",
           "Habacuc", "Sofonias", "Ageu", "Zacarias", "Malaquias", "1 Macabeus", "2 Macabeus",
           "Mateus", "Marcos", "Lucas", "João", "Atos", "Romanos", "1 Coríntios", "2 Coríntios", "Gálatas", "Efésios",
           "Filipenses", "Colossenses", "1 Tessalonicenses", "2 Tessalonicenses", "1 Timóteo", "2 Timóteo", "Tito", "Filêmon",
           "Hebreus", "Tiago", "1 Pedro", "2 Pedro", "1 João", "2 João", "3 João", "Judas", "Apocalipse"]
BOOK_TL = ["Genesis", "Exodo", "Levitico", "Mga Bilang", "Deuteronomio", "Josue", "Mga Hukom", "Ruth", "1 Samuel", "2 Samuel",
           "1 Mga Hari", "2 Mga Hari", "1 Cronica", "2 Cronica", "Ezra", "Nehemias", "Tobit", "Judit", "Ester", "Job",
           "Mga Awit", "Mga Kawikaan", "Mangangaral", "Awit ng mga Awit", "Karunungan", "Sirac", "Isaias", "Jeremias",
           "Mga Panaghoy", "Baruc", "Ezekiel", "Daniel", "Oseas", "Joel", "Amos", "Abdias", "Jonas", "Mikas", "Nahum",
           "Habakuk", "Sofonias", "Hagai", "Zacarias", "Malakias", "1 Macabeo", "2 Macabeo",
           "Mateo", "Marcos", "Lucas", "Juan", "Mga Gawa", "Roma", "1 Corinto", "2 Corinto", "Galacia", "Efeso",
           "Filipos", "Colosas", "1 Tesalonica", "2 Tesalonica", "1 Timoteo", "2 Timoteo", "Tito", "Filemon",
           "Hebreo", "Santiago", "1 Pedro", "2 Pedro", "1 Juan", "2 Juan", "3 Juan", "Judas", "Pahayag"]
PSALM_ONE = {"en": "Psalm", "es": "Salmo", "pt": "Salmo", "tl": "Awit"}
CCC_WORD = {"en": "Catechism", "es": "Catecismo", "pt": "Catecismo", "tl": "Katesismo"}
CCC_PARTS = [  # first paragraph, names
    (1, ("Prologue", "Prólogo", "Prólogo", "Paunang salita")),
    (26, ("Part One: The Profession of Faith", "Primera parte: La profesión de la fe", "Primeira parte: A profissão da fé", "Unang bahagi: Ang pagpapahayag ng pananampalataya")),
    (1066, ("Part Two: The Celebration of the Christian Mystery", "Segunda parte: La celebración del misterio cristiano", "Segunda parte: A celebração do mistério cristão", "Ikalawang bahagi: Ang pagdiriwang ng misteryong Kristiyano")),
    (1691, ("Part Three: Life in Christ", "Tercera parte: La vida en Cristo", "Terceira parte: A vida em Cristo", "Ikatlong bahagi: Ang buhay kay Kristo")),
    (2558, ("Part Four: Christian Prayer", "Cuarta parte: La oración cristiana", "Quarta parte: A oração cristã", "Ikaapat na bahagi: Ang panalanging Kristiyano")),
]
# The 90-day OCIA plan reads the Catechism by topic: the site's topic list, plus a first topic on our desire for God
OCIA_TOPICS = [("Our desire for God", "El deseo de Dios", "O desejo de Deus", "Ang pananabik sa Diyos", 27, 49)] + \
    [t for t in features.CCC_TOPICS if t[0] != "Indulgences"]  # Indulgences sits inside Confession

PLAN_IDS = ("bible", "catechism", "gospels", "ocia")
PLAN_DAYS = {"bible": 365, "catechism": 365, "gospels": 30, "ocia": 90}


def load_bible():
    books = json.loads((BIBLE / "books.json").read_text(encoding="utf-8"))
    for b in books:
        b["text"] = json.loads((BIBLE / f"{b['n']}.json").read_text(encoding="utf-8"))
    return books


def verses(books, nums):
    """Flat list of (book n, chapter, verse, weight, last verse of chapter?) for the given books."""
    out = []
    for n in nums:
        b = books[n - 1]
        for ci, ch in enumerate(b["text"], 1):
            for vi, t in enumerate(ch, 1):
                out.append((n, ci, vi, max(len(t), 20), vi == len(ch)))
    return out


def split(vs, days, snap=0.5):
    """Cut a run of verses into `days` portions of about equal length.

    Works day by day: each portion aims at the length still to read divided by the days left,
    and a cut in the middle of a chapter costs as much as being `snap` of a day's length off."""
    cum = [0]
    for v in vs:
        cum.append(cum[-1] + v[3])
    portions, s, n = [], 0, len(vs)
    for k in range(days):
        left = days - k
        if left == 1:
            portions.append(vs[s:])
            break
        target = (cum[n] - cum[s]) / left
        best, best_cost = None, None
        lo = bisect.bisect_left(cum, cum[s] + 0.35 * target)
        hi = bisect.bisect_right(cum, cum[s] + 2.0 * target)
        for e in range(max(lo, s + 1), min(hi, n - left + 1) + 1):  # portion is vs[s:e]
            dev = (cum[e] - cum[s] - target) / target
            cost = dev * dev + (0 if vs[e - 1][4] else snap * snap)
            if best_cost is None or cost < best_cost:
                best, best_cost = e, cost
        if best is None:
            best = s + 1
        portions.append(vs[s:best])
        s = best
    assert len(portions) == days and all(portions), "empty portion"
    return portions


def segments(portion, books):
    """Group a portion's verses by book: [(book, c1, v1, c2, v2, whole_chapters)]."""
    segs = []
    for n, c, v, _, last in portion:
        if segs and segs[-1][0] == n:
            segs[-1][3:5] = [c, v]
            segs[-1][5] = last
        else:
            segs.append([n, c, v, c, v, last])
    out = []
    for n, c1, v1, c2, v2, last in segs:
        whole = v1 == 1 and v2 == len(books[n - 1]["text"][c2 - 1])
        out.append((n, c1, v1, c2, v2, whole))
    return out


def psalm_modern(dr):
    """Douay-Rheims (Greek/Latin) psalm number -> modern (Hebrew) numbers as (first, last)."""
    if dr <= 8 or dr >= 148:
        return dr, dr
    if dr == 9:
        return 9, 10
    if dr <= 112:
        return dr + 1, dr + 1
    if dr == 113:
        return 114, 115
    if dr in (114, 115):
        return 116, 116
    if dr <= 145:
        return dr + 1, dr + 1
    return 147, 147  # 146 and 147


def bible_reading(seg, books, lang):
    n, c1, v1, c2, v2, whole = seg
    b = books[n - 1]
    names = {"en": b["name"], "es": BOOK_ES[n - 1], "pt": BOOK_PT[n - 1], "tl": BOOK_TL[n - 1]}
    sep = "," if lang == "pt" else ":"
    if whole:
        span = f"{c1}" if c1 == c2 else f"{c1}–{c2}"
        ref = f"{b['code']}+{c1}" if c1 == c2 else f"{b['code']}+{c1}-{c2}"
    elif c1 == c2:
        span = f"{c1}{sep}{v1}–{v2}"
        ref = f"{b['code']}+{c1}:{v1}-{v2}"
    else:
        span = f"{c1}{sep}{v1}–{c2}{sep}{v2}"
        ref = f"{b['code']}+{c1}:{v1}-{c2}:{v2}"
    name = names[lang]
    if n == 21:
        if c1 == c2 and lang != "tl":
            name = PSALM_ONE[lang]
        m1, m2 = psalm_modern(c1)[0], psalm_modern(c2)[1]
        if (m1, m2) != (c1, c2):
            modern = f"{m1}" if m1 == m2 else f"{m1}–{m2}"
            span += f" ({modern})"
    return {"k": "b", "l": f"{name} {span}", "r": ref}


def ccc_reading(a, b, lang, topic=None):
    part = [names[LI[lang]] for start, names in CCC_PARTS if start <= a][-1]
    r = {"k": "c", "l": f"{CCC_WORD[lang]} {a}–{b}", "u": features.ccc_page(a, lang), "t": topic or part}
    u2 = features.ccc_page(b, lang)
    if u2 != r["u"]:
        r["u2"] = u2
    return r


def even(a, b, days):
    """Split paragraphs a..b into `days` runs of nearly equal size."""
    n = b - a + 1
    out, s = [], a
    for d in range(days):
        size = n // days + (1 if d < n % days else 0)
        out.append((s, s + size - 1))
        s += size
    return out


def build_plans(books):
    wisdom = [21, 22, 23, 24, 25, 26]  # Psalms, Proverbs, Ecclesiastes, Song of Songs, Wisdom, Sirach
    ot = [b["n"] for b in books if not b["nt"] and b["n"] not in wisdom]
    nt = [b["n"] for b in books if b["nt"]]
    stream = {
        "ot": split(verses(books, ot), 365),
        "nt": split(verses(books, nt), 365),
        "ps": split(verses(books, wisdom), 365, snap=0.8),
        "gospels": split(verses(books, [47, 48, 49, 50]), 30),
        "ocia": split(verses(books, [49, 50, 51]), 90),  # Luke, John, Acts
    }
    # OCIA Catechism: give each topic a share of the 90 days by its length, at least one day each
    sizes = [t[5] - t[4] + 1 for t in OCIA_TOPICS]
    total = sum(sizes)
    alloc = [max(1, round(s * 90 / total)) for s in sizes]
    while sum(alloc) > 90:
        i = max(range(len(alloc)), key=lambda i: alloc[i] - sizes[i] * 90 / total)
        alloc[i] -= 1
    while sum(alloc) < 90:
        i = min(range(len(alloc)), key=lambda i: alloc[i] - sizes[i] * 90 / total)
        alloc[i] += 1
    ocia_ccc = []
    for t, d in zip(OCIA_TOPICS, alloc):
        for a, b in even(t[4], t[5], d):
            ocia_ccc.append((a, b, t))
    assert len(ocia_ccc) == 90
    ccc_year = even(1, 2865, 365)
    return stream, ccc_year, ocia_ccc


def write(out_dir):
    books = load_bible()
    stream, ccc_year, ocia_ccc = build_plans(books)
    out_dir.mkdir(parents=True, exist_ok=True)
    for lang in LANGS:
        br = lambda p: [bible_reading(s, books, lang) for s in segments(p, books)]
        plans = {
            "bible": [br(stream["ot"][d]) + br(stream["nt"][d]) + br(stream["ps"][d]) for d in range(365)],
            "catechism": [[ccc_reading(a, b, lang)] for a, b in ccc_year],
            "gospels": [br(p) for p in stream["gospels"]],
            "ocia": [br(stream["ocia"][d]) + [ccc_reading(a, b, lang, t[LI[lang]])] for d, (a, b, t) in enumerate(ocia_ccc)],
        }
        for k, v in plans.items():
            assert len(v) == PLAN_DAYS[k]
        (out_dir / f"plans-{lang}.json").write_text(json.dumps(plans, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return plans


if __name__ == "__main__":
    p = write(ROOT / "site" / "data")
    for k in PLAN_IDS:
        print(k, len(p[k]), p[k][0], p[k][-1])
