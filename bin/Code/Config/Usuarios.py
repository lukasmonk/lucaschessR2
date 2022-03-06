import sys

import Code
from Code import Util
from Code.Config import Configuration


class User:
    name = ""
    number = 0
    password = ""

    def __str__(self):
        return "%d: %s %s" % (self.number, self.name, self.password)


class Usuarios:
    def __init__(self):
        self.file = "%s/users.p64" % Configuration.active_folder()
        self.list_users = self.read()
        self.include_main()

    def include_main(self):
        ok_main = False
        conf_main = Code.configuration
        # conf_main.lee()
        for user in self.list_users:
            if user.number == 0:
                ok_main = True
                user.name = conf_main.x_player
        if not ok_main:
            user = User()
            user.number = 0
            user.name = conf_main.x_player
            self.list_users.insert(0, user)
            self.save()

    def save(self):
        Util.save_pickle(self.file, self.list_users)

    def read(self):
        if Util.exist_file(self.file):
            try:
                resp = Util.restore_pickle(self.file)
            except ModuleNotFoundError:
                import Code.Config.Usuarios

                sys.modules["Code.Usuarios"] = Code.Config.Usuarios
                resp = self.list_users = Util.restore_pickle(self.file)
                self.save()
            except:
                resp = []
            return resp if resp else []
        return []

    def save_list(self, list_users):
        self.list_users = list_users
        self.save()
