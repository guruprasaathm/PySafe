'''
This program file is a part of the open source PySafe encryption software developed and maintained by
GuruPrasaathM (https://www.guruprasaathm.com | https://github.com/GuruPrasaathM | mailto:guruprasaathm@gmail.com)

See the core file Pysafe.py for more details
'''

from json import load
from os import path

class JsonIndex:
    def __init__(self, username):
        self.username = username
        self.parent_json = {}

    def initialize_index(self, username, ac_mail, ac_create_time):
        self.parent_json["username"] = username
        self.parent_json["mail"] = ac_mail
        self.parent_json["ac_create_time"] = ac_create_time
        self.parent_json["access_time_array"] = []
        self.parent_json["library_index"] = {"lib_count": 0, "lib_array":[], "edges": {}}

    def update_SignIn_array(self, ac_access_time):
        self.parent_json["access_time_array"].append(ac_access_time)

    def add_index_node(self, lib_name, lib_filecount, file_edge_array):
        self.parent_json["library_index"]["lib_count"] += 1
        self.parent_json["library_index"]["lib_array"].append(lib_name)
        _temp_fpatharray = []
        _totalbytes = 0
        for srcfile in file_edge_array:
            _temp_fpatharray.append((path.splittext(srcfile[1]))[1])
            _totalbytes += srcfile[2]
        self.parent_json["library_index"]
    def return_json(self):
        return self.parent_json

if "__name__" == "__main__":
    pass
