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
import re
import urllib.parse

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
    ("first-mass", "Your First Mass", "Your First Mass: A Step-by-Step Guide | CatholicDoorway",
     "Going to Mass for the first time? A step-by-step companion for your phone: when to stand, sit and kneel, what people say, and what to do at Communion."),
    ("how-to", "How-To Guides", "Catholic How-To Guides: Confession, Baptism, Marriage and More | CatholicDoorway",
     "Plain, practical Catholic how-tos: going to Confession, joining a parish, baptizing a child, getting married, Last Rites, funerals and coming back to the Church."),
    ("confession", "Confession", "How to Go to Confession: A Step-by-Step Guide | CatholicDoorway",
     "How to go to Catholic Confession: when and where, how to prepare, exactly what to say, and what to do if it has been years."),
    ("coming-back", "Coming Back", "Coming Back to the Catholic Church | CatholicDoorway",
     "Been away from the Catholic Church? How to come back: Mass, talking with a priest, Confession, and special situations like marriage outside the Church."),
    ("join-a-parish", "Join a Parish", "How to Join (Register at) a Catholic Parish | CatholicDoorway",
     "Why and how to register at a Catholic parish in the U.S., and what it helps with: sponsor letters, baptisms, weddings and Catholic school."),
    ("baptism", "Baptism", "How to Have Your Child Baptized Catholic | CatholicDoorway",
     "How infant baptism works in a Catholic parish: when to call, the preparation class, godparent requirements, the ceremony and special situations."),
    ("marriage", "Marriage", "How to Get Married in the Catholic Church | CatholicDoorway",
     "Getting married in the Catholic Church: how far ahead to start, marriage preparation, documents, marrying a non-Catholic, previous marriages and convalidation."),
    ("anointing", "Anointing of the Sick", "Anointing of the Sick and Last Rites: When to Call a Priest | CatholicDoorway",
     "When and how to call a priest for Anointing of the Sick or Last Rites, what the sacraments are, and what to do if someone is dying now."),
    ("funerals", "Funerals", "Planning a Catholic Funeral | CatholicDoorway",
     "How to plan a Catholic funeral: the vigil, funeral Mass and committal, cremation rules, costs, and having a Mass offered for the deceased."),
    ("baptism-certificate", "Baptism Records", "How to Get a Copy of Your Catholic Baptism Certificate | CatholicDoorway",
     "How to request your Catholic baptism record with notations for a wedding or sponsor letter, including closed parishes and baptisms abroad."),
    ("find-a-church", "Find a Church", "Find a Catholic Church Near You | CatholicDoorway",
     "Find Catholic churches near you on a free map built from OpenStreetMap, with address, phone, website and directions."),
    ("prayers", "Prayers", "Catholic Prayers and How to Pray the Rosary | CatholicDoorway",
     "Traditional Catholic prayers, from the Our Father and Hail Mary to the Memorare, plus a step-by-step guide to the Rosary."),
    ("rosary", "Pray the Rosary", "Pray the Rosary Online, Bead by Bead | CatholicDoorway",
     "An interactive Rosary: tap through each bead with the prayers, today's mysteries and their Scripture passages. Free, no app needed."),
    ("bible", "Bible & Readings", "The Bible and Today's Mass Readings | CatholicDoorway",
     "Today's Catholic Mass readings, how the Catholic Bible is arranged, and where to read it free online."),
    ("calendar", "Holy Days Calendar", "Catholic Holy Days of Obligation and Fasting Calendar | CatholicDoorway",
     "Holy days of obligation, fasting days and major Catholic feasts for the U.S., with a free calendar you can add to your iPhone, Google or Outlook."),
    ("beliefs", "Beliefs", "What Catholics Believe | CatholicDoorway",
     "A plain-language overview of Catholic belief and practice: the Creed, the seven sacraments, Scripture and Tradition, Mary and the saints, and the moral life."),
    ("questions", "Honest Questions", "Honest Questions About the Catholic Church, Answered | CatholicDoorway",
     "Short, kind, straight answers to the questions people ask about Catholics: Mary, saints, confession, the Pope, purgatory, the extra Bible books and more."),
    ("structure", "Church Structure", "How the Catholic Church Is Organized | CatholicDoorway",
     "How the Catholic Church is organized: the Pope, bishops, dioceses, parishes, priests and deacons, explained simply."),
    ("dioceses", "Dioceses", "U.S. Catholic Dioceses Directory | CatholicDoorway",
     "Every Catholic diocese, archdiocese and eparchy in the United States: its bishop, cathedral, website, OCIA help and local saints."),
    ("saints", "Saints", "Catholic Saints, Blesseds and Venerables | CatholicDoorway",
     "Meet the saints, and learn the path to sainthood: Servant of God, Venerable, Blessed and Saint."),
    ("saints-directory", "Saints Directory", "Saints and Causes Directory: Saints, Blesseds, Venerables, Servants of God | CatholicDoorway",
     "Search thousands of Catholic Saints, Blesseds, Venerables and Servants of God by name, country, century and patronage. Updated weekly."),
    ("glossary", "Glossary", "Catholic Glossary: Terms Explained Simply | CatholicDoorway",
     "Plain-English definitions of Catholic words, from Advent to Vespers."),
    ("popes", "Popes", "All 267 Popes in Succession, from St. Peter to Leo XIV | CatholicDoorway",
     "Every Pope in order from St. Peter to Leo XIV: number in the line of succession, years as Pope, birth and death, and what each is remembered for."),
    ("about", "About", "About CatholicDoorway",
     "About CatholicDoorway.com: a free, ad-free guide to the Catholic faith. Sources, data and corrections."),
    ("404", "Not found", "Page not found | CatholicDoorway", "This page could not be found."),
]
NAV_EXCLUDE = {"about", "404", "saints-directory", "how-to", "confession", "coming-back", "join-a-parish", "baptism", "marriage", "anointing", "funerals", "baptism-certificate", "popes", "dioceses", "find-a-church", "first-mass", "calendar", "rosary", "questions"}
# Pages shown in a dropdown under a main menu item: parent slug -> [(slug, label)]
SUBNAV = {"beliefs": [("beliefs", "What Catholics believe"), ("questions", "Honest questions, answered")],
          "prayers": [("prayers", "Catholic prayers"), ("rosary", "Pray the Rosary")],
          "bible": [("bible", "Today’s readings and the Bible"), ("calendar", "Holy Days Calendar")],
          "start-here": [("start-here", "Becoming Catholic (OCIA)"), ("first-mass", "Your First Mass"),
                         ("how-to", "How-To Guides"), ("confession", "How to go to Confession"), ("coming-back", "Coming back to the Church")],
          "saints": [("saints", "Meet the saints"), ("saints-directory", "Saints and causes directory")],
          "structure": [("structure", "How the Church is organized"), ("popes", "All 267 Popes"),
                        ("dioceses", "U.S. Dioceses"), ("find-a-church", "Find a Church")]}

