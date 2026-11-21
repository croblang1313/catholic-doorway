"""Site organization: the task-grouped menu, the "What's next" cards, and the home-page journey paths.

Everything here is keyed by the English page slug; build.py passes in helpers that turn a key into
the page's URL and label in each language, so every language gets the same structure.

  MENU           top menu, in a fixed order (Home first, Find a Church as a button)
  NEXT           three suggested next pages at the bottom of each guide
  {{PATHS}}      the home page's "Where are you on the journey?" chooser
"""
import html

e = html.escape

# Top menu: (hub key, its menu label per language, child keys). The hub is listed first in its
# dropdown, then the rest A to Z. Order of the top items is fixed: it follows what visitors come to do.
MENU = [
    ("start-here", {"en": "Begin Here", "es": "Empieza aquí", "pt": "Comece aqui", "tl": "Magsimula"},
     ["start-here", "first-mass", "coming-back", "questions", "join-a-parish"]),
    ("prayers", {"en": "Pray", "es": "Orar", "pt": "Rezar", "tl": "Magdasal"},
     ["prayers", "rosary", "devotions", "stations-of-the-cross", "liturgy-of-the-hours", "prayer-wall", "advent"]),
    ("how-to", {"en": "Mass & Sacraments", "es": "Misa y sacramentos", "pt": "Missa e sacramentos", "tl": "Misa at sakramento"},
     ["how-to", "watch-mass", "inside-the-mass", "confession", "examination-of-conscience", "baptism", "first-communion",
      "confirmation", "marriage", "holy-orders", "anointing", "funerals"]),
    ("bible", {"en": "Bible", "es": "Biblia", "pt": "Bíblia", "tl": "Bibliya"},
     ["bible", "read-the-bible", "reading-plans", "calendar", "this-week"]),
    ("beliefs", {"en": "Learn", "es": "Aprender", "pt": "Aprender", "tl": "Matuto"},
     ["beliefs", "church-documents", "glossary", "church-anatomy", "vestments", "structure", "popes", "dioceses"]),
    ("saints", {"en": "Saints", "es": "Santos", "pt": "Santos", "tl": "Mga santo"},
     ["saints", "saints-directory"]),
    ("kids", {"en": "Kids & Families", "es": "Niños y familias", "pt": "Crianças", "tl": "Pamilya"},
     ["kids", "coloring-pages", "first-prayers", "mass-for-kids", "saint-stories", "family-corner"]),
]
CTA = "find-a-church"

# Menu labels that differ from the page's own short label (other entries come from the old dropdown labels).
LABELS = {
    "en": {"coming-back": "Coming Back to the Faith", "how-to": "All How-To Guides", "join-a-parish": "Join a Parish"},
    "es": {"how-to": "Todas las guías prácticas"},
    "pt": {"how-to": "Todos os guias práticos", "find-a-church": "Encontrar igreja"},
    "tl": {"how-to": "Lahat ng praktikal na gabay"},
}
WIDE = 9  # dropdowns with more items than this show in two columns on desktop

CHEVRON = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 9l6 6 6-6" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
SHOW = {"en": "Show pages in {}", "es": "Ver las páginas de {}", "pt": "Ver as páginas de {}", "tl": "Ipakita ang mga pahina ng {}"}


def nav(lang, current, url, label, sort_key):
    """The <li> items of the main menu. current is the English key of this page.

    url(key) -> URL or None (no translation), label(key) -> menu label, sort_key(label) -> A-Z key.
    """
    items = [f'        <li><a href="{url("index")}"{" aria-current=\"page\"" if current == "index" else ""}>{e(label("index"))}</a></li>']
    for hub, top, children in MENU:
        kids = [k for k in children if url(k)]
        rest = sorted((k for k in kids if k != hub), key=lambda k: sort_key(label(k)))
        kids = ([hub] if hub in kids else []) + rest
        here = current in kids
        sub = "".join(
            f'<li{" class=\"hub\"" if k == hub else ""}><a href="{url(k)}"{" aria-current=\"page\"" if k == current else ""}>{e(label(k))}</a></li>'
            for k in kids)
        wide = " wide" if len(kids) > WIDE else ""
        items.append(f'        <li class="has-sub{" open" if here else ""}"><a href="{url(hub)}"{" class=\"in-section\"" if here else ""}>{e(top[lang])}</a>'
                     f'<button class="sub-toggle" type="button" aria-expanded="{"true" if here else "false"}" aria-label="{e(SHOW[lang].format(top[lang]))}">{CHEVRON}</button>'
                     f'<ul class="sub{wide}">{sub}</ul></li>')
    items.append(f'        <li class="nav-cta"><a href="{url(CTA)}"{" aria-current=\"page\"" if current == CTA else ""}>{e(label(CTA))}</a></li>')
    return "\n".join(items)


