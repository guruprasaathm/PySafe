import eel
from py3.encryption_file_dialog import *
from py3.alertboxes import *
from py3.aes.index_cryptography import *
from py3.aes.stream import *
from py3.json_model_functions import *
from py3.UserIndex import *
from os import remove, makedirs, path
from time import time
from getpass import getuser
from json import dump

__author__ = "GuruPrasaath Manirajan"
__license__ = "The Prosperity Public License 3.0.0"
__version__ = "0.1A"

'''
This file PySafe.py is a core part of the open source PySafe encryption software developed and maintained by
GuruPrasaathM (https://www.guruprasaathm.com | https://github.com/GuruPrasaathM | mailto:guruprasaathm@gmail.com)

CRITICAL NOTE: The Project PySafe is still in a very young, alpha development phase, It is suggested to not use this software at its current state
			   in production environments/personal use until more stable releases come through, As a lot of functions are still to be implemented and
			   data loss/corruption is still a very real possibility.

Important things to note: (License Brief)
Usage of this software is liable to the conditions mentioned in the license file (see License.md), As per the same:
	1. This software is made available as open source with specific exemptions including the usage of this software
	   and any of its associated digital material for any commercial purpose unless it qualifies as fair use or permission to do so has been acquired
	   from the creator, Non-Commercial usage is freely permitted and permission need not be acquired.
	2. This software may be contributed to directly or can re-developed exclusively in open-source environments.
	3. The Creator of this software is in no way liable for any damages/loss resulting from the usage of this software in any context.
'''

eel.init('web')

@eel.expose
def Mbox(title, text, style):
	GenericMessageBox(title, text, style)
	return None

@eel.expose
def LoginValidation(uname, pwd):
	UserObj = UserIndex(uname)
	if UserObj.CheckUser() == 1:
		encdecobj = encdec(uname, pwd)
		DecryptPromise = encdecobj.decryptfrompass()
		return DecryptPromise[0]
	else:
		return -2

@eel.expose
def GetUserIndex(uname, pwd):
	global crypto_obj
	crypto_obj = encdec(uname, pwd)
	DecryptPromise = crypto_obj.decryptfrompass()
	#print(encdecobj.decryptfrompass())
	UserData = str(DecryptPromise[1])
	return UserData

@eel.expose
def AddAccount(profarray):
	try:
		JsonTemplateObject = JsonIndex(profarray[0])
		JsonTemplateObject.initialize_index(profarray[0],profarray[2],int(time()))
		this_account = JsonTemplateObject.return_json()
		crypto_obj = encdec(profarray[0], profarray[1])
		if (crypto_obj.encryptfrompass(this_account)) == 1:
			tempobj = UserIndex(profarray[0])
			tempobj.Append_User()
			return 1
		else:
			return 0
	except:
		raise

@eel.expose
def fileinihandle(id):
	return (general_files(id))

@eel.expose
def File_Encrypt(libname, ifp):
	aes_obj = aes256(libname, crypto_obj)
	aes_data = aes_obj.filecryptini(ifp)
	return aes_obj.file_encrypt_stream(aes_data)

@eel.expose
def File_Decrypt(libname, ofp):
	aes_obj = aes256(libname, crypto_obj)
	aes_data = aes_obj.filedecryptini(ofp)
	return aes_obj.file_decrypt_stream(aes_data, ofp)

@eel.expose
def Text_Encrpyt(libname, inp_text):
	aes_obj = aes256(libname, crypto_obj)
	return aes_obj.text_encrpyt_2_txt(inp_text)

@eel.expose
def Text_Decrypt(libname):
	global tbr_txt
	aes_obj = aes256(libname, crypto_obj)
	aes_return = aes_obj.text_decrypt_f4m_txt()

	tbr_txt = []
	tbr_txt.append(aes_return)


@eel.expose
def mkindex():
	global tbr_txt
	tbr_txt = []
	GenPath = "C:\\Users\\{}\\AppData\\Local\\PySafe".format(getuser())
	patharr = [GenPath, GenPath + "\\accessindex", GenPath + "\\libs", GenPath +"\\users"]
	for fpath in patharr:
		if not path.exists(fpath):
			makedirs(fpath)
		else:
			break
	else:
		Json_Template = {"users":[]}
		with open(GenPath + "\\users\\" + "users.json", 'w+') as fp:
			dump(Json_Template, fp, indent=4)
			fp.close()

@eel.expose
def logout_clear():
	global crypto_obj
	del crypto_obj
	if not tbr_txt:
		for file in tbr_txt:
			remove(file)

eel.start('index.html', size=(1040, 615))

#1040615
#1040709
