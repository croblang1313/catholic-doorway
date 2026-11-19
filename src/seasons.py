"""Advent and Christmas: this season's dates, and the seasonal banner on each home page.

{{ADVENT_DATES}}   a table of this Advent and Christmas season's dates (U.S. calendar)
{{SEASON_BANNER}}  a home-page card that main.js shows from mid-November to the Baptism of the Lord
"""
import datetime as dt
import html

D = dt.date

MONTHS = {
    "en": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
    "es": ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"],
    "pt": ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"],
    "tl": ["Enero", "Pebrero", "Marso", "Abril", "Mayo", "Hunyo", "Hulyo", "Agosto", "Setyembre", "Oktubre", "Nobyembre", "Disyembre"],
}
DAYS = {
    "en": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    "es": ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"],
    "pt": ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"],
    "tl": ["Lunes", "Martes", "Miyerkoles", "Huwebes", "Biyernes", "Sabado", "Linggo"],
}
ADVENT_URL = {"en": "/advent", "es": "/es/adviento", "pt": "/pt/advento", "tl": "/tl/adbiyento"}


def fmt(d, lang, weekday=True):
    m, wd = MONTHS[lang][d.month - 1], DAYS[lang][d.weekday()]
    if lang == "en":
        s = f"{m} {d.day}"
        return f"{wd}, {s}" if weekday else s
    if lang == "tl":
        s = f"{m} {d.day}"
        return f"{wd}, {s}" if weekday else s
    s = f"{d.day} de {m}"
    return f"{wd}, {s}" if weekday else s


def season_dates(y):
    """Dates for the Advent that begins in year y and the Christmas season that follows (U.S.)."""
    xmas = D(y, 12, 25)
    adv1 = xmas - dt.timedelta(days=xmas.weekday() + 1 + 21)  # 4th Sunday before Christmas
    imm = D(y, 12, 8)
    imm_moved = imm.weekday() == 6
    if imm_moved:
        imm = D(y, 12, 9)
    xd = (xmas.weekday() + 1) % 7  # 0 = Sunday
    holy_family = D(y, 12, 30) if xd == 0 else xmas + dt.timedelta(days=7 - xd)
    jan1 = D(y + 1, 1, 1)
    jan1_obl = jan1.weekday() not in (0, 5)  # U.S.: no obligation when it falls on a Saturday or Monday
    epiph = next(D(y + 1, 1, d) for d in range(2, 9) if D(y + 1, 1, d).weekday() == 6)
    bapt = epiph + dt.timedelta(days=1) if epiph.day >= 7 else epiph + dt.timedelta(days=7)
    return dict(adv1=adv1, adv=[adv1 + dt.timedelta(days=7 * i) for i in range(4)], imm=imm, imm_moved=imm_moved,
                guad=D(y, 12, 12), simbang=(D(y, 12, 16), D(y, 12, 24)), oant=(D(y, 12, 17), D(y, 12, 23)),
                xmas=xmas, holy_family=holy_family, jan1=jan1, jan1_obl=jan1_obl, epiph=epiph, bapt=bapt)


def current_year(today=None):
    today = today or dt.date.today()
    last = season_dates(today.year - 1)
    return today.year - 1 if today <= last["bapt"] else today.year


L = {
    "en": dict(a=["First Sunday of Advent", "Second Sunday of Advent", "Third Sunday of Advent (Gaudete, rose candle)", "Fourth Sunday of Advent"],
               imm="Immaculate Conception", obl="holy day of obligation", noobl="no obligation this year",
               imm_moved="moved to Monday because December 8 is a Sunday; no obligation this year",
               guad="Our Lady of Guadalupe", simbang="Simbang Gabi (Filipino dawn or evening Masses)",
               oant="“O Antiphons”", xmas="Christmas, the Nativity of the Lord", xmas_eve="Christmas Eve Masses",
               hf="The Holy Family", jan1="Mary, Mother of God", ep="The Epiphany of the Lord",
               bapt="The Baptism of the Lord (Christmas season ends)", to="to", season="Advent and Christmas",
               head=("Date", "Celebration"),
               banner_k="Advent begins {d}", banner_h="Get ready for Christmas",
               banner_p="Advent wreath prayers, the O Antiphons, Simbang Gabi, Confession before Christmas and every date for this season.",
               go="Open the Advent guide"),
    "es": dict(a=["Primer domingo de Adviento", "Segundo domingo de Adviento", "Tercer domingo de Adviento (Gaudete, vela rosa)", "Cuarto domingo de Adviento"],
               imm="La Inmaculada Concepción", obl="día de precepto", noobl="este año no es de precepto",
               imm_moved="se pasa al lunes porque el 8 de diciembre cae en domingo; este año no es de precepto",
               guad="Nuestra Señora de Guadalupe", simbang="Simbang Gabi (Misas filipinas de madrugada o de noche)",
               oant="Las antífonas «O»", xmas="Navidad, la Natividad del Señor", xmas_eve="Misas de Nochebuena",
               hf="La Sagrada Familia", jan1="Santa María, Madre de Dios", ep="La Epifanía del Señor",
               bapt="El Bautismo del Señor (termina el tiempo de Navidad)", to="al", season="Adviento y Navidad",
               head=("Fecha", "Celebración"),
               banner_k="El Adviento empieza el {d}", banner_h="Prepárate para la Navidad",
               banner_p="Oraciones para la corona de Adviento, las antífonas «O», las Posadas, la confesión antes de Navidad y todas las fechas de este tiempo.",
               go="Abrir la guía de Adviento"),
    "pt": dict(a=["Primeiro domingo do Advento", "Segundo domingo do Advento", "Terceiro domingo do Advento (Gaudete, vela rosa)", "Quarto domingo do Advento"],
               imm="Imaculada Conceição", obl="dia santo de guarda", noobl="neste ano não é de preceito",
               imm_moved="passa para segunda-feira porque 8 de dezembro cai num domingo; neste ano não é de preceito",
               guad="Nossa Senhora de Guadalupe", simbang="Simbang Gabi (Missas filipinas de madrugada ou à noite)",
               oant="As antífonas do “Ó”", xmas="Natal, a Natividade do Senhor", xmas_eve="Missas da véspera de Natal",
               hf="A Sagrada Família", jan1="Santa Maria, Mãe de Deus", ep="A Epifania do Senhor",
               bapt="O Batismo do Senhor (termina o tempo do Natal)", to="a", season="Advento e Natal",
               head=("Data", "Celebração"),
               banner_k="O Advento começa em {d}", banner_h="Prepare-se para o Natal",
               banner_p="Orações da coroa do Advento, as antífonas do “Ó”, a confissão antes do Natal e todas as datas deste tempo.",
               go="Abrir o guia do Advento"),
    "tl": dict(a=["Unang Linggo ng Adbiyento", "Ikalawang Linggo ng Adbiyento", "Ikatlong Linggo ng Adbiyento (Gaudete, kandilang rosas)", "Ikaapat na Linggo ng Adbiyento"],
               imm="Ang Kalinis-linisang Paglilihi", obl="pistang pangilin", noobl="hindi pistang pangilin ngayong taon",
               imm_moved="inilipat sa Lunes dahil Linggo ang Disyembre 8; hindi pistang pangilin ngayong taon",
               guad="Mahal na Birhen ng Guadalupe", simbang="Simbang Gabi",
               oant="Ang mga “O Antiphon”", xmas="Pasko, ang Pagsilang ng Panginoon", xmas_eve="Mga Misa sa Bisperas ng Pasko",
               hf="Ang Banal na Mag-anak", jan1="Santa Maria, Ina ng Diyos", ep="Ang Pagpapakita ng Panginoon (Tatlong Hari)",
               bapt="Ang Pagbibinyag sa Panginoon (katapusan ng Panahon ng Pasko)", to="hanggang", season="Adbiyento at Pasko",
               head=("Petsa", "Pagdiriwang"),
               banner_k="Magsisimula ang Adbiyento sa {d}", banner_h="Maghanda para sa Pasko",
               banner_p="Mga dasal sa korona ng Adbiyento, ang Simbang Gabi, ang Kumpisal bago mag-Pasko at lahat ng petsa ng panahong ito.",
               go="Buksan ang gabay sa Adbiyento"),
}


