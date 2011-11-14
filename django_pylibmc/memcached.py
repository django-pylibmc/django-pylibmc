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
import warnings

from django.conf import settings
from django.core.cache.backends.base import InvalidCacheBackendError
from django.core.cache.backends.memcached import BaseMemcachedCache

try:
    import pylibmc
    MemcachedError = pylibmc._pylibmc.MemcachedError
except ImportError:
    raise InvalidCacheBackendError('Could not import pylibmc.')


log = logging.getLogger('django.pylibmc')


MIN_COMPRESS = getattr(settings, 'PYLIBMC_MIN_COMPRESS_LEN', 0)  # Disabled
if MIN_COMPRESS > 0 and not pylibmc.support_compression:
    MIN_COMPRESS = 0
    warnings.warn('A minimum compression length was provided but pylibmc was '
                  'not compiled with support for it.')


class PyLibMCCache(BaseMemcachedCache):

    def __init__(self, server, params, username=None, password=None):
        import os
        self._local = local()
        self.binary = int(params.get('BINARY', False))
        self._username = os.environ.get('MEMCACHE_USERNAME', username)
        self._password = os.environ.get('MEMCACHE_PASSWORD', password)
        self._server = os.environ.get('MEMCACHE_SERVERS', server)
        super(PyLibMCCache, self).__init__(self._server, params, library=pylibmc,
                                           value_not_found_exception=pylibmc.NotFound)

    @property
    def _cache(self):
        # PylibMC uses cache options as the 'behaviors' attribute.
        # It also needs to use threadlocals, because some versions of
        # PylibMC don't play well with the GIL.
        client = getattr(self._local, 'client', None)
        if client:
            return client
        
        if (self._username != None and self._password != None):
            client = self._lib.Client(self._servers, 
            binary=self.binary, 
            username=self._username, 
            password=self._password)    
        else:
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
        except MemcachedError, e:
            log.error('MemcachedError: %s' % e, exc_info=True)
            return False

    def get(self, key, default=None, version=None):
        try:
            return super(PyLibMCCache, self).get(key, default, version)
        except MemcachedError, e:
            log.error('MemcachedError: %s' % e, exc_info=True)
            return default

    def set(self, key, value, timeout=None, version=None):
        key = self.make_key(key, version=version)
        try:
            return self._cache.set(key, value,
                                   self._get_memcache_timeout(timeout),
                                   MIN_COMPRESS)
        except pylibmc.ServerError:
            log.error('ServerError saving %s (%d bytes)' % (key, len(value)),
                      exc_info=True)
            return False
        except MemcachedError, e:
            log.error('MemcachedError: %s' % e, exc_info=True)
            return False

    def delete(self, *args, **kwargs):
        try:
            return super(PyLibMCCache, self).delete(*args, **kwargs)
        except MemcachedError, e:
            log.error('MemcachedError: %s' % e, exc_info=True)
            return False

    def get_many(self, *args, **kwargs):
        try:
            return super(PyLibMCCache, self).get_many(*args, **kwargs)
        except MemcachedError, e:
            log.error('MemcachedError: %s' % e, exc_info=True)
            return {}

    def set_many(self, *args, **kwargs):
        try:
            return super(PyLibMCCache, self).set_many(*args, **kwargs)
        except MemcachedError, e:
            log.error('MemcachedError: %s' % e, exc_info=True)
            return False

    def delete_many(self, *args, **kwargs):
        try:
            return super(PyLibMCCache, self).delete_many(*args, **kwargs)
        except MemcachedError, e:
            log.error('MemcachedError: %s' % e, exc_info=True)
            return False
