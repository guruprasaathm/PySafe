
import os, sys, json, base64, hashlib, time, socket, subprocess, shutil
from pathlib import Path
from datetime import datetime
from getpass import getuser
from typing import List, Dict, Any, Optional

import eel
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2

# -------------------------------
# Configuration / Paths (Windows)
# -------------------------------

APP_NAME = "PySafe"
DOCS_ROOT = Path.home() / "Documents" / APP_NAME                  # Encrypted payloads (ciphertexts) live here
LOCAL_ROOT = Path(os.getenv("LOCALAPPDATA", Path.home())) / APP_NAME / "data"  # App data (users, indexes, logs)
LOCAL_ROOT.mkdir(parents=True, exist_ok=True)
(DOCS_ROOT / "libs").mkdir(parents=True, exist_ok=True)

USERS_JSON = LOCAL_ROOT / "users.json"          # KDF salts & hashes only (no plaintext secrets)
LOGS_JSON  = LOCAL_ROOT / "access_logs.json"    # optional local log mirror (for demo)

# Mongo defaults
MONGO_HOST = "127.0.0.1"
MONGO_PORT = 27017
MONGO_DB   = "pysafe"

# --------------------
# Session & utilities
# --------------------

CURRENT_USERNAME: Optional[str] = None
CURRENT_MK: Optional[bytes]     = None   # Master key derived from password (not persisted)

def set_current_user(username: Optional[str], mk: Optional[bytes] = None):
    global CURRENT_USERNAME, CURRENT_MK
    CURRENT_USERNAME = (username or "").strip() or None
    CURRENT_MK = mk

def get_current_user() -> str:
    return CURRENT_USERNAME or getuser()

def stable_user_id(username: str) -> str:
    return hashlib.sha256(("user::"+username).encode("utf-8")).hexdigest()[:24]

def stable_lib_id(username: str, libname: str) -> str:
    return hashlib.sha256(("lib::"+username+"::"+libname).encode("utf-8")).hexdigest()[:24]

def lib_dir(username: str, libname: str) -> Path:
    p = DOCS_ROOT / "libs" / username / libname
    p.mkdir(parents=True, exist_ok=True)
    return p

def dec_dir(username: str, libname: str) -> Path:
    p = DOCS_ROOT / "decrypted" / username / libname
    p.mkdir(parents=True, exist_ok=True)
    return p

def load_json(path: Path, default):
    try:
        if path.is_file():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return default

def save_json(path: Path, obj) -> bool:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(obj, indent=2), encoding="utf-8")
        return True
    except Exception:
        return False

# -----------------
# KDF & Crypto (GCM)
# -----------------

def derive_mk(password: str, salt: bytes, iters: int = 200_000) -> bytes:
    return PBKDF2(password, salt, dkLen=32, count=iters)  # AES-256

def encrypt_bytes(plain: bytes, key: bytes, aad: Optional[bytes] = None) -> Dict[str, str]:
    iv = get_random_bytes(12)
    cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
    if aad:
        cipher.update(aad)
    ct, tag = cipher.encrypt_and_digest(plain)
    return {
        "iv": base64.b64encode(iv).decode(),
        "tag": base64.b64encode(tag).decode(),
        "ct":  base64.b64encode(ct).decode()
    }

def decrypt_bytes(blob: Dict[str, str], key: bytes, aad: Optional[bytes] = None) -> bytes:
    iv  = base64.b64decode(blob["iv"])
    tag = base64.b64decode(blob["tag"])
    ct  = base64.b64decode(blob["ct"])
    cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
    if aad:
        cipher.update(aad)
    return cipher.decrypt_and_verify(ct, tag)

# ----------------------
# Users (PBKDF2 verifer)
# ----------------------

def load_users():
    return load_json(USERS_JSON, {"users": []})

def save_users(obj) -> bool:
    return save_json(USERS_JSON, obj)

def find_user(username: str):
    udb = load_users()
    for u in udb["users"]:
        if u["username"].lower() == username.lower():
            return u
    return None

