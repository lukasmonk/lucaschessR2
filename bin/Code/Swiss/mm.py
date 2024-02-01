import math
import random

WHITE, BLACK, DRAW = range(3)

"""Las siguientes reglas son válidas para cada sistema suizo a menos que se indique explícitamente lo contrario.
a El número de rondas a jugar se declara de antemano.

b Dos jugadores no podrán jugar entre sí más de una vez.

C Si el número de jugadores a emparejar es impar, un jugador queda desemparejado. 
  Este jugador recibe un bye asignado por emparejamiento: sin oponente, sin color 
  y tantos puntos como se recompensen por una victoria, a menos que las reglas 
  del torneo indiquen lo contrario.

d Un jugador que ya haya recibido un descanso asignado por emparejamiento, 
  o que ya haya obtenido una victoria (perdida) debido a que un oponente 
  no apareció a tiempo, no recibirá el descanso asignado por emparejamiento.

e En general, los jugadores se emparejan con otros con la misma puntuación.

f Para cada jugador, la diferencia entre el número de partidas de negras y blancas 
  no será mayor que 2 ni menor que –2. Cada sistema puede tener excepciones a esta 
  regla en la última ronda de un torneo.

g Ningún jugador recibirá el mismo color tres veces seguidas. Cada sistema puede 
  tener excepciones a esta regla en la última ronda de un torneo.

h 1 Por lo general, a un jugador se le da el color con el que menos partidos ha jugado.
  2 Si los colores ya están equilibrados, entonces, en general, al jugador se le da el 
    color que se alterna con el último con el que jugó.

Las reglas de emparejamiento deben ser tan transparentes que la persona responsable
del emparejamiento pueda explicarlas"""


class Player:
    def __init__(self, name, elo):
        self.name = name
        self.elo = elo
        self.white = 0
        self.black = 0
        self.last_played = None
        self.win = 0
        self.lost = 0
        self.draw = 0
        self.byes = 0
        self.li_rival_win: list[Player] = []
        self.li_rival_draw: list[Player] = []
        self.li_rival_lost: list[Player] = []

    def score(self) -> int:
        return self.win * 10 + self.draw * 5

    def desempate(self):
        rival_win = sum(rival.score() for rival in self.li_rival_win)
        rival_draw = sum(rival.score() for rival in self.li_rival_draw)
        rival = rival_win * 10 + rival_draw * 5
        return f"{self.score():04d}{rival:05d}{self.win:03d}{self.draw:03d}{self.elo:04d}"

    def next_side(self):
        if self.white < self.black:
            return WHITE
        elif self.white > self.black:
            return BLACK
        elif self.last_played is not None:
            return WHITE if self.last_played == BLACK else BLACK
        else:
            return None


class Match:
    def __init__(self, player_w: Player, player_b: Player):
        self.player_w: Player = player_w
        self.player_b: Player = player_b
        self.result = None


class Ronda:
    def __init__(self, li_players):
        self.li_matches: list[Match] = []
        self.li_players: list[Player] = li_players
        self.with_byes = len(self.li_players) % 2 == 1

    def genera_matches(self):
        if self.with_byes:
            num_byes = 0
            while True:
                li_no_bye = [player for player in self.li_players if player.byes == num_byes]
                if len(li_no_bye) == 0:
                    num_byes += 1
                else:
                    break
            player_bye = random.choice(li_no_bye)
            player_bye.byes += 1
            li_players_play = [player for player in self.li_players if player != player_bye]
        else:
            li_players_play = self.li_players[:]

        li_players_play.sort(key=lambda player: player.desempate(), reverse=True)

        st_playing = set()
        num_players_play = len(li_players_play)
        player: Player
        for num, player in enumerate(li_players_play):
            if player in st_playing:
                continue
            rival_select = None
            look_for = player.next_side()
            if look_for is not None:
                for num_rival in range(num + 1, min(num + 2 + num_players_play * 20 // 100, num_players_play)):
                    rival = li_players_play[num_rival]
                    if rival in st_playing:
                        continue
                    look_for_rival = rival.next_side()
                    if look_for_rival != look_for:
                        rival_select = rival
                        break
            if rival_select is None:
                for num_rival in range(num + 1, num_players_play):
                    rival = li_players_play[num_rival]
                    if rival in st_playing:
                        continue
                    rival_select = rival
                    break
            player_w, player_b = player, rival_select
            if player_w.white >= player_w.black and player_b.black >= player_b.white:
                player_w, player_b = player_b, player_w
            player_w.white += 1
            player_b.black += 1
            player_w.last_played = WHITE
            player_b.last_played = BLACK
            st_playing.add(player_w)
            st_playing.add(player_b)
            match = Match(player_w, player_b)
            self.li_matches.append(match)

    def play_random(self):
        match: Match
        for match in self.li_matches:
            match.result = random.choice(
                [WHITE, WHITE, WHITE, WHITE, WHITE, WHITE, DRAW, DRAW, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK])
            player_w = match.player_w
            player_b = match.player_b
            if match.result == WHITE:
                player_w.win += 1
                player_w.li_rival_win.append(player_b)
                player_b.lost += 1
                player_b.li_rival_lost.append(player_w)
            elif match.result == BLACK:
                player_b.win += 1
                player_b.li_rival_win.append(player_w)
                player_w.lost += 1
                player_w.li_rival_lost.append(player_b)
            else:
                player_b.draw += 1
                player_b.li_rival_draw.append(player_w)
                player_w.draw += 1
                player_w.li_rival_draw.append(player_b)


def rondas(num_players: int) -> int:
    return math.ceil(math.log2(num_players))


def crea_players(num):
    li = []
    for x in range(num):
        player: Player = Player(f"P{x:03d}", random.choice(range(1200, 2000, 100)))
        li.append(player)
    return li


def genera(num_players):
    li_players = crea_players(num_players)

    num_rondas = rondas(num_players)

    for num_ronda in range(num_rondas):
        r = Ronda(li_players)
        r.genera_matches()
        r.play_random()

    li_players.sort(key=lambda player: player.desempate(), reverse=True)

    num_des = 0
    for player in li_players:
        print(player.name, player.white, player.black, player.win, player.lost, player.draw,
              player.white + player.black, player.desempate())

        if player.white != player.black:
            num_des += 1
    print(num_des)
    print(num_rondas)


genera(83)
