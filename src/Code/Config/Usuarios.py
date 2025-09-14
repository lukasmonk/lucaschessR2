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

    def save(self):
        Util.save_pickle(self.file, self.list_users)

    def read(self):
        li_users = None
        if Util.exist_file(self.file):
            li_users = Util.restore_pickle(self.file)
        li_users = [] if li_users is None else li_users
        ok_main = False
        if li_users:
            for user in li_users:
                if user.number == 0:
                    ok_main = True
                    user.name = Code.configuration.x_player
                    break
        if not ok_main:
            user = User()
            user.number = 0
            user.name = Code.configuration.x_player
            li_users.insert(0, user)
        return li_users

    def save_list(self, list_users):
        self.list_users = list_users
        self.save()
