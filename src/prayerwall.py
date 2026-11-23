"""Prayer Wall page, in four languages.

The page body is just {{PRAYER_WALL}}; render() replaces it with:
  1. a crisis help box (988 in the U.S., plus local lines for Spanish, Portuguese and Filipino readers),
  2. the wall itself, filled by site/assets/js/prayerwall.js from /api/prayers.json,
     with an "I prayed" button and count on each request,
  3. the form to ask for prayer (public or private), sent to /api/prayer-request (worker/prayers.js),
  4. a prayer for everyone on the wall.

Every request is reviewed before it appears and is deleted 30 days after it was sent.
"""
import html
import json

e = html.escape


T = {
    "en": dict(
        kicker='<a href="/prayers">Prayers</a> &rsaquo; Prayer Wall',
        h1="Prayer Wall",
        lede="Ask for prayer, and pray for others. Share an intention with a first name or anonymously, and tap <em>I prayed</em> when you have prayed for someone. No account, no sign-up, nothing to buy.",
        crisis_h="In crisis or thinking about suicide?",
        crisis="You don&rsquo;t have to carry this alone, and you don&rsquo;t have to wait. In the U.S., call or text <strong>988</strong> (Suicide &amp; Crisis Lifeline) any time, day or night. If someone is in immediate danger, call <strong>911</strong>.",
        crisis_btns='<a class="btn small" href="tel:988">Call 988</a> <a class="btn small secondary" href="sms:988">Text 988</a> <a class="btn small secondary" href="https://988lifeline.org/chat/" target="_blank" rel="noopener">Chat online</a>',
        crisis_more='Outside the U.S., find a free helpline at <a href="https://findahelpline.com/" target="_blank" rel="noopener">findahelpline.com</a>. A priest can also visit or talk with you: call any <a href="/find-a-church">Catholic parish</a>.',
        toc=[("wall", "Pray for others"), ("ask", "Ask for prayer"), ("for-all", "A prayer for everyone here")],
        wall_h="Pray for others",
        wall_p="Each request was sent by a visitor and read by our small team before it appeared. Requests stay for 30 days. Pray in your own words, or with a Hail Mary, then tap <em>I prayed</em> so the person knows they are not alone.",
        all_langs="All languages", loading="Loading prayer requests…",
        ask_h="Ask for prayer",
        ask_p="Tell us what you would like prayer for. Our team prays for every request we receive, including private ones.",
        f_req='Fields marked <span class="req">*</span> are required.', f_name="Your first name", f_name_hint="Optional. Leave it blank to post as &ldquo;Anonymous&rdquo;.",
        f_text="Your prayer request", f_text_ph="For example: Please pray for my mom, who starts chemotherapy this week, and for our family.",
        f_private="Keep it private: don&rsquo;t post it on the wall. Only our team will read it and pray for you.",
        f_send="Send my request",
        rules_h="Before you send",
        rules=["Use first names only. Please leave out last names, phone numbers, addresses and private details about other people.",
               "Every request is read before it appears, usually within a day. We may shorten a request, or keep it private, to protect you or someone else.",
               "No links, ads or fundraising. Requests are removed automatically after 30 days.",
               "Under 13? Ask a parent before you post."],
        f_legal='How we handle what you send: <a href="/privacy#prayer-wall">Privacy Policy</a> and <a href="/terms#prayer-wall">Terms of Use</a>.',
        all_h="A prayer for everyone on this wall",
        all_p="Pray this for all who have asked for prayer here, by name if you like.",
        all_text="Lord Jesus, you told us to ask, to seek and to knock.\nWe bring before you everyone who has asked for prayer here,\nand every need they carry in their hearts.\nHeal the sick, comfort those who grieve,\ngive work to those who need it, peace to the anxious\nand hope to those who feel alone.\nHoly Mary, Mother of God, and all the saints, pray for them.\nAmen.",
        more_h="More ways to ask for prayer",
        more=[("Have a Mass offered", "Call your parish office and ask to have a Mass said for your intention, for someone who is sick or for someone who has died. A small offering is customary but never required."),
              ("Ask your parish", "Many parishes have a prayer chain or a book of intentions near the door. Priests and deacons are glad to pray with you in person."),
              ("Pray the Rosary for someone", 'Offer a <a href="/rosary">Rosary</a> for a person on this wall. Each decade can be for a different intention.')],
        note="Requests on the Prayer Wall are written by visitors. CatholicDoorway reads each one before it appears but cannot check what it says.",
    ),
    "es": dict(
        kicker='<a href="/es/oraciones">Oraciones</a> &rsaquo; Muro de oración',
        h1="Muro de oración",
        lede="Pide oración y reza por los demás. Comparte una intención con tu nombre de pila o de forma anónima, y toca <em>Recé</em> cuando hayas rezado por alguien. Sin cuenta, sin registro y gratis.",
        crisis_h="¿Estás en crisis o piensas en el suicidio?",
        crisis="No tienes que cargar esto solo ni esperar. En EE. UU., llama o envía un mensaje de texto al <strong>988</strong> (Línea de Prevención del Suicidio y Crisis) a cualquier hora; para español, marca 2 o escribe AYUDA al 988. Si alguien corre peligro inmediato, llama al <strong>911</strong>.",
        crisis_btns='<a class="btn small" href="tel:988">Llamar al 988</a> <a class="btn small secondary" href="sms:988?body=AYUDA">Texto al 988</a> <a class="btn small secondary" href="https://988lifeline.org/es/chat/" target="_blank" rel="noopener">Chat en línea</a>',
        crisis_more='En México, la Línea de la Vida atiende las 24 horas en el <a href="tel:8009112000">800 911 2000</a>. En otros países, busca una línea gratuita en <a href="https://findahelpline.com/" target="_blank" rel="noopener">findahelpline.com</a>. Un sacerdote también puede visitarte o hablar contigo: llama a cualquier <a href="/es/buscar-iglesia">parroquia católica</a>.',
        toc=[("wall", "Reza por los demás"), ("ask", "Pide oración"), ("for-all", "Una oración por todos")],
        wall_h="Reza por los demás",
        wall_p="Cada petición la envió un visitante y nuestro pequeño equipo la leyó antes de publicarla. Las peticiones se quedan 30 días. Reza con tus propias palabras o con un Avemaría, y luego toca <em>Recé</em> para que la persona sepa que no está sola.",
        all_langs="Todos los idiomas", loading="Cargando peticiones…",
        ask_h="Pide oración",
        ask_p="Cuéntanos por qué quieres que recemos. Nuestro equipo reza por cada petición que recibe, también por las privadas.",
        f_req='Los campos marcados con <span class="req">*</span> son obligatorios.', f_name="Tu nombre de pila", f_name_hint="Opcional. Déjalo en blanco para publicarla como «Anónimo».",
        f_text="Tu petición de oración", f_text_ph="Por ejemplo: Recen por mi mamá, que empieza la quimioterapia esta semana, y por nuestra familia.",
        f_private="Mantenerla privada: no publicarla en el muro. Solo nuestro equipo la leerá y rezará por ti.",
        f_send="Enviar mi petición",
        rules_h="Antes de enviar",
        rules=["Usa solo nombres de pila. No incluyas apellidos, teléfonos, direcciones ni detalles privados de otras personas.",
               "Leemos cada petición antes de publicarla, por lo general en un día. Podemos acortarla o mantenerla privada para protegerte a ti o a otra persona.",
               "Sin enlaces, anuncios ni colectas. Las peticiones se borran solas a los 30 días.",
               "¿Tienes menos de 13 años? Pide permiso a tu papá o a tu mamá antes de publicar."],
        f_legal='Cómo tratamos lo que envías: <a href="/es/privacidad#prayer-wall">Política de privacidad</a> y <a href="/es/terminos#prayer-wall">Términos de uso</a>.',
        all_h="Una oración por todos los de este muro",
        all_p="Reza por todos los que pidieron oración aquí, si quieres, por su nombre.",
        all_text="Señor Jesús, tú nos dijiste que pidiéramos, buscáramos y llamáramos.\nTe presentamos a todos los que pidieron oración aquí\ny cada necesidad que llevan en el corazón.\nSana a los enfermos, consuela a los que lloran,\nda trabajo a quien lo necesita, paz a los angustiados\ny esperanza a los que se sienten solos.\nSanta María, Madre de Dios, y todos los santos, rueguen por ellos.\nAmén.",
        more_h="Otras formas de pedir oración",
        more=[("Pide que se ofrezca una Misa", "Llama a la oficina de tu parroquia y pide una Misa por tu intención, por un enfermo o por un difunto. Se acostumbra dar un pequeño donativo, pero nunca es obligatorio."),
              ("Pregunta en tu parroquia", "Muchas parroquias tienen una cadena de oración o un libro de intenciones junto a la puerta. Los sacerdotes y diáconos rezan contigo con gusto."),
              ("Reza el Rosario por alguien", 'Ofrece un <a href="/es/rosario">Rosario</a> por una persona de este muro. Cada misterio puede ser por una intención distinta.')],
        note="Las peticiones del Muro de oración las escriben los visitantes. CatholicDoorway lee cada una antes de publicarla, pero no puede comprobar lo que dice.",
    ),
    "pt": dict(
        kicker='<a href="/pt/oracoes">Orações</a> &rsaquo; Mural de oração',
        h1="Mural de oração",
        lede="Peça oração e reze pelos outros. Compartilhe uma intenção com o seu primeiro nome ou de forma anônima, e toque em <em>Rezei</em> quando tiver rezado por alguém. Sem conta, sem cadastro e de graça.",
        crisis_h="Em crise ou pensando em suicídio?",
        crisis="Você não precisa carregar isso sozinho nem esperar. No Brasil, ligue para o <strong>CVV, 188</strong>, de graça e a qualquer hora, ou converse pelo chat em cvv.org.br. Nos EUA, ligue ou mande mensagem para o <strong>988</strong>. Se alguém corre perigo imediato, ligue para o <strong>192</strong> (SAMU) no Brasil ou o <strong>911</strong> nos EUA.",
        crisis_btns='<a class="btn small" href="tel:188">Ligar para o 188</a> <a class="btn small secondary" href="https://cvv.org.br/" target="_blank" rel="noopener">Chat do CVV</a> <a class="btn small secondary" href="tel:988">EUA: 988</a>',
        crisis_more='Em outros países, encontre uma linha gratuita em <a href="https://findahelpline.com/" target="_blank" rel="noopener">findahelpline.com</a>. Um padre também pode visitar você ou conversar: ligue para qualquer <a href="/pt/encontrar-igreja">paróquia católica</a>.',
        toc=[("wall", "Reze pelos outros"), ("ask", "Peça oração"), ("for-all", "Uma oração por todos")],
        wall_h="Reze pelos outros",
        wall_p="Cada pedido foi enviado por um visitante e lido pela nossa pequena equipe antes de aparecer. Os pedidos ficam 30 dias. Reze com as suas palavras ou com uma Ave-Maria, depois toque em <em>Rezei</em> para que a pessoa saiba que não está sozinha.",
        all_langs="Todos os idiomas", loading="Carregando pedidos…",
        ask_h="Peça oração",
        ask_p="Conte para nós pelo que você quer que rezemos. A nossa equipe reza por cada pedido que recebe, inclusive os particulares.",
        f_req='Os campos marcados com <span class="req">*</span> são obrigatórios.', f_name="Seu primeiro nome", f_name_hint="Opcional. Deixe em branco para aparecer como “Anônimo”.",
        f_text="Seu pedido de oração", f_text_ph="Por exemplo: Rezem pela minha mãe, que começa a quimioterapia esta semana, e pela nossa família.",
        f_private="Manter em particular: não mostrar no mural. Só a nossa equipe vai ler e rezar por você.",
        f_send="Enviar meu pedido",
        rules_h="Antes de enviar",
        rules=["Use só o primeiro nome. Não coloque sobrenomes, telefones, endereços nem detalhes particulares de outras pessoas.",
               "Lemos cada pedido antes de publicar, em geral em um dia. Podemos encurtar o pedido ou mantê-lo em particular para proteger você ou outra pessoa.",
               "Sem links, anúncios nem vaquinhas. Os pedidos são apagados sozinhos depois de 30 dias.",
               "Tem menos de 13 anos? Peça licença ao seu pai ou à sua mãe antes de publicar."],
        f_legal='Como tratamos o que você envia: <a href="/pt/privacidade#prayer-wall">Política de privacidade</a> e <a href="/pt/termos#prayer-wall">Termos de uso</a>.',
        all_h="Uma oração por todos deste mural",
        all_p="Reze por todos os que pediram oração aqui, se quiser, pelo nome.",
        all_text="Senhor Jesus, tu nos disseste para pedir, procurar e bater.\nApresentamos a ti todos os que pediram oração aqui\ne cada necessidade que trazem no coração.\nCura os doentes, consola os que choram,\ndá trabalho a quem precisa, paz aos aflitos\ne esperança aos que se sentem sozinhos.\nSanta Maria, Mãe de Deus, e todos os santos, rogai por eles.\nAmém.",
        more_h="Outras formas de pedir oração",
        more=[("Peça uma Missa", "Ligue para a secretaria da sua paróquia e peça uma Missa pela sua intenção, por um doente ou por um falecido. Costuma-se dar uma pequena oferta, mas nunca é obrigatório."),
              ("Fale com a sua paróquia", "Muitas paróquias têm uma corrente de oração ou um livro de intenções perto da porta. Padres e diáconos rezam com você com alegria."),
              ("Reze o Rosário por alguém", 'Ofereça um <a href="/pt/rosario">Rosário</a> por uma pessoa deste mural. Cada mistério pode ser por uma intenção diferente.')],
        note="Os pedidos do Mural de oração são escritos pelos visitantes. O CatholicDoorway lê cada um antes de publicar, mas não pode verificar o que diz.",
    ),
    "tl": dict(
        kicker='<a href="/tl/mga-dasal">Mga dasal</a> &rsaquo; Mga kahilingang panalangin',
        h1="Mga kahilingang panalangin",
        lede="Humiling ng panalangin, at ipanalangin ang iba. Ibahagi ang iyong intensiyon gamit ang iyong unang pangalan o nang hindi nagpapakilala, at pindutin ang <em>Nanalangin ako</em> kapag naipagdasal mo na ang isang tao. Walang account, walang pag-sign up at libre.",
        crisis_h="Nasa matinding krisis o naiisip na magpakamatay?",
        crisis="Hindi mo kailangang pasanin ito nang mag-isa, at hindi mo kailangang maghintay. Sa Pilipinas, tumawag sa <strong>NCMH Crisis Hotline, 1553</strong>, libre at bukas araw at gabi. Sa Estados Unidos, tumawag o mag-text sa <strong>988</strong>. Kung may nasa agarang panganib, tumawag sa <strong>911</strong>.",
        crisis_btns='<a class="btn small" href="tel:1553">Tumawag sa 1553</a> <a class="btn small secondary" href="tel:988">U.S.: 988</a> <a class="btn small secondary" href="sms:988">Mag-text sa 988</a>',
        crisis_more='Sa ibang bansa, maghanap ng libreng hotline sa <a href="https://findahelpline.com/" target="_blank" rel="noopener">findahelpline.com</a>. Maaari ka ring dalawin o kausapin ng pari: tumawag sa alinmang <a href="/tl/hanapin-ang-simbahan">parokyang Katoliko</a>.',
        toc=[("wall", "Ipanalangin ang iba"), ("ask", "Humiling ng panalangin"), ("for-all", "Isang dasal para sa lahat")],
        wall_h="Ipanalangin ang iba",
        wall_p="Ipinadala ng isang bisita ang bawat kahilingan at binasa muna ng aming maliit na grupo bago ilabas. Nananatili ang mga kahilingan nang 30 araw. Magdasal sa sarili mong salita o ng isang Aba Ginoong Maria, saka pindutin ang <em>Nanalangin ako</em> para malaman ng tao na hindi siya nag-iisa.",
        all_langs="Lahat ng wika", loading="Naglo-load ang mga kahilingan…",
        ask_h="Humiling ng panalangin",
        ask_p="Sabihin sa amin kung ano ang gusto mong ipanalangin. Ipinagdarasal ng aming grupo ang bawat kahilingang natatanggap namin, pati ang mga pribado.",
        f_req='Kailangang punan ang mga field na may <span class="req">*</span>.', f_name="Iyong unang pangalan", f_name_hint="Hindi kailangan. Iwanang blangko para lumabas bilang “Hindi nagpakilala”.",
        f_text="Iyong kahilingang panalangin", f_text_ph="Halimbawa: Pakidasal po ang nanay ko na magsisimula ng chemotherapy ngayong linggo, at ang aming pamilya.",
        f_private="Gawing pribado: huwag ilabas sa pahina. Ang aming grupo lang ang babasa nito at magdarasal para sa iyo.",
        f_send="Ipadala ang aking kahilingan",
        rules_h="Bago ka magpadala",
        rules=["Unang pangalan lang ang gamitin. Huwag isama ang apelyido, numero ng telepono, address o pribadong detalye ng ibang tao.",
               "Binabasa namin ang bawat kahilingan bago ito lumabas, kadalasan sa loob ng isang araw. Maaari namin itong paikliin o gawing pribado para maprotektahan ka o ang ibang tao.",
               "Walang link, patalastas o paghingi ng pera. Kusang nabubura ang mga kahilingan pagkalipas ng 30 araw.",
               "Wala ka pang 13 taong gulang? Magpaalam muna sa iyong magulang bago magpadala."],
        f_legal='Paano namin pinangangasiwaan ang ipinapadala mo: <a href="/tl/patakaran-sa-privacy#prayer-wall">Patakaran sa privacy</a> at <a href="/tl/mga-tuntunin#prayer-wall">Mga tuntunin</a>.',
        all_h="Isang dasal para sa lahat ng narito",
        all_p="Idasal ito para sa lahat ng humiling ng panalangin dito, at banggitin ang kanilang pangalan kung gusto mo.",
        all_text="Panginoong Hesus, sinabi mo sa amin na humingi, humanap at kumatok.\nInilalapit namin sa iyo ang lahat ng humiling ng panalangin dito,\nat ang bawat pangangailangang dala nila sa kanilang puso.\nPagalingin mo ang maysakit, aliwin ang mga nagdadalamhati,\nbigyan ng trabaho ang nangangailangan, kapayapaan ang mga nababalisa\nat pag-asa ang mga nakadarama ng pag-iisa.\nSanta Maria, Ina ng Diyos, at lahat ng mga santo, ipanalangin ninyo sila.\nAmen.",
        more_h="Iba pang paraan ng paghingi ng panalangin",
        more=[("Magpamisa", "Tumawag sa opisina ng parokya at magpamisa para sa iyong intensiyon, para sa maysakit o para sa yumao. Karaniwang nagbibigay ng maliit na abuloy, pero hindi ito kailanman sapilitan."),
              ("Lumapit sa iyong parokya", "Maraming parokya ang may prayer chain o aklat ng mga intensiyon malapit sa pinto. Masaya ang mga pari at diyakono na manalangin kasama mo."),
              ("Magrosaryo para sa isang tao", 'Ialay ang isang <a href="/tl/rosaryo">Rosaryo</a> para sa isang tao rito. Maaaring iba-iba ang intensiyon ng bawat misteryo.')],
        note="Isinulat ng mga bisita ang mga kahilingang panalangin dito. Binabasa ng CatholicDoorway ang bawat isa bago ilabas, pero hindi namin masusuri ang sinasabi nito.",
    ),
}

