#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Based on:
# https://docs.djangoproject.com/en/1.9/topics/testing/advanced
# Using the Django test runner to test reusable applications

import os
import logging
import sys

import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'
    django.setup()

    # Log memcache errors to console
    from django_pylibmc.memcached import log
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    log.addHandler(handler)

    # Test that the cache is working at all
    from django.core.cache import cache
    assert cache
    test_val = 'The test passed'
    assert cache.set('test', test_val), "Could not set cache value"
    cache_val = cache.get('test')
    assert cache_val == test_val, "Could not get from cache"

    # Ignore memcache errors during tests
    handler.setLevel(logging.CRITICAL)

    # Run the tests
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["tests"])
    sys.exit(bool(failures))
