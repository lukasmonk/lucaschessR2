import time


class TimeControl:
    def __init__(self, window, game, side):
        self.window = window
        self.game = game
        self.side = side

        self.total_time = 0.0
        self.pending_time = 0.0
        self.seconds_per_move = 0.0
        self.zeitnot_marker = 0.0

        self.time_init = None
        self.show_clock = False
        self.time_paused = 0.0
        self.time_previous = 0.0  # gastado en anteriores pausas

        self.pending_time_initial = 0

        self.set_clock_side = window.set_clock_white if side else window.set_clock_black
        self.is_displayed = True

    def set_displayed(self, is_displayed):
        self.is_displayed = is_displayed

    def config_clock(self, total_time, seconds_per_move, zeinot_marker, secs_extra):
        self.pending_time = self.total_time = total_time + secs_extra
        self.seconds_per_move = seconds_per_move if seconds_per_move else 0
        self.zeitnot_marker = zeinot_marker if zeinot_marker else 0
        self.show_clock = total_time > 0.0

    def config_as_time_keeper(self):
        self.config_clock(99999, 0, 0, 0)
        self.is_displayed = False

    @staticmethod
    def text(segs):
        if segs <= 0.0:
            segs = 0.0
        tp = round(segs)
        txt = "%02d:%02d" % (int(tp / 60), tp % 60)

        return txt

    def get_seconds(self):
        if self.time_init:
            tp = self.pending_time - (time.time() - self.time_init)
        else:
            tp = self.pending_time
        if tp <= 0.0:
            tp = 0
        return round(tp)

    def label(self):
        return self.text(self.get_seconds())

    def start(self):
        if self.time_paused:
            self.pending_time -= self.time_paused
            self.time_previous += self.time_paused
        else:
            self.time_previous = 0
            self.pending_time_initial = self.pending_time
        self.time_init = time.time()
        self.time_paused = 0.0

    def stop(self):
        if self.time_init:
            t_used = time.time() - self.time_init
            self.pending_time -= t_used - self.seconds_per_move
            self.time_init = None
            self.time_previous = 0
            return t_used
        else:
            tp = self.time_paused
            self.pending_time -= tp - self.seconds_per_move
            self.time_paused = 0
            self.time_previous = 0
        return tp

    def pause(self):
        if self.time_init:
            t_used = time.time() - self.time_init
            self.time_init = None
            self.time_paused = t_used

    def reset(self):
        # Cuando se hace pause a un motor, se vuelve a los valores iniciales
        self.time_init = None
        self.time_paused = 0
        self.time_previous = 0
        self.pending_time = self.pending_time_initial

    def restart(self):
        self.time_init = time.time() - self.time_paused
        self.time_paused = 0
        self.set_labels()

    def get_seconds2(self):
        if self.time_init:
            tp2 = time.time() - self.time_init
            tp = self.pending_time - tp2
        else:
            tp = self.pending_time - self.time_paused
            tp2 = self.time_paused
        if tp <= 0.0:
            tp = 0
        return tp, tp2 + self.time_previous

    def set_labels(self):
        if self.is_displayed:
            tp, tp2 = self.get_seconds2()
            eti, eti2 = self.text(tp), self.text(tp2)

            if eti:
                # if self.pending_time > 30000:
                #     eti = ""
                self.set_clock_side(eti, eti2)

    def label_dgt(self):
        segs = self.get_seconds()
        mins = segs // 60
        segs -= mins * 60
        hors = mins // 60
        mins -= hors * 60

        return "%d:%02d:%02d" % (hors, mins, segs)

    def time_is_consumed(self):
        if self.time_init:
            if (self.pending_time - (time.time() - self.time_init)) <= 0.0:
                return True
        else:
            return self.pending_time <= 0.0
        return False

    def is_zeitnot(self):
        if self.zeitnot_marker:
            if self.time_init:
                t = self.pending_time - (time.time() - self.time_init)
            else:
                t = self.pending_time
            if t > 0:
                resp = t < self.zeitnot_marker
                if resp:
                    self.zeitnot_marker = None
                return resp
        return False

    def set_zeinot(self, segs):
        self.zeitnot_marker = segs

    def add_extra_seconds(self, secs):
        self.pending_time += secs
        self.total_time += secs

    def save(self):
        return self.total_time, self.pending_time, self.zeitnot_marker, self.time_paused

    def restore(self, tvar):
        self.total_time, self.pending_time, self.zeitnot_marker, self.time_paused = tvar
        self.time_init = None
