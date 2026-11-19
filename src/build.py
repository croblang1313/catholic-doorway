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
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import features  # noqa: E402

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
    ("examination-of-conscience", "Examination of Conscience", "Examination of Conscience for Kids, Teens and Adults | CatholicDoorway",
     "A Catholic examination of conscience before Confession, in versions for kids, teens and adults. Tick what applies and make a private list on your phone."),
    ("ocia-listing", "List Your Parish's OCIA", "List Your Parish's OCIA Program | CatholicDoorway",
     "Parish OCIA coordinators: add your contact so people exploring the Catholic faith near you know who to call. Free, reviewed before publishing."),
    ("find-a-church", "Find a Church", "Find a Catholic Church Near You | CatholicDoorway",
     "Find Catholic churches near you on a free map built from OpenStreetMap, with address, phone, website and directions."),
    ("prayers", "Prayers", "Catholic Prayers and How to Pray the Rosary | CatholicDoorway",
     "Traditional Catholic prayers, from the Our Father and Hail Mary to the Memorare, plus a step-by-step guide to the Rosary."),
    ("rosary", "Pray the Rosary", "Pray the Rosary Online, Bead by Bead | CatholicDoorway",
     "An interactive Rosary: tap through each bead with the prayers, today's mysteries and their Scripture passages. Free, no app needed."),
    ("devotions", "Devotions", "Catholic Devotions and Prayer Reminders | CatholicDoorway",
     "The best-loved Catholic devotions with the words to pray: the Rosary, Divine Mercy Chaplet, Stations of the Cross, novenas and the Angelus, with free calendar reminders."),
    ("divine-mercy-chaplet", "Divine Mercy Chaplet", "How to Pray the Divine Mercy Chaplet, Step by Step | CatholicDoorway",
     "Pray the Divine Mercy Chaplet bead by bead on your phone: the prayers for each decade, the 3 p.m. Hour of Mercy and the Divine Mercy Novena."),
    ("stations-of-the-cross", "Stations of the Cross", "Stations of the Cross: Pray All 14 Stations | CatholicDoorway",
     "Pray the Stations of the Cross with a short Scripture reference, reflection and prayer for each of the 14 stations, one station at a time on your phone."),
    ("novenas", "Novenas", "Catholic Novenas and This Year's Dates | CatholicDoorway",
     "How to pray a novena, with prayers and this year's dates for novenas to St. Joseph, the Holy Spirit, Divine Mercy, the Sacred Heart, Our Lady of Guadalupe and more."),
    ("angelus", "The Angelus", "The Angelus and Regina Caeli Prayers | CatholicDoorway",
     "The words of the Angelus, prayed at 6 a.m., noon and 6 p.m., and the Regina Caeli for the Easter season, with a free daily reminder."),
    ("liturgy-of-the-hours", "Liturgy of the Hours", "Liturgy of the Hours: Today's Morning and Evening Prayer | CatholicDoorway",
     "Pray today's Morning, Evening and Night Prayer of the Liturgy of the Hours, and learn how the Divine Office works and how to begin."),
    ("bible", "Bible & Readings", "The Bible and Today's Mass Readings | CatholicDoorway",
     "Today's Catholic Mass readings, how the Catholic Bible is arranged, and where to read it free online."),
    ("calendar", "Holy Days Calendar", "Catholic Holy Days of Obligation and Fasting Calendar | CatholicDoorway",
     "Holy days of obligation, fasting days and major Catholic feasts for the U.S., with a free calendar you can add to your iPhone, Google or Outlook."),
    ("beliefs", "Beliefs", "What Catholics Believe | CatholicDoorway",
     "A plain-language overview of Catholic belief and practice: the Creed, the seven sacraments, Scripture and Tradition, Mary and the saints, and the moral life."),
    ("questions", "Honest Questions", "Honest Questions About the Catholic Church, Answered | CatholicDoorway",
     "Short, kind, straight answers to the questions people ask about Catholics: Mary, saints, confession, the Pope, purgatory, the extra Bible books and more."),
    ("church-documents", "Catechism & Documents", "Catechism of the Catholic Church and Major Church Documents | CatholicDoorway",
     "Look up any paragraph of the Catechism, browse it by topic, and search the major encyclicals, apostolic letters and Vatican II documents, with links to the official texts."),
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
NAV_EXCLUDE = {"examination-of-conscience", "ocia-listing", "devotions", "divine-mercy-chaplet", "stations-of-the-cross", "novenas", "angelus", "liturgy-of-the-hours", "church-documents", "about", "404", "saints-directory", "how-to", "confession", "coming-back", "join-a-parish", "baptism", "marriage", "anointing", "funerals", "baptism-certificate", "popes", "dioceses", "find-a-church", "first-mass", "calendar", "rosary", "questions"}
# Pages shown in a dropdown under a main menu item: parent slug -> [(slug, label)]
SUBNAV = {"beliefs": [("beliefs", "What Catholics believe"), ("questions", "Honest questions, answered"),
                      ("church-documents", "Catechism and Church documents")],
          "prayers": [("prayers", "Catholic prayers"), ("rosary", "Pray the Rosary"), ("devotions", "Devotions and reminders"),
                      ("liturgy-of-the-hours", "Liturgy of the Hours")],
          "bible": [("bible", "Today’s readings and the Bible"), ("calendar", "Holy Days Calendar")],
          "start-here": [("start-here", "Becoming Catholic (OCIA)"), ("first-mass", "Your First Mass"),
                         ("how-to", "How-To Guides"), ("confession", "How to go to Confession"),
                         ("examination-of-conscience", "Examination of conscience"), ("coming-back", "Coming back to the Church")],
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
    ("examination-of-conscience", "examen-de-conciencia", "Examen de conciencia", "Examen de conciencia para niños, adolescentes y adultos | CatholicDoorway",
     "Un examen de conciencia católico para antes de confesarse, en versiones para niños, adolescentes y adultos. Marca lo que aplique y haz una lista privada en tu teléfono."),
    ("devotions", "devociones", "Devociones", "Devociones católicas y recordatorios de oración | CatholicDoorway",
     "Las devociones católicas más queridas con sus oraciones: el Rosario, la Coronilla de la Divina Misericordia, el Vía Crucis, las novenas y el Ángelus, con recordatorios gratis en tu calendario."),
    ("divine-mercy-chaplet", "coronilla-de-la-divina-misericordia", "Coronilla de la Divina Misericordia", "Cómo rezar la Coronilla de la Divina Misericordia, paso a paso | CatholicDoorway",
     "Reza la Coronilla de la Divina Misericordia cuenta por cuenta en tu teléfono: las oraciones de cada decena, la Hora de la Misericordia y la novena."),
    ("stations-of-the-cross", "via-crucis", "Vía Crucis", "Vía Crucis: reza las 14 estaciones | CatholicDoorway",
     "Reza el Vía Crucis con una cita bíblica, una reflexión y una oración para cada una de las 14 estaciones, una a la vez en tu teléfono."),
    ("novenas", "novenas", "Novenas", "Novenas católicas y sus fechas de este año | CatholicDoorway",
     "Cómo rezar una novena, con oraciones y las fechas de este año de las novenas a San José, al Espíritu Santo, a la Divina Misericordia, al Sagrado Corazón, a la Virgen de Guadalupe y más."),
    ("angelus", "angelus", "El Ángelus", "El Ángelus y el Regina Caeli | CatholicDoorway",
     "Las palabras del Ángelus, que se reza a las 6 de la mañana, al mediodía y a las 6 de la tarde, y el Regina Caeli del tiempo de Pascua, con un recordatorio diario gratis."),
    ("liturgy-of-the-hours", "liturgia-de-las-horas", "Liturgia de las Horas", "Liturgia de las Horas: Laudes y Vísperas de hoy | CatholicDoorway",
     "Reza hoy Laudes, Vísperas y Completas de la Liturgia de las Horas, y aprende cómo funciona el Oficio Divino y cómo empezar."),
    ("church-documents", "documentos-de-la-iglesia", "Catecismo y documentos", "El Catecismo de la Iglesia Católica y los grandes documentos de la Iglesia | CatholicDoorway",
     "Busca cualquier número del Catecismo, recórrelo por temas y busca entre las grandes encíclicas, cartas apostólicas y documentos del Vaticano II, con enlaces a los textos oficiales."),
    ("ocia-listing", "registrar-ocia", "Registra tu OCIA", "Registra el OCIA de tu parroquia | CatholicDoorway",
     "Coordinadores de OCIA: añadan su contacto para que quienes se acercan a la fe católica cerca de ustedes sepan a quién llamar. Gratis y revisado antes de publicarse."),
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
    ("saints-directory", "directorio-santos", "Directorio de santos", "Directorio de santos y causas: Santos, Beatos, Venerables y Siervos de Dios | CatholicDoorway",
     "Busca entre miles de Santos, Beatos, Venerables y Siervos de Dios por nombre, país, siglo y patronazgo. Se actualiza cada semana."),
    ("about", "acerca", "Acerca del sitio", "Acerca de CatholicDoorway",
     "Acerca de CatholicDoorway.com: una guía gratuita y sin anuncios de la fe católica. Fuentes, datos, privacidad y correcciones."),
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
    ("examination-of-conscience", "exame-de-consciencia", "Exame de consciência", "Exame de consciência para crianças, adolescentes e adultos | CatholicDoorway",
     "Um exame de consciência católico para antes da Confissão, em versões para crianças, adolescentes e adultos. Marque o que se aplica e faça uma lista privada no celular."),
    ("devotions", "devocoes", "Devoções", "Devoções católicas e lembretes de oração | CatholicDoorway",
     "As devoções católicas mais queridas com as suas orações: o Rosário, o Terço da Misericórdia, a Via-Sacra, as novenas e o Angelus, com lembretes gratuitos no seu calendário."),
    ("divine-mercy-chaplet", "terco-da-misericordia", "Terço da Misericórdia", "Como rezar o Terço da Misericórdia, passo a passo | CatholicDoorway",
     "Reze o Terço da Misericórdia conta por conta no celular: as orações de cada dezena, a Hora da Misericórdia e a novena."),
    ("stations-of-the-cross", "via-sacra", "Via-Sacra", "Via-Sacra: reze as 14 estações | CatholicDoorway",
     "Reze a Via-Sacra com uma citação bíblica, uma reflexão e uma oração para cada uma das 14 estações, uma de cada vez no celular."),
    ("novenas", "novenas", "Novenas", "Novenas católicas e as datas deste ano | CatholicDoorway",
     "Como rezar uma novena, com orações e as datas deste ano das novenas a São José, ao Espírito Santo, à Divina Misericórdia, ao Sagrado Coração, a Nossa Senhora de Guadalupe e mais."),
    ("angelus", "angelus", "O Angelus", "O Angelus e a Rainha do Céu (Regina Caeli) | CatholicDoorway",
     "As palavras do Angelus, rezado às 6 da manhã, ao meio-dia e às 6 da tarde, e a Rainha do Céu do Tempo Pascal, com um lembrete diário gratuito."),
    ("liturgy-of-the-hours", "liturgia-das-horas", "Liturgia das Horas", "Liturgia das Horas: Laudes e Vésperas de hoje | CatholicDoorway",
     "Reze hoje as Laudes, as Vésperas e as Completas da Liturgia das Horas, e entenda como funciona o Ofício Divino e como começar."),
    ("church-documents", "documentos-da-igreja", "Catecismo e documentos", "O Catecismo da Igreja Católica e os grandes documentos da Igreja | CatholicDoorway",
     "Procure qualquer parágrafo do Catecismo, percorra-o por temas e pesquise as grandes encíclicas, cartas apostólicas e documentos do Vaticano II, com links para os textos oficiais."),
    ("ocia-listing", "cadastrar-ocia", "Cadastre a sua OCIA", "Cadastre a OCIA da sua paróquia | CatholicDoorway",
     "Coordenadores da OCIA: adicionem o seu contato para que quem está conhecendo a fé católica perto de vocês saiba para quem ligar. Gratuito e revisado antes de ser publicado."),
    ("prayers", "oracoes", "Orações", "Orações católicas e como rezar o Rosário | CatholicDoorway",
     "As orações católicas tradicionais em português: o Pai-Nosso, a Ave-Maria, o Creio, a Salve-Rainha e mais, com um guia do Rosário."),
    ("rosary", "rosario", "Reze o Rosário", "Reze o Rosário on-line, conta por conta | CatholicDoorway",
     "Reze o Rosário passo a passo no seu celular: as contas se acendem, cada mistério traz sua passagem bíblica e o lugar onde você parou fica guardado."),
    ("beliefs", "crencas", "Crenças", "No que os católicos acreditam | CatholicDoorway",
     "Um resumo simples da fé e da prática católica: o Credo, os sete sacramentos, a Escritura e a Tradição, Maria e os santos, e a vida moral."),
    ("find-a-church", "encontrar-igreja", "Encontrar uma igreja", "Encontre uma igreja católica perto de você | CatholicDoorway",
     "Procure igrejas católicas nos Estados Unidos por cidade ou ZIP code: endereço, telefone, site e como chegar."),
    ("how-to", "guias", "Guias práticos", "Guias católicos práticos: Confissão, Batismo, Matrimônio e mais | CatholicDoorway",
     "Guias católicos simples e práticos: confessar-se, inscrever-se numa paróquia, batizar um filho, casar na Igreja, a Unção dos Enfermos, funerais e voltar para a Igreja."),
    ("confession", "confissao", "Confissão", "Como se confessar: guia passo a passo | CatholicDoorway",
     "Como fazer uma boa confissão: quando e onde, como se preparar, o que dizer exatamente e o que fazer se faz muitos anos."),
    ("coming-back", "voltar", "Voltar para a Igreja", "Voltar para a Igreja Católica | CatholicDoorway",
     "Afastou-se da Igreja? Como voltar: a Missa, conversar com um padre, a Confissão e casos especiais, como um casamento fora da Igreja."),
    ("join-a-parish", "inscrever-se-paroquia", "Inscrever-se numa paróquia", "Como se inscrever numa paróquia católica nos EUA | CatholicDoorway",
     "Por que e como se inscrever numa paróquia católica nos Estados Unidos, e em que isso ajuda: cartas para padrinhos, batizados, casamentos e escola católica."),
    ("baptism", "batismo", "Batismo", "Como batizar o seu filho na Igreja Católica | CatholicDoorway",
     "Como funciona o Batismo de um bebê numa paróquia católica: quando ligar, a preparação, os requisitos dos padrinhos, a cerimônia e os casos especiais."),
    ("marriage", "matrimonio", "Matrimônio", "Como casar na Igreja Católica | CatholicDoorway",
     "Casar na Igreja: com quanta antecedência começar, a preparação, os documentos, casar com alguém não católico, casamentos anteriores e convalidação."),
    ("anointing", "uncao", "Unção dos Enfermos", "A Unção dos Enfermos e os últimos sacramentos | CatholicDoorway",
     "Quando e como chamar um padre para a Unção dos Enfermos ou os últimos sacramentos, o que são e o que fazer se alguém está morrendo agora."),
    ("funerals", "funeral", "Funeral", "Como preparar um funeral católico | CatholicDoorway",
     "Como preparar um funeral católico: o velório, a Missa de exéquias e o sepultamento, as normas sobre a cremação, os custos e as Missas pelos falecidos."),
    ("baptism-certificate", "certidao-de-batismo", "Certidão de batismo", "Como pedir a sua certidão de batismo católica | CatholicDoorway",
     "Como pedir a sua certidão de batismo com as anotações para um casamento ou para ser padrinho, mesmo se a paróquia fechou ou você foi batizado no Brasil ou em Portugal."),
    ("bible", "biblia", "Bíblia", "A Bíblia e as leituras da Missa de hoje | CatholicDoorway",
     "As leituras da Missa de hoje em português, como a Bíblia católica é organizada e por onde começar a ler."),
    ("calendar", "calendario", "Calendário", "Dias santos de guarda e de jejum: calendário católico | CatholicDoorway",
     "Os dias santos de guarda, os dias de jejum e as festas principais nos Estados Unidos, com um calendário gratuito em português para o seu iPhone, Google ou Outlook."),
    ("questions", "perguntas", "Perguntas sinceras", "Perguntas sinceras sobre a Igreja Católica, respondidas | CatholicDoorway",
     "Respostas breves, gentis e claras ao que as pessoas perguntam sobre os católicos: Maria, os santos, a confissão, o Papa, o purgatório e mais."),
    ("glossary", "glossario", "Glossário", "Glossário católico: palavras explicadas | CatholicDoorway",
     "Definições simples das palavras católicas, de Absolvição a Vaticano."),
    ("structure", "estrutura", "A Igreja", "Como a Igreja Católica é organizada | CatholicDoorway",
     "Como a Igreja Católica é organizada: o Papa, os bispos, as dioceses, as paróquias, os padres e os diáconos, explicado com simplicidade."),
    ("popes", "papas", "Os Papas", "Os 267 Papas, de São Pedro a Leão XIV | CatholicDoorway",
     "Todos os Papas em ordem, de São Pedro a Leão XIV: o lugar de cada um na sucessão, os anos de pontificado e o motivo pelo qual é lembrado."),
    ("dioceses", "dioceses", "Dioceses", "As dioceses católicas dos Estados Unidos | CatholicDoorway",
     "Todas as dioceses, arquidioceses e eparquias católicas dos Estados Unidos: o bispo, a catedral, o site e ajuda para começar a OCIA."),
    ("saints", "santos", "Santos", "Santos, Beatos e Veneráveis católicos | CatholicDoorway",
     "Conheça os santos e o caminho para a santidade: Servo de Deus, Venerável, Beato e Santo."),
    ("saints-directory", "diretorio-santos", "Diretório de santos", "Diretório de santos e causas: Santos, Beatos, Veneráveis e Servos de Deus | CatholicDoorway",
     "Pesquise entre milhares de Santos, Beatos, Veneráveis e Servos de Deus por nome, país, século e padroado. Atualizado toda semana."),
    ("about", "sobre", "Sobre o site", "Sobre o CatholicDoorway",
     "Sobre o CatholicDoorway.com: um guia gratuito e sem anúncios da fé católica. Fontes, dados, privacidade e correções."),
]
PT_TEXT = dict(lang="pt", skip="Pular para o conteúdo", home="/pt/", home_label="Início do CatholicDoorway",
               theme_label="Mudar para o modo claro ou escuro", menu_label="Menu", nav_label="Principal")
