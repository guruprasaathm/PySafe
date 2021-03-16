'''
This program file is a part of the open source PySafe encryption software developed and maintained by
GuruPrasaathM (https://www.guruprasaathm.com | https://github.com/GuruPrasaathM | mailto:guruprasaathm@gmail.com)

See the core file Pysafe.py for more details
'''

from os import path, makedirs, walk, remove, startfile
from .indiecryption import *
from py3.aes.index_cryptography import *
from shutil import make_archive
from subprocess import Popen
from getpass import getuser

class aes256:
    def __init__(self, libname, encdecobj):
        self.libname = libname
        self.encdecobj = encdecobj

    def getfiles(self, start_path):
        filearr = []
        for dirpath, dirnames, filenames in walk(start_path):
            for f in filenames:
                fp = path.join(dirpath, f)
                if not path.islink(fp):
                    filearr.append(str(path.abspath(fp)))
        return filearr

    def filecryptini(self, ifparr):
        FileDict = []
        for element in ifparr:
            if not path.isdir(element):
                this_basename = path.basename(element)
                opath = "C:\\Users\\{}\\AppData\\Local\\PySafe\\libs\\".format(getuser()) + "{}\\".format(self.libname) + this_basename + ".aes"
                FileEdge = {"name":this_basename, "ifp":element, "ofp":opath}
                FileDict.append(FileEdge)
            else:
                for file in self.getfiles(element):
                    ifparr.append(file)
                    this_basename = path.basename(file)
                    opath = "C:\\Users\\{}\\AppData\\Local\\PySafe\\libs\\".format(getuser()) + "{}\\".format(self.libname) + this_basename + ".aes"
                    FileEdge = {"name":this_basename, "ifp":element, "ofp":opath}
                    FileDict.append(FileEdge)

        return FileDict

    def filedecryptini(self, output_path_root):
        FileDict = []

        FileEdgeSrc = (self.encdecobj).decryptfrompass()[1]
        FileEdges = FileEdgeSrc["library_index"]["edges"][self.libname]

        for element in FileEdges:
            bname = element["name"]
            ifp = element["fp"]
            passw = element["pass"]
            ofp = output_path_root + "/" + element["name"]
            FileEdge = {"name":bname, "ifp":ifp, "ofp":ofp, "pass":passw}
            FileDict.append(FileEdge)

        return FileDict

    def file_encrypt_stream(self, FileEdgeArr):
        FileDict = {"FileEdges":[]}
        LibsPath = "C:\\Users\\{}\\AppData\\Local\\PySafe\\libs\\".format(getuser()) + "{}\\".format(self.libname)
        stat = 0
        if not path.exists(LibsPath):
            makedirs(LibsPath)
        for element in FileEdgeArr:
            ofpstr = str(element["ofp"])
            ifpstr = str(element["ifp"])
            bname = str(element["name"])
            crypt_return = indie_file_encrypt(ifpstr, ofpstr)
            if crypt_return[0]:
                this_pass = crypt_return[1]
                ThisItem = {"name":bname, "fp":ofpstr, "pass":this_pass, "istxt":0}
                FileDict["FileEdges"].append(ThisItem)
            else:
                break
        else:
            DecryptedJson = (self.encdecobj).decryptfrompass()[1]
            DecryptedJson["library_index"]["lib_array"].append(self.libname)
            DecryptedJson["library_index"]["lib_count"]+=1
            DecryptedJson["library_index"]["edges"][self.libname] = []
            for element in FileDict["FileEdges"]:
                DecryptedJson["library_index"]["edges"][self.libname].append(element)

            (self.encdecobj).encryptfrompass(DecryptedJson)

            stat = 1

        return stat

    def file_decrypt_stream(self, FileEdgeArr, op):
        for elem in FileEdgeArr:
            ofp = open(elem["ofp"], 'wb+')
            ofp.close()
            crypt_return = indie_file_decrypt(elem["ifp"], elem["ofp"], elem["pass"])
            if crypt_return:
                stat = 1
            else:
                stat = 0
                break
        else:
            PathObj = path.realpath(op)
            startfile(PathObj)
        return stat


    def text_encrpyt_2_txt(self, text):
        LibsPath = "C:\\Users\\{}\\AppData\\Local\\PySafe\\libs\\".format(getuser()) + "{}\\".format(self.libname)
        if not path.exists(LibsPath):
            makedirs(LibsPath)

        temptext_ifp = LibsPath + self.libname + ".txt"
        text_ofp = LibsPath + self.libname + ".txt.aes"

        with open(temptext_ifp, 'w+') as tmp:
            tmp.write(text)
            tmp.close()
        with open(text_ofp, 'wb+') as tmp:
            tmp.close()

        crypt_return = indie_file_encrypt(temptext_ifp, text_ofp)

        remove(temptext_ifp)

        if crypt_return[0]:
            ThisItem = {"name":self.libname + ".txt", "fp": text_ofp, "pass":crypt_return[1], "istxt":1}

            DecryptedJson = (self.encdecobj).decryptfrompass()[1]
            DecryptedJson["library_index"]["lib_array"].append(self.libname)
            DecryptedJson["library_index"]["lib_count"]+=1
            DecryptedJson["library_index"]["edges"][self.libname] = []

            DecryptedJson["library_index"]["edges"][self.libname].append(ThisItem)

            (self.encdecobj).encryptfrompass(DecryptedJson)

            return 1

        else:
            return 0


    def text_decrypt_f4m_txt(self):
        FileEdge = (self.encdecobj).decryptfrompass()[1]["library_index"]["edges"][self.libname][0]

        ifp = FileEdge["fp"]
        ofp = ifp[:-4]
        passw = FileEdge["pass"]

        crypt_return = indie_file_decrypt(ifp, ofp, passw)

        programName = "notepad.exe"
        Popen([programName, ofp])

        return ofp
