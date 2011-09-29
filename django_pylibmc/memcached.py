"""
Memcached cache backend for Django using pylibmc.

If you want to use the binary protocol, specify `'BINARY': True` in your CACHES
settings.  The default is `False`, using the text protocol.

pylibmc behaviors can be declared as a dict in `CACHES` backend `OPTIONS`
setting.

Unlike the default Django caching backends, this backend lets you pass 0 as a
timeout, which translates to an infinite timeout in memcached.
"""
import logging
from threading import local

from django.conf import settings
from django.core.cache.backends.base import InvalidCacheBackendError
from django.core.cache.backends.memcached import BaseMemcachedCache

try:
    import pylibmc
except ImportError:
    raise InvalidCacheBackendError('Could not import pylibmc.')


MIN_COMPRESS = getattr(settings,
                       'PYLIBMC_MIN_COMPRESS_LEN', 150 * 1024)  # 150k
log = logging.getLogger('django.pylibmc')


class PyLibMCCache(BaseMemcachedCache):

    def __init__(self, server, params):
        self._local = local()
        self.binary = int(params.get('BINARY', False))
        super(PyLibMCCache, self).__init__(server, params, library=pylibmc,
                                           value_not_found_exception=pylibmc.NotFound)

    @property
    def _cache(self):
        # PylibMC uses cache options as the 'behaviors' attribute.
        # It also needs to use threadlocals, because some versions of
        # PylibMC don't play well with the GIL.
        client = getattr(self._local, 'client', None)
        if client:
            return client

        client = self._lib.Client(self._servers, binary=self.binary)
        if self._options:
            client.behaviors = self._options

        self._local.client = client

        return client

    def add(self, key, value, timeout=None, version=None):
        key = self.make_key(key, version=version)
        try:
            return self._cache.add(key, value,
                                   self._get_memcache_timeout(timeout),
                                   MIN_COMPRESS)
        except pylibmc.ServerError:
            log.error('ServerError saving %s (%d bytes)' % (key, len(value)),
                      exc_info=True)
            return False

    def set(self, key, value, timeout=None, version=None):
        key = self.make_key(key, version=version)
        try:
            self._cache.set(key, value, self._get_memcache_timeout(timeout),
                            MIN_COMPRESS)
        except pylibmc.ServerError:
            log.error('ServerError saving %s (%d bytes)' % (key, len(value)),
                      exc_info=True)
            return False