EN_TO_PT = {en: pt for en, pt, *_ in PT_PAGES}
PT_SUBNAV = {"comecar": [("comecar", "Tornar-se católico (OCIA)"), ("primeira-missa", "Sua primeira Missa"), ("guias", "Guias práticos"),
                         ("confissao", "Como se confessar"), ("exame-de-consciencia", "Exame de consciência"), ("voltar", "Voltar para a Igreja")],
             "oracoes": [("oracoes", "Orações católicas"), ("rosario", "Reze o Rosário"), ("devocoes", "Devoções e lembretes"),
                         ("liturgia-das-horas", "Liturgia das Horas")],
             "biblia": [("biblia", "As leituras de hoje e a Bíblia"), ("calendario", "Calendário de dias santos")],
             "crencas": [("crencas", "No que os católicos acreditam"), ("perguntas", "Perguntas sinceras"), ("glossario", "Glossário"),
                         ("documentos-da-igreja", "O Catecismo e os documentos")],
             "santos": [("santos", "Conheça os santos"), ("diretorio-santos", "Diretório de santos e causas")],
             "estrutura": [("estrutura", "Como a Igreja é organizada"), ("papas", "Os 267 Papas"), ("dioceses", "As dioceses dos EUA"),
                           ("encontrar-igreja", "Encontrar uma igreja")]}
# Portuguese pages reached from a hub page rather than the top menu
PT_NAV_EXCLUDE = {"terco-da-misericordia", "via-sacra", "novenas", "angelus", "cadastrar-ocia", "sobre", "inscrever-se-paroquia", "batismo", "matrimonio", "uncao", "funeral", "certidao-de-batismo"}