ES_PAGES = [
    ("index", "index", "Inicio", "CatholicDoorway en español: una guía gratuita de la fe católica",
     "Una guía sencilla y gratuita de la fe católica: oraciones, cómo hacerse católico (OCIA), tu primera Misa, el Rosario y preguntas frecuentes."),
    ("start-here", "comenzar", "Hacerse católico", "Cómo hacerse católico: OCIA paso a paso | CatholicDoorway",
     "¿Te interesa la Iglesia Católica? Cómo funciona OCIA, sus cuatro etapas, cuánto dura, con quién hablar y qué esperar en tu primera Misa."),
    ("first-mass", "primera-misa", "Tu primera Misa", "Tu primera Misa, paso a paso | CatholicDoorway",
     "¿Vas a Misa por primera vez? Una guía paso a paso para tu teléfono: cuándo ponerse de pie, sentarse y arrodillarse, qué se responde y qué hacer en la Comunión."),
    ("how-to", "guias", "Guías prácticas", "Guías católicas prácticas: Confesión, Bautismo, Matrimonio y más | CatholicDoorway",
     "Guías católicas sencillas y prácticas: confesarse, inscribirse en una parroquia, bautizar a un hijo, casarse por la Iglesia, la Unción de los enfermos, funerales y volver a la Iglesia."),
    ("confession", "confesion", "Confesión", "Cómo confesarse: guía paso a paso | CatholicDoorway",
     "Cómo hacer una buena confesión: cuándo y dónde, cómo prepararse, qué decir exactamente y qué hacer si han pasado años."),
    ("coming-back", "volver", "Volver a la Iglesia", "Volver a la Iglesia Católica | CatholicDoorway",
     "¿Te alejaste de la Iglesia? Cómo volver: la Misa, hablar con un sacerdote, la Confesión y casos especiales como un matrimonio fuera de la Iglesia."),
    ("join-a-parish", "inscribirse-parroquia", "Inscribirse en una parroquia", "Cómo inscribirse en una parroquia católica | CatholicDoorway",
     "Por qué y cómo inscribirse en una parroquia católica en Estados Unidos, y en qué ayuda: cartas para padrinos, bautizos, bodas y escuela católica."),
    ("baptism", "bautismo", "Bautismo", "Cómo bautizar a tu hijo en la Iglesia Católica | CatholicDoorway",
     "Cómo funciona el Bautismo de un bebé en una parroquia católica: cuándo llamar, la plática, los requisitos de los padrinos, la ceremonia y los casos especiales."),
    ("marriage", "matrimonio", "Matrimonio", "Cómo casarse por la Iglesia Católica | CatholicDoorway",
     "Casarse por la Iglesia: con cuánta anticipación empezar, la preparación, los documentos, casarse con alguien no católico, matrimonios anteriores y convalidación."),
    ("anointing", "uncion", "Unción de los enfermos", "La Unción de los enfermos y los últimos sacramentos | CatholicDoorway",
     "Cuándo y cómo llamar a un sacerdote para la Unción de los enfermos o los últimos sacramentos, qué son y qué hacer si alguien se está muriendo ahora."),
    ("funerals", "funerales", "Funerales", "Cómo preparar un funeral católico | CatholicDoorway",
     "Cómo preparar un funeral católico: la vigilia, la Misa de funeral y la sepultura, las normas sobre la cremación, los costos y las Misas por los difuntos."),
    ("baptism-certificate", "fe-de-bautismo", "Fe de bautismo", "Cómo pedir tu fe de bautismo católica | CatholicDoorway",
     "Cómo solicitar tu fe de bautismo con notas marginales para una boda o para ser padrino, incluso si la parroquia cerró o te bautizaron en otro país."),
    ("prayers", "oraciones", "Oraciones", "Oraciones católicas y cómo rezar el Rosario | CatholicDoorway",
     "Las oraciones católicas tradicionales en español: el Padre Nuestro, el Ave María, el Credo, la Salve y más, con una guía del Rosario."),
    ("rosary", "rosario", "Reza el Rosario", "Reza el Rosario en línea, cuenta por cuenta | CatholicDoorway",
     "Reza el Rosario paso a paso en tu teléfono: las cuentas se iluminan, cada misterio trae su pasaje bíblico y se guarda dónde vas."),
    ("bible", "biblia", "Biblia", "La Biblia y las lecturas de la Misa de hoy | CatholicDoorway",
     "Las lecturas de la Misa de hoy en español, cómo está organizada la Biblia católica y dónde leerla gratis en línea."),
    ("calendar", "calendario", "Calendario", "Días de precepto y de ayuno: calendario católico | CatholicDoorway",
     "Los días de precepto, los días de ayuno y las fiestas principales en Estados Unidos, con un calendario gratis en español para tu iPhone, Google u Outlook."),
    ("beliefs", "creencias", "Creencias", "Lo que creen los católicos | CatholicDoorway",
     "Un resumen sencillo de la fe y la práctica católica: el Credo, los siete sacramentos, la Escritura y la Tradición, María y los santos, y la vida moral."),
    ("questions", "preguntas", "Preguntas sinceras", "Preguntas sinceras sobre la Iglesia Católica, respondidas | CatholicDoorway",
     "Respuestas breves, amables y claras a lo que la gente pregunta sobre los católicos: María, los santos, la confesión, el Papa, el purgatorio y más."),
    ("glossary", "glosario", "Glosario", "Glosario católico: palabras explicadas | CatholicDoorway",
     "Definiciones sencillas de las palabras católicas, de Adviento a Vísperas."),
    ("structure", "estructura", "La Iglesia", "Cómo se organiza la Iglesia Católica | CatholicDoorway",
     "Cómo se organiza la Iglesia Católica: el Papa, los obispos, las diócesis, las parroquias, los sacerdotes y los diáconos, explicado con sencillez."),
    ("dioceses", "diocesis", "Diócesis", "Las diócesis católicas de Estados Unidos | CatholicDoorway",
     "Todas las diócesis, arquidiócesis y eparquías católicas de Estados Unidos: su obispo, su catedral, su sitio web y ayuda para empezar OCIA."),
    ("popes", "papas", "Los Papas", "Los 267 Papas, de San Pedro a León XIV | CatholicDoorway",
     "Todos los Papas en orden, de San Pedro a León XIV: su lugar en la sucesión, sus años de pontificado y por qué se les recuerda."),
    ("saints", "santos", "Santos", "Santos, Beatos y Venerables católicos | CatholicDoorway",
     "Conoce a los santos y el camino a la santidad: Siervo de Dios, Venerable, Beato y Santo."),
    ("find-a-church", "buscar-iglesia", "Buscar una iglesia", "Encuentra una iglesia católica cerca de ti | CatholicDoorway",
     "Busca iglesias católicas en Estados Unidos por ciudad o código postal: dirección, teléfono, sitio web y cómo llegar."),
]
ES_TEXT = dict(lang="es", skip="Saltar al contenido", home="/es/", home_label="Inicio de CatholicDoorway",
               theme_label="Cambiar a modo claro u oscuro", menu_label="Menú", nav_label="Principal",
               alt_lang="en", alt_label="English")
EN_TEXT = dict(lang="en", skip="Skip to content", home="/", home_label="CatholicDoorway home",
               theme_label="Switch light or dark mode", menu_label="Menu", nav_label="Main",
               alt_lang="es", alt_label="Español")
EN_TO_ES = {en: es for en, es, *_ in ES_PAGES}

# Portuguese: the core pages for newcomers. en_slug, pt_slug, nav label, <title>, meta description
PT_PAGES = [
    ("index", "index", "Início", "CatholicDoorway em português: um guia gratuito da fé católica",
     "Um guia simples e gratuito da fé católica: orações, como se tornar católico (OCIA), sua primeira Missa, o Rosário e uma busca de igrejas nos Estados Unidos."),
    ("start-here", "comecar", "Tornar-se católico", "Como se tornar católico: a OCIA passo a passo | CatholicDoorway",
     "Interessado na Igreja Católica? Como funciona a OCIA, suas quatro etapas, quanto tempo dura, com quem falar e o que esperar na sua primeira Missa."),
    ("first-mass", "primeira-missa", "Sua primeira Missa", "Sua primeira Missa, passo a passo | CatholicDoorway",
     "Vai à Missa pela primeira vez? Um guia passo a passo no seu celular: quando ficar de pé, sentar e ajoelhar, o que se responde e o que fazer na Comunhão."),
    ("prayers", "oracoes", "Orações", "Orações católicas e como rezar o Rosário | CatholicDoorway",
     "As orações católicas tradicionais em português: o Pai-Nosso, a Ave-Maria, o Creio, a Salve-Rainha e mais, com um guia do Rosário."),
    ("rosary", "rosario", "Reze o Rosário", "Reze o Rosário on-line, conta por conta | CatholicDoorway",
     "Reze o Rosário passo a passo no seu celular: as contas se acendem, cada mistério traz sua passagem bíblica e o lugar onde você parou fica guardado."),
    ("beliefs", "crencas", "Crenças", "No que os católicos acreditam | CatholicDoorway",
     "Um resumo simples da fé e da prática católica: o Credo, os sete sacramentos, a Escritura e a Tradição, Maria e os santos, e a vida moral."),
    ("find-a-church", "encontrar-igreja", "Encontrar uma igreja", "Encontre uma igreja católica perto de você | CatholicDoorway",
     "Procure igrejas católicas nos Estados Unidos por cidade ou ZIP code: endereço, telefone, site e como chegar."),
]
PT_TEXT = dict(lang="pt", skip="Pular para o conteúdo", home="/pt/", home_label="Início do CatholicDoorway",
               theme_label="Mudar para o modo claro ou escuro", menu_label="Menu", nav_label="Principal")
