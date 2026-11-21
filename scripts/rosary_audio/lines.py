"""What the guided-Rosary voice says, built from texts.json (the page's own prayer texts).

Clip ids:
  sign, creed, fatima, queen, close        whole prayers
  our_a/our_b, hail_a/hail_b, glory_a/glory_b
                                           the leader's half and the response half,
                                           so the player can "take turns" with you
  intro_<set>                              "Today we pray the Joyful Mysteries."
  m_<set>_<n>                              mystery announcement with its short meditation
  amen_end                                 a short closing line
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
TEXTS = json.load(open(os.path.join(HERE, "texts.json"), encoding="utf-8"))
SETS = ["joyful", "luminous", "sorrowful", "glorious"]

# Where the response half of a prayer begins, per language.
SPLIT = {
    "en": {"our": "Give us this day", "hail": "Holy Mary", "glory": "as it was in the beginning"},
    "es": {"our": "Danos hoy", "hail": "Santa María", "glory": "Como era en el principio"},
    "pt": {"our": "O pão nosso", "hail": "Santa Maria", "glory": "Como era no princípio"},
    "tl": {"our": "Bigyan mo kami", "hail": "Santa Maria", "glory": "Kapara noong unang-una"},
}

ORD = {
    "en": ["First", "Second", "Third", "Fourth", "Fifth"],
    "es": ["Primer", "Segundo", "Tercer", "Cuarto", "Quinto"],
    "pt": ["Primeiro", "Segundo", "Terceiro", "Quarto", "Quinto"],
    "tl": ["Unang", "Ikalawang", "Ikatlong", "Ikaapat na", "Ikalimang"],
}
ADJ = {
    "en": {"joyful": "Joyful", "luminous": "Luminous", "sorrowful": "Sorrowful", "glorious": "Glorious"},
    "es": {"joyful": "gozoso", "luminous": "luminoso", "sorrowful": "doloroso", "glorious": "glorioso"},
    "pt": {"joyful": "gozoso", "luminous": "luminoso", "sorrowful": "doloroso", "glorious": "glorioso"},
}


def clean(t):
    t = t.replace("\n", " ").replace("’", "'")
    t = re.sub(r"[“”«»]", '"', t)
    return re.sub(r"\s+", " ", t).strip()


def split(lang, key, text):
    at = SPLIT[lang][key]
    i = text.find(at)
    if i < 0:
        raise SystemExit("split point %r not found in %s/%s" % (at, lang, key))
    return clean(text[:i]), clean(text[i:])


def mystery_head(lang, s, n):
    if lang == "en":
        return "The %s %s Mystery." % (ORD["en"][n], ADJ["en"][s])
    if lang == "es":
        return "%s misterio %s." % (ORD["es"][n], ADJ["es"][s])
    if lang == "pt":
        return "%s mistério %s." % (ORD["pt"][n], ADJ["pt"][s])
    return "%s Misteryo ng %s." % (ORD["tl"][n], TEXTS["tl"]["SETS"][s]["short"])


FRUIT = {"en": "Fruit of the mystery: %s.", "es": "Fruto del misterio: %s.",
         "pt": "Fruto do mistério: %s.", "tl": "Bunga ng misteryo: %s."}
INTRO = {"en": "Today we pray the %s.", "es": "Hoy rezamos los %s.",
         "pt": "Hoje rezamos os %s.", "tl": "Ngayon ay dadasalin natin ang %s."}
END = {"en": "May God bless you. Amen.", "es": "Que Dios te bendiga. Amén.",
       "pt": "Que Deus te abençoe. Amém.", "tl": "Pagpalain ka nawa ng Diyos. Amen."}


def lower_first(t):
    return t[:1].lower() + t[1:]


def clips(lang):
    P, S = TEXTS[lang]["P"], TEXTS[lang]["SETS"]
    out = []
    for k in ("sign", "creed", "fatima", "queen", "close"):
        out.append((k, clean(P[k]["x"])))
    for k in ("our", "hail", "glory"):
        a, b = split(lang, k, P[k]["x"])
        out += [(k + "_a", a), (k + "_b", b)]
    for s in SETS:
        out.append(("intro_" + s, INTRO[lang] % S[s]["name"]))
        for n, m in enumerate(S[s]["m"]):
            name, _ref, fruit, desc = m[0], m[1], m[2], m[3]
            fr = fruit if lang == "tl" else lower_first(fruit)
            out.append(("m_%s_%d" % (s, n + 1),
                        "%s %s. %s %s" % (mystery_head(lang, s, n), clean(name), clean(desc), FRUIT[lang] % fr)))
    out.append(("amen_end", END[lang]))
    return out


if __name__ == "__main__":
    for lg in TEXTS:
        for cid, text in clips(lg):
            print(lg, cid, "|", text[:110])
