'''
This program file is a part of the open source PySafe encryption software developed and maintained by
GuruPrasaathM (https://www.guruprasaathm.com | https://github.com/GuruPrasaathM | mailto:guruprasaathm@gmail.com)

See the core file Pysafe.py for more details
'''

from base64 import urlsafe_b64encode
from os import urandom
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.exceptions import InvalidSignature
from os import path
from getpass import getuser
from json import dumps

class encdec:
    def __init__(self, libname, pwd):
        self.libname = libname
        self.pwd = pwd

    def encryptfrompass(self, jsondata):
        try:
            password = str.encode(self.pwd)
            salt = b"-/...././..-./..-/..../.-././.-./-../../-../-./---/-/..../../-./--./.--/.-./---/-./--.////"
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000
            )
            key = urlsafe_b64encode(kdf.derive(password))
            f = Fernet(key)
            filepath = "C:\\Users\\{}\\AppData\\Local\\PySafe\\accessindex\\".format(getuser()) + "{}.pysafelibindex".format(self.libname)
            if path.isfile(filepath):
                with open(filepath, "wb+") as file:
                    file.write(f.encrypt(str.encode(str(jsondata))))
                    file.close()
                    return 1
            else:
                with open(filepath, "wb+") as file:
                    file.write(f.encrypt(str.encode(str(jsondata))))
                    file.close()
                    return 1
        except:
            raise

    def decryptfrompass(self):
        password = str.encode(self.pwd)
        salt = b"-/...././..-./..-/..../.-././.-./-../../-../-./---/-/..../../-./--./.--/.-./---/-./--.////"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000
        )
        try:
            key = urlsafe_b64encode(kdf.derive(password))
            f = Fernet(key)
            filepath = ("C:\\Users\\{}\\AppData\\Local\\PySafe\\accessindex\\".format(getuser())) + "{}.pysafelibindex".format(self.libname)
            with open(filepath, 'rb') as fil:
                decrypted = eval(f.decrypt(fil.read()).decode())
                fil.close()
                return [1, decrypted]
        except (InvalidSignature, InvalidToken) as GroupedException:
            return [0, False]
        except:
            return [-2, True]

    def test(self):
        jsondata = {
            "guru": "smort",
            "walter": "white"
        }
        encrypted = self.encryptfrompass(jsondata)
        try:
            getpwd = input("Enter ye password...")
            print(self.decryptfrompass(getpwd, "GuruPrasaathM.pysafelibindex"))
        except (InvalidSignature, InvalidToken) as GroupedException:
            password=False
            print("Wrong password man!")
        #finally:
        #print("Wrong password you du di")

if "__name__"=="__main__":
    eobj = encdec("r","r")
    eobj.test()
