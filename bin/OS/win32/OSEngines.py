import platform

import FasterCode

from Code import Util
from Code.Engines import Engines


def read_engines(folder_engines):
    dic_engines = {}

    def mas(alias, autor, version, url, exe, elo, folder=None, emulate_movetime=None, nodes_compatible=None):
        if folder is None:
            folder = alias
        path_exe = Util.opj(folder_engines, folder, exe)
        engine = Engines.Engine(alias.lower(), autor, version, url, path_exe)
        engine.elo = elo
        engine.set_uci_option("Log", "false")
        engine.set_uci_option("Ponder", "false")
        engine.set_uci_option("Hash", "16")
        engine.set_uci_option("Threads", "1")
        dic_engines[alias] = engine
        if emulate_movetime is not None:
            engine.emulate_movetime = emulate_movetime
        if nodes_compatible is not None:
            engine.set_nodes_compatible(nodes_compatible)
        return engine

    mas("alouette", "Roland Chastain", "0.1.7", "https://codeberg.org/rchastain/alouette", "alouette32.exe", 800)

    mas("acqua", "Giovanni Di Maria", "2.0", "http://www.elektrosoft.it/scacchi/acqua/acqua.asp", "acqua.exe", 844)
    mas("foxcub", "Lucas Monge", "1.1", "", "FoxCub.exe", 800)
    mas("fox", "Lucas Monge", "1.1", "", "Fox.exe", 1400)

    mas("tarrasch", "Bill Forster", "ToyEngine Beta V0.906", "http://www.triplehappy.com/",
        "TarraschToyEngineV0.906.exe", 1481, emulate_movetime=True)

    mas(
        "rocinante",
        "Antonio Torrecillas",
        "2.0",
        "http://sites.google.com/site/barajandotrebejos/",
        "Windows/Intel/rocinante-20-32-ja.exe",
        1800,
    )

    mas("roce", "Roman Hartmann", "0.0390", "http://www.rocechess.ch/rocee.html", "roce39.exe", 1854)

    cm = mas("cinnamon", "Giuseppe Cannella", "1.2c", "https://github.com/gekomad/Cinnamon",
             "cinnamon_1.2c-generic.exe", 1930)
    cm.set_uci_option("Hash", "32")

    mas("bikjump", "Aart J.C. Bik", "2.01 (32-bit)", "http://www.aartbik.com/", "bikjump.exe", 2026)

    cm = mas("clarabit", "Salvador Pallares Bejarano", "1.00", "http://sapabe.googlepages.com",
             "clarabit_100_x32_win.exe", 2058, nodes_compatible=True)
    cm.set_uci_option("OwnBook", "false")

    mas("lime", "Richard Allbert", "v 66", "http://www.geocities.com/taciturn_lemon", "Lime_v66.exe", 2119)

    cm = mas("chispa", "Federico Corigliano", "4.0.3", "http://chispachess.blogspot.com/", "chispa403-blend.exe", 2227,
             nodes_compatible=True)
    cm.set_uci_option("Hash", "32")

    mas("ct800", "Rasmus Althoff", "1.46", "https://www.ct800.net/", "CT800_V1.46_x32.exe", 2600, nodes_compatible=True)

    cm = mas("gaia", "Jean-Francois Romang, David Rabel", "3.5", "http://gaiachess.free.fr", "gaia32.exe", 2378)
    cm.name = "Gaïa 3.5"

    mas("simplex", "Antonio Torrecillas", "0.9.8", "http://sites.google.com/site/barajandotrebejos/",
        "Windows/simplex-098-32-ja.exe", 2396)

    cm = mas("pawny", "Mincho Georgiev", "0.3.1", "http://pawny.netii.net/", "windows/pawny_0.3.1_x86.exe", 2484)
    cm.set_uci_option("OwnBook", "false")

    mas("umko", "Borko Boskovic", "0.7", "http://umko.sourceforge.net/", "w32/umko_x32.exe", 2488)

    mas("garbochess", "Gary Linscott", "2.20", "http://forwardcoding.com/projects/chess/chess.html",
        "GarboChess2-32.exe", 2526)

    mas("ufim", "Niyas Khasanov", "8.02", "http://wbec-ridderkerk.nl/html/details1/Ufim.html", "ufim802.exe", 2532)

    cm = mas("alaric", "Peter Fendrich", "707", "http://alaric.fendrich.se/index.html", "alaric707.exe", 2662,
             nodes_compatible=True)
    cm.set_uci_option("BookFile", "")
    cm.remove_log("Alaric.log")
    cm.remove_log("learn.bin")

    mas("cyrano", "Harald Johnsen", "06B17", "http://sites.estvideo.net/tipunch/cyrano/", "cyrano.exe", 2647,
        emulate_movetime=True)

    mas(
        "daydreamer",
        "Aaron Becker",
        "1.75 JA",
        "https://github.com/AaronBecker/daydreamer",
        "windows/32 bit/daydreamer-175-32-ja.exe",
        2670, nodes_compatible=True
    )

    cm = mas("godel", "Juan Manuel Vazquez", "7.0", "https://sites.google.com/site/godelchessengine", "Godel32.exe",
             2950)
    cm.name = "Gödel 7.0"

    cm = mas("rhetoric", "Alberto Sanjuan", "1.4.3", "http://www.chessrhetoric.com/", "Rhetoric_x32.exe", 2810,
             nodes_compatible=True)
    cm.set_multipv(1, 4)

    cm = mas("cheng", "Martin Sedlák", "4.40", "http://www.vlasak.biz/cheng", "cheng4.exe", 2750)
    cm.set_multipv(10, 256)

    cm = mas("glaurung", "Tord RomsTad", "2.2 JA", "http://www.glaurungchess.com/", "windows/glaurung-w32.exe", 2765,
             nodes_compatible=True)
    cm.set_multipv(10, 500)

    cm = mas("fruit", "Fabien Letouzey", "2.3.1", "http://www.fruitchess.com/", "Fruit-2-3-1.exe", 2786)
    cm.set_multipv(10, 256)

    mas("discocheck", "Lucas Braesch", "5.2.1", "https://github.com/lucasart", "DiscoCheck.exe", 2890,
        nodes_compatible=True)

    cm = mas("gaviota", "Miguel A. Ballicora", "1.0", "https://sites.google.com/site/gaviotachessengine",
             "gaviota-1.0-win32.exe", 2950, nodes_compatible=True)
    cm.set_multipv(10, 32)

    cm = mas("rybka", "Vasik Rajlich", "2.3.2a 32-bit", "http://rybkachess.com/", "Rybka v2.3.2a.w32.exe", 2936,
             nodes_compatible=True)
    cm.set_uci_option("Max CPUs", "1")
    cm.set_multipv(10, 100)

    cm = mas("critter", "Richard Vida", "1.6a 32bit", "http://www.vlasak.biz/critter/", "Critter_1.6a_32bit.exe", 3091,
             nodes_compatible=True)
    cm.set_multipv(10, 100)

    cm = mas(
        "texel", "Peter Österlund", "1.07 32bit", "https://github.com/peterosterlund2/texel",
        "texel32old.exe", 3100, nodes_compatible=True
    )
    cm.set_multipv(10, 256)

    mas("gull", "Vadim Demichev", "3 32bit", "https://sourceforge.net/projects/gullchess/", "Gull 3 w32 XP.exe", 3125)
    # cm.set_multipv(10, 64) Da problemas

    mas("irina", "Lucas Monge", "0.18", "https://github.com/lukasmonk/irina", "irina.exe", 1500)

    mas("rodentii", "Pawel Koziol", "0.9.64", "http://www.pkoziol.cal24.pl/rodent/rodent.htm", "RodentII_x32.exe", 2912,
        nodes_compatible=True)

    mas("amyan", "Antonio Dieguez R.", "1.62", "http://www.pincha.cl/amyan/amyane.html", "amyan.exe", 2545,
        emulate_movetime=True, nodes_compatible=True)

    cm = mas("hamsters", "Alessandro Scotti", "0.5", "https://walkofmind.com/programming/chess/hamsters.htm",
             "Hamsters.exe", 2487, nodes_compatible=True)
    cm.set_uci_option("OwnBook", "false")
    cm.remove_log("problem_log.txt")

    cm = mas(
        "toga",
        "WHMoweryJr,Thomas Gaksch,Fabien Letouzey",
        "deepTogaNPS 1.9.6",
        "http://www.computerchess.info/tdbb/phpBB3/viewtopic.php?f=9&t=357",
        "DeepToga1.9.6nps.exe",
        2843,
        emulate_movetime=True
    )
    cm.set_multipv(10, 40)

    mas("greko98", "Vladimir Medvedev", "9.8", "http://sourceforge.net/projects/greko", "GreKo98a.exe", 2500)

    mas("greko", "Vladimir Medvedev", "12.9", "http://sourceforge.net/projects/greko", "GreKo.exe", 2508)

    mas("delfi", "Fabio Cavicchio", "5.4", "http://www.msbsoftware.it/delfi/", "delfi.exe", 2686, emulate_movetime=True)

    mas("monarch", "Steve Maughan", "1.7", "http://www.monarchchess.com/", "Monarch(v1.7).exe", 2100)

    mas("andscacs", "Daniel José Queraltó", "0.9432n", "http://www.amateurschach.de/main/_download.htm",
        "andscacs_32_no_popcnt.exe", 3264, nodes_compatible=True)

    mas(
        "arminius", "Volker Annus", "2017-01-01", "http://www.nnuss.de/Hermann/Arminius2017-01-01.zip",
        "Arminius2017-01-01-32Bit.exe", 2662, emulate_movetime=True, nodes_compatible=True
    )

    mas("wildcat", "Igor Korshunov", "8", "http://www.igorkorshunov.narod.ru/WildCat", "WildCat_8.exe", 2627,
        emulate_movetime=True)

    mas("demolito", "Lucas Braesch", "32bit", "https://github.com/lucasart/Demolito", "demolito_32bit_old.exe", 2627)

    cm = mas("zappa", "Anthony Cozzie", "1.1", "http://www.acoz.net/zappa/", "zappa.exe", 2581, nodes_compatible=True)
    cm.remove_log("zappa_log.txt")

    cm = mas("houdini", "Robert Houdart", "1.5a", "http://www.cruxis.com/chess/houdini.htm", "Houdini_15a_w32.exe",
             3093)
    cm.set_multipv(10, 16)

    cm = mas(
        "hannibal",
        "Samuel N. Hamilton and Edsel G. Apostol",
        "1.4b",
        "http://sites.google.com/site/edapostol/hannibal",
        "Hannibal1.4bx32.exe",
        3000,
    )
    cm.remove_log("logfile.txt")

    mas("paladin", "Ankan Banerjee", "0.1", "https://github.com/ankan-ban/chess_cpu", "Paladin_32bits_old.exe", 2254)

    mas("cdrill", "Ferdinand Mosca", "1800 Build 4", "https://sites.google.com/view/cdrill", "CDrill_1800_Build_4.exe",
        1800)

    mas(
        "gambitfruit",
        "Ryan Benitez, Thomas Gaksch and Fabien Letouzey",
        "Beta 4bx",
        "https://github.com/lazydroid/gambit-fruit",
        "gfruit.exe",
        2750,
        nodes_compatible=True
    )

    is64 = platform.machine().endswith("64")
    t32_64 = "64" if is64 else "32"
    is_bmi2 = FasterCode.bmi2() == 1 if is64 else False

    # 32 bits permanece Komodo 12 64 bit Komodo 13
    if is64:
        if is_bmi2:
            cm = mas(
                "komodo",
                "Don Dailey, Larry Kaufman, Mark Lefler, Dmitry Pervov, Dietrich Kappe",
                f"Dragon 1",
                "https://komodochess.com/",
                "dragon-64bit-avx2.exe",
                3529,
                nodes_compatible=True
            )
        else:
            cm = mas(
                "komodo",
                "Don Dailey, Larry Kaufman, Mark Lefler",
                f"13.02 64",
                "https://komodochess.com/",
                "komodo-13.02-64bit.exe",
                3406,
            )
    else:
        cm = mas(
            "komodo",
            "Don Dailey, Larry Kaufman, Mark Lefler",
            "12.1.1 32",
            "https://komodochess.com/",
            "komodo-12.1.1-32.exe",
            3300,
        )
    cm.set_uci_option("Hash", "64")
    cm.set_uci_option("Threads", "2" if is64 else "1")
    cm.set_multipv(10, 218)

    if is64:
        if is_bmi2:
            cm = mas("lc0", "The LCZero Authors", "v0.31.2", "https://github.com/LeelaChessZero", "lc0_dnnl.exe", 3300,
                     nodes_compatible=True)
        else:
            cm = mas("lc0", "The LCZero Authors", "v0.31.2", "https://github.com/LeelaChessZero", "lc0.exe", 3300,
                     nodes_compatible=True)
        cm.set_uci_option("Threads", "2")
        cm.set_multipv(10, 500)

    cm = mas(
        "stockfish",
        " T. Romstad, M. Costalba, J. Kiiski, G. Linscott",
        f"17 {t32_64}",
        "https://stockfishchess.org/",
        f"Stockfish-17-{t32_64}.exe",
        3611,
        nodes_compatible=True
    )
    cm.set_uci_option("Ponder", "false")
    cm.set_uci_option("Threads", "2" if is64 else "1")
    cm.set_uci_option("Hash", "64")
    cm.set_multipv(10, 256)

    for level in range(1100, 2000, 100):
        cm = mas(
            "maia-%d" % level,
            "Reid McIlroy-Young,Ashton Anderson,Siddhartha Sen,Jon Kleinberg,Russell Wang + LcZero team",
            "%d" % level,
            "https://maiachess.com/",
            "lc0.exe",
            level,
            folder="maia",
            nodes_compatible=True
        )
        cm.set_uci_option("WeightsFile", "maia-%d.pb.gz" % level)
        cm.path_exe = Util.opj(folder_engines, "maia", "lc0.exe")
        cm.name = "Maia-%d" % level

    return dic_engines


def dict_engines_fixed_elo(folder_engines):
    d = read_engines(folder_engines)
    dic = {}
    for nm, xfrom, xto in (
            ("amyan", 1000, 2400),
            ("stockfish", 1400, 2800),
            ("rhetoric", 1300, 2600),
            ("cheng", 800, 2500),
            ("greko", 1600, 2400),
            ("hamsters", 1000, 2000),
            ("rybka", 1200, 2400),
            ("ufim", 700, 2000),
            ("delfi", 1000, 1000),
    ):
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
