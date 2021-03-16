'''
This program file is a part of the open source PySafe encryption software developed and maintained by
GuruPrasaathM (https://www.guruprasaathm.com | https://github.com/GuruPrasaathM | mailto:guruprasaathm@gmail.com)

See the core file Pysafe.py for more details
'''

from os import path
from json import load, dump
from getpass import getuser

class UserIndex:
    def __init__(self, passed_username):
        self.username = passed_username
        self.index_path = "C:\\Users\\{}\\AppData\\Local\\PySafe\\users\\users.json".format(getuser())

    def create_user_index(self):
        format = {"users":[]}
        with open("C:\\Users\\{}\\AppData\\Local\\PySafe\\users\\users.json".format(getuser()), "w+") as fil:
            dump(format, fil, indent=2)

    def Append_User(self):
        if path.isfile(self.index_path):
            with open(self.index_path, "r") as fil:
                JsonData = load(fil)
                fil.close()
            with open(self.index_path, "w") as fil:
                JsonData["users"].append(self.username)
                dump(JsonData, fil, indent=2)
        else:
            self.create_user_index()
            with open(self.index_path, "r") as fil:
                JsonData = load(fil)
                fil.close()
            with open(self.index_path, "w") as fil:
                JsonData["users"].append(self.username)
                dump(JsonData, fil, indent=2)

        return None

    def CheckUser(self):
        with open(self.index_path, "r") as fil:
            JsonData = load(fil)
            if (str(self.username) in str(JsonData["users"])):
                status = 1
            else:
                status = 0
            fil.close()
            return status
