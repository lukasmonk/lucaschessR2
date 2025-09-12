import datetime
import random

from PySide2 import QtCore

import Code
import Code.SQL.Base as SQLBase
from Code import Util
from Code.Engines import STS
from Code.QT import QTUtil2
from Code.SQL import UtilSQL
from Code.Translations import TrListas


class RegWorkMap:
    iso: str
    name: str
    border: str
    elo: int
    assoc: list

    donePV: str

    def __str__(self):
        s = ""
        for x in dir(self):
            if not x.startswith("_"):
                v = getattr(self, x)
                s += "[%s:%s]" % (x, str(v))
        return s

    def _save(self):
        dic = {}
        for x in dir(self):
            if not x.startswith("_"):
                v = getattr(self, x)
                dic[x] = v
        return dic

    def _restore(self, dic):
        for k, v in dic.items():
            setattr(self, k, v)


def ld_countries(mapa):
    dic_filtros = {
        "Africa": [
            "gw",
            "zm",
            "ci",
            "eh",
            "cm",
            "eg",
            "cg",
            "za",
            "ao",
            "cd",
            "ga",
            "gn",
            "et",
            "gm",
            "zw",
            "cv",
            "gh",
            "rw",
            "tz",
            "gq",
            "na",
            "ne",
            "ng",
            "tn",
            "re",
            "lr",
            "ls",
            "tg",
            "td",
            "er",
            "ly",
            "bf",
            "dj",
            "sl",
            "bi",
            "bj",
            "cf",
            "bw",
            "dz",
            "yt",
            "sz",
            "mg",
            "ma",
            "ke",
            "ss",
            "ml",
            "km",
            "st",
            "mu",
            "mw",
            "sh",
            "so",
            "sn",
            "mr",
            "sc",
            "ug",
            "mz",
            "sd",
        ],
        "WorldMap": None,
    }
    filtro = dic_filtros[mapa]
    lista = []
    for iso, name, border, elo, assoc in (
            ("ad", _("Andorra"), ["fr", "es"], 2252, []),
            ("ae", _("United Arab Emirates"), ["qa", "om", "sa"], 2292, []),
            ("af", _("Afghanistan"), ["cn", "uz", "ir", "tm", "tj", "pk"], 1975, []),
            ("al", _("Albania"), ["me", "gr", "mk", "rs"], 2336, []),
            ("am", _("Armenia"), ["tr", "ge", "az", "ir"], 2655, []),
            ("ao", _("Angola"), ["zm", "na", "cg", "cd"], 2214, []),
            ("ar", _("Argentina"), ["py", "bo", "uy", "br", "cl"], 2540, []),
            ("at", _("Austria"), ["ch", "de", "it", "li", "sk", "cz", "si", "hu"], 2490, []),
            ("au", _("Australia"), ["ki", "nz", "vu", "fj", "id", "pg"], 2451, ["cc", "cx", "hm"]),
            ("az", _("Azerbaijan"), ["ru", "tr", "ir", "am", "ge", "az"], 2629, []),
            ("ba", _("Bosnia and Herzegovina"), ["hr", "me", "rs"], 2511, []),
            ("bd", _("Bangladesh"), ["mm", "in"], 2397, []),
            ("be", _("Belgium"), ["lu", "fr", "de", "nl"], 2501, []),
            ("bf", _("Burkina Faso"), ["ci", "ml", "ne", "bj", "tg", "gh"], 1500, []),
            ("bg", _("Bulgaria"), ["ro", "tr", "gr", "mk", "rs"], 2605, []),
            ("bh", _("Bahrain"), ["sa"], 1935, []),
            ("bi", _("Burundi"), ["rw", "tz", "cd"], 1758, []),
            ("bj", _("Benin"), ["tg", "bf", "ne", "ng"], 1500, []),
            ("bn", _("Brunei Darussalam"), ["my"], 1961, []),
            ("bo", _("Bolivia"), ["py", "ar", "pe", "br", "cl"], 2245, []),
            ("br", _("Brazil"), ["py", "co", "ve", "sr", "bo", "gy", "gf", "ar", "pe", "uy"], 2519, []),
            ("bs", _("Bahamas"), ["us", "cu"], 1746, []),
            ("bt", _("Bhutan"), ["cn", "in"], 1686, []),
            ("bw", _("Botswana"), ["na", "zw", "za", "zm"], 2141, []),
            ("by", _("Belarus"), ["lv", "ru", "lt", "ua", "pl"], 2571, []),
            ("bz", _("Belize"), ["gt", "mx"], 1500, []),
            ("ca", _("Canada"), ["dk", "us"], 2499, []),
            (
                    "cd",
                    _("Congo, the Democratic Republic of the"),
                    ["zm", "rw", "tz", "ss", "cg", "bi", "ao", "cf", "ug"],
                    1500,
                    [],
            ),
            ("cf", _("Central African Republic"), ["cm", "ss", "cg", "cd", "td", "sd"], 1500, []),
            ("cg", _("Congo"), ["ga", "cd", "cm", "ao", "cf"], 1500, []),
            ("ch", _("Switzerland"), ["fr", "de", "it", "li", "at"], 2504, []),
            ("ci", _("Ivory Coast"), ["gn", "bf", "lr", "ml", "gh"], 1500, []),
            ("cl", _("Chile"), ["ar", "ws", "bo", "pe"], 2447, []),
            ("cm", _("Cameroon"), ["gq", "cg", "cf", "ng", "ga", "td"], 1989, []),
            (
                    "cn",
                    _("China"),
                    ["ru", "mn", "kg", "af", "mm", "la", "jp", "vn", "bt", "kp", "tj", "in", "np", "kz", "ph", "pk"],
                    2688,
                    ["tw", "hk", "mo"],
            ),
            ("co", _("Colombia"), ["ve", "pa", "ec", "br", "pe"], 2440, []),
            ("cr", _("Costa Rica"), ["ni", "pa"], 2305, []),
            ("cu", _("Cuba"), ["jm", "mx", "ht", "bs"], 2589, []),
            ("cv", _("Cabo Verde"), ["mr"], 1500, []),
            ("cy", _("Cyprus"), ["lb", "sy", "tr", "gb"], 2116, []),
            ("cz", _("Czech Republic"), ["sk", "de", "at", "pl"], 2582, []),
            ("de", _("Germany"), ["be", "fr", "ch", "nl", "dk", "cz", "lu", "at", "pl"], 2630, []),
            ("dj", _("Djibouti"), ["et", "so", "er"], 1500, []),
            ("dk", _("Denmark"), ["ca", "de", "is"], 2541, ["gl", "fo"]),
            ("dm", _("Dominica"), ["ht"], 1500, []),
            ("do", _("Dominican Republic"), ["ht"], 2315, []),
            ("dz", _("Algeria"), ["ma", "eh", "ml", "ne", "tn", "mr", "ly"], 2320, []),
            ("ec", _("Ecuador"), ["co", "pe"], 2326, []),
            ("ee", _("Estonia"), ["lv", "ru"], 2455, []),
            ("eg", _("Egypt"), ["ps", "sd", "il", "ly"], 2466, []),
            ("eh", _("Western Sahara"), ["ma", "dz", "mr"], 1500, []),
            ("er", _("Eritrea"), ["et", "dj", "sd"], 1500, []),
            ("es", _("Spain"), ["fr", "ma", "ad", "pt"], 2592, []),
            ("et", _("Ethiopia"), ["dj", "ke", "ss", "so", "er", "sd"], 1808, []),
            ("fi", _("Finland"), ["ru", "se", "no"], 2444, ["ax"]),
            ("fj", _("Fiji"), ["nz", "au", "vu"], 1855, []),
            ("fm", _("Micronesia, Federated States of"), ["pg", "mh"], 1500, []),
            (
                    "fr",
                    _("France"),
                    ["be", "ch", "nl", "ad", "mc", "de", "it", "lu", "es"],
                    2661,
                    ["gp", "nc", "re", "pf", "tf", "pm", "wf", "mf", "fx", "yt", "mq"],
            ),
            ("ga", _("Gabon"), ["cg", "gq", "cm", "st"], 1500, []),
            (
                    "gb",
                    _("United Kingdom"),
                    ["ie", "fr"],
                    2622,
                    [
                        "ck",
                        "vc",
                        "gs",
                        "ag",
                        "gg",
                        "im",
                        "io",
                        "gi",
                        "lc",
                        "tv",
                        "nf",
                        "sh",
                        "pn",
                        "vg",
                        "bb",
                        "bl",
                        "bm",
                        "je",
                        "fk",
                        "kn",
                        "tc",
                        "ai",
                        "gd",
                        "ms",
                        "sb",
                        "ky",
                    ],
            ),
            ("ge", _("Georgia"), ["ru", "az", "am", "tr"], 2590, []),
            ("gf", _("French Guiana"), ["sr", "lu", "br", "mc"], 1500, []),
            ("gh", _("Ghana"), ["tg", "bf", "ci"], 1855, []),
            ("gm", _("Gambia"), ["sn"], 1917, []),
            ("gn", _("Guinea"), ["gw", "ci", "ml", "lr", "sn", "sl"], 1500, []),
            ("gq", _("Equatorial Guinea"), ["ga", "cm"], 1500, []),
            ("gr", _("Greece"), ["bg", "tr", "al", "mk"], 2552, []),
            ("gt", _("Guatemala"), ["hn", "sv", "bz", "mx"], 2219, []),
            ("gw", _("Guinea-Bissau"), ["gn", "sn"], 1500, []),
            ("gy", _("Guyana"), ["sr", "ve", "br"], 1831, []),
            ("hn", _("Honduras"), ["ni", "gt", "sv"], 2175, []),
            ("hr", _("Croatia"), ["me", "si", "rs", "ba", "hu"], 2583, []),
            ("ht", _("Haiti"), ["do", "dm", "cu"], 1959, []),
            ("hu", _("Hungary"), ["rs", "hr", "sk", "si", "at", "ro", "ua"], 2655, []),
            ("id", _("Indonesia"), ["au", "tl", "my", "pg"], 2414, []),
            ("ie", _("Ireland"), ["is", "gb"], 2390, []),
            ("il", _("Israel"), ["ps", "eg", "jo", "lb", "sy"], 1513, []),
            ("in", _("India"), ["bd", "cn", "mm", "lk", "bt", "mv", "np", "pk"], 2660, []),
            ("iq", _("Iraq"), ["sy", "ir", "tr", "jo", "kw", "sa"], 2304, []),
            ("ir", _("Iran, Islamic Republic of"), ["af", "iq", "tr", "am", "tm", "pk", "az"], 2482, []),
            ("is", _("Iceland"), ["ie", "dk"], 2514, []),
            ("it", _("Italy"), ["va", "fr", "ch", "mt", "si", "at", "sm"], 2551, []),
            ("jm", _("Jamaica"), ["cu"], 2153, []),
            ("jo", _("Jordan"), ["iq", "sy", "sa", "il", "ps"], 2197, []),
            ("jp", _("Japan"), ["kr", "cn"], 2251, []),
            ("ke", _("Kenya"), ["ss", "et", "ug", "so", "tz"], 2061, []),
            ("kg", _("Kyrgyzstan"), ["kz", "tj", "cn", "uz"], 2265, []),
            ("kh", _("Cambodia"), ["vn", "th", "la"], 1500, []),
            ("ki", _("Kiribati"), ["nz", "au", "vu"], 1500, []),
            ("km", _("Comoros"), ["mg", "mz"], 1500, []),
            ("kp", _("Korea, Democratic People's Republic of"), ["kr", "cn", "ru"], 1500, []),
            ("kr", _("Korea, Republic of"), ["kp", "jp"], 2050, []),
            ("kw", _("Kuwait"), ["iq", "sa"], 1943, []),
            ("kz", _("Kazakhstan"), ["ru", "tm", "kg", "cn", "uz"], 2492, []),
            ("la", _("Lao People's Democratic Republic"), ["mm", "kh", "cn", "th", "vn"], 1500, []),
            ("lb", _("Lebanon"), ["sy", "cy", "il"], 2192, []),
            ("li", _("Liechtenstein"), ["ch", "at"], 2041, []),
            ("lk", _("Sri Lanka"), ["in"], 2137, []),
            ("lr", _("Liberia"), ["gn", "ci", "sl"], 1500, []),
            ("ls", _("Lesotho"), ["za"], 1583, []),
            ("lt", _("Lithuania"), ["lv", "ru", "by", "pl"], 2477, []),
            ("lu", _("Luxembourg"), ["be", "fr", "de", "gf"], 2323, []),
            ("lv", _("Latvia"), ["ee", "ru", "lt", "by"], 2525, []),
            ("ly", _("Libya"), ["eg", "ne", "tn", "dz", "td", "sd"], 2191, []),
            ("ma", _("Morocco"), ["dz", "eh", "es"], 2322, []),
            ("mc", _("Monaco"), ["gf", "fr"], 2310, []),
            ("md", _("Moldova, Republic of"), ["to", "ro", "ua"], 2462, []),
            ("me", _("Montenegro"), ["hr", "rs", "al", "ba"], 2447, []),
            ("mg", _("Madagascar"), ["mu", "sc", "km", "mz"], 2058, []),
            ("mh", _("Marshall Islands"), ["fm"], 1500, []),
            ("mk", _("Macedonia"), ["rs", "bg", "al", "gr"], 2455, []),
            ("ml", _("Mali"), ["bf", "ci", "ne", "dz", "sn", "mr", "gn"], 2139, []),
            ("mm", _("Myanmar"), ["bd", "la", "cn", "th", "in"], 1954, []),
            ("mn", _("Mongolia"), ["ru", "cn"], 2417, []),
            ("mr", _("Mauritania"), ["ml", "dz", "sn", "cv", "eh"], 1946, []),
            ("mt", _("Malta"), ["tn", "it"], 2095, []),
            ("mu", _("Mauritius"), ["mg"], 1891, []),
            ("mv", _("Maldives"), ["in"], 1650, []),
            ("mw", _("Malawi"), ["zm", "tz", "mz"], 1784, []),
            ("mx", _("Mexico"), ["cu", "gt", "us", "bz"], 2435, []),
            ("my", _("Malaysia"), ["bn", "ph", "sg", "id", "th"], 2283, []),
            ("mz", _("Mozambique"), ["sz", "mg", "tz", "zm", "za", "km", "mw", "zw"], 1858, []),
            ("na", _("Namibia"), ["zm", "bw", "za", "ao"], 1886, []),
            ("ne", _("Niger"), ["bf", "ml", "bj", "ng", "dz", "td", "ly"], 1500, []),
            ("ng", _("Nigeria"), ["td", "cm", "bj", "ne"], 2224, []),
            ("ni", _("Nicaragua"), ["cr", "hn"], 2233, []),
            ("nl", _("Netherlands"), ["be", "fr", "de"], 2642, ["aw", "cw", "bq", "sx"]),
            ("no", _("Norway"), ["fi", "se", "ru"], 2559, ["bv", "sj"]),
            ("np", _("Nepal"), ["cn", "in"], 2070, []),
            ("nr", _("Nauru"), ["pg"], 1500, []),
            ("nz", _("New Zealand"), ["ws", "fj", "au", "ki"], 2296, ["tk", "nu"]),
            ("om", _("Oman"), ["ye", "sa", "ae"], 2062, []),
            ("pa", _("Panama"), ["cr", "co"], 2160, []),
            ("pe", _("Peru"), ["bo", "co", "ec", "br", "cl"], 2520, []),
            ("pg", _("Papua New Guinea"), ["nr", "au", "id", "fm"], 1966, []),
            ("ph", _("Philippines"), ["my", "cn", "vn", "pw"], 2529, []),
            ("pk", _("Pakistan"), ["in", "ir", "cn", "af"], 1931, []),
            ("pl", _("Poland"), ["de", "sk", "cz", "lt", "ua", "by"], 2636, []),
            ("ps", _("Palestine, State of"), ["eg", "jo", "il"], 2798, []),
            ("pt", _("Portugal"), ["es"], 2393, []),
            ("pw", _("Palau"), ["ph"], 1761, []),
            ("py", _("Paraguay"), ["ar", "br", "bo"], 2367, []),
            ("qa", _("Qatar"), ["sa", "ae"], 2118, []),
            ("ro", _("Romania"), ["md", "bg", "ua", "rs", "hu"], 2562, []),
            ("rs", _("Serbia"), ["me", "bg", "ba", "rs", "hr", "al", "mk", "hu", "ro"], 2572, []),
            (
                    "ru",
                    _("Russian Federation"),
                    ["cn", "no", "ee", "mn", "lt", "us", "lv", "ge", "kp", "kz", "fi", "az", "ua", "by", "pl"],
                    2740,
                    [],
            ),
            ("rw", _("Rwanda"), ["ug", "tz", "bi", "cd"], 1723, []),
            ("sa", _("Saudi Arabia"), ["om", "ae", "iq", "bh", "ye", "qa", "jo", "kw"], 1952, []),
            ("sc", _("Seychelles"), ["mg", "so"], 1725, []),
            ("sd", _("Sudan"), ["ss", "eg", "cf", "et", "td", "er", "ly"], 2112, []),
            ("se", _("Sweden"), ["fi", "no"], 2537, []),
            ("sg", _("Singapore"), ["my"], 2375, []),
            ("si", _("Slovenia"), ["hr", "hu", "at", "it"], 2540, []),
            ("sk", _("Slovakia"), ["cz", "ua", "at", "pl", "hu"], 2498, []),
            ("sl", _("Sierra Leone"), ["gn", "lr"], 1500, []),
            ("sm", _("San Marino"), ["it"], 2000, []),
            ("sn", _("Senegal"), ["gw", "gn", "gm", "mr", "ml"], 1705, []),
            ("so", _("Somalia"), ["sc", "et", "dj", "so", "ke"], 1500, []),
            ("sr", _("Suriname"), ["gf", "gy", "br"], 2026, []),
            ("ss", _("South Sudan"), ["ke", "cf", "cd", "et", "ug", "sd"], 1500, []),
            ("st", _("Sao Tome and Principe"), ["ga"], 1781, []),
            ("sv", _("El Salvador"), ["gt", "hn"], 2200, []),
            ("sy", _("Syrian Arab Republic"), ["lb", "iq", "tr", "cy", "jo", "il"], 2267, []),
            ("sz", _("Swaziland"), ["za", "mz"], 1500, []),
            ("td", _("Chad"), ["cm", "ne", "ng", "cf", "ly", "sd"], 1500, []),
            ("tg", _("Togo"), ["bf", "bj", "gh"], 1771, []),
            ("th", _("Thailand"), ["mm", "kh", "my", "la"], 2190, []),
            ("tj", _("Tajikistan"), ["uz", "kg", "cn", "af"], 2304, []),
            ("tl", _("Timor-Leste"), ["id"], 1500, []),
            ("tm", _("Turkmenistan"), ["kz", "ir", "uz", "af"], 2390, []),
            ("tn", _("Tunisia"), ["mt", "dz", "ly"], 2297, []),
            ("to", _("Tonga"), ["md", "ua"], 1500, []),
            ("tr", _("Turkey"), ["sy", "bg", "gr", "iq", "ir", "am", "cy", "ge", "az"], 2544, []),
            ("tt", _("Trinidad and Tobago"), ["ve"], 2128, []),
            ("tz", _("Tanzania, United Republic of"), ["zm", "rw", "ke", "bi", "cd", "mw", "ug", "mz"], 1751, []),
            ("ua", _("Ukraine"), ["ru", "md", "hu", "sk", "to", "ro", "by", "pl"], 2690, []),
            ("ug", _("Uganda"), ["ss", "rw", "tz", "ke", "cd"], 2212, []),
            ("us", _("United States"), ["ru", "ca", "mx", "bs"], 2641, ["gu", "vi", "as", "pr", "um", "mp"]),
            ("uy", _("Uruguay"), ["ar", "br"], 2312, []),
            ("uz", _("Uzbekistan"), ["tj", "kz", "tm", "kg", "af"], 2512, []),
            ("va", _("Holy See (Vatican City State)"), ["it"], 1500, []),
            ("ve", _("Venezuela"), ["tt", "co", "gy", "br"], 2413, []),
            ("vn", _("Viet Nam"), ["ph", "kh", "cn", "la"], 2504, []),
            ("vu", _("Vanuatu"), ["fj", "au", "ki"], 1500, []),
            ("ws", _("Samoa"), ["nz", "cl"], 1500, []),
            ("ye", _("Yemen"), ["om", "sa"], 2217, []),
            ("za", _("South Africa"), ["sz", "na", "bw", "ls", "zw", "mz"], 2312, []),
            ("zm", _("Zambia"), ["tz", "na", "ao", "cd", "mw", "bw", "zw", "mz"], 2234, []),
            ("zw", _("Zimbabwe"), ["zm", "bw", "za", "mz"], 2186, []),
    ):

        if filtro:
            if iso not in filtro:
                continue
            border = [biso for biso in border if biso in filtro]
            assoc = [biso for biso in assoc if biso in filtro]
        alm = RegWorkMap()
        alm.iso = iso
        alm.name = name
        alm.border = border
        alm.elo = elo
        alm.assoc = assoc

        lista.append(alm)

    dic = {alm.iso: alm for alm in lista}
    return dic


