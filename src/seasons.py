"""Advent and Christmas: this season's dates, and the seasonal banner on each home page.

{{ADVENT_DATES}}   a table of this Advent and Christmas season's dates (U.S. calendar)
{{SEASON_BANNER}}  the "Right now in the Church" cards: one per part of the year plus holy days; main.js shows today's
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


def render(body, lang, url=None):
    if "{{ADVENT_DATES}}" in body:
        body = body.replace("{{ADVENT_DATES}}", dates_table(lang))
    if "{{ADVENT_CALENDAR}}" in body:
        import advent_calendar
        body = advent_calendar.render(body, lang)
    if "{{SEASON_BANNER}}" in body:
        body = body.replace("{{SEASON_BANNER}}", now_cards(lang, url) if url else banner(lang))
    return body


if __name__ == "__main__":
    for yy in (2026, 2027, 2028):
        print(yy, {k: str(v) for k, v in season_dates(yy).items()})


# ---------- "Right now in the Church": one home-page card for every part of the year ----------
def easter(y):
    """Gregorian Easter Sunday (anonymous algorithm)."""
    a, b, c = y % 19, y // 100, y % 100
    d, e_ = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l_ = (32 + 2 * e_ + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l_) // 451
    month = (h + l_ - 7 * m + 114) // 31
    day = (h + l_ - 7 * m + 114) % 31 + 1
    return D(y, month, day)


NOW = {
    "en": dict(
        advent_k="Now: Advent. Christmas is {d}", christmas_k="Now: the Christmas season", christmas_h="Merry Christmas!",
        christmas_p="Christmas lasts until the Baptism of the Lord on {d}. Keep celebrating, and see every date of the season.",
        christmas_go="Open the Christmas guide",
        ordinary_k="Now: Ordinary Time", ordinary_h="Grow a little every day",
        ordinary_p="The green season is a good time to build one habit: a reading plan, the daily Rosary, or a novena with reminders.",
        ordinary_go="Pick a reading plan",
        prelent_k="Lent begins {d}", prelent_h="Ash Wednesday is coming",
        prelent_p="A day of fasting and abstinence. Ashes are given at Mass, and anyone may receive them. Plan a Lent of prayer, fasting and giving.",
        prelent_go="See the holy days calendar",
        lent_k="Now: Lent. Easter is {d}", lent_h="Pray, fast and give",
        lent_p="No meat on Fridays (ages 14 and up), the Stations of the Cross on Fridays, and Confession before Easter.",
        lent_go="Pray the Stations of the Cross",
        holy_k="Now: Holy Week", holy_h="Walk with Jesus to the Cross",
        holy_p="The evening Mass of Holy Thursday, Good Friday (a day of fasting and abstinence), and the Easter Vigil on Saturday night.",
        holy_go="Pray the Stations of the Cross",
        easter_k="Now: the Easter season, until Pentecost on {d}", easter_h="He is risen!",
        easter_p="Fifty days of joy. Divine Mercy Sunday is {d}, and the Regina Caeli takes the place of the Angelus.",
        easter_go="Pray the Divine Mercy Chaplet",
        hdo_k="Holy day of obligation", hdo_h="{n}: {d}",
        hdo_p="Catholics are asked to go to Mass on this day or the evening before. Check Mass times at a parish near you.",
        hdo_go="Find a church", all_saints="All Saints", assumption="The Assumption of Mary"),
    "es": dict(
        advent_k="Ahora: Adviento. La Navidad es el {d}", christmas_k="Ahora: el tiempo de Navidad", christmas_h="¡Feliz Navidad!",
        christmas_p="La Navidad dura hasta el Bautismo del Señor, el {d}. Sigue celebrando y consulta todas las fechas del tiempo.",
        christmas_go="Abrir la guía de Navidad",
        ordinary_k="Ahora: Tiempo Ordinario", ordinary_h="Crece un poco cada día",
        ordinary_p="El tiempo verde es ideal para formar un hábito: un plan de lectura, el Rosario diario o una novena con recordatorios.",
        ordinary_go="Elegir un plan de lectura",
        prelent_k="La Cuaresma empieza el {d}", prelent_h="Se acerca el Miércoles de Ceniza",
        prelent_p="Día de ayuno y abstinencia. La ceniza se impone en la Misa y cualquiera puede recibirla. Prepara una Cuaresma de oración, ayuno y limosna.",
        prelent_go="Ver el calendario de días santos",
        lent_k="Ahora: Cuaresma. La Pascua es el {d}", lent_h="Ora, ayuna y comparte",
        lent_p="Sin carne los viernes (desde los 14 años), el Vía Crucis los viernes y la confesión antes de Pascua.",
        lent_go="Rezar el Vía Crucis",
        holy_k="Ahora: Semana Santa", holy_h="Acompaña a Jesús hasta la cruz",
        holy_p="La Misa vespertina del Jueves Santo, el Viernes Santo (día de ayuno y abstinencia) y la Vigilia Pascual el sábado por la noche.",
        holy_go="Rezar el Vía Crucis",
        easter_k="Ahora: tiempo de Pascua, hasta Pentecostés el {d}", easter_h="¡Ha resucitado!",
        easter_p="Cincuenta días de alegría. El Domingo de la Divina Misericordia es el {d}, y el Regina Coeli sustituye al Ángelus.",
        easter_go="Rezar la Coronilla de la Divina Misericordia",
        hdo_k="Día de precepto", hdo_h="{n}: {d}",
        hdo_p="Los católicos estamos llamados a ir a Misa ese día o la tarde anterior. Consulta los horarios de una parroquia cercana.",
        hdo_go="Buscar una iglesia", all_saints="Todos los Santos", assumption="La Asunción de María"),
    "pt": dict(
        advent_k="Agora: Advento. O Natal é {d}", christmas_k="Agora: o tempo do Natal", christmas_h="Feliz Natal!",
        christmas_p="O Natal vai até o Batismo do Senhor, em {d}. Continue celebrando e veja todas as datas do tempo.",
        christmas_go="Abrir o guia do Natal",
        ordinary_k="Agora: Tempo Comum", ordinary_h="Cresça um pouco a cada dia",
        ordinary_p="O tempo verde é ótimo para criar um hábito: um plano de leitura, o Rosário diário ou uma novena com lembretes.",
        ordinary_go="Escolher um plano de leitura",
        prelent_k="A Quaresma começa em {d}", prelent_h="A Quarta-feira de Cinzas está chegando",
        prelent_p="Dia de jejum e abstinência. As cinzas são impostas na Missa, e qualquer pessoa pode recebê-las. Prepare uma Quaresma de oração, jejum e caridade.",
        prelent_go="Ver o calendário de dias santos",
        lent_k="Agora: Quaresma. A Páscoa é {d}", lent_h="Reze, jejue e partilhe",
        lent_p="Sem carne às sextas-feiras (a partir dos 14 anos), a Via-Sacra às sextas e a confissão antes da Páscoa.",
        lent_go="Rezar a Via-Sacra",
        holy_k="Agora: Semana Santa", holy_h="Acompanhe Jesus até a cruz",
        holy_p="A Missa da Ceia do Senhor na Quinta-feira Santa, a Sexta-feira Santa (dia de jejum e abstinência) e a Vigília Pascal no sábado à noite.",
        holy_go="Rezar a Via-Sacra",
        easter_k="Agora: tempo pascal, até Pentecostes em {d}", easter_h="Ele ressuscitou!",
        easter_p="Cinquenta dias de alegria. O Domingo da Divina Misericórdia é {d}, e a Rainha do Céu substitui o Angelus.",
        easter_go="Rezar o Terço da Misericórdia",
        hdo_k="Dia santo de guarda", hdo_h="{n}: {d}",
        hdo_p="Os católicos são chamados a ir à Missa nesse dia ou na véspera à tarde. Veja os horários de uma paróquia perto de você.",
        hdo_go="Encontrar uma igreja", all_saints="Todos os Santos", assumption="A Assunção de Maria"),
    "tl": dict(
        advent_k="Ngayon: Adbiyento. Pasko sa {d}", christmas_k="Ngayon: Panahon ng Pasko", christmas_h="Maligayang Pasko!",
        christmas_p="Tumatagal ang Pasko hanggang sa Pagbibinyag sa Panginoon sa {d}. Ituloy ang pagdiriwang at tingnan ang lahat ng petsa.",
        christmas_go="Buksan ang gabay sa Pasko",
        ordinary_k="Ngayon: Karaniwang Panahon", ordinary_h="Lumago nang kaunti araw-araw",
        ordinary_p="Magandang panahon ito para bumuo ng isang gawi: isang plano sa pagbasa, ang araw-araw na Rosaryo, o isang nobena na may paalala.",
        ordinary_go="Pumili ng plano sa pagbasa",
        prelent_k="Magsisimula ang Kuwaresma sa {d}", prelent_h="Malapit na ang Miyerkoles ng Abo",
        prelent_p="Araw ng pag-aayuno at abstinensiya. Ipinapahid ang abo sa Misa, at maaaring tumanggap ang sinuman. Planuhin ang Kuwaresma ng panalangin, pag-aayuno at pagkakawanggawa.",
        prelent_go="Tingnan ang kalendaryo ng mga banal na araw",
        lent_k="Ngayon: Kuwaresma. Pasko ng Pagkabuhay sa {d}", lent_h="Manalangin, mag-ayuno at magbahagi",
        lent_p="Walang karne tuwing Biyernes (edad 14 pataas), ang Daan ng Krus tuwing Biyernes, at Kumpisal bago ang Pasko ng Pagkabuhay.",
        lent_go="Magdasal ng Daan ng Krus",
        holy_k="Ngayon: Mahal na Araw", holy_h="Samahan si Hesus hanggang sa Krus",
        holy_p="Ang Misa sa gabi ng Huwebes Santo, ang Biyernes Santo (araw ng pag-aayuno at abstinensiya), at ang Bihilya ng Pasko sa Sabado ng gabi.",
        holy_go="Magdasal ng Daan ng Krus",
        easter_k="Ngayon: Panahon ng Pasko ng Pagkabuhay, hanggang Pentekostes sa {d}", easter_h="Siya ay muling nabuhay!",
        easter_p="Limampung araw ng kagalakan. Ang Linggo ng Banal na Awa ay sa {d}, at ang Regina Caeli ang pumapalit sa Orasyon.",
        easter_go="Magdasal ng Koronilya ng Banal na Awa",
        hdo_k="Pistang pangilin", hdo_h="{n}: {d}",
        hdo_p="Inaanyayahan ang mga Katoliko na magsimba sa araw na ito o sa bisperas nito. Tingnan ang oras ng Misa sa malapit na parokya.",
        hdo_go="Maghanap ng simbahan", all_saints="Todos los Santos (Undas)", assumption="Ang Pag-akyat kay Maria sa Langit"),
}


def _card(href, frm, to, kicker, head, para, go, extra=""):
    e = html.escape
    return (f'<a class="card tile season-card{extra}" href="{href}" data-show-from="{frm.isoformat()}" data-show-to="{to.isoformat()}" hidden>'
            f'<p class="label">{e(kicker)}</p><h3>{e(head)}</h3><p>{e(para)}</p><span class="go">{e(go)} &rarr;</span></a>')


def now_cards(lang, url, today=None):
    """Every season card from last year to next; main.js shows the one(s) whose dates include today."""
    today = today or dt.date.today()
    t, a, n = L[lang], NOW[lang], NOW[lang]
    day = dt.timedelta(days=1)
    cards = []
    for y in range(today.year - 1, today.year + 2):
        s = season_dates(y)            # Advent of year y and the Christmas season that follows
        ea = easter(y)
        ash, palm, pent = ea - dt.timedelta(days=46), ea - dt.timedelta(days=7), ea + dt.timedelta(days=49)
        prev = season_dates(y - 1)     # the Christmas season that ends in January of year y
        show_from = s["adv1"] - dt.timedelta(days=21)
        cards += [
            _card(url("reading-plans"), prev["bapt"] + day, ash - 8 * day, a["ordinary_k"], a["ordinary_h"], a["ordinary_p"], a["ordinary_go"]),
            _card(url("calendar"), ash - 7 * day, ash - day, a["prelent_k"].format(d=fmt(ash, lang, False)), a["prelent_h"], a["prelent_p"], a["prelent_go"]),
            _card(url("stations-of-the-cross"), ash, palm - day, a["lent_k"].format(d=fmt(ea, lang, False)), a["lent_h"], a["lent_p"], a["lent_go"]),
            _card(url("stations-of-the-cross"), palm, ea - day, a["holy_k"], a["holy_h"], a["holy_p"], a["holy_go"]),
            _card(url("divine-mercy-chaplet"), ea, pent, a["easter_k"].format(d=fmt(pent, lang, False)), a["easter_h"],
                  a["easter_p"].format(d=fmt(ea + 7 * day, lang, False)), a["easter_go"]),
            _card(url("reading-plans"), pent + day, show_from - day, a["ordinary_k"], a["ordinary_h"], a["ordinary_p"], a["ordinary_go"]),
            _card(url("advent"), show_from, s["adv1"] - day, t["banner_k"].format(d=fmt(s["adv1"], lang, False)), t["banner_h"], t["banner_p"], t["go"]),
            _card(url("advent"), s["adv1"], s["xmas"] - day, a["advent_k"].format(d=fmt(s["xmas"], lang)), t["banner_h"], t["banner_p"], t["go"]),
            _card(url("advent"), s["xmas"], s["bapt"], a["christmas_k"], a["christmas_h"], a["christmas_p"].format(d=fmt(s["bapt"], lang, False)), a["christmas_go"]),
        ]
        # U.S. holy days of obligation outside Christmas (Ascension is moved to Sunday in most of the U.S.)
        hdos = []
        if not s["imm_moved"]:
            hdos.append((s["imm"], t["imm"]))
        for d, name in ((D(y, 8, 15), n["assumption"]), (D(y, 11, 1), n["all_saints"])):
            if d.weekday() not in (0, 5, 6):
                hdos.append((d, name))
        jan1 = prev["jan1"]
        if prev["jan1_obl"]:
            hdos.append((jan1, t["jan1"]))
        for d, name in hdos:
            cards.append(_card(url("find-a-church"), d - 6 * day, d, a["hdo_k"], a["hdo_h"].format(n=name, d=fmt(d, lang)), a["hdo_p"], a["hdo_go"], " hdo-card"))
    # drop cards that ended before last month; the site is rebuilt every week
    keep = [c for c in cards if c.split('data-show-to="')[1][:10] >= (today - dt.timedelta(days=31)).isoformat()]
    return "\n    ".join(keep)
