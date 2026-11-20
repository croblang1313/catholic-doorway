"""Watch Mass Online page, in four languages.

The page body is just {{WATCH}}; render() replaces it with:
  1. the big daily Mass broadcasts, with their schedules (site/assets/js/watch.js shows the
     times in the visitor's own time zone),
  2. parish livestreams that parishes send in through the listing form (reviewed first),
  3. help for the sick and homebound: the Sunday obligation, Communion at home and a
     Spiritual Communion prayer.

Schedules were checked on the broadcasters' own sites on 2026-11-20 (see CHECKED).
"""
import html
import json

e = html.escape
CHECKED = "2026-11-20"

# Days are 0 = Sunday ... 6 = Saturday, in the broadcaster's own time zone.
EVERY = [0, 1, 2, 3, 4, 5, 6]
MON_FRI = [1, 2, 3, 4, 5]
MON_SAT = [1, 2, 3, 4, 5, 6]

DAYS = {
    "en": {"every": "Every day", "mon_fri": "Monday to Friday", "mon_sat": "Monday to Saturday", "sat": "Saturday", "sun": "Sunday", "weekdays": "Weekdays"},
    "es": {"every": "Todos los días", "mon_fri": "De lunes a viernes", "mon_sat": "De lunes a sábado", "sat": "Sábado", "sun": "Domingo", "weekdays": "Entre semana"},
    "pt": {"every": "Todos os dias", "mon_fri": "De segunda a sexta", "mon_sat": "De segunda a sábado", "sat": "Sábado", "sun": "Domingo", "weekdays": "Dias de semana"},
    "tl": {"every": "Araw-araw", "mon_fri": "Lunes hanggang Biyernes", "mon_sat": "Lunes hanggang Sabado", "sat": "Sabado", "sun": "Linggo", "weekdays": "Karaniwang araw"},
}
ZONE = {
    "America/New_York": {"en": "Eastern Time", "es": "hora del Este", "pt": "horário do Leste dos EUA", "tl": "oras sa Eastern (EST/EDT)"},
    "America/Mexico_City": {"en": "Mexico City time", "es": "hora de la Ciudad de México", "pt": "horário da Cidade do México", "tl": "oras sa Mexico City"},
    "America/Sao_Paulo": {"en": "Brasília time", "es": "hora de Brasilia", "pt": "horário de Brasília", "tl": "oras sa Brasília"},
    "Europe/Rome": {"en": "Rome time", "es": "hora de Roma", "pt": "horário de Roma", "tl": "oras sa Roma"},
    "Asia/Manila": {"en": "Philippine time", "es": "hora de Filipinas", "pt": "horário das Filipinas", "tl": "oras sa Pilipinas"},
}
LANG_NAME = {
    "en": {"en": "English", "es": "Spanish", "pt": "Portuguese", "tl": "Filipino"},
    "es": {"en": "Inglés", "es": "Español", "pt": "Portugués", "tl": "Filipino"},
    "pt": {"en": "Inglês", "es": "Espanhol", "pt": "Português", "tl": "Filipino"},
    "tl": {"en": "Ingles", "es": "Espanyol", "pt": "Portuges", "tl": "Filipino"},
}

