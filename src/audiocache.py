import os
from typing import List
import re

from anki.utils import stripHTML
from tdk import TDK

from .consts import *


def normalize_word(word: str) -> str:
    return stripHTML(word).strip()


def to_disk_name(word: str) -> str:
    return word.replace(" ", "_")


def get_cached_audio(disk_word: str) -> List[str]:
    files = []
    pattern = re.compile(f"{re.escape(disk_word)}_[0-9]+")
    # FIXME: how does this perform for a large directory and how to optimize it?
    for file in os.listdir(AUDIO_CACHE_DIR):
        if pattern.match(file):
            files.append(os.path.join(AUDIO_CACHE_DIR, file))
    return files


def get_audio(word: str) -> List[str]:
    word = normalize_word(word)
    disk_word = to_disk_name(word)
    files = get_cached_audio(disk_word)
    if len(files) == 0:
        tdk = TDK(word)
        tdk.word = disk_word
        files = tdk.download_audio(AUDIO_CACHE_DIR)
    return files
