'''
This program file is a part of the open source PySafe encryption software developed and maintained by
GuruPrasaathM (https://www.guruprasaathm.com | https://github.com/GuruPrasaathM | mailto:guruprasaathm@gmail.com)

See the core file Pysafe.py for more details
'''

from json import dump
from getpass import getuser

def create_user_index():
    format = {"users":[]}
    with open("C:\\Users\\{}\\AppData\\Local\\PySafe\\users\\users.json").format(getuser()), "w+") as fil:
        dump(format, fil, indent=2)
