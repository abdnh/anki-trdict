import os

ADDON_NAME = "TRDict"
ADDON_NAME_LONG = "TRDict - Turkish Dictionary"
ADDON_DIR = os.path.dirname(__file__)
USER_FILES = os.path.join(ADDON_DIR, "user_files")
AUDIO_CACHE_DIR = os.path.join(USER_FILES, "audiocache")
os.makedirs(AUDIO_CACHE_DIR, exist_ok=True)