class DBWorkMap(SQLBase.DBBase):
    def __init__(self, fichdb):
        self.trDic = {
            "mate": _("Mate"),
            "sts": _("STS"),
            "basic": _("Basic"),
            "easy": _("Easy"),
            "medium": _("Medium"),
            "hard": _("Hard"),
        }

        SQLBase.DBBase.__init__(self, fichdb)

        self.dicDB = UtilSQL.DictSQL(fichdb, tabla="CONFIG")
        self.tabla = "WORK"

        self.test_table()

        self.releer()

    def test_table(self):
        if not self.existeTabla(self.tabla):
            cursor = self.conexion.cursor()
            cursor.execute(
                "CREATE TABLE %s( ACTIVE INT, DCREATION TEXT, DEND TEXT, DONE TEXT, "
                "TIPO TEXT, MODEL TEXT, INFO TEXT, DATA BLOB);" % self.tabla
            )
            self.conexion.commit()
            cursor.close()

    def num_rows(self):
        return len(self.listaRaws)

    def dato(self, row, key):
        return self.listaRaws[row][key]

    def releer(self):
        cursor = self.conexion.cursor()
        cursor.execute(
            "SELECT ROWID, ACTIVE, DCREATION, DEND, DONE, TIPO, MODEL, INFO "
            "FROM %s ORDER BY -DCREATION;" % self.tabla
        )
        lista = cursor.fetchall()
        cursor.close()
        li = []
        for ROWID, ACTIVE, DCREATION, DEND, DONE, TIPO, MODEL, INFO in lista:
            d = {
                "ROWID": ROWID,
                "ACTIVE": "X" if ACTIVE else "",
                "DCREATION": DCREATION[: DCREATION.rindex(":")],
                "DEND": DEND[: DEND.rindex(":")] if DEND else "",
                "DONE": DONE,
                "TYPE": "%s - %s" % (self.trDic[TIPO], self.trDic.get(MODEL, MODEL)),
                "XTIPO": TIPO,
                "RESULT": INFO if INFO else "",
            }
            li.append(d)
        self.listaRaws = li

    def dataActivo(self):
        cursor = self.conexion.cursor()
        cursor.execute(
            "SELECT ROWID, DCREATION, DEND, DONE, TIPO, MODEL, INFO, DATA " "FROM %s WHERE ACTIVE=1;" % self.tabla
        )
        raw = cursor.fetchone()
        cursor.close()
        return raw

    def activaROWID(self, row):
        rowid = self.listaRaws[row]["ROWID"]
        cursor = self.conexion.cursor()
        cursor.execute("UPDATE %s SET ACTIVE=0" % self.tabla)
        self.conexion.commit()
        cursor.close()
        cursor = self.conexion.cursor()
        cursor.execute("UPDATE %s SET ACTIVE=1 WHERE ROWID=?" % self.tabla, (rowid,))
        self.conexion.commit()
        cursor.close()
        self.releer()

    def nuevo(self, w):
        cursor = self.conexion.cursor()
        cursor.execute("UPDATE %s SET ACTIVE=0" % self.tabla)
        self.conexion.commit()
        cursor.close()
        cursor = self.conexion.cursor()
        cursor.execute(
            "INSERT INTO %s (ACTIVE, DCREATION, DEND, DONE, TIPO, MODEL, DATA) VALUES(?,?,?,?,?,?,?);" % self.tabla,
            (1, str(w.dcreation), "", w.done, w.tipo, w.model, w.save()),
        )
        self.conexion.commit()
        cursor.close()
        self.releer()

    def borra(self, rowid):
        cursor = self.conexion.cursor()
        cursor.execute("DELETE FROM %s WHERE ROWID=?;" % self.tabla, (rowid,))
        self.conexion.commit()
        cursor.close()
        self.releer()

    def saveWork(self, workmap):
        rowid = [d["ROWID"] for d in self.listaRaws if d["ACTIVE"]][0]

        dend = workmap.endDate()
        done = "%d/%d" % workmap.get_done()
        info = workmap.get_info()
        data = workmap.save()

        cursor = self.conexion.cursor()
        cursor.execute(
            "UPDATE %s SET DEND=?, DONE=?, INFO=?, DATA=? WHERE ROWID=?;" % self.tabla, (dend, done, info, data, rowid)
        )
        self.conexion.commit()
        cursor.close()
        self.releer()

    def getTipo(self):
        for d in self.listaRaws:
            if d["ACTIVE"] == "X":
                return d["TYPE"]
        return ""