# sched: list of (day-key, days, times "HH:MM" in tz)
STREAMS = [
    dict(id="ewtn", name="EWTN Daily Mass", langs=["en"], tz="America/New_York",
         sched=[("every", EVERY, ["08:00", "12:00", "19:00", "00:00"])],
         where={"en": "Our Lady of the Angels Chapel, Irondale, Alabama", "es": "Capilla de Nuestra Señora de los Ángeles, Irondale (Alabama)",
                "pt": "Capela de Nossa Senhora dos Anjos, Irondale (Alabama)", "tl": "Kapilya ng Our Lady of the Angels, Irondale, Alabama"},
         desc={"en": "The best-known daily TV Mass in the U.S., celebrated by the friars of EWTN. The 8 a.m. Eastern airing comes first; the later times are rebroadcasts, and past Masses are free on demand.",
               "es": "La Misa diaria por televisión más conocida de EE. UU., en inglés, celebrada por los frailes de EWTN. La transmisión de las 8 a. m. (hora del Este) es la primera; las demás son retransmisiones.",
               "pt": "A Missa diária na TV mais conhecida dos EUA, em inglês, celebrada pelos frades da EWTN. A transmissão das 8h (horário do Leste) é a primeira; as outras são reprises.",
               "tl": "Ang pinakakilalang Misa araw-araw sa TV sa Estados Unidos, sa Ingles, na idinaraos ng mga prayle ng EWTN. Ang alas-8 ng umaga (Eastern) ang una; mga replay na ang mga susunod."},
         live="https://www.ewtn.com/live", past="https://ondemand.ewtn.com/free/Home/Series/ondemand/video/en/daily-catholic-mass",
         src="https://www.ewtn.com/tv/schedule/united-states"),
    dict(id="catholictv", name="CatholicTV Mass", langs=["en"], tz="America/New_York",
         sched=[("mon_fri", MON_FRI, ["09:30", "12:30", "19:00", "23:30"]), ("sat", [6], ["09:30", "12:30"]), ("sun", [0], ["12:30", "19:00"])],
         where={"en": "Chapel of the Holy Cross, CatholicTV", "es": "Capilla de la Santa Cruz, CatholicTV", "pt": "Capela da Santa Cruz, CatholicTV", "tl": "Kapilya ng Banal na Krus, CatholicTV"},
         desc={"en": "A daily Mass from the CatholicTV Network's chapel, with replays of each day's Mass on its website.",
               "es": "Misa diaria en inglés desde la capilla de CatholicTV, con la Misa de cada día disponible después en su sitio web.",
               "pt": "Missa diária em inglês na capela da CatholicTV, com a Missa de cada dia disponível depois no site.",
               "tl": "Misa araw-araw sa Ingles mula sa kapilya ng CatholicTV, at mapapanood muli ang Misa ng bawat araw sa kanilang website."},
         live="https://www.catholictv.org/", past="https://www.catholictv.org/catholictv-mass",
         src="https://www.catholictv.org/faqs"),
    dict(id="shrine", name="Basilica of the National Shrine of the Immaculate Conception", langs=["en", "es"], tz="America/New_York",
         sched=[("sun", [0], ["12:00", "14:30"])],
         where={"en": "Washington, D.C.", "es": "Washington, D. C.", "pt": "Washington, D.C.", "tl": "Washington, D.C."},
         desc={"en": "“America’s Catholic Church” livestreams its Sunday noon Mass, and its 2:30 p.m. Mass in Spanish, with a printable program.",
               "es": "La “Iglesia católica de Estados Unidos” transmite su Misa dominical del mediodía (en inglés) y su Misa en español de las 2:30 p. m., con folleto para descargar.",
               "pt": "A “Igreja Católica dos Estados Unidos” transmite a Missa dominical do meio-dia (em inglês) e a Missa em espanhol das 14h30.",
               "tl": "Ipinapalabas nang live ng “Simbahang Katoliko ng Amerika” ang Misa tuwing Linggo ng tanghali (Ingles) at ang Misa sa Espanyol nang alas-2:30 ng hapon."},
         notes={"en": "Noon in English, 2:30 p.m. in Spanish", "es": "Mediodía en inglés, 2:30 p. m. en español", "pt": "Meio-dia em inglês, 14h30 em espanhol", "tl": "Tanghali sa Ingles, 2:30 ng hapon sa Espanyol"},
         live="https://www.nationalshrine.org/mass/", past="https://www.nationalshrine.org/mass/",
         src="https://www.nationalshrine.org/mass/"),
    dict(id="ewtn-es", name="EWTN Español: Santa Misa", langs=["es"], tz="America/New_York",
         sched=[("mon_sat", MON_SAT, ["08:00", "16:00"]), ("sun", [0], ["14:30"])],
         where={"en": "EWTN’s Spanish-language channel for the U.S.", "es": "Canal de EWTN en español para Estados Unidos", "pt": "Canal da EWTN em espanhol para os EUA", "tl": "Spanish na channel ng EWTN para sa Estados Unidos"},
         desc={"en": "Daily Mass in Spanish on EWTN’s U.S. Spanish channel, with Sunday Mass in the afternoon.",
               "es": "Misa diaria en español en el canal de EWTN para Estados Unidos, y la Misa dominical por la tarde.",
               "pt": "Missa diária em espanhol no canal da EWTN para os EUA, e a Missa dominical à tarde.",
               "tl": "Misa araw-araw sa Espanyol sa channel ng EWTN para sa Estados Unidos, at Misa tuwing Linggo ng hapon."},
         live="https://www.ewtn.com/live/tv/estados-unidos", past="",
         src="https://www.ewtn.com/tv/schedule/estados-unidos"),
    dict(id="guadalupe", name="Basílica de Santa María de Guadalupe", langs=["es"], tz="America/Mexico_City",
         sched=[("every", EVERY, ["06:00", "07:00", "09:00", "10:00", "11:00", "12:00", "15:00", "16:00", "19:00", "20:00"])],
         where={"en": "Mexico City", "es": "Ciudad de México", "pt": "Cidade do México", "tl": "Mexico City"},
         desc={"en": "Masses in Spanish before the tilma of Our Lady of Guadalupe, through the day. Not every Mass is streamed: the Basilica’s YouTube channel shows what is live.",
               "es": "Misas ante la tilma de la Virgen de Guadalupe durante todo el día. No todas se transmiten: el canal de YouTube de la Basílica muestra la que está en vivo.",
               "pt": "Missas em espanhol diante da tilma de Nossa Senhora de Guadalupe ao longo do dia. Nem todas são transmitidas: o canal da Basílica no YouTube mostra o que está ao vivo.",
               "tl": "Mga Misa sa Espanyol sa harap ng tilma ng Mahal na Birhen ng Guadalupe buong araw. Hindi lahat ay napapanood online: makikita sa YouTube channel ng Basilica kung ano ang live."},
         notes={"en": "Mass times at the main altar; not all are streamed", "es": "Horario del altar mayor; no todas se transmiten", "pt": "Horários do altar-mor; nem todas são transmitidas", "tl": "Oras sa pangunahing altar; hindi lahat ay live"},
         live="https://www.youtube.com/user/BasilicadeGuadalupe", past="",
         src="https://virgendeguadalupe.org.mx/horarios/"),
    dict(id="aparecida", name="TV Aparecida: Missa do Santuário Nacional", langs=["pt"], tz="America/Sao_Paulo",
         sched=[("weekdays", MON_FRI, ["06:45", "08:50", "12:00", "18:00"])],
         where={"en": "National Shrine of Our Lady of Aparecida, Brazil", "es": "Santuario Nacional de Aparecida, Brasil", "pt": "Santuário Nacional de Aparecida (SP)", "tl": "Pambansang Dambana ng Aparecida, Brazil"},
         desc={"en": "Daily Masses in Portuguese from the world’s largest Marian shrine. Weekend times differ; see TV Aparecida’s schedule.",
               "es": "Misas diarias en portugués desde el santuario mariano más grande del mundo. Los fines de semana el horario cambia.",
               "pt": "Missas diárias do maior santuário mariano do mundo. Nos fins de semana os horários mudam; veja a programação da TV Aparecida.",
               "tl": "Mga Misa araw-araw sa Portuges mula sa pinakamalaking dambana ni Maria sa mundo. Iba ang oras tuwing Sabado at Linggo."},
         live="https://www.a12.com/tv/tv-ao-vivo", past="https://www.a12.com/tv/programas/missa-aparecida-santuario-nacional",
         src="https://www.a12.com/tv/programacao"),
    dict(id="cancaonova", name="TV Canção Nova: Santa Missa", langs=["pt"], tz="America/Sao_Paulo",
         sched=[("weekdays", MON_FRI, ["07:00", "12:00"])],
         where={"en": "Cachoeira Paulista, Brazil", "es": "Cachoeira Paulista, Brasil", "pt": "Cachoeira Paulista (SP)", "tl": "Cachoeira Paulista, Brazil"},
         desc={"en": "Daily Mass in Portuguese from the Canção Nova community, live on its website.",
               "es": "Misa diaria en portugués desde la comunidad Canção Nova, en vivo en su sitio web.",
               "pt": "Santa Missa diária da Comunidade Canção Nova, ao vivo no site.",
               "tl": "Misa araw-araw sa Portuges mula sa komunidad ng Canção Nova, live sa kanilang website."},
         live="https://tv.cancaonova.com/", past="",
         src="https://tv.cancaonova.com/"),
    dict(id="tvmaria", name="TV Maria", langs=["tl"], tz="Asia/Manila", sched=[],
         where={"en": "The Catholic TV channel of the Philippines", "es": "El canal católico de Filipinas", "pt": "O canal católico das Filipinas", "tl": "Ang Katolikong TV channel ng Pilipinas"},
         desc={"en": "Owned by the Catholic Bishops’ Conference of the Philippines. It airs Masses in Filipino and English, including the Misa Nazareno from Quiapo Church.",
               "es": "Canal de la Conferencia Episcopal de Filipinas. Transmite Misas en filipino y en inglés, entre ellas la Misa Nazareno desde la iglesia de Quiapo.",
               "pt": "Canal da Conferência Episcopal das Filipinas. Transmite Missas em filipino e em inglês, entre elas a Misa Nazareno da igreja de Quiapo.",
               "tl": "Pag-aari ng Catholic Bishops’ Conference of the Philippines. Nagpapalabas ng mga Misa sa Filipino at Ingles, kasama ang Misa Nazareno mula sa Simbahan ng Quiapo."},
         notes={"en": "Times change; see TV Maria’s schedule", "es": "Los horarios cambian; consulta la programación", "pt": "Os horários mudam; veja a programação", "tl": "Nagbabago ang oras; tingnan ang iskedyul ng TV Maria"},
         live="https://tvmaria.ph/newgeneration/live-videos/", past="https://www.youtube.com/tvmariaphils",
         src="https://tvmaria.ph/schedule/"),
    dict(id="vatican", name="Vatican News", langs=["en", "es", "pt"], tz="Europe/Rome",
         sched=[("sun", [0], ["12:00"])],
         where={"en": "Vatican City", "es": "Ciudad del Vaticano", "pt": "Cidade do Vaticano", "tl": "Lungsod ng Vaticano"},
         desc={"en": "Papal Masses and celebrations are streamed live, with commentary in many languages; their times vary, so check the Pope’s calendar. Most Sundays the Pope also prays the Angelus at noon Rome time.",
               "es": "Las Misas y celebraciones del Papa se transmiten en vivo con comentario en español; el horario varía, así que consulta la agenda del Papa. Casi todos los domingos el Papa reza además el Ángelus al mediodía de Roma.",
               "pt": "As Missas e celebrações do Papa são transmitidas ao vivo com comentário em português; os horários variam, por isso veja a agenda do Papa. Quase todos os domingos o Papa reza também o Angelus ao meio-dia de Roma.",
               "tl": "Ipinapalabas nang live ang mga Misa at pagdiriwang ng Santo Papa, na may komentaryo sa Ingles; nag-iiba ang oras, kaya tingnan ang kalendaryo ng Papa. Halos tuwing Linggo, nagdarasal din ang Papa ng Angelus sa tanghali, oras sa Roma."},
         notes={"en": "The Sunday Angelus (not a Mass); papal Masses vary", "es": "Ángelus dominical (no es Misa); las Misas del Papa varían", "pt": "Angelus dominical (não é Missa); as Missas do Papa variam", "tl": "Angelus tuwing Linggo (hindi Misa); nag-iiba ang Misa ng Papa"},
         live={"en": "https://www.youtube.com/c/VaticanNewsEN", "es": "https://www.youtube.com/c/VaticanNewsES", "pt": "https://www.youtube.com/c/VaticanNewsPT", "tl": "https://www.youtube.com/c/VaticanNewsEN"},
         past={"en": "https://www.vatican.va/content/leo-xiv/en/events.html", "es": "https://www.vatican.va/content/leo-xiv/es/events.html",
               "pt": "https://www.vatican.va/content/leo-xiv/pt/events.html", "tl": "https://www.vatican.va/content/leo-xiv/en/events.html"},
         src="https://www.vaticannews.va/"),
]

