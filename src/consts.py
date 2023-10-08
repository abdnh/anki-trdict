import os

from ankiutils.consts import get_consts

consts = get_consts(__name__)
USER_FILES = os.path.join(consts.dir, "user_files")
AUDIO_CACHE_DIR = os.path.join(USER_FILES, "audiocache")
FAILED_LOOKUP_CACHE_FILE = os.path.join(USER_FILES, "lookups", "failed_lookups.json")
os.makedirs(AUDIO_CACHE_DIR, exist_ok=True)
if not os.path.exists(FAILED_LOOKUP_CACHE_FILE):
    with open(FAILED_LOOKUP_CACHE_FILE, "w", encoding="utf-8") as f:
        f.write("[]\n")

USER_AGENT = "Mozilla/5.0 (compatible; Anki)"