# ---------- "What's next" cards at the bottom of a page ----------
NEXT = {
    "start-here": ["first-mass", "find-a-church", "questions"],
    "first-mass": ["inside-the-mass", "find-a-church", "start-here"],
    "questions": ["beliefs", "start-here", "first-mass"],
    "beliefs": ["questions", "church-documents", "start-here"],
    "coming-back": ["examination-of-conscience", "confession", "join-a-parish"],
    "join-a-parish": ["find-a-church", "how-to", "coming-back"],
    "how-to": ["find-a-church", "confession", "start-here"],
    "confession": ["examination-of-conscience", "find-a-church", "prayers"],
    "examination-of-conscience": ["confession", "find-a-church", "prayers"],
    "baptism": ["baptism-certificate", "find-a-church", "kids"],
    "baptism-certificate": ["baptism", "how-to", "find-a-church"],
    "first-communion": ["confession", "mass-for-kids", "family-corner"],
    "confirmation": ["saints-directory", "prayers", "how-to"],
    "marriage": ["find-a-church", "confession", "how-to"],
    "holy-orders": ["structure", "prayers", "how-to"],
    "anointing": ["prayers", "find-a-church", "funerals"],
    "funerals": ["prayers", "find-a-church", "how-to"],
    "inside-the-mass": ["first-mass", "church-anatomy", "vestments"],
    "church-anatomy": ["inside-the-mass", "vestments", "glossary"],
    "vestments": ["church-anatomy", "calendar", "glossary"],
    "watch-mass": ["bible", "prayers", "find-a-church"],
    "prayers": ["rosary", "devotions", "prayer-wall"],
    "rosary": ["prayers", "devotions", "reading-plans"],
    "devotions": ["divine-mercy-chaplet", "novenas", "angelus"],
    "divine-mercy-chaplet": ["devotions", "rosary", "prayer-wall"],
    "novenas": ["devotions", "rosary", "prayer-wall"],
    "angelus": ["devotions", "rosary", "liturgy-of-the-hours"],
    "stations-of-the-cross": ["devotions", "confession", "rosary"],
    "liturgy-of-the-hours": ["bible", "prayers", "reading-plans"],
    "prayer-wall": ["prayers", "rosary", "devotions"],
    "bible": ["reading-plans", "read-the-bible", "calendar"],
    "read-the-bible": ["reading-plans", "bible", "church-documents"],
    "reading-plans": ["bible", "church-documents", "rosary"],
    "calendar": ["advent", "bible", "find-a-church"],
    "this-week": ["calendar", "saints", "bible"],
    "advent": ["confession", "family-corner", "calendar"],
    "saints": ["saints-directory", "saint-stories", "prayers"],
    "saints-directory": ["saints", "dioceses", "calendar"],
    "structure": ["popes", "dioceses", "find-a-church"],
    "popes": ["structure", "church-documents", "saints"],
    "dioceses": ["find-a-church", "structure", "saints-directory"],
    "glossary": ["beliefs", "church-anatomy", "questions"],
    "church-documents": ["beliefs", "reading-plans", "glossary"],
    "find-a-church": ["first-mass", "start-here", "watch-mass"],
    "kids": ["first-prayers", "mass-for-kids", "family-corner"],
    "coloring-pages": ["saint-stories", "first-prayers", "family-corner"],
    "first-prayers": ["mass-for-kids", "coloring-pages", "prayers"],
    "mass-for-kids": ["first-prayers", "saint-stories", "first-communion"],
    "saint-stories": ["coloring-pages", "saints", "first-prayers"],
    "family-corner": ["advent", "first-communion", "kids"],
}
NEXT_WORD = {"en": "What’s next", "es": "¿Qué sigue?", "pt": "Próximos passos", "tl": "Susunod na hakbang"}


