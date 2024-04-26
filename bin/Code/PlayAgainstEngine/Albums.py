import atexit
import collections
import os
import random

import Code
from Code.Base.Constantes import BOOK_RANDOM_UNIFORM
from Code.Books import Books
from Code.Engines import EngineManager, EngineResponse
from Code.QT import Iconos
from Code.SQL import UtilSQL

ALBUMSHECHOS = "albumshechos"


class ManagerMotorAlbum:
    def __init__(self, manager, cromo):

        self.cromo = cromo

        self.manager = manager

        self.game = manager.game

        self.name = cromo.name

        self.xirina = None
        self.xsimilar = None

        conf_engine = self.manager.configuration.buscaRival("irina")
        self.xirina = EngineManager.EngineManager(conf_engine)
        self.xirina.options(None, 1, False)

        self.opening = self.cromo.opening
        if self.opening:
            bookdef = Code.tbookPTZ
            name = os.path.basename(bookdef)[:-4]
            self.book = Books.Book("P", name, bookdef, True)
            self.book.polyglot()

        # De compatibilidad
        self.mstime_engine = 0
        self.depth_engine = 0

        atexit.register(self.cerrar)

    def cerrar(self):
        if self.xirina:
            self.xirina.terminar()
            self.xirina = None
        if self.xsimilar:
            self.xsimilar.terminar()
            self.xsimilar = None

    def juega(self, fen):

        if self.opening:
            pv = self.book.eligeJugadaTipo(fen, BOOK_RANDOM_UNIFORM)
            if pv:
                self.opening -= 1
                rmrival = EngineResponse.EngineResponse("Opening", "w" in fen)
                rmrival.from_sq = pv[:2]
                rmrival.to_sq = pv[2:4]
                rmrival.promotion = pv[4:]
                return rmrival
            else:
                self.opening = 0

        total = self.cromo.aleatorio + self.cromo.captura + self.cromo.esquivo + self.cromo.similar + self.cromo.bien

        bola = random.randint(1, total)
        if bola <= self.cromo.aleatorio:
            return self.juega_aleatorio(fen)
        bola -= self.cromo.aleatorio
        if bola <= self.cromo.captura:
            return self.juega_captura(fen)
        bola -= self.cromo.captura
        if bola <= self.cromo.esquivo:
            return self.juega_esquivo(fen)
        bola -= self.cromo.esquivo
        if bola <= self.cromo.bien:
            return self.juega_irina(fen)
        else:
            return self.juega_similar(fen)

    def juega_aleatorio(self, fen):
        self.xirina.set_option("Personality", "Random")
        return self.run_irina(fen)

    def juega_esquivo(self, fen):
        self.xirina.set_option("Personality", "Advance")
        return self.run_irina(fen)

    def juega_captura(self, fen):
        self.xirina.set_option("Personality", "Capture")
        return self.run_irina(fen)

    def juega_irina(self, fen):
        self.xirina.set_option("Personality", "Irina")
        return self.run_irina(fen)

    def run_irina(self, fen):
        mrm = self.xirina.control(fen, 1)
        mrm.game = self.game
        return mrm.best_rm_ordered()

    def juega_similar(self, fen):
        if self.xsimilar is None:
            conf_engine = self.manager.configuration.buscaRival(self.cromo.engine)
            self.xsimilar = EngineManager.EngineManager(conf_engine)
            self.xsimilar.options(None, 5, True)
        mrm = self.xsimilar.control(fen, 5)
        mrm.game = self.game
        return mrm.bestmov_adjusted_similar(self.cromo.dif_puntos, self.cromo.mate, self.cromo.aterrizaje)


