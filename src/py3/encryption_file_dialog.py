'''
This program file is a part of the open source PySafe encryption software developed and maintained by
GuruPrasaathM (https://www.guruprasaathm.com | https://github.com/GuruPrasaathM | mailto:guruprasaathm@gmail.com)

See the core file Pysafe.py for more details
'''

from tkinter.filedialog import askopenfilenames, askopenfilename, askdirectory
from os import path, stat, walk
import tkinter

def get_size(start_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in walk(start_path):
        for f in filenames:
            fp = path.join(dirpath, f)
            if not path.islink(fp):
                total_size += path.getsize(fp)
    return total_size

def general_files(id):
	rootwin = tkinter.Tk()
	rootwin.withdraw()

	TypeDict = {
		"docid":{
			"inidir":"shell:Personal",
			"title":"select a document",
			"types":[
				("Document Files", '*.doc;*.docx;*.txt;*.xls;*.xlsx;*.xml;*.ppt;*.pdf;*.csv'),
				('All files', '*')
			]
		},
		"imgid":{
			"inidir":"shell:PicturesLibrary",
			"title":"select an image",
			"types":[
				('Image Files', '*.png;*.jpeg;*.jpg;*.bmp;*.ico;*.svg;*.gif'),
				('All files', '*')
			]
		},
		"vidid":{
			"inidir":"shell:My Video",
			"title":"select a video",
			"types":[
				('Video Files', '*.mp4;*.wmv;*.mpeg;*.raw;*.avi'),
				('All files', '*')
			]
		},
		"audid":{
			"inidir":"shell:My Music",
			"title":"select a audio file",
			"types":[
				('Audio Files', '*.mp3;*.m4a;*.aac;*.wav'),
				('All files', '*')
			]
		},
		"othid":{
			"inidir":"/",
			"title":"select a file",
			"types":[
				('All files', '*')
			]
		}
	}
	if id != "foldid":
		filenames = askopenfilenames(parent=rootwin, initialdir=TypeDict[id]["inidir"], title=TypeDict[id]["title"], filetypes=(TypeDict[id]["types"]))
		RetDict = []
		for elem in filenames:
			RetDict.append([str(path.basename(elem)),str(elem),str((round(((int(stat(elem).st_size))/1048576),2))),str(id)])
		return RetDict
	else:
		fold = askdirectory(parent=rootwin, initialdir="/", title="Select a folder", mustexist=True)
		RetDict = [[str(path.basename(fold)),str(fold),str((round(((int(get_size(fold)))/1048576),2))), str(id)]]
		return RetDict
