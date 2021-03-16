'''
This program file is a part of the open source PySafe encryption software developed and maintained by
GuruPrasaathM (https://www.guruprasaathm.com | https://github.com/GuruPrasaathM | mailto:guruprasaathm@gmail.com)

See the core file Pysafe.py for more details
'''

import random, string
import pyAesCrypt

AESBlockSize = 16
bufferSize = 64 * 1024


def indie_file_encrypt(ifp, ofp):
	passw = str(''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(32)))
	try:
		pyAesCrypt.encryptFile(ifp, ofp, passw, bufferSize)
		stat = 1
	except ValueError:
		stat = -1
	except:
		stat = 0
	finally:
		return [stat, passw]

def indie_file_decrypt(ifp, ofp, passw):
	try:
		pyAesCrypt.decryptFile(ifp, ofp, passw, bufferSize)
		stat = 1
	except ValueError:
		stat = -1
	except:
		stat = 0
	finally:
		return stat