# Short strings the page script needs (site/assets/js/prayerwall.js).
JS = {
    "en": dict(prayed="I prayed", thanks="Thank you for praying", n1="1 person prayed", nn="{n} people prayed", n0="Be the first to pray",
               anon="Anonymous", empty="There are no prayer requests on the wall right now. Be the first to ask, below.", more="Show more",
               today="today", yday="yesterday", days="{n} days ago", sending="Sending…",
               ok="Thank you. We received your request and will pray for you. It will appear on the wall after we read it, usually within a day.",
               ok_private="Thank you. Your request stays private: only our team will read it, and we will pray for you.",
               crisis_seen="If you are thinking about ending your life, please call or text 988 now (or 911 in an emergency). You matter, and help is there for you right now.",
               e_text="Please write your request (at least a few words).", e_long="Please keep your request under 500 characters.",
               e_link="Please take out links and website addresses.", e_contact="Please take out email addresses and phone numbers.",
               e_name="Please use just your first name, or leave it blank.", e_many="You have sent several requests in the last hour. Please wait a little and try again.",
               e_ready="The Prayer Wall opens soon. For now, you can email your request to", e_fail="Something went wrong. Please try again, or email your request to",
               left="{n} characters left", lang={"en": "English", "es": "Spanish", "pt": "Portuguese", "tl": "Filipino"}),
    "es": dict(prayed="Recé", thanks="Gracias por rezar", n1="1 persona rezó", nn="{n} personas rezaron", n0="Sé el primero en rezar",
               anon="Anónimo", empty="Ahora no hay peticiones en el muro. Sé el primero en pedir oración, abajo.", more="Ver más",
               today="hoy", yday="ayer", days="hace {n} días", sending="Enviando…",
               ok="Gracias. Recibimos tu petición y rezaremos por ti. Aparecerá en el muro cuando la leamos, por lo general en un día.",
               ok_private="Gracias. Tu petición queda privada: solo nuestro equipo la leerá, y rezaremos por ti.",
               crisis_seen="Si estás pensando en quitarte la vida, llama o escribe al 988 ahora (marca 2 para español), o al 911 en una emergencia. Tu vida importa y hay ayuda para ti ahora mismo.",
               e_text="Escribe tu petición (al menos unas palabras).", e_long="Tu petición debe tener menos de 500 caracteres.",
               e_link="Quita los enlaces y las direcciones de sitios web.", e_contact="Quita los correos electrónicos y los números de teléfono.",
               e_name="Usa solo tu nombre de pila, o déjalo en blanco.", e_many="Enviaste varias peticiones en la última hora. Espera un poco y vuelve a intentarlo.",
               e_ready="El Muro de oración abrirá pronto. Por ahora, puedes enviar tu petición por correo a", e_fail="Algo salió mal. Inténtalo de nuevo o envía tu petición por correo a",
               left="Quedan {n} caracteres", lang={"en": "Inglés", "es": "Español", "pt": "Portugués", "tl": "Filipino"}),
    "pt": dict(prayed="Rezei", thanks="Obrigado por rezar", n1="1 pessoa rezou", nn="{n} pessoas rezaram", n0="Seja o primeiro a rezar",
               anon="Anônimo", empty="Agora não há pedidos no mural. Seja o primeiro a pedir oração, logo abaixo.", more="Ver mais",
               today="hoje", yday="ontem", days="há {n} dias", sending="Enviando…",
               ok="Obrigado. Recebemos o seu pedido e vamos rezar por você. Ele vai aparecer no mural depois que o lermos, em geral em um dia.",
               ok_private="Obrigado. O seu pedido fica em particular: só a nossa equipe vai ler, e vamos rezar por você.",
               crisis_seen="Se você está pensando em tirar a própria vida, ligue agora para o CVV, 188 (no Brasil), ou para o 988 nos EUA. A sua vida importa, e há ajuda para você agora mesmo.",
               e_text="Escreva o seu pedido (pelo menos algumas palavras).", e_long="O pedido deve ter menos de 500 caracteres.",
               e_link="Tire os links e endereços de sites.", e_contact="Tire os e-mails e números de telefone.",
               e_name="Use só o seu primeiro nome, ou deixe em branco.", e_many="Você enviou vários pedidos na última hora. Espere um pouco e tente de novo.",
               e_ready="O Mural de oração abre em breve. Por enquanto, envie o seu pedido por e-mail para", e_fail="Algo deu errado. Tente de novo ou envie o seu pedido por e-mail para",
               left="Restam {n} caracteres", lang={"en": "Inglês", "es": "Espanhol", "pt": "Português", "tl": "Filipino"}),
    "tl": dict(prayed="Nanalangin ako", thanks="Salamat sa pagdarasal", n1="1 tao ang nanalangin", nn="{n} tao ang nanalangin", n0="Ikaw ang unang manalangin",
               anon="Hindi nagpakilala", empty="Wala pang kahilingang panalangin ngayon. Ikaw ang unang humiling, sa ibaba.", more="Ipakita pa",
               today="ngayon", yday="kahapon", days="{n} araw na ang nakalipas", sending="Ipinapadala…",
               ok="Salamat. Natanggap namin ang iyong kahilingan at ipagdarasal ka namin. Lalabas ito rito pagkatapos naming basahin, kadalasan sa loob ng isang araw.",
               ok_private="Salamat. Mananatiling pribado ang iyong kahilingan: ang aming grupo lang ang babasa nito, at ipagdarasal ka namin.",
               crisis_seen="Kung naiisip mong wakasan ang iyong buhay, tumawag ngayon sa 1553 (NCMH, sa Pilipinas) o sa 988 sa Estados Unidos. Mahalaga ka, at may tulong para sa iyo ngayon din.",
               e_text="Isulat ang iyong kahilingan (kahit ilang salita).", e_long="Panatilihing mas maikli sa 500 titik ang iyong kahilingan.",
               e_link="Pakialis ang mga link at address ng website.", e_contact="Pakialis ang mga email address at numero ng telepono.",
               e_name="Unang pangalan lang ang gamitin, o iwanang blangko.", e_many="Nakapagpadala ka na ng ilang kahilingan sa nakaraang oras. Maghintay sandali at subukang muli.",
               e_ready="Malapit nang magbukas ang pahinang ito. Sa ngayon, maaari mong i-email ang iyong kahilingan sa", e_fail="May nangyaring mali. Subukang muli, o i-email ang iyong kahilingan sa",
               left="{n} titik pa", lang={"en": "Ingles", "es": "Espanyol", "pt": "Portuges", "tl": "Filipino"}),
}