def next_cards(key, lang, url, label):
    keys = [k for k in NEXT.get(key, []) if url(k)]
    if not keys:
        return ""
    cards = "".join(f'<a class="card tile next-card" href="{url(k)}"><span>{e(label(k))}</span><span class="go" aria-hidden="true">&rarr;</span></a>' for k in keys)
    return (f'\n<div class="wrap"><section class="section next-steps" aria-labelledby="next-h">'
            f'<h2 id="next-h">{NEXT_WORD[lang]}</h2><div class="next-grid">{cards}</div></section></div>\n')


# ---------- Home page: "Where are you on the journey?" ----------
# Each path: (id, button label, intro, [(page key, step title, step detail)], when note)
PATHS = {
    "en": dict(
        h="Where are you on the journey?", lede="Pick the one that fits you best. Each path is a few simple steps, in order.",
        when="When", step="Step",
        paths=[
            ("curious", "Curious about becoming Catholic", "No pressure and no sign-up. This is the usual order.", [
                ("first-mass", "Go to a Sunday Mass and just watch", "Anyone is welcome. Sit toward the back; our phone guide tells you what happens."),
                ("questions", "Bring your questions", "Short, honest answers about Mary, confession, the Pope and more."),
                ("start-here", "Learn how OCIA works", "The Church's path for adults: its four stages, how long it takes, and what it costs (nothing)."),
                ("find-a-church", "Call a parish and ask about OCIA", "Find the parish nearest you and ask for the OCIA or RCIA coordinator."),
            ], "OCIA groups usually begin in late summer or fall, but you can call a parish any time of year."),
            ("returning", "Coming back to the faith", "Coming home is simpler than you might think.", [
                ("coming-back", "Read how coming back works", "No paperwork or classes are needed for most people. Just come."),
                ("examination-of-conscience", "Prepare for Confession", "A gentle examination of conscience to help you remember what to say."),
                ("confession", "Go to Confession", "Step by step, including what to say if it's been years. Parishes list Confession times online."),
                ("join-a-parish", "Join a parish", "Register so the parish can help with sacraments, from weddings to funerals."),
            ], "Any time. Many parishes add extra Confession times during Advent and Lent."),
            ("prayer", "Growing in daily prayer", "Build a simple daily rhythm, one habit at a time.", [
                ("bible", "Start the day with the Mass readings", "Today's readings, with audio, from the U.S. bishops."),
                ("rosary", "Pray the Rosary", "Start with one decade; the guide shows today's mysteries."),
                ("reading-plans", "Pick a reading plan", "The Bible in a Year, the Catechism in a Year, or the Gospels in 30 days."),
                ("devotions", "Add devotions with reminders", "The Angelus at noon, the Divine Mercy Chaplet at 3 p.m., and novenas."),
                ("examination-of-conscience", "End the day with an examen", "A few quiet minutes to look back on the day with God."),
            ], "Readings in the morning, the Angelus at noon, Divine Mercy at 3 p.m., and the examen before bed."),
            ("family", "Raising kids in the faith", "Small, joyful habits at home make the biggest difference.", [
                ("first-prayers", "Teach first prayers", "Large type with read-aloud, from the Sign of the Cross to bedtime prayers."),
                ("mass-for-kids", "Get ready for Mass together", "A picture guide to what happens, plus an I-spy game for church."),
                ("saint-stories", "Read a saint story at bedtime", "Short true stories, each with something to try."),
                ("family-corner", "Live the seasons at home", "Simple ideas for Advent, Christmas, Lent and Easter, plus sacrament prep sheets."),
                ("coloring-pages", "Color on a rainy day", "Free saints, Bible stories and seasons to print or color on a tablet."),
            ], "Most parishes begin First Communion preparation around age 7 (second grade). Ask your parish a year ahead."),
            ("sacrament", "Preparing for a sacrament", "What to do, and how far ahead to call the parish.", [
                ("marriage", "Getting married", "Call the parish at least six months to a year before the date you hope for."),
                ("baptism", "Baptizing a baby", "Call during pregnancy or soon after the birth; most parishes have a short class."),
                ("first-communion", "First Communion or Confirmation", "Usually a one- or two-year program. Register in late summer."),
                ("confession", "Going to Confession", "No appointment needed during the parish's Confession times."),
                ("anointing", "Someone is seriously ill", "Call the parish right away, day or night, for Anointing of the Sick."),
                ("funerals", "Planning a funeral", "Call the parish or funeral home first; they will help with the rest."),
            ], "When someone is near death, call a priest at once. For everything else, call the parish office during the week."),
        ]),
    "es": dict(
        h="¿En qué parte del camino estás?", lede="Elige la opción que mejor te describa. Cada camino tiene unos pocos pasos sencillos, en orden.",
        when="Cuándo", step="Paso",
        paths=[
            ("curious", "Me interesa hacerme católico", "Sin presión y sin inscribirte. Este es el orden habitual.", [
                ("first-mass", "Ve a una Misa de domingo y observa", "Todos son bienvenidos. Siéntate atrás; nuestra guía te dice lo que sucede."),
                ("questions", "Trae tus preguntas", "Respuestas breves y sinceras sobre María, la confesión, el Papa y más."),
                ("start-here", "Conoce cómo funciona OCIA", "El camino de la Iglesia para adultos: sus cuatro etapas, cuánto dura y lo que cuesta (nada)."),
                ("find-a-church", "Llama a una parroquia y pregunta por OCIA", "Busca la parroquia más cercana y pide hablar con quien coordina OCIA o RICA."),
            ], "Los grupos de OCIA suelen empezar a fines del verano o en otoño, pero puedes llamar en cualquier momento del año."),
            ("returning", "Quiero volver a la Iglesia", "Volver a casa es más sencillo de lo que crees.", [
                ("coming-back", "Lee cómo se vuelve", "La mayoría no necesita trámites ni clases. Simplemente ven."),
                ("examination-of-conscience", "Prepárate para la confesión", "Un examen de conciencia sencillo para ayudarte a recordar qué decir."),
                ("confession", "Confiésate", "Paso a paso, incluso qué decir si han pasado años. Las parroquias publican sus horarios."),
                ("join-a-parish", "Inscríbete en una parroquia", "Así la parroquia puede ayudarte con los sacramentos, de bodas a funerales."),
            ], "En cualquier momento. Muchas parroquias añaden horarios de confesión en Adviento y Cuaresma."),
            ("prayer", "Quiero crecer en la oración diaria", "Crea un ritmo diario sencillo, un hábito a la vez.", [
                ("bible", "Empieza el día con las lecturas de la Misa", "Las lecturas de hoy, con audio, de los obispos de EE. UU."),
                ("rosary", "Reza el Rosario", "Empieza con un misterio; la guía muestra los misterios de hoy."),
                ("reading-plans", "Elige un plan de lectura", "La Biblia en un año, el Catecismo en un año o los Evangelios en 30 días."),
                ("devotions", "Añade devociones con recordatorios", "El Ángelus al mediodía, la Coronilla de la Divina Misericordia a las 3 p. m. y novenas."),
                ("examination-of-conscience", "Termina el día con un examen", "Unos minutos en silencio para repasar el día con Dios."),
            ], "Las lecturas por la mañana, el Ángelus al mediodía, la Divina Misericordia a las 3 p. m. y el examen antes de dormir."),
            ("family", "Quiero educar a mis hijos en la fe", "Los pequeños hábitos alegres en casa son los que más cuentan.", [
                ("first-prayers", "Enseña las primeras oraciones", "Letra grande y lectura en voz alta, de la señal de la cruz a las oraciones de la noche."),
                ("mass-for-kids", "Prepárense juntos para la Misa", "Una guía con dibujos de lo que sucede, y un juego de «veo, veo» para la iglesia."),
                ("saint-stories", "Lee una historia de santos antes de dormir", "Historias breves y verdaderas, cada una con algo para hacer."),
                ("family-corner", "Vive los tiempos litúrgicos en casa", "Ideas sencillas para Adviento, Navidad, Cuaresma y Pascua, y hojas para preparar los sacramentos."),
                ("coloring-pages", "Colorea en un día de lluvia", "Santos, historias de la Biblia y tiempos litúrgicos para imprimir o colorear en la tableta."),
            ], "La mayoría de las parroquias empiezan la preparación para la Primera Comunión hacia los 7 años. Pregunta con un año de anticipación."),
            ("sacrament", "Me preparo para un sacramento", "Qué hacer y con cuánta anticipación llamar a la parroquia.", [
                ("marriage", "Casarse", "Llama a la parroquia al menos de seis meses a un año antes de la fecha que deseas."),
                ("baptism", "Bautizar a un bebé", "Llama durante el embarazo o poco después del nacimiento; casi todas tienen una charla breve."),
                ("first-communion", "Primera Comunión o Confirmación", "Suele ser un programa de uno o dos años. La inscripción es a fines del verano."),
                ("confession", "Confesarse", "No hace falta cita durante los horarios de confesión de la parroquia."),
                ("anointing", "Alguien está gravemente enfermo", "Llama a la parroquia enseguida, de día o de noche, para la Unción de los enfermos."),
                ("funerals", "Preparar un funeral", "Llama primero a la parroquia o a la funeraria; ellos te ayudan con lo demás."),
            ], "Si alguien está por morir, llama a un sacerdote de inmediato. Para todo lo demás, llama a la oficina parroquial entre semana."),
        ]),
    "pt": dict(
        h="Em que parte do caminho você está?", lede="Escolha a opção que mais combina com você. Cada caminho tem poucos passos simples, em ordem.",
        when="Quando", step="Passo",
        paths=[
            ("curious", "Quero conhecer a fé católica", "Sem pressão e sem inscrição. Esta é a ordem de costume.", [
                ("first-mass", "Vá a uma Missa de domingo e apenas observe", "Todos são bem-vindos. Sente-se mais atrás; nosso guia explica o que acontece."),
                ("questions", "Traga as suas perguntas", "Respostas curtas e sinceras sobre Maria, a confissão, o Papa e mais."),
                ("start-here", "Entenda como funciona a OCIA", "O caminho da Igreja para adultos: as quatro etapas, quanto tempo leva e quanto custa (nada)."),
                ("find-a-church", "Ligue para uma paróquia e pergunte pela OCIA", "Encontre a paróquia mais próxima e peça para falar com quem coordena a OCIA."),
            ], "Os grupos da OCIA costumam começar no fim do verão ou no outono, mas você pode ligar em qualquer época do ano."),
            ("returning", "Quero voltar para a Igreja", "Voltar para casa é mais simples do que parece.", [
                ("coming-back", "Leia como é voltar", "A maioria das pessoas não precisa de papelada nem de aulas. Basta vir."),
                ("examination-of-conscience", "Prepare-se para a confissão", "Um exame de consciência simples para ajudar você a lembrar o que dizer."),
                ("confession", "Confesse-se", "Passo a passo, inclusive o que dizer depois de muitos anos. As paróquias divulgam os horários."),
                ("join-a-parish", "Inscreva-se numa paróquia", "Assim a paróquia pode ajudar com os sacramentos, do casamento ao funeral."),
            ], "A qualquer momento. Muitas paróquias abrem horários extras de confissão no Advento e na Quaresma."),
            ("prayer", "Quero crescer na oração diária", "Crie um ritmo diário simples, um hábito de cada vez.", [
                ("bible", "Comece o dia com as leituras da Missa", "As leituras de hoje, todos os dias."),
                ("rosary", "Reze o Rosário", "Comece com uma dezena; o guia mostra os mistérios de hoje."),
                ("reading-plans", "Escolha um plano de leitura", "A Bíblia em um ano, o Catecismo em um ano ou os Evangelhos em 30 dias."),
                ("devotions", "Acrescente devoções com lembretes", "O Angelus ao meio-dia, o Terço da Misericórdia às 15h e novenas."),
                ("examination-of-conscience", "Termine o dia com um exame", "Alguns minutos em silêncio para rever o dia com Deus."),
            ], "As leituras de manhã, o Angelus ao meio-dia, a Misericórdia às 15h e o exame antes de dormir."),
            ("family", "Quero criar meus filhos na fé", "Pequenos hábitos alegres em casa fazem a maior diferença.", [
                ("first-prayers", "Ensine as primeiras orações", "Letra grande e leitura em voz alta, do sinal da cruz às orações da noite."),
                ("mass-for-kids", "Preparem-se juntos para a Missa", "Um guia ilustrado do que acontece, e um jogo de «eu vejo» para a igreja."),
                ("saint-stories", "Leia uma história de santo antes de dormir", "Histórias curtas e verdadeiras, cada uma com algo para fazer."),
                ("family-corner", "Viva os tempos litúrgicos em casa", "Ideias simples para o Advento, o Natal, a Quaresma e a Páscoa, e folhas de preparação para os sacramentos."),
                ("coloring-pages", "Pinte num dia de chuva", "Santos, histórias da Bíblia e tempos litúrgicos para imprimir ou pintar no tablet."),
            ], "A maioria das paróquias começa a preparação para a Primeira Comunhão por volta dos 7 anos. Pergunte com um ano de antecedência."),
            ("sacrament", "Estou me preparando para um sacramento", "O que fazer e com quanta antecedência ligar para a paróquia.", [
                ("marriage", "Casar-se", "Ligue para a paróquia pelo menos de seis meses a um ano antes da data desejada."),
                ("baptism", "Batizar um bebê", "Ligue durante a gravidez ou logo após o nascimento; quase todas têm um curso rápido."),
                ("first-communion", "Primeira Comunhão ou Crisma", "Costuma ser um programa de um ou dois anos. As inscrições são no fim do verão."),
                ("confession", "Confessar-se", "Não precisa marcar nos horários de confissão da paróquia."),
                ("anointing", "Alguém está gravemente doente", "Ligue para a paróquia na hora, de dia ou de noite, para a Unção dos Enfermos."),
                ("funerals", "Preparar um funeral", "Ligue primeiro para a paróquia ou para a funerária; eles ajudam com o resto."),
            ], "Se alguém está para morrer, chame um padre na hora. Para todo o resto, ligue para a secretaria paroquial durante a semana."),
        ]),
    "tl": dict(
        h="Nasaan ka na sa paglalakbay?", lede="Piliin ang pinakaangkop sa iyo. Bawat landas ay may ilang simpleng hakbang, nang sunud-sunod.",
        when="Kailan", step="Hakbang",
        paths=[
            ("curious", "Interesado akong maging Katoliko", "Walang pilitan at walang pagpapatala. Ito ang karaniwang pagkakasunod.", [
                ("first-mass", "Magsimba sa Linggo at manood lang", "Malugod na tinatanggap ang lahat. Umupo sa likod; sinasabi ng aming gabay ang nangyayari."),
                ("questions", "Dalhin ang iyong mga tanong", "Maiikli at tapat na sagot tungkol kay Maria, sa kumpisal, sa Papa at iba pa."),
                ("start-here", "Alamin kung paano gumagana ang OCIA", "Ang landas ng Simbahan para sa matatanda: ang apat na yugto, gaano katagal, at magkano (libre)."),
                ("find-a-church", "Tumawag sa parokya at magtanong tungkol sa OCIA", "Hanapin ang pinakamalapit na parokya at hanapin ang tagapag-ugnay ng OCIA."),
            ], "Karaniwang nagsisimula ang OCIA sa huling bahagi ng tag-init o sa taglagas, pero maaari kang tumawag anumang oras."),
            ("returning", "Gusto kong bumalik sa Simbahan", "Mas simple ang pagbabalik kaysa inaakala mo.", [
                ("coming-back", "Basahin kung paano bumalik", "Karamihan ay hindi na kailangan ng papeles o klase. Pumunta ka lang."),
                ("examination-of-conscience", "Maghanda para sa Kumpisal", "Isang mahinahong pagsusuri ng budhi para matandaan mo ang sasabihin."),
                ("confession", "Mangumpisal", "Hakbang-hakbang, pati ang sasabihin kung matagal ka nang hindi nangungumpisal."),
                ("join-a-parish", "Magpatala sa parokya", "Para matulungan ka ng parokya sa mga sakramento, mula kasal hanggang libing."),
            ], "Anumang oras. Maraming parokya ang nagdaragdag ng oras ng kumpisal tuwing Adbiyento at Kuwaresma."),
            ("prayer", "Gusto kong lumago sa araw-araw na panalangin", "Bumuo ng simpleng araw-araw na gawi, isa-isa.", [
                ("bible", "Simulan ang araw sa mga pagbasa ng Misa", "Ang mga pagbasa ngayon, araw-araw."),
                ("rosary", "Magrosaryo", "Magsimula sa isang misteryo; ipinapakita ng gabay ang mga misteryo ngayon."),
                ("reading-plans", "Pumili ng plano sa pagbasa", "Ang Bibliya sa isang taon, ang Katesismo sa isang taon, o ang mga Ebanghelyo sa 30 araw."),
                ("devotions", "Magdagdag ng debosyon na may paalala", "Ang Orasyon sa tanghali, ang Koronilya ng Banal na Awa sa ika-3 ng hapon, at mga nobena."),
                ("examination-of-conscience", "Tapusin ang araw sa pagsusuri ng budhi", "Ilang tahimik na minuto para balikan ang araw kasama ang Diyos."),
            ], "Mga pagbasa sa umaga, Orasyon sa tanghali, Banal na Awa sa ika-3 ng hapon, at pagsusuri ng budhi bago matulog."),
            ("family", "Pinalalaki ko ang mga anak sa pananampalataya", "Ang maliliit at masasayang gawi sa bahay ang pinakamahalaga.", [
                ("first-prayers", "Ituro ang mga unang dasal", "Malalaking titik at binabasa nang malakas, mula sa Tanda ng Krus hanggang dasal bago matulog."),
                ("mass-for-kids", "Sabay na maghanda para sa Misa", "Gabay na may larawan kung ano ang nangyayari, at larong I-spy sa simbahan."),
                ("saint-stories", "Magbasa ng kuwento ng santo bago matulog", "Maiikli at totoong kuwento, bawat isa ay may maaaring gawin."),
                ("family-corner", "Ipagdiwang ang mga panahon sa bahay", "Mga simpleng ideya para sa Adbiyento, Pasko, Kuwaresma at Pasko ng Pagkabuhay."),
                ("coloring-pages", "Magkulay kapag tag-ulan", "Mga santo, kuwento sa Bibliya at mga panahon na maaaring i-print o kulayan sa tablet."),
            ], "Karamihan ng parokya ay nagsisimula ng paghahanda sa Unang Komunyon sa edad na 7. Magtanong sa parokya isang taon bago."),
            ("sacrament", "Naghahanda ako para sa isang sakramento", "Ano ang gagawin, at gaano kaaga tatawag sa parokya.", [
                ("marriage", "Magpapakasal", "Tumawag sa parokya anim na buwan hanggang isang taon bago ang petsang nais mo."),
                ("baptism", "Magpapabinyag ng sanggol", "Tumawag habang nagbubuntis o pagkapanganak; karamihan ay may maikling seminar."),
                ("first-communion", "Unang Komunyon o Kumpil", "Karaniwang isa o dalawang taon ang programa. Magpatala sa huling bahagi ng tag-init."),
                ("confession", "Mangungumpisal", "Hindi kailangan ng appointment sa oras ng kumpisal ng parokya."),
                ("anointing", "May malubhang maysakit", "Tumawag agad sa parokya, araw man o gabi, para sa Pagpapahid ng Langis sa Maysakit."),
                ("funerals", "Naghahanda ng libing", "Tumawag muna sa parokya o sa punerarya; tutulungan ka nila sa iba pa."),
            ], "Kapag may naghihingalo, tumawag agad ng pari. Para sa iba pa, tumawag sa tanggapan ng parokya sa karaniwang araw."),
        ]),
}