T = {
    "en": dict(
        kicker='<a href="/prayers">Prayers</a> &rsaquo; Watch Mass',
        h1="Watch Mass Online",
        lede="Can’t get to church? Pray the Mass with a live broadcast, find a parish near you that streams its Masses, and learn how to receive Communion at home if you are sick or homebound. Everything here is free, with no sign-up.",
        toc=[("broadcasts", "Daily Mass broadcasts"), ("parish-streams", "Parish livestreams"), ("homebound", "Sick or homebound?"),
             ("spiritual-communion", "Spiritual Communion prayer"), ("at-home", "Praying the Mass at home"), ("add-stream", "Parishes: add your livestream")],
        b_h="Daily Mass broadcasts",
        b_p="These come straight from the broadcasters’ own websites and channels. Times are shown in your time zone",
        b_p2="Feasts, holidays and papal events can change the schedule, so the broadcaster’s own page is the final word.",
        all_langs="All languages", your="your time", at_source="At the source", next_="Next", on_now="On now", see_sched="See the schedule",
        watch="Watch live", past="Past Masses", vat_past="The Pope’s calendar", sched_link="Broadcaster’s schedule", checked=f"Schedule checked {CHECKED}",
        p_h="Parish livestreams",
        p_p="Many parishes stream their own Masses on YouTube, Facebook or their website. Parishes send us their link, we check it with the parish, and you can see when each link was last checked. If one stops working, tap <em>Report broken link</em> and we’ll look at it.",
        p_map='Prefer a parish near you? On <a href="/find-a-church?stream=1">Find a Church</a>, tick <strong>Streams Mass</strong> to see only churches that have added a livestream.',
        state="State", all_states="All states", loading="Loading…",
        h_h="Sick or homebound?",
        obl_h="Does watching count for Sunday Mass?",
        obl=["Watching Mass on TV or online is a good way to pray, but it does not take the place of going to Mass. Catholics are asked to take part in Mass in person on Sundays and holy days of obligation.",
             "You are <strong>excused</strong> when you have a serious reason you can’t go: if you are sick, homebound, recovering, frail with age, caring for someone who needs you, or when travel or weather makes it truly unsafe (Catechism 2181). There is no sin in missing Mass for a reason like that, and you don’t need anyone’s permission. Your pastor can also excuse you in other cases, so ask if you aren’t sure.",
             "On those days, watching a Mass and making a Spiritual Communion is a beautiful way to keep the Lord’s Day."],
        obl_link='See this year’s <a href="/calendar">holy days of obligation</a>.',
        com_h="Communion at home",
        com=["Every parish can bring Holy Communion to people who can’t come to church. A priest, deacon or trained lay minister visits, often every week, and you don’t need to be registered at the parish to ask.",
             "If you are sick, you can also ask for a priest to hear your Confession and give the Anointing of the Sick at home or in the hospital."],
        com_say_h="Call the parish office and say something like:",
        com_say="“Hi, my name is ____. I’m (my mother is) homebound at ____ and would like to receive Communion at home. Could someone from the parish come? I’d also like to see a priest for Confession.”",
        com_tips=["In a hospital or nursing home, ask the front desk for the Catholic chaplain.",
                  "The one-hour fast before Communion doesn’t bind the elderly, the sick or those caring for them (Canon 919).",
                  "Prepare a small table with a clean cloth, a crucifix and a candle if you have them."],
        com_links='<a class="btn small" href="/find-a-church">Find your parish</a> <a class="btn small secondary" href="/anointing">Anointing of the Sick</a>',
        sc_h="Spiritual Communion prayer",
        sc_p="When you can’t receive the Eucharist, you can still ask Jesus to come into your heart. Many people pray this at Communion time while watching Mass. It is adapted from St. Alphonsus Liguori.",
        sc_text="My Jesus, I believe that you are present in the Most Holy Sacrament.\nI love you above all things, and I desire to receive you into my soul.\nSince I cannot at this moment receive you sacramentally,\ncome at least spiritually into my heart.\nI embrace you as if you were already there,\nand I unite myself wholly to you.\nNever permit me to be separated from you. Amen.",
        ah_h="Praying the Mass at home",
        ah=[("Watch it live if you can", "A live Mass draws you into the same prayer as the people in church. Replays are good too, especially for people who work or sleep at odd hours."),
            ("Make a little space", "Turn off other screens, light a candle, put a crucifix or holy picture near the TV, and dress as you would for church if you’re able."),
            ("Pray along", 'Say the responses, sing, and stand, sit and kneel if you can. Our <a href="/first-mass">Mass companion</a> has every response, and the <a href="/bible">day’s readings</a> are here.'),
            ("At Communion, pray", 'Pause, bow your head and pray the <a href="#spiritual-communion">Spiritual Communion prayer</a>. Stay quiet for a moment of thanksgiving.'),
            ("Stay connected", "Call your parish: priests and ministers want to know who can’t come, and many parishes deliver the bulletin or connect you with a visitor.")],
        f_h="Parishes: add your livestream",
        f_p="If your parish streams its Masses, add the link here. It is free. We check it with the parish before it appears, and your email stays private (we only use it to confirm the listing). Parishes can also add their OCIA contact and Mass times on the <a href=\"/ocia-listing#form\">parish listing form</a>.",
        f_parish="Parish name", f_city="City", f_state="State", f_stream="Livestream link", f_stream_ph="https://www.youtube.com/@yourparish/streams",
        f_when="When you stream", f_when_ph="e.g. Sun 10:30 a.m. (English), 12:30 p.m. (Spanish); weekdays 8 a.m.",
        f_name="Your name", f_email="Your email (not published)", f_consent="I serve at this parish, and the parish agrees to have this link shown publicly on CatholicDoorway.com.",
        f_legal='How we handle what you send: <a href="/privacy#you-send">Privacy Policy</a> and <a href="/terms#listings">Terms of Use</a>.',
        f_send="Send for review",
        note="CatholicDoorway lists broadcasters’ official pages and links that parishes send us. We don’t host or copy any video. A link here doesn’t mean we endorse everything on that channel.",
    ),
    "es": dict(
        kicker='<a href="/es/oraciones">Oraciones</a> &rsaquo; Misa en línea',
        h1="Ver la Misa en línea",
        lede="¿No puedes ir a la iglesia? Reza la Misa con una transmisión en vivo, busca una parroquia cercana que transmita sus Misas y descubre cómo recibir la Comunión en casa si estás enfermo o no puedes salir. Todo es gratis y sin registrarse.",
        toc=[("broadcasts", "Misas diarias transmitidas"), ("parish-streams", "Transmisiones de parroquias"), ("homebound", "¿Enfermo o sin poder salir?"),
             ("spiritual-communion", "Oración de comunión espiritual"), ("at-home", "Vivir la Misa en casa"), ("add-stream", "Parroquias: añadan su transmisión")],
        b_h="Misas diarias transmitidas",
        b_p="Los enlaces vienen directamente de los sitios y canales oficiales de cada emisora. Los horarios se muestran en tu zona horaria",
        b_p2="Las fiestas, los feriados y los eventos del Papa pueden cambiar el horario; la página de cada emisora tiene la última palabra.",
        all_langs="Todos los idiomas", your="tu hora", at_source="Hora local", next_="Próxima", on_now="Ahora en vivo", see_sched="Ver la programación",
        watch="Ver en vivo", past="Misas anteriores", vat_past="La agenda del Papa", sched_link="Programación de la emisora", checked=f"Horario revisado el {CHECKED}",
        p_h="Transmisiones de parroquias",
        p_p="Muchas parroquias transmiten sus Misas por YouTube, Facebook o su sitio web. Las parroquias nos mandan su enlace, lo confirmamos con ellas y puedes ver cuándo se revisó cada enlace por última vez. Si alguno deja de funcionar, toca <em>Avisar de un enlace roto</em> y lo revisaremos.",
        p_map='¿Prefieres una parroquia cercana? En <a href="/es/buscar-iglesia?stream=1">Buscar una iglesia</a>, marca <strong>Transmite la Misa</strong> para ver solo las iglesias que añadieron una transmisión.',
        state="Estado", all_states="Todos los estados", loading="Cargando…",
        h_h="¿Enfermo o sin poder salir?",
        obl_h="¿Ver la Misa cuenta para el domingo?",
        obl=["Ver la Misa por televisión o internet es una buena manera de rezar, pero no sustituye ir a Misa. Los católicos están llamados a participar en persona en la Misa los domingos y los días de precepto.",
             "Estás <strong>dispensado</strong> cuando tienes un motivo serio para no ir: si estás enfermo, no puedes salir de casa, te estás recuperando, la edad te lo impide, cuidas a alguien que te necesita, o cuando el viaje o el clima lo hacen realmente peligroso (Catecismo 2181). No hay pecado en faltar a Misa por una razón así y no necesitas permiso de nadie. Tu párroco también puede dispensarte en otros casos; pregúntale si tienes dudas.",
             "En esos días, ver una Misa y hacer una comunión espiritual es una hermosa manera de santificar el día del Señor."],
        obl_link='Consulta los <a href="/es/calendario">días de precepto</a> de este año.',
        com_h="La Comunión en casa",
        com=["Toda parroquia puede llevar la Sagrada Comunión a quienes no pueden ir a la iglesia. Te visita un sacerdote, un diácono o un ministro laico preparado, muchas veces cada semana, y no necesitas estar inscrito en la parroquia para pedirlo.",
             "Si estás enfermo, también puedes pedir que un sacerdote te confiese y te dé la Unción de los enfermos en casa o en el hospital."],
        com_say_h="Llama a la oficina parroquial y di algo así:",
        com_say="“Hola, me llamo ____. Yo (mi mamá) no puedo salir de casa; vivo en ____ y quisiera recibir la Comunión en casa. ¿Podría venir alguien de la parroquia? También me gustaría ver a un sacerdote para confesarme.”",
        com_tips=["En un hospital o un asilo, pregunta en la recepción por el capellán católico.",
                  "El ayuno de una hora antes de comulgar no obliga a los ancianos, a los enfermos ni a quienes los cuidan (canon 919).",
                  "Prepara una mesita con un mantel limpio, un crucifijo y una vela si los tienes."],
        com_links='<a class="btn small" href="/es/buscar-iglesia">Busca tu parroquia</a> <a class="btn small secondary" href="/es/uncion">La Unción de los enfermos</a>',
        sc_h="Oración de comunión espiritual",
        sc_p="Cuando no puedes recibir la Eucaristía, puedes pedirle a Jesús que venga a tu corazón. Muchos la rezan en el momento de la Comunión mientras ven la Misa. Está tomada de san Alfonso María de Ligorio.",
        sc_text="Creo, Jesús mío, que estás realmente presente en el Santísimo Sacramento del Altar.\nTe amo sobre todas las cosas y deseo recibirte en mi alma.\nPero como ahora no puedo recibirte sacramentado,\nven al menos espiritualmente a mi corazón.\nComo si ya te hubiese recibido, te abrazo y me uno del todo a ti.\nNo permitas, Señor, que jamás me separe de ti. Amén.",
        ah_h="Vivir la Misa en casa",
        ah=[("Mírala en vivo si puedes", "Una Misa en vivo te une a la misma oración de quienes están en la iglesia. Las retransmisiones también sirven, sobre todo si trabajas o duermes en horarios distintos."),
            ("Prepara un rincón", "Apaga las demás pantallas, enciende una vela, pon un crucifijo o una imagen cerca del televisor y vístete como para ir a la iglesia si puedes."),
            ("Participa", 'Responde, canta y ponte de pie, siéntate o arrodíllate si puedes. Nuestra <a href="/es/primera-misa">guía de la Misa</a> tiene todas las respuestas, y aquí están las <a href="/es/biblia">lecturas del día</a>.'),
            ("En la Comunión, reza", 'Haz una pausa, inclina la cabeza y reza la <a href="#spiritual-communion">oración de comunión espiritual</a>. Quédate en silencio un momento para dar gracias.'),
            ("No pierdas el contacto", "Llama a tu parroquia: los sacerdotes y ministros quieren saber quién no puede venir, y muchas parroquias llevan el boletín o te ponen en contacto con alguien que te visite.")],
        f_h="Parroquias: añadan su transmisión",
        f_p="Si su parroquia transmite sus Misas, añadan el enlace aquí. Es gratis. Lo confirmamos con la parroquia antes de publicarlo y su correo queda privado (solo lo usamos para confirmar). También pueden añadir su contacto de OCIA y sus horarios de Misa en el <a href=\"/es/registrar-ocia#form\">formulario para parroquias</a>.",
        f_parish="Nombre de la parroquia", f_city="Ciudad", f_state="Estado", f_stream="Enlace de la transmisión", f_stream_ph="https://www.youtube.com/@suparroquia/streams",
        f_when="Cuándo transmiten", f_when_ph="p. ej. dom. 10:30 a. m. (inglés) y 12:30 p. m. (español); entre semana 8 a. m.",
        f_name="Su nombre", f_email="Su correo (no se publica)", f_consent="Sirvo en esta parroquia, y la parroquia está de acuerdo en que este enlace se muestre en CatholicDoorway.com.",
        f_legal='Cómo tratamos lo que nos envía: <a href="/es/privacidad#you-send">Política de privacidad</a> y <a href="/es/terminos#listings">Términos de uso</a>.',
        f_send="Enviar para revisión",
        note="CatholicDoorway enlaza las páginas oficiales de cada emisora y los enlaces que nos envían las parroquias. No alojamos ni copiamos ningún video. Que un enlace aparezca aquí no significa que respaldemos todo lo que hay en ese canal.",
    ),
    "pt": dict(
        kicker='<a href="/pt/oracoes">Orações</a> &rsaquo; Missa on-line',
        h1="Assistir à Missa on-line",
        lede="Não pode ir à igreja? Reze a Missa com uma transmissão ao vivo, encontre uma paróquia perto de você que transmite as Missas e saiba como receber a Comunhão em casa se estiver doente ou sem poder sair. Tudo é gratuito e sem cadastro.",
        toc=[("broadcasts", "Missas diárias transmitidas"), ("parish-streams", "Transmissões de paróquias"), ("homebound", "Doente ou sem poder sair?"),
             ("spiritual-communion", "Oração da comunhão espiritual"), ("at-home", "Viver a Missa em casa"), ("add-stream", "Paróquias: cadastrem a transmissão")],
        b_h="Missas diárias transmitidas",
        b_p="Os links vêm direto dos sites e canais oficiais de cada emissora. Os horários aparecem no seu fuso horário",
        b_p2="Festas, feriados e eventos do Papa podem mudar a programação; a página de cada emissora tem a palavra final.",
        all_langs="Todos os idiomas", your="seu horário", at_source="Horário local", next_="Próxima", on_now="Ao vivo agora", see_sched="Ver a programação",
        watch="Assistir ao vivo", past="Missas anteriores", vat_past="A agenda do Papa", sched_link="Programação da emissora", checked=f"Programação conferida em {CHECKED}",
        p_h="Transmissões de paróquias",
        p_p="Muitas paróquias transmitem as Missas pelo YouTube, Facebook ou pelo próprio site. As paróquias nos enviam o link, confirmamos com elas e você pode ver quando cada link foi conferido pela última vez. Se algum parar de funcionar, toque em <em>Avisar link quebrado</em> e vamos verificar.",
        p_map='Prefere uma paróquia perto de você? Em <a href="/pt/encontrar-igreja?stream=1">Encontrar uma igreja</a>, marque <strong>Transmite a Missa</strong> para ver só as igrejas que cadastraram uma transmissão.',
        state="Estado", all_states="Todos os estados", loading="Carregando…",
        h_h="Doente ou sem poder sair?",
        obl_h="Assistir à Missa vale para o domingo?",
        obl=["Assistir à Missa pela TV ou pela internet é uma boa forma de rezar, mas não substitui ir à Missa. Os católicos são chamados a participar pessoalmente da Missa aos domingos e nos dias de preceito.",
             "Você está <strong>dispensado</strong> quando tem um motivo sério para não ir: se está doente, não pode sair de casa, está se recuperando, a idade não permite, cuida de alguém que precisa de você, ou quando a viagem ou o tempo tornam a ida realmente perigosa (Catecismo 2181). Não há pecado em faltar à Missa por um motivo assim, e você não precisa da permissão de ninguém. O seu pároco também pode dispensá-lo em outros casos; pergunte se tiver dúvida.",
             "Nesses dias, assistir a uma Missa e fazer a comunhão espiritual é uma bela forma de santificar o dia do Senhor."],
        obl_link='Veja os <a href="/pt/calendario">dias de preceito</a> deste ano.',
        com_h="A Comunhão em casa",
        com=["Toda paróquia pode levar a Sagrada Comunhão a quem não pode ir à igreja. Um padre, diácono ou ministro leigo preparado faz a visita, muitas vezes toda semana, e você não precisa estar inscrito na paróquia para pedir.",
             "Se estiver doente, você também pode pedir que um padre ouça a sua Confissão e dê a Unção dos Enfermos em casa ou no hospital."],
        com_say_h="Ligue para a secretaria paroquial e diga algo assim:",
        com_say="“Olá, meu nome é ____. Eu (minha mãe) não posso sair de casa; moro em ____ e gostaria de receber a Comunhão em casa. Alguém da paróquia poderia vir? Também gostaria de falar com um padre para me confessar.”",
        com_tips=["Num hospital ou casa de repouso, peça na recepção pelo capelão católico.",
                  "O jejum de uma hora antes da Comunhão não obriga os idosos, os doentes nem quem cuida deles (cânon 919).",
                  "Prepare uma mesinha com uma toalha limpa, um crucifixo e uma vela, se tiver."],
        com_links='<a class="btn small" href="/pt/encontrar-igreja">Encontre a sua paróquia</a> <a class="btn small secondary" href="/pt/uncao">A Unção dos Enfermos</a>',
        sc_h="Oração da comunhão espiritual",
        sc_p="Quando não pode receber a Eucaristia, você ainda pode pedir a Jesus que venha ao seu coração. Muitos rezam esta oração na hora da Comunhão, enquanto assistem à Missa. É adaptada de Santo Afonso Maria de Ligório.",
        sc_text="Meu Jesus, eu creio que estais presente no Santíssimo Sacramento do Altar.\nAmo-vos sobre todas as coisas e desejo receber-vos em minha alma.\nJá que agora não posso receber-vos sacramentalmente,\nvinde ao menos espiritualmente ao meu coração.\nComo se já vos tivesse recebido, eu vos abraço e me uno inteiramente a vós.\nNão permitais que eu jamais me separe de vós. Amém.",
        ah_h="Viver a Missa em casa",
        ah=[("Assista ao vivo se puder", "Uma Missa ao vivo une você à mesma oração de quem está na igreja. As reprises também ajudam, principalmente para quem trabalha ou dorme em horários diferentes."),
            ("Prepare um cantinho", "Desligue as outras telas, acenda uma vela, coloque um crucifixo ou uma imagem perto da TV e, se puder, vista-se como para ir à igreja."),
            ("Participe", 'Responda, cante e fique de pé, sente-se ou ajoelhe-se se puder. O nosso <a href="/pt/primeira-missa">guia da Missa</a> traz todas as respostas, e aqui estão as <a href="/pt/biblia">leituras do dia</a>.'),
            ("Na Comunhão, reze", 'Faça uma pausa, incline a cabeça e reze a <a href="#spiritual-communion">oração da comunhão espiritual</a>. Fique um momento em silêncio, em ação de graças.'),
            ("Mantenha o contato", "Ligue para a sua paróquia: padres e ministros querem saber quem não pode vir, e muitas paróquias levam o boletim ou indicam alguém para visitar você.")],
        f_h="Paróquias: cadastrem a sua transmissão",
        f_p="Se a sua paróquia transmite as Missas, cadastre o link aqui. É gratuito. Confirmamos com a paróquia antes de publicar, e o seu e-mail fica privado (só o usamos para confirmar). As paróquias também podem informar o contato da OCIA e os horários de Missa no <a href=\"/pt/cadastrar-ocia#form\">formulário para paróquias</a>.",
        f_parish="Nome da paróquia", f_city="Cidade", f_state="Estado", f_stream="Link da transmissão", f_stream_ph="https://www.youtube.com/@suaparoquia/streams",
        f_when="Quando transmitem", f_when_ph="ex.: dom. 10h30 (inglês) e 12h30 (português); dias de semana 8h",
        f_name="Seu nome", f_email="Seu e-mail (não é publicado)", f_consent="Sirvo nesta paróquia, e a paróquia concorda que este link seja mostrado no CatholicDoorway.com.",
        f_legal='Como tratamos o que você envia: <a href="/pt/privacidade#you-send">Política de privacidade</a> e <a href="/pt/termos#listings">Termos de uso</a>.',
        f_send="Enviar para revisão",
        note="O CatholicDoorway indica as páginas oficiais de cada emissora e os links que as paróquias nos enviam. Não hospedamos nem copiamos nenhum vídeo. Um link aqui não significa que endossamos tudo o que há naquele canal.",
    ),
    "tl": dict(
        kicker='<a href="/tl/mga-dasal">Mga dasal</a> &rsaquo; Misa online',
        h1="Manood ng Misa online",
        lede="Hindi makapunta sa simbahan? Ipagdasal ang Misa kasabay ng live na palabas, maghanap ng parokyang malapit sa iyo na nagla-livestream ng Misa, at alamin kung paano tumanggap ng Komunyon sa bahay kung may sakit ka o hindi makalabas. Libre ang lahat dito at walang kailangang pag-sign up.",
        toc=[("broadcasts", "Araw-araw na Misa sa TV at online"), ("parish-streams", "Livestream ng mga parokya"), ("homebound", "May sakit o hindi makalabas?"),
             ("spiritual-communion", "Dasal ng espirituwal na pakikinabang"), ("at-home", "Pakikiisa sa Misa sa bahay"), ("add-stream", "Para sa parokya: idagdag ang livestream")],
        b_h="Araw-araw na Misa sa TV at online",
        b_p="Galing mismo sa opisyal na website at channel ng bawat istasyon ang mga link na ito. Nakikita ang oras sa iyong time zone",
        b_p2="Maaaring magbago ang iskedyul tuwing kapistahan, pista opisyal at mga pagdiriwang ng Santo Papa, kaya ang pahina ng istasyon ang masusunod.",
        all_langs="Lahat ng wika", your="oras mo", at_source="Lokal na oras", next_="Susunod", on_now="Live ngayon", see_sched="Tingnan ang iskedyul",
        watch="Manood nang live", past="Mga nakaraang Misa", vat_past="Kalendaryo ng Santo Papa", sched_link="Iskedyul ng istasyon", checked=f"Sinuri ang iskedyul noong {CHECKED}",
        p_h="Livestream ng mga parokya",
        p_p="Maraming parokya ang nagla-livestream ng sariling Misa sa YouTube, Facebook o sa kanilang website. Ipinapadala sa amin ng parokya ang link, kinukumpirma namin ito sa kanila, at makikita mo kung kailan huling sinuri ang bawat link. Kung may hindi na gumagana, pindutin ang <em>Iulat ang sirang link</em> at titingnan namin.",
        p_map='Gusto mo ng parokyang malapit sa iyo? Sa <a href="/tl/hanapin-ang-simbahan?stream=1">Maghanap ng simbahan</a>, markahan ang <strong>May livestream ng Misa</strong> para makita lang ang mga simbahang nagdagdag ng livestream.',
        state="Estado", all_states="Lahat ng estado", loading="Naglo-load…",
        h_h="May sakit o hindi makalabas?",
        obl_h="Bilang ba sa Linggo ang panonood ng Misa?",
        obl=["Mabuting paraan ng pagdarasal ang panonood ng Misa sa TV o online, pero hindi nito napapalitan ang pagpunta sa Misa. Tinatawagan ang mga Katoliko na personal na makibahagi sa Misa tuwing Linggo at mga pistang pangilin.",
             "<strong>Hindi ka obligado</strong> kapag may mabigat kang dahilan kaya hindi ka makapunta: kung may sakit ka, hindi makalabas ng bahay, nagpapagaling, mahina na dahil sa edad, nag-aalaga ng taong nangangailangan sa iyo, o kapag talagang delikado ang biyahe o ang panahon (Katesismo 2181). Walang kasalanan sa hindi pagsisimba dahil sa ganitong dahilan, at hindi mo kailangan ng pahintulot ninuman. Maaari ka ring pahintulutan ng iyong kura paroko sa ibang sitwasyon, kaya magtanong kung hindi ka sigurado.",
             "Sa mga araw na iyon, magandang paraan ng pagpapabanal sa Araw ng Panginoon ang panonood ng Misa at espirituwal na pakikinabang."],
        obl_link='Tingnan ang mga <a href="/tl/kalendaryo">pistang pangilin</a> ngayong taon.',
        com_h="Komunyon sa bahay",
        com=["Kayang dalhan ng bawat parokya ng Banal na Komunyon ang mga hindi makapunta sa simbahan. Bumibisita ang pari, diyakono o sinanay na lay minister, kadalasan bawat linggo, at hindi mo kailangang nakatala sa parokya para humiling.",
             "Kung may sakit ka, maaari ka ring humiling ng pari para mangumpisal at tumanggap ng Pagpapahid ng Langis sa Maysakit sa bahay o sa ospital."],
        com_say_h="Tawagan ang opisina ng parokya at sabihin ang ganito:",
        com_say="“Magandang araw po, ako si ____. Hindi po ako (ang nanay ko) makalabas ng bahay; nakatira po kami sa ____ at gusto po naming tumanggap ng Komunyon sa bahay. Maaari po bang may dumalaw mula sa parokya? Gusto ko rin pong makausap ang pari para mangumpisal.”",
        com_tips=["Sa ospital o nursing home, hanapin sa front desk ang Katolikong chaplain.",
                  "Hindi saklaw ng isang oras na pag-aayuno bago mag-Komunyon ang matatanda, maysakit at ang nag-aalaga sa kanila (Canon 919).",
                  "Maghanda ng maliit na mesa na may malinis na tela, krus at kandila kung mayroon."],
        com_links='<a class="btn small" href="/tl/hanapin-ang-simbahan">Hanapin ang iyong parokya</a> <a class="btn small secondary" href="/tl/pagpapahid-ng-langis">Pagpapahid ng Langis sa Maysakit</a>',
        sc_h="Dasal ng espirituwal na pakikinabang",
        sc_p="Kapag hindi ka makatanggap ng Eukaristiya, maaari mo pa ring hilingin kay Hesus na pumasok sa iyong puso. Marami ang nagdarasal nito sa oras ng Komunyon habang nanonood ng Misa. Hango ito kay San Alfonso Maria de Liguori.",
        sc_text="Hesus ko, sumasampalataya akong tunay kang naririto sa Kabanal-banalang Sakramento.\nIniibig kita nang higit sa lahat ng bagay, at hinahangad kong tanggapin ka sa aking kaluluwa.\nYamang hindi kita matanggap ngayon sa Sakramento,\npumarito ka man lamang sa aking puso sa espirituwal na paraan.\nNiyayakap kita na para bang nasa akin ka na,\nat buong-buo akong nakikiisa sa iyo.\nHuwag mong itulot na ako'y mahiwalay pa sa iyo kailanman. Amen.",
        ah_h="Pakikiisa sa Misa sa bahay",
        ah=[("Manood nang live kung kaya", "Pinag-iisa ka ng live na Misa sa iisang dasal ng mga nasa simbahan. Mainam din ang replay, lalo na sa mga nagtatrabaho o natutulog sa ibang oras."),
            ("Maghanda ng maliit na lugar", "Patayin ang ibang screen, magsindi ng kandila, maglagay ng krus o banal na larawan malapit sa TV, at magbihis na parang magsisimba kung kaya."),
            ("Makiisa", 'Sumagot, umawit, at tumayo, umupo o lumuhod kung kaya. Nasa aming <a href="/tl/unang-misa">gabay sa Misa</a> ang lahat ng sagot, at narito ang <a href="/tl/bibliya">mga pagbasa ngayon</a>.'),
            ("Sa Komunyon, magdasal", 'Huminto sandali, yumuko at idasal ang <a href="#spiritual-communion">dasal ng espirituwal na pakikinabang</a>. Manahimik sandali bilang pasasalamat.'),
            ("Manatiling konektado", "Tawagan ang iyong parokya: gustong malaman ng mga pari at minister kung sino ang hindi makapunta, at maraming parokya ang nagdadala ng bulletin o nag-uugnay sa iyo sa isang dadalaw.")],
        f_h="Para sa parokya: idagdag ang inyong livestream",
        f_p="Kung nagla-livestream ng Misa ang inyong parokya, idagdag dito ang link. Libre ito. Kinukumpirma namin sa parokya bago ito lumabas, at mananatiling pribado ang inyong email (gagamitin lang namin ito para kumpirmahin). Maaari ring idagdag ng parokya ang kontak ng OCIA at oras ng Misa sa <a href=\"/tl/ilista-ang-ocia#form\">form para sa parokya</a>.",
        f_parish="Pangalan ng parokya", f_city="Lungsod", f_state="Estado", f_stream="Link ng livestream", f_stream_ph="https://www.youtube.com/@inyongparokya/streams",
        f_when="Kailan kayo nagla-livestream", f_when_ph="hal. Linggo 10:30 n.u. (Ingles), 12:30 n.t. (Tagalog); karaniwang araw 8 n.u.",
        f_name="Inyong pangalan", f_email="Inyong email (hindi ilalathala)", f_consent="Naglilingkod ako sa parokyang ito, at pumapayag ang parokya na ipakita ang link na ito sa CatholicDoorway.com.",
        f_legal='Paano namin pinangangasiwaan ang ipinapadala ninyo: <a href="/tl/patakaran-sa-privacy#you-send">Patakaran sa privacy</a> at <a href="/tl/mga-tuntunin#listings">Mga tuntunin</a>.',
        f_send="Ipadala para masuri",
        note="Nagli-link ang CatholicDoorway sa opisyal na pahina ng bawat istasyon at sa mga link na ipinapadala ng mga parokya. Hindi kami nagho-host o kumokopya ng anumang video. Ang paglalagay ng link dito ay hindi nangangahulugang sinasang-ayunan namin ang lahat ng nasa channel na iyon.",
    ),
}


