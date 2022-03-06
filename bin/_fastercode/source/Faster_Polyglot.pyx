DEF_TXT = "".join([chr(x) for x in range(33, 124)])
DEF_TXT_LEN = len(DEF_TXT)

def int_str(num):
     li = []
     while num > 0:
         r = num % DEF_TXT_LEN
         li.append(DEF_TXT[r])
         num //= DEF_TXT_LEN
     return "".join(reversed(li))


def str_int(txt):
    num = 0
    for n in range(len(txt)):
        c = txt[n]
        if c > " ":
            num = num * DEF_TXT_LEN + DEF_TXT.index(c)
    return num


def keymove_str(nkey, nmove):
    return "%10s%3s" % (int_str(nkey), int_str(nmove))


def str_keymove(txt):
    return str_int(txt[:10]), str_int(txt[10:])


def hash_polyglot(bfen):
    return hash_from_fen(bfen)


def hash_polyglot8(fen):
    return hash_from_fen(fen.encode())


def movepolyglot_string(nmove):
    cdef char move_s[6];
    move_to_string(move_s, nmove)
    return move_s.decode()


def string_movepolyglot(cmove):
    return move_from_string(cmove.encode())


class Entry:
    key = 0
    move = 0
    weight = 0
    score = 0
    depth = 0
    learn = 0

    def pv(self):
        move = self.move

        f = (move >> 6) & 0o77
        fr = (f >> 3) & 0x7
        ff = f & 0x7
        t = move & 0o77
        tr = (t >> 3) & 0x7
        tf = t & 0x7
        p = (move >> 12) & 0x7
        pv = chr(ff + ord("a")) + chr(fr + ord("1")) + chr(tf + ord("a")) + chr(tr + ord("1"))
        if p:
            pv += " nbrq"[p]

        return {"e1h1": "e1g1", "e1a1": "e1c1", "e8h8": "e8g8", "e8a8": "e8c8"}.get(pv, pv)


class Polyglot:
    SEEK_SET, SEEK_CUR, SEEK_END = range(3)

    def __init__(self, path_book=None, modo=None):
        self.path_book = path_book
        self.file = None
        self.mode = "rb" if modo is None else modo
        if self.path_book:
            self.open()

    def open(self):
        if self.file is None:
            self.file = open(self.path_book, self.mode)

    def close(self):
        if self.file:
            self.file.close()
            self.file = None

    def int_fromfile(self, l, r):
        cad = self.file.read(l)
        if len(cad) != l:
            return True, 0
        for c in cad:
            r = (r << 8) + c
        return False, r

    def entry_fromfile(self):
        entry = Entry()

        r = 0
        ret, r = self.int_fromfile(8, r)
        if ret:
            return True, None
        entry.key = r

        ret, r = self.int_fromfile(2, r)
        if ret:
            return True, None
        entry.move = r & 0xFFFF

        ret, r = self.int_fromfile(2, r)
        if ret:
            return True, None
        entry.weight = r & 0xFFFF

        ret, r = self.int_fromfile(2, r)
        if ret:
            return True, None
        entry.score = r & 0xFFFF

        ret, r = self.int_fromfile(1, r)
        if ret:
            return True, None
        entry.depth = r & 0xFF

        ret, r = self.int_fromfile(1, r)
        if ret:
            return True, None
        entry.learn = r & 0xFF

        return False, entry

    def __len__(self):
        self.file.seek(0, self.SEEK_END)
        return  self.file.tell() // 16

    def find_key(self, key):
        first = -1
        try:
            if not self.file.seek(-16, self.SEEK_END):
                entry = Entry()
                entry.key = key + 1
                return -1, entry
        except Exception as e:
            return -1, None

        last = self.file.tell() // 16
        ret, last_entry = self.entry_fromfile()
        while True:
            if last - first == 1:
                return last, last_entry

            middle = (first + last) // 2
            self.file.seek(16 * middle, self.SEEK_SET)
            ret, middle_entry = self.entry_fromfile()
            if key <= middle_entry.key:
                last = middle
                last_entry = middle_entry
            else:
                first = middle

    def list_entries(self, fen):
        key = hash_from_fen(fen.encode())

        offset, entry = self.find_key(key)
        li = []
        if entry and entry.key == key:

            li.append(entry)

            self.file.seek(16 * (offset + 1), self.SEEK_SET)
            while True:
                ret, entry = self.entry_fromfile()
                if ret or (entry.key != key):
                    break

                li.append(entry)
        return li

    def dict_entries(self, fen):
        key = hash_from_fen(fen.encode())

        offset, entry = self.find_key(key)
        d = {}
        if entry and entry.key == key:

            d[entry.move] = entry

            self.file.seek(16 * (offset + 1), self.SEEK_SET)
            while True:
                ret, entry = self.entry_fromfile()
                if ret or (entry.key != key):
                    break

                d[entry.move] = entry
        return key, int_str(key), d

    def __iter__(self):
        self.offset = 0
        self.file.seek(0, self.SEEK_SET)
        return self

    def __next__(self):
        nok, entry = self.entry_fromfile()
        if nok:
            raise StopIteration
        else:
            return entry


class BinMove:
    def __init__(self, info_move):
        self.info_move = info_move
        # def xfrom(self):
        # def xto(self):
        # def promotion(self):
        # def move(self):
        # def check(self):
        # def mate(self):
        # def capture(self):
        # def piece(self):
        # def iscastle_k(self):
        # def iscastle_q(self):
        # def is_enpassant(self):
        # def san(self):

        self.entry = Entry()

    def imove(self):
        return move_from_string(self.info_move.bmove())

    def move(self):
        return self.info_move.move()

    def set_entry(self, entry):
        self.entry = entry

    def get_entry(self):
        return self.entry

    def get_field(self, field):
        return getattr(self.entry, field)

    def weight(self):
        return self.entry.weight

    def set_field(self, field, valor):
        setattr(self.entry, field, valor)


class PolyglotWriter:
    def __init__(self, path_bin):
        open_poly_w(path_bin.encode())

    def write(self, entry):
        write_integer(8, entry.key)
        write_integer(2, entry.move)
        write_integer(2, entry.weight)
        write_integer(2, entry.score)
        write_integer(1, entry.depth)
        write_integer(1, entry.learn)

    def close(self):
        close_poly()