EN_TO_PT = {en: pt for en, pt, *_ in PT_PAGES}
PT_SUBNAV = {"comecar": [("comecar", "Tornar-se católico (OCIA)"), ("primeira-missa", "Sua primeira Missa")],
             "oracoes": [("oracoes", "Orações católicas"), ("rosario", "Reze o Rosário")]}
PT_NAV_EXCLUDE = set()

LANGS = [("en", "English", "home page"), ("es", "Español", "página de inicio"), ("pt", "Português", "página inicial")]
LANG_HOME = {"en": "/", "es": "/es/", "pt": "/pt/"}
LANG_WORD = {"en": "Language", "es": "Idioma", "pt": "Idioma"}
GLOBE_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M3 12h18M12 3c2.6 2.6 3.9 5.6 3.9 9s-1.3 6.4-3.9 9c-2.6-2.6-3.9-5.6-3.9-9S9.4 5.6 12 3z" fill="none" stroke="currentColor" stroke-width="1.8"/></svg>'


def lang_urls(en_slug):
    """The URL of this page in each language, or None where it has no translation yet."""
    if en_slug is None:
        return {"en": None, "es": None, "pt": None}
    es, pt = EN_TO_ES.get(en_slug), EN_TO_PT.get(en_slug)
    return {"en": "/" if en_slug == "index" else f"/{en_slug}",
            "es": None if es is None else ("/es/" if es == "index" else f"/es/{es}"),
            "pt": None if pt is None else ("/pt/" if pt == "index" else f"/pt/{pt}")}


def lang_menu(cur, urls):
    items = []
    for code, name, home_word in LANGS:
        href = urls.get(code)
        note = ""
        if href is None:
            href, note = LANG_HOME[code], f' <span class="lm-note">({home_word})</span>'
        here = ' aria-current="true"' if code == cur else ""
        items.append(f'<li><a href="{href}" hreflang="{code}" lang="{code}" data-lang="{code}"{here}>{name}{note}</a></li>')
    cur_name = dict((c, n) for c, n, _ in LANGS)[cur]
    return (f'<details class="lang-menu"><summary aria-label="{LANG_WORD[cur]}: {cur_name}">{GLOBE_SVG}'
            f'<span class="lm-code">{cur.upper()}</span></summary><ul class="lm-list">{"".join(items)}</ul></details>')


def alternates_html(urls):
    have = [(c, u) for c, u in urls.items() if u]
    if len(have) < 2:
        return ""
    out = [f'<link rel="alternate" hreflang="{c}" href="{DOMAIN}{u}">' for c, u in have]
    if urls.get("en"):
        out.append(f'<link rel="alternate" hreflang="x-default" href="{DOMAIN}{urls["en"]}">')
    return "\n".join(out)

DOOR_SVG = '''<svg viewBox="0 0 34 40" aria-hidden="true" focusable="false"><path d="M3 39V17C3 8.7 9.3 2 17 2s14 6.7 14 15v22" fill="none" stroke="currentColor" stroke-width="2.4"/><path d="M8 39V18.5C8 13 12 8.5 17 8.5S26 13 26 18.5V39" fill="currentColor" opacity=".16"/><path d="M8 39V18.5C8 13 12 8.5 17 8.5S26 13 26 18.5V39" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M17 12v9M13.6 15.2h6.8" stroke="#a8802f" stroke-width="2" stroke-linecap="round"/><circle cx="22" cy="28" r="1.4" fill="#a8802f"/><path d="M1 39h32" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/></svg>'''

MENU_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 6h18M3 12h18M3 18h18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>'
THEME_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>'

HEAD = """<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
{alternates}
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
<a class="skip-link" href="#main">{skip}</a>
<header class="site-header">
  <div class="wrap header-row">
    <a class="brand" href="{home}" aria-label="{home_label}">{door}<span class="brand-name">Catholic<span>Doorway</span></span></a>
    <div class="header-tools">
      {lang_menu}
      <button class="theme-btn" type="button" data-theme-toggle aria-label="{theme_label}">{theme}</button>
      <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav">{menu}<span class="nt-label">{menu_label}</span></button>
    </div>
    <nav class="site-nav" id="site-nav" aria-label="{nav_label}">
      <ul>
{nav}
      </ul>
    </nav>
  </div>
</header>
<main id="main">
"""

FOOT_ES = """</main>
<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <p class="footer-verse">&ldquo;Yo soy la puerta; el que entre por mí se salvará.&rdquo;</p>
        <p class="small">Juan 10:9</p>
      </div>
      <div>
        <h4>En español</h4>
        <ul>
          <li><a href="/es/comenzar">Cómo hacerse católico (OCIA)</a></li>
          <li><a href="/es/primera-misa">Tu primera Misa</a></li>
          <li><a href="/es/oraciones">Oraciones y el Rosario</a></li>
        </ul>
      </div>
      <div>
        <h4>Aprender</h4>
        <ul>
          <li><a href="/es/buscar-iglesia">Buscar una iglesia</a></li>
          <li><a href="/es/creencias">Lo que creemos</a></li>
          <li><a href="/es/santos">Santos</a></li>
        </ul>
      </div>
      <div>
        <h4>Sobre el sitio</h4>
        <ul>
          <li><a href="/about" lang="en">About</a></li>
          <li><a href="mailto:hello@catholicdoorway.com">Escríbenos</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-base">
      CatholicDoorway es una guía gratuita e independiente, sin anuncios. No es un sitio oficial de la Iglesia Católica ni de ninguna diócesis. Para la enseñanza oficial de la Iglesia, consulta el <a href="https://www.vatican.va/archive/catechism_sp/index_sp.html">Catecismo de la Iglesia Católica</a>.
    </div>
  </div>
</footer>
<script src="/assets/js/main.js" defer></script>
{extra_foot}
</body>
</html>
"""