def _pick(v, lang):
    return v.get(lang, v.get("en", "")) if isinstance(v, dict) else v


def _times_text(s, lang):
    rows = []
    for key, _days, times in s["sched"]:
        rows.append(f'{DAYS[lang][key]}: {", ".join(times)}')
    return "; ".join(rows)


def _stream_card(s, lang, t):
    langs = " ".join(s["langs"])
    sched = [{"d": d, "t": tt, "k": DAYS[lang][k]} for k, d, tt in s["sched"]]
    zone = ZONE[s["tz"]][lang]
    names = " · ".join(LANG_NAME[lang][x] for x in s["langs"])
    note = _pick(s.get("notes", {}), lang)
    src_line = (f'{t["at_source"]} ({e(zone)}): {e(_times_text(s, lang))}' if s["sched"] else e(note))
    if s["sched"] and note:
        src_line += f'<br>{e(note)}'
    live, past = _pick(s["live"], lang), _pick(s["past"], lang)
    past_label = t["vat_past"] if s["id"] == "vatican" else t["past"]
    btns = f'<a class="btn small" href="{e(live)}" target="_blank" rel="noopener">{t["watch"]}</a>'
    if past and past != live:
        btns += f' <a class="btn small secondary" href="{e(past)}" target="_blank" rel="noopener">{past_label}</a>'
    return (f'<article class="card stream" id="stream-{s["id"]}" data-langs="{langs}" data-tz="{s["tz"]}" '
            f"data-sched='{e(json.dumps(sched, ensure_ascii=False), quote=True)}'>"
            f'<h3>{e(s["name"])}</h3>'
            f'<p class="small muted stream-meta">{e(s["where"][lang])} &middot; {e(names)}</p>'
            f'<p>{e(s["desc"][lang])}</p>'
            f'<div class="stream-times" aria-live="polite"></div>'
            f'<p class="small muted stream-src">{src_line}</p>'
            f'<div class="actions">{btns}</div>'
            f'<p class="small muted stream-check"><a href="{e(s["src"])}" target="_blank" rel="noopener">{t["sched_link"]}</a> &middot; {t["checked"]}</p>'
            f'</article>')