def create_user(username: str, password: str, mail: str) -> int:
    if not username or not password:
        return 0
    udb = load_users()
    if any(u["username"].lower() == username.lower() for u in udb["users"]):
        return 2  # exists
    salt = get_random_bytes(16)
    mk   = derive_mk(password, salt)
    verifier = hashlib.sha256(mk).hexdigest()
    udb["users"].append({
        "username": username,
        "mail": mail,
        "kdf": {"salt": base64.b64encode(salt).decode(), "iters": 200_000},
        "verifier": verifier,
        "createdAt": datetime.utcnow().isoformat()+"Z"
    })
    save_users(udb)
    # initialize empty index (encrypted) for the user
    init_user_index(username, mk)
    return 1

# ----------------------
# Encrypted User Index
# ----------------------

def user_index_path(username: str) -> Path:
    return LOCAL_ROOT / "users" / username / "index.enc.json"

def init_user_index(username: str, mk: bytes):
    idx = {
        "user": username,
        "createdAt": datetime.utcnow().isoformat()+"Z",
        "library_index": {"lib_array": [], "lib_count": 0, "edges": {}}
    }
    save_user_index(username, mk, idx)

def load_user_index(username: str, mk: bytes) -> Dict[str, Any]:
    p = user_index_path(username)
    if not p.is_file():
        init_user_index(username, mk)
        return load_user_index(username, mk)
    raw = json.loads(p.read_text(encoding="utf-8"))
    plain = decrypt_bytes(raw, mk)
    data = json.loads(plain.decode("utf-8"))
    # normalize
    li = data.setdefault("library_index", {})
    li.setdefault("lib_array", [])
    li.setdefault("lib_count", len(li["lib_array"]))
    li.setdefault("edges", {})
    return data

def save_user_index(username: str, mk: bytes, data: Dict[str, Any]) -> bool:
    try:
        data["library_index"]["lib_count"] = len(data["library_index"]["lib_array"])
    except Exception:
        pass
    blob = encrypt_bytes(json.dumps(data).encode("utf-8"), mk)
    p = user_index_path(username)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(blob), encoding="utf-8")
    return True

# --------------------
# MongoDB (optional)
# --------------------
try:
    from pymongo import MongoClient, ASCENDING, DESCENDING
    from gridfs import GridFS
    MONGO_AVAILABLE = True
except Exception:
    MONGO_AVAILABLE = False

_MONGO_CLIENT = None
_MONGO_DB = None
_MONGO_FS = None

def port_open(host="127.0.0.1", port=27017, timeout=0.5):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False

def find_mongod_windows():
    candidates = [
        r"C:\\Program Files\\MongoDB\\Server\\8.0\\bin\\mongod.exe",
        r"C:\\Program Files\\MongoDB\\Server\\7.0\\bin\\mongod.exe",
        r"C:\\Program Files\\MongoDB\\Server\\6.0\\bin\\mongod.exe",
    ]
    for p in candidates:
        if os.path.isfile(p):
            return p
    return shutil.which("mongod.exe")

def bootstrap_mongo() -> bool:
    if not MONGO_AVAILABLE:
        return False
    if port_open(MONGO_HOST, MONGO_PORT):
        return True
    mongod = find_mongod_windows()
    if not mongod:
        return False
    dbpath = str(LOCAL_ROOT / "mongodb")
    os.makedirs(dbpath, exist_ok=True)
    try:
        subprocess.Popen(
            [mongod, "--dbpath", dbpath, "--port", str(MONGO_PORT), "--bind_ip", MONGO_HOST],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=0x00000008
        )
    except Exception:
        return False
    for _ in range(40):
        if port_open(MONGO_HOST, MONGO_PORT): return True
        time.sleep(0.25)
    return False