# Filipino (Tagalog): en_slug, tl_slug, nav label, <title>, meta description
TL_PAGES = [
    ("index", "index", "Tahanan", "CatholicDoorway sa Filipino: isang libreng gabay sa pananampalatayang Katoliko",
     "Isang simple at libreng gabay sa pananampalatayang Katoliko: mga dasal, paano maging Katoliko (OCIA), ang iyong unang Misa, ang Rosaryo at paghahanap ng simbahan sa Estados Unidos."),
    ("start-here", "magsimula", "Maging Katoliko", "Paano maging Katoliko: ang OCIA, hakbang-hakbang | CatholicDoorway",
     "Interesado sa Simbahang Katolika? Paano gumagana ang OCIA, ang apat na yugto nito, gaano katagal, sino ang kakausapin at ano ang aasahan sa iyong unang Misa."),
    ("first-mass", "unang-misa", "Ang iyong unang Misa", "Ang iyong unang Misa, hakbang-hakbang | CatholicDoorway",
     "Unang beses mong magsisimba? Isang gabay sa iyong telepono: kailan tatayo, uupo at luluhod, ano ang isasagot ng mga tao at ano ang gagawin sa Komunyon."),
    ("how-to", "mga-gabay", "Mga praktikal na gabay", "Mga praktikal na gabay Katoliko: Kumpisal, Binyag, Kasal at iba pa | CatholicDoorway",
     "Simple at praktikal na mga gabay Katoliko: pangungumpisal, pagpapatala sa parokya, pagpapabinyag sa anak, pagpapakasal sa Simbahan, Pagpapahid ng Langis, libing at pagbabalik sa Simbahan."),
    ("confession", "kumpisal", "Kumpisal", "Paano mangumpisal: gabay na hakbang-hakbang | CatholicDoorway",
     "Paano mangumpisal nang mabuti: kailan at saan, paano maghanda, ano mismo ang sasabihin at ano ang gagawin kung matagal ka nang hindi nakapangungumpisal."),
    ("coming-back", "pagbabalik", "Pagbabalik sa Simbahan", "Pagbabalik sa Simbahang Katolika | CatholicDoorway",
     "Matagal kang nawalay sa Simbahan? Paano bumalik: ang Misa, pakikipag-usap sa pari, ang Kumpisal at mga espesyal na kalagayan gaya ng kasal sa labas ng Simbahan."),
    ("join-a-parish", "magpatala-sa-parokya", "Magpatala sa parokya", "Paano magpatala sa isang parokyang Katoliko sa Estados Unidos | CatholicDoorway",
     "Bakit at paano magpatala sa isang parokyang Katoliko sa Estados Unidos, at saan ito nakatutulong: sulat para sa ninong o ninang, binyag, kasal at paaralang Katoliko."),
    ("baptism", "binyag", "Binyag", "Paano ipabinyag ang iyong anak sa Simbahang Katolika | CatholicDoorway",
     "Paano ang binyag ng sanggol sa isang parokyang Katoliko: kailan tatawag, ang seminar, ang mga kailangan sa ninong at ninang, ang seremonya at mga espesyal na kalagayan."),
    ("marriage", "kasal", "Kasal", "Paano magpakasal sa Simbahang Katolika | CatholicDoorway",
     "Pagpapakasal sa Simbahan: gaano kaaga magsisimula, ang paghahanda sa kasal, ang mga dokumento, pagpapakasal sa hindi Katoliko, naunang kasal at kumbalidasyon."),
    ("anointing", "pagpapahid-ng-langis", "Pagpapahid ng Langis sa Maysakit", "Ang Pagpapahid ng Langis sa Maysakit at ang huling mga sakramento | CatholicDoorway",
     "Kailan at paano tatawag ng pari para sa Pagpapahid ng Langis sa Maysakit o sa huling mga sakramento, ano ang mga ito at ano ang gagawin kung may naghihingalo ngayon."),
    ("funerals", "libing", "Lamay at libing", "Paano maghanda ng lamay at libing na Katoliko | CatholicDoorway",
     "Paano maghanda ng libing na Katoliko: ang lamay, ang Misa ng patay at ang paglilibing, ang mga tuntunin sa cremation, ang gastos at ang pagpapamisa para sa yumao."),
    ("baptism-certificate", "katibayan-ng-binyag", "Katibayan ng binyag", "Paano kumuha ng kopya ng iyong katibayan ng binyag | CatholicDoorway",
     "Paano humingi ng katibayan ng binyag na may mga tala para sa kasal o pagiging ninong o ninang, kahit sarado na ang parokya o sa Pilipinas ka bininyagan."),
    ("examination-of-conscience", "pagsusuri-ng-budhi", "Pagsusuri ng budhi", "Pagsusuri ng budhi para sa mga bata, kabataan at nakatatanda | CatholicDoorway",
     "Isang pagsusuri ng budhi bago mangumpisal, para sa mga bata, kabataan at nakatatanda. Markahan ang angkop at gumawa ng pribadong listahan sa iyong telepono."),
    ("devotions", "mga-debosyon", "Mga debosyon", "Mga debosyong Katoliko at mga paalala sa pagdarasal | CatholicDoorway",
     "Ang mga pinakamamahal na debosyong Katoliko at ang kanilang mga dasal: ang Rosaryo, ang Koronilya ng Banal na Awa, ang Daan ng Krus, mga nobena at ang Orasyon, may libreng paalala sa iyong kalendaryo."),
    ("divine-mercy-chaplet", "koronilya-ng-banal-na-awa", "Koronilya ng Banal na Awa", "Paano dasalin ang Koronilya ng Banal na Awa, hakbang-hakbang | CatholicDoorway",
     "Dasalin ang Koronilya ng Banal na Awa butil por butil sa iyong telepono: ang mga dasal sa bawat dekada, ang Oras ng Awa sa ika-3 ng hapon at ang nobena."),
    ("stations-of-the-cross", "daan-ng-krus", "Daan ng Krus", "Daan ng Krus: dasalin ang 14 na estasyon | CatholicDoorway",
     "Dasalin ang Daan ng Krus (Via Crucis) na may sipi ng Banal na Kasulatan, pagninilay at dasal sa bawat isa sa 14 na estasyon, isa-isa sa iyong telepono."),
    ("novenas", "mga-nobena", "Mga nobena", "Mga nobenang Katoliko at ang mga petsa nito ngayong taon | CatholicDoorway",
     "Paano magnobena, kasama ang mga dasal at petsa ngayong taon ng mga nobena kay San Jose, sa Espiritu Santo, sa Banal na Awa, sa Sagrado Corazon, sa Birhen ng Guadalupe at iba pa."),
    ("angelus", "orasyon", "Ang Orasyon", "Ang Orasyon (Angelus) at ang Regina Caeli | CatholicDoorway",
     "Ang mga salita ng Orasyon o Angelus, na dinarasal sa ika-6 ng umaga, tanghali at ika-6 ng gabi, at ang Regina Caeli sa Panahon ng Pagkabuhay, may libreng paalala araw-araw."),
    ("liturgy-of-the-hours", "liturhiya-ng-mga-oras", "Liturhiya ng mga Oras", "Liturhiya ng mga Oras: Panalangin sa Umaga at Gabi ngayon | CatholicDoorway",
     "Dasalin ngayon ang Panalangin sa Umaga, sa Gabi at Bago Matulog ng Liturhiya ng mga Oras, at alamin kung paano ito gumagana at paano magsisimula."),
    ("church-documents", "katesismo-at-dokumento", "Katesismo at mga dokumento", "Ang Katesismo ng Simbahang Katolika at ang mahahalagang dokumento ng Simbahan | CatholicDoorway",
     "Hanapin ang anumang talata ng Katesismo, basahin ito ayon sa paksa, at hanapin ang mahahalagang ensiklika, liham apostoliko at dokumento ng Vaticano II, may link sa opisyal na teksto."),
    ("ocia-listing", "ilista-ang-ocia", "Ilista ang inyong OCIA", "Ilista ang OCIA ng inyong parokya | CatholicDoorway",
     "Mga tagapag-ugnay ng OCIA: idagdag ang inyong contact upang malaman ng mga nakikilala ang pananampalatayang Katoliko malapit sa inyo kung sino ang tatawagan. Libre at sinusuri bago ilathala."),
    ("prayers", "mga-dasal", "Mga dasal", "Mga dasal Katoliko at paano magrosaryo | CatholicDoorway",
     "Ang mga tradisyonal na dasal Katoliko sa Tagalog: Ama Namin, Aba Ginoong Maria, Sumasampalataya, Aba Po Santa Mariang Hari at iba pa, kasama ang gabay sa Rosaryo."),
    ("rosary", "rosaryo", "Magrosaryo", "Magrosaryo online, butil por butil | CatholicDoorway",
     "Dasalin ang Rosaryo hakbang-hakbang sa iyong telepono: umiilaw ang mga butil, may sipi ng Bibliya ang bawat misteryo at natatandaan kung saan ka huminto."),
    ("beliefs", "mga-paniniwala", "Mga paniniwala", "Ano ang pinaniniwalaan ng mga Katoliko | CatholicDoorway",
     "Isang simpleng buod ng pananampalataya at pamumuhay Katoliko: ang Kredo, ang pitong sakramento, ang Banal na Kasulatan at Tradisyon, si Maria at ang mga santo, at ang buhay moral."),
    ("find-a-church", "hanapin-ang-simbahan", "Maghanap ng simbahan", "Maghanap ng simbahang Katoliko malapit sa iyo | CatholicDoorway",
     "Maghanap ng mga simbahang Katoliko sa Estados Unidos ayon sa lungsod o ZIP code: address, telepono, website at direksiyon."),
    ("bible", "bibliya", "Bibliya", "Ang Bibliya at ang mga pagbasa sa Misa ngayon | CatholicDoorway",
     "Ang mga pagbasa sa Misa ngayon, paano nakaayos ang Bibliyang Katoliko at kung saan ito mababasa nang libre."),
    ("calendar", "kalendaryo", "Kalendaryo", "Mga araw na pangilin at araw ng pag-aayuno: kalendaryong Katoliko | CatholicDoorway",
     "Ang mga araw na pangilin, mga araw ng pag-aayuno at ang mga pangunahing kapistahan sa Estados Unidos, may libreng kalendaryo sa Filipino para sa iyong iPhone, Google o Outlook."),
    ("questions", "mga-tanong", "Tapat na mga tanong", "Tapat na mga tanong tungkol sa Simbahang Katolika, sinagot | CatholicDoorway",
     "Maikli, magiliw at malinaw na sagot sa mga itinatanong tungkol sa mga Katoliko: si Maria, ang mga santo, ang kumpisal, ang Papa, ang purgatoryo at iba pa."),
    ("glossary", "glosaryo", "Glosaryo", "Glosaryong Katoliko: mga salitang ipinaliwanag | CatholicDoorway",
     "Simpleng kahulugan ng mga salitang Katoliko, mula Adbiyento hanggang Vaticano."),
    ("structure", "istruktura", "Ang Simbahan", "Paano nakaayos ang Simbahang Katolika | CatholicDoorway",
     "Paano nakaayos ang Simbahang Katolika: ang Papa, ang mga obispo, mga diyosesis, mga parokya, mga pari at mga diyakono, ipinaliwanag nang simple."),
    ("popes", "mga-papa", "Ang mga Papa", "Ang 267 Papa, mula kay San Pedro hanggang kay Leo XIV | CatholicDoorway",
     "Lahat ng Papa ayon sa pagkakasunod, mula kay San Pedro hanggang kay Leo XIV: ang kanilang lugar sa paghahalili, mga taon ng pagiging Papa at kung bakit sila naaalala."),
    ("dioceses", "mga-diyosesis", "Mga diyosesis", "Ang mga diyosesis Katoliko sa Estados Unidos | CatholicDoorway",
     "Lahat ng diyosesis, arkidiyosesis at eparkiya Katoliko sa Estados Unidos: ang obispo, ang katedral, ang website at tulong para magsimula sa OCIA."),
    ("saints", "mga-santo", "Mga santo", "Mga Santo, Beato at Benerableng Katoliko | CatholicDoorway",
     "Kilalanin ang mga santo at ang landas tungo sa kabanalan: Lingkod ng Diyos, Benerable, Beato at Santo."),
    ("saints-directory", "direktoryo-ng-mga-santo", "Direktoryo ng mga santo", "Direktoryo ng mga santo at kausa: Santo, Beato, Benerable at Lingkod ng Diyos | CatholicDoorway",
     "Maghanap sa libu-libong Santo, Beato, Benerable at Lingkod ng Diyos ayon sa pangalan, bansa, siglo at pagiging patron. Ina-update linggo-linggo."),
    ("about", "tungkol", "Tungkol sa site", "Tungkol sa CatholicDoorway",
     "Tungkol sa CatholicDoorway.com: isang libre at walang patalastas na gabay sa pananampalatayang Katoliko. Mga pinagkunan, datos, privacy at pagtatama."),
]
TL_TEXT = dict(lang="tl", skip="Lumaktaw sa nilalaman", home="/tl/", home_label="Tahanan ng CatholicDoorway",
               theme_label="Lumipat sa maliwanag o madilim na anyo", menu_label="Menu", nav_label="Pangunahin")
EN_TO_TL = {en: tl for en, tl, *_ in TL_PAGES}
TL_SUBNAV = {"magsimula": [("magsimula", "Maging Katoliko (OCIA)"), ("unang-misa", "Ang iyong unang Misa"), ("mga-gabay", "Mga praktikal na gabay"),
                           ("kumpisal", "Paano mangumpisal"), ("pagsusuri-ng-budhi", "Pagsusuri ng budhi"), ("pagbabalik", "Pagbabalik sa Simbahan")],
             "mga-dasal": [("mga-dasal", "Mga dasal Katoliko"), ("rosaryo", "Magrosaryo"), ("mga-debosyon", "Mga debosyon at paalala"),
                           ("liturhiya-ng-mga-oras", "Liturhiya ng mga Oras")],
             "bibliya": [("bibliya", "Ang mga pagbasa ngayon at ang Bibliya"), ("kalendaryo", "Kalendaryo ng mga banal na araw")],
             "mga-paniniwala": [("mga-paniniwala", "Ang pinaniniwalaan ng mga Katoliko"), ("mga-tanong", "Tapat na mga tanong"), ("glosaryo", "Glosaryo"),
                                ("katesismo-at-dokumento", "Ang Katesismo at mga dokumento")],
             "mga-santo": [("mga-santo", "Kilalanin ang mga santo"), ("direktoryo-ng-mga-santo", "Direktoryo ng mga santo at kausa")],
             "istruktura": [("istruktura", "Paano nakaayos ang Simbahan"), ("mga-papa", "Ang 267 Papa"), ("mga-diyosesis", "Ang mga diyosesis sa Estados Unidos"),
                            ("hanapin-ang-simbahan", "Maghanap ng simbahan")]}
# Filipino pages reached from a hub page rather than the top menu
TL_NAV_EXCLUDE = {"koronilya-ng-banal-na-awa", "daan-ng-krus", "mga-nobena", "orasyon", "ilista-ang-ocia", "tungkol", "magpatala-sa-parokya", "binyag", "kasal", "pagpapahid-ng-langis", "libing", "katibayan-ng-binyag"}

LANGS = [("en", "English", "home page"), ("es", "Español", "página de inicio"), ("pt", "Português", "página inicial"), ("tl", "Filipino", "pangunahing pahina")]
LANG_HOME = {"en": "/", "es": "/es/", "pt": "/pt/", "tl": "/tl/"}
LANG_WORD = {"en": "Language", "es": "Idioma", "pt": "Idioma", "tl": "Wika"}
GLOBE_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M3 12h18M12 3c2.6 2.6 3.9 5.6 3.9 9s-1.3 6.4-3.9 9c-2.6-2.6-3.9-5.6-3.9-9S9.4 5.6 12 3z" fill="none" stroke="currentColor" stroke-width="1.8"/></svg>'


def lang_urls(en_slug):
    """The URL of this page in each language, or None where it has no translation yet."""
    if en_slug is None:
        return {"en": None, "es": None, "pt": None, "tl": None}
    es, pt, tl = EN_TO_ES.get(en_slug), EN_TO_PT.get(en_slug), EN_TO_TL.get(en_slug)
    return {"en": "/" if en_slug == "index" else f"/{en_slug}",
            "es": None if es is None else ("/es/" if es == "index" else f"/es/{es}"),
            "pt": None if pt is None else ("/pt/" if pt == "index" else f"/pt/{pt}"),
            "tl": None if tl is None else ("/tl/" if tl == "index" else f"/tl/{tl}")}


STATE_WORD = {"en": "Choose a state", "es": "Elige un estado", "pt": "Escolha um estado", "tl": "Pumili ng estado"}
DIO_WORD = {"en": "Not sure / other", "es": "No sé / otra", "pt": "Não sei / outra", "tl": "Hindi sigurado / iba pa"}


def ocia_options(body, lang):
    """State and diocese choices for the parish OCIA listing form."""
    if "{{STATE_OPTIONS}}" not in body:
        return body
    dd = load_dioceses()["dioceses"]
    tbl = STATE_NAME.get(lang, {})
    states = sorted({s for d in dd for s in d.get("states", []) if s in ABBR}, key=lambda s: tbl.get(s, s))
    so = f'<option value="">{STATE_WORD[lang]}</option>' + "".join(
        f'<option value="{html.escape(s)}">{html.escape(tbl.get(s, s))}</option>' for s in states)
    dios = sorted(dd, key=lambda d: dio_name(d["short"], lang))
    do = f'<option value="">{DIO_WORD[lang]}</option>' + "".join(
        f'<option value="{html.escape(d["short"])}">{html.escape(dio_name(d["short"], lang))}</option>' for d in dios)
    return body.replace("{{STATE_OPTIONS}}", so).replace("{{DIOCESE_OPTIONS}}", do)