def page(lang):
    t, js = T[lang], JS[lang]
    toc = "".join(f'<li><a href="#{a}">{e(b)}</a></li>' for a, b in t["toc"])
    rules = "".join(f"<li>{x}</li>" for x in t["rules"])
    more = "".join(f'<article class="card"><h3>{e(h)}</h3><p>{p}</p></article>' for h, p in t["more"])
    chips = f'<button type="button" class="chip" data-plang="all" aria-pressed="true">{e(t["all_langs"])}</button>' + "".join(
        f'<button type="button" class="chip" data-plang="{c}" aria-pressed="false">{e(js["lang"][c])}</button>' for c in ("en", "es", "pt", "tl"))
    labels = json.dumps(js, ensure_ascii=False)
    return f'''<div class="page-head">
  <div class="wrap">
    <p class="kicker">{t["kicker"]}</p>
    <h1>{t["h1"]}</h1>
    <p class="lede">{t["lede"]}</p>
  </div>
</div>

<div class="wrap prayer-wall" data-labels='{e(labels, quote=True)}'>
  <aside class="crisis-box" id="crisis" aria-labelledby="crisis-h">
    <h2 id="crisis-h">{t["crisis_h"]}</h2>
    <p>{t["crisis"]}</p>
    <div class="actions">{t["crisis_btns"]}</div>
    <p class="small">{t["crisis_more"]}</p>
  </aside>

  <ul class="toc" aria-label="{e(t["h1"])}">{toc}</ul>

  <section class="section" id="wall">
    <h2>{t["wall_h"]}</h2>
    <p class="prose">{t["wall_p"]}</p>
    <div class="filters" role="group" aria-label="{e(t["all_langs"])}">{chips}</div>
    <div id="pw-list" class="pw-list" aria-live="polite"><p class="muted">{t["loading"]}</p></div>
    <div class="btn-row"><button type="button" class="btn secondary" id="pw-more" hidden>{e(js["more"])}</button></div>
  </section>

  <section class="section" id="ask">
    <h2>{t["ask_h"]}</h2>
    <p class="prose">{t["ask_p"]}</p>
    <div class="grid two pw-ask">
      <form class="card ocia-form" id="prayer-form" novalidate>
        <p class="small muted form-req">{t["f_req"]}</p>
        <div class="form-grid">
          <label>{t["f_name"]}<input name="name" maxlength="40" autocomplete="given-name"><span class="small muted">{t["f_name_hint"]}</span></label>
        </div>
        <label class="wide">{t["f_text"]} <span class="req">*</span><textarea name="text" required maxlength="500" rows="5" placeholder="{e(t["f_text_ph"])}"></textarea></label>
        <p class="small muted pw-left" id="pw-left" aria-live="polite"></p>
        <label class="hp" aria-hidden="true">Leave this empty<input name="website2" tabindex="-1" autocomplete="off"></label>
        <label class="consent"><input type="checkbox" name="private"> {t["f_private"]}</label>
        <p class="small muted">{t["f_legal"]}</p>
        <div class="btn-row"><button class="btn" type="submit">{t["f_send"]}</button></div>
        <p class="status-msg" id="prayer-msg" role="status" aria-live="polite"></p>
        <div class="crisis-box small-crisis" id="pw-crisis" hidden><p></p></div>
      </form>
      <aside class="card pw-rules">
        <h3>{t["rules_h"]}</h3>
        <ul class="prose small">{rules}</ul>
      </aside>
    </div>
  </section>

  <section class="section">
    <article class="card prayer" id="for-all">
      <h2>{t["all_h"]}</h2>
      <p class="muted">{t["all_p"]}</p>
      <p class="text">{e(t["all_text"])}</p>
    </article>
  </section>

  <section class="section" id="more-ways">
    <h2>{t["more_h"]}</h2>
    <div class="grid three">{more}</div>
  </section>

  <p class="small muted">{t["note"]}</p>
</div>'''


def render(body, lang):
    if "{{PRAYER_WALL}}" not in body:
        return body
    return body.replace("{{PRAYER_WALL}}", page(lang))
