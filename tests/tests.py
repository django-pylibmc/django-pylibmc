#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import time
from unittest import skipIf

import django
from django.core import signals
from django.core.cache import caches
from django.db import close_old_connections
from django.test import TestCase
from django.utils import six

from .models import Poll, expensive_calculation

try:
    from unittest import mock
except ImportError:
    # Python 2
    import mock

try:    # Use the same idiom as in cache backends
    from django.utils.six.moves import cPickle as pickle
except ImportError:
    import pickle


# functions/classes for complex data type tests
def f():
    return 42


class C:
    def m(n):
        return 24


class Unpicklable(object):
    def __getstate__(self):
        raise pickle.PickleError()


# Lifted from:
# https://github.com/django/django/blob/1.11.9/tests/cache/tests.py
class PylibmcCacheTests(TestCase):
    cache_name = 'default'
    # libmemcached manages its own connections.
    should_disconnect_on_close = False

    def setUp(self):
        self.cache = caches[self.cache_name]

    def tearDown(self):
        self.cache.clear()

    # #### From Django's BaseCacheTests ####

    def test_simple(self):
        # Simple cache set/get works
        self.cache.set("key", "value")
        self.assertEqual(self.cache.get("key"), "value")

    def test_add(self):
        # A key can be added to a cache
        self.cache.add("addkey1", "value")
        result = self.cache.add("addkey1", "newvalue")
        self.assertFalse(result)
        self.assertEqual(self.cache.get("addkey1"), "value")

    def test_non_existent(self):
        # Non-existent cache keys return as None/default
        # get with non-existent keys
        self.assertIsNone(self.cache.get("does_not_exist"))
        self.assertEqual(self.cache.get("does_not_exist", "bang!"), "bang!")

    def test_get_many(self):
        # Multiple cache keys can be returned using get_many
        self.cache.set('a', 'a')
        self.cache.set('b', 'b')
        self.cache.set('c', 'c')
        self.cache.set('d', 'd')
        self.assertDictEqual(self.cache.get_many(['a', 'c', 'd']), {'a': 'a', 'c': 'c', 'd': 'd'})
        self.assertDictEqual(self.cache.get_many(['a', 'b', 'e']), {'a': 'a', 'b': 'b'})

    def test_delete(self):
        # Cache keys can be deleted
        self.cache.set("key1", "spam")
        self.cache.set("key2", "eggs")
        self.assertEqual(self.cache.get("key1"), "spam")
        self.cache.delete("key1")
        self.assertIsNone(self.cache.get("key1"))
        self.assertEqual(self.cache.get("key2"), "eggs")

    def test_has_key(self):
        # The cache can be inspected for cache keys
        self.cache.set("hello1", "goodbye1")
        self.assertTrue(self.cache.has_key("hello1"))  # noqa: W601
        self.assertFalse(self.cache.has_key("goodbye1"))  # noqa: W601
        self.cache.set("no_expiry", "here", None)
        self.assertTrue(self.cache.has_key("no_expiry"))  # noqa: W601

    def test_in(self):
        # The in operator can be used to inspet cache contents
        self.cache.set("hello2", "goodbye2")
        self.assertIn("hello2", self.cache)
        self.assertNotIn("goodbye2", self.cache)

    def test_incr(self):
        # Cache values can be incremented
        self.cache.set('answer', 41)
        self.assertEqual(self.cache.incr('answer'), 42)
        self.assertEqual(self.cache.get('answer'), 42)
        self.assertEqual(self.cache.incr('answer', 10), 52)
        self.assertEqual(self.cache.get('answer'), 52)
        self.assertEqual(self.cache.incr('answer', -10), 42)
        with self.assertRaises(ValueError):
            self.cache.incr('does_not_exist')

    def test_decr(self):
        # Cache values can be decremented
        self.cache.set('answer', 43)
        self.assertEqual(self.cache.decr('answer'), 42)
        self.assertEqual(self.cache.get('answer'), 42)
        self.assertEqual(self.cache.decr('answer', 10), 32)
        self.assertEqual(self.cache.get('answer'), 32)
        self.assertEqual(self.cache.decr('answer', -10), 42)
        with self.assertRaises(ValueError):
            self.cache.decr('does_not_exist')

    def test_data_types(self):
        # Many different data types can be cached
        stuff = {
            'string': 'this is a string',
            'int': 42,
            'list': [1, 2, 3, 4],
            'tuple': (1, 2, 3, 4),
            'dict': {'A': 1, 'B': 2},
            'function': f,
            'class': C,
        }
        self.cache.set("stuff", stuff)
        self.assertEqual(self.cache.get("stuff"), stuff)

    def test_cache_read_for_model_instance(self):
        # Don't want fields with callable as default to be called on cache read
        expensive_calculation.num_runs = 0
        Poll.objects.all().delete()
        my_poll = Poll.objects.create(question="Well?")
        self.assertEqual(Poll.objects.count(), 1)
        pub_date = my_poll.pub_date
        self.cache.set('question', my_poll)
        cached_poll = self.cache.get('question')
        self.assertEqual(cached_poll.pub_date, pub_date)
        # We only want the default expensive calculation run once
        self.assertEqual(expensive_calculation.num_runs, 1)

    def test_cache_write_for_model_instance_with_deferred(self):
        # Don't want fields with callable as default to be called on cache write
        expensive_calculation.num_runs = 0
        Poll.objects.all().delete()
        Poll.objects.create(question="What?")
        self.assertEqual(expensive_calculation.num_runs, 1)
        defer_qs = Poll.objects.all().defer('question')
        self.assertEqual(defer_qs.count(), 1)
        self.assertEqual(expensive_calculation.num_runs, 1)
        self.cache.set('deferred_queryset', defer_qs)
        # cache set should not re-evaluate default functions
        self.assertEqual(expensive_calculation.num_runs, 1)

    def test_cache_read_for_model_instance_with_deferred(self):
        # Don't want fields with callable as default to be called on cache read
        expensive_calculation.num_runs = 0
        Poll.objects.all().delete()
        Poll.objects.create(question="What?")
        self.assertEqual(expensive_calculation.num_runs, 1)
        defer_qs = Poll.objects.all().defer('question')
        self.assertEqual(defer_qs.count(), 1)
        self.cache.set('deferred_queryset', defer_qs)
        self.assertEqual(expensive_calculation.num_runs, 1)
        runs_before_cache_read = expensive_calculation.num_runs
        self.cache.get('deferred_queryset')
        # We only want the default expensive calculation run on creation and set
        self.assertEqual(expensive_calculation.num_runs, runs_before_cache_read)

    def test_expiration(self):
        # Cache values can be set to expire
        self.cache.set('expire1', 'very quickly', 1)
        self.cache.set('expire2', 'very quickly', 1)
        self.cache.set('expire3', 'very quickly', 1)

        time.sleep(2)
        self.assertIsNone(self.cache.get("expire1"))

        self.cache.add("expire2", "newvalue")
        self.assertEqual(self.cache.get("expire2"), "newvalue")
        self.assertFalse(self.cache.has_key("expire3"))  # noqa: W601

    def test_unicode(self):
        # Unicode values can be cached
        stuff = {
            'ascii': 'ascii_value',
            'unicode_ascii': 'Iñtërnâtiônàlizætiøn1',
            'Iñtërnâtiônàlizætiøn': 'Iñtërnâtiônàlizætiøn2',
            'ascii2': {'x': 1}
        }
        # Test `set`
        for (key, value) in stuff.items():
            self.cache.set(key, value)
            self.assertEqual(self.cache.get(key), value)

        # Test `add`
        for (key, value) in stuff.items():
            self.cache.delete(key)
            self.cache.add(key, value)
            self.assertEqual(self.cache.get(key), value)

        # Test `set_many`
        for (key, value) in stuff.items():
            self.cache.delete(key)
        self.cache.set_many(stuff)
        for (key, value) in stuff.items():
            self.assertEqual(self.cache.get(key), value)

    def test_binary_string(self):
        # Binary strings should be cacheable
        from zlib import compress, decompress
        value = 'value_to_be_compressed'
        compressed_value = compress(value.encode())

        # Test set
        self.cache.set('binary1', compressed_value)
        compressed_result = self.cache.get('binary1')
        self.assertEqual(compressed_value, compressed_result)
        self.assertEqual(value, decompress(compressed_result).decode())

        # Test add
        self.cache.add('binary1-add', compressed_value)
        compressed_result = self.cache.get('binary1-add')
        self.assertEqual(compressed_value, compressed_result)
        self.assertEqual(value, decompress(compressed_result).decode())

        # Test set_many
        self.cache.set_many({'binary1-set_many': compressed_value})
        compressed_result = self.cache.get('binary1-set_many')
        self.assertEqual(compressed_value, compressed_result)
        self.assertEqual(value, decompress(compressed_result).decode())

    def test_set_many(self):
        # Multiple keys can be set using set_many
        self.cache.set_many({"key1": "spam", "key2": "eggs"})
        self.assertEqual(self.cache.get("key1"), "spam")
        self.assertEqual(self.cache.get("key2"), "eggs")

    def test_set_many_expiration(self):
        # set_many takes a second ``timeout`` parameter
        self.cache.set_many({"key1": "spam", "key2": "eggs"}, 1)
        time.sleep(2)
        self.assertIsNone(self.cache.get("key1"))
        self.assertIsNone(self.cache.get("key2"))

    def test_delete_many(self):
        # Multiple keys can be deleted using delete_many
        self.cache.set("key1", "spam")
        self.cache.set("key2", "eggs")
        self.cache.set("key3", "ham")
        self.cache.delete_many(["key1", "key2"])
        self.assertIsNone(self.cache.get("key1"))
        self.assertIsNone(self.cache.get("key2"))
        self.assertEqual(self.cache.get("key3"), "ham")

    def test_clear(self):
        # The cache can be emptied using clear
        self.cache.set("key1", "spam")
        self.cache.set("key2", "eggs")
        self.cache.clear()
        self.assertIsNone(self.cache.get("key1"))
        self.assertIsNone(self.cache.get("key2"))

    def test_long_timeout(self):
        """
        Followe memcached's convention where a timeout greater than 30 days is
        treated as an absolute expiration timestamp instead of a relative
        offset (#12399).
        """
        self.cache.set('key1', 'eggs', 60 * 60 * 24 * 30 + 1)  # 30 days + 1 second
        self.assertEqual(self.cache.get('key1'), 'eggs')

        self.cache.add('key2', 'ham', 60 * 60 * 24 * 30 + 1)
        self.assertEqual(self.cache.get('key2'), 'ham')

        self.cache.set_many({'key3': 'sausage', 'key4': 'lobster bisque'}, 60 * 60 * 24 * 30 + 1)
        self.assertEqual(self.cache.get('key3'), 'sausage')
        self.assertEqual(self.cache.get('key4'), 'lobster bisque')

    def test_forever_timeout(self):
        """
        Passing in None into timeout results in a value that is cached forever
        """
        self.cache.set('key1', 'eggs', None)
        self.assertEqual(self.cache.get('key1'), 'eggs')

        self.cache.add('key2', 'ham', None)
        self.assertEqual(self.cache.get('key2'), 'ham')
        added = self.cache.add('key1', 'new eggs', None)
        self.assertIs(added, False)
        self.assertEqual(self.cache.get('key1'), 'eggs')

        self.cache.set_many({'key3': 'sausage', 'key4': 'lobster bisque'}, None)
        self.assertEqual(self.cache.get('key3'), 'sausage')
        self.assertEqual(self.cache.get('key4'), 'lobster bisque')

    def test_zero_timeout(self):
        """
        Passing in zero for the timeout results in a value that is cached
        forever.

        In Django, it results in a value that is not cached.
        TODO: Re-sync this with the upstream test once django-pylibmc
        follows the Django behaviour:
        https://github.com/django-pylibmc/django-pylibmc/issues/35
        """
        self.cache.set('key1', 'eggs', 0)
        self.assertEqual(self.cache.get('key1'), 'eggs')

        self.cache.add('key2', 'ham', 0)
        self.assertEqual(self.cache.get('key2'), 'ham')
        added = self.cache.add('key1', 'new eggs', None)
        self.assertEqual(added, False)
        self.assertEqual(self.cache.get('key1'), 'eggs')

        self.cache.set_many({'key3': 'sausage', 'key4': 'lobster bisque'}, None)
        self.assertEqual(self.cache.get('key3'), 'sausage')
        self.assertEqual(self.cache.get('key4'), 'lobster bisque')

    def test_float_timeout(self):
        # Make sure a timeout given as a float doesn't crash anything.
        self.cache.set("key1", "spam", 100.2)
        self.assertEqual(self.cache.get("key1"), "spam")

    def test_cache_versioning_get_set(self):
        # set, using default version = 1
        self.cache.set('answer1', 42)
        self.assertEqual(self.cache.get('answer1'), 42)
        self.assertEqual(self.cache.get('answer1', version=1), 42)
        self.assertIsNone(self.cache.get('answer1', version=2))

        # set, default version = 1, but manually override version = 2
        self.cache.set('answer2', 42, version=2)
        self.assertIsNone(self.cache.get('answer2'))
        self.assertIsNone(self.cache.get('answer2', version=1))
        self.assertEqual(self.cache.get('answer2', version=2), 42)

    def test_cache_versioning_add(self):
        # add, default version = 1, but manually override version = 2
        self.cache.add('answer1', 42, version=2)
        self.assertIsNone(self.cache.get('answer1', version=1))
        self.assertEqual(self.cache.get('answer1', version=2), 42)

        self.cache.add('answer1', 37, version=2)
        self.assertIsNone(self.cache.get('answer1', version=1))
        self.assertEqual(self.cache.get('answer1', version=2), 42)

        self.cache.add('answer1', 37, version=1)
        self.assertEqual(self.cache.get('answer1', version=1), 37)
        self.assertEqual(self.cache.get('answer1', version=2), 42)

    def test_cache_versioning_has_key(self):
        self.cache.set('answer1', 42)

        # has_key
        self.assertTrue(self.cache.has_key('answer1'))  # noqa: W601
        self.assertTrue(self.cache.has_key('answer1', version=1))  # noqa: W601
        self.assertFalse(self.cache.has_key('answer1', version=2))  # noqa: W601

    def test_cache_versioning_delete(self):
        self.cache.set('answer1', 37, version=1)
        self.cache.set('answer1', 42, version=2)
        self.cache.delete('answer1')
        self.assertIsNone(self.cache.get('answer1', version=1))
        self.assertEqual(self.cache.get('answer1', version=2), 42)

        self.cache.set('answer2', 37, version=1)
        self.cache.set('answer2', 42, version=2)
        self.cache.delete('answer2', version=2)
        self.assertEqual(self.cache.get('answer2', version=1), 37)
        self.assertIsNone(self.cache.get('answer2', version=2))

    def test_cache_versioning_incr_decr(self):
        self.cache.set('answer1', 37, version=1)
        self.cache.set('answer1', 42, version=2)
        self.cache.incr('answer1')
        self.assertEqual(self.cache.get('answer1', version=1), 38)
        self.assertEqual(self.cache.get('answer1', version=2), 42)
        self.cache.decr('answer1')
        self.assertEqual(self.cache.get('answer1', version=1), 37)
        self.assertEqual(self.cache.get('answer1', version=2), 42)

        self.cache.set('answer2', 37, version=1)
        self.cache.set('answer2', 42, version=2)
        self.cache.incr('answer2', version=2)
        self.assertEqual(self.cache.get('answer2', version=1), 37)
        self.assertEqual(self.cache.get('answer2', version=2), 43)
        self.cache.decr('answer2', version=2)
        self.assertEqual(self.cache.get('answer2', version=1), 37)
        self.assertEqual(self.cache.get('answer2', version=2), 42)

    def test_cache_versioning_get_set_many(self):
        # set, using default version = 1
        self.cache.set_many({'ford1': 37, 'arthur1': 42})
        self.assertDictEqual(self.cache.get_many(['ford1', 'arthur1']), {'ford1': 37, 'arthur1': 42})
        self.assertDictEqual(self.cache.get_many(['ford1', 'arthur1'], version=1), {'ford1': 37, 'arthur1': 42})
        self.assertDictEqual(self.cache.get_many(['ford1', 'arthur1'], version=2), {})

        # set, default version = 1, but manually override version = 2
        self.cache.set_many({'ford2': 37, 'arthur2': 42}, version=2)
        self.assertDictEqual(self.cache.get_many(['ford2', 'arthur2']), {})
        self.assertDictEqual(self.cache.get_many(['ford2', 'arthur2'], version=1), {})
        self.assertDictEqual(self.cache.get_many(['ford2', 'arthur2'], version=2), {'ford2': 37, 'arthur2': 42})

    def test_incr_version(self):
        self.cache.set('answer', 42, version=2)
        self.assertIsNone(self.cache.get('answer'))
        self.assertIsNone(self.cache.get('answer', version=1))
        self.assertEqual(self.cache.get('answer', version=2), 42)
        self.assertIsNone(self.cache.get('answer', version=3))

        self.assertEqual(self.cache.incr_version('answer', version=2), 3)
        self.assertIsNone(self.cache.get('answer'))
        self.assertIsNone(self.cache.get('answer', version=1))
        self.assertIsNone(self.cache.get('answer', version=2))
        self.assertEqual(self.cache.get('answer', version=3), 42)

        with self.assertRaises(ValueError):
            self.cache.incr_version('does_not_exist')

    def test_decr_version(self):
        self.cache.set('answer', 42, version=2)
        self.assertIsNone(self.cache.get('answer'))
        self.assertIsNone(self.cache.get('answer', version=1))
        self.assertEqual(self.cache.get('answer', version=2), 42)

        self.assertEqual(self.cache.decr_version('answer', version=2), 1)
        self.assertEqual(self.cache.get('answer'), 42)
        self.assertEqual(self.cache.get('answer', version=1), 42)
        self.assertIsNone(self.cache.get('answer', version=2))

        with self.assertRaises(ValueError):
            self.cache.decr_version('does_not_exist', version=2)

    def test_add_fail_on_pickleerror(self):
        # Shouldn't fail silently if trying to cache an unpicklable type.
        with self.assertRaises(pickle.PickleError):
            self.cache.add('unpicklable', Unpicklable())

    def test_set_fail_on_pickleerror(self):
        with self.assertRaises(pickle.PickleError):
            self.cache.set('unpicklable', Unpicklable())

    @skipIf(django.VERSION < (1, 11),
            'get_or_set with `None` not supported (Django ticket #26792)')
    def test_get_or_set(self):
        self.assertIsNone(self.cache.get('projector'))
        self.assertEqual(self.cache.get_or_set('projector', 42), 42)
        self.assertEqual(self.cache.get('projector'), 42)
        self.assertEqual(self.cache.get_or_set('null', None), None)

    @skipIf(django.VERSION < (1, 9), 'get_or_set not supported')
    def test_get_or_set_callable(self):
        def my_callable():
            return 'value'

        self.assertEqual(self.cache.get_or_set('mykey', my_callable), 'value')
        self.assertEqual(self.cache.get_or_set('mykey', my_callable()), 'value')

    @skipIf(django.VERSION < (1, 9), 'get_or_set not supported')
    def test_get_or_set_callable_returning_none(self):
        self.assertIsNone(self.cache.get_or_set('mykey', lambda: None))
        # Previous get_or_set() doesn't store None in the cache.
        self.assertEqual(self.cache.get('mykey', 'default'), 'default')

    @skipIf(django.VERSION < (1, 11),
            'get_or_set with `None` not supported (Django ticket #26792)')
    def test_get_or_set_version(self):
        msg = (
            "get_or_set() missing 1 required positional argument: 'default'"
            if six.PY3
            else 'get_or_set() takes at least 3 arguments'
        )
        self.cache.get_or_set('brian', 1979, version=2)
        with self.assertRaisesMessage(TypeError, msg):
            self.cache.get_or_set('brian')
        with self.assertRaisesMessage(TypeError, msg):
            self.cache.get_or_set('brian', version=1)
        self.assertIsNone(self.cache.get('brian', version=1))
        self.assertEqual(self.cache.get_or_set('brian', 42, version=1), 42)
        self.assertEqual(self.cache.get_or_set('brian', 1979, version=2), 1979)
        self.assertIsNone(self.cache.get('brian', version=3))

    # #### From Django's BaseMemcachedTests ####

    def test_invalid_key_length(self):
        # memcached limits key length to 250
        with self.assertRaises(Exception):
            self.cache.set('a' * 251, 'value')

    def test_memcached_deletes_key_on_failed_set(self):
        # By default memcached allows objects up to 1MB. For the cache_db session
        # backend to always use the current session, memcached needs to delete
        # the old key if it fails to set.
        # pylibmc doesn't seem to have SERVER_MAX_VALUE_LENGTH as far as I can
        # tell from a quick check of its source code. This is falling back to
        # the default value exposed by python-memcached on my system.
        max_value_length = getattr(self.cache._lib, 'SERVER_MAX_VALUE_LENGTH', 1048576)

        self.cache.set('small_value', 'a')
        self.assertEqual(self.cache.get('small_value'), 'a')

        large_value = 'a' * (max_value_length + 1)
        try:
            self.cache.set('small_value', large_value)
        except Exception:
            # Some clients (e.g. pylibmc) raise when the value is too large,
            # while others (e.g. python-memcached) intentionally return True
            # indicating success. This test is primarily checking that the key
            # was deleted, so the return/exception behavior for the set()
            # itself is not important.
            pass
        # small_value should be deleted, or set if configured to accept larger values
        value = self.cache.get('small_value')
        self.assertTrue(value is None or value == large_value)

    def test_close(self):
        # For clients that don't manage their connections properly, the
        # connection is closed when the request is complete.
        signals.request_finished.disconnect(close_old_connections)
        try:
            with mock.patch.object(self.cache._lib.Client, 'disconnect_all', autospec=True) as mock_disconnect:
                signals.request_finished.send(self.__class__)
                self.assertIs(mock_disconnect.called, self.should_disconnect_on_close)
        finally:
            signals.request_finished.connect(close_old_connections)

    # #### django-pylibmc specific ####

    def test_gt_1MB_value(self):
        # Test value > 1M gets compressed and stored
        big_value = 'x' * 2 * 1024 * 1024
        self.cache.set('big_value', big_value)
        self.assertEqual(self.cache.get('big_value'), big_value)

    def test_too_big_value(self):
        # A value larger than 1M after compression will fail and return False
        super_big_value = 'x' * 400 * 1024 * 1024
        self.assertFalse(self.cache.set('super_big_value', super_big_value))


class PylibmcCacheWithBinaryTests(PylibmcCacheTests):
    cache_name = 'binary'


class PylibmcCacheWithOptionsTests(PylibmcCacheTests):
    cache_name = 'with_options'
