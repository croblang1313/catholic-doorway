/* CatholicDoorway interactive Rosary: tap through the beads one prayer at a time. */
(function () {
  'use strict';
  var root = document.getElementById('rosary-app');
  if (!root) return;
  var $ = function (s, c) { return (c || document).querySelector(s); };

  var P = {
    sign: { t: 'The Sign of the Cross', x: 'In the name of the Father, and of the Son, and of the Holy Spirit. Amen.' },
    creed: { t: 'The Apostles’ Creed', x: 'I believe in God, the Father almighty, Creator of heaven and earth; and in Jesus Christ, his only Son, our Lord; who was conceived by the Holy Spirit, born of the Virgin Mary, suffered under Pontius Pilate, was crucified, died, and was buried. He descended into hell; the third day he rose again from the dead; he ascended into heaven, and sits at the right hand of God, the Father almighty; from there he shall come to judge the living and the dead. I believe in the Holy Spirit, the holy Catholic Church, the communion of saints, the forgiveness of sins, the resurrection of the body, and life everlasting. Amen.' },
    our: { t: 'Our Father', x: 'Our Father, who art in heaven, hallowed be thy name; thy kingdom come, thy will be done on earth as it is in heaven. Give us this day our daily bread, and forgive us our trespasses, as we forgive those who trespass against us; and lead us not into temptation, but deliver us from evil. Amen.' },
    hail: { t: 'Hail Mary', x: 'Hail Mary, full of grace, the Lord is with thee. Blessed art thou among women, and blessed is the fruit of thy womb, Jesus. Holy Mary, Mother of God, pray for us sinners, now and at the hour of our death. Amen.' },
    glory: { t: 'Glory Be', x: 'Glory be to the Father, and to the Son, and to the Holy Spirit, as it was in the beginning, is now, and ever shall be, world without end. Amen.' },
    fatima: { t: 'The Fatima Prayer', x: 'O my Jesus, forgive us our sins, save us from the fires of hell, lead all souls to heaven, especially those in most need of thy mercy.' },
    queen: { t: 'Hail, Holy Queen', x: 'Hail, holy Queen, Mother of mercy, our life, our sweetness and our hope. To thee do we cry, poor banished children of Eve. To thee do we send up our sighs, mourning and weeping in this valley of tears. Turn then, most gracious advocate, thine eyes of mercy toward us, and after this our exile show unto us the blessed fruit of thy womb, Jesus. O clement, O loving, O sweet Virgin Mary.\n\nV. Pray for us, O holy Mother of God.\nR. That we may be made worthy of the promises of Christ.' },
    close: { t: 'Closing prayer', x: 'Let us pray. O God, whose only-begotten Son, by his life, death and resurrection, has purchased for us the rewards of eternal life, grant, we beseech thee, that meditating upon these mysteries of the most holy Rosary of the Blessed Virgin Mary, we may imitate what they contain and obtain what they promise, through the same Christ our Lord. Amen.' }
  };

  var SETS = {
    joyful: { name: 'Joyful Mysteries', days: 'Mondays and Saturdays', m: [
      ['The Annunciation', 'Luke 1:26–38', 'Humility', 'The angel Gabriel tells Mary she will be the mother of God’s Son, and she says yes.'],
      ['The Visitation', 'Luke 1:39–56', 'Love of neighbor', 'Mary hurries to help her cousin Elizabeth, whose child leaps for joy.'],
      ['The Nativity', 'Luke 2:1–20', 'Poverty of spirit', 'Jesus is born in a stable in Bethlehem and laid in a manger.'],
      ['The Presentation in the Temple', 'Luke 2:22–38', 'Obedience', 'Mary and Joseph present the baby Jesus to God, and Simeon recognizes the Savior.'],
      ['The Finding of Jesus in the Temple', 'Luke 2:41–52', 'Joy in finding Jesus', 'After three days of searching, Mary and Joseph find the young Jesus in his Father’s house.']] },
    luminous: { name: 'Luminous Mysteries', days: 'Thursdays', m: [
      ['The Baptism of Jesus', 'Matthew 3:13–17', 'Openness to the Holy Spirit', 'The Father’s voice declares, “This is my beloved Son,” as the Spirit descends.'],
      ['The Wedding at Cana', 'John 2:1–11', 'To Jesus through Mary', 'At Mary’s request, Jesus turns water into wine, his first sign.'],
      ['The Proclamation of the Kingdom', 'Mark 1:14–15', 'Repentance', 'Jesus calls everyone to repent and believe the Good News.'],
      ['The Transfiguration', 'Luke 9:28–36', 'Desire for holiness', 'On the mountain, Jesus shines with glory before Peter, James and John.'],
      ['The Institution of the Eucharist', 'Luke 22:14–20', 'Love of the Eucharist', 'At the Last Supper, Jesus gives his Body and Blood under the signs of bread and wine.']] },
    sorrowful: { name: 'Sorrowful Mysteries', days: 'Tuesdays and Fridays', m: [
      ['The Agony in the Garden', 'Matthew 26:36–46', 'Sorrow for sin', 'In Gethsemane, Jesus prays, “Not my will, but yours be done.”'],
      ['The Scourging at the Pillar', 'John 19:1', 'Purity', 'Jesus is bound and whipped by the soldiers.'],
      ['The Crowning with Thorns', 'Matthew 27:27–31', 'Courage', 'Soldiers mock Jesus as a king, pressing a crown of thorns on his head.'],
      ['The Carrying of the Cross', 'Luke 23:26–32', 'Patience', 'Jesus carries his cross to Calvary, helped by Simon of Cyrene.'],
      ['The Crucifixion', 'Luke 23:33–46', 'Perseverance', 'Jesus dies on the cross, forgiving those who crucified him.']] },
    glorious: { name: 'Glorious Mysteries', days: 'Wednesdays and Sundays', m: [
      ['The Resurrection', 'Luke 24:1–12', 'Faith', 'On the third day, the tomb is empty: Jesus is risen.'],
      ['The Ascension', 'Acts 1:6–11', 'Hope', 'Jesus returns to the Father, promising to send the Holy Spirit.'],
      ['The Descent of the Holy Spirit', 'Acts 2:1–4', 'Love of God', 'At Pentecost, the Spirit comes upon Mary and the Apostles as tongues of fire.'],
      ['The Assumption of Mary', 'Revelation 12:1', 'Grace of a holy death', 'At the end of her life, Mary is taken body and soul into heaven.'],
      ['The Coronation of Mary', 'Revelation 12:1', 'Trust in Mary’s prayers', 'Mary is crowned Queen of heaven and earth.']] }
  };

  /* ---- Spanish ---- */
  var LG = document.documentElement.lang, ES = LG === 'es', PT = LG === 'pt';
  var T = function (en, es, pt) { return PT ? (pt !== undefined ? pt : en) : ES ? es : en; };
  if (ES) {
    P = {
      sign: { t: 'La Señal de la Cruz', x: 'En el nombre del Padre, y del Hijo, y del Espíritu Santo. Amén.' },
      creed: { t: 'El Credo de los Apóstoles', x: 'Creo en Dios, Padre todopoderoso, Creador del cielo y de la tierra.\nCreo en Jesucristo, su único Hijo, nuestro Señor, que fue concebido por obra y gracia del Espíritu Santo, nació de Santa María Virgen, padeció bajo el poder de Poncio Pilato, fue crucificado, muerto y sepultado, descendió a los infiernos, al tercer día resucitó de entre los muertos, subió a los cielos y está sentado a la derecha de Dios, Padre todopoderoso. Desde allí ha de venir a juzgar a vivos y muertos.\nCreo en el Espíritu Santo, la santa Iglesia católica, la comunión de los santos, el perdón de los pecados, la resurrección de la carne y la vida eterna. Amén.' },
      our: { t: 'Padre Nuestro', x: 'Padre nuestro, que estás en el cielo, santificado sea tu Nombre; venga a nosotros tu reino; hágase tu voluntad en la tierra como en el cielo. Danos hoy nuestro pan de cada día; perdona nuestras ofensas, como también nosotros perdonamos a los que nos ofenden; no nos dejes caer en la tentación, y líbranos del mal. Amén.' },
      hail: { t: 'Ave María', x: 'Dios te salve, María, llena eres de gracia, el Señor es contigo. Bendita tú eres entre todas las mujeres, y bendito es el fruto de tu vientre, Jesús.\nSanta María, Madre de Dios, ruega por nosotros, pecadores, ahora y en la hora de nuestra muerte. Amén.' },
      glory: { t: 'Gloria', x: 'Gloria al Padre, y al Hijo, y al Espíritu Santo. Como era en el principio, ahora y siempre, por los siglos de los siglos. Amén.' },
      fatima: { t: 'La oración de Fátima', x: 'Oh Jesús mío, perdona nuestros pecados, líbranos del fuego del infierno, lleva al cielo a todas las almas, especialmente a las más necesitadas de tu misericordia.' },
      queen: { t: 'La Salve', x: 'Dios te salve, Reina y Madre de misericordia, vida, dulzura y esperanza nuestra; Dios te salve. A ti llamamos los desterrados hijos de Eva; a ti suspiramos, gimiendo y llorando en este valle de lágrimas. Ea, pues, Señora, abogada nuestra, vuelve a nosotros esos tus ojos misericordiosos; y después de este destierro muéstranos a Jesús, fruto bendito de tu vientre. ¡Oh clementísima, oh piadosa, oh dulce Virgen María!\nV. Ruega por nosotros, Santa Madre de Dios.\nR. Para que seamos dignos de alcanzar las promesas de nuestro Señor Jesucristo. Amén.' },
      close: { t: 'Oración final', x: 'Oremos. Oh Dios, cuyo Hijo unigénito, con su vida, muerte y resurrección, nos alcanzó el premio de la vida eterna: concédenos que, meditando estos misterios del santísimo Rosario de la Bienaventurada Virgen María, imitemos lo que contienen y alcancemos lo que prometen. Por el mismo Cristo nuestro Señor. Amén.' }
    };
    // [name, reference shown, fruit, description, English reference for the link]
    SETS = {
      joyful: { name: 'Misterios Gozosos', short: 'Gozoso', days: 'Lunes y sábados', m: [
        ['La Anunciación', 'Lucas 1, 26–38', 'La humildad', 'El ángel Gabriel anuncia a María que será la madre del Hijo de Dios, y ella dice que sí.', 'Luke 1:26'],
        ['La Visitación', 'Lucas 1, 39–56', 'El amor al prójimo', 'María va de prisa a ayudar a su prima Isabel, y el niño salta de alegría en su seno.', 'Luke 1:39'],
        ['El Nacimiento de Jesús', 'Lucas 2, 1–20', 'La pobreza de espíritu', 'Jesús nace en un establo de Belén y es recostado en un pesebre.', 'Luke 2:1'],
        ['La Presentación en el Templo', 'Lucas 2, 22–38', 'La obediencia', 'María y José presentan al niño Jesús a Dios, y Simeón reconoce al Salvador.', 'Luke 2:22'],
        ['El Niño Jesús perdido y hallado en el Templo', 'Lucas 2, 41–52', 'La alegría de encontrar a Jesús', 'Después de tres días de búsqueda, María y José encuentran a Jesús en el Templo, en la casa de su Padre.', 'Luke 2:41']] },
      luminous: { name: 'Misterios Luminosos', short: 'Luminoso', days: 'Jueves', m: [
        ['El Bautismo de Jesús', 'Mateo 3, 13–17', 'La apertura al Espíritu Santo', 'La voz del Padre dice: “Este es mi Hijo amado”, mientras el Espíritu desciende como una paloma.', 'Matthew 3:13'],
        ['Las bodas de Caná', 'Juan 2, 1–11', 'A Jesús por María', 'A petición de María, Jesús convierte el agua en vino, su primer signo.', 'John 2:1'],
        ['El anuncio del Reino de Dios', 'Marcos 1, 14–15', 'La conversión', 'Jesús llama a todos a convertirse y a creer en la Buena Nueva.', 'Mark 1:14'],
        ['La Transfiguración', 'Lucas 9, 28–36', 'El deseo de santidad', 'En el monte, Jesús resplandece de gloria ante Pedro, Santiago y Juan.', 'Luke 9:28'],
        ['La institución de la Eucaristía', 'Lucas 22, 14–20', 'El amor a la Eucaristía', 'En la Última Cena, Jesús nos da su Cuerpo y su Sangre bajo las especies del pan y del vino.', 'Luke 22:14']] },
      sorrowful: { name: 'Misterios Dolorosos', short: 'Doloroso', days: 'Martes y viernes', m: [
        ['La oración en el huerto', 'Mateo 26, 36–46', 'El dolor de los pecados', 'En Getsemaní, Jesús reza: “No se haga mi voluntad, sino la tuya”.', 'Matthew 26:36'],
        ['La flagelación', 'Juan 19, 1', 'La pureza', 'Jesús es atado y azotado por los soldados.', 'John 19:1'],
        ['La coronación de espinas', 'Mateo 27, 27–31', 'La valentía', 'Los soldados se burlan de Jesús como rey y le ponen una corona de espinas.', 'Matthew 27:27'],
        ['Jesús con la cruz a cuestas', 'Lucas 23, 26–32', 'La paciencia', 'Jesús lleva su cruz hasta el Calvario, ayudado por Simón de Cirene.', 'Luke 23:26'],
        ['La crucifixión y muerte de Jesús', 'Lucas 23, 33–46', 'La perseverancia', 'Jesús muere en la cruz, perdonando a quienes lo crucificaron.', 'Luke 23:33']] },
      glorious: { name: 'Misterios Gloriosos', short: 'Glorioso', days: 'Miércoles y domingos', m: [
        ['La Resurrección', 'Lucas 24, 1–12', 'La fe', 'Al tercer día, el sepulcro está vacío: Jesús ha resucitado.', 'Luke 24:1'],
        ['La Ascensión', 'Hechos 1, 6–11', 'La esperanza', 'Jesús vuelve al Padre y promete enviar el Espíritu Santo.', 'Acts 1:6'],
        ['La venida del Espíritu Santo', 'Hechos 2, 1–4', 'El amor a Dios', 'En Pentecostés, el Espíritu desciende sobre María y los Apóstoles como lenguas de fuego.', 'Acts 2:1'],
        ['La Asunción de María', 'Apocalipsis 12, 1', 'La gracia de una buena muerte', 'Al final de su vida, María es llevada en cuerpo y alma al cielo.', 'Revelation 12:1'],
        ['La Coronación de María', 'Apocalipsis 12, 1', 'La confianza en la intercesión de María', 'María es coronada Reina del cielo y de la tierra.', 'Revelation 12:1']] }
    };
  }
  if (PT) {
    P = {
      sign: { t: 'O Sinal da Cruz', x: 'Em nome do Pai, e do Filho, e do Espírito Santo. Amém.' },
      creed: { t: 'O Creio (Símbolo dos Apóstolos)', x: 'Creio em Deus Pai todo-poderoso, Criador do céu e da terra.\nE em Jesus Cristo, seu único Filho, nosso Senhor, que foi concebido pelo poder do Espírito Santo; nasceu da Virgem Maria; padeceu sob Pôncio Pilatos, foi crucificado, morto e sepultado; desceu à mansão dos mortos; ressuscitou ao terceiro dia; subiu aos céus; está sentado à direita de Deus Pai todo-poderoso, donde há de vir a julgar os vivos e os mortos.\nCreio no Espírito Santo, na santa Igreja Católica, na comunhão dos santos, na remissão dos pecados, na ressurreição da carne, na vida eterna. Amém.' },
      our: { t: 'Pai-Nosso', x: 'Pai nosso, que estais nos céus, santificado seja o vosso nome; venha a nós o vosso reino; seja feita a vossa vontade, assim na terra como no céu. O pão nosso de cada dia nos dai hoje; perdoai-nos as nossas ofensas, assim como nós perdoamos a quem nos tem ofendido; e não nos deixeis cair em tentação, mas livrai-nos do mal. Amém.' },
      hail: { t: 'Ave-Maria', x: 'Ave, Maria, cheia de graça, o Senhor é convosco; bendita sois vós entre as mulheres, e bendito é o fruto do vosso ventre, Jesus.\nSanta Maria, Mãe de Deus, rogai por nós, pecadores, agora e na hora de nossa morte. Amém.' },
      glory: { t: 'Glória', x: 'Glória ao Pai, e ao Filho, e ao Espírito Santo. Como era no princípio, agora e sempre. Amém.' },
      fatima: { t: 'A oração de Fátima', x: 'Ó meu Jesus, perdoai-nos, livrai-nos do fogo do inferno, levai as almas todas para o céu e socorrei principalmente as que mais precisarem.' },
      queen: { t: 'Salve-Rainha', x: 'Salve, Rainha, Mãe de misericórdia, vida, doçura e esperança nossa, salve! A vós bradamos, os degredados filhos de Eva. A vós suspiramos, gemendo e chorando neste vale de lágrimas. Eia, pois, advogada nossa, esses vossos olhos misericordiosos a nós volvei. E depois deste desterro, mostrai-nos Jesus, bendito fruto do vosso ventre. Ó clemente, ó piedosa, ó doce sempre Virgem Maria.\nV. Rogai por nós, santa Mãe de Deus.\nR. Para que sejamos dignos das promessas de Cristo. Amém.' },
      close: { t: 'Oração final', x: 'Oremos. Ó Deus, cujo Filho Unigênito, por sua vida, morte e ressurreição, nos alcançou o prêmio da salvação eterna, concedei-nos que, meditando estes mistérios do santíssimo Rosário da Bem-aventurada Virgem Maria, imitemos o que contêm e alcancemos o que prometem. Pelo mesmo Cristo, nosso Senhor. Amém.' }
    };
    SETS = {
      joyful: { name: 'Mistérios Gozosos', short: 'Gozoso', days: 'Segundas e sábados', m: [
        ['A Anunciação', 'Lucas 1,26-38', 'A humildade', 'O anjo Gabriel anuncia a Maria que ela será a mãe do Filho de Deus, e ela diz sim.', 'Luke 1:26'],
        ['A Visitação', 'Lucas 1,39-56', 'O amor ao próximo', 'Maria vai às pressas ajudar sua prima Isabel, e o menino salta de alegria em seu ventre.', 'Luke 1:39'],
        ['O Nascimento de Jesus', 'Lucas 2,1-20', 'A pobreza de espírito', 'Jesus nasce num estábulo em Belém e é deitado numa manjedoura.', 'Luke 2:1'],
        ['A Apresentação no Templo', 'Lucas 2,22-38', 'A obediência', 'Maria e José apresentam o menino Jesus a Deus, e Simeão reconhece o Salvador.', 'Luke 2:22'],
        ['A Perda e o Encontro de Jesus no Templo', 'Lucas 2,41-52', 'A alegria de encontrar Jesus', 'Depois de três dias de procura, Maria e José encontram Jesus no Templo, na casa de seu Pai.', 'Luke 2:41']] },
      luminous: { name: 'Mistérios Luminosos', short: 'Luminoso', days: 'Quintas-feiras', m: [
        ['O Batismo de Jesus', 'Mateus 3,13-17', 'A abertura ao Espírito Santo', 'A voz do Pai diz: “Este é o meu Filho amado”, enquanto o Espírito desce como uma pomba.', 'Matthew 3:13'],
        ['As Bodas de Caná', 'João 2,1-11', 'A Jesus por Maria', 'A pedido de Maria, Jesus transforma a água em vinho, o seu primeiro sinal.', 'John 2:1'],
        ['O Anúncio do Reino de Deus', 'Marcos 1,14-15', 'A conversão', 'Jesus chama todos a se converterem e a crerem no Evangelho.', 'Mark 1:14'],
        ['A Transfiguração', 'Lucas 9,28-36', 'O desejo de santidade', 'No monte, Jesus resplandece de glória diante de Pedro, Tiago e João.', 'Luke 9:28'],
        ['A Instituição da Eucaristia', 'Lucas 22,14-20', 'O amor à Eucaristia', 'Na Última Ceia, Jesus nos dá o seu Corpo e o seu Sangue sob as espécies do pão e do vinho.', 'Luke 22:14']] },
      sorrowful: { name: 'Mistérios Dolorosos', short: 'Doloroso', days: 'Terças e sextas', m: [
        ['A Agonia de Jesus no Horto', 'Mateus 26,36-46', 'A dor dos pecados', 'No Getsêmani, Jesus reza: “Não seja feita a minha vontade, mas a tua”.', 'Matthew 26:36'],
        ['A Flagelação de Jesus', 'João 19,1', 'A pureza', 'Jesus é amarrado e açoitado pelos soldados.', 'John 19:1'],
        ['A Coroação de Espinhos', 'Mateus 27,27-31', 'A coragem', 'Os soldados zombam de Jesus como rei e colocam em sua cabeça uma coroa de espinhos.', 'Matthew 27:27'],
        ['Jesus Carrega a Cruz', 'Lucas 23,26-32', 'A paciência', 'Jesus leva a sua cruz até o Calvário, ajudado por Simão de Cirene.', 'Luke 23:26'],
        ['A Crucifixão e Morte de Jesus', 'Lucas 23,33-46', 'A perseverança', 'Jesus morre na cruz, perdoando os que o crucificaram.', 'Luke 23:33']] },
      glorious: { name: 'Mistérios Gloriosos', short: 'Glorioso', days: 'Quartas e domingos', m: [
        ['A Ressurreição de Jesus', 'Lucas 24,1-12', 'A fé', 'Ao terceiro dia, o túmulo está vazio: Jesus ressuscitou.', 'Luke 24:1'],
        ['A Ascensão de Jesus', 'Atos 1,6-11', 'A esperança', 'Jesus volta para o Pai e promete enviar o Espírito Santo.', 'Acts 1:6'],
        ['A Vinda do Espírito Santo', 'Atos 2,1-4', 'O amor a Deus', 'Em Pentecostes, o Espírito desce sobre Maria e os Apóstolos como línguas de fogo.', 'Acts 2:1'],
        ['A Assunção de Maria', 'Apocalipse 12,1', 'A graça de uma boa morte', 'No fim de sua vida, Maria é levada de corpo e alma ao céu.', 'Revelation 12:1'],
        ['A Coroação de Maria', 'Apocalipse 12,1', 'A confiança na intercessão de Maria', 'Maria é coroada Rainha do céu e da terra.', 'Revelation 12:1']] }
    };
  }
  /* ---- Latin (optional) ---- */
  var LA = {
      "sign": {
          "t": "Signum Crucis",
          "x": "In nómine Patris, et Fílii, et Spíritus Sancti. Amen."
      },
      "creed": {
          "t": "Symbolum Apostolorum",
          "x": "Credo in Deum, Patrem omnipoténtem,\nCreatórem caeli et terrae.\nEt in Iesum Christum, Fílium eius únicum, Dóminum nostrum,\nqui concéptus est de Spíritu Sancto,\nnatus ex María Vírgine,\npassus sub Póntio Piláto,\ncrucifíxus, mórtuus, et sepúltus,\ndescéndit ad ínferos,\ntértia die resurréxit a mórtuis,\nascéndit ad caelos,\nsedet ad déxteram Dei Patris omnipoténtis,\ninde ventúrus est iudicáre vivos et mórtuos.\nCredo in Spíritum Sanctum,\nsanctam Ecclésiam cathólicam,\nsanctórum communiónem,\nremissiónem peccatórum,\ncarnis resurrectiónem,\nvitam aetérnam. Amen."
      },
      "our": {
          "t": "Pater Noster",
          "x": "Pater noster, qui es in caelis,\nsanctificétur nomen tuum.\nAdvéniat regnum tuum.\nFiat volúntas tua, sicut in caelo et in terra.\nPanem nostrum cotidiánum da nobis hódie,\net dimítte nobis débita nostra,\nsicut et nos dimíttimus debitóribus nostris.\nEt ne nos indúcas in tentatiónem,\nsed líbera nos a malo. Amen."
      },
      "hail": {
          "t": "Ave Maria",
          "x": "Ave María, grátia plena, Dóminus tecum.\nBenedícta tu in muliéribus,\net benedíctus fructus ventris tui, Iesus.\nSancta María, Mater Dei,\nora pro nobis peccatóribus,\nnunc et in hora mortis nostrae. Amen."
      },
      "glory": {
          "t": "Gloria Patri",
          "x": "Glória Patri, et Fílio, et Spirítui Sancto.\nSicut erat in princípio, et nunc, et semper,\net in sáecula saeculórum. Amen."
      },
      "fatima": {
          "t": "Oratio Fatimae",
          "x": "Dómine Iesu, dimítte nobis débita nostra,\nsalva nos ab igne inferióri,\nperduc in caelum omnes ánimas,\npraesértim eas, quae misericórdiae tuae máxime índigent. Amen."
      },
      "queen": {
          "t": "Salve Regina",
          "x": "Salve, Regína, Mater misericórdiae,\nvita, dulcédo, et spes nostra, salve.\nAd te clamámus, éxsules fílii Evae.\nAd te suspirámus, geméntes et flentes\nin hac lacrimárum valle.\nEia ergo, advocáta nostra,\nillos tuos misericórdes óculos ad nos convérte.\nEt Iesum, benedíctum fructum ventris tui,\nnobis post hoc exsílium osténde.\nO clemens, O pia, O dulcis Virgo María.\nV. Ora pro nobis, sancta Dei Génetrix.\nR. Ut digni efficiámur promissiónibus Christi."
      },
      "close": {
          "t": "Orémus",
          "x": "Orémus. Deus, cuius Unigénitus per vitam, mortem et resurrectiónem suam nobis salútis aetérnae praémia comparávit: concéde, quaésumus, ut haec mystéria sacratíssimo beátae Maríae Vírginis Rosário recoléntes, et imitémur quod cóntinent, et quod promíttunt assequámur. Per eúndem Christum Dóminum nostrum. Amen."
      }
  };
  var latin = false;
  try { latin = localStorage.getItem('cd-rosary-latin') === '1'; } catch (e) {}
  var BY_DAY = ['glorious', 'joyful', 'sorrowful', 'glorious', 'luminous', 'sorrowful', 'joyful'];

  /* ---- Steps: each is one prayer on one bead ---- */
  function buildSteps() {
    var s = [];
    s.push({ bead: 'cross', p: 'sign', label: T('Begin at the crucifix', 'Empieza en el crucifijo', 'Comece no crucifixo') });
    s.push({ bead: 'cross', p: 'creed', label: T('On the crucifix', 'En el crucifijo', 'No crucifixo') });
    s.push({ bead: 'p1', p: 'our', label: T('First large bead', 'Primera cuenta grande', 'Primeira conta grande') });
    for (var i = 1; i <= 3; i++) s.push({ bead: 'ps' + i, p: 'hail', k: i, label: T('Hail Mary ' + i + ' of 3', 'Avemaría ' + i + ' de 3', 'Ave-Maria ' + i + ' de 3'), note: PT ? ['Pelo aumento da fé', 'Pelo aumento da esperança', 'Pelo aumento da caridade'][i - 1] : ES ? ['Por el aumento de la fe', 'Por el aumento de la esperanza', 'Por el aumento de la caridad'][i - 1] : ['For an increase of faith', 'For an increase of hope', 'For an increase of charity'][i - 1] });
    s.push({ bead: 'p2', p: 'glory', label: T('Before the next large bead', 'Antes de la siguiente cuenta grande', 'Antes da próxima conta grande') });
    for (var d = 1; d <= 5; d++) {
      var big = d === 1 ? 'p2' : 'L' + (d - 1);
      s.push({ bead: big, p: 'mystery', d: d, label: T('Decade ' + d + ': announce the mystery', 'Decena ' + d + ': anuncia el misterio', 'Dezena ' + d + ': anuncie o mistério') });
      s.push({ bead: big, p: 'our', d: d, label: T('Decade ', 'Decena ', 'Dezena ') + d });
      for (var h = 1; h <= 10; h++) s.push({ bead: 'd' + d + '_' + h, p: 'hail', d: d, k: h, label: T('Decade ' + d + ' · Hail Mary ' + h + ' of 10', 'Decena ' + d + ' · Avemaría ' + h + ' de 10', 'Dezena ' + d + ' · Ave-Maria ' + h + ' de 10') });
      var after = d < 5 ? 'L' + d : 'center';
      s.push({ bead: after, p: 'glory', d: d, label: T('End of decade ', 'Fin de la decena ', 'Fim da dezena ') + d });
      s.push({ bead: after, p: 'fatima', d: d, label: T('End of decade ' + d + ' (optional)', 'Fin de la decena ' + d + ' (opcional)', 'Fim da dezena ' + d + ' (opcional)') });
    }
    s.push({ bead: 'center', p: 'queen', label: T('Closing prayers', 'Oraciones finales', 'Orações finais') });
    s.push({ bead: 'center', p: 'close', label: T('Closing prayers', 'Oraciones finales', 'Orações finais') });
    s.push({ bead: 'cross', p: 'sign', label: T('Finish at the crucifix', 'Termina en el crucifijo', 'Termine no crucifixo') });
    return s;
  }
  var STEPS = buildSteps();

  /* ---- Draw the rosary ---- */
  var NS = 'http://www.w3.org/2000/svg';
  var svg = $('#rosary-svg'), beads = {};
  function circle(id, x, y, r, cls) {
    var c = document.createElementNS(NS, 'circle');
    c.setAttribute('cx', x.toFixed(1)); c.setAttribute('cy', y.toFixed(1)); c.setAttribute('r', r);
    c.setAttribute('class', 'bead ' + cls);
    svg.appendChild(c); beads[id] = c; return c;
  }
  (function draw() {
    var cx = 150, cy = 135, R = 118;
    var chain = document.createElementNS(NS, 'circle');
    chain.setAttribute('cx', cx); chain.setAttribute('cy', cy); chain.setAttribute('r', R); chain.setAttribute('class', 'chain');
    svg.appendChild(chain);
    var line = document.createElementNS(NS, 'path');
    line.setAttribute('d', 'M150 ' + (cy + R) + ' V 382'); line.setAttribute('class', 'chain');
    svg.appendChild(line);
    // Loop: decade 1 runs up the right side from the centerpiece
    var units = [];
    for (var d = 1; d <= 5; d++) {
      for (var h = 1; h <= 10; h++) units.push({ id: 'd' + d + '_' + h, w: 1, cls: 'small' });
      if (d < 5) units.push({ id: 'L' + d, w: 1.9, cls: 'large' });
    }
    var total = units.reduce(function (a, u) { return a + u.w; }, 0), gap = 3.2;
    var step = 2 * Math.PI / (total + gap), a = Math.PI / 2 - step * gap / 2;
    units.forEach(function (u) {
      a -= step * u.w / 2;
      circle(u.id, cx + R * Math.cos(a), cy + R * Math.sin(a), u.cls === 'large' ? 7.5 : 5, u.cls);
      a -= step * u.w / 2;
    });
    var c = circle('center', 150, cy + R, 9, 'center');
    c.setAttribute('rx', 3);
    circle('p2', 150, cy + R + 26, 7.5, 'large');
    circle('ps1', 150, cy + R + 46, 5, 'small');
    circle('ps2', 150, cy + R + 62, 5, 'small');
    circle('ps3', 150, cy + R + 78, 5, 'small');
    circle('p1', 150, cy + R + 99, 7.5, 'large');
    var cross = document.createElementNS(NS, 'path');
    var top = cy + R + 114;
    cross.setAttribute('d', 'M150 ' + top + ' v38 M138 ' + (top + 11) + ' h24');
    cross.setAttribute('class', 'bead cross');
    svg.appendChild(cross); beads.cross = cross;
  })();

  /* ---- State ---- */
  var KEY = 'cd-rosary', at = 0, set = BY_DAY[new Date().getDay()], lock = null;
  try {
    var saved = JSON.parse(localStorage.getItem(KEY));
    if (saved && Date.now() - saved.t < 6 * 3600 * 1000 && SETS[saved.set]) { at = saved.i; set = saved.set; }
  } catch (e) {}
  function save() { try { localStorage.setItem(KEY, JSON.stringify({ i: at, set: set, t: Date.now() })); } catch (e) {} }

  var picker = $('#rosary-set');
  Object.keys(SETS).forEach(function (k) {
    var o = document.createElement('option');
    o.value = k; o.textContent = SETS[k].name + (k === BY_DAY[new Date().getDay()] ? T(' (today)', ' (hoy)', ' (hoje)') : '');
    picker.appendChild(o);
  });
  picker.value = set;
  picker.addEventListener('change', function () { set = picker.value; show(at); });

  function esc(x) { return String(x).replace(/[&<>]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]; }); }

  function show(i) {
    at = Math.max(0, Math.min(STEPS.length - 1, i));
    var st = STEPS[at], S = SETS[set];
    Object.keys(beads).forEach(function (k) { beads[k].classList.remove('now'); beads[k].classList.remove('done'); });
    for (var j = 0; j < at; j++) if (beads[STEPS[j].bead]) beads[STEPS[j].bead].classList.add('done');
    beads[st.bead].classList.remove('done'); beads[st.bead].classList.add('now');

    var html = '<p class="rs-where">' + esc(st.label) + '</p>';
    if (st.d) {
      var m = S.m[st.d - 1];
      html += '<div class="rs-mystery"><span class="rs-num">' + (PT ? ['Primeiro', 'Segundo', 'Terceiro', 'Quarto', 'Quinto'][st.d - 1] + ' Mistério ' + S.short : ES ? ['Primer', 'Segundo', 'Tercer', 'Cuarto', 'Quinto'][st.d - 1] + ' Misterio ' + S.short : ['First', 'Second', 'Third', 'Fourth', 'Fifth'][st.d - 1] + ' ' + S.name.replace(' Mysteries', '') + ' Mystery') + '</span>' +
        '<strong>' + esc(m[0]) + '</strong>' +
        (st.p === 'mystery' ? '<p>' + esc(m[3]) + '</p><p class="rs-meta">' + T('Read', 'Lee', 'Leia') + ': <a href="https://bible.usccb.org/bible/' + bibleSlug(m[4] || m[1]) + '" target="_blank" rel="noopener"' + (ES || PT ? ' hreflang="en"' : '') + '>' + esc(m[1]) + '</a> &middot; ' + T('Fruit of the mystery', 'Fruto del misterio', 'Fruto do mistério') + ': ' + esc(m[2]) + '</p>' : '') +
        '</div>';
    }
    if (st.p === 'mystery') {
      html += '<p class="rs-text">' + T('Announce the mystery, and picture the scene as you pray this decade.', 'Anuncia el misterio e imagina la escena mientras rezas esta decena.', 'Anuncie o mistério e imagine a cena enquanto reza esta dezena.') + '</p>';
    } else {
      var p = P[st.p];
      if (st.p === 'hail') {
        var n = st.d ? 10 : 3, k = st.k, dots = '';
        for (var q = 1; q <= n; q++) dots += '<span class="' + (q < k ? 'done' : q === k ? 'now' : '') + '"></span>';
        html += '<div class="rs-dots" aria-label="' + T('Hail Mary ', 'Avemaría ', 'Ave-Maria ') + k + T(' of ', ' de ', ' de ') + n + '">' + dots + '</div>';
      }
      if (latin && LA[st.p]) {
        html += '<h3><span lang="la">' + esc(LA[st.p].t) + '</span> <span class="small muted">(' + esc(p.t) + ')</span></h3>' + (st.note ? '<p class="rs-note">' + esc(st.note) + '</p>' : '') +
          '<p class="rs-text" lang="la">' + esc(LA[st.p].x).replace(/\n/g, '<br>') + '</p><p class="rs-trans">' + esc(p.x) + '</p>';
      } else {
        html += '<h3>' + esc(p.t) + '</h3>' + (st.note ? '<p class="rs-note">' + esc(st.note) + '</p>' : '') + '<p class="rs-text">' + esc(p.x).replace(/\n/g, '<br>') + '</p>';
      }
    }
    $('#rosary-step').innerHTML = html;
    $('#rs-count').textContent = (at + 1) + ' / ' + STEPS.length;
    $('#rs-bar').style.width = ((at + 1) / STEPS.length * 100) + '%';
    $('#rs-back').disabled = at === 0;
    $('#rs-next').innerHTML = at === STEPS.length - 1 ? T('Amen. Start over', 'Amén. Empezar de nuevo', 'Amém. Recomeçar') : T('Next', 'Siguiente', 'Próximo') + ' &rarr;';
    save();
  }

  function bibleSlug(ref) {
    // "Luke 1:26-38" -> "luke/1?26" style deep link on the USCCB site
    var m = /^(\d?\s?[A-Za-z]+)\s(\d+)(?::(\d+))?/.exec(ref);
    if (!m) return '';
    var book = m[1].toLowerCase().replace(/\s/g, '');
    if (book === 'revelation') book = 'revelation';
    return book + '/' + m[2] + (m[3] ? '?' + m[3] : '');
  }

  function next() { if (at === STEPS.length - 1) { show(0); } else show(at + 1); keepAwake(); }
  function back() { show(at - 1); }
  function keepAwake() {
    if (!lock && navigator.wakeLock && document.visibilityState === 'visible') {
      navigator.wakeLock.request('screen').then(function (l) { lock = l; l.addEventListener('release', function () { lock = null; }); }).catch(function () {});
    }
  }
  $('#rs-next').addEventListener('click', next);
  $('#rs-back').addEventListener('click', back);
  $('#rs-restart').addEventListener('click', function () { show(0); });
  var latBtn = $('#rs-latin');
  if (latBtn) {
    latBtn.setAttribute('aria-pressed', latin ? 'true' : 'false');
    latBtn.addEventListener('click', function () {
      latin = !latin;
      latBtn.setAttribute('aria-pressed', latin ? 'true' : 'false');
      try { localStorage.setItem('cd-rosary-latin', latin ? '1' : '0'); } catch (e) {}
      show(at);
    });
  }
  svg.addEventListener('click', next);
  document.addEventListener('keydown', function (e) {
    if (e.target.tagName === 'SELECT') return;
    if (e.key === 'ArrowRight' || e.key === ' ') { e.preventDefault(); next(); }
    else if (e.key === 'ArrowLeft') back();
  });
  var x0 = null;
  root.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
  root.addEventListener('touchend', function (e) {
    if (x0 === null) return;
    var dx = e.changedTouches[0].clientX - x0; x0 = null;
    if (Math.abs(dx) > 60) (dx < 0 ? next : back)();
  });
  root.hidden = false;
  var nojs = $('#rosary-nojs'); if (nojs) nojs.hidden = true;
  show(at);
})();