def dates_table(lang, y=None):
    y = current_year() if y is None else y
    s, t = season_dates(y), L[lang]
    e = html.escape
    rows = [(d, fmt(d, lang), t["a"][i]) for i, d in enumerate(s["adv"])]
    rows.append((s["imm"], fmt(s["imm"], lang), f'{t["imm"]} ({t["imm_moved"] if s["imm_moved"] else t["obl"]})'))
    rows.append((s["guad"], fmt(s["guad"], lang), t["guad"]))
    rows.append((s["simbang"][0], f'{fmt(s["simbang"][0], lang, False)} {t["to"]} {fmt(s["simbang"][1], lang, False)}', t["simbang"]))
    rows.append((s["oant"][0], f'{fmt(s["oant"][0], lang, False)} {t["to"]} {fmt(s["oant"][1], lang, False)}', t["oant"]))
    rows.append((s["xmas"] - dt.timedelta(days=1), fmt(s["xmas"] - dt.timedelta(days=1), lang), t["xmas_eve"]))
    rows.append((s["xmas"], fmt(s["xmas"], lang), f'{t["xmas"]} ({t["obl"]})'))
    rows.append((s["holy_family"], fmt(s["holy_family"], lang), t["hf"]))
    rows.append((s["jan1"], fmt(s["jan1"], lang), f'{t["jan1"]} ({t["obl"] if s["jan1_obl"] else t["noobl"]})'))
    rows.append((s["epiph"], fmt(s["epiph"], lang), t["ep"]))
    rows.append((s["bapt"], fmt(s["bapt"], lang), t["bapt"]))
    rows = [(a, b) for _, a, b in sorted(rows, key=lambda r: r[0])]
    body = "".join(f"<tr><td>{e(a)}</td><td>{e(b)}</td></tr>" for a, b in rows)
    return (f'<div class="table-wrap"><table class="season-dates"><caption>{e(t["season"])} {y}&ndash;{y + 1}</caption>'
            f'<thead><tr><th scope="col">{t["head"][0]}</th><th scope="col">{t["head"][1]}</th></tr></thead><tbody>{body}</tbody></table></div>')


def banner(lang, y=None):
    y = current_year() if y is None else y
    s, t = season_dates(y), L[lang]
    show_from = s["adv1"] - dt.timedelta(days=21)
    return (f'<a class="card tile season-card" href="{ADVENT_URL[lang]}" data-show-from="{show_from.isoformat()}" '
            f'data-show-to="{s["bapt"].isoformat()}" hidden><p class="label">{html.escape(t["banner_k"].format(d=fmt(s["adv1"], lang, False)))}</p>'
            f'<h3>{html.escape(t["banner_h"])}</h3><p>{html.escape(t["banner_p"])}</p><span class="go">{html.escape(t["go"])} &rarr;</span></a>')


def render(body, lang):
    if "{{ADVENT_DATES}}" in body:
        body = body.replace("{{ADVENT_DATES}}", dates_table(lang))
    if "{{SEASON_BANNER}}" in body:
        body = body.replace("{{SEASON_BANNER}}", banner(lang))
    return body


if __name__ == "__main__":
    for yy in (2026, 2027, 2028):
        print(yy, {k: str(v) for k, v in season_dates(yy).items()})