def page(lang):
    t = T[lang]
    # The visitor's own language first, then the others.
    order = sorted(STREAMS, key=lambda s: (0 if lang in s["langs"] else 1))
    cards = "\n".join(_stream_card(s, lang, t) for s in order)
    langs_used = ["en", "es", "pt", "tl"]
    chips = f'<button type="button" class="chip" data-slang="all" aria-pressed="true">{t["all_langs"]}</button>' + "".join(
        f'<button type="button" class="chip" data-slang="{c}" aria-pressed="false">{LANG_NAME[lang][c]}</button>' for c in langs_used)
    toc = "".join(f'<li><a href="#{a}">{e(b)}</a></li>' for a, b in t["toc"])
    obl = "".join(f"<p>{p}</p>" for p in t["obl"])
    com = "".join(f"<p>{p}</p>" for p in t["com"])
    tips = "".join(f"<li>{x}</li>" for x in t["com_tips"])
    ah = "".join(f'<article class="card"><h3>{e(h)}</h3><p>{p}</p></article>' for h, p in t["ah"])
    labels = json.dumps({k: t[k] for k in ("your", "next_", "on_now", "see_sched")}, ensure_ascii=False)
    return f'''<div class="page-head">
  <div class="wrap">
    <p class="kicker">{t["kicker"]}</p>
    <h1>{t["h1"]}</h1>
    <p class="lede">{t["lede"]}</p>
  </div>
</div>

<div class="wrap watch" data-labels='{e(labels, quote=True)}'>
  <ul class="toc" aria-label="{e(t["h1"])}">{toc}</ul>

  <section class="section" id="broadcasts">
    <h2>{t["b_h"]}</h2>
    <p class="prose">{t["b_p"]}<span class="tz-name"></span>. {t["b_p2"]}</p>
    <div class="filters" role="group" aria-label="{e(t["all_langs"])}">{chips}</div>
    <div class="grid two stream-grid">
{cards}
    </div>
  </section>

  <section class="section" id="parish-streams">
    <h2>{t["p_h"]}</h2>
    <p class="prose">{t["p_p"]}</p>
    <div class="note"><p>{t["p_map"]}</p></div>
    <div class="filters"><label>{t["state"]} <select id="ps-state"><option value="">{t["all_states"]}</option></select></label></div>
    <div id="ps-list" class="grid two"><p class="muted">{t["loading"]}</p></div>
  </section>

  <section class="section" id="homebound">
    <h2>{t["h_h"]}</h2>
    <div class="grid two">
      <article class="card" id="sunday-obligation">
        <h3>{t["obl_h"]}</h3>
        {obl}
        <p class="small muted">{t["obl_link"]}</p>
      </article>
      <article class="card" id="communion-at-home">
        <h3>{t["com_h"]}</h3>
        {com}
        <p><strong>{t["com_say_h"]}</strong></p>
        <p class="ocia-say">{t["com_say"]}</p>
        <ul class="prose small">{tips}</ul>
        <div class="actions">{t["com_links"]}</div>
      </article>
    </div>
  </section>

  <section class="section">
    <article class="card prayer" id="spiritual-communion">
      <h2>{t["sc_h"]}</h2>
      <p class="muted">{t["sc_p"]}</p>
      <p class="text">{e(t["sc_text"])}</p>
    </article>
  </section>

  <section class="section" id="at-home">
    <h2>{t["ah_h"]}</h2>
    <div class="grid three">{ah}</div>
  </section>

  <section class="section" id="add-stream">
    <h2>{t["f_h"]}</h2>
    <p class="prose">{t["f_p"]}</p>
    <form class="card ocia-form" id="stream-form" novalidate>
      <div class="form-grid">
        <label>{t["f_parish"]} <span class="req">*</span><input name="parish" required maxlength="120" autocomplete="organization"></label>
        <label>{t["f_city"]} <span class="req">*</span><input name="city" required maxlength="80" autocomplete="address-level2"></label>
        <label>{t["f_state"]} <span class="req">*</span><select name="state" required>{{{{STATE_OPTIONS}}}}</select></label>
        <label class="wide">{t["f_stream"]} <span class="req">*</span><input name="stream" type="url" required maxlength="300" placeholder="{e(t["f_stream_ph"])}"></label>
        <label class="wide">{t["f_when"]}<input name="stream_times" maxlength="200" placeholder="{e(t["f_when_ph"])}"></label>
        <label>{t["f_name"]} <span class="req">*</span><input name="contact" required maxlength="80" autocomplete="name"></label>
        <label>{t["f_email"]} <span class="req">*</span><input name="email" type="email" required maxlength="120" autocomplete="email"></label>
      </div>
      <label class="hp" aria-hidden="true">Leave this empty<input name="website2" tabindex="-1" autocomplete="off"></label>
      <label class="consent"><input type="checkbox" name="consent" required> {t["f_consent"]} <span class="req">*</span></label>
      <p class="small muted">{t["f_legal"]}</p>
      <div class="btn-row"><button class="btn" type="submit">{t["f_send"]}</button></div>
      <p class="status-msg" id="stream-msg" role="status" aria-live="polite"></p>
    </form>
  </section>

  <p class="small muted">{t["note"]}</p>
</div>'''


def render(body, lang):
    if "{{WATCH}}" not in body:
        return body
    return body.replace("{{WATCH}}", page(lang))