def mongo_conn():
    global _MONGO_CLIENT, _MONGO_DB, _MONGO_FS
    if not MONGO_AVAILABLE:
        return None, None, None
    if _MONGO_DB is not None:
        return _MONGO_CLIENT, _MONGO_DB, _MONGO_FS
    if not bootstrap_mongo():
        return None, None, None
    try:
        _MONGO_CLIENT = MongoClient(f"mongodb://{MONGO_HOST}:{MONGO_PORT}", appname=APP_NAME)
        _MONGO_DB = _MONGO_CLIENT[MONGO_DB]
        _MONGO_FS = GridFS(_MONGO_DB)
        _MONGO_DB["fs.files"].create_index("metadata.userId")
        _MONGO_DB["fs.files"].create_index("metadata.libraryId")
        _MONGO_DB["fs.files"].create_index("uploadDate")
        _MONGO_DB["access_logs"].create_index([("userId", ASCENDING), ("ts", DESCENDING)])
        return _MONGO_CLIENT, _MONGO_DB, _MONGO_FS
    except Exception:
        return None, None, None

def db_status_for(username: Optional[str] = None) -> Dict[str, Any]:
    _, db, _ = mongo_conn()
    if db is None:
        return {"connected": False}
    try:
        uname = username or get_current_user()
        uid = stable_user_id(uname)
        files_count = db["fs.files"].count_documents({"metadata.userId": uid})
        texts_count = db["text_items"].count_documents({"userId": uid})
        size = 0
        for d in db["fs.files"].find({"metadata.userId": uid}, {"length": 1}):
            size += int(d.get("length", 0))
        return {"connected": True, "dbName": MONGO_DB, "filesCount": int(files_count), "textsCount": int(texts_count), "storageMB": round(size/1048576,2)}
    except Exception:
        return {"connected": True, "dbName": MONGO_DB, "filesCount": 0, "textsCount": 0, "storageMB": None}

def push_to_gridfs(username: str, libname: str, enc_path: Path, orig_name: str):
    _, db, fs = mongo_conn()
    if db is None or fs is None:
        return None
    data = enc_path.read_bytes()
    sha256 = hashlib.sha256(data).hexdigest()
    fid = fs.put(
        data,
        filename=enc_path.name,
        metadata={
            "userId": stable_user_id(username),
            "libraryId": stable_lib_id(username, libname),
            "orig": {"filename": orig_name, "bytes": len(data)},
            "cipher": {"alg": "AES-256-GCM"},
        }
    )
    try:
        db["access_logs"].insert_one({
            "ts": datetime.utcnow(),
            "userId": stable_user_id(username),
            "libraryId": stable_lib_id(username, libname),
            "action": "upload",
            "bytes": len(data),
            "success": True
        })
    except Exception:
        pass
    return str(fid)

def fetch_logs_mongo(log_type: str, limit: int = 200):
    _, db, _ = mongo_conn()
    if db is None: return []
    coll = db["access_logs"] if log_type != "auth" else db["auth_logs"]
    out = []
    try:
        cur = coll.find({}, sort=[("ts", -1)], limit=int(limit))
        for d in cur:
            d["_id"] = str(d.get("_id",""))
            out.append(d)
    except Exception:
        pass
    return out

# ------------------------
# Frontend-facing helpers
# ------------------------

def ensure_user_record(username: str, mk: bytes):
    # create index if missing
    p = user_index_path(username)
    if not p.is_file():
        init_user_index(username, mk)

def ensure_local_dirs(username: str):
    (DOCS_ROOT / "libs" / username).mkdir(parents=True, exist_ok=True)
    (DOCS_ROOT / "decrypted" / username).mkdir(parents=True, exist_ok=True)

# -----------------
# Eel Exposed APIs
# -----------------
# ---- TK helpers (one hidden root for all dialogs) ----
_tk_root = None
def _get_tk_root():
    global _tk_root
    if _tk_root is None:
        import tkinter as tk
        _tk_root = tk.Tk()
        _tk_root.withdraw()          # never show a window
    return _tk_root

@eel.expose
def mkindex():
    # No-op bootstrap hook used by UI
    return 1

