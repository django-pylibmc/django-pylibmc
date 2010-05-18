"""
Memcached cache backend for Django using pylibmc.

If you want to use the binary protocol, specify &binary=1 in your
CACHE_BACKEND.  The default is 0, using the text protocol.

pylibmc behaviors can be declared as a dict in settings.py under the name
PYLIBMC_BEHAVIORS.

Unlike the default Django caching backends, this backend lets you pass 0 as a
timeout, which translates to an infinite timeout in memcached.
"""
import time

from django.conf import settings
from django.core.cache.backends.base import BaseCache, InvalidCacheBackendError
from django.utils.encoding import smart_unicode, smart_str

try:
    import pylibmc
except ImportError:
    raise InvalidCacheBackendError('Could not import pylibmc.')


# It would be nice to inherit from Django's memcached backend, but that
# requires import python-memcache or cmemcache.  Those probably aren't
# available since we're using pylibmc, hence the copy/paste.


class CacheClass(BaseCache):

    def __init__(self, server, params):
        BaseCache.__init__(self, params)
        binary = int(params.get('binary', False))
        self._cache = pylibmc.Client(server.split(';'), binary=binary)
        self._cache.behaviors = getattr(settings, 'PYLIBMC_BEHAVIORS', {})

    def _get_memcache_timeout(self, timeout):
        """
        Memcached deals with long (> 30 days) timeouts in a special
        way. Call this function to obtain a safe value for your timeout.
        """
        timeout = self.default_timeout if timeout is None else timeout
        if timeout > 2592000: # 60*60*24*30, 30 days
            # See http://code.google.com/p/memcached/wiki/FAQ
            # "You can set expire times up to 30 days in the future. After that
            # memcached interprets it as a date, and will expire the item after
            # said date. This is a simple (but obscure) mechanic."
            #
            # This means that we have to switch to absolute timestamps.
            timeout += int(time.time())
        return timeout

    def add(self, key, value, timeout=None):
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        return self._cache.add(smart_str(key), value, self._get_memcache_timeout(timeout))

    def get(self, key, default=None):
        val = self._cache.get(smart_str(key))
        if val is None:
            return default
        return val

    def set(self, key, value, timeout=None):
        self._cache.set(smart_str(key), value, self._get_memcache_timeout(timeout))

    def delete(self, key):
        self._cache.delete(smart_str(key))

    def get_many(self, keys):
        return self._cache.get_multi(map(smart_str,keys))

    def close(self, **kwargs):
        self._cache.disconnect_all()

    def incr(self, key, delta=1):
        try:
            return self._cache.incr(key, delta)
        except pylibmc.NotFound:
            raise ValueError("Key '%s' not found" % key)

    def decr(self, key, delta=1):
        try:
            return self._cache.decr(key, delta)
        except pylibmc.NotFound:
            raise ValueError("Key '%s' not found" % key)

    def set_many(self, data, timeout=None):
        safe_data = {}
        for key, value in data.items():
            if isinstance(value, unicode):
                value = value.encode('utf-8')
            safe_data[smart_str(key)] = value
        self._cache.set_multi(safe_data, self._get_memcache_timeout(timeout))

    def delete_many(self, keys):
        self._cache.delete_multi(map(smart_str, keys))

    def clear(self):
        self._cache.flush_all()
