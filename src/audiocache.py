import os
from typing import List
import re
import json

from anki.utils import stripHTML
import tdk

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


def cache_failed_lookup(disk_word: str) -> None:
    with open(FAILED_LOOKUP_CACHE_FILE, "r") as f:
        lookups: List = json.load(f)
    lookups.append(disk_word)
    with open(FAILED_LOOKUP_CACHE_FILE, "w") as f:
        json.dump(lookups, f, ensure_ascii=False)


def has_cached_failed_lookup(disk_word: str) -> bool:
    with open(FAILED_LOOKUP_CACHE_FILE, "r") as f:
        lookups = set(json.load(f))
        return disk_word in lookups


def get_audio(word: str) -> List[str]:
    word = normalize_word(word)
    disk_word = to_disk_name(word)
    files = get_cached_audio(disk_word)
    if len(files) == 0 and not has_cached_failed_lookup(disk_word):
        query = tdk.TDK(word)
        try:
            links = query.audio_links
            query.word = disk_word
            files = query.download_audio(AUDIO_CACHE_DIR)
        except tdk.NoAudioError:
            cache_failed_lookup(disk_word)
            raise
    return files