def paths_html(lang, url):
    t = PATHS[lang]
    tabs, panels = [], []
    for i, (pid, title, intro, steps, when) in enumerate(t["paths"]):
        sel = i == 0
        tabs.append(f'<button type="button" role="tab" id="pt-{pid}" aria-controls="pp-{pid}" aria-selected="{"true" if sel else "false"}"'
                    f'{"" if sel else " tabindex=\"-1\""}>{e(title)}</button>')
        lis = "".join(f'<li><a href="{url(k)}"><strong>{e(st)}</strong><span>{e(sd)}</span></a></li>' for k, st, sd in steps if url(k))
        panels.append(f'<div class="path-panel" role="tabpanel" id="pp-{pid}" aria-labelledby="pt-{pid}">'
                      f'<h3>{e(title)}</h3><p class="path-intro">{e(intro)}</p><ol class="path-steps">{lis}</ol>'
                      f'<p class="path-when"><strong>{e(t["when"])}:</strong> {e(when)}</p></div>')
    return (f'<section class="section journey" aria-labelledby="journey-h" data-paths>'
            f'<h2 id="journey-h">{e(t["h"])}</h2><p class="muted">{e(t["lede"])}</p>'
            f'<div class="path-tabs" role="tablist" aria-labelledby="journey-h" hidden>{"".join(tabs)}</div>'
            f'<div class="path-panels">{"".join(panels)}</div></section>')


def render(body, lang, url):
    if "{{PATHS}}" in body:
        body = body.replace("{{PATHS}}", paths_html(lang, url))
    return body