class Cromo:
    def __init__(
            self,
            key,
            name,
            nivel,
            bien,
            aleatorio,
            captura,
            esquivo,
            similar,
            dif_puntos,
            aterrizaje,
            mate,
            engine,
            opening,
    ):
        self.key = key
        self.name = name
        self.nivel = nivel
        self.hecho = False
        self.pos = None  # se inicializa al crear el album

        # Porcentaje para seleccionar movimiento
        self.bien = bien
        self.aleatorio = aleatorio
        self.captura = captura
        self.esquivo = esquivo
        self.similar = similar

        # Para seleccionar similar en mrm con un multiPV
        self.dif_puntos = dif_puntos
        self.aterrizaje = int(aterrizaje)
        self.mate = int(mate)

        dic = {"t": "fruit", "c": "critter", "k": "komodo", "s": "stockfish"}
        self.engine = dic.get(engine, None)

        self.opening = opening

    def icono(self):
        return Iconos.icono(self.key)

    def pixmap(self):
        return Iconos.pixmap(self.key)

    def pixmap_level(self):
        li = ("Amarillo", "Naranja", "Verde", "Azul", "Magenta", "Rojo")
        return Iconos.pixmap(li[self.nivel])


class Album:
    def __init__(self, clavedb, alias):
        self.claveDB = clavedb
        self.alias = alias
        self.liCromos = []
        self.hecho = False
        self.ficheroDB = Code.configuration.ficheroAlbumes

    def icono(self):
        return Iconos.icono(self.alias)

    def __len__(self):
        return len(self.liCromos)

    @property
    def name(self):
        for cromo in self.liCromos:
            if cromo.key == self.alias:
                return cromo.name
        return _F(self.alias)

    def get_cromo(self, pos):
        return self.liCromos[pos]

    def new_cromo(self, cromo):
        cromo.is_white = len(self.liCromos) % 2 == 0
        self.liCromos.append(cromo)

    def get_db(self, key):
        db = UtilSQL.DictSQL(self.ficheroDB)
        resp = db[key]
        db.close()
        return resp

    def put_db(self, key, value):
        db = UtilSQL.DictSQL(self.ficheroDB)
        db[key] = value
        db.close()

    def guarda(self):
        dic = collections.OrderedDict()
        for cromo in self.liCromos:
            dic[cromo.key] = cromo.hecho
        self.put_db(self.claveDB, dic)

    def test_finished(self):
        for cromo in self.liCromos:
            if not cromo.hecho:
                return False
        dic = self.get_db(ALBUMSHECHOS)
        if not dic:
            dic = {}
        dic[self.claveDB] = True
        self.put_db(ALBUMSHECHOS, dic)
        return True

    def reset(self):
        self.put_db(self.claveDB, None)


class Albums:
    def __init__(self, pre_clave):
        self.ficheroDB = Code.configuration.ficheroAlbumes
        self.preClave = pre_clave
        self.liGeneralCromos = self.read_csv()
        self.dicAlbumes = self.configura()

    def read_csv(self):
        return []

    def configura(self):
        return {}

    def create_album(self, alias):
        album = Album(self.preClave + "_" + alias, alias)

        for nivel, cuantos in enumerate(self.dicAlbumes[alias]):
            if cuantos:
                li = []
                for cromo in self.liGeneralCromos:
                    if cromo.nivel == nivel:
                        li.append(cromo)
                for pos, cromo in enumerate(random.sample(li, cuantos)):
                    cromo.pos = pos
                    cromo.is_white = pos % 2 == 0
                    cromo.hecho = False
                    album.new_cromo(cromo)
        album.guarda()
        return album

    def get_album(self, alias):
        key_db = self.preClave + "_" + alias
        dic = self.get_db(key_db)
        if dic:
            dig = {}
            for cromo in self.liGeneralCromos:
                dig[cromo.key] = cromo
            album = Album(key_db, alias)
            li = []
            pos = 0
            for k, v in dic.items():
                cromo = dig[k]
                cromo.hecho = v
                cromo.pos = pos
                cromo.is_white = pos % 2 == 0
                pos += 1
                li.append(cromo)
            album.liCromos = li
        else:
            album = self.create_album(alias)

        li = list(self.dicAlbumes.keys())
        for n, k in enumerate(li):
            if k == alias:
                album.siguiente = li[n + 1] if n + 1 < len(li) else None
                if album.siguiente:
                    dic_db = self.get_db(ALBUMSHECHOS)
                    if dic_db and dic_db.get(self.preClave + "_" + alias):
                        album.siguiente = None  # Para que no avise de que esta hecho
                break
        return album

    def reset(self, alias):
        self.create_album(alias)

    def get_db(self, key):
        db = UtilSQL.DictSQL(self.ficheroDB)
        resp = db[key]
        db.close()
        return resp

    def put_db(self, key, value):
        db = UtilSQL.DictSQL(self.ficheroDB)
        db[key] = value
        db.close()

    def list_menu(self):
        dic_db = self.get_db(ALBUMSHECHOS)
        if not dic_db:
            dic_db = {}
        dic = collections.OrderedDict()
        for uno in self.dicAlbumes:
            key = self.preClave + "_" + uno
            dic[uno] = dic_db.get(key, False)
        return dic