@eel.expose
def AddAccount(data: List[str]):
    try:
        username, password, mail = data[0], data[1], data[2]
    except Exception:
        return 0
    return create_user(username, password, mail)

@eel.expose
def LoginValidation(uname: str, pwd: str):
    try:
        u = find_user(uname)
        if not u:
            return -2  # no account
        salt = base64.b64decode(u["kdf"]["salt"])
        mk   = derive_mk(pwd, salt, u["kdf"].get("iters", 200_000))
        if hashlib.sha256(mk).hexdigest() != u["verifier"]:
            return 0  # wrong password
        # success
        set_current_user(uname, mk)
        ensure_user_record(uname, mk)
        ensure_local_dirs(uname)
        return 1
    except Exception:
        return -1

@eel.expose
def logout_clear():
    set_current_user(None, None)
    return 1

@eel.expose
def GetUserIndex(uname: str, pwd: str):
    # Ignore pwd here (already validated in session); return a JSON structure the UI expects
    try:
        u = find_user(uname)
        if not u: return json.dumps({"err": "nouser"})
        salt = base64.b64decode(u["kdf"]["salt"])
        mk   = derive_mk(pwd, salt, u["kdf"].get("iters", 200_000))
        idx  = load_user_index(uname, mk)
        # augment with a couple fields UI uses
        idx["ac_create_time"] = u.get("createdAt")
        idx["mail"] = u.get("mail","")
        return json.dumps(idx)
    except Exception as e:
        return json.dumps({"err": "loadfail", "msg": str(e)})

# -------- File chooser for UI --------
@eel.expose
def fileinihandle(kind: str):
    from tkinter import filedialog
    root = _get_tk_root()
    files = filedialog.askopenfilenames(
        parent=root,
        title="Select files to encrypt",
        filetypes=[("All files", "*.*")]
    )
    return [[os.path.basename(f), f] for f in files]

@eel.expose
def pick_folder(initial: str = "") -> str:
    """
    Return a single absolute path to a chosen folder ('' if canceled).
    """
    from tkinter import filedialog
    root = _get_tk_root()
    init = initial.strip() or str(Path.home())
    path = filedialog.askdirectory(parent=root, title="Select destination folder", initialdir=init, mustexist=True)
    return path or ""

@eel.expose
def folderinihandle(kind: str = "destdir", initial: str = ""):
    """
    Mirror the file selector's return shape: [[label, fullpath]]
    This lets decr.js consume it exactly like fileselhandler().
    """
    p = pick_folder(initial)
    if not p:
        return []
    # label = last folder name; full absolute path returned as second element
    label = os.path.basename(p.rstrip("\\/"))
    return [[label or p, p]]

# -------- Encryption / Decryption --------

def _aead_encrypt_file(src_path: Path, out_path: Path, key: bytes):
    data = src_path.read_bytes()
    blob = encrypt_bytes(data, key, aad=src_path.name.encode("utf-8"))
    out = {
        "v": 1,
        "name": src_path.name,
        "alg": "AES-256-GCM",
        "blob": blob
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out), encoding="utf-8")

def _aead_decrypt_file(enc_path: Path, out_dir: Path, key: bytes) -> Path:
    obj = json.loads(enc_path.read_text(encoding="utf-8"))
    name = obj.get("name","decrypted.bin")
    blob = obj["blob"]
    plain = decrypt_bytes(blob, key, aad=name.encode("utf-8"))
    out_path = out_dir / name
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(plain)
    return out_path

@eel.expose
def File_Encrypt(lib_name: str, root_path: List[str], to_mongo: bool=False):
    if not CURRENT_USERNAME or not CURRENT_MK:
        return 0
    try:
        uname = get_current_user()
        # Ensure library exists in index
        idx = load_user_index(uname, CURRENT_MK)
        if lib_name not in idx["library_index"]["lib_array"]:
            idx["library_index"]["lib_array"].append(lib_name)
            idx["library_index"]["edges"][lib_name] = [ {"istxt": 0} ]
            save_user_index(uname, CURRENT_MK, idx)

        target_dir = lib_dir(uname, lib_name)
        for p in root_path:
            src = Path(p)
            enc_path = target_dir / (src.name + ".enc")
            _aead_encrypt_file(src, enc_path, CURRENT_MK)
            if to_mongo:
                push_to_gridfs(uname, lib_name, enc_path, src.name)
        return 1
    except Exception as e:
        return 0

