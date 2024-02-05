import os

import FasterCode

from Code.Engines import Engines


def read_engines(folder_engines):
    dic_engines = {}

    def mas(clave, autor, version, url, exe, elo, folder=None, nodes_compatible=None):
        if folder is None:
            folder = clave
        path_exe = os.path.join(folder_engines, folder, exe)
        engine = Engines.Engine(clave, autor, version, url, path_exe, )
        engine.elo = elo
        engine.set_uci_option("Log", "false")
        engine.set_uci_option("Ponder", "false")
        engine.set_uci_option("Hash", "16")
        engine.set_uci_option("Threads", "1")
        dic_engines[clave] = engine
        if nodes_compatible is not None:
            engine.set_nodes_compatible(nodes_compatible)
        # engine.read_uci_options()
        return engine

    bmi2 = "-bmi2" if FasterCode.bmi2() else ""

    for level in range(1100, 2000, 100):
        cm = mas("maia-%d" % level,
                 "Reid McIlroy-Young,Ashton Anderson,Siddhartha Sen,Jon Kleinberg,Russell Wang + LcZero team",
                 "%d" % level, "https://maiachess.com/", "Lc0-0.27.0", level, folder="maia", nodes_compatible=True)
        cm.set_uci_option("WeightsFile", "maia-%d.pb.gz" % level)
        cm.path_exe = os.path.join(folder_engines, "maia", "Lc0-0.27.0")
        cm.name = "maia-%d" % level
        cm.set_uci_option("Ponder", "false")
        cm.set_uci_option("Hash", "8")
        cm.set_uci_option("Threads", "1")

    cm = mas("lc0", "The LCZero Authors", "0.27.0", "https://github.com/LeelaChessZero", "Lc0-0.27.0", 3332,
             nodes_compatible=True)
    cm.set_uci_option("Hash", "64")
    cm.set_uci_option("Threads", "2")
    cm.set_multipv(10, 500)

    cm = mas("stockfish", "Tord Romstad, Marco Costalba, Joona Kiiski", f"16{bmi2}", "http://stockfishchess.org/",
             f"Stockfish-16_x64{bmi2}", 3611)
    cm.set_uci_option("Hash", "64")
    cm.set_uci_option("Threads", "2")
    cm.set_multipv(10, 500)

    avx2 = "-avx2" if bmi2 else ""
    cm = mas("komodo", "Don Dailey, Larry Kaufman, Mark Lefler, Dmitry Pervov, Dietrich Kappe", f"dragon-1{avx2}",
             "http://komodochess.com/", f"dragon-linux{avx2}", 3529, nodes_compatible=True)
    cm.set_uci_option("Hash", "64")
    cm.set_uci_option("Threads", "2")
    cm.set_multipv(10, 218)

    mas("alouette", "Roland Chastain", "0.1.4", "https://gitlab.com/rchastain/alouette", "Alouette-0.1.4", 689)

    mas("amoeba", "Richard Delorme", "2.6", "https://github.com/abulmo/amoeba", "Amoeba-2.6", 2911,
        nodes_compatible=True)

    mas("andscacs", "Daniel José Queraltó", "0.95", "http://www.andscacs.com/", "Andscacs-0.95", 3240)

    mas("arasan", "Jon Dart", "22.2", "https://www.arasanchess.org/", "Arasan-22.2", 3259)

    mas("asymptote", "Maximilian Lupke", "0.8", "https://github.com/malu/asymptote", "Asymptote-0.8", 2909,
        nodes_compatible=True)

    mas("beef", "Jonathan Tseng", "0.36", "https://github.com/jtseng20/Beef", "Beef-0.36", 3097)

    cm = mas("cassandre", "Jean-Francois Romang), Raphael Grundrich, Thomas Adolph, Chad Koch", "0.24",
             "https://sourceforge.net/projects/cassandre/", "Cassandre-0.24", 1140)

    mas("ceechess", "Tom Reinitz", "1.3.2", "https://github.com/bctboi23/CeeChess", "CeeChess-1.3.2", 2268)

    mas("cheng", "Martin Sedlák", "4.40", "http://www.vlasak.biz/cheng", "Cheng-4.40", 2750)

    mas("cinnamon", "Giuseppe Cannella", "1.2b", "http://cinnamonchess.altervista.org/", "Cinnamon-1.2b", 1930)

    mas("chessika", "Laurent Chea", "2.21", "https://gitlab.com/MrPingouin/chessika", "Chessika-2.21", 1441)

    cm = mas("clarabit", "Salvador Pallares Bejarano", "1.00", "https://sites.google.com/site/sapabe/", "Clarabit-1.00",
             2058)
    cm.set_uci_option("OwnBook", "false")

    mas("counter", "Vadim Chizhov", "3.7", "https://github.com/ChizhovVadim/CounterGo", "Counter-3.7", 2963,
        nodes_compatible=True)

    mas("critter", "Richard Vida", "1.6a", "http://www.vlasak.biz/critter", "Critter-1.6a", 3091)

    mas("ct800", "Rasmus Althoff", "1.42", "https://www.ct800.net/", "CT800-1.42", 2380, nodes_compatible=True)

    mas("daydreamer", "Aaron Becker", "1.75 JA", "http://github.com/AaronBecker/daydreamer/downloads",
        "Daydreamer-1.75", 2670, nodes_compatible=True)

    mas("delocto", "Moritz Terink", "0.61n", "https://github.com/moterink/Delocto", "Delocto-0.61n", 2625)

    mas("discocheck", "Lucas Braesch", "5.2.1", "https://github.com/lucasart/", "Discocheck-5.2.1", 2700,
        nodes_compatible=True)

    mas("dragontooth", "Dylan Hunn", "0.2", "https://github.com/dylhunn/dragontooth", "Dragontooth-0.2", 1225)

    mas("drofa", "Rhys Rustad-Elliott and Alexander Litov", "3.3.0", "https://github.com/justNo4b/Drofa", "Drofa-3.3.0",
        2642)

    mas("ethereal", "Andrew Grant, Alayan & Laldon", "12.75", "https://github.com/AndyGrant/Ethereal", "Ethereal-12.75",
        3392)

    mas("foxcub", "Lucas Monge", "1.1", "", "FoxCub", 800)

    mas("fox", "Lucas Monge", "1.1", "", "Fox", 1400)

    mas("fractal", "Visan Alexandru", "1.0", "https://github.com/visanalexandru/FracTal-ChessEngine", "FracTal-1.0",
        2010)

    mas("fruit", "Fabien Letouzey", "2.1", "http://www.fruitchess.com/", "Fruit-2.1", 2784)

    mas("gambitfruit", "Ryan Benitez, Thomas Gaksch and Fabien Letouzey", "1.0 Beta 4bx",
        "https://github.com/lazydroid/gambit-fruit", "gfruit", 2750)

    mas("gaviota", "Miguel Ballicora", "0.84", "https://sites.google.com/site/gaviotachessengine/Home", "Gaviota-0.84",
        2638, nodes_compatible=True)

    mas("glaurung", "Tord RomsTad", "2.2", "http://www.glaurungchess.com/", "Glaurung-2.2", 2765, nodes_compatible=True)

    mas("godel", "Juan Manuel Vazquez", "7.0", "https://sites.google.com/site/godelchessengine", "Godel-7.0", 2979,
        nodes_compatible=True)

    mas("goldfish", "Bendik Samseth", "1.13.0", "https://github.com/bsamseth/Goldfish", "Goldfish-1.13.0", 2050,
        nodes_compatible=True)

    mas("greko", "Vladimir Medvedev", "2020.03", "http://greko.su/index_en.html", "GreKo-2020.03", 2580,
        nodes_compatible=True)

    mas("greko98", "Vladimir Medvedev", "9.8", "http://sourceforge.net/projects/greko", "GreKo98a", 2500,
        nodes_compatible=True)

    mas("gunborg", "Torbjorn Nilsson", "1.35", "https://github.com/torgnil/gunborg", "Gunborg-1.35", 2086)

    mas("hactar", "Jost Triller", "0.9.05", "https://github.com/tsoj/hactar", "Hactar-0.9.0", 1421)

    mas("igel", "Volodymyr Shcherbyna", "3.0.0", "https://github.com/vshcherbyna/igel/", "Igel-3.0.10", 3402,
        nodes_compatible=True)

    mas("irina", "Lucas Monge", "0.16", "https://github.com/lukasmonk/irina", "irina-0.16", 1500)

    mas("jabba", "Richard Allbert", "1.0", "http://jabbachess.blogspot.com/", "Jabba-1.0", 2078)

    mas("k2", "Sergey Meus", "0.99", "https://github.com/serg-meus/k2", "K2-0.99", 2704, nodes_compatible=True)

    mas("laser", "Jeffrey An and Michael An", "1.7", "https://github.com/jeffreyan11/laser-chess-engine", "Laser-1.17",
        3227)

    mas("marvin", "Martin Danielsson", "5.0.0", "https://github.com/bmdanielsson/marvin-chess", "Marvin-5.0.0", 3112,
        nodes_compatible=True)

    mas("monolith", "Jonas Mayr", "2.01", "https://github.com/cimarronOST/Monolith", "Monolith-2.01", 3003,
        nodes_compatible=True)

    mas("monochrome",
        "Dan Ravensloft, formerly Matthew Brades (England), Manik Charan (India), George Koskeridis, Robert Taylor", "",
        "https://github.com/cpirc/Monochrome", "Monochrome", 1601)

    mas("octochess", "Tim Kosse", "r5190", "http://octochess.org/", "Octochess-r5190", 2771)  # New build

    mas("pawny", "Mincho Georgiev", "1.2", "http://pawny.netii.net/", "Pawny-1.2", 2550)

    mas("pigeon", "Stuart Riffle", "1.5.1", "https://github.com/StuartRiffle/pigeon", "Pigeon-1.5.1", 1836)

    mas("pulse", "Phokham Nonava", "1.6.1", "https://github.com/fluxroot/pulse", "Pulse-1.6.1", 1615,
        nodes_compatible=True)

    mas("quokka", "Matt Palmer", "2.1", "https://github.com/mattbruv/Quokka", "Quokka-2.1", 1448)  # New build

    mas("rocinante", "Antonio Torrecillas", "2.0", "http://sites.google.com/site/barajandotrebejos/", "Rocinante-2.0",
        1800)

    mas("rodentii", "Pawel Koziol", "0.9.64", "http://www.pkoziol.cal24.pl/rodent/rodent.htm", "RodentII-0.9.64", 2912,
        nodes_compatible=True)

    mas("shallow-blue", "Rhys Rustad-Elliott", "2.0.0", "https://github.com/GunshipPenguin/shallow-blue",
        "Shallow-blue-2.0.0", 1712)

    mas("simplex", "Antonio Torrecillas", "0.98", "http://sites.google.com/site/barajandotrebejos", "Simplex-0.9.8",
        2396)

    mas("sissa", "Christophe J. Mandin", "2.0", "http://devzero.fr/~mnc/SISSA/fr/index_fr.html", "Sissa-2.0", 1957)

    mas("spacedog", "Eric Silverman", "0.97.7", "https://github.com/thorsilver/SpaceDog", "SpaceDog-0.97.7", 2231)

    mas("stash", "Morgan Houppin", "29.0", "https://gitlab.com/mhouppin/stash-bot", "Stash-29.0", 3065)

    mas("supernova", "Minkai Yang", "2.3", "https://github.com/MichaeltheCoder7/Supernova", "Supernova-2.3", 2646,
        nodes_compatible=True)

    mas("teki", "Manik Charan", "2", "https://github.com/Mk-Chan/Teki", "Teki-2", 2439)

    mas("texel", "Peter Österlund", "1.06", "http://web.comhem.se/petero2home/javachess/index.html#texel", "Texel-1.06",
        2900)

    cm = mas("toga", "WHMoweryJr,Thomas Gaksch,Fabien Letouzey", "deepTogaNPS 1.9.6",
             "http://www.computerchess.info/tdbb/phpBB3/viewtopic.php?f=9&t=357", "DeepToga1.9.6nps", 2843)
    cm.set_multipv(10, 40)

    mas("tucano", "Alcides Schulz", "9.00", "https://sites.google.com/site/tucanochess", "Tucano-9.00", 2940,
        nodes_compatible=True)

    mas("tunguska", "Fernando Tenorio", "1.1", "https://github.com/fernandotenorio/Tunguska", "Tunguska-1.1", 2439)

    mas("velvet", "Martin Honert", "1.2.0", "https://github.com/mhonert/velvet-chess", "Velvet-1.2.0", 2686)

    mas("weiss", "Terje Kirstihagen", "1.2", "https://github.com/TerjeKir/weiss", "Weiss-1.2", 2982)

    mas("wowl", "Eric Yip", "1.3.7", "https://github.com/eric-ycw/wowl", "Wowl-1.3.7", 1925, nodes_compatible=True)

    mas("wyldchess", "Manik Charan", "1.51", "https://github.com/Mk-Chan/WyldChess", "WyldChess-1.51", 2682)

    mas("zappa", "Anthony Cozzie", "1.1", "http://www.acoz.net/zappa/", "Zappa-1.1", 2614, nodes_compatible=True)

    mas("zurichess", "Alexandru Mosoi", "1.7.4", "https://bitbucket.org/zurichess/zurichess/", "Zurichess-1.7.4", 2830)

    return dic_engines


def dict_engines_fixed_elo(folder_engines):
    d = read_engines(folder_engines)
    dic = {}
    for nm, xfrom, xto in (
    ("stockfish", 1400, 2800), ("arasan", 1000, 2600), ("cheng", 800, 2500), ("greko", 1600, 2400)):
        for elo in range(xfrom, xto + 100, 100):
            cm = d[nm].clona()
            if elo not in dic:
                dic[elo] = []
            cm.set_uci_option("UCI_Elo", str(elo))
            cm.set_uci_option("UCI_LimitStrength", "true")
            cm.name += " (%d)" % elo
            cm.key += " (%d)" % elo
            cm.elo = elo
            dic[elo].append(cm)
    return dic
