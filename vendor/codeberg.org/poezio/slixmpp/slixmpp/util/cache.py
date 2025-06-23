# Slixmpp: The Slick XMPP Library
# Copyright (C) 2018 Emmanuel Gil Peyrot
# This file is part of Slixmpp.
# See the file LICENSE for copying permission.
import os
import logging

from typing import Callable, Optional, Any

log = logging.getLogger(__name__)


class Cache:
    def retrieve(self, key):
        raise NotImplementedError

    def store(self, key, value):
        raise NotImplementedError

    def remove(self, key):
        raise NotImplementedError


class PerJidCache:
    def retrieve_by_jid(self, jid, key):
        raise NotImplementedError

    def store_by_jid(self, jid, key, value):
        raise NotImplementedError

    def remove_by_jid(self, jid, key):
        raise NotImplementedError


class MemoryCache(Cache):
    def __init__(self):
        self.cache = {}

    def retrieve(self, key):
        return self.cache.get(key, None)

    def store(self, key, value):
        self.cache[key] = value
        return True

    def remove(self, key):
        if key in self.cache:
            del self.cache[key]
        return True


class MemoryPerJidCache(PerJidCache):
    def __init__(self):
        self.cache = {}

    def retrieve_by_jid(self, jid, key):
        cache = self.cache.get(jid, None)
        if cache is None:
            return None
        return cache.get(key, None)

    def store_by_jid(self, jid, key, value):
        cache = self.cache.setdefault(jid, {})
        cache[key] = value
        return True

    def remove_by_jid(self, jid, key):
        cache = self.cache.get(jid, None)
        if cache is not None and key in cache:
            del cache[key]
        return True


class FileSystemStorage:
    def __init__(self, encode: Optional[Callable[[Any], str]], decode: Optional[Callable[[str], Any]], binary: bool):
        self.encode = encode if encode is not None else lambda x: x
        self.decode = decode if decode is not None else lambda x: x
        self.read = 'rb' if binary else 'r'
        self.write = 'wb' if binary else 'w'

    def _retrieve(self, directory: str, key: str):
        filename = os.path.join(directory, key.replace('/', '_'))
        try:
            with open(filename, self.read) as cache_file:
                return self.decode(cache_file.read())
        except FileNotFoundError:
            log.debug('%s not present in cache', key)
        except OSError:
            log.debug('Failed to read %s from cache:', key, exc_info=True)
        except Exception:
            log.debug('Failed to decode %s from cache:', key, exc_info=True)
            log.debug('Removing %s entry', key)
            self._remove(directory, key)

    def _store(self, directory: str, key: str, value):
        filename = os.path.join(directory, key.replace('/', '_'))
        try:
            os.makedirs(directory, exist_ok=True)
            with open(filename, self.write) as output:
                output.write(self.encode(value))
                return True
        except OSError:
            log.debug('Failed to store %s to cache:', key, exc_info=True)
            return False
        except Exception:
            log.debug('Failed to encode %s to cache:', key, exc_info=True)

    def _remove(self, directory: str, key: str):
        filename = os.path.join(directory, key.replace('/', '_'))
        try:
            os.remove(filename)
        except OSError:
            log.debug('Failed to remove %s from cache:', key, exc_info=True)
            return False
        return True


class FileSystemCache(Cache, FileSystemStorage):
    def __init__(self, directory: str, cache_type: str, *, encode=None, decode=None, binary=False):
        FileSystemStorage.__init__(self, encode, decode, binary)
        self.base_dir = os.path.join(directory, cache_type)

    def retrieve(self, key):
        return self._retrieve(self.base_dir, key)

    def store(self, key, value):
        return self._store(self.base_dir, key, value)

    def remove(self, key):
        return self._remove(self.base_dir, key)


class FileSystemPerJidCache(PerJidCache, FileSystemStorage):
    def __init__(self, directory: str, cache_type: str, *, encode=None, decode=None, binary=False):
        FileSystemStorage.__init__(self, encode, decode, binary)
        self.base_dir = os.path.join(directory, cache_type)

    def retrieve_by_jid(self, jid, key):
        directory = os.path.join(self.base_dir, jid)
        return self._retrieve(directory, key)

    def store_by_jid(self, jid, key, value):
        directory = os.path.join(self.base_dir, jid)
        return self._store(directory, key, value)

    def remove_by_jid(self, jid, key):
        directory = os.path.join(self.base_dir, jid)
        return self._remove(directory, key)