class WorkMap:
    def __init__(self, mapa):
        self.mapa = mapa

        self.svg, self.lineasSVG = self.leeSVG()

        self.db = DBWorkMap("%s/%s.db" % (Code.configuration.folder_results, mapa))

        self.current = None
        self.aim = None

        self.tipo = None
        self.model = None
        self.rowid = None
        self.dcreation = None
        self.dend = None
        self.info = None
        self.done = None

        self.dic = ld_countries(mapa)

        self.data_activo()

    def name_map(self):
        dic = TrListas.maps()
        return dic[self.mapa]

    def data_activo(self):
        raw = self.db.dataActivo()
        if raw:
            self.rowid, self.dcreation, self.dend, self.done, self.tipo, self.model, self.info, data = raw
            self.restore(data)
            self.reset_list_grid()
        else:
            self.nuevo()
            self.data_activo()
            return

    def nuevo(self, tipo="mate", model="basic"):
        self.tipo = tipo
        self.model = model
        self.current = None

        if tipo == "sts":
            random.seed(model)
            self.genSTS()
        else:
            self.genMate()
        self.dcreation = datetime.datetime.now()
        self.dend = ""
        self.info = ""
        self.done = "%d/%d" % self.get_done()
        self.db.nuevo(self)

    def leeSVG(self):
        svg = Code.path_resource("IntFiles", "Maps", "%s.svg" % self.mapa)
        f = open(svg)
        lineasSVG = []
        for nlinea, linea in enumerate(f):
            linea = linea.strip()
            if linea.startswith("."):
                if linea == ".DONE":
                    self.ln_done = nlinea, linea
                elif linea == ".CURRENT":
                    self.ln_current = nlinea, linea
                elif linea == ".BORDER":
                    self.ln_border = nlinea, linea
                elif linea == ".BORDERDONE":
                    self.ln_borderdone = nlinea, linea
            lineasSVG.append(linea)
        f.close()
        return svg, lineasSVG

    def save(self):
        dic_w = {}
        dic_w["CURRENT"] = self.current
        dic_w["DIC"] = {iso: reg._save() for iso, reg in self.dic.items()}
        return Util.var2zip(dic_w)

    def restore(self, xbin):
        dic_w = Util.zip2var(xbin)
        self.current = dic_w["CURRENT"]
        d = {}
        for iso, v in dic_w["DIC"].items():
            reg = RegWorkMap()
            reg._restore(v)
            d[iso] = reg
        self.dic = d

        self.reset_list_grid()

    def reset_list_grid(self):
        if self.current:
            li = [self.dic[iso] for iso in self.dic[self.current].border if iso in self.dic]
        else:
            li = [v for k, v in self.dic.items()]
        for alm in li:
            alm.name = _F(alm.name)
        self.listaGrid = sorted(li, key=lambda alm: alm.name)

    def set_widget(self, widget):
        self.widget = widget

    def reset_widget(self):
        lidone = []
        alm: RegWorkMap
        for iso, alm in self.dic.items():
            if alm.donePV:
                lidone.append(iso)
        if self.current:
            reg = self.dic[self.current]
            licurrent = [self.current]
            liborder = reg.border
            liborderdone = [iso for iso in liborder if iso in self.dic and self.dic[iso].donePV.strip()]
        else:
            licurrent = liborder = liborderdone = []

        def modif(x, lista):
            for xiso in lista:
                if xiso in self.dic:
                    lista.extend(self.dic[xiso].assoc)
            line, default = x
            self.lineasSVG[line] = "." + ",.".join(lista) if lista else default

        modif(self.ln_done, lidone)
        modif(self.ln_current, licurrent)
        modif(self.ln_border, liborder)
        modif(self.ln_borderdone, liborderdone)
        x = "\n".join(self.lineasSVG)
        self.widget.load(QtCore.QByteArray(bytes(x, "utf-8")))

        self.reset_list_grid()

    def num_rows(self):
        return len(self.listaGrid)

    def dato(self, row, column):
        if column == "TYPE":
            return "5" if self.listaGrid[row].donePV else "1"  # 5 = Azul 1 = Gris
        else:
            return self.listaGrid[row].name

    def set_aim_row(self, row):
        self.aim = self.listaGrid[row].iso
        si_hecho = self.iso_done(self.aim)
        if si_hecho:
            self.current = self.aim
        self.db.saveWork(self)
        return si_hecho

    def get_aim(self):
        return self.dic[self.aim] if self.aim else None

    def iso_done(self, iso):
        return len(self.dic[iso].donePV) > 0

    def fenAim(self):
        return self.dic[self.aim].fen

    def name_aim(self):
        return self.dic[self.aim].name

    def win_aim(self, window, pv):
        reg = self.dic[self.aim]
        reg.donePV = pv
        self.current = self.aim
        si_end = False
        if not self.dend:
            si_end = True
            for iso, reg in self.dic.items():
                if not reg.donePV:
                    si_end = False
                    break
            if si_end:
                self.dend = datetime.datetime.now()
        self.info = self.calcINFO()
        self.db.saveWork(self)
        if si_end:
            mensaje = _("Congratulations, goal achieved") + "<br><br>" + _("Finished") + ": " + self.name_map()
            QTUtil2.message_result_win(window, mensaje)
        return si_end

    def calcINFO(self):
        info = ""
        if self.tipo == "sts":
            sump = sumt = 0
            for iso, alm in self.dic.items():
                if alm.donePV:
                    sump += alm.puntos
                    sumt += alm.total
            porc = sump * 100.0 / sumt if sumt else 0.0
            info = "%d/%d (%0.02f%%)" % (sump, sumt, porc)
        elif self.tipo == "mate":
            sum_m = sum_u = 0
            for iso, alm in self.dic.items():
                if alm.donePV:
                    sum_u += len(alm.donePV.split(" ")) // 2 + 1
                    sum_m += alm.mate
            porc = sum_m * 100.0 / sum_u if sum_u else 0.0
            info = "%d/%d (%0.02f%%)" % (sum_u, sum_m, porc)
        return info

    def nameCurrent(self):
        return self.dic[self.current].name if self.current else ""

    def total(self):
        return len(self.dic)

    def get_done(self):
        h = 0
        t = 0
        for k, v in self.dic.items():
            if v.donePV:
                h += 1
            t += 1
        return h, t

    def is_terminated(self):
        h, t = self.get_done()
        return h == t

    def get_info(self):
        return self.info

    def get_tipo(self):
        return self.tipo

    def creationDate(self):
        c = str(self.dcreation)
        return c[: c.rindex(":")]

    def endDate(self):
        return str(self.dend) if self.dend else ""

    def activaRowID(self, row):
        self.db.activaROWID(row)
        self.data_activo()

    def genSTS(self):
        groups = STS.Groups()

        st = set()
        ngroup = 0
        ngroups = len(groups)
        liGroups = groups.lista
        random.shuffle(liGroups)
        for iso, alm in self.dic.items():
            g = liGroups[ngroup]
            pos = random.randint(0, 99)
            while (ngroup, pos) in st:
                pos = random.randint(0, 99)
            st.add((ngroup, pos))

            elem = g.element(pos)
            alm.fen = elem.fen
            alm.dicResults = elem.dic_results
            alm.donePV = ""
            alm.strGroup = g.name

            ngroup += 1
            if ngroup == ngroups:
                ngroup = 0

    def genMate(self):
        dicMates = {}
        for mate in range(1, 8):
            fich = Code.path_resource("Trainings", "Checkmates in GM games", "Mate in %d.fns" % mate)
            with open(fich) as f:
                li = []
                for linea in f:
                    linea = linea.strip()
                    if linea:
                        li1 = linea.split("|")
                        fen = li1[0]
                        pgn = li1[3]
                        li1 = pgn.split("[")[:-1]
                        dic = {}
                        for x in li1:
                            if '"' in x:
                                r = x.split('"')[1].replace(".?", "").replace("?", "")
                                if r:
                                    k = x.split('"')[0].strip()
                                    dic[k] = r
                        g = dic.get
                        txt = "<b>%s-%s</b><br>" % (g("White", ""), g("Black", ""))
                        txt += ("%s/%s/%s" % (g("Event", ""), g("Site", ""), g("Date", ""))).strip("/")
                        li.append("%s|%s" % (fen, txt))
            dicMates[mate] = li
        if self.model == "basic":
            prob7 = {
                15: (70, 20, 10, 0, 0, 0, 0),
                16: (50, 30, 20, 0, 0, 0, 0),
                17: (30, 30, 20, 20, 0, 0, 0),
                18: (10, 20, 40, 20, 10, 0, 0),
                19: (0, 10, 40, 30, 10, 10, 0),
                20: (0, 10, 30, 30, 20, 10, 0),
                21: (0, 0, 10, 20, 30, 30, 10),
                22: (0, 0, 0, 20, 30, 30, 20),
                23: (0, 0, 0, 10, 20, 40, 30),
                24: (0, 0, 0, 10, 10, 40, 40),
                25: (0, 0, 0, 0, 10, 40, 50),
                26: (0, 0, 0, 0, 10, 30, 60),
                27: (0, 0, 0, 0, 0, 30, 70),
            }

            def levelElo(elo):
                elo //= 100
                li = []
                for n, x in enumerate(prob7[elo]):
                    if x:
                        li.extend([n + 1] * x)
                return random.choice(li)

            for iso, alm in self.dic.items():
                mate = levelElo(alm.elo)
                alm.fen = random.choice(dicMates[mate])
                alm.donePV = ""
                alm.mate = mate
        else:

            def sel(from_sq, to_sq):
                st = set()
                for iso, alm in self.dic.items():
                    mate = random.randint(from_sq, to_sq)
                    li = dicMates[mate]
                    fen = random.choice(li)
                    while fen in st:
                        fen = random.choice(li)
                    alm.fen = fen
                    alm.donePV = ""
                    alm.mate = mate
                    st.add(fen)

            d = {"easy": (1, 2), "medium": (2, 5), "hard": (4, 7)}
            from_sq, to_sq = d[self.model]
            sel(from_sq, to_sq)
