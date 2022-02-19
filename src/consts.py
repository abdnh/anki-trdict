import os

ADDON_NAME = "TRDict"
ADDON_NAME_LONG = "TRDict - Turkish Dictionary"
ADDON_DIR = os.path.dirname(__file__)
USER_FILES = os.path.join(ADDON_DIR, "user_files")
AUDIO_CACHE_DIR = os.path.join(USER_FILES, "audiocache")
FAILED_LOOKUP_CACHE_FILE = os.path.join(USER_FILES, "failed_lookups.json")
os.makedirs(AUDIO_CACHE_DIR, exist_ok=True)
if not os.path.exists(FAILED_LOOKUP_CACHE_FILE):
    with open(FAILED_LOOKUP_CACHE_FILE, "w") as f:
        f.write("[]\n")