@eel.expose
def Text_Encrpyt(lib_name: str, plaintext: str, to_mongo: bool=False):
    if not CURRENT_USERNAME or not CURRENT_MK:
        return 0
    try:
        uname = get_current_user()
        # mark lib as text if new
        idx = load_user_index(uname, CURRENT_MK)
        if lib_name not in idx["library_index"]["lib_array"]:
            idx["library_index"]["lib_array"].append(lib_name)
            idx["library_index"]["edges"][lib_name] = [ {"istxt": 1} ]
            save_user_index(uname, CURRENT_MK, idx)

        target_dir = lib_dir(uname, lib_name)
        tmp_plain = (target_dir / f"{lib_name}.txt")
        tmp_plain.write_text(plaintext, encoding="utf-8")
        enc_path = target_dir / f"{lib_name}.txt.enc"
        _aead_encrypt_file(tmp_plain, enc_path, CURRENT_MK)
        tmp_plain.unlink(missing_ok=True)
        if to_mongo:
            push_to_gridfs(uname, lib_name, enc_path, f"{lib_name}.txt")
        return 1
    except Exception:
        return 0

@eel.expose
def Decrypt_Library(lib_name: str, dest_dir: str):
    """
    Decrypt all .enc files in the library into the specified destination folder.
    Returns: {"ok": true, "count": N} on success, or {"ok": false, "error": "..."}.
    """
    try:
        uname = get_current_user()
        src_dir = lib_dir(uname, lib_name)
        if not src_dir.exists():
            return {"ok": False, "error": "library_not_found"}

        target = Path(dest_dir).expanduser()
        if not target.exists():
            try:
                target.mkdir(parents=True, exist_ok=True)
            except Exception:
                return {"ok": False, "error": "dest_unwritable"}

        count = 0
        for enc_path in src_dir.glob("*.enc"):
            try:
                print(_aead_decrypt_file(enc_path, target, CURRENT_MK))
                count += 1
            except Exception as f:
                # skip bad files and continue
                return {"ok": False, "error": str(f)}

        return {"ok": True, "count": count}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@eel.expose
def Text_Decrypt(lib_name: str):
    if not CURRENT_USERNAME or not CURRENT_MK:
        return 0
    try:
        uname = get_current_user()
        enc_path = lib_dir(uname, lib_name) / f"{lib_name}.txt.enc"
        outp = _aead_decrypt_file(enc_path, dec_dir(uname, lib_name), CURRENT_MK)
        return 1 if outp.is_file() else 0
    except Exception:
        return 0

# -------- Home DB Card & Logs --------

@eel.expose
def db_status():
    return db_status_for(get_current_user())

@eel.expose
def fetch_logs(log_type: str="access", limit: int=200):
    return fetch_logs_mongo(log_type, int(limit))

# -------- Message Box bridge --------

@eel.expose
def Mbox(title: str, message: str, kind: int = 0):
    from tkinter import messagebox
    root = _get_tk_root()
    if kind == 0:
        messagebox.showinfo(title, message, parent=root); return 1
    if kind == 1:
        messagebox.showwarning(title, message, parent=root); return 1
    if kind == 2:
        messagebox.showerror(title, message, parent=root); return 1
    if kind == 3:
        return 1 if messagebox.askyesno(title, message, parent=root) else 0
    # fallback
    messagebox.showinfo(title, message, parent=root); return 1

# -------- Eel init / start --------

def run():
    base_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))  # works in PyInstaller onefile
    web_dir = base_dir / "web"
    eel.init(str(web_dir))
    eel.start("index.html", size=(1200, 800), port=0, block=True)

if __name__ == "__main__":
    run()