FOOT_PT = """</main>
<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <p class="footer-verse">&ldquo;Eu sou a porta; se alguém entrar por mim, será salvo.&rdquo;</p>
        <p class="small">João 10,9</p>
      </div>
      <div>
        <h4>Em português</h4>
        <ul>
          <li><a href="/pt/comecar">Como se tornar católico (OCIA)</a></li>
          <li><a href="/pt/primeira-missa">Sua primeira Missa</a></li>
          <li><a href="/pt/oracoes">Orações e o Rosário</a></li>
        </ul>
      </div>
      <div>
        <h4>Aprender</h4>
        <ul>
          <li><a href="/pt/encontrar-igreja">Encontrar uma igreja</a></li>
          <li><a href="/pt/crencas">No que acreditamos</a></li>
        </ul>
      </div>
      <div>
        <h4>Sobre o site</h4>
        <ul>
          <li><a href="/about" lang="en">About</a></li>
          <li><a href="mailto:hello@catholicdoorway.com">Escreva para nós</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-base">
      O CatholicDoorway é um guia gratuito e independente, sem anúncios. Não é um site oficial da Igreja Católica nem de nenhuma diocese. Para o ensinamento oficial da Igreja, consulte o <a href="https://www.vatican.va/archive/cathechism_po/index_new/prima-pagina-cic_po.html">Catecismo da Igreja Católica</a>.
    </div>
  </div>
</footer>
<script src="/assets/js/main.js" defer></script>
{extra_foot}
</body>
</html>
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
    "rosary": ("", '<script src="/assets/js/rosary.js" defer></script>'),
    "saints-directory": ("", '<script src="/assets/js/saints-dir.js" defer></script>'),
    "find-a-church": (
        '<link rel="stylesheet" href="/assets/vendor/leaflet/leaflet.css">',
        '<script src="/assets/vendor/leaflet/leaflet.js"></script>\n<script src="/assets/js/map.js" defer></script>',
    ),
}


STATUS_LABEL = {"saint": "Saint", "blessed": "Blessed", "venerable": "Venerable", "servant": "Servant of God"}


STATUS_LABEL_ES = {"saint": ("Santo", "Santa"), "blessed": ("Beato", "Beata"), "venerable": ("Venerable", "Venerable"),
                   "servant": ("Siervo de Dios", "Sierva de Dios")}


def saints_html(lang="en"):
    es = lang == "es"
    data = json.loads((ROOT / "src" / "data" / ("saints_es.json" if es else "saints.json")).read_text(encoding="utf-8"))
    out = []
    for p in data:
        e = html.escape
        feast = f" &middot; {'Fiesta' if es else 'Feast'}: {e(p['feast'])}" if p.get("feast") else ""
        if es:
            fem = p["name"].startswith(("Santa ", "Beata ", "Sierva ")) or p["name"].startswith("Venerable") and p["name"].split()[1] in ("Mary", "Henriette")
            label = STATUS_LABEL_ES[p["status"]][1 if fem else 0]
        else:
            label = STATUS_LABEL[p["status"]]
        out.append(
            f'      <article class="card saint" data-status="{p["status"]}">'
            f'<span class="status s-{p["status"]}">{label}</span>'
            f'<h3>{e(p["name"])}</h3><span class="meta">{e(p["years"])}{feast}</span>'
            f'<p>{e(p["bio"])}</p><span class="meta" style="margin-top:.4rem">{e(p["tags"][0].upper() + p["tags"][1:])}</span></article>')
    return "\n".join(out)


def glossary_html(lang="en"):
    import unicodedata
    fold = lambda t: unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    data = json.loads((ROOT / "src" / "data" / ("glossary_es.json" if lang == "es" else "glossary.json")).read_text(encoding="utf-8"))
    data.sort(key=lambda t: fold(t[1]))
    out, letters, cur = [], [], None
    for slug, term, definition in data:
        L = fold(term)[0].upper()
        if L != cur:
            cur = L
            letters.append(L)
            out.append(f'    <div class="letter-head" id="letter-{L}">{L}</div>')
        out.append(f'    <dt id="{slug}">{html.escape(term)}</dt>\n    <dd>{html.escape(definition)}</dd>')
    alpha = "\n".join(f'    <a href="#letter-{L}">{L}</a>' for L in letters)
    return "\n".join(out), alpha


def _yr(d):
    if not d:
        return ""
    y = str(int(d[:4]))
    return ("c. " + y) if d.endswith("-01-01") else y


def _ordinal(n):
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


POPE_ES = {"Peter": "Pedro", "Linus": "Lino", "Anacletus": "Anacleto", "Clement": "Clemente", "Evaristus": "Evaristo",
           "Alexander": "Alejandro", "Sixtus": "Sixto", "Telesphorus": "Telesforo", "Hyginus": "Higinio", "Pius": "Pío",
           "Anicetus": "Aniceto", "Soter": "Sotero", "Eleutherius": "Eleuterio", "Victor": "Víctor", "Zephyrinus": "Ceferino",
           "Callixtus": "Calixto", "Urban": "Urbano", "Pontian": "Ponciano", "Anterus": "Antero", "Fabian": "Fabián",
           "Cornelius": "Cornelio", "Lucius": "Lucio", "Stephen": "Esteban", "Dionysius": "Dionisio", "Felix": "Félix",
           "Eutychian": "Eutiquiano", "Caius": "Cayo", "Marcellinus": "Marcelino", "Marcellus": "Marcelo", "Eusebius": "Eusebio",
           "Miltiades": "Melquíades", "Sylvester": "Silvestre", "Mark": "Marcos", "Julius": "Julio", "Liberius": "Liberio",
           "Damasus": "Dámaso", "Siricius": "Siricio", "Anastasius": "Anastasio", "Innocent": "Inocencio", "Zosimus": "Zósimo",
           "Boniface": "Bonifacio", "Celestine": "Celestino", "Leo": "León", "Hilarius": "Hilario", "Simplicius": "Simplicio",
           "Gelasius": "Gelasio", "Symmachus": "Símaco", "John": "Juan", "Agapetus": "Agapito", "Silverius": "Silverio",
           "Vigilius": "Vigilio", "Pelagius": "Pelagio", "Benedict": "Benedicto", "Gregory": "Gregorio", "Sabinian": "Sabiniano",
           "Adeodatus": "Adeodato", "Honorius": "Honorio", "Severinus": "Severino", "Theodore": "Teodoro", "Martin": "Martín",
           "Eugene": "Eugenio", "Vitalian": "Vitaliano", "Donus": "Dono", "Agatho": "Agatón", "Conon": "Conón", "Sergius": "Sergio",
           "Sisinnius": "Sisinio", "Constantine": "Constantino", "Zachary": "Zacarías", "Paul": "Pablo", "Adrian": "Adriano",
           "Paschal": "Pascual", "Valentine": "Valentín", "Nicholas": "Nicolás", "Marinus": "Marino", "Formosus": "Formoso",
           "Romanus": "Romano", "Lando": "Landón", "Francis": "Francisco"}
ROMAN = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII",
         "XIX", "XX", "XXI"]


def pope_name_es(n):
    n = n.replace("(the Great)", "Magno").replace("(1st time)", "(primera vez)").replace("(2nd time)", "(segunda vez)").replace("(3rd time)", "(tercera vez)")
    pre = ""
    for a, b in (("St. ", "San "), ("Bl. ", "Beato "), ("Ven. ", "Venerable ")):
        if n.startswith(a):
            pre, n = b, n[len(a):]
    n = " ".join(POPE_ES.get(w, w) for w in n.split(" "))
    return pre + n


def popes_html(lang="en"):
    es = lang == "es"
    rows = [l.split("\t") for l in (ROOT / "src" / "data" / "popes.tsv").read_text(encoding="utf-8").splitlines()
            if l and not l.startswith("#")]
    if es:
        tr = dict(l.split("\t", 1) for l in (ROOT / "src" / "data" / "popes_es.tsv").read_text(encoding="utf-8").splitlines() if l)
    e = html.escape
    yr = (lambda d: _yr(d).replace("c. ", "h. ")) if es else _yr
    out, cents, cur = [], [], None
    for ord_, name, bn, start, end, birth, death, summary in rows:
        n = int(ord_)
        if es:
            name, summary = pope_name_es(name), tr[ord_]
        c = (int(start[:4]) - 1) // 100 + 1
        if c != cur:
            if cur is not None:
                out.append("    </ol>")
            cur = c
            cents.append(c)
            head = f"Siglo {ROMAN[c]}" if es else f"{_ordinal(c)} century"
            out.append(f'    <h2 class="pope-cent" id="c{c}">{head}</h2>\n    <ol class="popes">')
        if n == 1:
            reign, life = ("h. años 30 &ndash; 64 o 67", "Mártir en Roma, 64 o 67") if es else ("c. 30s &ndash; 64 or 67", "Martyred in Rome, 64 or 67")
        else:
            a, b = yr(start), yr(end)
            reign = (f"{'desde' if es else 'since'} {a}" if not end else a if a == b else f"{a}&ndash;{b}")
            if not death:
                life = f"{'Nació en' if es else 'Born'} {yr(birth)}"
            elif birth:
                life = f"{'Vivió' if es else 'Lived'} {yr(birth)}&ndash;{yr(death)}"
            else:
                life = f"{'Murió en' if es else 'Died'} {yr(death)}"
        born = f'<span class="pope-bn">{"Nombre de pila:" if es else "Born"} {e(bn)}</span>' if bn else ""
        curcls = " current" if not end else ""
        out.append(
            f'      <li class="pope{curcls}" id="pope-{n}" value="{n}"><span class="pope-no" aria-hidden="true">{n}</span>'
            f'<div><h3>{e(name)}</h3>{born}'
            f'<p class="pope-meta"><span>{"Papa" if es else "Pope"} {reign}</span><span>{life}</span></p>'
            f'<p>{e(summary)}</p></div></li>')
    out.append("    </ol>")
    jump = "\n".join(f'    <a href="#c{c}">{ROMAN[c] if es else _ordinal(c)}</a>' for c in cents)
    return "\n".join(out), jump


POSE = {"stand": "Stand", "sit": "Sit", "kneel": "Kneel", "any": "As you wish"}


POSE_ES = {"stand": "De pie", "sit": "Sentados", "kneel": "De rodillas", "any": "Como prefieras"}
POSE_PT = {"stand": "De pé", "sit": "Sentados", "kneel": "De joelhos", "any": "Como preferir"}


LATIN_TEXT = {
    "en": ("Pray in Latin", "Latin is the Church&rsquo;s own language, and these are the words Catholics everywhere have prayed for centuries. You will still hear them at many parishes, in sung Masses and at Benediction. Latin is on the left, English on the right.",
           "How to say it", "Church Latin sounds a lot like Italian. Say every vowel; <em>ae</em> sounds like &ldquo;eh&rdquo;. <em>C</em> before e or i sounds like &ldquo;ch&rdquo; (<em>caelis</em>: CHEH-lees), <em>g</em> before e or i is soft as in &ldquo;gem&rdquo;, and <em>gn</em> sounds like &ldquo;ny&rdquo; (<em>regnum</em>: REH-nyoom). The accent marks show which syllable to stress.", "Latin"),
    "es": ("Reza en latín", "El latín es la lengua propia de la Iglesia, y estas son las palabras que los católicos de todo el mundo han rezado durante siglos. Todavía se oyen en muchas parroquias, en las Misas cantadas y en la Bendición con el Santísimo. El latín está a la izquierda y el español a la derecha.",
           "Cómo se pronuncia", "El latín de la Iglesia suena muy parecido al italiano. Pronuncia todas las vocales; <em>ae</em> suena como &ldquo;e&rdquo;. La <em>c</em> antes de e o i suena como &ldquo;ch&rdquo; (<em>caelis</em>: CHE-lis), la <em>g</em> antes de e o i suena como la <em>y</em> de &ldquo;yema&rdquo;, y <em>gn</em> suena como &ldquo;ñ&rdquo; (<em>regnum</em>: RE-ñum). Los acentos indican qué sílaba se pronuncia con más fuerza.", "Latín"),
    "pt": ("Reze em latim", "O latim é a língua própria da Igreja, e estas são as palavras que os católicos do mundo inteiro rezam há séculos. Você ainda as ouve em muitas paróquias, nas Missas cantadas e na Bênção do Santíssimo. O latim está à esquerda e o português à direita.",
           "Como pronunciar", "O latim da Igreja soa muito parecido com o italiano. Pronuncie todas as vogais; <em>ae</em> soa como &ldquo;é&rdquo;. O <em>c</em> antes de e ou i soa como &ldquo;tch&rdquo; (<em>caelis</em>: TCHÉ-lis), o <em>g</em> antes de e ou i soa como &ldquo;dj&rdquo;, e <em>gn</em> soa como &ldquo;nh&rdquo; (<em>regnum</em>: RÉ-nhum). Os acentos mostram a sílaba tônica.", "Latim"),
}
LANG_LABEL = {"en": "English", "es": "Español", "pt": "Português"}


def latin_html(lang="en"):
    data = json.loads((ROOT / "src" / "data" / "latin.json").read_text(encoding="utf-8"))
    head, lede, how_h, how, la_word = LATIN_TEXT[lang]
    cards = []
    for pr in data:
        cards.append(
            f'      <article class="card latin-prayer" id="{pr["id"]}">\n'
            f'        <h3><span lang="la">{html.escape(pr["la_title"])}</span> <span class="muted small">({html.escape(pr["title"][lang])})</span></h3>\n'
            f'        <div class="latin-cols">\n'
            f'          <div><p class="latin-label">{la_word}</p><p class="text" lang="la">{html.escape(pr["la"])}</p></div>\n'
            f'          <div><p class="latin-label">{LANG_LABEL[lang]}</p><p class="text">{html.escape(pr[lang])}</p></div>\n'
            f'        </div>\n      </article>')
    return (f'  <section class="section" id="latin">\n    <h2>{head}</h2>\n    <p class="muted prose">{lede}</p>\n'
            f'    <div class="note prose"><p><strong>{how_h}.</strong> {how}</p></div>\n'
            f'    <div class="latin-list">\n' + "\n".join(cards) + '\n    </div>\n  </section>')


def mass_html(lang="en"):
    name = "mass.json" if lang == "en" else f"mass_{lang}.json"
    steps = json.loads((ROOT / "src" / "data" / name).read_text(encoding="utf-8"))
    pose = {"en": POSE, "es": POSE_ES, "pt": POSE_PT}[lang]
    everyone = {"en": ("All", "You", "Catholic"), "es": ("Todos", "Tú", "Quien comulga"),
                "pt": ("Todos", "Você", "Quem comunga")}[lang]
    out, part = [], None
    for i, st in enumerate(steps, 1):
        if st["part"] != part:
            part = st["part"]
            out.append(f'    <h2 class="mass-part">{html.escape(part)}</h2>')
        say = ""
        if st["say"]:
            rows = "".join(
                f'<div class="say-row{" all" if who.startswith(everyone) else ""}"><dt>{html.escape(who)}</dt><dd>{html.escape(line)}</dd></div>'
                for who, line in st["say"])
            say = f'<dl class="say">{rows}</dl>'
        tip = f'<p class="mass-tip">{st["tip"]}</p>' if st["tip"] else ""
        out.append(
            f'    <section class="mass-step" id="step-{i}" data-part="{html.escape(part)}" data-step="{i}">'
            f'<div class="mass-head"><span class="pose pose-{st["pose"]}">{pose[st["pose"]]}</span>'
            f'<h3><span class="mass-no">{i}.</span> {html.escape(st["title"])}</h3></div>'
            f'<p>{html.escape(st["what"])}</p>{say}{tip}</section>')
    return "\n".join(out), len(steps)


def questions_html(lang="en"):
    es = lang == "es"
    data = json.loads((ROOT / "src" / "data" / ("questions_es.json" if es else "questions.json")).read_text(encoding="utf-8"))
    out = []
    for q in data:
        refs = []
        for ref in q["refs"]:
            if isinstance(ref, str):  # Spanish: a plain citation
                if ref.startswith("Catecismo"):
                    refs.append(f'<a href="https://www.vatican.va/archive/catechism_sp/index_sp.html" target="_blank" rel="noopener">{html.escape(ref)}</a>')
                else:
                    refs.append(html.escape(ref))
                continue
            label, target = ref
            if isinstance(target, int):
                url = f"https://www.scborromeo.org/ccc/para/{target}.htm"
            elif target.startswith("http"):
                url = target
            else:
                url = f"https://bible.usccb.org/bible/{target}"
            refs.append(f'<a href="{url}" target="_blank" rel="noopener">{html.escape(label)}</a>')
        if q.get("glossary"):
            refs.append(f'<a href="{"/es/glosario" if es else "/glossary"}#{q["glossary"]}">{"Glosario" if es else "Glossary"}</a>')
        body = "".join(f"<p>{para}</p>" for para in q["a"])
        summary = q["q"] if es else html.escape(q["q"])
        out.append(f'    <details class="qa" id="{q["id"]}"><summary>{summary}</summary>'
                   f'<div class="qa-body">{body}<p class="qa-refs">{"Para leer más" if es else "Read more"}: {" &middot; ".join(refs)}</p></div></details>')
    return "\n".join(out)


# ---------- Diocese directory (data: src/data/dioceses.json from Wikidata) ----------
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
RANK_LABEL = {4: "Saint", 3: "Blessed", 2: "Venerable", 1: "Servant of God"}
RANK_CLS = {4: "s-saint", 3: "s-blessed", 2: "s-venerable", 1: "s-servant"}


def load_dioceses():
    f = ROOT / "src" / "data" / "dioceses.json"
    return json.loads(f.read_text(encoding="utf-8"))


def dio_kind(d):
    n = d["short"].lower()
    if "military" in n:
        return "nationwide"
    if "eparchy" in n:
        return "eastern"
    return "latin"


def dio_leader(d):
    n = d["short"].lower()
    return "Archbishop" if n.startswith(("archdiocese", "archeparchy")) or " archeparchy" in n else "Bishop"


ABBR = dict(zip("Alabama Alaska Arizona Arkansas California Colorado Connecticut Delaware Florida Georgia Hawaii Idaho Illinois Indiana Iowa Kansas Kentucky Louisiana Maine Maryland Massachusetts Michigan Minnesota Mississippi Missouri Montana Nebraska Nevada New_Hampshire New_Jersey New_Mexico New_York North_Carolina North_Dakota Ohio Oklahoma Oregon Pennsylvania Rhode_Island South_Carolina South_Dakota Tennessee Texas Utah Vermont Virginia Washington West_Virginia Wisconsin Wyoming District_of_Columbia Puerto_Rico Guam".replace("_", "~").split(),
    "AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY DC PR GU".split()))
ABBR = {k.replace("~", " "): v for k, v in ABBR.items()}


ES_STATE = {"New York": "Nueva York", "New Jersey": "Nueva Jersey", "New Mexico": "Nuevo México", "North Carolina": "Carolina del Norte",
            "South Carolina": "Carolina del Sur", "North Dakota": "Dakota del Norte", "South Dakota": "Dakota del Sur",
            "Pennsylvania": "Pensilvania", "Hawaii": "Hawái", "Louisiana": "Luisiana", "Missouri": "Misuri", "Mississippi": "Misisipi",
            "Michigan": "Míchigan", "Oregon": "Oregón", "Virginia": "Virginia", "West Virginia": "Virginia Occidental",
            "District of Columbia": "Distrito de Columbia", "Kansas": "Kansas", "Tennessee": "Tennessee",
            "Northern Mariana Islands": "Islas Marianas del Norte", "American Samoa": "Samoa Americana",
            "U.S. Virgin Islands": "Islas Vírgenes de EE. UU.", "Puerto Rico": "Puerto Rico"}


def dio_place(d, lang="en"):
    es = lang == "es"
    name = (lambda x: ES_STATE.get(x, x)) if es else (lambda x: x)
    st = ", ".join(f"{name(x)} ({ABBR[x]})" if x in ABBR else name(x) for x in d["states"])
    if dio_kind(d) == "eastern":
        base = "Católica oriental, todo el país" if es else "Eastern Catholic, nationwide"
        if d.get("city") and st:
            base += f" ({'sede en' if es else 'based in'} {d['city']}, {', '.join(name(x) for x in d['states'])})"
        return base
    if dio_kind(d) == "nationwide":
        return "Todo el país" if es else "Nationwide"
    return st or ("Estados Unidos" if es else "United States")


def dio_name_es(n):
    for a, b in (("Archdiocese for the", "Arquidiócesis para los"), ("Archdiocese of", "Arquidiócesis de"), ("Diocese of", "Diócesis de")):
        if n.startswith(a):
            n = b + n[len(a):]
            break
    return n.replace("Military Services", "Servicios Militares").replace(" in California", ", California").replace(" in Florida", ", Florida")


def dio_rows(data, lang="en"):
    es = lang == "es"
    order = {"latin": 0, "eastern": 1, "nationwide": 2}
    ds = sorted(data["dioceses"], key=lambda d: (order[dio_kind(d)], d["states"][0] if d["states"] else "~", d["short"]))
    rows = []
    for d in ds:
        lead = html.escape(d.get("bishop", "")) or f'<span class="muted">{"Vacante o sin dato" if es else "Vacant or not recorded"}</span>'
        nm = dio_name_es(d["short"]) if es else d["short"]
        rows.append(f'          <tr><td><a href="/dioceses/{d["slug"]}">{html.escape(nm)}</a></td>'
                    f'<td>{html.escape(dio_place(d, lang))}</td><td>{lead}</td></tr>')
    return "\n".join(rows), len(ds)


def _domain(url):
    return re.sub(r"^https?://(www\.)?", "", url or "").split("/")[0]


def _since(x):
    m = re.match(r"(\d{4})-(\d{2})", x or "")
    return f"{MONTHS[int(m.group(2)) - 1]} {m.group(1)}" if m else ""


def diocese_body(d, data):
    e = html.escape
    kind = dio_kind(d)
    st = d["states"][0] if d["states"] else ""
    city = d.get("city", "")
    where = ", ".join(x for x in (city, st) if x)
    what = {"latin": "archdiocese" if d["short"].startswith("Archdiocese") else "diocese",
            "eastern": "Eastern Catholic eparchy", "nationwide": "nationwide jurisdiction"}[kind]
    lede = f"A Catholic {what}" + (f" based in {e(where)}" if where else "") + (f", founded in {d['founded']}" if d.get("founded") else "") + "."
    if kind == "eastern":
        lede += " Eparchies serve Eastern Catholics across a wide region, alongside the local Latin Church dioceses."
    lead = dio_leader(d)
    church = "eparchy" if kind == "eastern" else ("archdiocese" if d["short"].startswith("Archdiocese") else "diocese")
    out = ['<div class="page-head">\n  <div class="wrap">',
           f'    <p class="kicker"><a href="/dioceses">Dioceses</a> &rsaquo; {e(st or "United States")}</p>',
           f'    <h1>{e(d["short"])}</h1>',
           f'    <p class="lede">{lede}</p>',
           '  </div>\n</div>\n\n<div class="wrap">\n  <section class="section">\n    <div class="grid two">']
    if d.get("bishop"):
        since = _since(d.get("bishop_since"))
        out.append('      <div class="card">\n        <h3>Who leads it</h3>'
                   f'\n        <p><strong>{e(d["bishop"])}</strong>{", since " + since if since else ""}.</p>'
                   f'\n        <p class="small muted">From Wikidata. If a new {lead.lower()} was named recently, the {church} website will have it first.</p>\n      </div>')
    if d.get("website"):
        out.append('      <div class="card">\n        <h3>Official website</h3>'
                   '\n        <p>News, Mass times, schools, Catholic Charities, marriage preparation and contacts for every office.</p>'
                   f'\n        <div class="btn-row" style="justify-content:flex-start"><a class="btn" href="{e(d["website"])}" rel="noopener">{e(_domain(d["website"]))}</a></div>\n      </div>')
    if d.get("cathedral"):
        mp = (f' <a href="https://www.openstreetmap.org/?mlat={d["lat"]}&amp;mlon={d["lon"]}#map=17/{d["lat"]}/{d["lon"]}" rel="noopener">See it on a map</a>.'
              if d.get("lat") else "")
        town = f", {e(city)}" if city and city not in d["cathedral"] else ""
        out.append('      <div class="card">\n        <h3>Cathedral</h3>'
                   f'\n        <p><strong>{e(d["cathedral"])}</strong>{town}. The cathedral is the {lead.lower()}&rsquo;s own church and the mother church of the {church}.{mp}</p>\n      </div>')
    q = urllib.parse.quote(where or d["short"])
    dom = _domain(d.get("website"))
    near = f" near {e(city)}" if city and kind == "latin" else ""
    ocia = (f'\n          <a class="btn secondary" href="https://duckduckgo.com/?q={urllib.parse.quote("OCIA site:" + dom)}" rel="noopener">Search its website for OCIA</a>'
            if dom else "")
    out.append('      <div class="card">\n        <h3>Thinking of becoming Catholic?</h3>'
               '\n        <p>OCIA happens in parishes. Pick a parish near you, then call or email and ask when the next OCIA group starts. '
               f'The {church}&rsquo;s Office of Worship (sometimes called Evangelization or Christian Initiation) can help if a parish doesn&rsquo;t answer. <a href="/start-here">How OCIA works</a>.</p>'
               f'\n        <div class="btn-row" style="justify-content:flex-start">\n          <a class="btn" href="/find-a-church?ocia=1&amp;q={q}">Find parishes{near}</a>{ocia}\n        </div>\n      </div>')
    if d.get("members"):
        out.append('      <div class="card">\n        <h3>Size</h3>'
                   f'\n        <p>About <strong>{d["members"]:,}</strong> Catholics, according to the most recent figure in Wikidata.</p>\n      </div>')
    out.append("    </div>\n  </section>")

    holy = data["holy_by_state"].get(st, []) if kind == "latin" and st else []
    if holy:
        items = []
        for p in holy:
            yrs = f' <span class="small muted">({p["born"]}&ndash;{p["died"]})</span>' if p["born"] and p["died"] else ""
            items.append(f'<li><a href="/saints-directory?q={urllib.parse.quote(p["name"])}">{e(p["name"])}</a> '
                         f'<span class="status {RANK_CLS[p["rank"]]}">{RANK_LABEL[p["rank"]]}</span>{yrs}</li>')
        out.append(f'\n  <section class="section">\n    <h2>Holy men and women of {e(st)}</h2>'
                   f'\n    <p class="prose">Saints, Blesseds, Venerables and Servants of God who were born or died in {e(st)}. Some causes are led by this diocese; others by a neighboring diocese or a religious order.</p>'
                   f'\n    <ul class="holy-list">\n      ' + "\n      ".join(items) + '\n    </ul>'
                   '\n    <p class="small muted">Wikidata does not record every cause yet. <a href="/saints-directory">Search the full directory</a>.</p>\n  </section>')

    others = sorted((o for o in data["dioceses"] if o is not d and st and st in o["states"] and dio_kind(o) == "latin"),
                    key=lambda o: o["short"]) if kind == "latin" else []
    if others:
        links = " &middot; ".join(f'<a href="/dioceses/{o["slug"]}">{e(o["short"])}</a>' for o in others)
        out.append(f'\n  <section class="section">\n    <h2>Other dioceses in {e(st)}</h2>\n    <p>{links}</p>\n  </section>')

    refs = []
    if d.get("ch"):
        refs.append(f'<a href="https://www.catholic-hierarchy.org/diocese/d{e(d["ch"])}.html" rel="noopener">Catholic-Hierarchy</a>')
    if d.get("gc"):
        refs.append(f'<a href="https://gcatholic.org/dioceses/diocese/{e(d["gc"])}.htm" rel="noopener">GCatholic</a>')
    out.append('\n  <section class="section">'
               f'\n    <p class="small muted">History, parishes and statistics: {" &middot; ".join(refs) or "see the " + church + " website"}. '
               f'The details on this page come from <a href="https://www.wikidata.org/wiki/{d["qid"]}" rel="noopener">Wikidata</a> (updated {data["updated"]}), where anyone can correct them. <a href="/dioceses">All U.S. dioceses</a>.</p>'
               '\n  </section>\n</div>\n')
    return "\n".join(out)


def build_dioceses(data):
    out_dir = OUT / "dioceses"
    out_dir.mkdir(exist_ok=True)
    keep = set()
    for d in data["dioceses"]:
        title = f'{d["short"]}: Bishop, Cathedral, OCIA and Parishes | CatholicDoorway'
        st = ", ".join(d["states"])
        desc = (f'{d["short"]}{" (" + st + ")" if st else ""}: who leads it, its cathedral and website, '
                'how to find a parish and OCIA, and the holy men and women of the area.')
        page = HEAD.format(title=html.escape(title), desc=html.escape(desc), canonical=f"{DOMAIN}/dioceses/{d['slug']}",
                           domain=DOMAIN, slug="dioceses", door=DOOR_SVG, menu=MENU_SVG, theme=THEME_SVG,
                           nav=nav_html("dioceses"), extra_head="", alternates="",
                           lang_menu=lang_menu("en", {"en": f"/dioceses/{d['slug']}", "es": None, "pt": None}), **EN_TEXT)
        page += diocese_body(d, data) + FOOT.format(extra_foot="")
        (out_dir / f"{d['slug']}.html").write_text(bust(page), encoding="utf-8")
        keep.add(f"{d['slug']}.html")
    for old in out_dir.glob("*.html"):
        if old.name not in keep:
            old.unlink()
    print(f"built {len(keep)} diocese pages")
    return sorted(d["slug"] for d in data["dioceses"])


def version(rel):
    """Short content hash so browsers fetch new CSS/JS as soon as it changes."""
    return hashlib.sha1((OUT / rel.lstrip("/")).read_bytes()).hexdigest()[:10]


def bust(page):
    for rel in ("/assets/css/style.css", "/assets/js/main.js", "/assets/js/map.js", "/assets/js/rosary.js", "/assets/js/saints-dir.js"):
        page = page.replace(f'"{rel}"', f'"{rel}?v={version(rel)}"')
    return page


def nav_html(current):
    items = []
    for slug, label, *_ in PAGES:
        if slug in NAV_EXCLUDE:
            continue
        href = "/" if slug == "index" else f"/{slug}"
        cur = ' aria-current="page"' if slug == current else ""
        subs = SUBNAV.get(slug)
        if subs:
            if current in [s for s, _ in subs]:
                cur = ' class="in-section"'
            sub = "".join(
                f'<li><a href="/{s}"{" aria-current=\"page\"" if s == current else ""}>{l}</a></li>' for s, l in subs)
            items.append(f'        <li class="has-sub"><a href="{href}"{cur}>{label}</a><ul class="sub">{sub}</ul></li>')
            continue
        items.append(f'        <li><a href="{href}"{cur}>{label}</a></li>')
    return "\n".join(items)


ES_SUBNAV = {"comenzar": [("comenzar", "Hacerse católico (OCIA)"), ("primera-misa", "Tu primera Misa"), ("guias", "Guías prácticas"),
                          ("confesion", "Cómo confesarse"), ("volver", "Volver a la Iglesia")],
             "oraciones": [("oraciones", "Oraciones católicas"), ("rosario", "Reza el Rosario")],
             "biblia": [("biblia", "Las lecturas de hoy y la Biblia"), ("calendario", "Calendario de días santos")],
             "creencias": [("creencias", "Lo que creen los católicos"), ("preguntas", "Preguntas sinceras"), ("glosario", "Glosario")],
             "estructura": [("estructura", "Cómo se organiza la Iglesia"), ("papas", "Los 267 Papas"), ("diocesis", "Las diócesis de EE. UU."),
                            ("buscar-iglesia", "Buscar una iglesia")]}
ES_SUB_CHILDREN = {c for subs in ES_SUBNAV.values() for c, _ in subs} - set(ES_SUBNAV)
# Spanish pages reached from a hub page rather than the top menu
ES_NAV_EXCLUDE = {"inscribirse-parroquia", "bautismo", "matrimonio", "uncion", "funerales", "fe-de-bautismo"}


def lang_nav(code, pages, subnav, exclude, current):
    children = {c for subs in subnav.values() for c, _ in subs} - set(subnav)
    items = []
    for _, sl, label, *_ in pages:
        if sl in children or sl in exclude:
            continue
        href = f"/{code}/" if sl == "index" else f"/{code}/{sl}"
        cur = ' aria-current="page"' if sl == current else ""
        subs = subnav.get(sl)
        if subs:
            if current in [c for c, _ in subs]:
                cur = ' class="in-section"'
            sub = "".join(f'<li><a href="/{code}/{c}"{" aria-current=\"page\"" if c == current else ""}>{l}</a></li>' for c, l in subs)
            items.append(f'        <li class="has-sub"><a href="{href}"{cur}>{label}</a><ul class="sub">{sub}</ul></li>')
            continue
        items.append(f'        <li><a href="{href}"{cur}>{label}</a></li>')
    return "\n".join(items)


def es_nav(current):
    return lang_nav("es", ES_PAGES, ES_SUBNAV, ES_NAV_EXCLUDE, current)


LOCALE = {"es": "es_US", "pt": "pt_BR"}


def build_lang(code, pages, text, foot, subnav, exclude):
    out_dir = OUT / code
    out_dir.mkdir(exist_ok=True)
    for en, sl, label, title, desc in pages:
        body = (PAGES_DIR / code / f"{sl}.html").read_text(encoding="utf-8")
        url = f"/{code}/" if sl == "index" else f"/{code}/{sl}"
        urls = lang_urls(en)
        eh, ef = EXTRA.get(en, ("", ""))
        page = HEAD.format(title=title, desc=desc, canonical=DOMAIN + url, domain=DOMAIN,
                           slug=en, door=DOOR_SVG, menu=MENU_SVG, theme=THEME_SVG,
                           nav=lang_nav(code, pages, subnav, exclude, sl), extra_head=eh,
                           alternates=alternates_html(urls), lang_menu=lang_menu(code, urls), **text)
        page = page.replace('<meta property="og:site_name" content="CatholicDoorway">',
                            f'<meta property="og:site_name" content="CatholicDoorway">\n<meta property="og:locale" content="{LOCALE[code]}">')
        body = body.replace("{{DOOR}}", DOOR_SVG)
        if "{{QUESTIONS}}" in body:
            body = body.replace("{{QUESTIONS}}", questions_html(code))
        if "{{SAINTS}}" in body:
            body = body.replace("{{SAINTS}}", saints_html(code))
        if "{{DIOCESES}}" in body:
            dd = load_dioceses()
            rows, n = dio_rows(dd, code)
            body = body.replace("{{DIOCESES}}", rows).replace("{{DIOCESE_COUNT}}", str(n)).replace("{{DIOCESE_UPDATED}}", dd["updated"])
        if "{{POPES}}" in body:
            pl, pj = popes_html(code)
            body = body.replace("{{POPES}}", pl).replace("{{CENTURIES}}", pj)
        if "{{GLOSSARY}}" in body:
            g, a = glossary_html(code)
            body = body.replace("{{GLOSSARY}}", g).replace("{{ALPHA}}", a)
        if "{{LATIN}}" in body:
            body = body.replace("{{LATIN}}", latin_html(code))
        if "{{MASS}}" in body:
            ms, mn = mass_html(code)
            body = body.replace("{{MASS}}", ms).replace("{{MASS_COUNT}}", str(mn))
        page += body + foot.format(extra_foot=ef)
        (out_dir / f"{sl}.html").write_text(bust(page), encoding="utf-8")
        print(f"built {code}/{sl}")


def build_es():
    build_lang("es", ES_PAGES, ES_TEXT, FOOT_ES, ES_SUBNAV, ES_NAV_EXCLUDE)


def build_pt():
    build_lang("pt", PT_PAGES, PT_TEXT, FOOT_PT, PT_SUBNAV, PT_NAV_EXCLUDE)


def main():
    dio_data = load_dioceses()
    for slug, label, title, desc in PAGES:
        body = (PAGES_DIR / f"{slug}.html").read_text(encoding="utf-8")
        canonical = DOMAIN + ("/" if slug == "index" else f"/{slug}")
        eh, ef = EXTRA.get(slug, ("", ""))
        urls = lang_urls(None if slug == "404" else slug)
        page = HEAD.format(title=title, desc=desc, canonical=canonical, domain=DOMAIN,
                           slug=slug, door=DOOR_SVG, menu=MENU_SVG, theme=THEME_SVG,
                           nav=nav_html(slug), extra_head=eh, alternates=alternates_html(urls),
                           lang_menu=lang_menu("en", urls), **EN_TEXT)
        body = body.replace("{{DOOR}}", DOOR_SVG)
        if "{{SAINTS}}" in body:
            body = body.replace("{{SAINTS}}", saints_html())
        if "{{GLOSSARY}}" in body:
            g, a = glossary_html()
            body = body.replace("{{GLOSSARY}}", g).replace("{{ALPHA}}", a)
        if "{{LATIN}}" in body:
            body = body.replace("{{LATIN}}", latin_html())
        if "{{MASS}}" in body:
            ms, mn = mass_html()
            body = body.replace("{{MASS}}", ms).replace("{{MASS_COUNT}}", str(mn))
        if "{{QUESTIONS}}" in body:
            body = body.replace("{{QUESTIONS}}", questions_html())
        if "{{DIOCESES}}" in body:
            rows, n = dio_rows(dio_data)
            body = body.replace("{{DIOCESES}}", rows).replace("{{DIOCESE_COUNT}}", str(n)).replace("{{DIOCESE_UPDATED}}", dio_data["updated"])
        if "{{POPES}}" in body:
            pl, pj = popes_html()
            body = body.replace("{{POPES}}", pl).replace("{{CENTURIES}}", pj)
        page += body
        page += FOOT.format(extra_foot=ef)
        (OUT / f"{slug}.html").write_text(bust(page), encoding="utf-8")
        print("built", slug)

    build_es()
    build_pt()
    dio_slugs = build_dioceses(dio_data)

    today = datetime.date.today().isoformat()
    urls = "\n".join(
        f"  <url><loc>{DOMAIN}{'/' if s == 'index' else '/' + s}</loc><lastmod>{today}</lastmod></url>"
        for s, *_ in PAGES if s != "404")
    urls += "\n" + "\n".join(
        f"  <url><loc>{DOMAIN}/es/{'' if es == 'index' else es}</loc><lastmod>{today}</lastmod></url>"
        for _, es, *_ in ES_PAGES)
    urls += "\n" + "\n".join(
        f"  <url><loc>{DOMAIN}/pt/{'' if pt == 'index' else pt}</loc><lastmod>{today}</lastmod></url>"
        for _, pt, *_ in PT_PAGES)
    urls += "\n" + "\n".join(f"  <url><loc>{DOMAIN}/dioceses/{s}</loc><lastmod>{today}</lastmod></url>" for s in dio_slugs)
    (OUT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n',
        encoding="utf-8")


if __name__ == "__main__":
    main()