class AlbumAnimales(Albums):
    def __init__(self):
        Albums.__init__(self, "animales")

    def configura(self):
        dic = collections.OrderedDict()
        dic["Ant"] = (6, 0, 0, 0, 0, 0)  # 6
        dic["Bee"] = (5, 3, 0, 0, 0, 0)  # 8

        dic["Turtle"] = (4, 6, 0, 0, 0, 0)  # 10
        dic["Chicken"] = (3, 6, 3, 0, 0, 0)  # 12

        dic["Eagle"] = (3, 5, 6, 0, 0, 0)  # 14
        dic["Panda"] = (2, 4, 6, 4, 0, 0)  # 16

        dic["Hippo"] = (2, 5, 5, 6, 0, 0)  # 18
        dic["Rabbit"] = (1, 5, 5, 6, 3, 0)  # 20

        dic["Giraffe"] = (2, 5, 5, 6, 6, 0)  # 24
        dic["Shark"] = (1, 6, 6, 6, 6, 3)  # 28

        dic["Wolf"] = (2, 5, 6, 6, 6, 7)  # 32
        dic["Owl"] = (4, 6, 7, 7, 7, 9)  # 40
        return dic

    def read_csv(self):
        # x = """Animal;Nivel ;Bien;Aleatorio;Captura;Esquivo;Similar;Dif puntos;Aterrizaje;Mate;Engine;Opening
        # Ant;0;0;100;0;0;0;1000;450;0;t;0
        # Bee;0;1;95;0;0;0;1000;450;0;k;0
        # Butterfly;0;2;90;0;0;0;1000;450;0;c;0
        # Fish;0;3;85;0;0;0;1000;450;0;s;2
        # Bat;0;5;75;0;0;0;1000;450;0;k;2
        # Bird;0;6;70;0;0;0;1000;450;0;c;2
        # Turtle;1;7;65;100;0;0;1000;450;0;s;3
        # Crab;1;8;60;95;0;0;1000;350;0;t;3
        # Duck;1;9;55;90;0;0;900;350;0;k;3
        # Chicken;1;10;50;85;0;0;900;350;0;c;3
        # Alligator;1;11;45;80;0;50;900;350;0;s;4
        # Bull;1;12;40;75;0;48;900;350;0;t;4
        # Rooster;1;14;35;70;0;46;900;350;0;k;4
        # Eagle;2;15;30;65;100;50;900;350;0;c;4
        # Crocodile;2;16;25;60;95;59;900;350;0;s;5
        # Bear;2;17;20;55;90;60;800;350;0;t;5
        # Panda;2;18;15;50;85;65;800;350;0;k;5
        # Cow;2;20;10;45;80;69;800;350;1;c;5
        # Moose;2;25;5;40;75;64;700;250;1;s;5
        # Rhino;2;30;0;35;70;63;400;250;1;t;6
        # Hippo;3;35;0;30;65;62;400;250;1;k;6
        # Rabbit;3;40;0;25;60;50;400;250;1;c;6
        # Sheep;3;45;0;20;55;55;400;250;1;s;6
        # Donkey;3;50;0;15;50;47;400;250;1;t;6
        # Pig;3;50;0;10;45;46;400;150;1;k;7
        # Deer;3;55;0;5;40;45;400;150;1;c;7
        # Frog;3;57;0;0;35;41;400;150;1;t;7
        # Giraffe;4;60;0;0;30;36;400;150;1;k;7
        # Mouse;4;61;0;0;25;39;400;150;1;c;7
        # Penguin;4;62;0;0;20;37;400;150;1;s;7
        # Snake;4;64;0;0;15;36;400;150;1;t;8
        # Shark;4;66;0;0;10;35;400;150;1;c;8
        # Turkey;4;67;0;0;10;30;400;150;1;s;8
        # Monkey;4;68;0;0;10;28;400;150;1;t;8
        # Wolf;5;70;0;0;10;26;300;150;1;k;8
        # Fox;5;72;0;0;10;24;300;150;1;c;9
        # Cat;5;74;0;0;10;22;300;150;1;s;9
        # Dog;5;75;0;0;10;20;300;150;1;t;9
        # Tiger;5;77;0;0;10;18;300;150;1;k;9
        # Lion;5;80;0;0;10;16;300;150;1;c;9
        # Horse;5;82;0;0;10;14;300;150;2;s;9
        # Elephant;5;85;0;0;10;12;300;150;2;t;9
        # Gorilla;5;90;0;0;5;10;300;150;2;k;9
        # Owl;5;100;0;0;0;0;0;150;2;c;999"""
        # p rint "        li= []"
        # for n, linea in enumerate(x.split("\n")):
        # if n:
        # animal,nivel ,bien,aleatorio,captura,esquivo,similar,dif_puntos,aterrizaje,mate,engine,
        # opening=linea.strip().split(";")
        # p rint '        li.append(Cromo("%s",_("%s"),%s,%s,%s,%s,%s,%s,%s,%s,%s,"%s",%s))'
        # %(animal,animal,nivel,bien,aleatorio,captura,esquivo, similar,dif_puntos,aterrizaje,
        # mate,engine,opening)

        li = [
            Cromo("Ant", _("Ant"), 0, 0, 100, 0, 0, 0, 1000, 450, 0, "t", 0),
            Cromo("Bee", _("Bee"), 0, 1, 95, 0, 0, 0, 1000, 450, 0, "k", 0),
            Cromo("Butterfly", _("Butterfly"), 0, 2, 90, 0, 0, 0, 1000, 450, 0, "c", 0),
            Cromo("Fish", _("Fish"), 0, 3, 85, 0, 0, 0, 1000, 450, 0, "s", 2),
            Cromo("Bat", _("Bat"), 0, 5, 75, 0, 0, 0, 1000, 450, 0, "k", 2),
            Cromo("Bird", _("Bird"), 0, 6, 70, 0, 0, 0, 1000, 450, 0, "c", 2),
            Cromo("Turtle", _("Turtle"), 1, 7, 65, 100, 0, 0, 1000, 450, 0, "s", 3),
            Cromo("Crab", _("Crab"), 1, 8, 60, 95, 0, 0, 1000, 350, 0, "t", 3),
            Cromo("Duck", _("Duck"), 1, 9, 55, 90, 0, 0, 900, 350, 0, "k", 3),
            Cromo("Chicken", _("Chicken"), 1, 10, 50, 85, 0, 0, 900, 350, 0, "c", 3),
            Cromo("Alligator", _("Alligator"), 1, 11, 45, 80, 0, 50, 900, 350, 0, "s", 4),
            Cromo("Bull", _("Bull"), 1, 12, 40, 75, 0, 48, 900, 350, 0, "t", 4),
            Cromo("Rooster", _("Rooster"), 1, 14, 35, 70, 0, 46, 900, 350, 0, "k", 4),
            Cromo("Eagle", _("Eagle"), 2, 15, 30, 65, 100, 50, 900, 350, 0, "c", 4),
            Cromo("Crocodile", _("Crocodile"), 2, 16, 25, 60, 95, 59, 900, 350, 0, "s", 5),
            Cromo("Bear", _("Bear"), 2, 17, 20, 55, 90, 60, 800, 350, 0, "t", 5),
            Cromo("Panda", _("Panda"), 2, 18, 15, 50, 85, 65, 800, 350, 0, "k", 5),
            Cromo("Cow", _("Cow"), 2, 20, 10, 45, 80, 69, 800, 350, 1, "c", 5),
            Cromo("Moose", _("Moose"), 2, 25, 5, 40, 75, 64, 700, 250, 1, "s", 5),
            Cromo("Rhino", _("Rhino"), 2, 30, 0, 35, 70, 63, 400, 250, 1, "t", 6),
            Cromo("Hippo", _("Hippo"), 3, 35, 0, 30, 65, 62, 400, 250, 1, "k", 6),
            Cromo("Rabbit", _("Rabbit"), 3, 40, 0, 25, 60, 50, 400, 250, 1, "c", 6),
            Cromo("Sheep", _("Sheep"), 3, 45, 0, 20, 55, 55, 400, 250, 1, "s", 6),
            Cromo("Donkey", _("Donkey"), 3, 50, 0, 15, 50, 47, 400, 250, 1, "t", 6),
            Cromo("Pig", _("Pig"), 3, 50, 0, 10, 45, 46, 400, 150, 1, "k", 7),
            Cromo("Deer", _("Deer"), 3, 55, 0, 5, 40, 45, 400, 150, 1, "c", 7),
            Cromo("Frog", _("Frog"), 3, 57, 0, 0, 35, 41, 400, 150, 1, "t", 7),
            Cromo("Giraffe", _("Giraffe"), 4, 60, 0, 0, 30, 36, 400, 150, 1, "k", 7),
            Cromo("Mouse", _("Mouse"), 4, 61, 0, 0, 25, 39, 400, 150, 1, "c", 7),
            Cromo("Penguin", _("Penguin"), 4, 62, 0, 0, 20, 37, 400, 150, 1, "s", 7),
            Cromo("Snake", _("Snake"), 4, 64, 0, 0, 15, 36, 400, 150, 1, "t", 8),
            Cromo("Shark", _("Shark"), 4, 66, 0, 0, 10, 35, 400, 150, 1, "c", 8),
            Cromo("Turkey", _("Turkeycock"), 4, 67, 0, 0, 10, 30, 400, 150, 1, "s", 8),
            Cromo("Monkey", _("Monkey"), 4, 68, 0, 0, 10, 28, 400, 150, 1, "t", 8),
            Cromo("Wolf", _("Wolf"), 5, 70, 0, 0, 10, 26, 300, 150, 1, "k", 8),
            Cromo("Fox", _("Fox"), 5, 72, 0, 0, 10, 24, 300, 150, 1, "c", 9),
            Cromo("Cat", _("Cat"), 5, 74, 0, 0, 10, 22, 300, 150, 1, "s", 9),
            Cromo("Dog", _("Dog"), 5, 75, 0, 0, 10, 20, 300, 150, 1, "t", 9),
            Cromo("Tiger", _("Tiger"), 5, 77, 0, 0, 10, 18, 300, 150, 1, "k", 9),
            Cromo("Lion", _("Lion"), 5, 80, 0, 0, 10, 16, 300, 150, 1, "c", 9),
            Cromo("Horse", _("Horse"), 5, 82, 0, 0, 10, 14, 300, 150, 2, "s", 9),
            Cromo("Elephant", _("Elephant"), 5, 85, 0, 0, 10, 12, 300, 150, 2, "t", 9),
            Cromo("Gorilla", _("Gorilla"), 5, 90, 0, 0, 5, 10, 300, 150, 2, "k", 9),
            Cromo("Owl", _("Owl"), 5, 100, 0, 0, 0, 0, 0, 150, 2, "c", 999),
        ]
        return li