def write_saint_days():
    """Saint of the day: the U.S. General Roman Calendar's fixed dates, for the home and saints pages."""
    rows = {}
    for line in (ROOT / "src" / "data" / "saint_days.tsv").read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        date, rank, en, es, pt, tl = line.split("\t")
        rows[date] = [rank, en, es, pt, tl]
    (OUT / "data" / "saint-days.json").write_text(json.dumps(rows, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


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
<script>document.documentElement.classList.add('js');try{{var t=localStorage.getItem('cd-theme');if(t)document.documentElement.setAttribute('data-theme',t);}}catch(e){{}}</script>
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
          <li><a href="/es/acerca">Acerca del sitio</a></li>
          <li><a href="/es/registrar-ocia">Registra el OCIA de tu parroquia</a></li>
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
          <li><a href="/pt/santos">Santos</a></li>
        </ul>
      </div>
      <div>
        <h4>Sobre o site</h4>
        <ul>
          <li><a href="/pt/sobre">Sobre o site</a></li>
          <li><a href="/pt/cadastrar-ocia">Cadastre a OCIA da sua paróquia</a></li>
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

FOOT_TL = """</main>
<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <p class="footer-verse">&ldquo;Ako ang pintuan; ang sinumang pumasok sa pamamagitan ko ay maliligtas.&rdquo;</p>
        <p class="small">Juan 10:9</p>
      </div>
      <div>
        <h4>Sa Filipino</h4>
        <ul>
          <li><a href="/tl/magsimula">Paano maging Katoliko (OCIA)</a></li>
          <li><a href="/tl/unang-misa">Ang iyong unang Misa</a></li>
          <li><a href="/tl/mga-dasal">Mga dasal at ang Rosaryo</a></li>
        </ul>
      </div>
      <div>
        <h4>Matuto</h4>
        <ul>
          <li><a href="/tl/hanapin-ang-simbahan">Maghanap ng simbahan</a></li>
          <li><a href="/tl/mga-paniniwala">Ang aming pinaniniwalaan</a></li>
          <li><a href="/tl/mga-santo">Mga santo</a></li>
        </ul>
      </div>
      <div>
        <h4>Tungkol sa site</h4>
        <ul>
          <li><a href="/tl/tungkol">Tungkol sa site</a></li>
          <li><a href="/tl/ilista-ang-ocia">Ilista ang OCIA ng iyong parokya</a></li>
          <li><a href="mailto:hello@catholicdoorway.com">Sumulat sa amin</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-base">
      Ang CatholicDoorway ay isang libre at malayang gabay na walang patalastas. Hindi ito opisyal na site ng Simbahang Katolika o ng anumang diyosesis. Para sa opisyal na turo ng Simbahan, tingnan ang <a href="https://www.vatican.va/archive/ENG0015/_INDEX.HTM">Katesismo ng Simbahang Katolika</a>.
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
          <li><a href="/ocia-listing">List your parish&rsquo;s OCIA</a></li>
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

PRAY_JS = ("", '<script src="/assets/js/pray.js" defer></script>')
EXTRA = {
    "examination-of-conscience": PRAY_JS, "devotions": PRAY_JS, "novenas": PRAY_JS, "angelus": PRAY_JS,
    "liturgy-of-the-hours": PRAY_JS, "church-documents": PRAY_JS, "ocia-listing": PRAY_JS,
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


STATUS_LABEL_TL = {"saint": ("San", "Santa"), "blessed": ("Beato", "Beata"), "venerable": ("Benerable", "Benerable"),
                   "servant": ("Lingkod ng Diyos", "Lingkod ng Diyos")}
STATUS_LABEL_PT = {"saint": ("Santo", "Santa"), "blessed": ("Beato", "Beata"), "venerable": ("Venerável", "Venerável"),
                   "servant": ("Servo de Deus", "Serva de Deus")}


def saints_html(lang="en"):
    es = lang == "es"
    data = json.loads((ROOT / "src" / "data" / ("saints.json" if lang == "en" else f"saints_{lang}.json")).read_text(encoding="utf-8"))
    out = []
    for p in data:
        e = html.escape
        fw = {"en": "Feast", "es": "Fiesta", "pt": "Festa", "tl": "Kapistahan"}[lang]
        feast = f" &middot; {fw}: {e(p['feast'])}" if p.get("feast") else ""
        if lang == "tl":
            label = {"saint": "Santo", "blessed": "Beato", "venerable": "Benerable", "servant": "Lingkod ng Diyos"}[p["status"]]
            if p.get("fem"):
                label = {"saint": "Santa", "blessed": "Beata"}.get(p["status"], label)
        elif lang == "pt":
            label = STATUS_LABEL_PT[p["status"]][1 if p.get("fem") else 0]
        elif es:
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
    data = json.loads((ROOT / "src" / "data" / ("glossary.json" if lang == "en" else f"glossary_{lang}.json")).read_text(encoding="utf-8"))
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


POPE_PT = {"Peter": "Pedro", "Linus": "Lino", "Anacletus": "Anacleto", "Clement": "Clemente", "Evaristus": "Evaristo",
           "Alexander": "Alexandre", "Sixtus": "Sisto", "Telesphorus": "Telésforo", "Hyginus": "Higino", "Pius": "Pio",
           "Anicetus": "Aniceto", "Soter": "Sotero", "Eleutherius": "Eleutério", "Victor": "Vítor", "Zephyrinus": "Zeferino",
           "Callixtus": "Calisto", "Urban": "Urbano", "Pontian": "Ponciano", "Anterus": "Antero", "Fabian": "Fabiano",
           "Cornelius": "Cornélio", "Lucius": "Lúcio", "Stephen": "Estêvão", "Dionysius": "Dionísio", "Felix": "Félix",
           "Eutychian": "Eutiquiano", "Caius": "Caio", "Marcellinus": "Marcelino", "Marcellus": "Marcelo", "Eusebius": "Eusébio",
           "Miltiades": "Melquíades", "Sylvester": "Silvestre", "Mark": "Marcos", "Julius": "Júlio", "Liberius": "Libério",
           "Damasus": "Dâmaso", "Siricius": "Sirício", "Anastasius": "Anastácio", "Innocent": "Inocêncio", "Zosimus": "Zósimo",
           "Boniface": "Bonifácio", "Celestine": "Celestino", "Leo": "Leão", "Hilarius": "Hilário", "Simplicius": "Simplício",
           "Gelasius": "Gelásio", "Symmachus": "Símaco", "John": "João", "Agapetus": "Agapito", "Silverius": "Silvério",
           "Vigilius": "Vigílio", "Pelagius": "Pelágio", "Benedict": "Bento", "Gregory": "Gregório", "Sabinian": "Sabiniano",
           "Adeodatus": "Adeodato", "Honorius": "Honório", "Severinus": "Severino", "Theodore": "Teodoro", "Martin": "Martinho",
           "Eugene": "Eugênio", "Vitalian": "Vitaliano", "Donus": "Dono", "Agatho": "Agatão", "Conon": "Cónon", "Sergius": "Sérgio",
           "Sisinnius": "Sisínio", "Constantine": "Constantino", "Zachary": "Zacarias", "Paul": "Paulo", "Adrian": "Adriano",
           "Paschal": "Pascoal", "Valentine": "Valentino", "Nicholas": "Nicolau", "Marinus": "Marino", "Formosus": "Formoso",
           "Romanus": "Romano", "Lando": "Lando", "Francis": "Francisco", "Hormisdas": "Hormisdas"}


def pope_name_pt(n):
    n = n.replace("(the Great)", "Magno").replace("(1st time)", "(primeira vez)").replace("(2nd time)", "(segunda vez)").replace("(3rd time)", "(terceira vez)")
    pre = ""
    for a in ("St. ", "Bl. ", "Ven. "):
        if n.startswith(a):
            pre, n = a, n[len(a):]
    n = " ".join(POPE_PT.get(w, w) for w in n.split(" "))
    if pre == "St. ":
        pre = "Santo " if n[0] in "AEIOUÁÉÍÓÚH" else "São "
    elif pre:
        pre = {"Bl. ": "Beato ", "Ven. ": "Venerável "}[pre]
    return pre + n


POPE_TL = dict(POPE_ES, Leo="Leo", Benedict="Benedicto", Paul="Pablo", Stephen="Esteban")


def pope_name_tl(n):
    n = n.replace("(the Great)", "Dakila").replace("(1st time)", "(unang pagkakataon)").replace("(2nd time)", "(ikalawang pagkakataon)").replace("(3rd time)", "(ikatlong pagkakataon)")
    pre = ""
    for a, b in (("St. ", "San "), ("Bl. ", "Beato "), ("Ven. ", "Benerable ")):
        if n.startswith(a):
            pre, n = b, n[len(a):]
    n = " ".join(POPE_TL.get(w, w) for w in n.split(" "))
    return pre + n


def popes_html(lang="en"):
    es = lang == "es"
    pt = lang == "pt"
    tlg = lang == "tl"
    rows = [l.split("\t") for l in (ROOT / "src" / "data" / "popes.tsv").read_text(encoding="utf-8").splitlines()
            if l and not l.startswith("#")]
    if lang != "en":
        tr = dict(l.split("\t", 1) for l in (ROOT / "src" / "data" / f"popes_{lang}.tsv").read_text(encoding="utf-8").splitlines() if l)
    e = html.escape
    yr = (lambda d: _yr(d).replace("c. ", "h. ")) if es else _yr
    out, cents, cur = [], [], None
    for ord_, name, bn, start, end, birth, death, summary in rows:
        n = int(ord_)
        if es:
            name, summary = pope_name_es(name), tr[ord_]
        elif pt:
            name, summary = pope_name_pt(name), tr[ord_]
        elif tlg:
            name, summary = pope_name_tl(name), tr[ord_]
        c = (int(start[:4]) - 1) // 100 + 1
        if c != cur:
            if cur is not None:
                out.append("    </ol>")
            cur = c
            cents.append(c)
            head = f"Siglo {ROMAN[c]}" if es else f"Ika-{c} siglo" if tlg else f"Século {ROMAN[c]}" if pt else f"{_ordinal(c)} century"
            out.append(f'    <h2 class="pope-cent" id="c{c}">{head}</h2>\n    <ol class="popes">')
        W = {"en": ("since", "Born", "Lived", "Died", "Born", "Pope"), "es": ("desde", "Nació en", "Vivió", "Murió en", "Nombre de pila:", "Papa"),
             "pt": ("desde", "Nasceu em", "Viveu", "Morreu em", "Nome de batismo:", "Papa"),
             "tl": ("mula", "Isinilang noong", "Nabuhay", "Namatay noong", "Pangalan sa binyag:", "Papa")}[lang]
        if n == 1:
            reign, life = {"es": ("h. años 30 &ndash; 64 o 67", "Mártir en Roma, 64 o 67"),
                           "pt": ("c. anos 30 &ndash; 64 ou 67", "Mártir em Roma, 64 ou 67"),
                           "tl": ("c. dekada 30 &ndash; 64 o 67", "Martir sa Roma, 64 o 67")}.get(lang, ("c. 30s &ndash; 64 or 67", "Martyred in Rome, 64 or 67"))
        else:
            a, b = yr(start), yr(end)
            reign = (f"{W[0]} {a}" if not end else a if a == b else f"{a}&ndash;{b}")
            if not death:
                life = f"{W[1]} {yr(birth)}"
            elif birth:
                life = f"{W[2]} {yr(birth)}&ndash;{yr(death)}"
            else:
                life = f"{W[3]} {yr(death)}"
        born = f'<span class="pope-bn">{W[4]} {e(bn)}</span>' if bn else ""
        curcls = " current" if not end else ""
        out.append(
            f'      <li class="pope{curcls}" id="pope-{n}" value="{n}"><span class="pope-no" aria-hidden="true">{n}</span>'
            f'<div><h3>{e(name)}</h3>{born}'
            f'<p class="pope-meta"><span>{W[5]} {reign}</span><span>{life}</span></p>'
            f'<p>{e(summary)}</p></div></li>')
    out.append("    </ol>")
    jump = "\n".join(f'    <a href="#c{c}">{ROMAN[c] if lang not in ("en", "tl") else (str(c) if lang == "tl" else _ordinal(c))}</a>' for c in cents)
    return "\n".join(out), jump


POSE = {"stand": "Stand", "sit": "Sit", "kneel": "Kneel", "any": "As you wish"}


POSE_ES = {"stand": "De pie", "sit": "Sentados", "kneel": "De rodillas", "any": "Como prefieras"}
POSE_PT = {"stand": "De pé", "sit": "Sentados", "kneel": "De joelhos", "any": "Como preferir"}
POSE_TL = {"stand": "Tumayo", "sit": "Umupo", "kneel": "Lumuhod", "any": "Kung ano ang gusto mo"}


LATIN_TEXT = {
    "en": ("Pray in Latin", "Latin is the Church&rsquo;s own language, and these are the words Catholics everywhere have prayed for centuries. You will still hear them at many parishes, in sung Masses and at Benediction. Latin is on the left, English on the right.",
           "How to say it", "Church Latin sounds a lot like Italian. Say every vowel; <em>ae</em> sounds like &ldquo;eh&rdquo;. <em>C</em> before e or i sounds like &ldquo;ch&rdquo; (<em>caelis</em>: CHEH-lees), <em>g</em> before e or i is soft as in &ldquo;gem&rdquo;, and <em>gn</em> sounds like &ldquo;ny&rdquo; (<em>regnum</em>: REH-nyoom). The accent marks show which syllable to stress.", "Latin"),
    "es": ("Reza en latín", "El latín es la lengua propia de la Iglesia, y estas son las palabras que los católicos de todo el mundo han rezado durante siglos. Todavía se oyen en muchas parroquias, en las Misas cantadas y en la Bendición con el Santísimo. El latín está a la izquierda y el español a la derecha.",
           "Cómo se pronuncia", "El latín de la Iglesia suena muy parecido al italiano. Pronuncia todas las vocales; <em>ae</em> suena como &ldquo;e&rdquo;. La <em>c</em> antes de e o i suena como &ldquo;ch&rdquo; (<em>caelis</em>: CHE-lis), la <em>g</em> antes de e o i suena como la <em>y</em> de &ldquo;yema&rdquo;, y <em>gn</em> suena como &ldquo;ñ&rdquo; (<em>regnum</em>: RE-ñum). Los acentos indican qué sílaba se pronuncia con más fuerza.", "Latín"),
    "pt": ("Reze em latim", "O latim é a língua própria da Igreja, e estas são as palavras que os católicos do mundo inteiro rezam há séculos. Você ainda as ouve em muitas paróquias, nas Missas cantadas e na Bênção do Santíssimo. O latim está à esquerda e o português à direita.",
           "Como pronunciar", "O latim da Igreja soa muito parecido com o italiano. Pronuncie todas as vogais; <em>ae</em> soa como &ldquo;é&rdquo;. O <em>c</em> antes de e ou i soa como &ldquo;tch&rdquo; (<em>caelis</em>: TCHÉ-lis), o <em>g</em> antes de e ou i soa como &ldquo;dj&rdquo;, e <em>gn</em> soa como &ldquo;nh&rdquo; (<em>regnum</em>: RÉ-nhum). Os acentos mostram a sílaba tônica.", "Latim"),
    "tl": ("Magdasal sa Latin", "Ang Latin ang sariling wika ng Simbahan, at ito ang mga salitang dinarasal ng mga Katoliko sa buong mundo sa loob ng maraming siglo. Naririnig mo pa rin ang mga ito sa maraming parokya, sa mga inaawit na Misa at sa Pagbebendisyon sa Santisimo Sakramento. Nasa kaliwa ang Latin at nasa kanan ang Tagalog.",
           "Paano bigkasin", "Ang Latin ng Simbahan ay katunog ng Italyano. Bigkasin ang bawat patinig; ang <em>ae</em> ay parang &ldquo;e&rdquo;. Ang <em>c</em> bago ang e o i ay parang &ldquo;ts&rdquo; (<em>caelis</em>: TSE-lis), ang <em>g</em> bago ang e o i ay parang &ldquo;dy&rdquo;, at ang <em>gn</em> ay parang &ldquo;ny&rdquo; (<em>regnum</em>: RE-nyum). Ipinapakita ng tuldik kung aling pantig ang may diin.", "Latin"),
}
LANG_LABEL = {"en": "English", "es": "Español", "pt": "Português", "tl": "Tagalog"}


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
    pose = {"en": POSE, "es": POSE_ES, "pt": POSE_PT, "tl": POSE_TL}[lang]
    everyone = {"en": ("All", "You", "Catholic"), "es": ("Todos", "Tú", "Quien comulga"),
                "pt": ("Todos", "Você", "Quem comunga"), "tl": ("Lahat", "Ikaw", "Ang tatanggap ng Komunyon")}[lang]
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


CCC_URL = {"tl": "https://www.vatican.va/archive/ENG0015/_INDEX.HTM", "es": "https://www.vatican.va/archive/catechism_sp/index_sp.html",
           "pt": "https://www.vatican.va/archive/cathechism_po/index_new/prima-pagina-cic_po.html"}


def questions_html(lang="en"):
    es = lang != "en"  # Spanish and Portuguese share the same layout
    data = json.loads((ROOT / "src" / "data" / ("questions.json" if lang == "en" else f"questions_{lang}.json")).read_text(encoding="utf-8"))
    out = []
    for q in data:
        refs = []
        for ref in q["refs"]:
            if isinstance(ref, str):  # Spanish/Portuguese: a plain citation
                if ref.startswith("Catecismo"):
                    refs.append(f'<a href="{CCC_URL[lang]}" target="_blank" rel="noopener">{html.escape(ref)}</a>')
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
            g = {"en": ("/glossary", "Glossary"), "es": ("/es/glosario", "Glosario"), "pt": ("/pt/glossario", "Glossário"), "tl": ("/tl/glosaryo", "Glosaryo")}[lang]
            refs.append(f'<a href="{g[0]}#{q["glossary"]}">{g[1]}</a>')
        body = "".join(f"<p>{para}</p>" for para in q["a"])
        summary = q["q"] if es else html.escape(q["q"])
        out.append(f'    <details class="qa" id="{q["id"]}"><summary>{summary}</summary>'
                   f'<div class="qa-body">{body}<p class="qa-refs">{ {"en": "Read more", "es": "Para leer más", "pt": "Para ler mais", "tl": "Basahin pa"}[lang] }: {" &middot; ".join(refs)}</p></div></details>')
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
    tbl = STATE_NAME.get(lang, {})
    name = lambda x: tbl.get(x, x)
    st = ", ".join(f"{name(x)} ({ABBR[x]})" if x in ABBR else name(x) for x in d["states"])
    W = {"en": ("Eastern Catholic, nationwide", "based in", "Nationwide", "United States"),
         "es": ("Católica oriental, todo el país", "sede en", "Todo el país", "Estados Unidos"),
         "pt": ("Católica oriental, todo o país", "sede em", "Todo o país", "Estados Unidos"),
         "tl": ("Katolikong Silanganin, buong bansa", "nakabase sa", "Buong bansa", "Estados Unidos")}[lang]
    if dio_kind(d) == "eastern":
        base = W[0]
        if d.get("city") and st:
            base += f" ({W[1]} {d['city']}, {', '.join(name(x) for x in d['states'])})"
        return base
    if dio_kind(d) == "nationwide":
        return W[2]
    return st or W[3]


PT_STATE = {"New York": "Nova York", "New Jersey": "Nova Jersey", "New Mexico": "Novo México", "New Hampshire": "Nova Hampshire",
            "North Carolina": "Carolina do Norte", "South Carolina": "Carolina do Sul", "North Dakota": "Dakota do Norte",
            "South Dakota": "Dakota do Sul", "Pennsylvania": "Pensilvânia", "Hawaii": "Havaí", "Louisiana": "Luisiana",
            "Missouri": "Missouri", "Mississippi": "Mississippi", "West Virginia": "Virgínia Ocidental", "Virginia": "Virgínia",
            "District of Columbia": "Distrito de Colúmbia", "California": "Califórnia", "Florida": "Flórida", "Georgia": "Geórgia",
            "Arizona": "Arizona", "Oregon": "Oregon", "Northern Mariana Islands": "Ilhas Marianas do Norte",
            "American Samoa": "Samoa Americana", "U.S. Virgin Islands": "Ilhas Virgens Americanas", "Puerto Rico": "Porto Rico"}
STATE_NAME = {"es": ES_STATE, "pt": PT_STATE, "tl": {}}

# Eastern Catholic eparchies and the military archdiocese: Spanish, Portuguese
EP_NAMES = {
    "Byzantine Catholic Eparchy of Phoenix": ("Eparquía bizantina católica de Phoenix", "Eparquia Bizantina Católica de Phoenix"),
    "Armenian Catholic Eparchy of Our Lady of Nareg in the United States of America and Canada": (
        "Eparquía armenia católica de Nuestra Señora de Narek en Estados Unidos y Canadá", "Eparquia Armênia Católica de Nossa Senhora de Narek nos Estados Unidos e no Canadá"),
    "Chaldean Catholic Eparchy of Saint Peter The Apostle": ("Eparquía caldea católica de San Pedro Apóstol", "Eparquia Caldeia Católica de São Pedro Apóstolo"),
    "Maronite Catholic Eparchy of Our Lady of Lebanon of Los Angeles": ("Eparquía maronita de Nuestra Señora del Líbano de Los Ángeles", "Eparquia Maronita de Nossa Senhora do Líbano de Los Angeles"),
    "Ukrainian Catholic Eparchy of Stamford": ("Eparquía greco-católica ucraniana de Stamford", "Eparquia Greco-Católica Ucraniana de Stamford"),
    "St. Thomas Syro-Malabar Catholic Eparchy of Chicago": ("Eparquía siro-malabar de Santo Tomás de Chicago", "Eparquia Siro-Malabar de São Tomé de Chicago"),
    "Ukrainian Catholic Eparchy of Chicago": ("Eparquía greco-católica ucraniana de Chicago", "Eparquia Greco-Católica Ucraniana de Chicago"),
    "Melkite Greek Catholic Eparchy of Newton": ("Eparquía greco-melquita católica de Newton", "Eparquia Greco-Melquita Católica de Newton"),
    "Chaldean Catholic Eparchy of Saint Thomas the Apostle of Detroit": ("Eparquía caldea católica de Santo Tomás Apóstol de Detroit", "Eparquia Caldeia Católica de São Tomé Apóstolo de Detroit"),
    "Byzantine Catholic Eparchy of Passaic": ("Eparquía bizantina católica de Passaic", "Eparquia Bizantina Católica de Passaic"),
    "Syriac Catholic Eparchy of Our Lady of Deliverance in the United States": ("Eparquía siro-católica de Nuestra Señora de la Liberación en Estados Unidos", "Eparquia Siro-Católica de Nossa Senhora da Libertação nos Estados Unidos"),
    "Eparchy of St. Maron of Brooklyn": ("Eparquía maronita de San Marón de Brooklyn", "Eparquia Maronita de São Marão de Brooklyn"),
    "Byzantine Catholic Eparchy of Parma": ("Eparquía bizantina católica de Parma", "Eparquia Bizantina Católica de Parma"),
    "Romanian Catholic Eparchy of St George's in Canton": ("Eparquía greco-católica rumana de San Jorge en Canton", "Eparquia Greco-Católica Romena de São Jorge em Canton"),
    "Ukrainian Catholic Eparchy of Saint Josaphat in Parma": ("Eparquía greco-católica ucraniana de San Josafat en Parma", "Eparquia Greco-Católica Ucraniana de São Josafá em Parma"),
    "Byzantine Catholic Archeparchy of Pittsburgh": ("Archieparquía bizantina católica de Pittsburgh", "Arquieparquia Bizantina Católica de Pittsburgh"),
    "Ukrainian Catholic Archeparchy of Philadelphia": ("Archieparquía greco-católica ucraniana de Filadelfia", "Arquieparquia Greco-Católica Ucraniana da Filadélfia"),
    "Archdiocese for the Military Services": ("Arquidiócesis para los Servicios Militares", "Arquidiocese para os Serviços Militares"),
    "Syro-Malankara Catholic Eparchy of St. Mary, Queen of Peace, of the United States of America and Canada": (
        "Eparquía siro-malankar de Santa María, Reina de la Paz, de Estados Unidos y Canadá", "Eparquia Siro-Malancar de Santa Maria, Rainha da Paz, dos Estados Unidos e do Canadá"),
}


EP_TL = {
    "Byzantine Catholic Eparchy of Phoenix": "Eparkiyang Katolikong Bisantino ng Phoenix",
    "Armenian Catholic Eparchy of Our Lady of Nareg in the United States of America and Canada": "Eparkiyang Katolikong Armenyo ng Mahal na Birhen ng Narek sa Estados Unidos at Canada",
    "Chaldean Catholic Eparchy of Saint Peter The Apostle": "Eparkiyang Katolikong Kaldeo ni San Pedro Apostol",
    "Maronite Catholic Eparchy of Our Lady of Lebanon of Los Angeles": "Eparkiyang Maronita ng Mahal na Birhen ng Lebanon ng Los Angeles",
    "Ukrainian Catholic Eparchy of Stamford": "Eparkiyang Katolikong Ukranyano ng Stamford",
    "St. Thomas Syro-Malabar Catholic Eparchy of Chicago": "Eparkiyang Siro-Malabar ni Santo Tomas ng Chicago",
    "Ukrainian Catholic Eparchy of Chicago": "Eparkiyang Katolikong Ukranyano ng Chicago",
    "Melkite Greek Catholic Eparchy of Newton": "Eparkiyang Katolikong Griyegong Melkita ng Newton",
    "Chaldean Catholic Eparchy of Saint Thomas the Apostle of Detroit": "Eparkiyang Katolikong Kaldeo ni Santo Tomas Apostol ng Detroit",
    "Byzantine Catholic Eparchy of Passaic": "Eparkiyang Katolikong Bisantino ng Passaic",
    "Syriac Catholic Eparchy of Our Lady of Deliverance in the United States": "Eparkiyang Katolikong Siryako ng Mahal na Birhen ng Kaligtasan sa Estados Unidos",
    "Eparchy of St. Maron of Brooklyn": "Eparkiyang Maronita ni San Maron ng Brooklyn",
    "Byzantine Catholic Eparchy of Parma": "Eparkiyang Katolikong Bisantino ng Parma",
    "Romanian Catholic Eparchy of St George's in Canton": "Eparkiyang Katolikong Rumano ni San Jorge sa Canton",
    "Ukrainian Catholic Eparchy of Saint Josaphat in Parma": "Eparkiyang Katolikong Ukranyano ni San Josafat sa Parma",
    "Byzantine Catholic Archeparchy of Pittsburgh": "Arkieparkiyang Katolikong Bisantino ng Pittsburgh",
    "Ukrainian Catholic Archeparchy of Philadelphia": "Arkieparkiyang Katolikong Ukranyano ng Philadelphia",
    "Archdiocese for the Military Services": "Arkidiyosesis para sa mga Serbisyong Militar",
    "Syro-Malankara Catholic Eparchy of St. Mary, Queen of Peace, of the United States of America and Canada": "Eparkiyang Siro-Malankara ni Santa Maria, Reyna ng Kapayapaan, ng Estados Unidos at Canada",
}


def dio_name(n, lang="en"):
    if lang == "en":
        return n
    if lang == "tl":
        if n in EP_TL:
            return EP_TL[n]
        for x, y in (("Archdiocese of", "Arkidiyosesis ng"), ("Diocese of", "Diyosesis ng")):
            if n.startswith(x):
                n = y + n[len(x):]
                break
        n = n.replace(" in America", " sa Amerika").replace(" in the Virgin Islands", ", Virgin Islands").replace("Saint Paul and Minneapolis", "Saint Paul at Minneapolis")
        return re.sub(r" in ([A-Z][a-z]+)$", r", \1", n)
    if n in EP_NAMES:
        return EP_NAMES[n][0 if lang == "es" else 1]
    pairs = ((("Archdiocese of", "Arquidiócesis de"), ("Diocese of", "Diócesis de")) if lang == "es"
             else (("Archdiocese of", "Arquidiocese de"), ("Diocese of", "Diocese de")))
    for x, y in pairs:
        if n.startswith(x):
            n = y + n[len(x):]
            break
    es = lang == "es"
    n = n.replace(" in America", " en América" if es else " na América").replace(" in the Virgin Islands", ", Islas Vírgenes" if es else ", Ilhas Virgens")
    n = n.replace("Saint Paul and Minneapolis", "Saint Paul y Minneapolis" if es else "Saint Paul e Minneapolis")
    m = re.search(r" in ([A-Z][a-z]+)$", n)
    if m:
        n = n[:m.start()] + ", " + STATE_NAME[lang].get(m.group(1), m.group(1))
    return n


def dio_name_es(n):
    return dio_name(n, "es")


DIO_BASE = {"en": "/dioceses", "es": "/es/diocesis", "pt": "/pt/dioceses", "tl": "/tl/mga-diyosesis"}
DIO_LANGS = ("en", "es", "pt", "tl")


def dio_rows(data, lang="en"):
    es = lang == "es"
    order = {"latin": 0, "eastern": 1, "nationwide": 2}
    ds = sorted(data["dioceses"], key=lambda d: (order[dio_kind(d)], d["states"][0] if d["states"] else "~", d["short"]))
    rows = []
    for d in ds:
        vac = {"en": "Vacant or not recorded", "es": "Vacante o sin dato", "pt": "Vacante ou sem dado", "tl": "Bakante o walang tala"}[lang]
        lead = html.escape(d.get("bishop", "")) or f'<span class="muted">{vac}</span>'
        nm = dio_name(d["short"], lang)
        rows.append(f'          <tr><td><a href="{DIO_BASE[lang]}/{d["slug"]}">{html.escape(nm)}</a></td>'
                    f'<td>{html.escape(dio_place(d, lang))}</td><td>{lead}</td></tr>')
    return "\n".join(rows), len(ds)


def _domain(url):
    return re.sub(r"^https?://(www\.)?", "", url or "").split("/")[0]


MESES = {"es": ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"],
         "pt": ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"],
         "tl": ["Enero", "Pebrero", "Marso", "Abril", "Mayo", "Hunyo", "Hulyo", "Agosto", "Setyembre", "Oktubre", "Nobyembre", "Disyembre"]}


def _since(x, lang="en"):
    m = re.match(r"(\d{4})-(\d{2})", x or "")
    if not m:
        return ""
    if lang in ("en", "tl"):
        return f"{(MONTHS if lang == 'en' else MESES['tl'])[int(m.group(2)) - 1]} {m.group(1)}"
    return f"{MESES[lang][int(m.group(2)) - 1]} de {m.group(1)}"


# Words for the diocese pages. {c} is the church word (diocese, archdiocese, eparchy), {l} the leader word.
DIO_TXT = {
    "en": dict(
        what={"diocese": "diocese", "archdiocese": "archdiocese", "eastern": "Eastern Catholic eparchy", "nationwide": "nationwide jurisdiction"},
        church={"diocese": "diocese", "archdiocese": "archdiocese", "eparchy": "eparchy"},
        lede_a="A Catholic {what}", lede_east="An Eastern Catholic eparchy", based=" based in {w}", founded=", founded in {y}",
        eastern_note=" Eparchies serve Eastern Catholics across a wide region, alongside the local Latin Church dioceses.",
        crumb="Dioceses", us="United States",
        leader={"Archbishop": "archbishop", "Bishop": "bishop"},
        who="Who leads it", since=", since {s}",
        who_note="From Wikidata. If a new {l} was named recently, the {c} website will have it first.",
        site="Official website", site_p="News, Mass times, schools, Catholic Charities, marriage preparation and contacts for every office.",
        site_lang="",
        cath="Cathedral", on_map="See it on a map",
        cath_p="The cathedral is the {l}&rsquo;s own church and the mother church of the {c}.",
        ocia_h="Thinking of becoming Catholic?",
        ocia_p="OCIA happens in parishes. Pick a parish near you, then call or email and ask when the next OCIA group starts. "
               "The {c}&rsquo;s Office of Worship (sometimes called Evangelization or Christian Initiation) can help if a parish doesn&rsquo;t answer.",
        ocia_link="How OCIA works", start="/start-here", find="/find-a-church", find_btn="Find parishes", near=" near {city}",
        search_btn="Search its website for OCIA", ocia_q="OCIA",
        size="Size", size_p="About <strong>{n}</strong> Catholics, according to the most recent figure in Wikidata.",
        holy_h="Holy men and women of {st}",
        holy_p="Saints, Blesseds, Venerables and Servants of God who were born or died in {st}. Some causes are led by this diocese; others by a neighboring diocese or a religious order.",
        sd="/saints-directory", holy_more="Wikidata does not record every cause yet. <a href=\"{sd}\">Search the full directory</a>.",
        others="Other dioceses in {st}",
        refs="History, parishes and statistics: {r}.", refs_none="see the {c} website",
        src="The details on this page come from <a href=\"https://www.wikidata.org/wiki/{q}\" rel=\"noopener\">Wikidata</a> (updated {u}), where anyone can correct them.",
        all="All U.S. dioceses",
        title="{n}: Bishop, Cathedral, OCIA and Parishes | CatholicDoorway",
        desc="{n}{st}: who leads it, its cathedral and website, how to find a parish and OCIA, and the holy men and women of the area.",
        rank={4: "Saint", 3: "Blessed", 2: "Venerable", 1: "Servant of God"}),
    "es": dict(
        what={"diocese": "diócesis", "archdiocese": "arquidiócesis", "eastern": "eparquía católica oriental", "nationwide": "jurisdicción para todo el país"},
        church={"diocese": "la diócesis", "archdiocese": "la arquidiócesis", "eparchy": "la eparquía"},
        lede_a="Una {what} católica", lede_east="Una eparquía católica oriental", based=" con sede en {w}", founded=", fundada en {y}",
        eastern_note=" Las eparquías atienden a los católicos orientales de una región amplia, junto a las diócesis latinas del lugar.",
        crumb="Diócesis", us="Estados Unidos",
        leader={"Archbishop": "el arzobispo", "Bishop": "el obispo"},
        who="Quién la dirige", since=", desde {s}",
        who_note="Dato de Wikidata. Si hace poco se nombró a un nuevo {l2}, el sitio web de {c} lo tendrá primero.",
        site="Sitio web oficial", site_p="Noticias, horarios de Misa, escuelas, Caridades Católicas, preparación matrimonial y los contactos de cada oficina.",
        site_lang=" Muchas diócesis tienen una sección en español o un ministerio hispano.",
        cath="Catedral", on_map="Verla en un mapa",
        cath_p="La catedral es la iglesia propia de{l3} y la iglesia madre de {c}.",
        ocia_h="¿Piensas hacerte católico?",
        ocia_p="OCIA se hace en las parroquias. Elige una parroquia cerca de ti y llama o escribe para preguntar cuándo empieza el próximo grupo. "
               "Si la parroquia no responde, la Oficina de Culto de {c} (a veces llamada de Evangelización, de Iniciación Cristiana o del Ministerio Hispano) puede ayudarte.",
        ocia_link="Cómo funciona OCIA", start="/es/comenzar", find="/es/buscar-iglesia", find_btn="Buscar parroquias", near=" cerca de {city}",
        search_btn="Buscar OCIA en su sitio web", ocia_q="OCIA español",
        size="Tamaño", size_p="Unos <strong>{n}</strong> católicos, según la cifra más reciente de Wikidata.",
        holy_h="Hombres y mujeres santos de {st}",
        holy_p="Santos, Beatos, Venerables y Siervos de Dios que nacieron o murieron en {st}. Algunas causas las lleva esta diócesis; otras, una diócesis vecina o una orden religiosa.",
        sd="/es/directorio-santos", holy_more="Wikidata todavía no registra todas las causas. <a href=\"{sd}\">Busca en el directorio completo</a>.",
        others="Otras diócesis de {st}",
        refs="Historia, parroquias y estadísticas: {r}.", refs_none="consulta el sitio web de {c}",
        src="Los datos de esta página vienen de <a href=\"https://www.wikidata.org/wiki/{q}?uselang=es\" rel=\"noopener\">Wikidata</a> (actualizado el {u}), donde cualquiera puede corregirlos.",
        all="Todas las diócesis de EE. UU.",
        title="{n}: obispo, catedral, OCIA y parroquias | CatholicDoorway",
        desc="{n}{st}: quién la dirige, su catedral y su sitio web, cómo encontrar una parroquia y OCIA, y los santos de la región.",
        rank={4: "Santo", 3: "Beato", 2: "Venerable", 1: "Siervo de Dios"}),
    "pt": dict(
        what={"diocese": "diocese", "archdiocese": "arquidiocese", "eastern": "eparquia católica oriental", "nationwide": "jurisdição para todo o país"},
        church={"diocese": "a diocese", "archdiocese": "a arquidiocese", "eparchy": "a eparquia"},
        lede_a="Uma {what} católica", lede_east="Uma eparquia católica oriental", based=" com sede em {w}", founded=", fundada em {y}",
        eastern_note=" As eparquias atendem os católicos orientais de uma região ampla, ao lado das dioceses latinas do lugar.",
        crumb="Dioceses", us="Estados Unidos",
        leader={"Archbishop": "o arcebispo", "Bishop": "o bispo"},
        who="Quem a dirige", since=", desde {s}",
        who_note="Dado do Wikidata. Se um novo {l2} foi nomeado há pouco, o site d{c} terá a notícia primeiro.",
        site="Site oficial", site_p="Notícias, horários de Missa, escolas, Cáritas (Catholic Charities), preparação para o matrimônio e os contatos de cada setor.",
        site_lang=" Algumas dioceses têm uma pastoral ou comunidade de língua portuguesa.",
        cath="Catedral", on_map="Ver no mapa",
        cath_p="A catedral é a igreja própria d{l3} e a igreja-mãe d{c}.",
        ocia_h="Pensando em se tornar católico?",
        ocia_p="A OCIA acontece nas paróquias. Escolha uma paróquia perto de você e ligue ou escreva para perguntar quando começa o próximo grupo. "
               "Se a paróquia não responder, o setor de liturgia d{c} (às vezes chamado de Evangelização, Iniciação Cristã ou Pastoral dos Imigrantes) pode ajudar.",
        ocia_link="Como funciona a OCIA", start="/pt/comecar", find="/pt/encontrar-igreja", find_btn="Procurar paróquias", near=" perto de {city}",
        search_btn="Procurar a OCIA no site", ocia_q="OCIA",
        size="Tamanho", size_p="Cerca de <strong>{n}</strong> católicos, segundo o número mais recente do Wikidata.",
        holy_h="Homens e mulheres santos de {st}",
        holy_p="Santos, Beatos, Veneráveis e Servos de Deus que nasceram ou morreram em {st}. Algumas causas são conduzidas por esta diocese; outras, por uma diocese vizinha ou por uma ordem religiosa.",
        sd="/pt/diretorio-santos", holy_more="O Wikidata ainda não registra todas as causas. <a href=\"{sd}\">Pesquise no diretório completo</a>.",
        others="Outras dioceses em {st}",
        refs="História, paróquias e estatísticas: {r}.", refs_none="veja o site d{c}",
        src="Os dados desta página vêm do <a href=\"https://www.wikidata.org/wiki/{q}?uselang=pt-br\" rel=\"noopener\">Wikidata</a> (atualizado em {u}), onde qualquer pessoa pode corrigi-los.",
        all="Todas as dioceses dos EUA",
        title="{n}: bispo, catedral, OCIA e paróquias | CatholicDoorway",
        desc="{n}{st}: quem a dirige, sua catedral e seu site, como encontrar uma paróquia e a OCIA, e os santos da região.",
        rank={4: "Santo", 3: "Beato", 2: "Venerável", 1: "Servo de Deus"}),
    "tl": dict(
        what={"diocese": "diyosesis", "archdiocese": "arkidiyosesis", "eastern": "eparkiyang Katolikong Silanganin", "nationwide": "hurisdiksiyon para sa buong bansa"},
        church={"diocese": "diyosesis", "archdiocese": "arkidiyosesis", "eparchy": "eparkiya"},
        lede_a="Isang {what} Katoliko", lede_east="Isang eparkiyang Katolikong Silanganin", based=" na nakabase sa {w}", founded=", itinatag noong {y}",
        eastern_note=" Naglilingkod ang mga eparkiya sa mga Katolikong Silanganin sa isang malawak na rehiyon, kasabay ng mga lokal na diyosesis ng Simbahang Latin.",
        crumb="Mga diyosesis", us="Estados Unidos",
        leader={"Archbishop": "arsobispo", "Bishop": "obispo"},
        who="Sino ang namumuno", since=", mula {s}",
        who_note="Mula sa Wikidata. Kung kamakailan lamang may itinalagang bagong {l}, unang makikita ito sa website ng {c}.",
        site="Opisyal na website", site_p="Mga balita, oras ng Misa, mga paaralan, Catholic Charities, paghahanda sa kasal at ang contact ng bawat tanggapan.",
        site_lang=" May ilang diyosesis na may ministeryo o komunidad para sa mga Pilipino.",
        cath="Katedral", on_map="Tingnan sa mapa",
        cath_p="Ang katedral ang sariling simbahan ng {l} at ang inang simbahan ng {c}.",
        ocia_h="Iniisip mo bang maging Katoliko?",
        ocia_p="Sa mga parokya ginaganap ang OCIA. Pumili ng parokya malapit sa iyo, saka tumawag o mag-email at itanong kung kailan magsisimula ang susunod na grupo. "
               "Kung hindi sumagot ang parokya, makatutulong ang Tanggapan ng Pagsamba ng {c} (minsan tinatawag na Ebanghelisasyon o Pagsisimula sa Buhay Kristiyano).",
        ocia_link="Paano gumagana ang OCIA", start="/tl/magsimula", find="/tl/hanapin-ang-simbahan", find_btn="Maghanap ng parokya", near=" malapit sa {city}",
        search_btn="Hanapin ang OCIA sa website nito", ocia_q="OCIA",
        size="Laki", size_p="Mga <strong>{n}</strong> Katoliko, ayon sa pinakabagong bilang sa Wikidata.",
        holy_h="Mga banal na lalaki at babae ng {st}",
        holy_p="Mga Santo, Beato, Benerable at Lingkod ng Diyos na isinilang o namatay sa {st}. May mga kausang pinangangasiwaan ng diyosesis na ito; ang iba, ng kalapit na diyosesis o ng isang relihiyosong orden.",
        sd="/tl/direktoryo-ng-mga-santo", holy_more="Hindi pa naitatala ng Wikidata ang lahat ng kausa. <a href=\"{sd}\">Maghanap sa buong direktoryo</a>.",
        others="Iba pang diyosesis sa {st}",
        refs="Kasaysayan, mga parokya at estadistika: {r}.", refs_none="tingnan ang website ng {c}",
        src="Ang mga detalye sa pahinang ito ay mula sa <a href=\"https://www.wikidata.org/wiki/{q}?uselang=tl\" rel=\"noopener\">Wikidata</a> (na-update noong {u}), kung saan maaaring itama ito ng sinuman.",
        all="Lahat ng diyosesis sa Estados Unidos",
        title="{n}: obispo, katedral, OCIA at mga parokya | CatholicDoorway",
        desc="{n}{st}: sino ang namumuno, ang katedral at website nito, paano maghanap ng parokya at OCIA, at ang mga banal ng rehiyon.",
        rank={4: "Santo", 3: "Beato", 2: "Benerable", 1: "Lingkod ng Diyos"}),

}


def _num(n, lang):
    s = f"{n:,}"
    return s.replace(",", ".") if lang == "pt" else s


def diocese_body(d, data, lang="en"):
    e = html.escape
    L = DIO_TXT[lang]
    stn = lambda x: STATE_NAME.get(lang, {}).get(x, x)
    kind = dio_kind(d)
    st = d["states"][0] if d["states"] else ""
    st_l = stn(st)
    city = d.get("city", "")
    where = ", ".join(x for x in (city, st_l) if x)
    arch = d["short"].startswith("Archdiocese")
    wkey = {"latin": "archdiocese" if arch else "diocese", "eastern": "eastern", "nationwide": "nationwide"}[kind]
    if kind == "nationwide":
        wkey = "archdiocese"
    lede = (L["lede_east"] if kind == "eastern" else L["lede_a"].format(what=L["what"][wkey])) + (L["based"].format(w=e(where)) if where else "") + \
        (L["founded"].format(y=d["founded"]) if d.get("founded") else "") + "."
    if kind == "eastern":
        lede += L["eastern_note"]
    lead = dio_leader(d)
    ckey = "eparchy" if kind == "eastern" else ("archdiocese" if arch else "diocese")
    church = L["church"][ckey]
    lword = L["leader"][lead]
    # Spanish/Portuguese contractions: "de + el obispo" -> "del obispo", "d + o bispo" -> "do bispo"
    if lang == "es":
        l2, l3 = lword.split(" ", 1)[1], "l " + lword.split(" ", 1)[1]
        c_of = church
    elif lang == "pt":
        l2, l3 = lword.split(" ", 1)[1], lword
        c_of = church
    elif lang == "tl":
        l2 = l3 = lword
        c_of = church
    else:
        l2 = l3 = lword
        c_of = church
    if lang == "es" and kind == "eastern":
        l2 = {"Archbishop": "arzobispo (archieparca)", "Bishop": "obispo (eparca)"}[lead]
    if lang == "tl" and kind == "eastern":
        l2 = l3 = {"Archbishop": "arsobispo (arkieparka)", "Bishop": "obispo (eparka)"}[lead]
    if lang == "pt" and kind == "eastern":
        l2 = {"Archbishop": "arcebispo (arquieparca)", "Bishop": "bispo (eparca)"}[lead]
    name = dio_name(d["short"], lang)
    base = DIO_BASE[lang]
    out = ['<div class="page-head">\n  <div class="wrap">',
           f'    <p class="kicker"><a href="{base}">{L["crumb"]}</a> &rsaquo; {e(st_l or L["us"])}</p>',
           f'    <h1>{e(name)}</h1>',
           f'    <p class="lede">{lede}</p>',
           '  </div>\n</div>\n\n<div class="wrap">\n  <section class="section">\n    <div class="grid two">']
    if d.get("bishop"):
        since = _since(d.get("bishop_since"), lang)
        out.append(f'      <div class="card">\n        <h3>{L["who"]}</h3>'
                   f'\n        <p><strong>{e(d["bishop"])}</strong>{L["since"].format(s=since) if since else ""}.</p>'
                   f'\n        <p class="small muted">{L["who_note"].format(l=l2, l2=l2, c=c_of)}</p>\n      </div>')
    if d.get("website"):
        out.append(f'      <div class="card">\n        <h3>{L["site"]}</h3>'
                   f'\n        <p>{L["site_p"]}{L["site_lang"] if kind == "latin" else ""}</p>'
                   f'\n        <div class="btn-row" style="justify-content:flex-start"><a class="btn" href="{e(d["website"])}" rel="noopener">{e(_domain(d["website"]))}</a></div>\n      </div>')
    if d.get("cathedral"):
        mp = (f' <a href="https://www.openstreetmap.org/?mlat={d["lat"]}&amp;mlon={d["lon"]}#map=17/{d["lat"]}/{d["lon"]}" rel="noopener">{L["on_map"]}</a>.'
              if d.get("lat") else "")
        town = f", {e(city)}" if city and city not in d["cathedral"] else ""
        out.append(f'      <div class="card">\n        <h3>{L["cath"]}</h3>'
                   f'\n        <p><strong>{e(d["cathedral"])}</strong>{town}. {L["cath_p"].format(l=l3, l3=l3, c=c_of)}{mp}</p>\n      </div>')
    q = urllib.parse.quote(", ".join(x for x in (city, st) if x) or d["short"])
    dom = _domain(d.get("website"))
    near = L["near"].format(city=e(city)) if city and kind == "latin" else ""
    ocia = (f'\n          <a class="btn secondary" href="https://duckduckgo.com/?q={urllib.parse.quote(L["ocia_q"] + " site:" + dom)}" rel="noopener">{L["search_btn"]}</a>'
            if dom else "")
    out.append(f'      <div class="card">\n        <h3>{L["ocia_h"]}</h3>'
               f'\n        <p>{L["ocia_p"].format(c=c_of)} <a href="{L["start"]}">{L["ocia_link"]}</a>.</p>'
               f'\n        <div class="btn-row" style="justify-content:flex-start">\n          <a class="btn" href="{L["find"]}?ocia=1&amp;q={q}">{L["find_btn"]}{near}</a>{ocia}\n        </div>\n      </div>')
    if d.get("members"):
        out.append(f'      <div class="card">\n        <h3>{L["size"]}</h3>'
                   f'\n        <p>{L["size_p"].format(n=_num(d["members"], lang))}</p>\n      </div>')
    out.append("    </div>\n  </section>")

    holy = data["holy_by_state"].get(st, []) if kind == "latin" and st else []
    if holy:
        items = []
        for p in holy:
            yrs = f' <span class="small muted">({p["born"]}&ndash;{p["died"]})</span>' if p["born"] and p["died"] else ""
            items.append(f'<li><a href="{L["sd"]}?q={urllib.parse.quote(p["name"])}">{e(p["name"])}</a> '
                         f'<span class="status {RANK_CLS[p["rank"]]}">{L["rank"][p["rank"]]}</span>{yrs}</li>')
        out.append(f'\n  <section class="section">\n    <h2>{L["holy_h"].format(st=e(st_l))}</h2>'
                   f'\n    <p class="prose">{L["holy_p"].format(st=e(st_l))}</p>'
                   f'\n    <ul class="holy-list">\n      ' + "\n      ".join(items) + '\n    </ul>'
                   f'\n    <p class="small muted">{L["holy_more"].format(sd=L["sd"])}</p>\n  </section>')

    others = sorted((o for o in data["dioceses"] if o is not d and st and st in o["states"] and dio_kind(o) == "latin"),
                    key=lambda o: o["short"]) if kind == "latin" else []
    if others:
        links = " &middot; ".join(f'<a href="{base}/{o["slug"]}">{e(dio_name(o["short"], lang))}</a>' for o in others)
        out.append(f'\n  <section class="section">\n    <h2>{L["others"].format(st=e(st_l))}</h2>\n    <p>{links}</p>\n  </section>')

    refs = []
    if d.get("ch"):
        refs.append(f'<a href="https://www.catholic-hierarchy.org/diocese/d{e(d["ch"])}.html" rel="noopener">Catholic-Hierarchy</a>')
    if d.get("gc"):
        refs.append(f'<a href="https://gcatholic.org/dioceses/diocese/{e(d["gc"])}.htm" rel="noopener">GCatholic</a>')
    out.append('\n  <section class="section">'
               f'\n    <p class="small muted">{L["refs"].format(r=" &middot; ".join(refs) or L["refs_none"].format(c=c_of))} '
               f'{L["src"].format(q=d["qid"], u=data["updated"])} <a href="{base}">{L["all"]}</a>.</p>'
               '\n  </section>\n</div>\n')
    return "\n".join(out)


def build_dioceses(data):
    keep_all = {}
    for lang, text, foot in (("en", EN_TEXT, FOOT), ("es", ES_TEXT, FOOT_ES), ("pt", PT_TEXT, FOOT_PT), ("tl", TL_TEXT, FOOT_TL)):
        if lang not in DIO_LANGS:
            continue
        base = DIO_BASE[lang]
        out_dir = OUT / base.strip("/")
        out_dir.mkdir(parents=True, exist_ok=True)
        L = DIO_TXT[lang]
        nav = {"en": lambda: nav_html("dioceses"),
               "es": lambda: lang_nav("es", ES_PAGES, ES_SUBNAV, ES_NAV_EXCLUDE, "diocesis"),
               "pt": lambda: lang_nav("pt", PT_PAGES, PT_SUBNAV, PT_NAV_EXCLUDE, "dioceses"),
               "tl": lambda: lang_nav("tl", TL_PAGES, TL_SUBNAV, TL_NAV_EXCLUDE, "mga-diyosesis")}[lang]()
        keep = set()
        for d in data["dioceses"]:
            nm = dio_name(d["short"], lang)
            st = ", ".join(STATE_NAME.get(lang, {}).get(x, x) for x in d["states"])
            title = L["title"].format(n=nm)
            desc = L["desc"].format(n=nm, st=f" ({st})" if st else "")
            urls = {c: (f"{DIO_BASE[c]}/{d['slug']}" if c in DIO_LANGS else None) for c in ("en", "es", "pt", "tl")}
            page = HEAD.format(title=html.escape(title), desc=html.escape(desc), canonical=f"{DOMAIN}{base}/{d['slug']}",
                               domain=DOMAIN, slug="dioceses", door=DOOR_SVG, menu=MENU_SVG, theme=THEME_SVG,
                               nav=nav, extra_head="", alternates=alternates_html(urls),
                               lang_menu=lang_menu(lang, urls), **text)
            if lang != "en":
                page = page.replace('<meta property="og:site_name" content="CatholicDoorway">',
                                    f'<meta property="og:site_name" content="CatholicDoorway">\n<meta property="og:locale" content="{LOCALE[lang]}">')
            page += diocese_body(d, data, lang) + foot.format(extra_foot="")
            dio_ld = {"@type": "Organization", "name": d["name"], "description": desc}
            if d.get("website"):
                dio_ld["url"] = d["website"]
            if d.get("qid"):
                dio_ld["sameAs"] = f"https://www.wikidata.org/wiki/{d['qid']}"
            idx = DIO_BASE[lang]
            idx_name = {"en": "Dioceses", "es": "Diócesis", "pt": "Dioceses", "tl": "Mga diyosesis"}[lang]
            page = seo(page, lang, f"{base}/{d['slug']}",
                       crumbs=[(HOME_WORD[lang], LANG_HOME[lang]), (idx_name, idx), (nm, f"{base}/{d['slug']}")],
                       extra=[dict(dio_ld, **{"subjectOf": {"@id": f"{DOMAIN}{base}/{d['slug']}#webpage"}})])
            (out_dir / f"{d['slug']}.html").write_text(bust(page), encoding="utf-8")
            keep.add(f"{d['slug']}.html")
        for old in out_dir.glob("*.html"):
            if old.name not in keep:
                old.unlink()
        print(f"built {len(keep)} diocese pages ({lang})")
    return sorted(d["slug"] for d in data["dioceses"])



# ---------- Search and AI-answer metadata (JSON-LD, social cards) ----------
OG_LOCALE = {"en": "en_US", "es": "es_US", "pt": "pt_BR", "tl": "tl_PH"}
SITE_DESC = {"en": "A free, ad-free guide to the Catholic faith: prayers, the Bible, daily readings, finding a church, OCIA, saints and more.",
             "es": "Una guía gratuita y sin anuncios de la fe católica: oraciones, la Biblia, lecturas del día, cómo encontrar una iglesia, OCIA, santos y más.",
             "pt": "Um guia gratuito e sem anúncios da fé católica: orações, a Bíblia, leituras do dia, como encontrar uma igreja, OCIA, santos e mais.",
             "tl": "Isang libre at walang patalastas na gabay sa pananampalatayang Katoliko: mga dasal, ang Bibliya, mga pagbasa sa araw-araw, paghahanap ng simbahan, OCIA, mga santo at iba pa."}
HOME_WORD = {"en": "Home", "es": "Inicio", "pt": "Início", "tl": "Tahanan"}
OG_ALT = "CatholicDoorway: I am the door; if any one enters by me, he will be saved. (John 10:9)"


def _strip(x):
    return html.unescape(re.sub(r"<[^>]+>", "", x)).strip()


def site_ld():
    org = {"@type": "Organization", "@id": f"{DOMAIN}/#org", "name": "CatholicDoorway", "url": f"{DOMAIN}/",
           "logo": f"{DOMAIN}/assets/img/logo.png", "email": "hello@catholicdoorway.com"}
    site = {"@type": "WebSite", "@id": f"{DOMAIN}/#website", "name": "CatholicDoorway", "url": f"{DOMAIN}/",
            "description": SITE_DESC["en"], "inLanguage": ["en", "es", "pt", "tl"], "publisher": {"@id": f"{DOMAIN}/#org"}}
    return [org, site]


def faq_ld(lang):
    data = json.loads((ROOT / "src" / "data" / ("questions.json" if lang == "en" else f"questions_{lang}.json")).read_text(encoding="utf-8"))
    return {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": _strip(q["q"]),
         "acceptedAnswer": {"@type": "Answer", "text": " ".join(_strip(a) for a in q["a"])}} for q in data]}


def seo(page, lang, url, crumbs=None, extra=None):
    """Adds social-card tags and a JSON-LD graph to a built page's <head>."""
    title = _strip(re.search(r"<title>(.*?)</title>", page, re.S).group(1))
    desc = _strip(re.search(r'<meta name="description" content="([^"]*)"', page).group(1))
    graph = site_ld()
    webpage = {"@type": "WebPage", "@id": f"{DOMAIN}{url}#webpage", "url": f"{DOMAIN}{url}", "name": title,
               "description": desc, "inLanguage": lang, "isPartOf": {"@id": f"{DOMAIN}/#website"},
               "publisher": {"@id": f"{DOMAIN}/#org"}, "primaryImageOfPage": f"{DOMAIN}/assets/img/og.png"}
    if crumbs:
        webpage["breadcrumb"] = {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": f"{DOMAIN}{u}"} for i, (n, u) in enumerate(crumbs)]}
    graph.append(webpage)
    for e in (extra or []):
        e = dict(e)
        if e.get("@type") == "FAQPage":
            e["@id"] = f"{DOMAIN}{url}#faq"
            e["isPartOf"] = {"@id": f"{DOMAIN}{url}#webpage"}
        graph.append(e)
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    tags = []
    if 'property="og:locale"' not in page:
        tags.append(f'<meta property="og:locale" content="{OG_LOCALE[lang]}">')
    tags += ['<meta property="og:image:width" content="1200">', '<meta property="og:image:height" content="630">',
             f'<meta property="og:image:alt" content="{html.escape(OG_ALT)}">',
             '<meta name="twitter:card" content="summary_large_image">',
             '<link rel="apple-touch-icon" href="/assets/img/logo.png">',
             f'<script type="application/ld+json">{ld}</script>']
    return page.replace("</head>", "\n".join(tags) + "\n</head>", 1)


def version(rel):
    """Short content hash so browsers fetch new CSS/JS as soon as it changes."""
    return hashlib.sha1((OUT / rel.lstrip("/")).read_bytes()).hexdigest()[:10]


def bust(page):
    for rel in ("/assets/css/style.css", "/assets/js/main.js", "/assets/js/map.js", "/assets/js/rosary.js", "/assets/js/saints-dir.js", "/assets/js/pray.js"):
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
                          ("confesion", "Cómo confesarse"), ("examen-de-conciencia", "Examen de conciencia"), ("volver", "Volver a la Iglesia")],
             "oraciones": [("oraciones", "Oraciones católicas"), ("rosario", "Reza el Rosario"), ("devociones", "Devociones y recordatorios"),
                           ("liturgia-de-las-horas", "Liturgia de las Horas")],
             "biblia": [("biblia", "Las lecturas de hoy y la Biblia"), ("calendario", "Calendario de días santos")],
             "creencias": [("creencias", "Lo que creen los católicos"), ("preguntas", "Preguntas sinceras"), ("glosario", "Glosario"),
                           ("documentos-de-la-iglesia", "El Catecismo y los documentos")],
             "santos": [("santos", "Conoce a los santos"), ("directorio-santos", "Directorio de santos y causas")],
             "estructura": [("estructura", "Cómo se organiza la Iglesia"), ("papas", "Los 267 Papas"), ("diocesis", "Las diócesis de EE. UU."),
                            ("buscar-iglesia", "Buscar una iglesia")]}
ES_SUB_CHILDREN = {c for subs in ES_SUBNAV.values() for c, _ in subs} - set(ES_SUBNAV)
# Spanish pages reached from a hub page rather than the top menu
ES_NAV_EXCLUDE = {"coronilla-de-la-divina-misericordia", "via-crucis", "novenas", "angelus", "registrar-ocia", "acerca", "inscribirse-parroquia", "bautismo", "matrimonio", "uncion", "funerales", "fe-de-bautismo"}


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


LOCALE = {"es": "es_US", "pt": "pt_BR", "tl": "tl_PH"}


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
        body = features.render(body, code)
        body = ocia_options(body, code)
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
        crumbs = None if sl == "index" else [(HOME_WORD[code], LANG_HOME[code]), (label, url)]
        page = seo(page, code, url, crumbs=crumbs, extra=[faq_ld(code)] if en == "questions" else None)
        (out_dir / f"{sl}.html").write_text(bust(page), encoding="utf-8")
        print(f"built {code}/{sl}")


def build_es():
    build_lang("es", ES_PAGES, ES_TEXT, FOOT_ES, ES_SUBNAV, ES_NAV_EXCLUDE)


def build_pt():
    build_lang("pt", PT_PAGES, PT_TEXT, FOOT_PT, PT_SUBNAV, PT_NAV_EXCLUDE)


def build_tl():
    build_lang("tl", TL_PAGES, TL_TEXT, FOOT_TL, TL_SUBNAV, TL_NAV_EXCLUDE)


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
        body = features.render(body, "en")
        body = ocia_options(body, "en")
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
        if slug != "404":
            url = "/" if slug == "index" else f"/{slug}"
            crumbs = None if slug == "index" else [(HOME_WORD["en"], "/"), (label, url)]
            page = seo(page, "en", url, crumbs=crumbs, extra=[faq_ld("en")] if slug == "questions" else None)
        (OUT / f"{slug}.html").write_text(bust(page), encoding="utf-8")
        print("built", slug)

    build_es()
    build_pt()
    build_tl()
    dio_slugs = build_dioceses(dio_data)

    write_sitemap(dio_slugs)
    write_llms(len(dio_slugs))
    write_saint_days()
    features.write_worker_data(ROOT)


LLMS_GROUPS = [
    ("Becoming Catholic and practical guides", ["start-here", "first-mass", "how-to", "confession", "examination-of-conscience", "coming-back",
                                               "join-a-parish", "baptism", "marriage", "anointing", "funerals", "baptism-certificate", "ocia-listing"]),
    ("Prayer, Scripture and the calendar", ["prayers", "rosary", "devotions", "divine-mercy-chaplet", "stations-of-the-cross", "novenas", "angelus",
                                            "liturgy-of-the-hours", "bible", "calendar"]),
    ("What Catholics believe", ["beliefs", "questions", "church-documents", "glossary"]),
    ("Saints, Popes and Church structure", ["saints", "saints-directory", "popes", "structure", "dioceses", "find-a-church"]),
    ("About", ["about"]),
]


def write_llms(dio_count):
    """llms.txt: a plain map of the site for AI assistants and answer engines."""
    info = {s: (title.replace(" | CatholicDoorway", ""), desc) for s, _, title, desc in PAGES}
    out = ["# CatholicDoorway", "",
           "> " + SITE_DESC["en"] + " Written for Catholics and for anyone exploring the faith or starting OCIA "
           "(the Order of Christian Initiation of Adults). Free, no ads, no sign-up. English, Spanish, Portuguese and Filipino (Tagalog).", "",
           "Content follows the teaching of the Catholic Church and cites the Catechism of the Catholic Church and Scripture. "
           "U.S. focused for parishes, dioceses and holy days. Saint and diocese data come from Wikidata (CC0) and are refreshed weekly; "
           "the church map uses OpenStreetMap data. Corrections: hello@catholicdoorway.com.", ""]
    for head, slugs in LLMS_GROUPS:
        out.append(f"## {head}")
        out.append("")
        for sl in slugs:
            t, d = info[sl]
            out.append(f"- [{t}]({DOMAIN}/{sl}): {d}")
        out.append("")
    out += ["## Other languages", "",
            f"- [Español]({DOMAIN}/es/): " + SITE_DESC["es"],
            f"- [Português]({DOMAIN}/pt/): " + SITE_DESC["pt"],
            f"- [Filipino (Tagalog)]({DOMAIN}/tl/): " + SITE_DESC["tl"], "",
            "## Data", "",
            f"- [Diocese pages]({DOMAIN}/dioceses): one page for each of {dio_count} U.S. dioceses, archdioceses and eparchies at /dioceses/<slug>.",
            f"- [Saints directory data]({DOMAIN}/data/saints-directory.json): JSON list of Saints, Blesseds, Venerables and Servants of God.",
            f"- [Holy days calendar]({DOMAIN}/api/calendar.json): JSON feed of U.S. holy days of obligation, fast days and major feasts (also .ics).",
            f"- [Prayer reminders]({DOMAIN}/api/devotions.ics): iCalendar feed of Angelus, 3 p.m. Divine Mercy, Lenten Stations and novena reminders.",
            f"- [Saint of the day]({DOMAIN}/data/saint-days.json): the fixed-date celebrations of the U.S. General Roman Calendar (MM-DD keys).",
            f"- [Sitemap]({DOMAIN}/sitemap.xml)", ""]
    (OUT / "llms.txt").write_text("\n".join(out), encoding="utf-8")


def page_file(u):
    return OUT / ("index.html" if u == "/" else (u.strip("/") + "/index.html" if u.endswith("/") else u.lstrip("/") + ".html"))


def write_sitemap(dio_slugs):
    """lastmod only moves when a page's content really changes, so search engines can trust it."""
    paths = [("/" if s == "index" else "/" + s) for s, *_ in PAGES if s != "404"]
    paths += [f"/es/{'' if es == 'index' else es}" for _, es, *_ in ES_PAGES]
    paths += [f"/pt/{'' if pt == 'index' else pt}" for _, pt, *_ in PT_PAGES]
    paths += [f"/tl/{'' if tl == 'index' else tl}" for _, tl, *_ in TL_PAGES]
    paths += [f"{DIO_BASE[c]}/{s}" for c in DIO_LANGS for s in dio_slugs]
    state_file = ROOT / "src" / "data" / "sitemap-state.json"
    state = json.loads(state_file.read_text(encoding="utf-8")) if state_file.exists() else {}
    today = datetime.date.today().isoformat()
    new_state, rows = {}, []
    for u in paths:
        text = re.sub(r"\?v=[0-9a-f]{10}", "", page_file(u).read_text(encoding="utf-8"))
        h = hashlib.sha1(text.encode("utf-8")).hexdigest()[:16]
        old = state.get(u)
        lastmod = old[1] if old and old[0] == h else today
        new_state[u] = [h, lastmod]
        rows.append(f"  <url><loc>{DOMAIN}{u}</loc><lastmod>{lastmod}</lastmod></url>")
    state_file.write_text(json.dumps(new_state, indent=0, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(rows) + "\n</urlset>\n", encoding="utf-8")


if __name__ == "__main__":
    main()
