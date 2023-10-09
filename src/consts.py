from ankiutils.consts import get_consts

consts = get_consts(__name__)
USER_FILES = consts.dir / "user_files"
AUDIO_CACHE_DIR = USER_FILES / "audiocache"
FAILED_LOOKUP_CACHE_FILE = USER_FILES / "lookups" / "failed_lookups.json"
AUDIO_CACHE_DIR.mkdir(exist_ok=True, parents=True)
FAILED_LOOKUP_CACHE_FILE.parent.mkdir(exist_ok=True, parents=True)
if not FAILED_LOOKUP_CACHE_FILE.exists():
    with open(FAILED_LOOKUP_CACHE_FILE, "w", encoding="utf-8") as f:
        f.write("[]\n")

USER_AGENT = "Mozilla/5.0 (compatible; Anki)"
