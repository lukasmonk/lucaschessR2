import os
import random

import Code
from Code import Util


class ThanksTo:
    def __init__(self):
        self.dic = {
            "maincontributors": _("Main contributors"),
            "contributors": _("Contributors"),
            "translators": _("Translators"),
            "images": _("Images"),
            "themes": _("Themes"),
            "pieces": _("Pieces"),
            "training": _("Training"),
            "engines-1": "%s/1" % _("Engines"),
            "engines-2": "%s/2" % _("Engines"),
            "engines-3": "%s/3" % _("Engines"),
            "engines-4": "%s/4" % _("Engines"),
            "engines-5": "%s/5" % _("Engines"),
            "games": _("Games"),
            "programming": _("Programming"),
            "dedicated": _("Dedicated to"),
        }

    @staticmethod
    def list_engines(bloque):
        li = Code.configuration.list_engines_show()
        li.sort(key=lambda xt: xt[0])
        for n, x in enumerate(li, 1):
            x[0] = "%d. %s" % (n, x[0])
        nli = len(li)
        x = nli // 5
        bl = [x, x, x, x, x]
        resto = nli - x * 5
        if resto:
            for x in range(resto):
                bl[x] += 1
        nbl = int(bloque)
        from_sq = sum(bl[: nbl - 1])
        to_sq = from_sq + bl[nbl - 1]
        return li[from_sq:to_sq]

    def texto(self, key):
        if "-" in key:
            key, arg = key.split("-")
            return getattr(self, key)(arg)
        return getattr(self, key)()

    @staticmethod
    def table_ini(center=True, border="1"):
        txt = "<center>" if center else ""
        txt += '<table border="%s" cellpadding="3" cellspacing="0" width="90%%">' % border
        return txt

    @staticmethod
    def table_end():
        return "</table>"

    @staticmethod
    def th(txt, mas=""):
        return "<th %s>%s</th>" % (mas, txt)

    @staticmethod
    def dl_ini():
        return "<blockquote><dl>"

    @staticmethod
    def dl_tit(tit):
        return "<dt><b>%s</b></dt>" % tit

    @staticmethod
    def dl_elem(elem):
        return "<dd>%s</dd>" % elem

    @staticmethod
    def dl_end():
        return "</dl></blockquote>"

    def maincontributors(self):
        li = (
            ("Michele Tumbarello", "Definition of Tourney-elo engines and the formulae for calculating the indices."),
            (
                "Alfonso Solbes",
                "His work was an essential help (saved many hours) in the transition from Python 2.7 (version 11) to Python 3 (version R).",
            ),
            ("Eric", "Main betatester."),
            (
                "Johannes Bolzano",
                "Code improvements and ideas to Find best move training and more.",
            ),  # Programme wiki administrator"),
            (
                "Laudecir Daniel",
                "Main promoter of the Linux version, he did the selection and compilation of engines, as well as the establishment of the working Linux version.",
            ),
            (
                '<a href="https://goneill.co.nz/index.php">Graham O\'Neill</a>',
                "Author of the drivers for the use of the electronic boards (except the official DGT ones). Also co-operator in the development of the interface code with the electronic boards.",
            ),
        )

        txt = self.dl_ini()
        for person, task in li:
            txt += self.dl_tit(person)
            txt += self.dl_elem(task) + "<hr>"
        txt += self.dl_end()
        return txt

    def contributors(self):
        txt = self.dl_ini()

        def version(num, li_basex, li_restox, sim=True):
            random.shuffle(li_basex)
            li_basex.extend(li_restox)
            mtxt = self.dl_tit(_("Version %s") % num)
            el_txt = ""
            if sim:
                el_txt += "Michele Tumbarello, "
            n = 0
            for uno in li_basex:
                if n >= 110:
                    el_txt += "<br>"
                    n = 0
                el_txt += uno + ", "
                elem = uno
                if ">" in elem:
                    elem = elem.split(">")[1].split("<")[0]
                n += len(elem)

            mtxt += self.dl_elem(el_txt[:-2]) + "<hr>"
            return mtxt.replace(", ,", ",")

        # Version R
        li_base = [
            "Alan Lee",
            "Nambi",
            '<a href="https://github.com/phihag">Philipp Hagemeister</a>',
            '<a href="https://github.com/futurelauncher">futurelauncher</a>',
            "Reinhard",
            "Olav Stüwe",
            '<a href="http://99-developer-tools.com/chess/">A. Wicker</a>',
            'Budana P',
            'Rudolf Krämer'
            ""
        ]
        li_resto = []
        txt += version("R", li_base, li_resto, False)

        # Version 11
        li_base = [
            "Alfonso Solbes",
            "Max Aloyau",
            "tico-tico",
            "Nils Andersson",
            "Bernhard",
            "Ed Smith",
            "Rob",
            "Giovanni di Maria",
            "vga",
            "Remes",
            "Péter Rabi",
            "Iñaki Rodriguez",
        ]
        li_resto = ["Immortalchess forum"]
        txt += version(11, li_base, li_resto)

        # Version 10
        li_base = ["Remes", "Max Aloyau", "Alfonso Solbes", "tico-tico", "Nils Andersson", "Bernhard", "Ed Smith"]
        li_resto = ["Immortalchess forum"]
        txt += version(10, li_base, li_resto)

        # Version 9
        li_base = [
            "Indianajones",
            "Pavel Rehulka",
            "ADT",
            "Adrijan",
            "Nils Andersson",
            "Urban Gustavsson",
            "Johannes Reimers",
            "Red Hood",
            "Robert Anderson",
            "Laudecir Daniel",
            "Reinhard",
            "Giovanni di Maria",
            "Filomeno Marmalé",
            "Max Aloyau",
        ]
        li_resto = ["Chessindia forum", "Immortalchess forum"]
        txt += version(9, li_base, li_resto)

        # Version 8
        li_base = [
            "Indianajones",
            "James",
            "Uli",
            "Pavel Rehulka",
            "Laudecir Daniel",
            "Xavier Jimenez",
            "Rajkrishna",
            "ADT",
            "Vishy",
            "thetasquared",
            "Mike Eddies",
            "jayriginal",
            "baddadza",
            "bbbaro25us",
            "Victor Perez",
            "M.Larson",
            "Filomeno Marmalé",
            "Shahin Jafarli (shahinjy)",
            "Heikki Junes",
            "Toan Luong",
            "R. Sehgal",
            "WyoCas",
            "J.Reimers",
            "Dariusz Popadowski",
            "Ken Brown",
            "Dieter Heinrich",
            "Nils Andersson",
            "Chris K.",
            "Philou",
        ]
        li_resto = ["Chessindia forum", "Immortalchess forum"]
        txt += version(8, li_base, li_resto, False)

        # Version 1..7
        li_base = [
            "Felicia",
            "Shahin Jafarli (shahinjy)",
            "Alfons",
            "Raúl Giorgi",
            "Red Hood",
            "Filomeno Marmalé",
            "Roberto Mizzoni",
            "bolokay",
            "Istolacio",
            "Mohammed Abdalazez",
            "Rui Grafino",
            "Georg Pfefferle",
            "Lolo S.",
            "Joaquín Alvarez",
            "Ransith Fernando",
        ]
        li_resto = ["Gianfranco Cutipa", "Daniel Trebejo", "Jose Luis García", "Carmen Martínez"]  # "Ezequiel Canario"
        txt += version("1..7", li_base, li_resto, False)

        txt += self.dl_end()
        return txt

    def translators(self):
        txt = self.table_ini(center=False, border="0")
        txt += "<tr><td>"
        txt += self.dl_ini()
        li = os.listdir(Code.path_resource("Locale"))
        salto = len(li) // 2
        for n, lng in enumerate(li):
            if len(lng) > 2:
                continue
            d = Util.ini_base2dic(Code.path_resource("Locale", "%s/lang.ini" % lng))
            if n >= salto:
                salto = 99
                txt += self.dl_end()
                txt += "</td><td>"
                txt += self.dl_ini()
            txt += self.dl_tit(d["NAME"])
            txt += self.dl_elem(d["AUTHOR"])
            if "PREVIOUS" in d:
                txt += self.dl_elem("%s: %s" % (_("Previous"), d["PREVIOUS"]))

        txt += self.dl_end()
        txt += "</td></tr>"
        txt += self.table_end()
        txt += (
                '<big><bold><center>%s: <a href="https://explore.transifex.com/">Transifex</a>'
                % _("Web")
        )
        txt += ' -  <a href="https://app.transifex.com/join/?o=lukasmonk&p=lucaschess&t=opensource">Join Translation of LucasChess</a></center></bold></big>'
        return txt

    def images(self):
        txt = self.table_ini()

        li = [
            ("Nuvola", "David Vignoni", "https://www.icon-king.com/projects/nuvola/", "LGPL"),
            (
                "Icons for Windows8",
                "Icons8",
                "https://icons8.com",
                "Creative Commons Attribution-NoDerivs 3.0 Unported",
            ),
            ("Gnome", "Gnome", "https://commons.wikimedia.org/wiki/GNOME_Desktop_icons", "GPL"),
            (
                "Silk icon set 1.3",
                "Mark James",
                "https://github.com/markjames/famfamfam-silk-icons",
                "Creative Commons Attribution 2.5 License",
            ),
            ("Wooicons1", "Janik Baumgartner", "https://www.woothemes.com/2010/08/woocons1/", "GPL"),
            (
                "Ultimate Gnome 0.5.1",
                "Marco Tessarotto",
                "https://gnome-look.org/content/show.php/Ultimate+Gnome?content=75000",
                "GPL",
            ),
            ("SnowIsh SVG", "Saki", "https://gnome-look.org/content/show.php/SnowIsh+SVG+%26+PNG?content=32599", "GPL"),
            (
                "Cartoon animal icons",
                "Martin Bérubé",
                "https://www.how-to-draw-funny-cartoons.com/",
                _("Free for personal non-commercial use"),
            ),
            (
                "Album of vehicles",
                "Icons-Land",
                "https://www.icons-land.com/vista-icons-transport-icon-set.php",
                "Icons-Land Demo License Agreement",
            ),
            ("Figurines", "Armando H. Marroquín", "https://www.enpassant.dk/chess/fonteng.htm", _("Freeware")),
            (
                "Transsiberian map",
                "Stefan Ertmann & Lokal Profil",
                "https://commons.wikimedia.org/wiki/File:Trans-Siberian_railway_map.svg",
                "CC BY-SA 2.5 via Wikimedia Commons",
            ),
            (
                "Washing machine",
                "Shinnoske",
                "https://openclipart.org/detail/218905/simple-washing-machine",
                "Public domain",
            ),
        ]
        for tipo, autor, web, licencia in li:
            txt += "<tr>"
            txt += "<td align=right><b>%s</b></td>" % tipo
            txt += '<td><center><a href="%s">%s</a></center></td>' % (web, autor)
            txt += "<td>%s</td>" % licencia
            txt += "</tr>"

        txt += "</table></center>"
        return txt

    def themes(self):
        txt = self.table_ini()

        txt += "<tr>"
        txt += self.th(_("Author"))
        txt += self.th(_("License"))
        txt += "</tr>"

        li = [
            ("Michele Tumbarello", _("Permission of author")),
            ("Felicia", _("Permission of author")),
            ("Balestegui", _("Permission of author")),
            ("Mohammed Abdalazez", _("Permission of author")),
            ("Red Hood", _("Permission of author")),
            ("Michael Byrne", _("Permission of author")),
            ("Ben Citak", _("Permission of author")),
            ("Xpdnc", _("Permission of author")),
            ("Alexander", _("Permission of author")),
            ("Dan Brad", _("Permission of author")),
            ("Tamer64", _("Permission of author")),
        ]
        for autor, licencia in li:
            txt += "<tr>"
            txt += "<td align=center>%s</td>" % autor
            txt += "<td>%s</td>" % licencia
            txt += "</tr>"
        txt += "</table>"

        txt += '<br><table border="1" cellpadding="5" cellspacing="0" >'
        txt += "<tr>"
        txt += self.th(_("Colors"))
        txt += self.th(_("Author"))
        txt += '<th>%s: <a href="%s">%s</a></th>' % (
            _("License"),
            "https://creativecommons.org/licenses/by-nc-sa/3.0/",
            "Attribution-NonCommercial-ShareAlike 3.0 Unported",
        )
        txt += "</tr>"

        li = [
            ("Armani Closet", "mimi22", "https://www.colourlovers.com/palette/117475/armani_closet"),
            ("Chocolate Creams", "Skyblue2u", "https://www.colourlovers.com/palette/582195/Chocolate_Creams"),
            ("Good Friends", "Yasmino", "https://www.colourlovers.com/palette/77121/Good_Friends"),
            ("Nectarius", "note", "https://www.colourlovers.com/palette/1897208/nectarius"),
            ("Trajan", "Jaime Guadagni aka The Cooler", "https://www.colourlovers.com/palette/67170/Trajan"),
        ]

        for tipo, autor, web in li:
            txt += "<tr>"
            txt += "<td align=right>%s</td>" % tipo
            txt += "<td align=center>%s</td>" % autor
            txt += '<td><a href="%s">%s</a></td>' % (web, web)
            txt += "</tr>"

        txt += "</table><center>"
        return txt

    def pieces(self):
        txt = self.table_ini()

        li = [
            ("ChessiconsV3.5", '<a href="https://www.virtualpieces.net">Peter Wong</a>', _("Permission of author")),
            ("Merida-Internet", '<a href="https://www.rybkachess.com">Felix Kling</a>', _("Permission of author")),
            (
                "Spatial-Fantasy-Fantasy Alt<br>SKulls-Freak-Prmi<br>Celtic-Eyes",
                '<a href="https://poisson.phc.unipi.it/~monge/chess_art.php">Maurizio Monge</a>',
                "GPL",
            ),
            (
                "Cburnett",
                '<a href="https://en.wikipedia.org/wiki/User:Cburnett/GFDL_images/Chess">Cburnett</a>',
                "Creative Commons Attribution 2.5 License",
            ),
            (
                "Chess Alpha",
                '<a href="https://www.enpassant.dk/chess/fonteng.htm">Eric Bentzen</a>',
                _("Permission of author"),
            ),
            (
                "Montreal",
                '<a href="https://alcor.concordia.ca/~gpkatch/montreal_font.html">Gary Katch</a>',
                _("Permission of author"),
            ),
            (
                "Magnetic-AlfonsoX<br>Maya-Condal",
                '<a href="https://www.enpassant.dk/chess/fonteng.htm">Armando H. Marroquín<br>(enpassant)</a>',
                _("Freeware"),
            ),
            (
                "Leipzig",
                '<a href="https://github.com/artistofmind/Chess-Leipzig">Armando H. Marroquín<br>(github)</a>',
                "GPL",
            ),
            ("Chess Pirat", '<a href="https://www.enpassant.dk/chess/fonteng.htm">Klaus Wolf</a>', _("Freeware")),
            ("Chess Regular", '<a href="https://www.enpassant.dk/chess/fonteng.htm">Alastair Scott</a>', _("Freeware")),
            (
                "Chess Regular2",
                '<a href="https://www.enpassant.dk/chess/fonteng.htm">Regular redesigned by Tamer64</a>',
                _("Freeware"),
            ),
            (
                "Kilfiger",
                '<a href="https://sites.google.com/site/jameskilfiger/">James Kilfiger</a>',
                "SIL open font licence",
            ),
            (
                "Cartoon",
                '<a href="https://www.how-to-draw-funny-cartoons.com">Based on work by <br>Martin Bérubé</a>',
                _("Free for personal non-commercial use"),
            ),
            (
                "Qwertyxp2000",
                '<a href="https://commons.wikimedia.org/wiki/File%3AChess_pieces_(qwertyxp2000).svg">Qwertyxp2000</a>',
                "Creative Commons Attribution 2.5 License",
            ),
            (
                "Jin Alpha",
                '<a href="https://ixian.com/chess/jin-piece-sets/">Eric De Mund</a>',
                "Creative Commons Attribution-Share<br>Alike3.0 Unported",
            ),
            ("Etruscan<br>Etruscan clear", '<a href="https://zipanatura.fr/">Fabrice</a>', "CC BY-NC-ND 4.0"),
            (
                "Stauton 3D<br>Kidsdraw",
                '<a href="https://plus.google.com/101635611158475796811/about">Marc Graziani</a>',
                _("Permission of author"),
            ),
            (
                "Book Classic<br>Book Diagram<br>Book Strategie",
                '<a href="https://www.linkedin.com/in/benjamin-citak-04982714">Ben Citak</a>',
                _("Permission of author"),
            ),
            (
                "Balestegui<br>Balestegui2",
                "",
                _("Permission of author"),
            ),
        ]
        salto = len(li) // 2
        if salto * 2 < len(li):
            salto += 1
        for n in range(salto):
            txt += "<tr>"

            tipo, autor, licencia = li[n * 2]
            if n * 2 + 1 < len(li):
                tipo1, autor1, licencia1 = li[n * 2 + 1]
            else:
                tipo1, autor1, licencia1 = "", "", ""
            txt += "<td align=right><b>%s</b></td>" % tipo
            txt += "<td><center>%s</center></td>" % autor
            txt += "<td>%s</td>" % licencia

            txt += "<td align=right><b>%s</b></td>" % tipo1
            txt += "<td><center>%s</center></td>" % autor1
            txt += "<td>%s</td>" % licencia1

        txt += self.table_end()
        return txt

    def training(self):
        txt = self.table_ini()

        txt += "<tr>"
        txt += self.th(_("Training"))
        txt += self.th(_("Web"))
        txt += self.th(_("License"))
        txt += "</tr>"

        li = (
            (
                _("Checkmates by Eduardo Sadier"),
                '<a href="https://edusadier.googlepages.com/">https://edusadier.googlepages.com</a>',
                _("Permission of author"),
            ),
            (_("Endgames by Rui Grafino"), "", _("Permission of author")),
            (_("Varied positions by Joaquin Alvarez"), "", _("Permission of author")),
            (_("Tactics by Uwe Auerswald"), "", _("Freeware")),
            (_("Endgames by Victor Perez"), "", _("Permission of author")),
            (
                _("Tactics by UNED chess school"),
                '<a href="https://portal.uned.es/portal/page?_pageid=93,2564320&_dad=portal&_schema=PORTAL">'
                "https://portal.uned.es/portal</a>",
                _("Permission of author"),
            ),
        )
        for autor, web, licencia in li:
            txt += "<tr>"
            txt += "<td align=center><b>%s</b></td>" % autor
            txt += "<td>%s</td>" % web
            txt += "<td>%s</td>" % licencia
            txt += "</tr>"

        txt += "</table><center>"
        return txt

    def engines(self, orden):
        txt = self.table_ini()
        txt += "<tr>"
        txt += self.th(_("Engine"))
        txt += self.th(_("Author"))
        txt += self.th(_("Web"))
        txt += "</tr>"
        for name, autor, url in self.list_engines(orden):
            txt += "<tr>"
            txt += "<td>%s</td>" % name
            txt += "<td>%s</td>" % autor
            txt += '<td><a href="%s">%s</a></td>' % (url, url)
            txt += "</tr>"
        txt += self.table_end()
        return txt

    @staticmethod
    def games():
        li = (
            ("Jordi Gonzalez Boada", "http://www.jordigonzalezboada.com/ajedrez/aperturas.php"),
            ("PGN Mentor", "https://www.pgnmentor.com/files.html"),
            ("Dann Corbit", "http://cap.connx.com/"),
            ("The Week in Chess", "https://theweekinchess.com/"),
            ("Wikipedia", "https://en.wikipedia.org/wiki/List_of_chess_games"),
            ("fics", "https://www.ficsgames.org/download.html"),
            ("Norman Pollock", "http://www.nk-qy.info/40h/"),
            (
                "STS<br>" + _X(_("Created by %1"), "Dann Corbit, Swaminathan"),
                "https://sites.google.com/site/strategictestsuite/about",
            ),
            ("liChess database", "https://database.lichess.org"),
            ("lichess openings", "https://github.com/lichess-org/chess-openings"),
        )
        txt = '<center><table border="1" cellpadding="5" cellspacing="0" >'
        for nom, web in li:
            txt += "<tr>"
            txt += "<th>%s</th>" % nom
            txt += '<td><a href="%s">%s</a></td>' % (web, web)
            txt += "</tr>"
        txt += "</table><center>"
        return txt

    def programming(self):
        li = (
            (_("Programming language"), "Python 3.7", "https://www.python.org/"),
            (_("GUI"), "PySide2", "https://wiki.qt.io/Qt_for_Python"),
            ("psutil", _X(_("Created by %1"), "Giampaolo Rodola"), "https://github.com/giampaolo/psutil"),
            ("chardet", _X(_("Created by %1"), "Ian Cordasco"), "https://github.com/chardet/chardet"),
            (
                _("Polyglot books"),
                _X(_("Based on work by %1"), "Michel Van den Bergh"),
                "https://hardy.uhasselt.be/personal/vdbergh/Members/michel_id.html",
            ),
            ("python-chess", _X(_("Created by %1"), "Niklas Fiekas"), "https://github.com/niklasf/python-chess"),
            ("pillow", "Copyright 2010-2022, Alex Clark and Contributors", "https://github.com/python-pillow/Pillow"),
            ("photohash", "Chris Pickett and others", "https://github.com/bunchesofdonald/photohash"),
            (
                "cython",
                "Stefan Behnel, Robert Bradshaw, Lisandro Dalcín,<br>Mark Florisson, Vitja Makarov, Dag Sverre Seljebotn",
                "https://cython.org/",
            ),
            ("formlayout", _X(_("Created by %1"), "Pierre Raybaut"), "https://github.com/PierreRaybaut/formlayout"),
            (
                "sortedcontainers",
                _X(_("Created by %1"), "Grant Jenks"),
                "https://www.grantjenks.com/docs/sortedcontainers/",
            ),
            ("polib", "David Jean Louis and others", "https://github.com/izimobil/polib"),
        )
        txt = self.table_ini()

        for tipo, nom, web in li:
            txt += "<tr>"
            txt += "<th>%s</th>" % tipo
            txt += "<td><center>%s</center></td>" % nom
            txt += '<td><a href="%s">%s</a></td>' % (web, web)
            txt += "</tr>"

        txt += self.table_end()
        return txt

    @staticmethod
    def dedicated():
        txt = '<center><big style="color:teal;"><b>Lucas & Luisa</b></big></center>'
        return txt