class AlbumVehicles(Albums):
    def __init__(self):
        Albums.__init__(self, "vehicles")

        # dic = { "animales_Ant":True, "animales_Bee":True, "animales_Turtle":True, "animales_Chicken":True,
        # "animales_Eagle":True, "animales_Panda":True,
        # "animales_Hippo":True, "animales_Rabbit":True, "animales_Giraffe":True, "animales_Shark":True,
        # "animales_Wolf":True }
        # self.putDB( ALBUMSHECHOS, dic )

    def configura(self):
        dic = collections.OrderedDict()
        dic["TouringMotorcycle"] = (4, 0, 0, 0, 0, 0)  # 4
        dic["Car"] = (3, 2, 2, 1, 0, 0)  # 8
        dic["QuadBike"] = (3, 3, 3, 3, 0, 0)  # 12
        dic["Truck"] = (4, 4, 3, 3, 2, 0)  # 16
        dic["DieselLocomotiveBoxcar"] = (4, 4, 4, 4, 4, 0)  # 20
        dic["SubwayTrain"] = (4, 5, 5, 4, 4, 2)  # 24
        dic["Airplane"] = (4, 5, 5, 5, 5, 4)  # 28
        return dic

    def read_csv(self):
        # x = """Vehicle;Nivel ;Bien;Aleatorio;Captura;Esquivo;Similar;Dif puntos;Aterrizaje;Mate;Engine;Opening
        # Wheel;0;0;100;0;0;0;1000;450;0;t;0
        # Wheelchair;0;1;95;0;0;0;1000;450;0;k;0
        # TouringMotorcycle;0;2;90;0;0;0;1000;450;0;c;0
        # Container;0;6;70;0;0;0;1000;450;0;c;2
        # BoatEquipment;1;8;60;95;0;0;1000;350;0;t;3
        # Car;1;9;55;90;0;0;900;350;0;k;3
        # Lorry;1;9;55;90;0;0;900;350;0;k;3
        # CarTrailer;1;10;50;85;0;0;900;350;0;c;3
        # TowTruck;1;14;35;70;0;46;900;350;0;k;4
        # QuadBike;2;15;30;65;100;50;900;350;0;c;4
        # RecoveryTruck;2;16;25;60;95;59;900;350;0;s;5
        # ContainerLoader;2;17;20;55;90;60;800;350;0;t;5
        # PoliceCar;2;18;15;50;85;65;800;350;0;k;5
        # ExecutiveCar;2;30;0;35;70;63;400;250;1;t;6
        # Truck;3;35;0;30;65;62;400;250;1;k;6
        # Excavator;3;40;0;25;60;50;400;250;1;c;6
        # Cabriolet;3;45;0;20;55;55;400;250;1;s;6
        # MixerTruck;3;50;0;15;50;47;400;250;1;t;6
        # ForkliftTruckLoaded;3;55;0;10;45;46;400;150;1;k;7
        # Ambulance;4;60;0;0;30;36;400;150;1;k;7
        # DieselLocomotiveBoxcar;4;65;0;0;30;36;400;150;1;k;7
        # TractorUnit;4;70;0;0;30;36;400;150;1;k;7
        # FireTruck;4;75;0;0;20;37;400;150;1;s;7
        # CargoShip;4;76;0;0;10;35;400;150;1;c;8
        # SubwayTrain;5;85;0;0;10;20;300;150;1;t;9
        # TruckMountedCrane;5;90;0;0;10;24;300;150;1;c;9
        # AirAmbulance;5;95;0;0;10;22;300;150;1;s;9
        # Airplane;5;99;0;0;10;26;300;150;1;k;999"""
        # p rint "        li= []"
        # for n, linea in enumerate(x.split("\n")):
        # if n:
        # animal,nivel ,bien,aleatorio,captura,esquivo,similar,dif_puntos,aterrizaje,mate,engine,
        # opening=linea.strip().split(";")
        # p rint '                    Cromo("%s",_("%s"),%s,%s,%s,%s,%s,%s,%s,%s,%s,"%s",%s))'
        # %(animal,animal,nivel,bien,aleatorio,captura,esquivo, similar,dif_puntos,aterrizaje,
        # mate,engine,opening)

        li = [
            Cromo("Wheel", _("Wheel"), 0, 0, 100, 0, 0, 0, 1000, 450, 0, "t", 0),
            Cromo("Wheelchair", _("Wheelchair"), 0, 1, 95, 0, 0, 0, 1000, 450, 0, "k", 0),
            Cromo("TouringMotorcycle", _("Touring Motorcycle"), 0, 2, 90, 0, 0, 0, 1000, 450, 0, "c", 0),
            Cromo("Container", _("Container"), 0, 6, 70, 0, 0, 0, 1000, 450, 0, "c", 2),
            Cromo("BoatEquipment", _("Boat Equipment"), 1, 8, 60, 95, 0, 0, 1000, 350, 0, "t", 3),
            Cromo("Car", _("Car"), 1, 9, 55, 90, 0, 0, 900, 350, 0, "k", 3),
            Cromo("Lorry", _("Lorry"), 1, 9, 55, 90, 0, 0, 900, 350, 0, "k", 3),
            Cromo("CarTrailer", _("Car Trailer"), 1, 10, 50, 85, 0, 0, 900, 350, 0, "c", 3),
            Cromo("TowTruck", _("Tow Truck"), 1, 14, 35, 70, 0, 46, 900, 350, 0, "k", 4),
            Cromo("QuadBike", _("Quad Bike"), 2, 15, 30, 65, 100, 50, 900, 350, 0, "c", 4),
            Cromo("RecoveryTruck", _("Recovery Truck"), 2, 16, 25, 60, 95, 59, 900, 350, 0, "s", 5),
            Cromo("ContainerLoader", _("Container Loader"), 2, 17, 20, 55, 90, 60, 800, 350, 0, "t", 5),
            Cromo("PoliceCar", _("Police Car"), 2, 18, 15, 50, 85, 65, 800, 350, 0, "k", 5),
            Cromo("ExecutiveCar", _("Executive Car"), 2, 30, 0, 35, 70, 63, 400, 250, 1, "t", 6),
            Cromo("Truck", _("Truck"), 3, 35, 0, 30, 65, 62, 400, 250, 1, "k", 6),
            Cromo("Excavator", _("Excavator"), 3, 40, 0, 25, 60, 50, 400, 250, 1, "c", 6),
            Cromo("Cabriolet", _("Cabriolet"), 3, 45, 0, 20, 55, 55, 400, 250, 1, "s", 6),
            Cromo("MixerTruck", _("Mixer Truck"), 3, 50, 0, 15, 50, 47, 400, 250, 1, "t", 6),
            Cromo("ForkliftTruckLoaded", _("Forklift Truck Loaded"), 3, 55, 0, 10, 45, 46, 400, 150, 1, "k", 7),
            Cromo("Ambulance", _("Ambulance"), 4, 60, 0, 0, 30, 36, 400, 150, 1, "k", 7),
            Cromo("DieselLocomotiveBoxcar", _("Diesel Locomotive Boxcar"), 4, 65, 0, 0, 30, 36, 400, 150, 1, "k", 7),
            Cromo("TractorUnit", _("Tractor Unit"), 4, 70, 0, 0, 30, 36, 400, 150, 1, "k", 7),
            Cromo("FireTruck", _("Fire Truck"), 4, 75, 0, 0, 20, 37, 400, 150, 1, "s", 7),
            Cromo("CargoShip", _("Cargo Ship"), 4, 76, 0, 0, 10, 35, 400, 150, 1, "c", 8),
            Cromo("SubwayTrain", _("Subway Train"), 5, 85, 0, 0, 10, 20, 300, 150, 1, "t", 9),
            Cromo("TruckMountedCrane", _("Truck Mounted Crane"), 5, 90, 0, 0, 10, 24, 300, 150, 1, "c", 9),
            Cromo("AirAmbulance", _("Air Ambulance"), 5, 95, 0, 0, 10, 22, 300, 150, 1, "s", 9),
            Cromo("Airplane", _("Airplane"), 5, 99, 0, 0, 10, 26, 300, 150, 1, "k", 999),
        ]
        return li
