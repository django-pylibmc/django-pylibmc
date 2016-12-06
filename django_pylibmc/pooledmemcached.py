"""
Memcached cache backend for Django using pylibmc that uses a connection pool.
"""
from .memcached import PyLibMCCache
from contextlib import contextmanager
from Queue import Queue


class PooledPyLibMCCache(PyLibMCCache):

    def __init__(self, *args, **kwargs):
        super(PooledPyLibMCCache, self).__init__(*args, **kwargs)

        # queue is thread safe
        self._client_pool = Queue()
        pool_size = 10
        if self._options:
            pool_size = self._options.get('pool_size', pool_size)

        for i in xrange(pool_size):
            # add None as a sentinel
            self._client_pool.put(None)

    @contextmanager
    def _with_pool(self):
        # blocking get, None sentinel will cause new connection to be created
        self._local.client = self._client_pool.get()

        try:
            yield
        finally:
            # put the client back into the pool to be reused
            self._client_pool.put(self._local.client)

    def close(self, **kwargs):
        # do not disconnect client
        pass

    def add(self, *args, **kwargs):
        with self._with_pool():
            return super(PooledPyLibMCCache, self).add(*args, **kwargs)

    def get(self, *args, **kwargs):
        with self._with_pool():
            return super(PooledPyLibMCCache, self).get(*args, **kwargs)

    def set(self, *args, **kwargs):
        with self._with_pool():
            return super(PooledPyLibMCCache, self).set(*args, **kwargs)

    def delete(self, *args, **kwargs):
        with self._with_pool():
            return super(PooledPyLibMCCache, self).delete(*args, **kwargs)

    def set_many(self, *args, **kwargs):
        with self._with_pool():
            return super(PooledPyLibMCCache, self).set_many(*args, **kwargs)

    def delete_many(self, *args, **kwargs):
        with self._with_pool():
            return super(PooledPyLibMCCache, self).delete_many(*args, **kwargs)

    def clear(self, *args, **kwargs):
        with self._with_pool():
            return super(PooledPyLibMCCache, self).clear(*args, **kwargs)

    def incr(self, *args, **kwargs):
        with self._with_pool():
            return super(PooledPyLibMCCache, self).incr(*args, **kwargs)

    def decr(self, *args, **kwargs):
        with self._with_pool():
            return super(PooledPyLibMCCache, self).decr(*args, **kwargs)
